#!/usr/bin/env python3
"""
Create a presentation in Gamma using the Generate API.

Usage:
    python gamma_create_presentation.py <input_file> [--title "Title"]
    python gamma_create_presentation.py <input_file> --dry-run
    python gamma_create_presentation.py --test
"""

import os
import sys
import json
import time
import argparse
if __package__:
    from .optional_dependencies import require_dependency, run_cli
else:
    from optional_dependencies import require_dependency, run_cli
from pathlib import Path


BASE_URL = "https://public-api.gamma.app/v1.0"

VALID_FORMATS = ["presentation", "document", "webpage"]


def test_connection() -> bool:
    """Test API connection by making a simple request."""
    requests = require_dependency("requests", "publishing")
    GAMMA_API_KEY = os.getenv("GAMMA_API_KEY")
    if not GAMMA_API_KEY:
        print("Error: GAMMA_API_KEY not found in environment")
        return False

    headers = {
        "X-API-KEY": GAMMA_API_KEY
    }

    try:
        # Use the generations endpoint with a GET to check auth
        # The API may not have a dedicated health endpoint, so we check if auth works
        response = requests.get(
            f"{BASE_URL}/generations/test-nonexistent-id",
            headers=headers,
            timeout=15,
        )
        # A missing resource or server error cannot establish credential validity.
        if response.status_code == 200:
            print("✓ Gamma API connection successful")
            print("  API credentials accepted")
            return True
        elif response.status_code in [401, 403]:
            print("✗ Gamma API authentication failed")
            print(f"  Status: {response.status_code}")
            return False
        else:
            print(f"Gamma authentication not verified (HTTP {response.status_code}).")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error: {e}")
        return False


def analyze_markdown(content: str) -> dict:
    """Analyze markdown content for dry-run preview."""
    lines = content.split('\n')

    # Count slide breaks (--- on its own line)
    slide_breaks = sum(1 for line in lines if line.strip() == '---')
    slide_count = slide_breaks + 1  # N breaks = N+1 slides

    # Find title (first H1 heading)
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Count other elements
    h2_count = sum(1 for line in lines if line.startswith('## '))
    h3_count = sum(1 for line in lines if line.startswith('### '))
    bullet_count = sum(1 for line in lines if line.strip().startswith('- '))

    # Character and word count
    char_count = len(content)
    word_count = len(content.split())

    return {
        "title": title or "(no title found)",
        "slide_count": slide_count,
        "slide_breaks": slide_breaks,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "bullet_count": bullet_count,
        "char_count": char_count,
        "word_count": word_count
    }


