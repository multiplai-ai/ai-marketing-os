#!/usr/bin/env python3
"""Validate canonical SOP schema, discovery metadata, references and adapter drift."""
from __future__ import annotations

import argparse
import re
from pathlib import Path, PurePosixPath

import yaml
from jsonschema import Draft202012Validator

if __package__:
    from .generate_adapters import adapter_drift, frontmatter
else:
    from generate_adapters import adapter_drift, frontmatter


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def declared_file(root: Path, reference: str) -> bool:
    """Require a real repository-local file, including when symlinks are present."""
    path = PurePosixPath(reference)
    return (
        not path.is_absolute() and ".." not in path.parts and "\\" not in reference
        and (root / reference).is_file()
        and (root / reference).resolve().is_relative_to(root.resolve())
    )


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not (root / "sops").is_dir():
        return ["missing sops directory"]
    try:
        schema = read_yaml(root / "schemas/sop.schema.yaml")
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
    except Exception as exc:
        return [f"cannot load SOP schema: {exc}"]
    seen = set()
    for package in sorted((root / "sops").iterdir()):
        if not package.is_dir():
            continue
        sid = package.name
        seen.add(sid)
        skill, meta = package / "SKILL.md", package / "sop.yaml"
        if not skill.is_file() or not meta.is_file():
            errors.append(f"incomplete SOP package: {sid}")
            continue
        try:
            data = read_yaml(meta)
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{sid}: invalid metadata YAML: {exc}")
            continue
        for error in validator.iter_errors(data):
            location = ".".join(str(p) for p in error.absolute_path) or "metadata"
            errors.append(f"{sid}: {location}: {error.message}")
        if isinstance(data, dict):
            if data.get("id") != sid:
                errors.append(f"SOP id/path mismatch: {sid}")
            tests = data.get("tests", [])
            if isinstance(tests, list):
                for reference in tests:
                    if isinstance(reference, str) and not declared_file(root, reference):
                        errors.append(f"{sid}: missing or nonlocal declared test {reference}")
        text = skill.read_text(encoding="utf-8")
        try:
            header = frontmatter(text)
            if header.get("name") != sid:
                errors.append(f"{sid}: SKILL.md frontmatter name must match id")
            description = header.get("description")
            if not isinstance(description, str) or not description.strip():
                errors.append(f"{sid}: SKILL.md frontmatter requires a nonempty description")
        except ValueError as exc:
            errors.append(f"{sid}: {exc}")
        for reference in re.findall(r"tools/([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.(?:py|sh|json))", text):
            if not declared_file(root, "tools/" + reference):
                errors.append(f"{sid}: missing tool {reference}")
        for reference in re.findall(r"\]\(((?:references|fixtures)/[^\s)#]+)(?:#[^\s)]*)?\)", text):
            if not declared_file(package, reference):
                errors.append(f"{sid}: missing package reference {reference}")
    for path in (root / "sops/manifest.yaml", root / "provenance.yaml"):
        try:
            data = read_yaml(path)
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"cannot read {path.relative_to(root)}: {exc}")
            continue
        if path.name == "manifest.yaml":
            declared = data.get("sops") if isinstance(data, dict) else None
            if not isinstance(declared, list) or any(not isinstance(x, str) for x in declared) or set(declared) != seen or len(declared) != len(seen):
                errors.append("sops/manifest.yaml does not match canonical SOP packages")
        elif not isinstance(data, dict) or data.get("sop_count") != len(seen):
            errors.append("provenance.yaml sop_count does not match canonical SOP packages")
    try:
        errors.extend(adapter_drift(root))
    except (OSError, ValueError) as exc:
        errors.append(f"cannot validate generated adapters: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print(f"SOP canon valid: {len(list((args.root / 'sops').glob('*/sop.yaml')))} packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
