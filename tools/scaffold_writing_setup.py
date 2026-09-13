#!/usr/bin/env python3
"""Scaffold portable, consumer-owned writing configuration."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import yaml


CORE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = CORE_ROOT / "templates" / "writing"


@dataclass(frozen=True)
class SetupResult:
    profile_path: Path
    catalog_path: Path
    primary_long_form_asset_type: None
    asset_type_ids: tuple[str, ...]
    created_paths: tuple[Path, ...]
    preserved_paths: tuple[Path, ...]


def _write(path: Path, content: str, *, replace: bool, created: list[Path], preserved: list[Path]) -> None:
    if path.exists() and not replace:
        preserved.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path)


def _copy(source: Path, destination: Path, *, replace: bool, created: list[Path], preserved: list[Path]) -> None:
    _write(destination, source.read_text(encoding="utf-8"), replace=replace, created=created, preserved=preserved)


def scaffold_setup(root: Path, mode: str = "initial", *, replace: bool = False) -> SetupResult:
    """Create defaults while preserving existing consumer decisions by default."""
    if mode not in {"initial", "incremental"}:
        raise ValueError("mode must be initial or incremental")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    config = root / "config" / "writing"
    created: list[Path] = []
    preserved: list[Path] = []
    file_map = {
        TEMPLATE_ROOT / "blog-article/editorial-brief.template.md": config / "briefs/default-blog.md",
        TEMPLATE_ROOT / "blog-article/draft.template.md": config / "templates/default-blog.md",
        TEMPLATE_ROOT / "blog-article/editorial-standard.template.md": config / "standards/default-blog.md",
        TEMPLATE_ROOT / "newsletter/editorial-brief.template.md": config / "briefs/default-newsletter.md",
        TEMPLATE_ROOT / "newsletter/draft.template.md": config / "templates/default-newsletter.md",
        TEMPLATE_ROOT / "newsletter/editorial-standard.template.md": config / "standards/default-newsletter.md",
        TEMPLATE_ROOT / "social-post-type.template.md": config / "social/post-type-candidate.md",
    }
    for source, destination in file_map.items():
        _copy(source, destination, replace=replace, created=created, preserved=preserved)
    voice_guide = config / "voice-guide.md"
    _write(
        voice_guide,
        "# Voice guide\n\nRecord the author's natural language, useful tendencies, boundaries, and review notes here.\n",
        replace=replace,
        created=created,
        preserved=preserved,
    )
    candidates = config / "exemplar-candidates.yaml"
    _write(
        candidates,
        yaml.safe_dump({"schema_version": 1, "good_exemplars": [], "bad_exemplars": [], "approved": False}, sort_keys=False),
        replace=replace,
        created=created,
        preserved=preserved,
    )
    profile = {
        "schema_version": 1,
        "author_id": "configure-author-id",
        "voice_guide_ref": "config/writing/voice-guide.md",
        "good_exemplars": [],
        "bad_exemplars": [],
        "default_output_root": "content/writing",
        "additional_quality_gate_refs": [],
    }
    assets = [
        {
            "id": "default-blog",
            "kind": "long_form",
            "editorial_brief_ref": "config/writing/briefs/default-blog.md",
            "template_ref": "config/writing/templates/default-blog.md",
            "standards_refs": ["config/writing/standards/default-blog.md"],
            "good_exemplar_refs": [],
            "bad_exemplar_refs": [],
            "required_inputs": ["editorial_source_packet"],
            "quality_gates": ["human-writing-standard"],
        },
        {
            "id": "default-newsletter",
            "kind": "long_form",
            "editorial_brief_ref": "config/writing/briefs/default-newsletter.md",
            "template_ref": "config/writing/templates/default-newsletter.md",
            "standards_refs": ["config/writing/standards/default-newsletter.md"],
            "good_exemplar_refs": [],
            "bad_exemplar_refs": [],
            "required_inputs": ["editorial_source_packet"],
            "quality_gates": ["human-writing-standard"],
        },
    ]
    profile_path = config / "writing-profile.yaml"
    catalog_path = config / "writing-asset-catalog.yaml"
    _write(profile_path, yaml.safe_dump(profile, sort_keys=False), replace=replace, created=created, preserved=preserved)
    _write(catalog_path, yaml.safe_dump({"schema_version": 1, "asset_types": assets}, sort_keys=False), replace=replace, created=created, preserved=preserved)
    return SetupResult(profile_path, catalog_path, None, tuple(item["id"] for item in assets), tuple(created), tuple(preserved))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-root", required=True, type=Path)
    parser.add_argument("--mode", choices=["initial", "incremental"], default="initial")
    parser.add_argument("--replace", action="store_true", help="Explicitly replace existing scaffold files")
    args = parser.parse_args(argv)
    try:
        result = scaffold_setup(args.consumer_root, args.mode, replace=args.replace)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"profile: {result.profile_path}")
    print(f"catalog: {result.catalog_path}")
    print("asset types: " + ", ".join(result.asset_type_ids))
    print(f"created: {len(result.created_paths)}; preserved: {len(result.preserved_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
