#!/usr/bin/env python3
"""
Ghost CMS Publisher
-------------------
Create and schedule posts on Ghost, with optional newsletter send,
using the Ghost Admin API (JWT auth).

Usage:
    python3 tools/ghost_publisher.py --test
    python3 tools/ghost_publisher.py --draft content/article.md
    python3 tools/ghost_publisher.py --draft content/article.md --dry-run
    python3 tools/ghost_publisher.py --draft content/article.md --schedule 2026-03-15T09:00:00
    python3 tools/ghost_publisher.py --draft content/article.md --newsletter
    python3 tools/ghost_publisher.py --draft content/article.md --newsletter members --tags "AI,Marketing"

    # Gated lead magnet (free subscribers only — set visibility in frontmatter):
    python3 tools/ghost_publisher.py --draft content/resources/guide.md --tags "resource,lead-magnet"

Environment variables (export explicitly before live requests):
    GHOST_URL           - Ghost site URL (e.g. https://example.com)
    GHOST_ADMIN_API_KEY - Admin API key in format {id}:{secret}
"""

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    import jwt
except ImportError:
    jwt = None

# ---------------------------------------------------------------------------
# Project root for direct script execution
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.markdown_utils import (
    extract_frontmatter, extract_title, markdown_to_html,
    parse_tags, strip_title_heading, text_field,
)


# ---------------------------------------------------------------------------
# Ghost JWT auth
# ---------------------------------------------------------------------------

def _generate_ghost_token(api_key: str) -> str:
    """Generate a short-lived Ghost Admin API JWT token.

    Ghost Admin API key format: {id}:{secret}
    - id  → JWT kid header
    - secret → hex-encoded, decoded to bytes for signing
    Token: HS256, audience /admin/, 5-minute expiry
    """
    if jwt is None:
        raise ImportError(
            "PyJWT is required; install with: pip install '.[publishing]'"
        )

    parts = api_key.split(":")
    if len(parts) != 2:
        raise ValueError(
            "GHOST_ADMIN_API_KEY must be in format {id}:{secret}"
        )

    key_id, secret_hex = parts
    try:
        secret_bytes = bytes.fromhex(secret_hex)
    except ValueError as exc:
        raise ValueError("GHOST_ADMIN_API_KEY secret must be hex encoded") from exc
    if not key_id or not secret_bytes:
        raise ValueError("GHOST_ADMIN_API_KEY id and secret must both be nonempty")

    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 300,  # 5-minute expiry
        "aud": "/admin/",
    }
    headers = {"alg": "HS256", "kid": key_id}

    token = jwt.encode(payload, secret_bytes, algorithm="HS256", headers=headers)
    # PyJWT ≥2.0 returns str; older versions return bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


# ---------------------------------------------------------------------------
# Ghost API client
# ---------------------------------------------------------------------------

