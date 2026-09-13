#!/usr/bin/env python3
"""
Design Token Extractor

Loads a URL via Playwright, injects JavaScript to extract computed styles
from all visible elements, groups/deduplicates values, and outputs structured JSON.

Extracts: colors, typography, spacing, borders, shadows, layout patterns.

Usage:
    python tools/extract_design_tokens.py https://example.com
    python tools/extract_design_tokens.py https://example.com --output .tmp/
    python tools/extract_design_tokens.py https://example.com --screenshot
"""
from __future__ import annotations
# Support both direct scripts and package imports.
if __package__:
    from .optional_dependencies import require_dependency, run_cli, launch_chromium
else:
    from optional_dependencies import require_dependency, run_cli, launch_chromium

import argparse
import colorsys
import json
import math
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse



# JavaScript injected into the page to extract computed styles from all visible elements
EXTRACTION_JS = """
() => {
    const results = {
        colors: { color: [], backgroundColor: [], borderColor: [] },
        typography: { fontFamily: [], fontSize: [], fontWeight: [], lineHeight: [], letterSpacing: [] },
        spacing: { padding: [], margin: [], gap: [] },
        borders: { borderRadius: [], borderWidth: [] },
        shadows: [],
        layout: { viewportWidth: window.innerWidth, maxWidths: [] },
        cssVariables: {}
    };

    // Extract CSS custom properties from :root
    const rootStyles = getComputedStyle(document.documentElement);
    const sheets = document.styleSheets;
    try {
        for (const sheet of sheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText === ':root' || rule.selectorText === ':root, :host') {
                        const style = rule.style;
                        for (let i = 0; i < style.length; i++) {
                            const prop = style[i];
                            if (prop.startsWith('--')) {
                                results.cssVariables[prop] = style.getPropertyValue(prop).trim();
                            }
                        }
                    }
                }
            } catch (e) {
                // Cross-origin stylesheet, skip
            }
        }
    } catch (e) {}

    const allElements = document.querySelectorAll('*');

    for (const el of allElements) {
        // Skip invisible elements
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;

        const style = getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        if (parseFloat(style.opacity) === 0) continue;

        // Colors
        const color = style.color;
        if (color && color !== 'rgba(0, 0, 0, 0)') results.colors.color.push(color);

        const bgColor = style.backgroundColor;
        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') results.colors.backgroundColor.push(bgColor);

        const borderColor = style.borderColor;
        if (borderColor && borderColor !== 'rgba(0, 0, 0, 0)') {
            // borderColor can be shorthand with multiple values
            const parts = borderColor.split(/(?<=\\))\\s+/);
            for (const part of parts) {
                if (part && part !== 'rgba(0, 0, 0, 0)') results.colors.borderColor.push(part);
            }
        }

        // Typography
        results.typography.fontFamily.push(style.fontFamily);
        results.typography.fontSize.push(style.fontSize);
        results.typography.fontWeight.push(style.fontWeight);
        results.typography.lineHeight.push(style.lineHeight);
        results.typography.letterSpacing.push(style.letterSpacing);

        // Spacing (individual values)
        for (const side of ['Top', 'Right', 'Bottom', 'Left']) {
            const pad = style['padding' + side];
            if (pad && pad !== '0px') results.spacing.padding.push(pad);
            const mar = style['margin' + side];
            if (mar && mar !== '0px' && mar !== 'auto') results.spacing.margin.push(mar);
        }
        const gap = style.gap;
        if (gap && gap !== 'normal' && gap !== '0px') results.spacing.gap.push(gap);

        // Borders
        const radius = style.borderRadius;
        if (radius && radius !== '0px') results.borders.borderRadius.push(radius);
        const bw = style.borderWidth;
        if (bw && bw !== '0px') results.borders.borderWidth.push(bw);

        // Shadows
        const shadow = style.boxShadow;
        if (shadow && shadow !== 'none') results.shadows.push(shadow);

        // Layout max-widths
        const maxW = style.maxWidth;
        if (maxW && maxW !== 'none' && maxW !== '0px') results.layout.maxWidths.push(maxW);
    }

    return results;
}
"""


