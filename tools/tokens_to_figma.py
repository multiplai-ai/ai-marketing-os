#!/usr/bin/env python3
"""
tokens_to_figma.py — Convert W3C Design Tokens to Figma Tokens Studio format.

Reads tokens.json and outputs a JSON file compatible with the Figma Tokens
Studio plugin.

Usage:
    python3 tools/tokens_to_figma.py tokens.json
    python3 tools/tokens_to_figma.py tokens.json --output generated/figma-tokens.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


WEIGHT_MAP = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black",
}


def extract_value(token):
    """Extract $value from a token dict."""
    if isinstance(token, dict) and '$value' in token:
        return token['$value']
    return None


def extract_desc(token):
    """Extract $description from a token dict."""
    if isinstance(token, dict) and '$description' in token:
        return token['$description']
    return None


def strip_px(val):
    """Strip px suffix and return raw number string."""
    s = str(val)
    if s.endswith('px'):
        return s[:-2]
    return s


def line_height_to_pct(val):
    """Convert decimal line height to percentage string."""
    if isinstance(val, (int, float)):
        return f"{int(val * 100)}%"
    s = str(val)
    try:
        return f"{int(float(s) * 100)}%"
    except ValueError:
        return s


def letter_spacing_to_pct(val):
    """Convert em letter spacing to percentage. -0.02em -> -2%."""
    s = str(val)
    if s == '0' or s == '0em':
        return "0%"
    if s.endswith('em'):
        try:
            num = float(s[:-2])
            return f"{int(num * 100)}%"
        except ValueError:
            return s
    return s


def weight_to_name(val):
    """Convert numeric weight to name."""
    if isinstance(val, (int, float)):
        return WEIGHT_MAP.get(int(val), str(int(val)))
    return str(val)


def first_font(val):
    """Extract first font from comma-separated font family."""
    return str(val).split(',')[0].strip()


def parse_shadow(val):
    """Parse CSS shadow string into structured Tokens Studio format."""
    s = str(val).strip()
    # Match: x y blur spread? color
    # e.g. "0 1px 3px rgba(49,38,59,0.06)"
    rgba_match = re.match(
        r'(-?\d+(?:px)?)\s+(-?\d+(?:px)?)\s+(\d+(?:px)?)(?:\s+(\d+(?:px)?))?\s+(rgba?\([^)]+\)|#[0-9a-fA-F]+)',
        s
    )
    if rgba_match:
        x, y, blur = rgba_match.group(1), rgba_match.group(2), rgba_match.group(3)
        spread = rgba_match.group(4) or "0"
        color = rgba_match.group(5)
        return {
            "value": {
                "x": strip_px(x),
                "y": strip_px(y),
                "blur": strip_px(blur),
                "spread": strip_px(spread),
                "color": color,
                "type": "dropShadow"
            },
            "type": "boxShadow"
        }
    return {"value": s, "type": "boxShadow"}


def convert_colors(colors: dict) -> dict:
    """Convert color tokens to Tokens Studio format."""
    result = {}
    for group_name, group in colors.items():
        if not isinstance(group, dict):
            continue
        group_result = {}
        for token_name, token in group.items():
            val = extract_value(token)
            if val is None:
                continue
            entry = {"value": str(val), "type": "color"}
            desc = extract_desc(token)
            if desc:
                entry["description"] = desc
            group_result[token_name] = entry
        if group_result:
            result[group_name] = group_result
    return result


def convert_typography(typography: dict) -> dict:
    """Convert typography tokens to Tokens Studio format."""
    result = {}
    for level_name, level in typography.items():
        if not isinstance(level, dict):
            continue

        level_result = {}

        font_family = extract_value(level.get('fontFamily', {}))
        if font_family:
            level_result["fontFamily"] = {"value": first_font(font_family), "type": "fontFamilies"}

        font_weight = extract_value(level.get('fontWeight', {}))
        if font_weight is not None:
            level_result["fontWeight"] = {"value": weight_to_name(font_weight), "type": "fontWeights"}

        font_size = extract_value(level.get('fontSize', {}))
        if font_size:
            level_result["fontSize"] = {"value": strip_px(font_size), "type": "fontSizes"}

        line_height = extract_value(level.get('lineHeight', {}))
        if line_height is not None:
            level_result["lineHeight"] = {"value": line_height_to_pct(line_height), "type": "lineHeights"}

        letter_spacing = extract_value(level.get('letterSpacing', {}))
        if letter_spacing is not None:
            level_result["letterSpacing"] = {"value": letter_spacing_to_pct(letter_spacing), "type": "letterSpacing"}

        if level_result:
            result[level_name] = level_result

    return result


def convert_spacing(spacing: dict) -> dict:
    """Convert spacing tokens to Tokens Studio format."""
    result = {}
    base = extract_value(spacing.get('base', {}))
    if base:
        result["base"] = {"value": strip_px(base), "type": "spacing"}

    scale = extract_value(spacing.get('scale', {}))
    if isinstance(scale, list):
        for i, val in enumerate(scale, 1):
            result[str(i)] = {"value": str(int(val) if isinstance(val, float) else val), "type": "spacing"}

    return result


def convert_shape(shape: dict) -> dict:
    """Convert shape tokens to Tokens Studio format."""
    result = {}

    border_radius = {}
    for name in ('borderRadius', 'cardRadius'):
        val = extract_value(shape.get(name, {}))
        if val:
            key = 'default' if name == 'borderRadius' else name.replace('Radius', '').lower()
            border_radius[key] = {"value": strip_px(val), "type": "borderRadius"}
    if border_radius:
        result["borderRadius"] = border_radius

    shadow_val = extract_value(shape.get('shadow', {}))
    if shadow_val:
        result["boxShadow"] = {"default": parse_shadow(shadow_val)}

    return result


def convert(tokens: dict) -> dict:
    """Convert W3C DTCG tokens to Figma Tokens Studio format."""
    brand = {}

    if 'color' in tokens:
        brand["color"] = convert_colors(tokens['color'])

    if 'typography' in tokens:
        brand["typography"] = convert_typography(tokens['typography'])

    if 'spacing' in tokens:
        brand["spacing"] = convert_spacing(tokens['spacing'])

    if 'shape' in tokens:
        brand.update(convert_shape(tokens['shape']))

    return {
        "$themes": [],
        "$metadata": {
            "tokenSetOrder": ["brand"]
        },
        "brand": brand
    }


def main():
    parser = argparse.ArgumentParser(description='Convert W3C design tokens to Figma Tokens Studio JSON')
    parser.add_argument('tokens_file', help='Path to tokens.json')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    args = parser.parse_args()

    tokens_path = Path(args.tokens_file)
    if not tokens_path.exists():
        print(f"Error: {tokens_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(tokens_path) as f:
        tokens = json.load(f)

    result = convert(tokens)
    output = json.dumps(result, indent=2)

    sections = len([k for k in result.get('brand', {}) if k not in ('$themes', '$metadata')])

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + '\n')
        print(f"Figma tokens generated: {sections} sections -> {args.output}", file=sys.stderr)
    else:
        print(output)
        print(f"Figma tokens generated: {sections} sections", file=sys.stderr)


if __name__ == '__main__':
    main()