class GhostClient:
    """Create and schedule posts on Ghost via the Admin API."""

    def __init__(self, ghost_url: str, admin_api_key: str):
        self.ghost_url = ghost_url.rstrip("/")
        self.admin_api_key = admin_api_key

    def _auth_header(self) -> dict:
        token = _generate_ghost_token(self.admin_api_key)
        return {"Authorization": f"Ghost {token}"}

    def test_connection(self) -> tuple[bool, str]:
        """GET /ghost/api/admin/site/ to verify auth."""
        if requests is None:
            return False, "requests is required; install with: pip install '.[publishing]'"

        url = f"{self.ghost_url}/ghost/api/admin/site/"
        try:
            resp = requests.get(
                url,
                headers={**self._auth_header(), "Accept-Version": "v5.0"},
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                site_title = data.get("site", {}).get("title", self.ghost_url)
                version = data.get("site", {}).get("version", "?")
                return True, f"Connected to \"{site_title}\" (Ghost {version}) at {self.ghost_url}"
            elif resp.status_code == 401:
                return False, "Authentication failed — check GHOST_ADMIN_API_KEY"
            else:
                msg = resp.text[:200]
                try:
                    msg = resp.json().get("errors", [{}])[0].get("message", msg)
                except Exception:
                    pass
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, f"Connection error: {e}"

    def create_post(
        self,
        title: str,
        html_body: str,
        status: str = "draft",
        scheduled_at: str = None,
        tags: list[str] = None,
        feature_image: str = None,
        meta_title: str = None,
        meta_description: str = None,
        newsletter_slug: str = None,
        featured: bool = False,
        visibility: str = "public",
        slug: str = None,
        is_page: bool = False,
        dry_run: bool = False,
    ) -> tuple[bool, str]:
        """Create a post or page on Ghost.

        Args:
            title: Resource title
            html_body: Resource body as HTML
            status: "draft", "published", or "scheduled"
            scheduled_at: ISO datetime string (e.g. "2026-03-15T09:00:00")
                          Overrides status to "scheduled" when provided.
                          Posts only; ignored for pages.
            tags: List of tag name strings
            feature_image: URL for the resource's feature image
            meta_title: SEO title override
            meta_description: SEO description
            newsletter_slug: Send as newsletter to this newsletter slug.
                          Posts only; ignored for pages.
            featured: Mark as featured
            visibility: "public", "members" (free subscribers), or "paid"
            slug: URL slug override
            is_page: When True, create a Ghost page (/admin/pages/) instead of
                     a post (/admin/posts/). Pages do not support newsletter
                     sending or scheduling.
            dry_run: Preview payload without making API call
        """
        resource_label = "Page" if is_page else "Post"
        resource_key = "pages" if is_page else "posts"
        editor_key = "page" if is_page else "post"

        # Build resource object
        resource: dict = {
            "title": title,
            "html": html_body,
            "status": "scheduled" if scheduled_at and not is_page else status,
            "featured": featured,
            "visibility": visibility,
        }

        if scheduled_at and not is_page:
            # Normalize both positive and negative offsets; bare datetimes use UTC.
            try:
                if "T" not in scheduled_at:
                    raise ValueError("datetime must include T and a time")
                timestamp = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                resource["published_at"] = timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            except ValueError:
                return False, "Invalid schedule: use an ISO datetime such as 2030-03-15T09:00:00-04:00 (bare times use UTC)"

        if tags:
            resource["tags"] = [{"name": t} for t in tags]

        if feature_image:
            resource["feature_image"] = feature_image

        if meta_title:
            resource["meta_title"] = meta_title

        if meta_description:
            resource["meta_description"] = meta_description

        if slug:
            resource["slug"] = slug

        if newsletter_slug and not is_page:
            resource["email_segment"] = "all"
            resource["newsletter"] = {"slug": newsletter_slug}

        payload = {resource_key: [resource]}

        if dry_run:
            import json
            preview = html_body[:200].replace('\n', ' ')
            payload_preview = json.dumps(payload, indent=2)
            return True, (
                f"[DRY RUN] {resource_label}: \"{title}\"\n"
                f"  Status: {resource['status']}\n"
                f"  Visibility: {visibility}\n"
                f"  Slug: {slug or '(auto)'}\n"
                f"  Tags: {', '.join(t['name'] for t in resource.get('tags', [])) or '(none)'}\n"
                f"  Newsletter: {newsletter_slug or '(none)' if not is_page else '(n/a — pages)'}\n"
                f"  Scheduled at: {scheduled_at or '(not scheduled)' if not is_page else '(n/a — pages)'}\n"
                f"  Body length: {len(html_body)} chars HTML\n"
                f"  Preview: {preview}...\n\n"
                f"Payload:\n{payload_preview}"
            )

        if requests is None:
            return False, "requests is required; install with: pip install '.[publishing]'"

        url = f"{self.ghost_url}/ghost/api/admin/{resource_key}/?source=html"
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={
                    **self._auth_header(),
                    "Content-Type": "application/json",
                    "Accept-Version": "v5.0",
                },
                timeout=30,
            )
            if resp.ok:
                data = resp.json()
                created = data.get(resource_key, [{}])[0]
                resource_id = created.get("id", "?")
                resource_url = created.get("url", "")
                edit_url = f"{self.ghost_url}/ghost/#/editor/{editor_key}/{resource_id}"
                result_status = created.get("status", resource["status"])
                return True, (
                    f"{resource_label} created (status: {result_status})\n"
                    f"  Edit: {edit_url}\n"
                    f"  URL: {resource_url}"
                )
            else:
                msg = resp.text[:300]
                try:
                    errors = resp.json().get("errors", [])
                    if errors:
                        msg = errors[0].get("message", msg)
                        ctx = errors[0].get("context", "")
                        if ctx:
                            msg = f"{msg} — {ctx}"
                except Exception:
                    pass
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, f"{resource_label} creation error: {e}"


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def format_output(success: bool, detail: str, source: str, dry_run: bool = False) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "GHOST PUBLISHER" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"Source: {source}",
        "",
    ]

    if success:
        lines.append(detail)
    else:
        lines.extend([
            "Failed to create post.",
            f"Error: {detail}",
            "",
            "Check the exported GHOST_URL and GHOST_ADMIN_API_KEY environment variables.",
        ])

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ghost CMS Publisher — create and schedule posts via Ghost Admin API"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Ghost API connection",
    )
    parser.add_argument(
        "--draft",
        metavar="FILE",
        help="Path to markdown file to publish as a Ghost post",
    )
    parser.add_argument(
        "--schedule",
        metavar="DATETIME",
        help='ISO datetime for scheduling (e.g. "2030-03-15T09:00:00-04:00"); bare times use UTC',
    )
    parser.add_argument(
        "--newsletter",
        metavar="SLUG",
        nargs="?",
        const="default",
        help='Send as newsletter; optionally specify slug (default: "default")',
    )
    parser.add_argument(
        "--tags",
        metavar="TAGS",
        help="Comma-separated list of tags (e.g. \"AI,Marketing\")",
    )
    parser.add_argument(
        "--page",
        action="store_true",
        help="Create a Ghost page (/admin/pages/) instead of a post. Newsletter and scheduling flags are ignored.",
    )
    parser.add_argument(
        "--slug",
        metavar="SLUG",
        help="URL slug override (e.g. \"advisory\")",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview payload without creating",
    )

    args = parser.parse_args()

    if args.dry_run and args.test:
        parser.error("--dry-run cannot be combined with --test (a live connection check)")
    if not args.draft and not args.test:
        parser.print_help()
        return 1

    # Dry runs render locally and never require credentials.
    ghost_url = os.environ.get("GHOST_URL")
    admin_api_key = os.environ.get("GHOST_ADMIN_API_KEY")

    if not args.dry_run and (not ghost_url or not admin_api_key):
        print("Error: Missing Ghost credentials.", file=sys.stderr)
        print("Required: GHOST_URL, GHOST_ADMIN_API_KEY", file=sys.stderr)
        print("Export these environment variables before making a live request.", file=sys.stderr)
        return 1

    client = GhostClient(ghost_url or "https://example.invalid", admin_api_key or "")

    # --test
    if args.test:
        ok, msg = client.test_connection()
        print(f"{'OK' if ok else 'FAIL'}: {msg}")
        return 0 if ok else 1

    # --draft
    if args.draft:
        filepath = Path(args.draft)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return 1

        # Parse markdown
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1

        try:
            fm, body = extract_frontmatter(content)
            title = text_field(fm, "title") or extract_title(body, filepath)
            html_body = markdown_to_html(strip_title_heading(body))
            tags = parse_tags(args.tags if args.tags is not None else fm.get("tags"))
            feature_image = text_field(fm, "feature_image") or text_field(fm, "og_image")
            meta_title = text_field(fm, "meta_title") or text_field(fm, "seo_title")
            meta_description = text_field(fm, "meta_description") or text_field(fm, "description")
            status = text_field(fm, "status", "draft")
            visibility = text_field(fm, "visibility", "public")
            slug = args.slug or text_field(fm, "slug")
            if status not in {"draft", "published", "scheduled"}:
                raise ValueError("Frontmatter 'status' must be draft, published, or scheduled")
            if status == "scheduled" and (not args.schedule or args.page):
                raise ValueError("Scheduled posts require --schedule; pages cannot be scheduled")
            if visibility not in {"public", "members", "paid"}:
                raise ValueError("Frontmatter 'visibility' must be public, members, or paid")
        except (ValueError, ImportError) as exc:
            print(f"Error preparing draft: {exc}", file=sys.stderr)
            return 1

        ok, detail = client.create_post(
            title=title,
            html_body=html_body,
            status=status,
            scheduled_at=args.schedule,
            tags=tags,
            feature_image=feature_image,
            meta_title=meta_title,
            meta_description=meta_description,
            newsletter_slug=args.newsletter,
            visibility=visibility,
            slug=slug,
            is_page=args.page,
            dry_run=args.dry_run,
        )
        print(format_output(ok, detail, str(filepath), dry_run=args.dry_run))
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
