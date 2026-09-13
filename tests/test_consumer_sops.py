from __future__ import annotations

import base64
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from consumer_sops import (  # noqa: E402
    ConsumerSopError,
    generate_adapters,
    resolve_sop,
    validate_consumer_bootstrap,
    validate_consumer,
    write_adapters,
    write_consumer_bootstrap,
)


SKILL = """---
name: {sop_id}
description: Exercise {sop_id} behavior.
---

# {sop_id}

Do the thing.
"""


class ConsumerSopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.core = base / "multiplai-core"
        self.consumer = base / "client-os"
        for root in (self.core, self.consumer):
            root.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        self._write_package(self.core, "shared-task")
        subprocess.run(["git", "add", "."], cwd=self.core, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.core, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.core, text=True).strip()
        (self.consumer / "entity.yaml").write_text("id: client\n", encoding="utf-8")
        (self.consumer / ".multiplai").mkdir()
        self._write_lock(["shared-task"])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_package(self, root: Path, sop_id: str) -> None:
        package = root / "sops" / sop_id
        package.mkdir(parents=True)
        (package / "SKILL.md").write_text(SKILL.format(sop_id=sop_id), encoding="utf-8")
        (package / "sop.yaml").write_text(
            yaml.safe_dump({
                "id": sop_id,
                "version": "1.0.0",
                "title": sop_id,
                "maturity": "internal",
                "inputs": [],
                "outputs": [],
                "tools": [],
            }, sort_keys=False),
            encoding="utf-8",
        )

    def _write_lock(self, sops: list[str]) -> None:
        (self.consumer / ".multiplai" / "core.lock.yaml").write_text(
            yaml.safe_dump({
                "core": {
                    "version": "4.0.0-rc.2",
                    "commit": self.commit,
                    "digest": "sha256:" + "1" * 64,
                },
                "sops": sops,
            }, sort_keys=False),
            encoding="utf-8",
        )

    def test_resolves_local_without_binding(self) -> None:
        self._write_package(self.consumer, "local-task")
        package, binding, _, lock = resolve_sop(self.consumer, "local-task", self.core)
        self.assertEqual(package.source_type, "local")
        self.assertIsNone(binding)
        self.assertIsNone(lock)

    def test_resolves_exact_pinned_core_content(self) -> None:
        (self.core / "sops" / "shared-task" / "SKILL.md").write_text("uncommitted replacement", encoding="utf-8")
        package, _, _, lock = resolve_sop(self.consumer, "shared-task", self.core)
        self.assertEqual(package.source_type, "core")
        self.assertIn("Do the thing", package.skill_markdown)
        self.assertNotIn("replacement", package.skill_markdown)
        self.assertEqual(lock["core"]["commit"], self.commit)

    def test_legacy_core_without_frontmatter_gets_discoverable_adapter(self) -> None:
        legacy = self.core / "sops" / "shared-task" / "SKILL.md"
        legacy.write_text("# Shared task\n\nBuild the recurring shared report from approved inputs.\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.core, check=True)
        subprocess.run(["git", "commit", "-qm", "legacy fixture"], cwd=self.core, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.core, text=True).strip()
        self._write_lock(["shared-task"])
        adapter = generate_adapters(self.consumer, self.core)["shared-task"]
        self.assertIn("Use when the task requires shared-task", adapter)
        self.assertIn("Build the recurring shared report", adapter)

    def test_duplicate_local_and_core_fails_closed(self) -> None:
        self._write_package(self.consumer, "shared-task")
        with self.assertRaisesRegex(ConsumerSopError, "duplicate SOP ownership"):
            resolve_sop(self.consumer, "shared-task", self.core)

    def test_unlocked_sop_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConsumerSopError, "neither local nor allowed"):
            resolve_sop(self.consumer, "unknown-task", self.core)

    def test_empty_binding_is_invalid(self) -> None:
        binding_dir = self.consumer / "config" / "sop-bindings"
        binding_dir.mkdir(parents=True)
        (binding_dir / "shared-task.yaml").write_text(
            "schema_version: 1\nsop_id: shared-task\nentity: client\nvalues: {}\n",
            encoding="utf-8",
        )
        errors = validate_consumer(self.consumer, self.core)
        self.assertTrue(any("non-empty" in error for error in errors))

    def test_generated_adapters_contain_pointers_not_procedure_copy(self) -> None:
        self._write_package(self.consumer, "local-task")
        adapters = generate_adapters(self.consumer, self.core)
        write_adapters(self.consumer, adapters)
        self.assertIn("Canonical source", adapters["local-task"])
        self.assertNotIn("Do the thing", adapters["local-task"])
        self.assertIn("resolve_sop.py", adapters["shared-task"])
        self.assertIn('$ROOT/.multiplai/tools/resolve_sop.py', adapters["shared-task"])
        self.assertNotIn("../multiplai-core", adapters["shared-task"])
        self.assertIn("--ensure-installed", adapters["shared-task"])
        self.assertNotIn("--materialize", adapters["shared-task"])
        self.assertIn("source_ref", adapters["shared-task"])
        self.assertIn("tool_roots", adapters["shared-task"])
        self.assertIn("absolute path", adapters["shared-task"])
        self.assertIn("first listed root", adapters["shared-task"])
        self.assertIn(
            "Never execute runtime tools from an unverified core working tree",
            adapters["shared-task"],
        )
        for name in ("resolve_sop.py", "consumer_sops.py", "core_install.py"):
            self.assertTrue((self.consumer / ".multiplai" / "tools" / name).is_file())
        self.assertTrue((self.consumer / ".multiplai" / "trust" / "minisign.pub").is_file())
        self.assertEqual(validate_consumer(self.consumer, self.core), [])

    def test_bootstrap_preserves_an_existing_valid_trust_root(self) -> None:
        trust = self.consumer / ".multiplai" / "trust" / "minisign.pub"
        trust.parent.mkdir(parents=True)
        independently_pinned = base64.b64encode(b"Ed" + b"x" * 40).decode() + "\n"
        trust.write_text(independently_pinned, encoding="utf-8")

        write_consumer_bootstrap(self.consumer)

        self.assertEqual(trust.read_text(encoding="utf-8"), independently_pinned)
        self.assertEqual(validate_consumer_bootstrap(self.consumer), [])

    def test_bootstrap_rejects_malformed_existing_trust_root(self) -> None:
        trust = self.consumer / ".multiplai" / "trust" / "minisign.pub"
        trust.parent.mkdir(parents=True)
        trust.write_text("not-a-minisign-key\n", encoding="utf-8")

        with self.assertRaisesRegex(ConsumerSopError, "base64"):
            write_consumer_bootstrap(self.consumer)

        self.assertFalse((self.consumer / ".multiplai" / "tools" / "resolve_sop.py").exists())

    def test_bootstrap_validation_detects_module_drift(self) -> None:
        write_consumer_bootstrap(self.consumer)
        resolver = self.consumer / ".multiplai" / "tools" / "resolve_sop.py"
        resolver.write_text("# drifted\n", encoding="utf-8")

        errors = validate_consumer_bootstrap(self.consumer)

        self.assertTrue(any("stale" in error and "resolve_sop.py" in error for error in errors))

    def test_bootstrap_refuses_symlinked_trust_directory(self) -> None:
        outside = Path(self.temp.name) / "outside-trust"
        outside.mkdir()
        (self.consumer / ".multiplai" / "trust").symlink_to(outside, target_is_directory=True)

        with self.assertRaisesRegex(ConsumerSopError, "must not be a symlink"):
            write_consumer_bootstrap(self.consumer)

        self.assertEqual(list(outside.iterdir()), [])

    def test_generated_offline_validator_accepts_fixture(self) -> None:
        adapters = generate_adapters(self.consumer, self.core)
        write_adapters(self.consumer, adapters)
        target = self.consumer / ".multiplai" / "tools" / "validate_repo.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (Path(__file__).resolve().parents[1] / "templates" / "consumer" / "validate_repo.py").read_text(),
            encoding="utf-8",
        )
        result = subprocess.run([sys.executable, str(target)], cwd=self.consumer, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generated_offline_validator_rejects_missing_bootstrap_module(self) -> None:
        adapters = generate_adapters(self.consumer, self.core)
        write_adapters(self.consumer, adapters)
        target = self.consumer / ".multiplai" / "tools" / "validate_repo.py"
        target.write_text(
            (Path(__file__).resolve().parents[1] / "templates" / "consumer" / "validate_repo.py").read_text(),
            encoding="utf-8",
        )
        (self.consumer / ".multiplai" / "tools" / "core_install.py").unlink()

        result = subprocess.run(
            [sys.executable, str(target)],
            cwd=self.consumer,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing or unsafe consumer bootstrap module", result.stdout)


if __name__ == "__main__":
    unittest.main()
