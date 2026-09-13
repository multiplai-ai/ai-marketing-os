#!/usr/bin/env python3
"""
tokens_to_css.py — Translate W3C DTCG design tokens to CSS custom properties.

Reads a tokens.json file in W3C Design Tokens Community Group format and
generates a :root block of CSS custom properties.

Usage:
    python tokens_to_css.py tokens.json
    python tokens_to_css.py tokens.json --output styles/tokens.css
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


# ---------------------------------------------------------------------------
# Section generators
# ---------------------------------------------------------------------------

def generate_color_vars(colors: dict) -> list[str]:
    """Generate --color-{group}-{name} variables from the color section."""
    lines = []
    for group_name, group in sorted(colors.items()):
        if not isinstance(group, dict):
            continue
        # If the group itself is a token (unlikely but safe)
        if is_token(group):
            var = f"--color-{camel_to_kebab(group_name)}"
            lines.append(f"  {var}: {get_value(group)};")
            continue
        # Group header
        header = group_name.replace("_", " ").title()
        lines.append(f"\n  /* Colors -- {header} */")
        for token_name, token in sorted(group.items()):
            if not is_token(token):
                continue
            var = f"--color-{camel_to_kebab(group_name)}-{camel_to_kebab(token_name)}"
            lines.append(f"  {var}: {get_value(token)};")
    return lines


def generate_typography_vars(typography: dict) -> list[str]:
    """Generate font-family shorthand vars and per-level type-scale vars."""
    lines = []

    # Collect unique font families for shorthand vars
    families_seen: dict[str, str] = {}  # display label -> value
    for level_name, level in typography.items():
        if not isinstance(level, dict):
            continue
        ff = level.get("fontFamily")
        if is_token(ff if isinstance(ff, dict) else {}):
            label = camel_to_kebab(level_name)
            value = get_value(ff)
            if value and value not in families_seen.values():
                families_seen[label] = value

    if families_seen:
        lines.append("\n  /* Typography -- Font Families */")
        for label, value in families_seen.items():
            lines.append(f"  --font-{label}: {value};")

    # Per-level type scale
    prop_map = {
        "fontSize": "size",
        "fontWeight": "weight",
        "lineHeight": "line-height",
        "letterSpacing": "letter-spacing",
    }

    lines.append("\n  /* Typography -- Type Scale */")
    for level_name, level in typography.items():
        if not isinstance(level, dict):
            continue
        kebab_level = camel_to_kebab(level_name)
        for prop_key, css_suffix in prop_map.items():
            token = level.get(prop_key)
            if is_token(token if isinstance(token, dict) else {}):
                val = get_value(token)
                lines.append(f"  --text-{kebab_level}-{css_suffix}: {val};")

    return lines


def generate_spacing_vars(spacing: dict) -> list[str]:
    """Generate spacing variables from base and scale."""
    lines = ["\n  /* Spacing */"]

    base = spacing.get("base")
    if is_token(base if isinstance(base, dict) else {}):
        lines.append(f"  --spacing-base: {get_value(base)};")

    scale = spacing.get("scale")
    if is_token(scale if isinstance(scale, dict) else {}):
        values = get_value(scale)
        if isinstance(values, list):
            for i, val in enumerate(values, start=1):
                unit = "px" if isinstance(val, (int, float)) else ""
                lines.append(f"  --spacing-{i}: {val}{unit};")

    # Handle any other spacing tokens
    for key, token in spacing.items():
        if key in ("base", "scale"):
            continue
        if is_token(token if isinstance(token, dict) else {}):
            lines.append(f"  --spacing-{camel_to_kebab(key)}: {get_value(token)};")

    return lines


def generate_shape_vars(shape: dict) -> list[str]:
    """Generate shape/border/shadow variables."""
    lines = ["\n  /* Shape */"]

    key_map = {
        "borderRadius": "--border-radius",
        "cardRadius": "--card-radius",
        "borderWidth": "--border-width",
        "borderColor": "--border-color",
        "shadow": "--shadow",
    }

    for token_name, token in shape.items():
        if not is_token(token if isinstance(token, dict) else {}):
            continue
        var = key_map.get(token_name, f"--shape-{camel_to_kebab(token_name)}")
        lines.append(f"  {var}: {get_value(token)};")

    return lines


def generate_button_vars(buttons: dict) -> list[str]:
    """Generate button variant variables."""
    lines = ["\n  /* Buttons */"]

    prop_map = {
        "background": "bg",
        "text": "text",
        "fontFamily": "font",
        "fontStyle": "font-style",
        "fontWeight": "font-weight",
        "fontSize": "font-size",
        "borderRadius": "radius",
        "border": "border",
    }

    for variant_name, variant in sorted(buttons.items()):
        if not isinstance(variant, dict):
            continue
        if is_token(variant):
            continue

        kebab_variant = camel_to_kebab(variant_name)

        # Check for paddingVertical + paddingHorizontal to combine
        pv = variant.get("paddingVertical")
        ph = variant.get("paddingHorizontal")
        has_combined_padding = (
            is_token(pv if isinstance(pv, dict) else {})
            and is_token(ph if isinstance(ph, dict) else {})
        )

        for prop_key, token in variant.items():
            if not is_token(token if isinstance(token, dict) else {}):
                continue

            # Skip individual padding props if we'll combine them
            if prop_key in ("paddingVertical", "paddingHorizontal") and has_combined_padding:
                continue

            css_suffix = prop_map.get(prop_key, camel_to_kebab(prop_key))
            var = f"  --btn-{kebab_variant}-{css_suffix}"
            lines.append(f"{var}: {get_value(token)};")

        # Combined padding
        if has_combined_padding:
            pv_val = get_value(pv)
            ph_val = get_value(ph)
            lines.append(f"  --btn-{kebab_variant}-padding: {pv_val} {ph_val};")

    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_css(tokens: dict) -> str:
    """Build the full CSS string from the parsed tokens dict."""
    brand_name = ""
    brand_section = tokens.get("brand", {})
    name_token = brand_section.get("name")
    if is_token(name_token if isinstance(name_token, dict) else {}):
        brand_name = get_value(name_token)

    header_lines = ["/* Generated from tokens.json -- do not edit manually */"]
    if brand_name:
        header_lines.append(f"/* Brand: {brand_name} */")
    header_lines.append("")
    header_lines.append(":root {")

    body_lines: list[str] = []

    # Colors
    if "color" in tokens:
        body_lines.extend(generate_color_vars(tokens["color"]))

    # Typography
    if "typography" in tokens:
        body_lines.extend(generate_typography_vars(tokens["typography"]))

    # Spacing
    if "spacing" in tokens:
        body_lines.extend(generate_spacing_vars(tokens["spacing"]))

    # Shape
    if "shape" in tokens:
        body_lines.extend(generate_shape_vars(tokens["shape"]))

    # Buttons
    if "button" in tokens:
        body_lines.extend(generate_button_vars(tokens["button"]))

    footer = ["}"]

    all_lines = header_lines + body_lines + [""] + footer
    return "\n".join(all_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Translate W3C DTCG tokens.json to CSS custom properties."
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

    css = build_css(tokens)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(css)
        # Count variables generated
        var_count = css.count("--")
        print(f"CSS generated: {var_count} custom properties -> {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(css)
        var_count = css.count("--")
        print(f"\nCSS generated: {var_count} custom properties -> stdout", file=sys.stderr)


if __name__ == "__main__":
    main()
