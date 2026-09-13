#!/usr/bin/env python3
"""
Notion Content Database Publisher
----------------------------------
Parse a content calendar markdown file and create one Notion database row
per content piece + associated asset items.

Usage:
    python3 tools/notion_content_db.py --setup --parent-page-id <PAGE_ID>
    python3 tools/notion_content_db.py --publish brains/mitl/content/personal/calendar-2026-03.md
    python3 tools/notion_content_db.py --publish brains/mitl/content/personal/calendar-2026-03.md --dry-run
    python3 tools/notion_content_db.py --test

Environment variables (export explicitly):
    NOTION_API_KEY          - Notion integration API key
    NOTION_CONTENT_DB_ID    - Content database ID (set after --setup)
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ContentItem:
    """A single content piece or asset from the calendar."""
    title: str
    item_type: str = "Content"  # Content, Asset, Offer
    show: str = ""              # Build Log, Hot Take, Framework, Skill Drop, Tool Bench
    channels: list = field(default_factory=list)
    status: str = "To Produce"
    publish_date: str = ""      # e.g. "2026-03-07"
    week: str = ""              # Week 1, Week 2, etc.
    pillar: str = ""
    content_type: str = "New"   # New, Redistribute, Flex
    month_theme: str = ""
    cta: str = ""
    cta_keyword: str = ""
    notes: str = ""
    asset_items: list = field(default_factory=list)  # titles of linked assets


# ---------------------------------------------------------------------------
# Calendar parser
# ---------------------------------------------------------------------------

# Day abbreviations to full day names for date extraction
DAY_ABBREVS = {
    "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
    "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday",
}

SHOW_MAP = {
    "Build Log": "Build Log",
    "Build Log (Flagship)": "Build Log",
    "BUILD LOG": "Build Log",
    "Flagship": "Build Log",
    "Hot Take": "Hot Take",
    "HOT TAKE": "Hot Take",
    "Framework": "Framework",
    "Skill Drop": "Skill Drop",
    "SKILL DROP": "Skill Drop",
    "Tool Bench": "Tool Bench",
    "TOOL BENCH": "Tool Bench",
    "Pillar Post": "Pillar Post",
    "PILLAR POST": "Pillar Post",
    "Reader Intel": "Reader Intel",
    "READER INTEL": "Reader Intel",
}

CHANNEL_MAP = {
    "LI": "LinkedIn",
    "LinkedIn": "LinkedIn",
    "Twitter": "Twitter",
    "Twitter/X": "Twitter",
    "Substack": "Substack",
    "Email": "Email",
}


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
    fm = {}
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, _, val = line.partition(':')
                fm[key.strip()] = val.strip()
    return fm


def parse_channels(platform_str: str) -> list[str]:
    """Parse platform string like 'Substack + LI + Twitter' into channel list."""
    channels = []
    for part in re.split(r'\s*\+\s*', platform_str.strip()):
        part = part.strip()
        mapped = CHANNEL_MAP.get(part, part)
        if mapped and mapped not in channels:
            channels.append(mapped)
    return channels


def parse_date(day_str: str, year: int = 2026) -> str:
    """Parse date string like 'Sat Mar 7' into ISO date '2026-03-07'."""
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    # Try pattern: "Day Mon DD"
    m = re.search(r'(\w{3})\s+(\d{1,2})', day_str)
    if m:
        month_abbr = m.group(1)
        day_num = int(m.group(2))
        month_num = month_map.get(month_abbr)
        if month_num:
            return f"{year}-{month_num:02d}-{day_num:02d}"
    return ""


def extract_cta_keyword(cta_str: str) -> str:
    """Extract the keyword from a CTA like 'Comment SKILL → DM'."""
    m = re.search(r'Comment\s+(\w+)', cta_str)
    if m:
        return m.group(1)
    return ""


def parse_show(show_str: str) -> str:
    """Normalize show name."""
    show_str = show_str.strip()
    # Remove parenthetical like "(Flagship)"
    for key, val in SHOW_MAP.items():
        if key.lower() in show_str.lower():
            return val
    return show_str


def parse_content_status(status_str: str) -> str:
    """Parse status from calendar (New, Redistribute, etc.) into DB status."""
    s = status_str.strip().lower()
    if "redistribute" in s:
        return "Redistribute"
    if "flex" in s:
        return "Flex"
    return "New"


def parse_table_rows(table_text: str) -> list[dict]:
    """Parse a markdown table into list of dicts using header row as keys."""
    lines = [l.strip() for l in table_text.strip().split('\n') if l.strip()]
    if len(lines) < 3:
        return []

    # Header row
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    # Skip separator line (lines[1])
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if len(cells) >= len(headers):
            row = {}
            for i, h in enumerate(headers):
                row[h] = cells[i] if i < len(cells) else ""
            rows.append(row)
    return rows


def extract_year_from_frontmatter(fm: dict) -> int:
    """Get year from frontmatter title like 'Content Calendar — March 2026'."""
    title = fm.get("title", "")
    m = re.search(r'(\d{4})', title)
    if m:
        return int(m.group(1))
    return 2026


def parse_calendar(filepath: Path) -> list[ContentItem]:
    """Parse a content calendar markdown file into ContentItem list."""
    content = filepath.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    theme = fm.get("theme", "")
    pillar_default = fm.get("pillar", "")
    year = extract_year_from_frontmatter(fm)

    items = []
    asset_items = []

    # Find week sections
    week_pattern = re.compile(
        r'### Week (\d+):.*?\n(.*?)(?=\n### Week |\n---|\n## |\Z)',
        re.DOTALL
    )

    for week_match in week_pattern.finditer(content):
        week_num = int(week_match.group(1))
        week_label = f"Week {week_num}"
        week_body = week_match.group(2)

        # Find the table in this week section
        table_match = re.search(
            r'(\|.*Day.*\|.*\n\|[-| :]+\|\n(?:\|.*\n)*)',
            week_body
        )
        if not table_match:
            continue

        table_text = table_match.group(1)
        rows = parse_table_rows(table_text)

        for row in rows:
            day_str = row.get("Day", "")
            show_raw = row.get("Show", "")
            title_raw = row.get("Title/Topic", "")
            platform_raw = row.get("Platform", "")
            status_raw = row.get("Status", "")
            pillar_raw = row.get("Pillar", pillar_default)
            cta_raw = row.get("CTA", "")

            # Clean title — strip bold markers and quotes
            title_clean = re.sub(r'\*\*', '', title_raw).strip()
            # Truncate at first " — " for very long descriptions (keep main title)
            # But keep it if it's short enough
            if len(title_clean) > 200:
                parts = title_clean.split(" — ", 1)
                title_clean = parts[0]

            # Detect redistribute
            is_redistribute = "redistribute" in status_raw.lower() or "REDISTRIBUTE" in title_raw

            item = ContentItem(
                title=title_clean,
                item_type="Content",
                show=parse_show(show_raw),
                channels=parse_channels(platform_raw),
                status="To Produce",
                publish_date=parse_date(day_str, year),
                week=week_label,
                pillar=pillar_raw.strip(),
                content_type="Redistribute" if is_redistribute else parse_content_status(status_raw),
                month_theme=theme,
                cta=cta_raw.strip(),
                cta_keyword=extract_cta_keyword(cta_raw),
                notes="",
            )

            # Detect associated assets from Skill Drop CTA patterns
            if item.show == "Skill Drop" and item.cta_keyword:
                asset_title = f"DM Deliverable: {item.cta_keyword} — {item.title[:80]}"
                asset = ContentItem(
                    title=asset_title,
                    item_type="Asset",
                    show="",
                    channels=["Skills Library"],
                    status="To Produce",
                    publish_date=item.publish_date,
                    week=week_label,
                    pillar=item.pillar,
                    content_type="New",
                    month_theme=theme,
                    notes=f"DM deliverable for Skill Drop. Keyword: {item.cta_keyword}",
                )
                asset_items.append(asset)
                item.asset_items.append(asset_title)

            items.append(item)

    # Add asset items at the end
    items.extend(asset_items)

    return items


# ---------------------------------------------------------------------------
# Notion API client
# ---------------------------------------------------------------------------

class NotionContentDB:
    """Manage the Content Production database in Notion."""

    API_URL = "https://api.notion.com/v1"
    VERSION = "2022-06-28"

    # Database property definitions for --setup
    DB_PROPERTIES = {
        "Title": {"title": {}},
        "Item Type": {
            "select": {
                "options": [
                    {"name": "Content", "color": "blue"},
                    {"name": "Asset", "color": "green"},
                    {"name": "Offer", "color": "purple"},
                ]
            }
        },
        "Show": {
            "select": {
                "options": [
                    {"name": "Build Log", "color": "blue"},
                    {"name": "Hot Take", "color": "red"},
                    {"name": "Framework", "color": "orange"},
                    {"name": "Skill Drop", "color": "green"},
                    {"name": "Tool Bench", "color": "yellow"},
                    {"name": "Pillar Post", "color": "purple"},
                    {"name": "Reader Intel", "color": "pink"},
                ]
            }
        },
        "Channel": {
            "multi_select": {
                "options": [
                    {"name": "LinkedIn", "color": "blue"},
                    {"name": "Twitter", "color": "default"},
                    {"name": "Substack", "color": "orange"},
                    {"name": "Email", "color": "yellow"},
                    {"name": "Skills Library", "color": "green"},
                ]
            }
        },
        "Status": {
            "status": {
                "options": [
                    {"name": "To Produce", "color": "default"},
                    {"name": "Produced", "color": "blue"},
                    {"name": "Scheduled", "color": "yellow"},
                    {"name": "Published", "color": "green"},
                ],
                "groups": [
                    {"name": "To-do", "option_names": ["To Produce"]},
                    {"name": "In progress", "option_names": ["Produced", "Scheduled"]},
                    {"name": "Complete", "option_names": ["Published"]},
                ]
            }
        },
        "Publish Date": {"date": {}},
        "Week": {
            "select": {
                "options": [
                    {"name": "Week 1", "color": "blue"},
                    {"name": "Week 2", "color": "green"},
                    {"name": "Week 3", "color": "orange"},
                    {"name": "Week 4", "color": "red"},
                ]
            }
        },
        "Pillar": {
            "select": {
                "options": [
                    {"name": "AI-Equipped Growth", "color": "blue"},
                    {"name": "Founder-Stage", "color": "green"},
                    {"name": "Industry POV", "color": "orange"},
                    {"name": "Builder Stories", "color": "purple"},
                ]
            }
        },
        "Content Type": {
            "select": {
                "options": [
                    {"name": "New", "color": "blue"},
                    {"name": "Redistribute", "color": "green"},
                    {"name": "Flex", "color": "yellow"},
                ]
            }
        },
        "Month Theme": {"rich_text": {}},
        "Asset Ready": {"checkbox": {}},
        "CTA": {"rich_text": {}},
        "CTA Keyword": {"rich_text": {}},
        "Published URL": {"url": {}},
        "Notes": {"rich_text": {}},
    }

    def __init__(self, api_key: str, database_id: str = ""):
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.VERSION,
        }

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Notion API."""
        if requests is None:
            return False, "requests library not installed. Run: pip install requests"
        try:
            if self.database_id:
                resp = requests.get(
                    f"{self.API_URL}/databases/{self.database_id}",
                    headers=self.headers, timeout=10,
                )
                if resp.ok:
                    data = resp.json()
                    title_parts = data.get("title", [])
                    name = title_parts[0].get("plain_text", "DB") if title_parts else "DB"
                    return True, f"Connected to database: {name}"
                return False, f"HTTP {resp.status_code}: {resp.json().get('message', '')}"
            else:
                # Just test auth by listing users
                resp = requests.get(
                    f"{self.API_URL}/users/me",
                    headers=self.headers, timeout=10,
                )
                if resp.ok:
                    return True, "API key valid (no database ID set — run --setup first)"
                return False, f"HTTP {resp.status_code}: {resp.json().get('message', '')}"
        except Exception as e:
            return False, str(e)

    def setup_database(self, parent_page_id: str) -> tuple[bool, str]:
        """Create the Content Production database with all properties."""
        if requests is None:
            return False, "requests library not installed"

        # Notion Status property can't be created via API with custom options —
        # it auto-creates with defaults. We'll use a Select instead for Status.
        # Build properties dict, replacing Status with Select.
        props = {}
        for key, val in self.DB_PROPERTIES.items():
            if key == "Status":
                # Use Select instead — Notion API doesn't allow creating
                # Status properties with custom groups
                props[key] = {
                    "select": {
                        "options": [
                            {"name": "To Produce", "color": "default"},
                            {"name": "Produced", "color": "blue"},
                            {"name": "Scheduled", "color": "yellow"},
                            {"name": "Published", "color": "green"},
                        ]
                    }
                }
            else:
                props[key] = val

        payload = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": "Content Production"}}],
            "properties": props,
        }

        try:
            resp = requests.post(
                f"{self.API_URL}/databases",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            if resp.ok:
                data = resp.json()
                db_id = data["id"]
                return True, db_id
            else:
                msg = resp.json().get("message", resp.text[:200])
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, str(e)

    def create_page(self, item: ContentItem, dry_run: bool = False) -> tuple[bool, str]:
        """Create a Notion page for one ContentItem."""
        if dry_run:
            channels_str = ", ".join(item.channels) if item.channels else "—"
            return True, f"[DRY RUN] {item.item_type}: {item.title[:60]} | {item.show} | {channels_str} | {item.publish_date}"

        if requests is None:
            return False, "requests library not installed"

        # Map Stage status from calendar status
        stage_map = {
            "To Produce": "Idea",
            "Published": "Live",
            "Draft in Publer": "Merchandising and Scheduling",
            "Not scheduled": "Idea",
        }
        stage = stage_map.get(item.status, "Idea")

        # Map content type to Notion Content Type options
        content_type_map = {
            "Build Log": "Blog Post",
            "Hot Take": "Social Media",
            "Pillar Post": "Social Media",
            "Reader Intel": "Social Media",
            "Skill Drop": "Video",
            "Tool Bench": "Blog Post",
        }
        notion_content_type = content_type_map.get(item.show, "Social Media")

        properties = {
            "Content Piece": {
                "title": [{"text": {"content": item.title[:200]}}]
            },
            "Stage": {"status": {"name": stage}},
            "Content Type": {"select": {"name": notion_content_type}},
        }

        # Series or Franchise = Show name (Notion auto-creates new select options)
        if item.show:
            properties["Series or Franchise"] = {"select": {"name": item.show}}

        # Primary Channel — select, use first channel
        if item.channels:
            properties["Primary Channel"] = {"select": {"name": item.channels[0]}}

        if item.publish_date:
            properties["Target Publish Date"] = {"date": {"start": item.publish_date}}

        if item.pillar:
            properties["Content Pillar"] = {"select": {"name": item.pillar}}

        # Pack remaining info into Brief Notes
        notes_parts = []
        if item.week:
            notes_parts.append(item.week)
        if item.month_theme:
            notes_parts.append(f"Theme: {item.month_theme}")
        if item.cta:
            notes_parts.append(f"CTA: {item.cta}")
        if item.notes:
            notes_parts.append(item.notes)
        if notes_parts:
            properties["Brief Notes"] = {
                "rich_text": [{"text": {"content": " | ".join(notes_parts)}}]
            }

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
        }

        try:
            resp = requests.post(
                f"{self.API_URL}/pages",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            if resp.ok:
                page_id = resp.json()["id"]
                return True, page_id
            else:
                msg = resp.json().get("message", resp.text[:200])
                return False, f"HTTP {resp.status_code}: {msg}"
        except Exception as e:
            return False, str(e)

    def publish_calendar(self, filepath: Path, dry_run: bool = False) -> dict:
        """Parse calendar and create all items in Notion."""
        items = parse_calendar(filepath)

        results = {
            "total": len(items),
            "content": 0,
            "assets": 0,
            "succeeded": 0,
            "failed": 0,
            "details": [],
        }

        for item in items:
            if item.item_type == "Content":
                results["content"] += 1
            else:
                results["assets"] += 1

            success, detail = self.create_page(item, dry_run=dry_run)

            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "title": item.title[:60],
                "type": item.item_type,
                "success": success,
                "detail": detail,
            })

            # Rate limit spacing (Notion allows ~3 req/sec)
            if not dry_run:
                time.sleep(0.4)

        return results


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------

