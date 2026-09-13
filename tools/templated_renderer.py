#!/usr/bin/env python3
"""
Templated.io Bulk Image Renderer
---------------------------------
Generate branded images from content files using Templated.io templates.
Reads article markdown or social post JSON, maps content fields to template
layer slots, renders via API, and saves PNGs locally.

Usage:
    python3 tools/templated_renderer.py --test
    python3 tools/templated_renderer.py --templates
    python3 tools/templated_renderer.py --layers <template-id>
    python3 tools/templated_renderer.py --render <content-file> [--template <id-or-name>] [--dry-run]
    python3 tools/templated_renderer.py --batch <directory> [--dry-run]

Environment variables (export explicitly):
    TEMPLATED_API_KEY    - Templated.io API key

Content file formats supported:
    - Markdown with YAML frontmatter (articles): uses title + category from frontmatter
    - JSON array (social posts): uses text + content_type fields per post

Template layer mapping (configure in TEMPLATE_MAP below):
    Maps content_type values to template IDs + layer field assignments.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if __package__:
    from .optional_dependencies import require_dependency, run_cli
else:
    from optional_dependencies import require_dependency, run_cli

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_BASE = "https://api.templated.io/v1"
IMAGES_DIR = Path(os.environ.get("TEMPLATED_OUTPUT_DIR", "content/images")).resolve()
MANIFEST_PATH = IMAGES_DIR.parent / "image-manifest.json"

# Template mapping: content_type -> template config
# Update these IDs as you build templates in Templated.io editor.
# Use --templates to list available templates and their IDs.
TEMPLATE_MAP = {
    # Article feature images (1200x630)
    "build-log": {
        "template_id": None,  # Set after building template
        "layer_map": {
            "title-1": "headline",       # Article title
            "text-3": "category_label",   # "BUILD LOG"
        },
        "defaults": {
            "category_label": "BUILD LOG",
        },
    },
    "tool-bench": {
        "template_id": None,
        "layer_map": {
            "title-1": "headline",
            "text-3": "category_label",
        },
        "defaults": {
            "category_label": "TOOL BENCH",
        },
    },
    # Substack / Industry POV (existing template)
    "flagship": {
        "template_id": os.environ.get("TEMPLATED_FLAGSHIP_TEMPLATE_ID"),
        "layer_map": {
            "title-1": "headline",
            "text-3": "category_label",
        },
        "defaults": {
            "category_label": "INDUSTRY POV",
        },
    },
    # Social post templates (LinkedIn 1200x675)
    "hot-take": {
        "template_id": None,
        "layer_map": {
            "title-1": "headline",
            "text-3": "category_label",
        },
        "defaults": {
            "category_label": "HOT TAKE",
        },
    },
    "framework": {
        "template_id": None,
        "layer_map": {
            "title-1": "headline",
            "text-3": "category_label",
        },
        "defaults": {
            "category_label": "FRAMEWORK",
        },
    },
    "skill-drop": {
        "template_id": None,
        "layer_map": {
            "title-1": "headline",
            "text-3": "category_label",
        },
        "defaults": {
            "category_label": "SKILL DROP",
        },
    },
    "article-promo": {
        "template_id": None,
        "layer_map": {
            "title-1": "headline",
            "text-3": "category_label",
        },
        "defaults": {},
    },
}


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

class TemplatedClient:
    """Thin wrapper around the Templated.io REST API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def test_connection(self) -> Tuple[bool, str]:
        """Verify API key works by listing templates."""
        requests = require_dependency("requests", "publishing")
        try:
            r = requests.get(
                f"{API_BASE}/templates",
                headers=self.headers,
                timeout=15,
            )
            if r.status_code == 200:
                templates = r.json()
                return True, f"Connected. {len(templates)} template(s) available."
            elif r.status_code == 401:
                return False, "Invalid API key."
            else:
                return False, f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return False, f"Connection error: {e}"

    def list_templates(self) -> List[dict]:
        """List all templates with basic info."""
        requests = require_dependency("requests", "publishing")
        r = requests.get(f"{API_BASE}/templates", headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def get_layers(self, template_id: str) -> List[dict]:
        """Get layer definitions for a template."""
        requests = require_dependency("requests", "publishing")
        r = requests.get(
            f"{API_BASE}/template/{template_id}/layers",
            headers=self.headers,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    def render(
        self,
        template_id: str,
        layers: Dict[str, dict],
        fmt: str = "png",
        transparent: bool = False,
    ) -> dict:
        """
        Render a template with layer overrides.

        Args:
            template_id: Template UUID
            layers: Dict of layer_name -> {property: value} overrides
            fmt: Output format (png, jpg, webp, pdf)
            transparent: Transparent background (PNG only)

        Returns:
            Render result dict with 'url', 'id', 'status' fields.
        """
        requests = require_dependency("requests", "publishing")
        payload = {
            "template": template_id,
            "format": fmt,
            "layers": layers,
        }
        if transparent and fmt == "png":
            payload["transparent"] = True

        r = requests.post(
            f"{API_BASE}/render",
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    def download(self, url: str, dest: Path) -> Path:
        """Download a rendered image to a local path."""
        requests = require_dependency("requests", "publishing")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(r.content)
        return dest


# ---------------------------------------------------------------------------
# Content Parsing
# ---------------------------------------------------------------------------

def extract_frontmatter(content: str) -> Tuple[dict, str]:
    """Extract YAML frontmatter and return (metadata, body)."""
    fm = {}
    body = content
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, _, val = line.partition(':')
                fm[key.strip()] = val.strip().strip('"').strip("'")
        body = content[match.end():]
    return fm, body


def extract_title(content: str) -> Optional[str]:
    """Extract H1 title from markdown content."""
    match = re.search(r'^# (.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else None


def detect_content_type(filepath: Path, frontmatter: dict) -> str:
    """Detect content type from frontmatter or filename."""
    # Check frontmatter
    if "content_type" in frontmatter:
        return frontmatter["content_type"]
    if "type" in frontmatter:
        return frontmatter["type"]
    if "category" in frontmatter:
        return frontmatter["category"].lower().replace(" ", "-")

    # Infer from filename
    name = filepath.stem.lower()
    if "flagship" in name or "build-log" in name:
        return "flagship"
    if "tool-bench" in name or "tool-review" in name:
        return "tool-bench"
    if "hot-take" in name:
        return "hot-take"
    if "framework" in name:
        return "framework"
    if "skill-drop" in name:
        return "skill-drop"
    if "series-gtm" in name or "spoke" in name:
        return "article-promo"

    return "flagship"  # default


def parse_content_file(filepath: Path) -> List[dict]:
    """
    Parse a content file and return list of render jobs.

    Each job: {slug, headline, subheadline, category_label, content_type, source_file}
    """
    filepath = Path(filepath)

    if filepath.suffix == ".json":
        with open(filepath, encoding="utf-8") as f:
            posts = json.load(f)
        jobs = []
        for i, post in enumerate(posts):
            text = post.get("text", "")
            # First line is usually the hook/headline
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            headline = lines[0][:80] if lines else f"Post {i+1}"
            content_type = post.get("content_type", "hot-take")
            slug = post.get("slug", f"post-{i+1}")
            jobs.append({
                "slug": slug,
                "headline": headline,
                "subheadline": post.get("subheadline", ""),
                "category_label": post.get("category_label", ""),
                "content_type": content_type,
                "source_file": str(filepath),
            })
        return jobs

    # Markdown file
    content = filepath.read_text(encoding="utf-8")
    fm, body = extract_frontmatter(content)
    title = fm.get("title") or extract_title(content) or filepath.stem
    content_type = detect_content_type(filepath, fm)
    slug = filepath.stem

    return [{
        "slug": slug,
        "headline": title,
        "subheadline": fm.get("subheadline", fm.get("subtitle", "")),
        "category_label": fm.get("category", ""),
        "content_type": content_type,
        "source_file": str(filepath),
    }]


# ---------------------------------------------------------------------------
# Image Manifest Integration
# ---------------------------------------------------------------------------

def load_manifest() -> dict:
    """Load image manifest."""
    if not MANIFEST_PATH.exists():
        return {
            "_schema": "1.0",
            "_description": "Maps content slugs to required images.",
            "images": {},
        }
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest: dict) -> None:
    """Save image manifest."""
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def update_manifest(slug: str, filename: str, content_type: str,
                    source_file: str, template_id: str, status: str = "generated") -> None:
    """Add or update an entry in the image manifest."""
    manifest = load_manifest()
    images = manifest.setdefault("images", {})

    if slug not in images:
        images[slug] = {"content_file": source_file, "images": []}

    # Update existing entry or add new
    entry_list = images[slug]["images"]
    for entry in entry_list:
        if entry["filename"] == filename:
            entry["status"] = status
            entry["template_id"] = template_id
            entry["generated_at"] = _now_iso()
            save_manifest(manifest)
            return

    entry_list.append({
        "type": content_type,
        "filename": filename,
        "dimensions": "",
        "status": status,
        "template_id": template_id,
        "generated_at": _now_iso(),
    })
    save_manifest(manifest)


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Render Logic
# ---------------------------------------------------------------------------

def build_layer_overrides(job: dict, template_config: dict) -> dict:
    """
    Build the layers dict for the render API from a content job.

    Uses template_config['layer_map'] to know which template layer
    corresponds to which content field, and template_config['defaults']
    for fallback values.
    """
    layer_map = template_config.get("layer_map", {})
    defaults = template_config.get("defaults", {})
    layers = {}

    for layer_name, content_field in layer_map.items():
        # Get value from job, then defaults, then skip
        value = job.get(content_field) or defaults.get(content_field)
        if value:
            layers[layer_name] = {"text": value}

    return layers


def render_job(client: TemplatedClient, job: dict, dry_run: bool = False) -> Optional[Path]:
    """
    Render a single content job to an image.

    Returns the local file path on success, None on skip/error.
    """
    content_type = job["content_type"]
    config = TEMPLATE_MAP.get(content_type)

    if not config:
        print(f"  SKIP: No template config for content_type '{content_type}'")
        return None

    template_id = config.get("template_id")
    if not template_id:
        print(f"  SKIP: No template_id set for '{content_type}' — build it in Templated.io editor first")
        return None

    layers = build_layer_overrides(job, config)
    filename = f"{job['slug']}-{content_type}.png"
    dest = IMAGES_DIR / filename

    if dry_run:
        print(f"  DRY-RUN: Would render '{job['headline'][:50]}...'")
        print(f"    template: {template_id}")
        print(f"    layers: {json.dumps(layers, indent=4)}")
        print(f"    output: {dest}")
        return None

    print(f"  Rendering '{job['headline'][:50]}...'")
    try:
        result = client.render(template_id, layers, fmt="png")
        url = result.get("render_url") or result.get("url")
        if not url:
            print(f"  ERROR: No URL in render response: {result}")
            return None

        # Download
        client.download(url, dest)
        print(f"  Saved: {dest.relative_to(PROJECT_ROOT)}")

        # Update manifest
        update_manifest(
            slug=job["slug"],
            filename=filename,
            content_type=content_type,
            source_file=job["source_file"],
            template_id=template_id,
        )

        return dest

    except Exception as e:
        print(f"  ERROR: {e}")
        return None


# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------

def cmd_test(client: TemplatedClient):
    """Test API connection."""
    ok, msg = client.test_connection()
    prefix = "OK" if ok else "Error"
    print(f"{prefix}: {msg}")
    sys.exit(0 if ok else 1)


def cmd_templates(client: TemplatedClient):
    """List available templates."""
    templates = client.list_templates()
    if not templates:
        print("No templates found.")
        return

    print(f"Templates ({len(templates)}):\n")
    for t in templates:
        print(f"  {t['name']} ({t['width']}x{t['height']})")
        print(f"    id: {t['id']}")
        print(f"    layers: {t.get('layersCount', '?')}")
        print(f"    folder: {t.get('folderName', '-')}")
        print()

    # Show which content types have templates configured
    print("Content type → template mapping:")
    for ctype, config in TEMPLATE_MAP.items():
        tid = config.get("template_id")
        status = tid[:12] + "..." if tid else "NOT SET"
        print(f"  {ctype}: {status}")


def cmd_layers(client: TemplatedClient, template_id: str):
    """Show layers for a template."""
    layers = client.get_layers(template_id)
    print(f"Layers ({len(layers)}):\n")
    for l in layers:
        ltype = l.get("type", "?")
        name = l.get("layer", "?")
        text = l.get("text", "")
        font = l.get("font_family", "")
        size = l.get("font_size", "")
        print(f"  [{ltype}] {name}")
        if text:
            print(f"    text: \"{text}\"")
        if font:
            print(f"    font: {font} {size}")
        img = l.get("image_url")
        if img:
            print(f"    image: {img[:60]}...")
        print()


def cmd_render(client: TemplatedClient, filepath: str, template_override: Optional[str], dry_run: bool):
    """Render images for a content file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    jobs = parse_content_file(path)
    print(f"Found {len(jobs)} render job(s) from {path.name}\n")

    rendered = 0
    skipped = 0
    for job in jobs:
        # Allow template override
        if template_override:
            for config in TEMPLATE_MAP.values():
                pass  # just override the content_type's template
            job_config = TEMPLATE_MAP.get(job["content_type"], {})
            if job_config:
                job_config = dict(job_config)
                job_config["template_id"] = template_override
                TEMPLATE_MAP[job["content_type"]] = job_config

        result = render_job(client, job, dry_run=dry_run)
        if result:
            rendered += 1
        else:
            skipped += 1

        # Rate limit: small delay between renders
        if not dry_run and rendered > 0:
            time.sleep(1)

    print(f"\nDone: {rendered} rendered, {skipped} skipped")


def cmd_batch(client: TemplatedClient, directory: str, dry_run: bool):
    """Render images for all content files in a directory."""
    dirpath = Path(directory)
    if not dirpath.is_dir():
        print(f"Error: Not a directory: {directory}", file=sys.stderr)
        sys.exit(1)

    files = sorted(
        list(dirpath.glob("*.md")) + list(dirpath.glob("*.json"))
    )
    if not files:
        print(f"No .md or .json files found in {directory}")
        return

    print(f"Batch rendering {len(files)} file(s) from {dirpath}\n")

    total_rendered = 0
    total_skipped = 0
    for f in files:
        print(f"--- {f.name} ---")
        jobs = parse_content_file(f)
        for job in jobs:
            result = render_job(client, job, dry_run=dry_run)
            if result:
                total_rendered += 1
            else:
                total_skipped += 1
            if not dry_run and result:
                time.sleep(1)
        print()

    print(f"Batch done: {total_rendered} rendered, {total_skipped} skipped")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Templated.io bulk image renderer")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--test", action="store_true", help="Test API connection")
    group.add_argument("--templates", action="store_true", help="List available templates")
    group.add_argument("--layers", metavar="TEMPLATE_ID", help="Show layers for a template")
    group.add_argument("--render", metavar="FILE", help="Render images for a content file")
    group.add_argument("--batch", metavar="DIR", help="Render images for all content files in a directory")

    parser.add_argument("--template", metavar="ID", help="Override template ID for rendering")
    parser.add_argument("--dry-run", action="store_true", help="Preview without rendering")

    args = parser.parse_args()

    if args.dry_run and not (args.render or args.batch):
        parser.error("--dry-run applies only to --render or --batch")
    if not args.dry_run:
        require_dependency("requests", "publishing")
    api_key = os.environ.get("TEMPLATED_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: TEMPLATED_API_KEY not exported in the environment", file=sys.stderr)
        sys.exit(1)

    client = None if args.dry_run else TemplatedClient(api_key)

    if args.test:
        cmd_test(client)
    elif args.templates:
        cmd_templates(client)
    elif args.layers:
        cmd_layers(client, args.layers)
    elif args.render:
        cmd_render(client, args.render, args.template, args.dry_run)
    elif args.batch:
        cmd_batch(client, args.batch, args.dry_run)


if __name__ == "__main__":
    sys.exit(run_cli(main))
