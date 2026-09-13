#!/usr/bin/env python3
"""Generate discoverable pointers; canonical instructions stay in sops/<id>/SKILL.md.

These adapters are for use inside the complete Core checkout. Consumer installs
must use tools/install_core_bundle.py and tools/generate_consumer_adapters.py instead.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md requires YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid SKILL.md frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    allowed = {"name", "description", "license", "allowed-tools", "metadata"}
    if set(data) - allowed:
        raise ValueError("custom SKILL.md frontmatter fields belong under metadata")
    name = data.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64:
        raise ValueError("SKILL.md name must be a string of 1–64 characters")
    description = data.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise ValueError("SKILL.md description must be a nonempty string of at most 1024 characters")
    if "<" in description or ">" in description:
        raise ValueError("SKILL.md description must not contain angle brackets")
    return data


def expected_adapters(root: Path) -> dict[Path, str]:
    expected = {}
    for package in sorted((root / "sops").iterdir()):
        if not package.is_dir():
            continue
        skill = package / "SKILL.md"
        if not skill.is_file() or not (package / "sop.yaml").is_file():
            raise ValueError(f"incomplete SOP package: {package.name}")
        data = frontmatter(skill.read_text(encoding="utf-8"))
        if data.get("name") != package.name:
            raise ValueError(f"{package.name}: frontmatter name must match package")
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{package.name}: frontmatter requires a nonempty description")
        header = yaml.safe_dump(
            {"name": package.name, "description": description},
            sort_keys=False, allow_unicode=True, width=1000,
        )
        expected[Path(package.name) / "SKILL.md"] = (
            f"---\n{header}---\n\n# Generated adapter: {package.name}\n\n"
            f"Read and follow the canonical source: `sops/{package.name}/SKILL.md` "
            "from the Core repository root. Resolve its package references relative "
            "to that canonical directory.\n\n"
            "This pointer requires the complete Core checkout. Do not install it "
            "as a standalone skill or edit it; regenerate with "
            "`python tools/generate_adapters.py .`.\n"
        )
    return expected


def adapter_drift(root: Path, expected: dict[Path, str] | None = None) -> list[str]:
    expected = expected_adapters(root) if expected is None else expected
    out = root / "generated/codex/skills"
    if any(path.is_symlink() for path in (out, out.parent, out.parent.parent)):
        return ["generated output directories must not be symlinks"]
    actual = {p.relative_to(out) for p in out.rglob("*") if p.is_file() or p.is_symlink()}
    errors = [f"unexpected generated file: {p}" for p in sorted(actual - expected.keys())]
    for relative, content in expected.items():
        path = out / relative
        if path.is_symlink():
            errors.append(f"generated adapter must not be a symlink: {relative}")
        elif not path.is_file():
            errors.append(f"missing generated adapter: {relative}")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"generated adapter drift: {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="fail on drift without writing files")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        expected = expected_adapters(root)
        if args.check:
            errors = adapter_drift(root, expected)
            if errors:
                print("\n".join(errors))
                return 1
            print(f"generated adapters current: {len(expected)}")
            return 0
        out = root / "generated/codex/skills"
        if any(path.is_symlink() for path in (out, out.parent, out.parent.parent)):
            raise ValueError("generated output directories must not be symlinks")
        # This directory is generator-owned. Remove files only after all source
        # packages have been read successfully, so invalid inputs preserve output.
        for path in sorted(out.rglob("*"), reverse=True):
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        for relative, content in expected.items():
            path = out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"generated {len(expected)} adapters")
        return 0
    except (OSError, ValueError) as exc:
        print(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
