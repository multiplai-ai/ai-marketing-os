#!/usr/bin/env python3
"""Shared, dependency-free safety primitives for the Hermes runtime."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable

SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
SHA = re.compile(r"^[0-9a-f]{40}$")


class HermesError(RuntimeError):
    """A stable, receipt-safe runtime failure."""


def require_id(value: str, label: str = "identifier") -> str:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise HermesError(f"invalid {label}")
    return value


def canonical_child(root: Path, *parts: str, must_exist: bool = False) -> Path:
    """Return a contained path and reject traversal or symlinked ancestors."""
    root = root.absolute()
    if root.is_symlink():
        raise HermesError(f"managed root must not be a symlink: {root}")
    if root.exists() and not root.is_dir():
        raise HermesError(f"managed root must be a directory: {root}")
    candidate = root.joinpath(*parts)
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise HermesError("path escapes managed root") from exc
    cursor = root
    for part in relative.parts:
        if part in ("", ".", ".."):
            raise HermesError("unsafe path component")
        cursor = cursor / part
        if cursor.is_symlink():
            raise HermesError(f"symlink prohibited in managed path: {cursor}")
    if must_exist and not candidate.exists():
        raise HermesError(f"path does not exist: {candidate}")
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
        fsync_dir(path.parent)
    finally:
        try:
            os.unlink(name)
        except FileNotFoundError:
            pass


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run(argv: Iterable[str], cwd: Path | None = None, timeout: int = 120) -> str:
    result = subprocess.run(
        list(argv), cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=timeout, check=False,
    )
    if result.returncode:
        raise HermesError(f"command failed ({result.returncode}): {result.stdout.strip()}")
    return result.stdout.strip()


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not stat.S_ISDIR(path.stat().st_mode):
        raise HermesError(f"private directory is unsafe: {path}")
    os.chmod(path, 0o700)


def fsync_dir(path: Path) -> None:
    """Persist a directory entry change before reporting it durable."""
    descriptor=os.open(path,os.O_RDONLY)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)
