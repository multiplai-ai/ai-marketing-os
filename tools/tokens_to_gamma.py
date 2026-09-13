#!/usr/bin/env python3
"""Translate W3C DTCG design tokens to Gamma-ready markdown prompts.

Reads a tokens.json file in W3C Design Tokens Community Group format
and generates a markdown file with structured Gamma prompts (Prompt A
for image style, Prompt B template for input text).

Usage:
    python tokens_to_gamma.py tokens.json
    python tokens_to_gamma.py tokens.json --output gamma-prompts.md
"""

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_value(token):
    """Return the $value of a token dict, or the dict/primitive itself."""
    if isinstance(token, dict) and "$value" in token:
        return token["$value"]
    return token


def _get_desc(token):
    """Return the $description of a token dict, or empty string."""
    if isinstance(token, dict):
        return token.get("$description", "")
    return ""


def _collect_colors(tokens):
    """Walk the 'color' section and return a flat list of (name, hex, usage)."""
    colors = []
    color_section = tokens.get("color", {})

    def _walk(node, prefix=""):
        if isinstance(node, dict):
            if "$value" in node:
                hex_val = node["$value"]
                desc = node.get("$description", "")
                colors.append((prefix, hex_val, desc))
            else:
                for key, child in node.items():
                    if key.startswith("$"):
                        continue
                    label = f"{prefix} {key}".strip() if prefix else key
                    _walk(child, label)

    _walk(color_section)
    return colors


def _collect_textures(tokens):
    """Return list of (name, opacity, description) from 'texture' section."""
    textures = []
    texture_section = tokens.get("texture", {})
    for name, token in texture_section.items():
        if name.startswith("$"):
            continue
        if isinstance(token, dict):
            opacity_tok = token.get("opacity", {})
            desc_tok = token.get("description", {})
            opacity = _get_value(opacity_tok) if isinstance(opacity_tok, dict) else opacity_tok
            desc = _get_value(desc_tok) if isinstance(desc_tok, dict) else desc_tok
            # If token itself is a leaf
            if "$value" in token:
                textures.append((name, "", _get_value(token)))
            else:
                textures.append((name, opacity or "", desc or ""))
    return textures


def _get_font(tokens, style):
    """Get fontFamily for a typography style (display, body, etc.)."""
    typo = tokens.get("typography", {})
    style_tok = typo.get(style, {})
    font_tok = style_tok.get("fontFamily", {})
    return _get_value(font_tok) if font_tok else ""


def _get_imagery(tokens, key):
    """Get a value from the imagery section."""
    imagery = tokens.get("imagery", {})
    tok = imagery.get(key, {})
    return _get_value(tok) if tok else ""


def _build_image_style(tokens, colors, textures):
    """Construct a Prompt A image style from token data when gammaImageStyle
    is not present."""
    parts = []

    # Color palette
    if colors:
        palette_items = [f"{name} ({hex_val})" for name, hex_val, _ in colors]
        parts.append(f"Color palette: {', '.join(palette_items)}.")

    # Textures
    if textures:
        tex_items = []
        for name, opacity, desc in textures:
            item = name
            if desc:
                item += f" ({desc})"
            if opacity:
                item += f" at {opacity} opacity"
            tex_items.append(item)
        parts.append(f"Textures: {', '.join(tex_items)}.")

    # Positive/negative keywords
    pos = _get_imagery(tokens, "positivePrompt")
    neg = _get_imagery(tokens, "negativePrompt")
    style = _get_imagery(tokens, "style")

    if style:
        parts.append(f"Style: {style}.")
    if pos:
        parts.append(f"Composition keywords: {pos}.")
    if neg:
        parts.append(f"Avoid: {neg}.")

    return " ".join(parts) if parts else "No image style data available in tokens."


