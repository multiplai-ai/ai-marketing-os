#!/usr/bin/env python3
"""
tokens_to_pencil.py — Convert W3C Design Tokens to Pencil set_variables format.

Reads tokens.json and outputs a flat JSON list of variables for Pencil's
set_variables MCP tool.

Usage:
    python3 tools/tokens_to_pencil.py tokens.json
    python3 tools/tokens_to_pencil.py tokens.json --output generated/pencil-variables.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


def camel_to_kebab(name: str) -> str:
    """Convert camelCase to kebab-case."""
    s = re.sub(r'([A-Z])', r'-\1', name).lower()
    return s.lstrip('-')


def extract_value(token):
    """Extract $value from a token dict."""
    if isinstance(token, dict) and '$value' in token:
        return token['$value']
    return None


def extract_type(token):
    """Extract $type from a token dict, defaulting to 'string'."""
    if isinstance(token, dict) and '$type' in token:
        t = token['$type']
        if t in ('color',):
            return 'color'
        if t in ('dimension', 'fontWeight', 'number'):
            return 'dimension'
        return 'string'
    return 'string'


def flatten_colors(colors: dict, variables: list):
    """Flatten color tokens into variables list."""
    for group_name, group in colors.items():
        if not isinstance(group, dict):
            continue
        for token_name, token in group.items():
            val = extract_value(token)
            if val is None:
                continue
            name = f"color-{camel_to_kebab(group_name)}-{camel_to_kebab(token_name)}"
            variables.append({
                "name": name,
                "value": str(val),
                "type": "color"
            })


def flatten_typography(typography: dict, variables: list):
    """Flatten typography tokens. Deduplicate font families."""
    seen_fonts = {}

    for level_name, level in typography.items():
        if not isinstance(level, dict):
            continue

        prefix = f"typography-{camel_to_kebab(level_name)}"

        for prop_name, token in level.items():
            val = extract_value(token)
            if val is None:
                continue

            # Track unique font families
            if prop_name == 'fontFamily':
                font_key = str(val).split(',')[0].strip().lower()
                if font_key not in seen_fonts:
                    role = camel_to_kebab(level_name)
                    seen_fonts[font_key] = {
                        "name": f"font-{role}",
                        "value": str(val),
                        "type": "string"
                    }

            name = f"{prefix}-{camel_to_kebab(prop_name)}"
            variables.append({
                "name": name,
                "value": str(val),
                "type": extract_type(token)
            })

    # Add deduplicated font-family shortcuts
    for font_var in seen_fonts.values():
        variables.insert(0, font_var)


def flatten_spacing(spacing: dict, variables: list):
    """Flatten spacing tokens."""
    base = extract_value(spacing.get('base', {}))
    if base:
        variables.append({"name": "spacing-base", "value": str(base), "type": "dimension"})

    scale = extract_value(spacing.get('scale', {}))
    if isinstance(scale, list):
        for i, val in enumerate(scale, 1):
            v = f"{val}px" if isinstance(val, (int, float)) else str(val)
            variables.append({"name": f"spacing-{i}", "value": v, "type": "dimension"})


def flatten_shape(shape: dict, variables: list):
    """Flatten shape tokens."""
    for token_name, token in shape.items():
        val = extract_value(token)
        if val is None:
            continue
        name = f"shape-{camel_to_kebab(token_name)}"
        variables.append({
            "name": name,
            "value": str(val),
            "type": extract_type(token)
        })


def flatten_buttons(buttons: dict, variables: list):
    """Flatten button tokens."""
    for variant_name, variant in buttons.items():
        if not isinstance(variant, dict):
            continue
        for prop_name, token in variant.items():
            val = extract_value(token)
            if val is None:
                continue
            name = f"button-{camel_to_kebab(variant_name)}-{camel_to_kebab(prop_name)}"
            variables.append({
                "name": name,
                "value": str(val),
                "type": extract_type(token)
            })


def convert(tokens: dict) -> dict:
    """Convert W3C DTCG tokens to Pencil variables format."""
    variables = []

    if 'color' in tokens:
        flatten_colors(tokens['color'], variables)

    if 'typography' in tokens:
        flatten_typography(tokens['typography'], variables)

    if 'spacing' in tokens:
        flatten_spacing(tokens['spacing'], variables)

    if 'shape' in tokens:
        flatten_shape(tokens['shape'], variables)

    if 'button' in tokens:
        flatten_buttons(tokens['button'], variables)

    return {"variables": variables}


def main():
    parser = argparse.ArgumentParser(description='Convert W3C design tokens to Pencil variables JSON')
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

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + '\n')
        print(f"Pencil variables generated: {len(result['variables'])} variables -> {args.output}", file=sys.stderr)
    else:
        print(output)
        print(f"Pencil variables generated: {len(result['variables'])} variables", file=sys.stderr)


if __name__ == '__main__':
    main()
