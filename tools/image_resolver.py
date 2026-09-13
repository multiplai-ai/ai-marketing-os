#!/usr/bin/env python3
"""
Image Resolver Tool
Manages the image manifest — maps content slugs to required images and tracks status.
Status lifecycle: needed → generated → exported → published

Usage:
    python tools/image_resolver.py --status
    python tools/image_resolver.py --resolve hot-take-mar3
    python tools/image_resolver.py --validate
    python tools/image_resolver.py --add-entry hot-take-mar3 "brains/mitl/content/personal/social-posts-2026-03.json" linkedin-post 1200x1200
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# --- Config ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "brand" / "content" / "image-manifest.json"
IMAGES_DIR = PROJECT_ROOT / "brand" / "content" / "images"


# --- Core Functions (importable) ---

def load_manifest() -> dict:
    """Load and return the image manifest."""
    if not MANIFEST_PATH.exists():
        return {"_schema": "1.0", "_description": "Maps content slugs to required images. Status lifecycle: needed → generated → exported → published", "images": {}}
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest: dict) -> None:
    """Write the manifest back to disk."""
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def resolve_images(slug: str) -> list:
    """
    Get image records for a content slug with disk-existence info.
    Returns list of dicts: filename, path, exists, status, type, dimensions.
    """
    manifest = load_manifest()
    entry = manifest.get("images", {}).get(slug)
    if not entry:
        return []

    results = []
    for img in entry.get("images", []):
        img_path = IMAGES_DIR / img["filename"]
        results.append({
            "filename": img["filename"],
            "path": str(img_path),
            "exists": img_path.exists(),
            "status": img.get("status", "needed"),
            "type": img.get("type", ""),
            "dimensions": img.get("dimensions", ""),
            "template_id": img.get("template_id"),
            "generated_at": img.get("generated_at"),
        })
    return results


def validate_all() -> dict:
    """
    Check all manifest entries against disk.
    Returns dict with total, found, missing counts and missing list.
    """
    manifest = load_manifest()
    total = 0
    found = 0
    missing = []

    for slug, entry in manifest.get("images", {}).items():
        for img in entry.get("images", []):
            total += 1
            img_path = IMAGES_DIR / img["filename"]
            if img_path.exists():
                found += 1
            else:
                missing.append({
                    "slug": slug,
                    "filename": img["filename"],
                    "type": img.get("type", ""),
                    "status": img.get("status", "needed"),
                })

    return {
        "total": total,
        "found": found,
        "missing_count": total - found,
        "missing": missing,
    }


def add_entry(slug: str, content_file: str, image_type: str, dimensions: str) -> str:
    """
    Add a new image entry to the manifest for a given slug.
    Returns the generated filename.
    """
    manifest = load_manifest()
    images = manifest.setdefault("images", {})

    # Build filename: {slug}-{type}.png with type sanitized
    type_slug = image_type.replace("/", "-").replace(" ", "-").lower()
    filename = f"{slug}-{type_slug}.png"

    if slug not in images:
        images[slug] = {
            "content_file": content_file,
            "images": [],
        }

    # Avoid duplicate type entries
    existing_types = [img["type"] for img in images[slug]["images"]]
    if image_type in existing_types:
        print(f"  Entry for type '{image_type}' already exists under slug '{slug}' — skipping.")
        return filename

    images[slug]["images"].append({
        "type": image_type,
        "filename": filename,
        "dimensions": dimensions,
        "status": "needed",
        "template_id": None,
        "generated_at": None,
    })

    save_manifest(manifest)
    return filename


# --- CLI Commands ---

def cmd_status(args):
    """Show manifest summary."""
    manifest = load_manifest()
    images_map = manifest.get("images", {})
    slug_count = len(images_map)
    total_images = sum(len(e.get("images", [])) for e in images_map.values())

    # Count by status
    status_counts = {}
    for entry in images_map.values():
        for img in entry.get("images", []):
            s = img.get("status", "needed")
            status_counts[s] = status_counts.get(s, 0) + 1

    print(f"Image Manifest — {MANIFEST_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  Schema:        {manifest.get('_schema', 'unknown')}")
    print(f"  Content slugs: {slug_count}")
    print(f"  Total images:  {total_images}")
    if status_counts:
        print("  By status:")
        for status, count in sorted(status_counts.items()):
            print(f"    {status}: {count}")
    else:
        print("  No image entries yet.")


def cmd_resolve(args):
    """Show image paths for a slug and whether they exist on disk."""
    slug = args.resolve
    results = resolve_images(slug)

    if not results:
        print(f"No entries found for slug: {slug}")
        return

    print(f"Images for '{slug}':")
    for img in results:
        exists_label = "EXISTS" if img["exists"] else "MISSING"
        print(f"  [{exists_label}] {img['filename']}")
        print(f"    type:       {img['type']}")
        print(f"    dimensions: {img['dimensions']}")
        print(f"    status:     {img['status']}")
        print(f"    path:       {img['path']}")
        if img["generated_at"]:
            print(f"    generated:  {img['generated_at']}")


def cmd_validate(args):
    """Check all manifest entries against disk."""
    result = validate_all()

    print(f"Manifest validation — {IMAGES_DIR.relative_to(PROJECT_ROOT)}/")
    print(f"  Total images:   {result['total']}")
    print(f"  Found on disk:  {result['found']}")
    print(f"  Missing:        {result['missing_count']}")

    if result["missing"]:
        print("\nMissing files:")
        for item in result["missing"]:
            print(f"  [{item['slug']}] {item['filename']} (type: {item['type']}, status: {item['status']})")
    else:
        print("\nAll manifest images are present on disk.")


def cmd_add_entry(args):
    """Add a new image entry to the manifest."""
    filename = add_entry(args.slug, args.content_file, args.type, args.dimensions)
    print(f"Added entry: {args.slug} → {filename}")
    print(f"  content_file: {args.content_file}")
    print(f"  type:         {args.type}")
    print(f"  dimensions:   {args.dimensions}")
    print(f"  status:       needed")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Image manifest resolver for content pipeline")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Show manifest summary")
    group.add_argument("--resolve", metavar="SLUG", help="Get image paths for a content slug")
    group.add_argument("--validate", action="store_true", help="Check all manifest entries against disk")
    group.add_argument("--add-entry", nargs=4, metavar=("SLUG", "CONTENT_FILE", "TYPE", "DIMENSIONS"),
                       help="Add a new image entry: SLUG CONTENT_FILE TYPE DIMENSIONS")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.resolve:
        cmd_resolve(args)
    elif args.validate:
        cmd_validate(args)
    elif args.add_entry:
        # Unpack the 4 positional args into named attrs for cmd_add_entry
        args.slug, args.content_file, args.type, args.dimensions = args.add_entry
        cmd_add_entry(args)


if __name__ == "__main__":
    main()
