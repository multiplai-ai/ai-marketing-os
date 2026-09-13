#!/usr/bin/env python3
"""Verify and atomically install an immutable core bundle for one consumer."""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request
import urllib.error
import shutil
import stat
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


class CoreInstallError(RuntimeError):
    """A core release cannot be installed or trusted safely."""


class CoreInstallStale(CoreInstallError):
    """The consumer contract changed and requires a fresh verified install."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CoreInstallError(f"missing release manifest: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoreInstallError(f"invalid release manifest {path}: {exc}") from exc
    required = {
        "schema_version",
        "name",
        "version",
        "commit",
        "artifact",
        "digest",
        "signature",
        "sop_count",
    }
    if not isinstance(data, dict) or not required.issubset(data):
        raise CoreInstallError(f"release manifest is missing required fields: {path}")
    if data.get("schema_version") != 1 or data.get("name") != "multiplai-core":
        raise CoreInstallError(f"unsupported release manifest identity: {path}")
    if data.get("signature") != f"{data.get('artifact')}.minisig":
        raise CoreInstallError(f"release manifest has an invalid artifact signature name: {path}")
    expected_manifest_signature = f"{path.name}.minisig"
    if data.get("manifest_signature", expected_manifest_signature) != expected_manifest_signature:
        raise CoreInstallError(f"release manifest has an invalid manifest signature name: {path}")
    return data


def _verify_signature(path: Path, signature: Path, public_key: str) -> None:
    if not signature.is_file():
        raise CoreInstallError(f"missing minisign signature: {signature}")
    if not public_key.strip():
        raise CoreInstallError("signature verification requires a minisign public key")
    if shutil.which("minisign") is None:
        raise CoreInstallError("signature verification requires the minisign executable")
    result = subprocess.run(
        ["minisign", "-Vm", str(path), "-x", str(signature), "-P", public_key.strip()],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise CoreInstallError(f"invalid minisign signature for {path}: {detail}")


def _validate_release_identity(
    lock: dict[str, Any], artifact: Path, manifest: dict[str, Any]
) -> None:
    core = lock["core"]
    for key in ("version", "commit", "digest"):
        if manifest.get(key) != core.get(key):
            raise CoreInstallError(
                f"release {key} does not match consumer lock: "
                f"{manifest.get(key)!r} != {core.get(key)!r}"
            )
    if manifest.get("artifact") != artifact.name:
        raise CoreInstallError("release manifest artifact name does not match selected artifact")
    actual_digest = f"sha256:{_sha256(artifact)}"
    if actual_digest != manifest.get("digest"):
        raise CoreInstallError(
            f"artifact digest does not match release manifest: "
            f"{actual_digest} != {manifest.get('digest')}"
        )


def _safe_member_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or path.parts[0] != "multiplai-core":
        raise CoreInstallError(f"unsafe archive member outside multiplai-core: {name}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise CoreInstallError(f"unsafe archive member path: {name}")
    return path


def _extract_bundle(artifact: Path, destination: Path) -> Path:
    if shutil.which("zstd") is None:
        raise CoreInstallError("core installation requires the zstd executable")
    raw_tar = destination / "bundle.tar"
    with raw_tar.open("wb") as output:
        result = subprocess.run(
            ["zstd", "-q", "-d", "-c", str(artifact)],
            stdout=output,
            stderr=subprocess.PIPE,
            check=False,
        )
    if result.returncode:
        raise CoreInstallError(
            f"cannot decompress core artifact: {result.stderr.decode(errors='replace').strip()}"
        )
    extract_root = destination / "payload"
    extract_root.mkdir()
    try:
        with tarfile.open(raw_tar, "r:") as archive:
            seen: set[PurePosixPath] = set()
            for member in archive.getmembers():
                relative = _safe_member_path(member.name)
                if relative in seen:
                    raise CoreInstallError(f"unsafe archive contains duplicate member: {member.name}")
                seen.add(relative)
                target = extract_root.joinpath(*relative.parts)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise CoreInstallError(
                        f"unsafe archive member type for {member.name}: only files and directories are allowed"
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise CoreInstallError(f"cannot read archive member: {member.name}")
                with source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
    except (tarfile.TarError, OSError) as exc:
        if isinstance(exc, CoreInstallError):
            raise
        raise CoreInstallError(f"cannot extract core artifact safely: {exc}") from exc
    finally:
        raw_tar.unlink(missing_ok=True)
    return extract_root / "multiplai-core"


def _make_writable(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted(root.rglob("*"), reverse=True):
        try:
            path.chmod(path.stat().st_mode | stat.S_IWUSR)
        except FileNotFoundError:
            pass
    root.chmod(root.stat().st_mode | stat.S_IWUSR)


def _make_read_only(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir():
            path.chmod(0o555)
        elif path.is_file():
            executable = bool(path.stat().st_mode & 0o111)
            path.chmod(0o555 if executable else 0o444)
    root.chmod(0o555)


def _package_hashes(install_root: Path, sop_ids: list[str]) -> dict[str, dict[str, str]]:
    hashes: dict[str, dict[str, str]] = {}
    for sop_id in sop_ids:
        package = install_root / "sops" / sop_id
        skill = package / "SKILL.md"
        metadata = package / "sop.yaml"
        if not skill.is_file() or not metadata.is_file():
            raise CoreInstallError(f"locked SOP is missing from installed bundle: {sop_id}")
        hashes[sop_id] = {
            "SKILL.md": _sha256(skill),
            "sop.yaml": _sha256(metadata),
        }
    return hashes


def _file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _validate_consumer_contract(consumer_root: Path, install_root: Path) -> tuple[dict, dict]:
    from consumer_sops import (  # Local import avoids a module cycle.
        entity_id,
        load_binding,
        load_core_lock,
        load_yaml,
        validate_package,
    )

    lock = load_core_lock(consumer_root)
    entity = entity_id(consumer_root)
    locked = set(lock["sops"])
    for sop_id in sorted(locked):
        package = install_root / "sops" / sop_id
        metadata = load_yaml(package / "sop.yaml")
        skill_path = package / "SKILL.md"
        if not skill_path.is_file():
            raise CoreInstallError(f"locked SOP is missing SKILL.md: {sop_id}")
        validate_package(
            sop_id,
            metadata,
            skill_path.read_text(encoding="utf-8"),
            str(package),
            require_frontmatter=False,
        )
        load_binding(consumer_root, sop_id, entity)
    binding_hashes = {}
    binding_root = consumer_root / "config" / "sop-bindings"
    if binding_root.is_dir():
        for path in sorted(binding_root.glob("*.yaml")):
            if path.stem not in locked:
                raise CoreInstallError(f"binding targets an unlocked core SOP: {path}")
            load_binding(consumer_root, path.stem, entity)
            binding_hashes[path.relative_to(consumer_root).as_posix()] = _sha256(path)
    return lock, binding_hashes


def _validate_manifest_contents(install_root: Path, manifest: dict[str, Any]) -> None:
    actual_sop_count = len(list((install_root / "sops").glob("*/sop.yaml")))
    if actual_sop_count != manifest.get("sop_count"):
        raise CoreInstallError(
            f"release SOP count does not match manifest: "
            f"{actual_sop_count} != {manifest.get('sop_count')}"
        )


def _receipt_path(consumer_root: Path) -> Path:
    return consumer_root / ".multiplai" / "core.install.json"


def install_core_bundle(
    consumer_root: Path,
    artifact: Path,
    manifest_path: Path,
    *,
    artifact_signature: Path | None = None,
    manifest_signature: Path | None = None,
    public_key: str | None = None,
    allow_unsigned: bool = False,
    cache_root: Path | None = None,
) -> dict[str, Any]:
    """Verify and atomically install the release pinned by a consumer lock."""
    from consumer_sops import find_repo_root, load_core_lock

    root = find_repo_root(consumer_root)
    artifact = artifact.resolve()
    manifest_path = manifest_path.resolve()
    if not artifact.is_file():
        raise CoreInstallError(f"missing core artifact: {artifact}")
    manifest = _load_manifest(manifest_path)
    lock = load_core_lock(root)
    _validate_release_identity(lock, artifact, manifest)

    if allow_unsigned:
        signature_status = "development-unsigned"
    else:
        artifact_signature = artifact_signature or artifact.with_name(str(manifest["signature"]))
        manifest_signature = manifest_signature or manifest_path.with_name(
            str(manifest.get("manifest_signature", manifest_path.name + ".minisig"))
        )
        _verify_signature(artifact, artifact_signature, public_key or "")
        _verify_signature(manifest_path, manifest_signature, public_key or "")
        signature_status = "verified"

    digest = str(lock["core"]["digest"]).split(":", 1)[1]
    cache = (cache_root or root / ".multiplai" / "installed-core").resolve()
    target_parent = cache / digest
    target = target_parent / "multiplai-core"
    cache.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{digest[:12]}-", dir=cache))
    try:
        extracted = _extract_bundle(artifact, staging)
        if not extracted.is_dir():
            raise CoreInstallError("core artifact has no multiplai-core root directory")
        _validate_manifest_contents(extracted, manifest)
        _, binding_hashes = _validate_consumer_contract(root, extracted)
        package_hashes = _package_hashes(extracted, lock["sops"])
        file_hashes = _file_hashes(extracted)
        if target_parent.exists():
            _make_writable(target_parent)
            shutil.rmtree(target_parent)
        target_parent.mkdir(parents=True)
        extracted.replace(target)
        _make_read_only(target)
        target_parent.chmod(0o555)
    finally:
        if staging.exists():
            _make_writable(staging)
            shutil.rmtree(staging)

    receipt = {
        "schema_version": 1,
        "consumer_root": str(root),
        "core": lock["core"],
        "sops": lock["sops"],
        "install_root": str(target),
        "artifact": str(artifact),
        "manifest": str(manifest_path),
        "signature_status": signature_status,
        "lock_sha256": _sha256(root / ".multiplai" / "core.lock.yaml"),
        "binding_sha256": binding_hashes,
        "package_sha256": package_hashes,
        "file_sha256": file_hashes,
    }
    receipt_path = _receipt_path(root)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=".core-install-",
        dir=receipt_path.parent,
        delete=False,
    ) as handle:
        handle.write(receipt_text)
        handle.flush()
        os.fsync(handle.fileno())
        temporary_receipt = Path(handle.name)
    temporary_receipt.replace(receipt_path)
    return receipt


def verify_core_install(consumer_root: Path) -> dict[str, Any]:
    """Fail closed if the active receipt, consumer contract, or installed files drifted."""
    from consumer_sops import find_repo_root, load_core_lock

    root = find_repo_root(consumer_root)
    path = _receipt_path(root)
    if not path.is_file():
        raise CoreInstallError(
            "no verified core installation; run tools/install_core_bundle.py for this consumer"
        )
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoreInstallError(f"invalid core installation receipt: {path}: {exc}") from exc
    lock = load_core_lock(root)
    if receipt.get("core") != lock["core"] or receipt.get("sops") != lock["sops"]:
        raise CoreInstallStale("core lock changed after installation")
    if receipt.get("lock_sha256") != _sha256(root / ".multiplai" / "core.lock.yaml"):
        raise CoreInstallStale("core lock changed after installation")
    install_root = Path(str(receipt.get("install_root", "")))
    if not install_root.is_dir():
        raise CoreInstallStale(f"installed core directory is missing: {install_root}")
    _, current_binding_hashes = _validate_consumer_contract(root, install_root)
    if current_binding_hashes != receipt.get("binding_sha256"):
        raise CoreInstallStale("consumer binding changed after installation")
    actual_packages = _package_hashes(install_root, lock["sops"])
    if actual_packages != receipt.get("package_sha256"):
        raise CoreInstallError("installed core package content changed after verification")
    if _file_hashes(install_root) != receipt.get("file_sha256"):
        raise CoreInstallError("installed core file content changed after verification")
    for candidate in (install_root, *install_root.rglob("*")):
        if candidate.stat().st_mode & 0o222:
            raise CoreInstallError(f"installed core is writable: {candidate}")
    return receipt


def remove_core_install(consumer_root: Path, *, cache_root: Path | None = None) -> Path:
    """Deliberately unlock and remove only the installation named by the active lock."""
    from consumer_sops import find_repo_root, load_core_lock

    root = find_repo_root(consumer_root)
    lock = load_core_lock(root)
    digest = str(lock["core"]["digest"]).split(":", 1)[1]
    cache = (cache_root or root / ".multiplai" / "installed-core").resolve()
    expected_parent = cache / digest
    receipt_path = _receipt_path(root)
    if receipt_path.is_file():
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CoreInstallError(f"invalid core installation receipt: {receipt_path}: {exc}") from exc
        recorded = Path(str(receipt.get("install_root", ""))).resolve().parent
        if recorded != expected_parent:
            raise CoreInstallError(
                f"refusing to remove installation outside the active lock cache: {recorded}"
            )
    if expected_parent.exists():
        _make_writable(expected_parent)
        shutil.rmtree(expected_parent)
    receipt_path.unlink(missing_ok=True)
    return expected_parent


def download_public_release(repository: str, version: str, destination: Path) -> tuple[Path, Path, Path, Path]:
    """Fetch four public assets anonymously; callers must verify signatures before use."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", repository):
        raise CoreInstallError("invalid public release repository; expected owner/name")
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-rc\.(?:0|[1-9][0-9]*))?", version):
        raise CoreInstallError("invalid public release version")
    names = tuple(f"multiplai-core-{version}{suffix}" for suffix in
                  (".tar.zst", ".manifest.json", ".tar.zst.minisig", ".manifest.json.minisig"))
    destination.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="release-", dir=destination) as staging:
            for name in names:
                url = f"https://github.com/{repository}/releases/download/v{version}/{name}"
                request = urllib.request.Request(url, headers={"User-Agent": "ai-marketing-os-installer"})
                limit = 128 * 1024 * 1024 if name.endswith(".tar.zst") else 1024 * 1024
                with urllib.request.urlopen(request, timeout=60) as response, (Path(staging) / name).open("wb") as output:
                    if not response.url.startswith("https://"):
                        raise CoreInstallError("release download redirected outside HTTPS")
                    size = 0
                    while block := response.read(1024 * 1024):
                        size += len(block)
                        if size > limit:
                            raise CoreInstallError(f"release asset exceeds size limit: {name}")
                        output.write(block)
            for name in names:
                os.replace(Path(staging) / name, destination / name)
    except (OSError, urllib.error.URLError) as exc:
        raise CoreInstallError(f"cannot download public release {repository} v{version}: {exc}") from exc
    return tuple(destination / name for name in names)


