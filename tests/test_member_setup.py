from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from consumer_sops import generate_adapters, load_core_lock, resolve_sop, validate_consumer_bootstrap
from core_install import CoreInstallError, remove_core_install, verify_core_install
from scaffold_member import DEFAULT_SOPS, MemberSetupError, scaffold_member

VERSION = "4.0.0-rc.99"


def command(*args: str) -> None:
    subprocess.run(args, check=True, capture_output=True, text=True)


@pytest.fixture
def release(tmp_path: Path) -> tuple[Path, Path]:
    directory = tmp_path / "release"
    directory.mkdir()
    key = tmp_path / "ephemeral-test.pub"
    secret = tmp_path / "ephemeral-test.key"
    command("minisign", "-G", "-W", "-p", str(key), "-s", str(secret))
    selected = [ROOT / f"sops/{sop}/{name}" for sop in DEFAULT_SOPS for name in ("SKILL.md", "sop.yaml")]
    selected += [ROOT / "tools" / name for name in (
        "core_install.py", "consumer_sops.py", "resolve_sop.py", "generate_consumer_adapters.py",
        "scaffold_writing_setup.py", "validate_writing_config.py", "writing_config.py", "human_writing_gate.py",
    )]
    selected += [ROOT / f"schemas/{name}" for name in ("writing-profile.schema.yaml", "writing-asset-catalog.schema.yaml")]
    selected += [path for path in (ROOT / "templates/writing").rglob("*") if path.is_file()]
    selected += [ROOT / "examples/member-demo/business-context.md"]
    tarpath = tmp_path / "fixture.tar"
    with tarfile.open(tarpath, "w") as archive:
        for path in selected:
            data = path.read_bytes()
            if path.name == "business-context.md":
                data += b"\nFictional release-only fixture marker.\n"
            member = tarfile.TarInfo("multiplai-core/" + path.relative_to(ROOT).as_posix())
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    artifact = directory / f"multiplai-core-{VERSION}.tar.zst"
    command("zstd", "-q", str(tarpath), "-o", str(artifact))
    manifest_path = directory / f"multiplai-core-{VERSION}.manifest.json"
    manifest = {
        "schema_version": 1, "name": "multiplai-core", "version": VERSION,
        "commit": "a" * 40, "artifact": artifact.name,
        "digest": "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "signature": artifact.name + ".minisig", "manifest_signature": manifest_path.name + ".minisig",
        "sop_count": len(DEFAULT_SOPS),
    }
    manifest_path.write_text(json.dumps(manifest) + "\n")
    for path in (artifact, manifest_path):
        command("minisign", "-Sm", str(path), "-s", str(secret))
    return directory, key


def test_signed_setup_resolves_three_adapters_and_uninstalls(release: tuple[Path, Path], tmp_path: Path) -> None:
    directory, key = release
    consumer = tmp_path / "consumer"
    result = scaffold_member(consumer, directory, VERSION, key)
    assert result["signature_status"] == "verified"
    assert result["entity"] == "riverton-workshop"
    assert load_core_lock(consumer)["sops"] == list(DEFAULT_SOPS)
    jsonschema.Draft202012Validator(yaml.safe_load((ROOT / "schemas/core-lock.schema.yaml").read_text())).validate(load_core_lock(consumer))
    binding_validator = jsonschema.Draft202012Validator(yaml.safe_load((ROOT / "schemas/sop-binding.schema.yaml").read_text()))
    for path in (consumer / "config/sop-bindings").glob("*.yaml"):
        binding_validator.validate(yaml.safe_load(path.read_text()))
    status = subprocess.check_output(["git", "-C", str(consumer), "status", "--porcelain", "--untracked-files=all"], text=True)
    assert ".multiplai/installed-core/" not in status
    assert ".multiplai/core.install.json" not in status
    assert "context/business-context.md" not in status
    assert ".multiplai/core.lock.yaml" in status
    assert ".multiplai/trust/minisign.pub" in status
    install = Path(result["install_root"])
    assert result["core"] == verify_core_install(consumer)["core"]
    assert not (consumer / "sops").exists()
    assert set(generate_adapters(consumer)) == set(DEFAULT_SOPS)
    assert validate_consumer_bootstrap(consumer, source_tools=install / "tools") == []
    for sop in DEFAULT_SOPS:
        package, binding, _, _ = resolve_sop(consumer, sop)
        assert package.source_type == "installed-core"
        assert binding["values"] == {"brain": "context", "context": "context"}
        adapter = consumer / ".agents/skills" / sop / "SKILL.md"
        assert adapter.is_file()
        assert "Resolve the exact pinned procedure" in adapter.read_text()
    assert (consumer / "context/business-context.md").read_bytes() == (install / "examples/member-demo/business-context.md").read_bytes()
    assert (consumer / "context/business-context.md").read_bytes() != (ROOT / "examples/member-demo/business-context.md").read_bytes()
    assert list((consumer / "context").iterdir()) == [consumer / "context/business-context.md"]
    assert (consumer / "config/writing/writing-profile.yaml").is_file()
    assert yaml.safe_load((consumer / "config/writing/exemplar-candidates.yaml").read_text())["approved"] is False
    gate = json.loads(subprocess.check_output([
        sys.executable, "-B", str(install / "tools/human_writing_gate.py"),
        "--text", "The repair board shows the next promised pickup time.", "--json",
    ], text=True))
    assert gate["passed"] and not gate["errors"]
    assert verify_core_install(consumer)["signature_status"] == "verified"
    assert not list(install.rglob("__pycache__"))
    # Use the consumer bootstrap as a real CLI, preserving signed receipts.
    resolved = subprocess.check_output([
        sys.executable, "-B", str(consumer / ".multiplai/tools/resolve_sop.py"),
        "--consumer-root", str(consumer), "--sop-id", "content-brief",
    ], text=True)
    assert json.loads(resolved)["source_ref"] == str(install / "sops/content-brief")
    assert not install.stat().st_mode & 0o222
    remove_core_install(consumer)
    assert not install.exists()
    assert (consumer / "context/business-context.md").is_file()
    assert (consumer / "config/writing/writing-profile.yaml").is_file()
    with pytest.raises(CoreInstallError, match="no verified core installation"):
        verify_core_install(consumer)