def format_setup_output(success: bool, result: str) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "NOTION CONTENT DB — SETUP",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    if success:
        lines.extend([
            "Database created successfully.",
            "",
            f"Database ID: {result}",
            "",
            "Export this variable in your shell:",
            f"NOTION_CONTENT_DB_ID={result}",
            "",
            "Then run: python3 tools/notion_content_db.py --publish <calendar.md>",
        ])
    else:
        lines.extend([
            "Setup failed.",
            f"Error: {result}",
        ])
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def format_publish_output(results: dict, filepath: Path, dry_run: bool = False) -> str:
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "NOTION CONTENT DB — PUBLISH" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"Source: {filepath}",
        f"Total items: {results['total']} ({results['content']} content + {results['assets']} assets)",
        f"Succeeded: {results['succeeded']}",
        f"Failed: {results['failed']}",
        "",
    ]

    # Show details
    for d in results["details"]:
        icon = "+" if d["success"] else "x"
        lines.append(f"  [{icon}] {d['type'][:7]:7s} | {d['title']}")

    if results["failed"] > 0:
        lines.append("")
        lines.append("Failures:")
        for d in results["details"]:
            if not d["success"]:
                lines.append(f"  {d['title']}: {d['detail']}")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Notion Content Database — publish calendar to production tracker"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Create the database with all properties",
    )
    parser.add_argument(
        "--parent-page-id",
        help="Notion page ID to create database under (required for --setup)",
    )
    parser.add_argument(
        "--publish",
        metavar="FILE",
        help="Path to content calendar markdown file",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview without publishing",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Notion connection",
    )

    args = parser.parse_args()

    # Get credentials
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        print("Error: NOTION_API_KEY not exported in the environment", file=sys.stderr)
        return 1

    db_id = os.environ.get("NOTION_CONTENT_DB_ID", "")
    client = NotionContentDB(api_key, db_id)

    # --test
    if args.test:
        ok, msg = client.test_connection()
        print(f"{'OK' if ok else 'FAIL'}: {msg}")
        return 0 if ok else 1

    # --setup
    if args.setup:
        if not args.parent_page_id:
            print("Error: --parent-page-id is required for --setup", file=sys.stderr)
            return 1
        ok, result = client.setup_database(args.parent_page_id)
        print(format_setup_output(ok, result))
        return 0 if ok else 1

    # --publish
    if args.publish:
        if not db_id and not args.dry_run:
            print("Error: NOTION_CONTENT_DB_ID not set. Run --setup first.", file=sys.stderr)
            return 1

        filepath = Path(args.publish)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return 1

        results = client.publish_calendar(filepath, dry_run=args.dry_run)
        print(format_publish_output(results, filepath, dry_run=args.dry_run))
        return 0 if results["failed"] == 0 else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