def parse_rgb(color_str):
    """Parse rgb/rgba string to (r, g, b, a) tuple."""
    match = re.match(
        r'rgba?\((\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)'
        r'(?:,\s*([\d.]+))?\)',
        color_str
    )
    if match:
        r, g, b = int(float(match.group(1))), int(float(match.group(2))), int(float(match.group(3)))
        a = float(match.group(4)) if match.group(4) else 1.0
        return (r, g, b, a)
    return None


def rgb_to_hex(r, g, b):
    """Convert RGB values to hex string."""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_str):
    """Convert hex string to (r, g, b) tuple."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def color_distance(c1, c2):
    """
    Compute perceptual color distance (simplified CIE76 delta E).
    c1, c2 are (r, g, b) tuples.
    """
    # Convert to Lab-like space for better perceptual distance
    def to_linear(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r1, g1, b1 = [to_linear(x) for x in c1]
    r2, g2, b2 = [to_linear(x) for x in c2]

    # Simplified distance in linear RGB (not true Lab but good enough for dedup)
    return math.sqrt(
        (r1 - r2) ** 2 * 0.3 +
        (g1 - g2) ** 2 * 0.59 +
        (b1 - b2) ** 2 * 0.11
    ) * 100


def get_luminance(r, g, b):
    """Get relative luminance of a color (0-1)."""
    def to_linear(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * to_linear(r) + 0.7152 * to_linear(g) + 0.0722 * to_linear(b)


def get_saturation(r, g, b):
    """Get HSL saturation of a color (0-1)."""
    _, s, _ = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return s


def categorize_color(hex_color, luminance, saturation):
    """Categorize a color by its likely role."""
    if luminance > 0.9:
        return "surface"
    if luminance < 0.1:
        return "text"
    if saturation < 0.1:
        return "neutral"
    return "chromatic"


def deduplicate_colors(color_counts, threshold=3.0):
    """Merge near-identical colors, keeping the most frequent."""
    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
    merged = []
    used = set()

    for hex_color, count in sorted_colors:
        if hex_color in used:
            continue
        rgb = hex_to_rgb(hex_color)
        group = {"hex": hex_color, "count": count, "rgb": rgb}

        for other_hex, other_count in sorted_colors:
            if other_hex == hex_color or other_hex in used:
                continue
            other_rgb = hex_to_rgb(other_hex)
            if color_distance(rgb, other_rgb) < threshold:
                group["count"] += other_count
                used.add(other_hex)

        used.add(hex_color)
        merged.append(group)

    return merged


def generate_color_scale(hex_color):
    """Generate a 50-900 color scale from a base color."""
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

    scale = {}
    steps = {
        "50": 0.95, "100": 0.90, "200": 0.80, "300": 0.70,
        "400": 0.60, "500": 0.50, "600": 0.40, "700": 0.30,
        "800": 0.20, "900": 0.12
    }

    for name, target_l in steps.items():
        # Adjust saturation slightly — less saturated at extremes
        sat_adjust = 1.0
        if target_l > 0.8:
            sat_adjust = 0.6 + (1.0 - target_l) * 2
        elif target_l < 0.2:
            sat_adjust = 0.7 + target_l * 1.5

        adj_s = min(1.0, s * sat_adjust)
        nr, ng, nb = colorsys.hls_to_rgb(h, target_l, adj_s)
        scale[name] = rgb_to_hex(int(nr * 255), int(ng * 255), int(nb * 255))

    # Find the closest step to the original color and replace it
    closest_step = min(steps.keys(), key=lambda k: abs(steps[k] - l))
    scale[closest_step] = hex_color

    return scale


def process_colors(raw_colors):
    """Process raw color data into categorized, deduplicated color palette."""
    all_color_counts = Counter()

    for category, values in raw_colors.items():
        for val in values:
            parsed = parse_rgb(val)
            if parsed:
                r, g, b, a = parsed
                if a < 0.1:
                    continue
                hex_val = rgb_to_hex(r, g, b)
                all_color_counts[hex_val] += 1

    # Deduplicate
    deduped = deduplicate_colors(all_color_counts, threshold=3.0)

    # Categorize
    surfaces = []
    texts = []
    neutrals = []
    chromatics = []

    for item in deduped:
        r, g, b = item["rgb"]
        lum = get_luminance(r, g, b)
        sat = get_saturation(r, g, b)
        cat = categorize_color(item["hex"], lum, sat)

        entry = {
            "hex": item["hex"],
            "count": item["count"],
            "luminance": round(lum, 3),
            "saturation": round(sat, 3),
        }

        if cat == "surface":
            surfaces.append(entry)
        elif cat == "text":
            texts.append(entry)
        elif cat == "neutral":
            neutrals.append(entry)
        else:
            chromatics.append(entry)

    # Assign roles from chromatic colors (sorted by frequency)
    chromatics.sort(key=lambda x: -x["count"])
    roles = {}
    if len(chromatics) >= 1:
        roles["primary"] = chromatics[0]["hex"]
    if len(chromatics) >= 2:
        roles["secondary"] = chromatics[1]["hex"]
    if len(chromatics) >= 3:
        roles["accent"] = chromatics[2]["hex"]

    # Pick best surface and text colors
    if surfaces:
        surfaces.sort(key=lambda x: -x["count"])
        roles["surface"] = surfaces[0]["hex"]
    if texts:
        texts.sort(key=lambda x: -x["count"])
        roles["text"] = texts[0]["hex"]
    if neutrals:
        neutrals.sort(key=lambda x: -x["count"])
        roles["border"] = neutrals[0]["hex"]

    # Generate scales for chromatic roles
    scales = {}
    for role in ["primary", "secondary", "accent"]:
        if role in roles:
            scales[role] = generate_color_scale(roles[role])

    return {
        "roles": roles,
        "scales": scales,
        "all_colors": [
            {"hex": item["hex"], "count": item["count"]}
            for item in deduped[:30]
        ],
        "surfaces": surfaces[:5],
        "texts": texts[:5],
        "neutrals": neutrals[:10],
        "chromatics": chromatics[:10],
    }


def process_typography(raw_type):
    """Process raw typography data into a structured type system."""
    # Font families — clean and count
    family_counts = Counter()
    for fam in raw_type["fontFamily"]:
        # Take the first font in the stack
        primary = fam.split(",")[0].strip().strip('"').strip("'")
        if primary and primary.lower() not in ("system-ui", "sans-serif", "serif", "monospace", "cursive"):
            family_counts[primary] += 1

    # Font sizes — parse px values and build scale
    size_counts = Counter()
    for size in raw_type["fontSize"]:
        match = re.match(r'([\d.]+)px', size)
        if match:
            px = round(float(match.group(1)), 1)
            size_counts[px] += 1

    # Font weights
    weight_counts = Counter()
    for w in raw_type["fontWeight"]:
        try:
            weight_counts[int(w)] += 1
        except (ValueError, TypeError):
            pass

    # Line heights
    lh_counts = Counter()
    for lh in raw_type["lineHeight"]:
        if lh == "normal":
            lh_counts["normal"] += 1
        else:
            match = re.match(r'([\d.]+)', lh)
            if match:
                val = round(float(match.group(1)), 2)
                # Normalize px line-heights to ratios if they look like px
                if val > 5:
                    pass  # Skip raw px, hard to interpret without font size
                else:
                    lh_counts[val] += 1

    # Letter spacings
    ls_counts = Counter()
    for ls in raw_type["letterSpacing"]:
        if ls != "normal" and ls != "0px":
            ls_counts[ls] += 1

    # Build type scale from sizes
    sorted_sizes = sorted(size_counts.keys())
    type_scale = {}
    scale_names = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl"]

    # Find the most common size as "base"
    if size_counts:
        base_size = size_counts.most_common(1)[0][0]
        # Build scale around base
        smaller = sorted([s for s in sorted_sizes if s < base_size], reverse=True)
        larger = sorted([s for s in sorted_sizes if s > base_size])

        # Assign base
        base_idx = 2  # "base" is at index 2
        type_scale[scale_names[base_idx]] = f"{base_size}px"

        # Assign smaller
        for i, size in enumerate(smaller[:base_idx]):
            idx = base_idx - 1 - i
            if idx >= 0:
                type_scale[scale_names[idx]] = f"{size}px"

        # Assign larger
        for i, size in enumerate(larger[:len(scale_names) - base_idx - 1]):
            idx = base_idx + 1 + i
            type_scale[scale_names[idx]] = f"{size}px"

    # Top font families
    families = [
        {"name": name, "count": count}
        for name, count in family_counts.most_common(5)
    ]

    # Assign roles
    font_roles = {}
    if len(families) >= 1:
        font_roles["heading"] = families[0]["name"]
        font_roles["body"] = families[0]["name"]
    if len(families) >= 2:
        # If the second font is significantly different, use it for body
        font_roles["body"] = families[1]["name"]
    # Look for a monospace font
    for fam in raw_type["fontFamily"]:
        if "mono" in fam.lower() or "code" in fam.lower() or "consolas" in fam.lower():
            primary = fam.split(",")[0].strip().strip('"').strip("'")
            if primary.lower() not in ("monospace",):
                font_roles["mono"] = primary
                break

    return {
        "families": families,
        "roles": font_roles,
        "scale": type_scale,
        "weights": [
            {"weight": w, "count": c}
            for w, c in sorted(weight_counts.items())
        ],
        "lineHeights": [
            {"value": v, "count": c}
            for v, c in lh_counts.most_common(5)
        ],
        "letterSpacings": [
            {"value": v, "count": c}
            for v, c in ls_counts.most_common(5)
        ],
    }


def process_spacing(raw_spacing):
    """Process raw spacing data into a coherent spacing scale."""
    all_values = Counter()

    for category, values in raw_spacing.items():
        for val in values:
            match = re.match(r'([\d.]+)px', val)
            if match:
                px = round(float(match.group(1)))
                if 0 < px <= 200:
                    all_values[px] += 1

    # Build a scale from the most common values
    sorted_vals = sorted(all_values.keys())

    # Try to identify a base unit (most common small value, likely 4 or 8)
    small_vals = [v for v in sorted_vals if 2 <= v <= 8]
    base_unit = 4  # default
    if small_vals:
        base_unit = min(small_vals, key=lambda v: -all_values[v])

    # Build scale
    scale = {}
    for px in sorted_vals:
        if all_values[px] >= 2:  # Only include values used more than once
            # Name by multiplier of base unit
            multiplier = round(px / base_unit)
            if multiplier > 0:
                scale[str(multiplier)] = f"{int(px)}px"

    return {
        "baseUnit": f"{base_unit}px",
        "scale": scale,
        "allValues": [
            {"px": px, "count": c}
            for px, c in sorted(all_values.items())
            if c >= 2
        ][:20],
    }


def process_borders(raw_borders):
    """Process raw border data."""
    radius_counts = Counter()
    width_counts = Counter()

    for val in raw_borders.get("borderRadius", []):
        # Normalize multi-value radii to first value
        first = val.split()[0] if val else val
        radius_counts[first] += 1

    for val in raw_borders.get("borderWidth", []):
        first = val.split()[0] if val else val
        width_counts[first] += 1

    return {
        "radii": [
            {"value": v, "count": c}
            for v, c in radius_counts.most_common(10)
        ],
        "widths": [
            {"value": v, "count": c}
            for v, c in width_counts.most_common(5)
        ],
    }


def process_shadows(raw_shadows):
    """Process raw shadow data."""
    shadow_counts = Counter()
    for val in raw_shadows:
        shadow_counts[val] += 1

    return [
        {"value": v, "count": c}
        for v, c in shadow_counts.most_common(10)
    ]


def process_layout(raw_layout):
    """Process layout data."""
    max_width_counts = Counter()
    for val in raw_layout.get("maxWidths", []):
        max_width_counts[val] += 1

    return {
        "viewportWidth": raw_layout.get("viewportWidth", 0),
        "maxWidths": [
            {"value": v, "count": c}
            for v, c in max_width_counts.most_common(5)
        ],
    }


def extract_tokens(url, output_dir=".tmp", take_screenshot=False):
    """
    Extract design tokens from a URL.

    Args:
        url: The URL to extract from
        output_dir: Directory for output files
        take_screenshot: Whether to capture a screenshot

    Returns:
        Dict with url, success, error, tokens, files
    """
    sync_playwright = require_dependency("playwright.sync_api", "web").sync_playwright
    PlaywrightTimeout = require_dependency("playwright.sync_api", "web").TimeoutError
    result = {
        "url": url,
        "success": False,
        "error": None,
        "tokens": None,
        "files": [],
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    domain = urlparse(url).netloc.replace("www.", "")

    with sync_playwright() as p:
        print("Launching browser...")
        browser = launch_chromium(p.chromium, headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        try:
            print(f"Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)

            # Scroll the full page to trigger lazy-loaded content
            print("Scrolling to load content...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            # Screenshot (before extraction so it's the natural page state)
            if take_screenshot:
                screenshot_path = output_path / f"screenshot-{domain}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"Screenshot saved: {screenshot_path}")
                result["files"].append(str(screenshot_path))

            # Extract raw styles
            print("Extracting computed styles...")
            raw = page.evaluate(EXTRACTION_JS)

            # Process each category
            print("Processing colors...")
            colors = process_colors(raw["colors"])

            print("Processing typography...")
            typography = process_typography(raw["typography"])

            print("Processing spacing...")
            spacing = process_spacing(raw["spacing"])

            print("Processing borders...")
            borders = process_borders(raw["borders"])

            print("Processing shadows...")
            shadows = process_shadows(raw["shadows"])

            print("Processing layout...")
            layout = process_layout(raw["layout"])

            # Assemble token output
            tokens = {
                "source": url,
                "domain": domain,
                "extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "colors": colors,
                "typography": typography,
                "spacing": spacing,
                "borders": borders,
                "shadows": shadows,
                "layout": layout,
                "cssVariables": raw.get("cssVariables", {}),
            }

            # Save JSON
            json_path = output_path / f"extracted-tokens-{domain}.json"
            json_path.write_text(
                json.dumps(tokens, indent=2, default=str),
                encoding="utf-8",
            )
            print(f"Tokens saved: {json_path}")

            result["tokens"] = tokens
            result["files"].append(str(json_path))
            result["success"] = True

        except PlaywrightTimeout:
            result["error"] = f"Timeout loading {url}"
            print(f"Error: {result['error']}")

        except Exception as e:
            result["error"] = str(e)
            print(f"Error: {result['error']}")

        finally:
            browser.close()

    return result


def print_summary(tokens):
    """Print a human-readable summary of extracted tokens."""
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    # Colors
    colors = tokens["colors"]
    print(f"\nCOLORS:")
    for role, hex_val in colors.get("roles", {}).items():
        print(f"  {role:12s} {hex_val}")
    print(f"  Total unique colors: {len(colors.get('all_colors', []))}")

    # Typography
    typo = tokens["typography"]
    print(f"\nTYPOGRAPHY:")
    for role, font in typo.get("roles", {}).items():
        print(f"  {role:12s} {font}")
    if typo.get("scale"):
        print(f"  Type scale:  {' / '.join(typo['scale'].values())}")

    # Spacing
    spacing = tokens["spacing"]
    print(f"\nSPACING:")
    print(f"  Base unit:   {spacing.get('baseUnit', 'unknown')}")
    if spacing.get("scale"):
        vals = list(spacing["scale"].values())[:8]
        print(f"  Scale:       {' / '.join(vals)}")

    # Borders
    borders = tokens["borders"]
    if borders.get("radii"):
        print(f"\nBORDERS:")
        top_radii = [r["value"] for r in borders["radii"][:4]]
        print(f"  Radii:       {' / '.join(top_radii)}")

    # Shadows
    shadows = tokens["shadows"]
    if shadows:
        print(f"\nSHADOWS: {len(shadows)} unique shadow(s)")

    # CSS Variables
    css_vars = tokens.get("cssVariables", {})
    if css_vars:
        print(f"\nCSS VARIABLES: {len(css_vars)} custom properties found")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Extract design tokens from a website URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://stripe.com
  %(prog)s https://linear.app --output .tmp/tokens/
  %(prog)s https://example.com --screenshot
        """,
    )
    parser.add_argument("url", help="URL to extract design tokens from")
    parser.add_argument(
        "--output",
        default=".tmp",
        help="Output directory for JSON and screenshots (default: .tmp)",
    )
    parser.add_argument(
        "--screenshot",
        action="store_true",
        help="Capture a full-page screenshot alongside tokens",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Design Token Extractor")
    print("=" * 60)
    print(f"URL:    {args.url}")
    print(f"Output: {args.output}")
    print("=" * 60)

    result = extract_tokens(
        url=args.url,
        output_dir=args.output,
        take_screenshot=args.screenshot,
    )

    if result["success"]:
        print_summary(result["tokens"])
        print(f"\nFiles created:")
        for f in result["files"]:
            print(f"  {f}")
        return 0
    else:
        print(f"\nExtraction failed: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(run_cli(main))
