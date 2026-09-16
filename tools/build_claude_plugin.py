#!/usr/bin/env python3
"""Build a deterministic Claude plugin zip for nontechnical installation."""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path


INCLUDED_ROOT_FILES = {"README.md", "START-HERE.md", "LICENSE", "NOTICE", "NOTICE.md", "pyproject.toml"}
INCLUDED_DIRECTORIES = {".claude-plugin", "sops", "tools", "schemas", "runtime", "templates"}
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[0-9]+)?$")


def included(relative: Path) -> bool:
    if "__pycache__" in relative.parts or relative.suffix in {".pyc", ".pyo"}:
        return False
    return (
        relative.as_posix() in INCLUDED_ROOT_FILES
        or bool(relative.parts and relative.parts[0] in INCLUDED_DIRECTORIES)
    )


def build(root: Path, output: Path, version: str) -> Path:
    if not VERSION.fullmatch(version):
        raise ValueError("version must look like 1.2.3 or 1.2.3-rc.4")
    manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest.get("version") != version:
        raise ValueError("Claude plugin manifest version does not match requested version")

    files = [path for path in root.rglob("*") if path.is_file() and included(path.relative_to(root))]
    if any(path.is_symlink() for path in files):
        raise ValueError("Claude plugin package must not contain symlinks")

    output.mkdir(parents=True, exist_ok=True)
    target = output / f"ai-marketing-os-claude-plugin-{version}.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    print(build(args.root.resolve(), args.output.resolve(), args.version))


if __name__ == "__main__":
    main()
