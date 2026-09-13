#!/usr/bin/env python3
"""
Substack Draft Creator
----------------------
Create Markdown articles as Substack drafts.

Usage:
    python3 tools/substack_publisher.py --draft content/article.md
    python3 tools/substack_publisher.py --draft content/article.md --dry-run
    python3 tools/substack_publisher.py --test

Environment variables (export explicitly before live requests):
    SUBSTACK_EMAIL     - Substack account email
    SUBSTACK_PASSWORD  - Substack account password
    SUBSTACK_SUBDOMAIN - Your Substack subdomain (e.g. "example")

IMPORTANT: Substack has NO official API. This uses a reverse-engineered,
community-maintained approach that may break if Substack changes their
internal API. Drafts only — scheduling is done in the Substack UI.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.markdown_utils import (
    extract_frontmatter, extract_title, markdown_to_html,
    strip_title_heading, text_field,
)


# ---------------------------------------------------------------------------
# Substack-specific markdown helpers
# ---------------------------------------------------------------------------

def extract_subtitle(content: str) -> str:
    """Extract subtitle — first non-empty line after H1, if short enough."""
    lines = content.split('\n')
    found_h1 = False
    for line in lines:
        if line.startswith('# '):
            found_h1 = True
            continue
        if found_h1 and line.strip():
            # If it looks like a subtitle (short, no markdown formatting)
            clean = line.strip()
            if len(clean) < 200 and not clean.startswith('#') and not clean.startswith('|'):
                return clean
            break
    return ""


# ---------------------------------------------------------------------------
# Substack API client
# ---------------------------------------------------------------------------

class SubstackPublisher:
    """Create article drafts on Substack using the unofficial API."""

    def __init__(self, email: str, password: str, subdomain: str):
        self.email = email
        self.password = password
        self.subdomain = subdomain
        self.base_url = f"https://{subdomain}.substack.com"
        self.session = None

    def _login(self) -> tuple[bool, str]:
        """Authenticate with Substack and get a session."""
        if requests is None:
            return False, "requests is required; install with: pip install '.[publishing]'"

        session = requests.Session()

        try:
            resp = session.post(
                "https://substack.com/api/v1/login",
                json={
                    "email": self.email,
                    "password": self.password,
                    "for_pub": self.subdomain,
                },
                timeout=15,
            )
            if resp.ok:
                self.session = session
                return True, "Logged in"
            elif resp.status_code == 401:
                return False, "Invalid email or password"
            else:
                msg = resp.text[:200]
                try:
                    msg = resp.json().get("error", msg)
                except Exception:
                    pass
                return False, f"Login failed — HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, f"Login error: {e}"

    def test_connection(self) -> tuple[bool, str]:
        """Test that we can authenticate with Substack."""
        ok, msg = self._login()
        if ok:
            return True, f"Connected to {self.base_url}"
        return False, msg

    def create_draft(self, filepath: Path, dry_run: bool = False) -> tuple[bool, str]:
        """Create a draft article from a markdown file."""
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            return False, f"Could not read file: {e}"

        try:
            fm, body = extract_frontmatter(content)
            title = text_field(fm, "title") or extract_title(body, filepath)
            subtitle = text_field(fm, "subtitle") or extract_subtitle(body)
            audience = text_field(fm, "audience", "everyone")
            if audience not in {"everyone", "only_paid", "only_free"}:
                raise ValueError("Frontmatter 'audience' must be everyone, only_paid, or only_free")
            html_body = markdown_to_html(strip_title_heading(body))
        except (ValueError, ImportError) as exc:
            return False, f"Could not prepare draft: {exc}"

        if dry_run:
            preview = html_body[:200].replace('\n', ' ')
            return True, (
                f"[DRY RUN] Draft: \"{title}\"\n"
                f"  Subtitle: {subtitle or '(none)'}\n"
                f"  Audience: {audience}\n"
                f"  Body length: {len(html_body)} chars HTML\n"
                f"  Preview: {preview}..."
            )

        if requests is None:
            return False, "requests is required; install with: pip install '.[publishing]'"

        # Login if needed
        if not self.session:
            ok, msg = self._login()
            if not ok:
                return False, msg

        # Create draft via Substack API
        payload = {
            "draft_title": title,
            "draft_subtitle": subtitle,
            "draft_body": html_body,
            "audience": audience,
            "type": "newsletter",
            "draft_bylines": [{}],
        }

        try:
            resp = self.session.post(
                f"{self.base_url}/api/v1/drafts",
                json=payload,
                timeout=30,
            )
            if resp.ok:
                data = resp.json()
                draft_id = data.get("id", "created")
                edit_url = f"{self.base_url}/publish/post/{draft_id}"
                return True, f"Draft created: {edit_url}"
            else:
                msg = resp.text[:200]
                try:
                    msg = resp.json().get("error", msg)
                except Exception:
                    pass
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, f"Draft creation error: {e}"


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def format_output(success: bool, detail: str, filepath: Path, dry_run: bool = False) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "SUBSTACK PUBLISHER" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"Source: {filepath}",
        "",
    ]

    if success:
        lines.append(detail)
    else:
        lines.extend([
            "Failed to create draft.",
            f"Error: {detail}",
            "",
            "If the API has changed, fall back to manual copy-paste into the Substack editor.",
        ])

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Substack Draft Creator — push articles as drafts"
    )
    parser.add_argument(
        "--draft",
        metavar="FILE",
        help="Path to markdown article to create as draft",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview without creating draft",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Substack connection",
    )

    args = parser.parse_args()

    if args.dry_run and args.test:
        parser.error("--dry-run cannot be combined with --test (a live connection check)")
    if not args.draft and not args.test:
        parser.print_help()
        return 1

    # Dry runs render locally and never require credentials.
    email = os.environ.get("SUBSTACK_EMAIL")
    password = os.environ.get("SUBSTACK_PASSWORD")
    subdomain = os.environ.get("SUBSTACK_SUBDOMAIN")

    if not args.dry_run and (not email or not password or not subdomain):
        print("Error: Missing Substack credentials.", file=sys.stderr)
        print("Required: SUBSTACK_EMAIL, SUBSTACK_PASSWORD, SUBSTACK_SUBDOMAIN", file=sys.stderr)
        print("Export these environment variables before making a live request.", file=sys.stderr)
        return 1

    client = SubstackPublisher(email or "", password or "", subdomain or "example")

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

        ok, detail = client.create_draft(filepath, dry_run=args.dry_run)
        print(format_output(ok, detail, filepath, dry_run=args.dry_run))
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
