#!/usr/bin/env python3
"""
Generate design system visuals using Nano Banana (Gemini Image Generation)

Usage:
    python tools/generate_design_visual.py --prompt "..." --output "path/to/image.png"
    python tools/generate_design_visual.py --prompt "..." --output "path/to/image.png" --model gemini-3-pro-image-preview

Models:
    - gemini-2.5-flash-image (default) - Fast generation
    - gemini-3-pro-image-preview - Higher quality

Requirements:
    - GOOGLE_API_KEY exported in the environment
    - python -m pip install '.[google]'

Examples:
    # Generate a style tile preview
    python tools/generate_design_visual.py \
        --prompt "Modern SaaS landing page hero section with deep blue (#1E3A5F) and coral (#FF6B5A) accent, Inter font, clean minimal design, professional marketing screenshot" \
        --output "projects/MyProject/visuals/style-tile-modern.png"

    # Generate a component mockup
    python tools/generate_design_visual.py \
        --prompt "A modern button component set showing primary (blue), secondary (gray outline), and destructive (red) variants, rounded corners, Inter font, white background, UI component showcase" \
        --output ".tmp/visuals/button-components.png"
"""
from __future__ import annotations
# Support both direct scripts and package imports.
if __package__:
    from .optional_dependencies import require_dependency, run_cli
else:
    from optional_dependencies import require_dependency, run_cli

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

def generate_visual(prompt: str, output_path: str, model: str = "gemini-2.5-flash-image") -> Optional[str]:
    """
    Generate a design visual using Gemini image generation.

    Args:
        prompt: Description of the visual to generate
        output_path: Where to save the generated image
        model: Gemini model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview)

    Returns:
        Path to saved image, or None if generation failed
    """
    genai = require_dependency("google.genai", "google")
    require_dependency("PIL", "google")

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment.")
        print("Export GOOGLE_API_KEY in your shell before running this command")
        return None

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Enhance prompt for design system context
    enhanced_prompt = f"""
{prompt}

Style requirements:
- High quality, professional design
- Clean and modern aesthetic
- Suitable for design system documentation
- Sharp, crisp rendering
- Web-ready visual
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=[enhanced_prompt.strip()],
        )

        # Extract image from response
        for part in response.parts:
            if part.inline_data is not None:
                # Save the image
                image = part.as_image()
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                image.save(output_path)
                print(f"Visual saved to: {output_path}")
                return output_path

        print("Error: No image generated in response")
        if response.text:
            print(f"Response text: {response.text}")
        return None

    except Exception as e:
        print(f"Error generating visual: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate design system visuals using Gemini image generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Style direction preview
  python tools/generate_design_visual.py \\
    --prompt "Modern tech SaaS dashboard interface, navy blue and teal color scheme" \\
    --output "projects/MyProject/visuals/direction-modern.png"

  # Component showcase
  python tools/generate_design_visual.py \\
    --prompt "Button component variants: primary, secondary, ghost, destructive states" \\
    --output ".tmp/visuals/buttons.png" \\
    --model gemini-3-pro-image-preview
        """
    )

    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Description of the visual to generate"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output path for the generated image (PNG)"
    )

    parser.add_argument(
        "--model", "-m",
        default="gemini-2.5-flash-image",
        choices=["gemini-2.5-flash-image", "gemini-3-pro-image-preview"],
        help="Gemini model to use (default: gemini-2.5-flash-image)"
    )

    args = parser.parse_args()

    result = generate_visual(args.prompt, args.output, args.model)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(run_cli(main))
