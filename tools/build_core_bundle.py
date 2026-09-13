#!/usr/bin/env python3
"""Build a deterministic member bundle from the clean, exact HEAD Git tree."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path

from release_content import content_issues, included, path_issue


class BundleError(ValueError):
    """The source or destination does not satisfy the release contract."""


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def source_commit(root: Path, requested: str | None = None) -> str:
    top = Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if top != root.resolve():
        raise BundleError("--root must be the Git repository root")
    commit = git(root, "rev-parse", "HEAD").decode().strip()
    if requested is not None and (not re.fullmatch(r"[0-9a-f]{40}", requested) or requested != commit):
        raise BundleError("--commit must be the full lowercase SHA of exact HEAD")
    # Untracked/ignored files are never inputs. Require all tracked content,
    # including excluded operator files, to match the commit being attested.
    if git(root, "status", "--porcelain=v1", "--untracked-files=no"):
        raise BundleError("release requires a clean index and tracked working tree; commit or preserve changes first")
    return commit


def committed_files(root: Path, commit: str) -> list[tuple[str, int, bytes]]:
    result = []
    for entry in git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        path = raw_path.decode("utf-8")
        problem = path_issue(path)
        if problem:
            raise BundleError(f"{path}: {problem}")
        if mode not in {"100644", "100755"} or kind != "blob":
            raise BundleError(f"{path}: symlinks, submodules and non-regular files are not release inputs")
        if not included(path):
            continue
        data = git(root, "cat-file", "blob", object_id)
        issues = content_issues(path, data)
        if issues:
            raise BundleError(f"{path}: {'; '.join(issues)}")
        result.append((path, 0o755 if mode == "100755" else 0o644, data))
    return sorted(result)


def archive_bytes(entries: list[tuple[str, int, bytes]]) -> bytes:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path, mode, data in entries:
            info = tarfile.TarInfo(f"multiplai-core/{path}")
            info.size = len(data)
            info.mode = mode
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    return stream.getvalue()


def tar_bytes(root: Path, commit: str | None = None) -> bytes:
    """Compatibility helper, with the same committed-source checks as the CLI."""
    return archive_bytes(committed_files(root, source_commit(root, commit)))


def build(root: Path, version: str, output: Path, commit: str | None = None) -> Path:
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-rc\.(?:0|[1-9][0-9]*))?", version):
        raise BundleError("version must be MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-rc.N (no leading zeros)")
    root = root.resolve()
    commit = source_commit(root, commit)
    entries = committed_files(root, commit)
    if not entries:
        raise BundleError("member distribution policy selected no committed files")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / f"multiplai-core-{version}.tar.zst"
    manifest_path = output / f"multiplai-core-{version}.manifest.json"
    destinations = [artifact, manifest_path, Path(str(artifact) + ".minisig"), Path(str(manifest_path) + ".minisig")]
    if any(path.exists() or path.is_symlink() for path in destinations):
        raise BundleError("release output already exists; immutable artifacts and signatures cannot be overwritten")
    with tempfile.TemporaryDirectory(prefix=".core-build-", dir=output) as temp:
        temp_root = Path(temp)
        raw = temp_root / "bundle.tar"
        packed = temp_root / artifact.name
        raw.write_bytes(archive_bytes(entries))
        # One compression thread and normalized tar metadata make repeated
        # builds byte-identical for a fixed Git tree and zstd version.
        subprocess.run(["zstd", "-q", "-19", "-T1", "--no-progress", str(raw), "-o", str(packed)], check=True)
        digest = hashlib.sha256(packed.read_bytes()).hexdigest()
        manifest = {
            "schema_version": 1, "name": "multiplai-core", "version": version,
            "commit": commit, "artifact": artifact.name, "digest": f"sha256:{digest}",
            "signature": f"{artifact.name}.minisig",
            "manifest_signature": f"{manifest_path.name}.minisig",
            "sop_count": sum(bool(re.fullmatch(r"sops/[^/]+/sop\.yaml", path)) for path, _, _ in entries),
        }
        manifest_tmp = temp_root / manifest_path.name
        manifest_tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        # Detect a changed checkout during the build. Bytes were read from
        # immutable blobs, never from the mutable working directory.
        if source_commit(root, commit) != commit:
            raise BundleError("HEAD changed during build")
        # Hard-link publication is atomic and refuses an existing destination.
        os.link(packed, artifact)
        try:
            os.link(manifest_tmp, manifest_path)
        except OSError:
            artifact.unlink()
            raise
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit")
    args = parser.parse_args()
    try:
        print(build(args.root, args.version, args.output, args.commit))
        return 0
    except (BundleError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"bundle: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