def create_presentation(
    input_text: str,
    title: str = None,
    num_cards: int = None,
    format_type: str = "presentation",
    image_style: str = "modern",
    theme_name: str = None,
    additional_instructions: str = None,
) -> dict:
    """Create a presentation via Gamma API."""
    requests = require_dependency("requests", "publishing")
    GAMMA_API_KEY = os.getenv("GAMMA_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": GAMMA_API_KEY
    }

    payload = {
        "inputText": input_text,
        "textMode": "preserve",  # Preserve the structure we created
        "format": format_type,
        "cardSplit": "inputTextBreaks",  # Use our --- breaks as slide separators
        "textOptions": {
            "amount": "detailed",
            "tone": "professional",
            "language": "en"
        },
        "imageOptions": {
            "source": "aiGenerated",
            "style": image_style
        },
        "cardOptions": {
            "dimensions": "fluid"
        },
        "sharingOptions": {
            "workspaceAccess": "view"
        }
    }

    if num_cards:
        payload["numCards"] = num_cards
    if theme_name:
        payload["themeName"] = theme_name
    if additional_instructions:
        payload["additionalInstructions"] = additional_instructions

    response = requests.post(
        f"{BASE_URL}/generations",
        headers=headers,
        json=payload
    )

    if response.status_code not in [200, 201]:
        print(f"Error creating presentation: {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.json()


def poll_generation(generation_id: str, max_attempts: int = 60, interval: int = 5) -> dict:
    """Poll for generation completion."""
    requests = require_dependency("requests", "publishing")
    GAMMA_API_KEY = os.getenv("GAMMA_API_KEY")
    headers = {
        "X-API-KEY": GAMMA_API_KEY
    }

    for attempt in range(max_attempts):
        response = requests.get(
            f"{BASE_URL}/generations/{generation_id}",
            headers=headers
        )

        if response.status_code != 200:
            print(f"Error polling: {response.status_code}")
            print(response.text)
            sys.exit(1)

        data = response.json()
        status = data.get("status")

        print(f"Status: {status} (attempt {attempt + 1}/{max_attempts})")

        if status == "completed":
            return data
        elif status == "failed":
            print(f"Generation failed: {data.get('error', 'Unknown error')}")
            sys.exit(1)

        time.sleep(interval)

    print("Timeout waiting for generation to complete")
    sys.exit(1)


def main():
    GAMMA_API_KEY = os.getenv("GAMMA_API_KEY")
    parser = argparse.ArgumentParser(description="Create a Gamma presentation")
    parser.add_argument("input_file", nargs="?", help="Path to markdown file with presentation content")
    parser.add_argument("--title", "-t", help="Presentation title", default=None)
    parser.add_argument("--num-cards", type=int, help="Number of slides", default=None)
    parser.add_argument("--test", action="store_true", help="Test API connection only")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview structure without publishing")
    parser.add_argument("--poll-generation-id", help="Poll an existing Gamma generation ID and print its URL", default=None)
    parser.add_argument("--format", "-f", choices=VALID_FORMATS, default="presentation",
                        help="Output format: presentation (default), document, or webpage")
    parser.add_argument("--image-style", help="Override imageOptions.style with a brand-specific prompt", default="modern")
    parser.add_argument("--theme-name", help="Name of a saved Gamma theme to apply (e.g., 'MultiplAI')", default=None)
    parser.add_argument("--additional-instructions", help="Free-text style/voice guidance passed to Gamma's generator", default=None)
    args = parser.parse_args()

    if args.dry_run and (args.test or args.poll_generation_id):
        parser.error("--dry-run applies only to input-file previews")

    # Handle --test flag
    if args.test:
        success = test_connection()
        sys.exit(0 if success else 1)

    if args.poll_generation_id:
        if not GAMMA_API_KEY:
            print("Error: GAMMA_API_KEY not found in environment")
            sys.exit(1)
        final_result = poll_generation(args.poll_generation_id)
        gamma_url = final_result.get("url") or final_result.get("gammaUrl") or final_result.get("viewUrl")
        print("\n" + "━" * 50)
        print("GENERATION COMPLETED")
        print("━" * 50)
        print(f"URL: {gamma_url}")
        print("━" * 50)
        return

    # Require input file for other operations
    if not args.input_file:
        print("Error: input_file is required (unless using --test)")
        parser.print_help()
        sys.exit(1)

    if not GAMMA_API_KEY and not args.dry_run:
        print("Error: GAMMA_API_KEY not found in environment")
        sys.exit(1)

    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)

    input_text = input_path.read_text()

    # Handle --dry-run flag
    if args.dry_run:
        analysis = analyze_markdown(input_text)
        print("\n" + "━" * 50)
        print("GAMMA DRY RUN PREVIEW")
        print("━" * 50)
        print(f"\nFile: {args.input_file}")
        print(f"Title: {args.title or analysis['title']}")
        print(f"Format: {args.format}")
        print(f"\nStructure Analysis:")
        print(f"  Slide breaks (---): {analysis['slide_breaks']}")
        print(f"  Estimated slides: {analysis['slide_count']}")
        print(f"  H2 headings: {analysis['h2_count']}")
        print(f"  H3 headings: {analysis['h3_count']}")
        print(f"  Bullet points: {analysis['bullet_count']}")
        print(f"\nContent Size:")
        print(f"  Characters: {analysis['char_count']:,}")
        print(f"  Words: {analysis['word_count']:,}")
        print("\n" + "━" * 50)
        print("✓ Dry run complete. Use without --dry-run to publish.")
        print("━" * 50)
        return

    print(f"Read {len(input_text)} characters from {args.input_file}")

    # Create presentation
    print(f"Creating {args.format}...")
    result = create_presentation(
        input_text,
        args.title,
        args.num_cards,
        args.format,
        image_style=args.image_style,
        theme_name=args.theme_name,
        additional_instructions=args.additional_instructions,
    )
    generation_id = result.get("generationId")
    print(f"Generation ID: {generation_id}")

    # Poll for completion
    print("Waiting for generation to complete...")
    final_result = poll_generation(generation_id)

    # Extract and print the URL
    gamma_url = final_result.get("url") or final_result.get("gammaUrl") or final_result.get("viewUrl")

    print("\n" + "━" * 50)
    print(f"{args.format.upper()} CREATED SUCCESSFULLY")
    print("━" * 50)
    print(f"URL: {gamma_url}")
    print("━" * 50)

    # Print full result for debugging if needed
    if os.getenv("DEBUG"):
        print(json.dumps(final_result, indent=2))

    return final_result


if __name__ == "__main__":
    sys.exit(run_cli(main))
