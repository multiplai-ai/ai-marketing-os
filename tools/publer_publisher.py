#!/usr/bin/env python3
"""
Publer Social Publisher
-----------------------
Bulk-create and schedule social posts in Publer with images, first comments,
and scheduled dates. Posts are created as drafts by default.

Usage:
    python3 tools/publer_publisher.py --test
    python3 tools/publer_publisher.py --accounts
    python3 tools/publer_publisher.py --publish brains/mitl/content/personal/social-posts-2026-03.json
    python3 tools/publer_publisher.py --publish brains/mitl/content/personal/social-posts-2026-03.json --dry-run

Environment variables (export explicitly):
    PUBLER_API_KEY       - Publer API key
    PUBLER_WORKSPACE_ID  - Publer workspace ID

Post JSON format (backward-compatible with metricool_publisher.py):
    [
      {
        "text": "Post content here...",
        "platforms": ["linkedin", "twitter"],
        "publish_date": "2026-03-03T08:00:00",
        "timezone": "America/New_York",
        "image_path": "brains/mitl/content/personal/images/hot-take-mar3-linkedin.png",
        "first_comment": "What do you think?",
        "state": "draft_private"
      }
    ]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

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


# ---------------------------------------------------------------------------
# Publer API client
# ---------------------------------------------------------------------------

class PublerClient:
    """Create and schedule social posts via Publer API."""

    API_BASE = "https://app.publer.com/api/v1"

    # Map generic platform names to Publer network keys
    PLATFORM_MAP = {
        "linkedin": "linkedin",
        "twitter": "twitter",
        "instagram": "instagram",
        "facebook": "facebook",
        "tiktok": "tiktok",
        "pinterest": "pinterest",
        "youtube": "youtube",
        "gmb": "google_business",
        "google": "google_business",
    }

    def __init__(self, api_key: str, workspace_id: str = ""):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.headers = {
            "Authorization": f"Bearer-API {api_key}",
            "Content-Type": "application/json",
        }
        if workspace_id:
            self.headers["Publer-Workspace-Id"] = workspace_id

    # ------------------------------------------------------------------
    # Core API methods
    # ------------------------------------------------------------------

    def test_connection(self) -> tuple[bool, str]:
        """Verify auth by fetching workspaces."""
        if requests is None:
            return False, "requests library not installed. Run: pip install requests"

        try:
            resp = requests.get(
                f"{self.API_BASE}/workspaces",
                headers=self.headers,
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                workspaces = data if isinstance(data, list) else data.get("data", [])
                if self.workspace_id:
                    match = next(
                        (w for w in workspaces if str(w.get("id", "")) == str(self.workspace_id)),
                        None,
                    )
                    if match:
                        name = match.get("name", self.workspace_id)
                        return True, f"Connected to Publer workspace: {name}"
                    else:
                        names = [w.get("name", w.get("id", "?")) for w in workspaces]
                        return True, f"Connected (workspace_id not found in list; available: {names})"
                count = len(workspaces)
                return True, f"Connected to Publer ({count} workspace(s) found)"
            elif resp.status_code == 401:
                return False, "Invalid API key. Check the exported PUBLER_API_KEY."
            elif resp.status_code == 403:
                return False, "Access denied. Check your Publer plan and API key permissions."
            else:
                return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            return False, str(e)

    def list_accounts(self) -> Tuple[bool, Union[List[dict], str]]:
        """Fetch connected social accounts. Returns (success, accounts_or_error)."""
        if requests is None:
            return False, "requests library not installed"

        try:
            resp = requests.get(
                f"{self.API_BASE}/accounts",
                headers=self.headers,
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                accounts = data if isinstance(data, list) else data.get("data", [])
                return True, accounts
            elif resp.status_code == 401:
                return False, "Invalid API key."
            else:
                return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            return False, str(e)

    def upload_media(self, filepath: Union[str, Path]) -> Tuple[bool, str]:
        """Upload a local image file. Returns (success, media_id_or_error).

        The Publer media upload endpoint is not fully documented. If it fails,
        a clear error is returned — use external URLs as a fallback.
        """
        if requests is None:
            return False, "requests library not installed"

        filepath = Path(filepath)
        if not filepath.exists():
            return False, f"File not found: {filepath}"

        # Build headers without Content-Type so requests sets multipart boundary
        upload_headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}

        try:
            with open(filepath, "rb") as f:
                files = {"file": (filepath.name, f, "image/jpeg")}
                resp = requests.post(
                    f"{self.API_BASE}/media",
                    headers=upload_headers,
                    files=files,
                    timeout=30,
                )

            if resp.ok:
                data = resp.json()
                # Try common response shapes
                media_id = (
                    data.get("id")
                    or data.get("media_id")
                    or (data.get("data") or {}).get("id")
                )
                if media_id:
                    return True, str(media_id)
                return False, f"Upload succeeded but no media ID found in response: {data}"
            else:
                msg = resp.text[:300]
                try:
                    msg = resp.json().get("message", msg)
                except Exception:
                    pass
                return False, (
                    f"Media upload failed (HTTP {resp.status_code}): {msg}. "
                    "Tip: Try using image_url (external URL) instead of image_path."
                )
        except Exception as e:
            return False, (
                f"Media upload error: {e}. "
                "Tip: Try using image_url (external URL) instead of image_path."
            )

    def poll_job(self, job_id: str, timeout: int = 30) -> Tuple[bool, dict]:
        """Poll job_status until complete or failed. Returns (success, result_data)."""
        if requests is None:
            return False, {"error": "requests library not installed"}

        deadline = time.time() + timeout
        poll_interval = 2  # seconds

        while time.time() < deadline:
            try:
                resp = requests.get(
                    f"{self.API_BASE}/job_status/{job_id}",
                    headers=self.headers,
                    timeout=10,
                )
                if resp.ok:
                    data = resp.json()
                    status = data.get("status", "working")
                    if status == "complete":
                        return True, data
                    elif status == "failed":
                        return False, data
                    # status == "working" — keep polling
                else:
                    return False, {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
            except Exception as e:
                return False, {"error": str(e)}

            time.sleep(poll_interval)

        return False, {"error": f"Job {job_id} did not complete within {timeout}s"}

    def create_post(
        self,
        account_ids: list[str],
        text: str,
        platform_map: dict[str, str],
        scheduled_at: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
        media_urls: Optional[List[str]] = None,
        first_comment: Optional[str] = None,
        state: str = "draft_private",
        dry_run: bool = False,
    ) -> Tuple[bool, str]:
        """Create a post in Publer. Returns (success, post_id_or_error).

        Args:
            account_ids: List of Publer account IDs to post to.
            text: Post body text.
            platform_map: Dict of platform name → post type, e.g. {"linkedin": "status"}.
            scheduled_at: ISO 8601 datetime string (UTC).
            media_ids: List of uploaded Publer media IDs.
            media_urls: List of external media URLs (alternative to media_ids).
            first_comment: Text for the first comment on the post.
            state: Draft state — "draft", "draft_private", or "draft_public".
            dry_run: If True, log intent without sending.
        """
        if dry_run:
            plats = ", ".join(platform_map.keys())
            preview = text[:60] + ("..." if len(text) > 60 else "")
            return True, f"[DRY RUN] {scheduled_at or 'no date'} → {plats} | {preview}"

        if requests is None:
            return False, "requests library not installed"

        # Build network-specific sub-objects
        networks = {}
        for platform, post_type in platform_map.items():
            networks[platform] = {"type": post_type, "text": text}

        # Build media list
        media = []
        if media_ids:
            for mid in media_ids:
                media.append({"id": mid, "type": "image"})
        if media_urls:
            for url in media_urls:
                media.append({"url": url, "type": "image"})

        # Build per-account config
        accounts_payload = []
        for acct_id in account_ids:
            acct_entry: dict = {"id": acct_id}
            if scheduled_at:
                acct_entry["scheduled_at"] = scheduled_at
            if first_comment:
                acct_entry["firstComment"] = first_comment
            accounts_payload.append(acct_entry)

        post_obj: dict = {
            "networks": networks,
            "accounts": accounts_payload,
        }
        if media:
            post_obj["media"] = media

        payload = {
            "bulk": {
                "state": state,
                "posts": [post_obj],
            }
        }

        try:
            resp = requests.post(
                f"{self.API_BASE}/posts/schedule",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            if resp.ok:
                data = resp.json()
                # Publer returns job_id directly or nested under data
                job_id = data.get("job_id") or (data.get("data") or {}).get("job_id")
                if job_id:
                    ok, result = self.poll_job(job_id)
                    if ok:
                        return True, job_id
                    else:
                        err = result.get("error", str(result))
                        return False, f"Job {job_id} failed: {err}"
                if data.get("success") or data.get("id"):
                    return True, data.get("id", "created")
                # Fallback — treat any 2xx with data as success
                msg = data.get("message", str(data)[:200])
                return False, f"API returned unexpected response: {msg}"
            else:
                msg = resp.text[:300]
                try:
                    msg = resp.json().get("message", msg)
                except Exception:
                    pass
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, str(e)

    # ------------------------------------------------------------------
    # Batch publishing
    # ------------------------------------------------------------------

    # Reverse map: Publer account type/provider → network key used in post payloads
    ACCOUNT_TYPE_TO_NETWORK = {
        "in_profile": "linkedin",
        "linkedin": "linkedin",
        "twitter": "twitter",
        "instagram": "instagram",
        "facebook": "facebook",
        "tiktok": "tiktok",
        "pinterest": "pinterest",
        "youtube": "youtube",
        "google_business": "google_business",
    }

    def _accounts_by_platform(self, accounts: List[dict]) -> Dict[str, List[str]]:
        """Build a map of network_key → [account_id, ...] from list_accounts response."""
        mapping: dict[str, list[str]] = {}
        for acct in accounts:
            # Publer account objects use "provider", "type", or "network" key
            raw_platform = (
                acct.get("provider")
                or acct.get("platform")
                or acct.get("type")
                or acct.get("network")
                or ""
            ).lower()
            # Normalize to the network key Publer expects in post payloads
            platform = self.ACCOUNT_TYPE_TO_NETWORK.get(raw_platform, raw_platform)
            acct_id = str(acct.get("id", ""))
            if platform and acct_id:
                mapping.setdefault(platform, []).append(acct_id)
        return mapping

    def publish_batch(self, posts: list[dict], dry_run: bool = False) -> dict:
        """Publish all posts with rate limiting. Returns results summary dict."""
        results = {
            "total": len(posts),
            "succeeded": 0,
            "failed": 0,
            "details": [],
        }

        # Fetch accounts once for platform → account_id mapping
        platform_to_accounts: dict[str, list[str]] = {}
        if not dry_run:
            ok, accounts_or_err = self.list_accounts()
            if ok:
                platform_to_accounts = self._accounts_by_platform(accounts_or_err)
            else:
                # Non-fatal: we'll warn per-post when mapping fails
                print(f"Warning: Could not fetch accounts: {accounts_or_err}", file=sys.stderr)

        for i, post in enumerate(posts):
            text = post.get("text", "")
            platforms = post.get("platforms", [])
            publish_date = post.get("publish_date", "")
            timezone = post.get("timezone", "America/New_York")
            image_path = post.get("image_path")
            image_url = post.get("image_url") or post.get("media_url")
            first_comment = post.get("first_comment")
            state = post.get("state", "draft_private")

            if not text or not platforms:
                results["failed"] += 1
                results["details"].append({
                    "index": i + 1,
                    "date": publish_date,
                    "platforms": platforms,
                    "text_preview": text[:50],
                    "success": False,
                    "detail": "Missing required fields: text, platforms",
                })
                continue

            # Convert publish_date + timezone to UTC ISO string for Publer
            scheduled_at = _to_utc_iso(publish_date, timezone) if publish_date else None

            # Build platform_map and collect account_ids
            pm: dict[str, str] = {}
            acct_ids: list[str] = []
            missing_platforms: list[str] = []

            for plat in platforms:
                publer_net = self.PLATFORM_MAP.get(plat.lower(), plat.lower())
                pm[publer_net] = "status"
                if not dry_run:
                    acct_list = platform_to_accounts.get(publer_net, [])
                    if acct_list:
                        acct_ids.extend(acct_list)
                    else:
                        missing_platforms.append(publer_net)

            # Warn but don't block if accounts not found (user may pass account_ids directly)
            if missing_platforms and not dry_run:
                print(
                    f"  Warning: No Publer accounts found for: {missing_platforms}. "
                    "Post may fail.",
                    file=sys.stderr,
                )

            # Upload image if provided
            media_ids: list[str] = []
            media_urls: list[str] = []

            if image_path and not dry_run:
                img_path = PROJECT_ROOT / image_path
                ok, result = self.upload_media(img_path)
                if ok:
                    media_ids.append(result)
                else:
                    print(f"  Warning: Image upload failed: {result}", file=sys.stderr)
            elif image_url:
                media_urls.append(image_url)

            success, detail = self.create_post(
                account_ids=acct_ids,
                text=text,
                platform_map=pm,
                scheduled_at=scheduled_at,
                media_ids=media_ids or None,
                media_urls=media_urls or None,
                first_comment=first_comment,
                state=state,
                dry_run=dry_run,
            )

            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "index": i + 1,
                "date": publish_date,
                "platforms": platforms,
                "text_preview": text[:50],
                "success": success,
                "detail": detail,
            })

            # Rate limit: 3-second spacing between posts
            if not dry_run and i < len(posts) - 1:
                time.sleep(3)

        return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_utc_iso(publish_date: str, timezone: str) -> str:
    """Convert a naive local datetime string + timezone to UTC ISO 8601.

    Falls back to appending 'Z' if conversion fails (assumes UTC input).
    """
    try:
        from datetime import datetime
        import zoneinfo

        dt = datetime.fromisoformat(publish_date)
        tz = zoneinfo.ZoneInfo(timezone)
        local_dt = dt.replace(tzinfo=tz)
        utc_dt = local_dt.astimezone(zoneinfo.ZoneInfo("UTC"))
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        # Best-effort fallback: treat as-is and append Z
        clean = publish_date.replace(" ", "T")
        if not clean.endswith("Z") and "+" not in clean:
            clean += "Z"
        return clean


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def format_output(results: dict, source: str, dry_run: bool = False) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "PUBLER PUBLISHER" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"Source: {source}",
        f"Total posts: {results['total']}",
        f"Created: {results['succeeded']}",
        f"Failed: {results['failed']}",
        "",
    ]

    for d in results["details"]:
        icon = "+" if d["success"] else "x"
        plats = ", ".join(d["platforms"])
        date_str = (d["date"] or "")[:10]
        lines.append(f"  [{icon}] {date_str:10s} | {plats:20s} | {d['text_preview']}")

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
        description="Publer Social Publisher — create and schedule posts in bulk"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Publer API connection",
    )
    parser.add_argument(
        "--accounts",
        action="store_true",
        help="List connected social accounts with IDs and platforms",
    )
    parser.add_argument(
        "--publish",
        metavar="FILE",
        help="Path to JSON file with post data",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview without sending to Publer",
    )

    args = parser.parse_args()

    # Get credentials
    api_key = os.environ.get("PUBLER_API_KEY")
    if not api_key:
        print("Error: PUBLER_API_KEY not exported in the environment", file=sys.stderr)
        return 1

    workspace_id = os.environ.get("PUBLER_WORKSPACE_ID", "")
    client = PublerClient(api_key, workspace_id)

    # --test
    if args.test:
        ok, msg = client.test_connection()
        print(f"{'OK' if ok else 'FAIL'}: {msg}")
        return 0 if ok else 1

    # --accounts
    if args.accounts:
        ok, result = client.list_accounts()
        if not ok:
            print(f"Error: {result}", file=sys.stderr)
            return 1
        accounts = result
        if not accounts:
            print("No connected accounts found.")
            return 0
        print(f"Connected accounts ({len(accounts)}):")
        for acct in accounts:
            acct_id = acct.get("id", "?")
            platform = acct.get("platform") or acct.get("type") or acct.get("network") or "?"
            name = acct.get("name") or acct.get("username") or acct.get("label") or "unnamed"
            print(f"  {platform:15s} | id={acct_id:20s} | {name}")
        return 0

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

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