@pytest.mark.parametrize("target", ["artifact", "manifest"])
def test_tampering_rejected_before_destination_write(release: tuple[Path, Path], tmp_path: Path, target: str) -> None:
    directory, key = release
    suffix = ".tar.zst" if target == "artifact" else ".manifest.json"
    path = directory / f"multiplai-core-{VERSION}{suffix}"
    path.write_bytes(path.read_bytes() + b"tampered")
    consumer = tmp_path / "consumer"
    with pytest.raises(CoreInstallError, match="invalid minisign signature"):
        scaffold_member(consumer, directory, VERSION, key)
    assert not consumer.exists()


def test_wrong_valid_key_rejected_and_empty_destination_preserved(release: tuple[Path, Path], tmp_path: Path) -> None:
    directory, _ = release
    wrong = tmp_path / "wrong.pub"
    command("minisign", "-G", "-W", "-p", str(wrong), "-s", str(tmp_path / "wrong.key"))
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    with pytest.raises(CoreInstallError, match="invalid minisign signature"):
        scaffold_member(consumer, directory, VERSION, wrong)
    assert list(consumer.iterdir()) == []


def test_nonempty_destination_preserves_existing_files(release: tuple[Path, Path], tmp_path: Path) -> None:
    directory, key = release
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    original = consumer / "entity.yaml"
    original.write_text("id: existing-business\n")
    with pytest.raises(MemberSetupError, match="existing files are preserved"):
        scaffold_member(consumer, directory, VERSION, key)
    assert original.read_text() == "id: existing-business\n"
    assert list(consumer.iterdir()) == [original]


def test_destination_inside_core_rejected_without_writes(release: tuple[Path, Path]) -> None:
    directory, key = release
    destination = ROOT / "member-setup-rejection-fixture"
    with pytest.raises(MemberSetupError, match="outside the Core"):
        scaffold_member(destination, directory, VERSION, key)
    assert not destination.exists()


def test_symlink_destination_rejected(release: tuple[Path, Path], tmp_path: Path) -> None:
    directory, key = release
    target = tmp_path / "empty"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(MemberSetupError, match="symlink"):
        scaffold_member(link, directory, VERSION, key)
    assert list(target.iterdir()) == []


def test_cli_has_required_trust_and_no_unsigned_option() -> None:
    help_text = subprocess.check_output([sys.executable, str(ROOT / "tools/scaffold_member.py"), "--help"], text=True)
    assert "--public-key-file" in help_text
    assert "--allow-unsigned" not in help_text


def test_signed_release_without_demo_reports_unsupported_member_setup(release: tuple[Path, Path], tmp_path: Path) -> None:
    directory, key = release
    artifact = directory / f"multiplai-core-{VERSION}.tar.zst"
    raw = subprocess.check_output(["zstd", "-q", "-d", "-c", str(artifact)])
    incomplete = tmp_path / "incomplete.tar"
    with tarfile.open(fileobj=io.BytesIO(raw)) as original, tarfile.open(incomplete, "w") as edited:
        for member in original.getmembers():
            if not member.name.endswith("business-context.md"):
                edited.addfile(member, original.extractfile(member))
    command("zstd", "-q", "-f", str(incomplete), "-o", str(artifact))
    manifest_path = directory / f"multiplai-core-{VERSION}.manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["digest"] = "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest) + "\n")
    for path in (artifact, manifest_path):
        command("minisign", "-Sm", str(path), "-s", str(key.parent / "ephemeral-test.key"))
    consumer = tmp_path / "consumer"
    with pytest.raises(MemberSetupError, match="missing examples/member-demo/business-context.md.*Partial files are preserved"):
        scaffold_member(consumer, directory, VERSION, key)
    assert (consumer / "entity.yaml").is_file()
    assert not (consumer / "context").exists()
    remove_core_install(consumer)