def _build_brand_summary(tokens, colors, textures):
    """Build the brand guidelines summary block for Prompt B."""
    lines = []

    # Palette
    if colors:
        color_list = ", ".join(f"{name} {hex_val}" for name, hex_val, _ in colors)
        lines.append(f"- **Palette:** {color_list}")

    # Typography
    display_font = _get_font(tokens, "display")
    body_font = _get_font(tokens, "body")
    if display_font or body_font:
        display_str = display_font or "[not specified]"
        body_str = body_font or "[not specified]"
        lines.append(f"- **Typography:** {display_str} for headlines, {body_str} for body")

    # Textures
    if textures:
        tex_items = []
        for name, opacity, desc in textures:
            item = name
            if opacity:
                item += f" ({opacity})"
            tex_items.append(item)
        lines.append(f"- **Textures:** {', '.join(tex_items)}")

    # Composition from imagery style
    style = _get_imagery(tokens, "style")
    if style:
        lines.append(f"- **Composition:** {style}")

    return "\n".join(lines) if lines else "- [No brand data in tokens]"


def _build_color_table(colors):
    """Build a markdown table of all colors."""
    if not colors:
        return "No colors defined in tokens."

    lines = ["| Name | Hex | Usage |", "|------|-----|-------|"]
    for name, hex_val, usage in colors:
        lines.append(f"| {name} | {hex_val} | {usage} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate_gamma_markdown(tokens):
    """Generate the full Gamma prompts markdown from parsed tokens."""
    # Brand name
    brand_section = tokens.get("brand", {})
    brand_name_tok = brand_section.get("name", brand_section.get("brandName", {}))
    brand_name = _get_value(brand_name_tok) if brand_name_tok else "Brand"

    colors = _collect_colors(tokens)
    textures = _collect_textures(tokens)

    # Prompt A
    gamma_image_style = _get_imagery(tokens, "gammaImageStyle")
    if gamma_image_style:
        prompt_a = gamma_image_style
    else:
        prompt_a = _build_image_style(tokens, colors, textures)

    # Positive / negative keywords
    positive = _get_imagery(tokens, "positivePrompt") or _build_positive_from_tokens(tokens, colors, textures)
    negative = _get_imagery(tokens, "negativePrompt") or "[No negative keywords in tokens]"

    # Brand summary for Prompt B
    brand_summary = _build_brand_summary(tokens, colors, textures)

    # Color table
    color_table = _build_color_table(colors)

    md = f"""# Gamma Prompts — {brand_name}
Generated from tokens.json — do not edit manually

## Prompt A: Image Style (Global)

{prompt_a}

## Prompt B: Input Text Template

### Business Context
[FILL: Business goal, ad goal, what they sell, who they sell to]

### Brand Guidelines Summary
{brand_summary}

### Global Rules
- No text in generated images (text is overlaid separately)
- Negative space required for text overlay zones
- All surfaces must show texture
- Colors must stay within the brand palette
- Dimensions: [FILL per asset]

### Shot Description
[FILL: One specific shot — composition, subject, mood, color treatment, texture]

## Positive Keywords
{positive}

## Negative Keywords
{negative}

## Color Reference
{color_table}
"""
    return md


def _build_positive_from_tokens(tokens, colors, textures):
    """Construct positive keywords from color names, texture names, and style."""
    keywords = []

    for name, hex_val, _ in colors:
        keywords.append(name)

    for name, _, desc in textures:
        keywords.append(name)
        if desc:
            keywords.append(desc)

    style = _get_imagery(tokens, "style")
    if style:
        keywords.append(style)

    return ", ".join(keywords) if keywords else "[No positive keywords — add imagery.positivePrompt to tokens]"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Translate W3C design tokens to Gamma-ready markdown prompts."
    )
    parser.add_argument(
        "tokens_json",
        help="Path to the W3C DTCG tokens.json file"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: stdout)"
    )
    args = parser.parse_args()

    with open(args.tokens_json, "r") as f:
        tokens = json.load(f)

    markdown = generate_gamma_markdown(tokens)

    if args.output:
        with open(args.output, "w") as f:
            f.write(markdown)
        print(f"[tokens_to_gamma] Wrote Gamma prompts to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(markdown)
        print("[tokens_to_gamma] Gamma prompts written to stdout", file=sys.stderr)

    # Summary
    colors = _collect_colors(tokens)
    textures = _collect_textures(tokens)
    has_gamma_style = bool(_get_imagery(tokens, "gammaImageStyle"))
    print(f"[tokens_to_gamma] Summary: {len(colors)} colors, {len(textures)} textures, "
          f"gammaImageStyle={'found' if has_gamma_style else 'constructed from tokens'}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
