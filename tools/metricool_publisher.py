#!/usr/bin/env python3
"""
Metricool Social Publisher
--------------------------
Bulk-create and schedule social posts in Metricool with specific publish dates/times.

Usage:
    python3 tools/metricool_publisher.py --publish brains/mitl/content/personal/social-posts-2026-03.json
    python3 tools/metricool_publisher.py --from-calendar brains/mitl/content/personal/calendar-2026-03.md
    python3 tools/metricool_publisher.py --dry-run brains/mitl/content/personal/social-posts-2026-03.json
    python3 tools/metricool_publisher.py --test

Environment variables (export explicitly):
    METRICOOL_API_TOKEN  - Metricool API token (requires Advanced plan)
    METRICOOL_USER_ID    - Metricool user/account ID
    METRICOOL_BLOG_ID    - Metricool blog ID

Post JSON format:
    [
      {
        "text": "Post content here...",
        "platforms": ["linkedin", "twitter"],
        "publish_date": "2026-03-03T08:00:00",
        "timezone": "America/New_York",
        "media_url": null
      }
    ]
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



# ---------------------------------------------------------------------------
# Post data
# ---------------------------------------------------------------------------

def load_posts_from_json(filepath: Path) -> list[dict]:
    """Load post data from a JSON file."""
    content = filepath.read_text(encoding="utf-8")
    posts = json.loads(content)
    if not isinstance(posts, list):
        raise ValueError("JSON file must contain an array of post objects")
    return posts


def extract_social_posts_from_calendar(filepath: Path) -> list[dict]:
    """Extract social-only posts from a content calendar markdown.

    Returns placeholder posts with titles and dates — the actual text
    needs to be written first via /writing skill. This is mostly useful
    for previewing what will need to be scheduled.
    """
    # Import calendar parser
    from tools.notion_content_db import parse_calendar

    items = parse_calendar(filepath)
    posts = []

    for item in items:
        if item.item_type != "Content":
            continue
        # Only social-native shows (Hot Take, Framework, Skill Drop)
        # Build Log and Tool Bench are Substack articles, not social posts
        if item.show not in ("Hot Take", "Framework", "Skill Drop"):
            continue
        if not item.publish_date:
            continue

        platforms = []
        if "LinkedIn" in item.channels:
            platforms.append("linkedin")
        if "Twitter" in item.channels:
            platforms.append("twitter")

        if not platforms:
            continue

        posts.append({
            "text": f"[DRAFT — needs writing] {item.title[:200]}",
            "platforms": platforms,
            "publish_date": f"{item.publish_date}T08:00:00",
            "timezone": "America/New_York",
            "media_url": None,
            "_show": item.show,
            "_week": item.week,
        })

    return posts


# ---------------------------------------------------------------------------
# Metricool API client
# ---------------------------------------------------------------------------

class MetricoolPublisher:
    """Publish and schedule social posts via Metricool API."""

    API_BASE = "https://app.metricool.com/api"

    def __init__(self, api_token: str, user_id: str = "", blog_id: str = ""):
        self.api_token = api_token
        self.user_id = user_id
        self.blog_id = blog_id
        self.headers = {
            "X-Mc-Auth": api_token,
            "Content-Type": "application/json",
        }

    def _params(self) -> dict:
        """Common query params for all API calls."""
        p = {}
        if self.user_id:
            p["userId"] = self.user_id
        if self.blog_id:
            p["blogId"] = self.blog_id
        return p

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Metricool API."""
        if requests is None:
            return False, "requests library not installed. Run: pip install requests"

        try:
            resp = requests.get(
                f"{self.API_BASE}/admin/simpleProfiles",
                headers=self.headers,
                params=self._params(),
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                if isinstance(data, list) and data:
                    name = data[0].get("label", "Account")
                    return True, f"Connected to Metricool: {name}"
                return True, "Connected to Metricool (no profiles found)"
            elif resp.status_code == 401:
                return False, "Invalid API token. Check METRICOOL_API_TOKEN."
            elif resp.status_code == 403:
                return False, "API access denied. Metricool Advanced plan required ($47-59/mo)."
            else:
                return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            return False, str(e)

    def _normalize_media(self, media_url: str) -> str:
        """Normalize a media URL through Metricool's servers."""
        try:
            resp = requests.get(
                f"{self.API_BASE}/actions/normalize/image/url",
                headers=self.headers,
                params={"url": media_url, **self._params()},
                timeout=15,
            )
            if resp.ok:
                data = resp.json()
                return data.get("url", media_url)
        except Exception:
            pass
        return media_url

    def schedule_post(self, post: dict, dry_run: bool = False) -> tuple[bool, str]:
        """Schedule a single post in Metricool."""
        text = post.get("text", "")
        platforms = post.get("platforms", [])
        publish_date = post.get("publish_date", "")
        timezone = post.get("timezone", "America/New_York")
        media_url = post.get("media_url")

        if not text or not platforms or not publish_date:
            return False, "Missing required fields: text, platforms, publish_date"

        if dry_run:
            plats = ", ".join(platforms)
            return True, f"[DRY RUN] {publish_date} → {plats} | {text[:60]}..."

        if requests is None:
            return False, "requests library not installed"

        # Metricool v2 API payload format
        # Split datetime for publicationDate object
        dt_part = publish_date.split("T")[0] + "T" + publish_date.split("T")[1] if "T" in publish_date else publish_date

        payload = {
            "text": text,
            "publicationDate": {
                "dateTime": dt_part,
                "timezone": timezone,
            },
        }

        # Metricool v2 API uses platform-specific data objects
        platform_map = {
            "linkedin": "linkedinData",
            "twitter": "twitterData",
            "instagram": "instagramData",
            "facebook": "facebookData",
            "tiktok": "tiktokData",
            "pinterest": "pinterestData",
            "gmb": "gmbData",
            "youtube": "youtubeData",
        }

        for plat in platforms:
            key = platform_map.get(plat)
            if key:
                payload[key] = {}

        if media_url:
            normalized = self._normalize_media(media_url)
            payload["media"] = {"mediaId": normalized}

        try:
            resp = requests.post(
                f"{self.API_BASE}/v2/scheduler/posts",
                headers=self.headers,
                params=self._params(),
                json=payload,
                timeout=30,
            )
            if resp.ok:
                post_id = resp.json().get("id", "created")
                return True, str(post_id)
            else:
                msg = resp.text[:200]
                try:
                    msg = resp.json().get("message", msg)
                except Exception:
                    pass
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, str(e)

    def publish_batch(self, posts: list[dict], dry_run: bool = False) -> dict:
        """Schedule all posts with rate limiting."""
        results = {
            "total": len(posts),
            "succeeded": 0,
            "failed": 0,
            "details": [],
        }

        for i, post in enumerate(posts):
            success, detail = self.schedule_post(post, dry_run=dry_run)

            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "index": i + 1,
                "date": post.get("publish_date", ""),
                "platforms": post.get("platforms", []),
                "text_preview": post.get("text", "")[:50],
                "success": success,
                "detail": detail,
            })

            # Rate limit: 2-3 second spacing between API calls
            if not dry_run and i < len(posts) - 1:
                time.sleep(2.5)

        return results


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def format_output(results: dict, source: str, dry_run: bool = False) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "METRICOOL PUBLISHER" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"Source: {source}",
        f"Total posts: {results['total']}",
        f"Scheduled: {results['succeeded']}",
        f"Failed: {results['failed']}",
        "",
    ]

    for d in results["details"]:
        icon = "+" if d["success"] else "x"
        plats = ", ".join(d["platforms"])
        lines.append(f"  [{icon}] {d['date'][:10]:10s} | {plats:20s} | {d['text_preview']}")

    if results["failed"] > 0:
        lines.append("")
        lines.append("Failures:")
        for d in results["details"]:
            if not d["success"]:
                lines.append(f"  Post {d['index']}: {d['detail']}")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Metricool Social Publisher — schedule posts in bulk"
    )
    parser.add_argument(
        "--publish",
        metavar="FILE",
        help="Path to JSON file with post data",
    )
    parser.add_argument(
        "--from-calendar",
        metavar="FILE",
        help="Extract social posts from a content calendar markdown",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview without publishing",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Metricool API connection",
    )

    args = parser.parse_args()

    # Get credentials
    api_token = os.environ.get("METRICOOL_API_TOKEN")
    if not api_token:
        print("Error: METRICOOL_API_TOKEN not exported in the environment", file=sys.stderr)
        print("Metricool Advanced plan required for API access ($47-59/mo)", file=sys.stderr)
        return 1

    user_id = os.environ.get("METRICOOL_USER_ID", "")
    blog_id = os.environ.get("METRICOOL_BLOG_ID", "")

    client = MetricoolPublisher(api_token, user_id, blog_id)

    # --test
    if args.test:
        ok, msg = client.test_connection()
        print(f"{'OK' if ok else 'FAIL'}: {msg}")
        return 0 if ok else 1

    # --publish (from JSON)
    if args.publish:
        filepath = Path(args.publish)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return 1

        try:
            posts = load_posts_from_json(filepath)
        except Exception as e:
            print(f"Error reading JSON: {e}", file=sys.stderr)
            return 1

        results = client.publish_batch(posts, dry_run=args.dry_run)
        print(format_output(results, str(filepath), dry_run=args.dry_run))
        return 0 if results["failed"] == 0 else 1

    # --from-calendar (extract and schedule)
    if args.from_calendar:
        filepath = Path(args.from_calendar)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return 1

        try:
            posts = extract_social_posts_from_calendar(filepath)
        except Exception as e:
            print(f"Error parsing calendar: {e}", file=sys.stderr)
            return 1

        if not posts:
            print("No social posts found in calendar.", file=sys.stderr)
            return 1

        results = client.publish_batch(posts, dry_run=args.dry_run)
        print(format_output(results, str(filepath), dry_run=args.dry_run))
        return 0 if results["failed"] == 0 else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
