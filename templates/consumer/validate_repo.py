#!/usr/bin/env python3
"""Generated operating-repository layout validator. Do not edit by hand."""

from __future__ import annotations

import base64
import binascii
import re
import subprocess
import sys
from pathlib import Path

import yaml


SOP_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BOOTSTRAP_MODULES = ("resolve_sop.py", "consumer_sops.py", "core_install.py")


def load_yaml(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"missing required file: {path}")
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        errors.append(f"expected YAML object: {path}")
        return {}
    return data


def frontmatter(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else {}


def valid_minisign_public_key(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lower().startswith(("untrusted comment:", "trusted comment:"))
    ]
    if len(lines) != 1:
        return False
    try:
        decoded = base64.b64decode(lines[0], validate=True)
    except (ValueError, binascii.Error):
        return False
    return len(decoded) == 42 and decoded[:2] in {b"Ed", b"ED"}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    errors: list[str] = []
    entity_file = root / "entity.yaml"
    if entity_file.is_file():
        entity = load_yaml(entity_file, errors).get("id")
    else:
        entity = None
        errors.append(f"missing required file: {entity_file}")
    lock = load_yaml(root / ".multiplai" / "core.lock.yaml", errors)
    locked = lock.get("sops", [])
    core = lock.get("core", {})
    if not isinstance(locked, list) or any(not isinstance(item, str) or not SOP_ID.fullmatch(item) for item in locked):
        errors.append("core lock has invalid sops")
        locked = []
    if len(locked) != len(set(locked)):
        errors.append("core lock has duplicate SOP ids")
    if not isinstance(core, dict) or not re.fullmatch(r"[0-9a-f]{40}", str(core.get("commit", ""))):
        errors.append("core lock has invalid commit")
    if not isinstance(core, dict) or not re.fullmatch(r"sha256:[0-9a-f]{64}", str(core.get("digest", ""))):
        errors.append("core lock has invalid digest")

    local_ids: set[str] = set()
    local_root = root / "sops"
    if local_root.is_dir():
        for package in sorted(local_root.iterdir()):
            if not package.is_dir():
                continue
            sop_id = package.name
            local_ids.add(sop_id)
            metadata = load_yaml(package / "sop.yaml", errors)
            skill_meta = frontmatter(package / "SKILL.md")
            if metadata.get("id") != sop_id:
                errors.append(f"local SOP id/path mismatch: {sop_id}")
            if skill_meta.get("name") != sop_id or not str(skill_meta.get("description", "")).strip():
                errors.append(f"invalid local SKILL.md frontmatter: {sop_id}")
    duplicate = local_ids.intersection(locked)
    if duplicate:
        errors.append("duplicate local/core SOP ids: " + ", ".join(sorted(duplicate)))

    bindings = root / "config" / "sop-bindings"
    if bindings.is_dir():
        for path in sorted(bindings.glob("*.yaml")):
            sop_id = path.stem
            data = load_yaml(path, errors)
            if sop_id in local_ids:
                errors.append(f"local SOP must not have a binding: {path}")
            if sop_id not in locked:
                errors.append(f"binding targets unlocked core SOP: {path}")
            if data.get("sop_id") != sop_id or data.get("entity") != entity:
                errors.append(f"binding identity mismatch: {path}")
            if not isinstance(data.get("values"), dict) or not data.get("values"):
                errors.append(f"binding values must be non-empty; otherwise delete it: {path}")
            if {"steps", "procedure", "instructions", "runbook"}.intersection(data):
                errors.append(f"binding contains procedure prose: {path}")

    expected = local_ids.union(locked)
    adapters = root / ".agents" / "skills"
    actual = {path.name for path in adapters.iterdir() if path.is_dir()} if adapters.is_dir() else set()
    if actual != expected:
        errors.append("generated adapter set does not match local SOPs plus core lock")
    for sop_id in sorted(expected):
        path = adapters / sop_id / "SKILL.md"
        metadata = frontmatter(path)
        if metadata.get("name") != sop_id or not str(metadata.get("description", "")).strip():
            errors.append(f"invalid generated adapter: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        expected_pointer = (
            f"sops/{sop_id}/SKILL.md"
            if sop_id in local_ids
            else '$ROOT/.multiplai/tools/resolve_sop.py'
        )
        if expected_pointer not in text:
            errors.append(f"generated adapter has wrong ownership pointer: {path}")

    bootstrap = root / ".multiplai" / "tools"
    for directory in (root / ".multiplai", bootstrap, root / ".multiplai" / "trust"):
        if directory.is_symlink():
            errors.append(f"consumer bootstrap directory must not be a symlink: {directory}")
    for name in BOOTSTRAP_MODULES:
        path = bootstrap / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing or unsafe consumer bootstrap module: {path}")
    trust_root = root / ".multiplai" / "trust" / "minisign.pub"
    if not valid_minisign_public_key(trust_root):
        errors.append(f"missing or invalid pinned core trust root: {trust_root}")

    tracked = subprocess.run(
        ["git", "ls-files", ".multiplai/core.install.json", ".multiplai/installed-core"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked.returncode:
        errors.append("cannot inspect tracked core installation state")
    elif tracked.stdout.strip():
        errors.append("machine-owned core installation state must not be tracked")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"consumer SOP layout valid: {len(local_ids)} local, {len(locked)} core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