def download_core_release(
    consumer_root: Path,
    *,
    repository: str | None = None,
    download_root: Path | None = None,
) -> tuple[Path, Path, Path, Path]:
    """Download the exact release, preserving legacy private locks."""
    from consumer_sops import find_repo_root, load_core_lock

    root = find_repo_root(consumer_root)
    lock = load_core_lock(root)
    version = str(lock["core"]["version"])
    destination = (download_root or root / ".multiplai" / "downloads" / version).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    names = (
        f"multiplai-core-{version}.tar.zst",
        f"multiplai-core-{version}.manifest.json",
        f"multiplai-core-{version}.tar.zst.minisig",
        f"multiplai-core-{version}.manifest.json.minisig",
    )
    selected_repository = repository or lock["core"].get("repository", "multiplai-ai/multiplai-core")
    if lock["core"].get("access", "private") == "public":
        return download_public_release(selected_repository, version, destination)
    if shutil.which("gh") is None:
        raise CoreInstallError("automatic private core download requires the authenticated gh CLI")
    command = [
        "gh",
        "release",
        "download",
        f"v{version}",
        "--repo",
        selected_repository,
        "--dir",
        str(destination),
        "--clobber",
    ]
    for name in names:
        command.extend(("--pattern", name))
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise CoreInstallError(f"cannot download pinned core release v{version}: {detail}")
    paths = tuple(destination / name for name in names)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise CoreInstallError("downloaded release is incomplete: " + ", ".join(missing))
    return paths  # type: ignore[return-value]