def test_signed_update_and_rollback_preserve_consumer_work(release, tmp_path):
    from core_install import install_core_bundle
    directory, key = release
    consumer = tmp_path / 'consumer'
    first = scaffold_member(consumer, directory, VERSION, key)
    lock_path = consumer / '.multiplai/core.lock.yaml'
    original_lock = lock_path.read_bytes()
    context = consumer / 'context/business-context.md'
    context.write_text('Consumer-owned edits must survive both transitions.\n')
    binding = consumer / 'config/sop-bindings/content-brief.yaml'
    original_binding = binding.read_bytes()
    profile = consumer / 'config/writing/writing-profile.yaml'
    original_profile = profile.read_bytes()
    artifact = directory / f'multiplai-core-{VERSION}.tar.zst'
    raw = subprocess.check_output(['zstd', '-q', '-dc', str(artifact)])
    next_version = '4.0.0-rc.100'
    next_artifact = directory / f'multiplai-core-{next_version}.tar.zst'
    tarpath = tmp_path / 'next.tar'
    with tarfile.open(fileobj=io.BytesIO(raw)) as old, tarfile.open(tarpath, 'w') as new:
        for member in old.getmembers():
            data = old.extractfile(member).read()
            if member.name.endswith('/examples/member-demo/business-context.md'):
                data += b'New release fixture.\n'
            member.size = len(data)
            new.addfile(member, io.BytesIO(data))
    command('zstd', '-q', str(tarpath), '-o', str(next_artifact))
    manifest_path = directory / f'multiplai-core-{VERSION}.manifest.json'
    next_manifest_path = directory / f'multiplai-core-{next_version}.manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest.update(version=next_version, commit='b' * 40, artifact=next_artifact.name,
                    digest='sha256:' + hashlib.sha256(next_artifact.read_bytes()).hexdigest(),
                    signature=next_artifact.name + '.minisig', manifest_signature=next_manifest_path.name + '.minisig')
    next_manifest_path.write_text(json.dumps(manifest))
    for item in (next_artifact, next_manifest_path):
        command('minisign', '-Sm', str(item), '-s', str(key.parent / 'ephemeral-test.key'))
    lock = yaml.safe_load(original_lock)
    lock['core'] = {name: manifest[name] for name in ('version', 'commit', 'digest')}
    lock_path.write_text(yaml.safe_dump(lock))
    trust = [line for line in key.read_text().splitlines() if not line.startswith('untrusted comment:')][0]
    second = install_core_bundle(consumer, next_artifact, next_manifest_path, public_key=trust)
    assert second['core']['version'] == next_version
    assert second['install_root'] != first['install_root']
    assert verify_core_install(consumer)['signature_status'] == 'verified'
    lock_path.write_bytes(original_lock)
    restored = install_core_bundle(consumer, artifact, manifest_path, public_key=trust)
    assert restored['core'] == first['core']
    assert verify_core_install(consumer)['signature_status'] == 'verified'
    assert context.read_text() == 'Consumer-owned edits must survive both transitions.\n'
    assert binding.read_bytes() == original_binding
    assert profile.read_bytes() == original_profile
    for sop in DEFAULT_SOPS:
        assert resolve_sop(consumer, sop)[0].source_type == 'installed-core'


def test_public_setup_pins_channel_and_reinstalls_anonymously(release, tmp_path, monkeypatch):
    import core_install
    directory, key = release
    consumer = tmp_path / 'public-consumer'
    scaffold_member(consumer, directory, VERSION, key, repository='multiplai-ai/ai-marketing-os')
    lock = load_core_lock(consumer)
    assert lock['core']['access'] == 'public'
    assert lock['core']['repository'] == 'multiplai-ai/ai-marketing-os'
    remove_core_install(consumer)
    calls = []
    def download(repo, version, destination):
        calls.append((repo, version))
        return tuple(directory / f'multiplai-core-{version}{suffix}' for suffix in
                     ('.tar.zst', '.manifest.json', '.tar.zst.minisig', '.manifest.json.minisig'))
    monkeypatch.setattr(core_install, 'download_public_release', download)
    receipt = core_install.ensure_core_install(consumer)
    assert calls == [('multiplai-ai/ai-marketing-os', VERSION)]
    assert receipt['signature_status'] == 'verified'
