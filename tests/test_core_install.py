from __future__ import annotations

import hashlib
import io
import json
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
import shutil
from unittest.mock import patch
from pathlib import Path

import yaml


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from core_install import (  # noqa: E402
    CoreInstallError,
    ensure_core_install,
    install_core_bundle,
    remove_core_install,
    verify_core_install,
)
from consumer_sops import resolution_receipt, resolve_sop, write_consumer_bootstrap  # noqa: E402


SKILL = """# Shared task

Build the shared report from approved inputs.
"""


class CoreInstallTests(unittest.TestCase):
    def _public_lock(self, root):
        path = root / ".multiplai/core.lock.yaml"
        lock = yaml.safe_load(path.read_text())
        lock["core"].update(repository="multiplai-ai/ai-marketing-os", access="public")
        path.write_text(yaml.safe_dump(lock))

    def test_public_consumers_share_one_install_and_detach_independently(self):
        self._public_lock(self.consumer)
        second = self.base / "second-client"
        shutil.copytree(self.consumer, second)
        with patch("core_install.Path.home", return_value=self.base):
            first = install_core_bundle(self.consumer, self.artifact, self.manifest, allow_unsigned=True)
            other = install_core_bundle(second, self.artifact, self.manifest, allow_unsigned=True)
        self.assertEqual(first["install_root"], other["install_root"])
        self.assertFalse((self.consumer / ".multiplai/installed-core").exists())
        remove_core_install(self.consumer)
        self.assertEqual(verify_core_install(second)["core"], other["core"])

    def test_public_missing_install_never_reads_sibling_core(self):
        from consumer_sops import ConsumerSopError
        self._public_lock(self.consumer)
        with self.assertRaisesRegex(ConsumerSopError, "Do not continue without the skill"):
            resolve_sop(self.consumer, "shared-task", core_root=self.base / "fake-core")

    def test_shared_tampering_is_not_repaired_silently_for_second_consumer(self):
        self._public_lock(self.consumer)
        second = self.base / "second-client"
        shutil.copytree(self.consumer, second)
        with patch("core_install.Path.home", return_value=self.base):
            receipt = install_core_bundle(self.consumer, self.artifact, self.manifest, allow_unsigned=True)
            skill = Path(receipt["install_root"]) / "sops/shared-task/SKILL.md"
            skill.chmod(0o644)
            skill.write_text("tampered")
            with self.assertRaisesRegex(CoreInstallError, "refusing to overwrite"):
                install_core_bundle(second, self.artifact, self.manifest, allow_unsigned=True)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.consumer = self.base / "client-os"
        self.consumer.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.consumer, check=True)
        (self.consumer / "entity.yaml").write_text("id: client\n", encoding="utf-8")
        (self.consumer / ".multiplai").mkdir()
        self.commit = "1" * 40
        self.version = "4.0.0-test.1"
        self.release = self.base / "release"
        self.release.mkdir()
        self.artifact = self.release / f"multiplai-core-{self.version}.tar.zst"
        self.manifest = self.release / f"multiplai-core-{self.version}.manifest.json"
        self._write_bundle()
        self._write_lock()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _core_files(self) -> dict[str, bytes]:
        metadata = yaml.safe_dump(
            {
                "id": "shared-task",
                "version": "1.0.0",
                "title": "Shared task",
                "maturity": "released",
                "inputs": [],
                "outputs": [],
                "tools": [],
            },
            sort_keys=False,
        ).encode()
        return {
            "multiplai-core/sops/shared-task/SKILL.md": SKILL.encode(),
            "multiplai-core/sops/shared-task/sop.yaml": metadata,
            "multiplai-core/tools/resolve_sop.py": b"# fixture\n",
        }

    def _compress_tar(self, members: dict[str, bytes]) -> None:
        raw = self.base / "bundle.tar"
        with tarfile.open(raw, "w") as archive:
            for name, content in members.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(content))
        subprocess.run(
            ["zstd", "-q", "-f", str(raw), "-o", str(self.artifact)],
            check=True,
        )

    def _write_bundle(self, members: dict[str, bytes] | None = None) -> None:
        self._compress_tar(members or self._core_files())
        digest = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "multiplai-core",
                    "version": self.version,
                    "commit": self.commit,
                    "artifact": self.artifact.name,
                    "digest": f"sha256:{digest}",
                    "signature": f"{self.artifact.name}.minisig",
                    "sop_count": 1,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_lock(self, *, digest: str | None = None, commit: str | None = None) -> None:
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        (self.consumer / ".multiplai" / "core.lock.yaml").write_text(
            yaml.safe_dump(
                {
                    "core": {
                        "version": self.version,
                        "commit": commit or self.commit,
                        "digest": digest or manifest["digest"],
                    },
                    "sops": ["shared-task"],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    def test_installs_verified_unsigned_development_bundle_read_only(self) -> None:
        receipt = install_core_bundle(
            self.consumer,
            self.artifact,
            self.manifest,
            allow_unsigned=True,
        )

        install_root = Path(receipt["install_root"])
        self.assertTrue((install_root / "sops/shared-task/SKILL.md").is_file())
        self.assertEqual(receipt["signature_status"], "development-unsigned")
        self.assertFalse((install_root / "sops/shared-task/SKILL.md").stat().st_mode & stat.S_IWUSR)
        self.assertEqual(verify_core_install(self.consumer)["core"], receipt["core"])

    def test_unsigned_bundle_is_rejected_by_default(self) -> None:
        with self.assertRaisesRegex(CoreInstallError, "signature"):
            install_core_bundle(self.consumer, self.artifact, self.manifest)

    def test_digest_mismatch_is_rejected(self) -> None:
        self._write_lock(digest="sha256:" + "f" * 64)
        with self.assertRaisesRegex(CoreInstallError, "digest"):
            install_core_bundle(
                self.consumer,
                self.artifact,
                self.manifest,
                allow_unsigned=True,
            )

    def test_commit_mismatch_is_rejected(self) -> None:
        self._write_lock(commit="2" * 40)
        with self.assertRaisesRegex(CoreInstallError, "commit"):
            install_core_bundle(
                self.consumer,
                self.artifact,
                self.manifest,
                allow_unsigned=True,
            )

    def test_unsafe_archive_member_is_rejected(self) -> None:
        members = self._core_files()
        members["multiplai-core/../escape.txt"] = b"nope"
        self._write_bundle(members)
        self._write_lock()
        with self.assertRaisesRegex(CoreInstallError, "unsafe archive"):
            install_core_bundle(
                self.consumer,
                self.artifact,
                self.manifest,
                allow_unsigned=True,
            )

    def test_resolver_can_require_and_use_installed_bundle(self) -> None:
        install_receipt = install_core_bundle(
            self.consumer,
            self.artifact,
            self.manifest,
            allow_unsigned=True,
        )

        package, _, _, lock = resolve_sop(
            self.consumer,
            "shared-task",
            require_installed=True,
        )

        self.assertEqual(package.source_type, "installed-core")
        self.assertIn("Build the shared report", package.skill_markdown)
        self.assertEqual(lock["core"]["commit"], self.commit)
        result = resolution_receipt(self.consumer, package, None, None, lock)
        self.assertEqual(
            result["tool_roots"],
            [
                str(self.consumer / "tools"),
                str(Path(install_receipt["install_root"]) / "tools"),
            ],
        )

    def test_consumer_owned_resolver_bootstraps_without_sibling_core_checkout(self) -> None:
        self.assertFalse((self.base / "multiplai-core").exists())
        write_consumer_bootstrap(self.consumer)
        resolver = self.consumer / ".multiplai" / "tools" / "resolve_sop.py"

        result = subprocess.run(
            [
                sys.executable,
                str(resolver),
                "--consumer-root",
                str(self.consumer),
                "--sop-id",
                "shared-task",
                "--ensure-installed",
                "--release-dir",
                str(self.release),
                "--allow-unsigned-development",
            ],
            cwd=self.consumer,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["source_type"], "installed-core")
        self.assertIn("/.multiplai/installed-core/", receipt["source_ref"])

    def test_receipt_detects_installed_content_tampering(self) -> None:
        receipt = install_core_bundle(
            self.consumer,
            self.artifact,
            self.manifest,
            allow_unsigned=True,
        )
        skill = Path(receipt["install_root"]) / "sops/shared-task/SKILL.md"
        skill.chmod(0o644)
        skill.write_text("tampered\n", encoding="utf-8")

        with self.assertRaisesRegex(CoreInstallError, "changed"):
            verify_core_install(self.consumer)

    def test_receipt_detects_non_sop_tool_tampering(self) -> None:
        receipt = install_core_bundle(
            self.consumer,
            self.artifact,
            self.manifest,
            allow_unsigned=True,
        )
        tool = Path(receipt["install_root"]) / "tools/resolve_sop.py"
        tool.chmod(0o644)
        tool.write_text("tampered tool\n", encoding="utf-8")

        with self.assertRaisesRegex(CoreInstallError, "file content changed"):
            verify_core_install(self.consumer)

    def test_explicit_remove_unlocks_and_deletes_installation(self) -> None:
        receipt = install_core_bundle(
            self.consumer,
            self.artifact,
            self.manifest,
            allow_unsigned=True,
        )

        removed = remove_core_install(self.consumer)

        self.assertEqual(removed, Path(receipt["install_root"]).parent)
        self.assertFalse(removed.exists())
        self.assertFalse((self.consumer / ".multiplai/core.install.json").exists())

    def test_ensure_installed_uses_local_development_release_once(self) -> None:
        first = ensure_core_install(
            self.consumer,
            release_dir=self.release,
            allow_unsigned=True,
        )
        self.artifact.unlink()

        second = ensure_core_install(
            self.consumer,
            release_dir=self.release,
            allow_unsigned=True,
        )

        self.assertEqual(second["install_root"], first["install_root"])

    def test_ensure_reinstalls_after_binding_change(self) -> None:
        binding_root = self.consumer / "config/sop-bindings"
        binding_root.mkdir(parents=True)
        binding = binding_root / "shared-task.yaml"
        binding.write_text(
            "schema_version: 1\nsop_id: shared-task\nentity: client\nvalues:\n  cadence: weekly\n",
            encoding="utf-8",
        )
        first = ensure_core_install(
            self.consumer,
            release_dir=self.release,
            allow_unsigned=True,
        )
        binding.write_text(
            "schema_version: 1\nsop_id: shared-task\nentity: client\nvalues:\n  cadence: monthly\n",
            encoding="utf-8",
        )

        second = ensure_core_install(
            self.consumer,
            release_dir=self.release,
            allow_unsigned=True,
        )

        self.assertNotEqual(second["binding_sha256"], first["binding_sha256"])

    def test_ensure_fails_closed_after_installed_content_tampering(self) -> None:
        receipt = ensure_core_install(
            self.consumer,
            release_dir=self.release,
            allow_unsigned=True,
        )
        skill = Path(receipt["install_root"]) / "sops/shared-task/SKILL.md"
        skill.chmod(0o644)
        skill.write_text("tampered\n", encoding="utf-8")

        with self.assertRaisesRegex(CoreInstallError, "existing core installation failed"):
            ensure_core_install(
                self.consumer,
                release_dir=self.release,
                allow_unsigned=True,
            )


if __name__ == "__main__":
    unittest.main()
