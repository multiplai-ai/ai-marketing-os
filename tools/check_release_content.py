#!/usr/bin/env python3
"""Check source or unpacked member distribution contents without network access."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from release_content import content_issues, included, path_issue


def check(root: Path) -> list[str]:
    # Extracted member archives deliberately have no .git directory. Scan the
    # whole archive boundary there, including files outside the allowlist.
    if not (root / ".git").exists():
        return check_unpacked(root)
    records = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "-z"])
    errors = []
    for record in records.split(b"\0"):
        if not record:
            continue
        meta, name = record.split(b"\t", 1)
        path = name.decode("utf-8")
        mode, _, stage = meta.decode().split()
        issue = path_issue(path)
        if issue:
            errors.append(f"{path}: {issue}")
        if mode not in {"100644", "100755"} or stage != "0":
            errors.append(f"{path}: non-regular or unresolved Git entry")
        if not included(path):
            continue
        source = root / path
        if source.is_symlink() or not source.is_file():
            errors.append(f"{path}: tracked distribution input is missing or is not a regular file")
            continue
        errors.extend(f"{path}: {issue}" for issue in content_issues(path, source.read_bytes()))
    return errors


def check_unpacked(root: Path) -> list[str]:
    errors = []
    for source in sorted(root.rglob("*")):
        relative = source.relative_to(root)
        # Running Python/pytest creates these after extraction. The builder
        # independently rejects any such tracked input before packaging.
        if set(relative.parts) & {"__pycache__", ".pytest_cache"}:
            continue
        path = relative.as_posix()
        if source.is_symlink():
            errors.append(f"{path}: symlink is not a release input")
            continue
        if source.is_dir():
            continue
        if not source.is_file():
            errors.append(f"{path}: not a regular release input")
            continue
        issue = path_issue(path)
        if issue:
            errors.append(f"{path}: {issue}")
        if not included(path):
            errors.append(f"{path}: outside member distribution policy")
        errors.extend(f"{path}: {issue}" for issue in content_issues(path, source.read_bytes()))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("release content: pass (member-distribution inputs; not a rights or access review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
