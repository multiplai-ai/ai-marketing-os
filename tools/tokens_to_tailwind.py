#!/usr/bin/env python3
"""
tokens_to_tailwind.py — Translate W3C DTCG design tokens to a Tailwind CSS config.

Reads a tokens.json file in W3C Design Tokens Community Group format and
generates a tailwind.config.js with theme.extend populated from the tokens.

Usage:
    python tokens_to_tailwind.py tokens.json
    python tokens_to_tailwind.py tokens.json --output tailwind.config.js
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def camel_to_kebab(name: str) -> str:
    """Convert camelCase or PascalCase to kebab-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    return s.lower()


def get_value(node: dict):
    """Return the $value from a token node, or None."""
    return node.get("$value")


def is_token(node: dict) -> bool:
    """A node is a token if it contains '$value'."""
    return isinstance(node, dict) and "$value" in node


def parse_font_family(value: str) -> list[str]:
    """Split a CSS font-family string into a list of individual font names."""
    parts = [p.strip().strip("'\"") for p in value.split(",")]
    return [p for p in parts if p]


def js_string(value) -> str:
    """Format a Python value as a JS literal string."""
    if isinstance(value, str):
        return f"'{value}'"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return f"'{value}'"


def indent(level: int) -> str:
    return "  " * level


# ---------------------------------------------------------------------------
# Section builders — each returns a list of JS source lines
# ---------------------------------------------------------------------------

def build_colors(colors: dict) -> list[str]:
    """Build the colors object entries."""
    lines = []
    for group_name, group in sorted(colors.items()):
        if not isinstance(group, dict):
            continue
        if is_token(group):
            key = camel_to_kebab(group_name)
            lines.append(f"{indent(4)}'{key}': {js_string(get_value(group))},")
            continue
        for token_name, token in sorted(group.items()):
            if not is_token(token if isinstance(token, dict) else {}):
                continue
            key = f"{camel_to_kebab(group_name)}-{camel_to_kebab(token_name)}"
            lines.append(f"{indent(4)}'{key}': {js_string(get_value(token))},")
    return lines


def build_font_family(typography: dict) -> list[str]:
    """Build the fontFamily object entries. Deduplicates by value."""
    lines = []
    seen_values: set[str] = set()

    for level_name, level in typography.items():
        if not isinstance(level, dict):
            continue
        ff = level.get("fontFamily")
        if not is_token(ff if isinstance(ff, dict) else {}):
            continue
        raw = get_value(ff)
        if raw in seen_values:
            continue
        seen_values.add(raw)
        parts = parse_font_family(raw)
        label = camel_to_kebab(level_name)
        arr = ", ".join(js_string(p) for p in parts)
        lines.append(f"{indent(4)}'{label}': [{arr}],")

    return lines


def build_font_size(typography: dict) -> list[str]:
    """Build the fontSize object entries with line-height/letter-spacing/weight metadata."""
    lines = []

    for level_name, level in typography.items():
        if not isinstance(level, dict):
            continue
        fs_token = level.get("fontSize")
        if not is_token(fs_token if isinstance(fs_token, dict) else {}):
            continue

        size = get_value(fs_token)
        kebab = camel_to_kebab(level_name)

        # Gather optional metadata
        meta_parts: list[str] = []

        lh = level.get("lineHeight")
        if is_token(lh if isinstance(lh, dict) else {}):
            meta_parts.append(f"lineHeight: {js_string(str(get_value(lh)))}")

        ls = level.get("letterSpacing")
        if is_token(ls if isinstance(ls, dict) else {}):
            meta_parts.append(f"letterSpacing: {js_string(str(get_value(ls)))}")

        fw = level.get("fontWeight")
        if is_token(fw if isinstance(fw, dict) else {}):
            meta_parts.append(f"fontWeight: {js_string(str(get_value(fw)))}")

        if meta_parts:
            meta = ", ".join(meta_parts)
            lines.append(
                f"{indent(4)}'{kebab}': [{js_string(size)}, {{ {meta} }}],"
            )
        else:
            lines.append(f"{indent(4)}'{kebab}': {js_string(size)},")

    return lines


def build_spacing(spacing: dict) -> list[str]:
    """Build spacing entries from the scale array."""
    lines = []

    scale = spacing.get("scale")
    if is_token(scale if isinstance(scale, dict) else {}):
        values = get_value(scale)
        if isinstance(values, list):
            for i, val in enumerate(values, start=1):
                unit = "px" if isinstance(val, (int, float)) else ""
                lines.append(f"{indent(4)}'{i}': '{val}{unit}',")

    # Any other individual spacing tokens
    for key, token in spacing.items():
        if key in ("base", "scale"):
            continue
        if is_token(token if isinstance(token, dict) else {}):
            lines.append(f"{indent(4)}'{camel_to_kebab(key)}': {js_string(get_value(token))},")

    return lines