def ensure_core_install(
    consumer_root: Path,
    *,
    release_dir: Path | None = None,
    public_key_file: Path | None = None,
    allow_unsigned: bool = False,
    repository: str | None = None,
) -> dict[str, Any]:
    """Verify the active install or acquire and install the exact pinned release."""
    from consumer_sops import find_repo_root, load_core_lock

    root = find_repo_root(consumer_root)
    try:
        return verify_core_install(root)
    except CoreInstallStale:
        pass
    except CoreInstallError as exc:
        if _receipt_path(root).exists():
            raise CoreInstallError(f"existing core installation failed verification: {exc}") from exc
    lock = load_core_lock(root)
    version = str(lock["core"]["version"])
    if release_dir is not None:
        artifact = release_dir / f"multiplai-core-{version}.tar.zst"
        manifest = release_dir / f"multiplai-core-{version}.manifest.json"
        artifact_signature = Path(str(artifact) + ".minisig")
        manifest_signature = Path(str(manifest) + ".minisig")
    else:
        artifact, manifest, artifact_signature, manifest_signature = download_core_release(
            root, repository=repository
        )
    key_path = public_key_file or root / ".multiplai" / "trust" / "minisign.pub"
    public_key = None
    if not allow_unsigned:
        if not key_path.is_file():
            raise CoreInstallError(f"missing pinned core trust root: {key_path}")
        public_key = key_path.read_text(encoding="utf-8").strip()
    return install_core_bundle(
        root,
        artifact,
        manifest,
        artifact_signature=artifact_signature,
        manifest_signature=manifest_signature,
        public_key=public_key,
        allow_unsigned=allow_unsigned,
    )
