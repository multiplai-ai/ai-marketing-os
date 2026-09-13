from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_core_bundle import BundleError, build, tar_bytes
from check_release_content import check
from release_content import included


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Release Test")
    git(root, "config", "user.email", "release@example.test")
    (root / "sops" / "demo").mkdir(parents=True)
    (root / "sops/demo/sop.yaml").write_text("id: demo\n")
    (root / "README.md").write_text("Fictional member example.\n")
    (root / ".gitignore").write_text(".env\ndist/\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "Fixture source")
    return root


def commit_file(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    git(root, "add", "--force", path)
    git(root, "commit", "-qm", "Add fixture")


def test_archive_uses_git_tree_excluding_untracked_ignored_and_operator_docs(repo: Path) -> None:
    commit_file(repo, "docs/superpowers/plans/private-rollout.md", "Private operator details\n")
    commit_file(repo, "MATT-README.md", "Operator onboarding\n")
    (repo / ".env").write_text("SYNTHETIC_SECRET=never-distribute\n")
    (repo / "sops/demo/untracked.txt").write_text("not committed\n")
    with tarfile.open(fileobj=io.BytesIO(tar_bytes(repo))) as archive:
        names = archive.getnames()
        assert names == ["multiplai-core/.gitignore", "multiplai-core/README.md", "multiplai-core/sops/demo/sop.yaml"]
        assert all(m.uid == m.gid == m.mtime == 0 for m in archive.getmembers())


@pytest.mark.parametrize("staged", [False, True])
def test_dirty_source_rejected(repo: Path, staged: bool) -> None:
    (repo / "README.md").write_text("modified\n")
    if staged:
        git(repo, "add", "README.md")
    with pytest.raises(BundleError, match="clean index"):
        tar_bytes(repo)


@pytest.mark.parametrize("commit", ["a" * 40, "HEAD", "../bad"])
def test_mismatched_or_symbolic_commit_rejected(repo: Path, commit: str) -> None:
    with pytest.raises(BundleError, match="exact HEAD"):
        tar_bytes(repo, commit)


@pytest.mark.parametrize("version", ["../escape", "1.2.3/../../bad", "1.2", "01.2.3", "1.2.3-rc.01", "1.2.3\n"])
def test_version_rejected_before_output_creation(repo: Path, tmp_path: Path, version: str) -> None:
    output = tmp_path / "out"
    with pytest.raises(BundleError, match="version must"):
        build(repo, version, output)
    assert not output.exists()


@pytest.mark.parametrize("path", [".env", "tools/.env.production", "tools/credentials.json", "tools/id_ed25519"])
def test_sensitive_tracked_files_rejected_even_outside_allowlist(repo: Path, path: str) -> None:
    commit_file(repo, path, "synthetic sensitive fixture\n")
    with pytest.raises(BundleError, match="release input"):
        tar_bytes(repo)
    assert check(repo)


def test_symlink_rejected(repo: Path) -> None:
    (repo / "tools").mkdir()
    (repo / "tools/link").symlink_to("../README.md")
    git(repo, "add", "tools/link")
    git(repo, "commit", "-qm", "Symlink fixture")
    with pytest.raises(BundleError, match="symlinks"):
        tar_bytes(repo)


def test_submodule_rejected(repo: Path) -> None:
    (repo / "vendor/module").mkdir(parents=True)
    git(repo, "update-index", "--add", "--cacheinfo", "160000", git(repo, "rev-parse", "HEAD"), "vendor/module")
    git(repo, "commit", "-qm", "Gitlink fixture")
    with pytest.raises(BundleError, match="submodules"):
        tar_bytes(repo)


def test_distributed_content_checked_beyond_sops_and_tools(repo: Path) -> None:
    commit_file(repo, "generated/codex/skills/demo/SKILL.md", "Use /Users/example/private/input.md\n")
    with pytest.raises(BundleError, match="host-specific"):
        tar_bytes(repo)
    assert any("generated/codex" in issue for issue in check(repo))


def test_trust_and_maintenance_files_included_but_operator_docs_excluded() -> None:
    assert included("archive/brand-history.json")
    assert included("examples/strategy-evaluation/review.json")
    assert not included("archive/unreviewed-material.md")
    for path in ("releases/trust/minisign.pub", "releases/TRUST.md", "tests/test_demo.py", ".github/workflows/validate.yml", "docs/member-guide.md", "examples/member-demo/brief.md"):
        assert included(path)
    for path in ("releases/member-list.csv", "docs/superpowers/plans/rollout.md", ".cursor/environment.json", "MATT-README.md", "new-unreviewed-directory/data.txt"):
        assert not included(path)


def test_repeated_builds_identical_and_manifest_matches_actual_archive(repo: Path, tmp_path: Path) -> None:
    commit = git(repo, "rev-parse", "HEAD")
    first = build(repo, "4.0.0-rc.13", tmp_path / "one", commit)
    os.utime(repo / "README.md", (123456, 123456))
    second = build(repo, "4.0.0-rc.13", tmp_path / "two", commit)
    assert first.read_bytes() == second.read_bytes()
    manifest = json.loads(first.read_text())
    artifact = first.parent / manifest["artifact"]
    assert artifact.read_bytes() == (second.parent / manifest["artifact"]).read_bytes()
    assert manifest["commit"] == commit
    assert manifest["digest"] == "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest()
    raw = subprocess.check_output(["zstd", "-q", "-d", "-c", str(artifact)])
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        assert sum(name.endswith("/sop.yaml") for name in archive.getnames()) == manifest["sop_count"] == 1


@pytest.mark.parametrize("existing", [".tar.zst", ".manifest.json", ".tar.zst.minisig", ".manifest.json.minisig"])
def test_existing_release_files_are_never_overwritten(repo: Path, tmp_path: Path, existing: str) -> None:
    output = tmp_path / "release"
    output.mkdir()
    original = output / f"multiplai-core-1.2.3{existing}"
    original.write_bytes(b"immutable existing bytes")
    with pytest.raises(BundleError, match="immutable"):
        build(repo, "1.2.3", output)
    assert original.read_bytes() == b"immutable existing bytes"
    assert list(output.iterdir()) == [original]


def test_git_executable_mode_preserved(repo: Path) -> None:
    commit_file(repo, "tools/run.py", "print('demo')\n")
    git(repo, "update-index", "--chmod=+x", "tools/run.py")
    git(repo, "commit", "-qm", "Executable fixture")
    (repo / "tools/run.py").chmod(0o755)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes(repo))) as archive:
        assert archive.getmember("multiplai-core/tools/run.py").mode == 0o755
        assert archive.getmember("multiplai-core/README.md").mode == 0o644


def test_unpacked_archive_is_checked_without_git(repo: Path, tmp_path: Path) -> None:
    destination = tmp_path / "unpacked"
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(tar_bytes(repo))) as archive:
        archive.extractall(destination, filter="data")
    unpacked = destination / "multiplai-core"
    assert check(unpacked) == []
    (unpacked / ".env").write_text("SYNTHETIC=must-fail\n")
    (unpacked / "operator-notes.md").write_text("private\n")
    errors = check(unpacked)
    assert any("environment files" in error for error in errors)
    assert any("operator-notes.md: outside" in error for error in errors)


def test_credentials_scanned_in_distributed_templates(repo: Path) -> None:
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    commit_file(repo, "templates/unsafe.txt", marker + "\n")
    with pytest.raises(BundleError, match="credential material"):
        tar_bytes(repo)


@pytest.mark.parametrize("path", ["tools/.pytest_cache/cache.json", "sops/demo/.DS_Store"])
def test_tracked_local_caches_rejected(repo: Path, path: str) -> None:
    commit_file(repo, path, "local cache fixture\n")
    with pytest.raises(BundleError, match="release input"):
        tar_bytes(repo)
    assert check(repo)