def build_border_radius(shape: dict) -> list[str]:
    """Build borderRadius entries."""
    lines = []

    radius_map = {
        "borderRadius": "DEFAULT",
        "cardRadius": "card",
    }

    for key, label in radius_map.items():
        token = shape.get(key)
        if is_token(token if isinstance(token, dict) else {}):
            lines.append(f"{indent(4)}'{label}': {js_string(get_value(token))},")

    return lines


def build_box_shadow(shape: dict) -> list[str]:
    """Build boxShadow entries."""
    lines = []
    token = shape.get("shadow")
    if is_token(token if isinstance(token, dict) else {}):
        lines.append(f"{indent(4)}'{js_string('DEFAULT')}': {js_string(get_value(token))},")
    # Fix: the key shouldn't be double-quoted — correct approach
    lines_fixed = []
    if is_token(token if isinstance(token, dict) else {}):
        lines_fixed.append(f"{indent(4)}'DEFAULT': {js_string(get_value(token))},")
    return lines_fixed


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_tailwind_config(tokens: dict) -> str:
    """Build the full tailwind.config.js string."""
    brand_name = ""
    brand_section = tokens.get("brand", {})
    name_token = brand_section.get("name")
    if is_token(name_token if isinstance(name_token, dict) else {}):
        brand_name = get_value(name_token)

    header = ["// Generated from tokens.json -- do not edit manually"]
    if brand_name:
        header.append(f"// Brand: {brand_name}")
    header.append("")
    header.append("/** @type {import('tailwindcss').Config} */")
    header.append("module.exports = {")
    header.append(f"{indent(1)}theme: {{")
    header.append(f"{indent(2)}extend: {{")

    sections: list[str] = []

    # Colors
    if "color" in tokens:
        color_lines = build_colors(tokens["color"])
        if color_lines:
            sections.append(f"{indent(3)}colors: {{")
            sections.extend(color_lines)
            sections.append(f"{indent(3)}}},")

    # Font Family
    if "typography" in tokens:
        ff_lines = build_font_family(tokens["typography"])
        if ff_lines:
            sections.append(f"{indent(3)}fontFamily: {{")
            sections.extend(ff_lines)
            sections.append(f"{indent(3)}}},")

    # Font Size
    if "typography" in tokens:
        fs_lines = build_font_size(tokens["typography"])
        if fs_lines:
            sections.append(f"{indent(3)}fontSize: {{")
            sections.extend(fs_lines)
            sections.append(f"{indent(3)}}},")

    # Spacing
    if "spacing" in tokens:
        sp_lines = build_spacing(tokens["spacing"])
        if sp_lines:
            sections.append(f"{indent(3)}spacing: {{")
            sections.extend(sp_lines)
            sections.append(f"{indent(3)}}},")

    # Border Radius
    if "shape" in tokens:
        br_lines = build_border_radius(tokens["shape"])
        if br_lines:
            sections.append(f"{indent(3)}borderRadius: {{")
            sections.extend(br_lines)
            sections.append(f"{indent(3)}}},")

    # Box Shadow
    if "shape" in tokens:
        bs_lines = build_box_shadow(tokens["shape"])
        if bs_lines:
            sections.append(f"{indent(3)}boxShadow: {{")
            sections.extend(bs_lines)
            sections.append(f"{indent(3)}}},")

    footer = [
        f"{indent(2)}}},",
        f"{indent(1)}}},",
        "};",
    ]

    all_lines = header + sections + footer
    return "\n".join(all_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Translate W3C DTCG tokens.json to a Tailwind CSS config."
    )
    parser.add_argument("tokens", help="Path to tokens.json")
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
        default=None,
    )
    args = parser.parse_args()

    tokens_path = Path(args.tokens)
    if not tokens_path.exists():
        print(f"Error: {tokens_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(tokens_path, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    config = build_tailwind_config(tokens)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(config)
        # Count sections
        section_count = sum(1 for line in config.splitlines() if line.strip().endswith("{") and "extend" not in line and "theme" not in line and "module" not in line)
        print(f"Tailwind config generated: {section_count} sections -> {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(config)
        section_count = sum(1 for line in config.splitlines() if line.strip().endswith("{") and "extend" not in line and "theme" not in line and "module" not in line)
        print(f"\nTailwind config generated: {section_count} sections -> stdout", file=sys.stderr)


if __name__ == "__main__":
    main()
