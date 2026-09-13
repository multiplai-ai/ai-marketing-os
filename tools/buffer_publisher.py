#!/usr/bin/env python3
"""
Buffer Publisher Tool
---------------------
Parse flagship markdown files and publish posts to Buffer (social) and Notion (long-form).

Usage:
    python3 tools/buffer_publisher.py                    # Auto-detect latest flagship
    python3 tools/buffer_publisher.py --file <path>      # Specific file
    python3 tools/buffer_publisher.py --dry-run          # Preview without sending
    python3 tools/buffer_publisher.py --day monday       # Single day only
    python3 tools/buffer_publisher.py --test             # Test parsing against sample file
    python3 tools/buffer_publisher.py --notion           # Publish Monday long-form to Notion
    python3 tools/buffer_publisher.py --all              # Publish social posts + Notion

Architecture:
    Uses PublisherBackend abstraction for flexibility:
    - ZapierBackend: Sends to Buffer via Zapier webhook (social posts)
    - NotionPublisher: Sends long-form to Notion database (for Substack editing)
"""

import argparse
import json
import os
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Configuration
CONTENT_DIR = PROJECT_ROOT / "projects" / "Social Media Strategy" / "content"
LINKEDIN_CHAR_LIMIT = 3000


@dataclass
class SocialPost:
    """Represents a single social media post extracted from flagship content."""
    day: str                          # "Monday", "Tuesday", etc.
    title: str                        # Section title (e.g., "Flagship Post")
    content: str                      # Post text
    posting_time: Optional[str] = None  # e.g., "Monday 9:00 AM"
    pillar: Optional[str] = None
    format: Optional[str] = None
    char_count: int = field(init=False)

    def __post_init__(self):
        self.char_count = len(self.content)

    def exceeds_limit(self) -> bool:
        return self.char_count > LINKEDIN_CHAR_LIMIT


@dataclass
class PublishResult:
    """Result of publishing a single post."""
    success: bool
    post: SocialPost
    buffer_id: Optional[str] = None
    error: Optional[str] = None


class PublisherBackend(ABC):
    """Abstract base class for publisher backends."""

    @abstractmethod
    def publish_draft(self, post: SocialPost) -> PublishResult:
        """Publish a post as a draft. Returns PublishResult."""
        pass

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Test the backend connection. Returns (success, message)."""
        pass


class ZapierBackend(PublisherBackend):
    """Publish to Buffer via Zapier webhook."""

    def __init__(self, webhook_url: str, profile_id: str):
        self.webhook_url = webhook_url
        self.profile_id = profile_id

    def publish_draft(self, post: SocialPost) -> PublishResult:
        if requests is None:
            return PublishResult(
                success=False,
                post=post,
                error="requests library not installed. Run: pip install requests"
            )

        payload = {
            "text": post.content,
            "profile_id": self.profile_id,
            "day": post.day,
            "title": post.title,
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.ok:
                return PublishResult(
                    success=True,
                    post=post,
                    buffer_id=response.json().get("id") if response.text else None
                )
            else:
                return PublishResult(
                    success=False,
                    post=post,
                    error=f"HTTP {response.status_code}: {response.text[:200]}"
                )

        except requests.exceptions.Timeout:
            return PublishResult(success=False, post=post, error="Request timed out")
        except requests.exceptions.RequestException as e:
            return PublishResult(success=False, post=post, error=str(e))

    def test_connection(self) -> tuple[bool, str]:
        if requests is None:
            return False, "requests library not installed"

        try:
            # Send a minimal test payload
            response = requests.post(
                self.webhook_url,
                json={"test": True, "profile_id": self.profile_id},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.ok:
                return True, "Zapier webhook connected"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)


class DryRunBackend(PublisherBackend):
    """Mock backend for dry-run testing."""

    def publish_draft(self, post: SocialPost) -> PublishResult:
        return PublishResult(
            success=True,
            post=post,
            buffer_id="dry-run-mock-id"
        )

    def test_connection(self) -> tuple[bool, str]:
        return True, "Dry run mode (no actual publishing)"


# =============================================================================
# Notion Publisher (Long-Form Articles)
# =============================================================================

@dataclass
class HyperlinkRef:
    """A hyperlink extracted from the article."""
    text: str
    url: str
    context: Optional[str] = None  # Surrounding text for context


@dataclass
class LongFormArticle:
    """Represents the Monday long-form article for Substack."""
    title: str
    content: str
    pillar: Optional[str]
    word_count: int
    hyperlinks: list[HyperlinkRef]
    resources_section: Optional[str] = None


@dataclass
class NotionPublishResult:
    """Result of publishing to Notion."""
    success: bool
    page_url: Optional[str] = None
    page_id: Optional[str] = None
    error: Optional[str] = None


def extract_hyperlinks(content: str) -> list[HyperlinkRef]:
    """Extract all markdown hyperlinks from content."""
    # Pattern: [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)

    hyperlinks = []
    for text, url in matches:
        hyperlinks.append(HyperlinkRef(text=text, url=url))

    return hyperlinks


def parse_monday_article(filepath: Path) -> Optional[LongFormArticle]:
    """Extract the Monday long-form article from flagship file."""
    content = filepath.read_text(encoding="utf-8")

    # Find Monday section
    monday_match = re.search(
        r"## Monday\s*[—-]\s*(.+?)\n(.*?)(?=\n## (?:Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)|\n## Source Material|\Z)",
        content,
        re.DOTALL
    )

    if not monday_match:
        return None

    section_title = monday_match.group(1).strip()
    section_content = monday_match.group(2)

    # Extract pillar
    pillar = None
    pillar_match = re.search(r"\*\*Pillar:\*\*\s*(.+?)$", section_content, re.MULTILINE)
    if pillar_match:
        pillar = pillar_match.group(1).strip()

    # Extract post content after "### Post"
    post_match = re.search(r"### Post\s*\n(.+?)(?=\n---|\Z)", section_content, re.DOTALL)
    if not post_match:
        return None

    article_content = post_match.group(1).strip()

    # Extract resources section if present
    resources_section = None
    resources_match = re.search(
        r"\*\*Resources mentioned.*?\*\*:?\s*\n((?:- .+\n?)+)",
        article_content,
        re.IGNORECASE
    )
    if resources_match:
        resources_section = resources_match.group(0).strip()

    # Extract hyperlinks
    hyperlinks = extract_hyperlinks(article_content)

    # Word count
    word_count = len(article_content.split())

    # Extract title from the article content (first # heading)
    title_match = re.search(r"^# (.+?)$", article_content, re.MULTILINE)
    title = title_match.group(1) if title_match else section_title

    return LongFormArticle(
        title=title,
        content=article_content,
        pillar=pillar,
        word_count=word_count,
        hyperlinks=hyperlinks,
        resources_section=resources_section
    )


def markdown_to_notion_blocks(content: str) -> list[dict]:
    """Convert markdown content to Notion block format."""
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # H1 heading
        if line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": parse_rich_text(line[2:].strip())
                }
            })
        # H2 heading
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": parse_rich_text(line[3:].strip())
                }
            })
        # H3 heading
        elif line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": parse_rich_text(line[4:].strip())
                }
            })
        # Bullet list
        elif line.startswith('- '):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_rich_text(line[2:].strip())
                }
            })
        # Horizontal rule
        elif line.strip() == '---':
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        # Bold line (like **Resources mentioned:**)
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": parse_rich_text(line.strip())
                }
            })
        # Regular paragraph
        else:
            # Collect consecutive non-empty, non-special lines as one paragraph
            para_lines = [line]
            while i + 1 < len(lines):
                next_line = lines[i + 1]
                if (next_line.strip() and
                    not next_line.startswith('#') and
                    not next_line.startswith('- ') and
                    next_line.strip() != '---'):
                    para_lines.append(next_line)
                    i += 1
                else:
                    break

            para_text = ' '.join(para_lines).strip()
            if para_text:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": parse_rich_text(para_text)
                    }
                })

        i += 1

    return blocks


def parse_rich_text(text: str) -> list[dict]:
    """Parse markdown text into Notion rich_text format with links and formatting."""
    rich_text = []

    # Pattern to find markdown links [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    last_end = 0
    for match in re.finditer(link_pattern, text):
        # Add text before the link
        if match.start() > last_end:
            before_text = text[last_end:match.start()]
            if before_text:
                rich_text.extend(parse_formatting(before_text))

        # Add the link
        link_text = match.group(1)
        link_url = match.group(2)
        rich_text.append({
            "type": "text",
            "text": {
                "content": link_text,
                "link": {"url": link_url}
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            }
        })

        last_end = match.end()

    # Add remaining text after last link
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            rich_text.extend(parse_formatting(remaining))

    # If no links found, just parse formatting
    if not rich_text:
        rich_text = parse_formatting(text)

    return rich_text if rich_text else [{"type": "text", "text": {"content": text}}]


def parse_formatting(text: str) -> list[dict]:
    """Parse bold/italic formatting in text."""
    result = []

    # Simple approach: handle **bold**
    bold_pattern = r'\*\*([^*]+)\*\*'

    last_end = 0
    for match in re.finditer(bold_pattern, text):
        # Text before bold
        if match.start() > last_end:
            before = text[last_end:match.start()]
            if before:
                result.append({
                    "type": "text",
                    "text": {"content": before}
                })

        # Bold text
        result.append({
            "type": "text",
            "text": {"content": match.group(1)},
            "annotations": {"bold": True}
        })

        last_end = match.end()

    # Remaining text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            result.append({
                "type": "text",
                "text": {"content": remaining}
            })

    if not result:
        result.append({
            "type": "text",
            "text": {"content": text}
        })

    return result


class NotionPublisher:
    """Publish long-form articles to Notion database."""

    NOTION_API_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION
        }

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Notion API."""
        if requests is None:
            return False, "requests library not installed"

        try:
            response = requests.get(
                f"{self.NOTION_API_URL}/databases/{self.database_id}",
                headers=self.headers,
                timeout=10
            )
            if response.ok:
                db_data = response.json()
                return True, f"Connected to: {db_data.get('title', [{}])[0].get('plain_text', 'Database')}"
            else:
                return False, f"HTTP {response.status_code}: {response.json().get('message', response.text[:100])}"
        except Exception as e:
            return False, str(e)

    def publish_article(self, article: LongFormArticle, dry_run: bool = False) -> NotionPublishResult:
        """Publish article to Notion database."""
        if requests is None:
            return NotionPublishResult(success=False, error="requests library not installed")

        if dry_run:
            return NotionPublishResult(
                success=True,
                page_url="https://notion.so/dry-run-preview",
                page_id="dry-run-id"
            )

        # Build the page
        # Convert content to Notion blocks
        content_blocks = markdown_to_notion_blocks(article.content)

        # Notion API limits children to 100 blocks per request
        # For longer articles, we'll add first 100, then append more
        initial_blocks = content_blocks[:100]
        remaining_blocks = content_blocks[100:]

        page_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {"content": article.title}
                        }
                    ]
                },
                "Stage": {
                    "status": {
                        "name": "Editing"
                    }
                }
            },
            "children": initial_blocks
        }

        # Add Content Pillar if article has one
        if article.pillar:
            page_data["properties"]["Content Pillar"] = {
                "select": {"name": article.pillar}
            }

        # Set Content Type to Blog Post (for Substack)
        page_data["properties"]["Content Type"] = {
            "select": {"name": "Blog Post"}
        }

        # Set Primary Channel to Substack
        page_data["properties"]["Primary Channel"] = {
            "select": {"name": "Substack"}
        }

        try:
            # Create the page
            response = requests.post(
                f"{self.NOTION_API_URL}/pages",
                headers=self.headers,
                json=page_data,
                timeout=30
            )

            if not response.ok:
                error_msg = response.json().get('message', response.text[:200])
                return NotionPublishResult(success=False, error=f"HTTP {response.status_code}: {error_msg}")

            page_result = response.json()
            page_id = page_result["id"]
            page_url = page_result.get("url", f"https://notion.so/{page_id.replace('-', '')}")

            # Append remaining blocks if any
            for i in range(0, len(remaining_blocks), 100):
                chunk = remaining_blocks[i:i+100]
                append_response = requests.patch(
                    f"{self.NOTION_API_URL}/blocks/{page_id}/children",
                    headers=self.headers,
                    json={"children": chunk},
                    timeout=30
                )
                if not append_response.ok:
                    # Log but don't fail - partial content is better than none
                    print(f"Warning: Could not append all content blocks", file=sys.stderr)
                    break

            return NotionPublishResult(
                success=True,
                page_url=page_url,
                page_id=page_id
            )

        except requests.exceptions.Timeout:
            return NotionPublishResult(success=False, error="Request timed out")
        except requests.exceptions.RequestException as e:
            return NotionPublishResult(success=False, error=str(e))


def format_notion_preview(article: LongFormArticle) -> str:
    """Format article preview for Notion publishing."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "NOTION ARTICLE PREVIEW",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"Title: {article.title}",
        f"Pillar: {article.pillar or 'Not specified'}",
        f"Word count: {article.word_count:,}",
        f"Hyperlinks: {len(article.hyperlinks)}",
        "",
        "Links to embed/verify:",
        "-" * 40,
    ]

    for i, link in enumerate(article.hyperlinks, 1):
        lines.append(f"  {i}. [{link.text}]")
        lines.append(f"     {link.url}")

    lines.extend([
        "-" * 40,
        "",
        "Content preview (first 500 chars):",
        "-" * 40,
    ])

    preview = article.content[:500]
    if len(article.content) > 500:
        preview += "..."
    for line in preview.split('\n')[:15]:
        lines.append(f"  {line}")

    lines.extend([
        "-" * 40,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ])

    return "\n".join(lines)


def format_notion_result(result: NotionPublishResult, article: LongFormArticle) -> str:
    """Format Notion publish result."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "NOTION PUBLISH RESULT",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    if result.success:
        lines.extend([
            f"✓ Published: {article.title}",
            f"  Word count: {article.word_count:,}",
            f"  Links: {len(article.hyperlinks)}",
            "",
            f"Page URL: {result.page_url}",
            "",
            "Next steps:",
            "1. Open the Notion page",
            "2. Review and edit content",
            "3. Add images/embeds",
            "4. Style headings and formatting",
            "5. Copy to Substack and publish"
        ])
    else:
        lines.extend([
            f"✗ Failed to publish",
            f"  Error: {result.error}"
        ])

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def find_latest_flagship() -> Optional[Path]:
    """Find the most recent pub-flagship-*.md file."""
    # Search in content dir and subdirectories (LIVE/, etc.)
    pattern = str(CONTENT_DIR / "**" / "pub-flagship-*.md")
    files = glob(pattern, recursive=True)
    # Also check direct content dir
    direct_pattern = str(CONTENT_DIR / "pub-flagship-*.md")
    files.extend(glob(direct_pattern))
    if not files:
        return None

    # Sort by date in filename (descending)
    def extract_date(filepath: str) -> str:
        match = re.search(r"pub-flagship-(\d{4}-\d{2}-\d{2})\.md$", filepath)
        return match.group(1) if match else ""

    files.sort(key=extract_date, reverse=True)
    return Path(files[0])


def parse_flagship_markdown(filepath: Path) -> list[SocialPost]:
    """
    Parse a flagship markdown file and extract all social posts.

    Expected format:
    - Posts separated by `---` horizontal rules
    - Day headers: `## Monday - Post Type`
    - Post content after `### Post` header
    - Metadata: `**Best posting time:** Monday 9:00 AM`
    """
    content = filepath.read_text(encoding="utf-8")
    posts = []

    # Split by day sections (## Monday, ## Tuesday, etc.)
    day_pattern = r"^## (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*[—-]\s*(.+?)$"
    day_sections = re.split(day_pattern, content, flags=re.MULTILINE)

    # day_sections will be: [preamble, day1, title1, content1, day2, title2, content2, ...]
    # Skip preamble (index 0), then process in groups of 3
    i = 1
    while i + 2 < len(day_sections):
        day = day_sections[i].strip()
        title = day_sections[i + 1].strip()
        section_content = day_sections[i + 2]

        # Skip the flagship post (Monday editorial) - too long for LinkedIn
        # Actually, let's include it but flag if it exceeds the limit
        # The user can decide whether to include or skip it

        # Extract post content after "### Post"
        post_match = re.search(
            r"### Post\s*\n(.+?)(?=\n---|\n## |\n### |\Z)",
            section_content,
            re.DOTALL
        )

        if post_match:
            post_content = post_match.group(1).strip()

            # Extract metadata
            posting_time = None
            time_match = re.search(r"\*\*Best posting time:\*\*\s*(.+?)$", section_content, re.MULTILINE)
            if time_match:
                posting_time = time_match.group(1).strip()

            pillar = None
            pillar_match = re.search(r"\*\*Pillar:\*\*\s*(.+?)$", section_content, re.MULTILINE)
            if pillar_match:
                pillar = pillar_match.group(1).strip()

            format_type = None
            format_match = re.search(r"\*\*Format:\*\*\s*(.+?)$", section_content, re.MULTILINE)
            if format_match:
                format_type = format_match.group(1).strip()

            posts.append(SocialPost(
                day=day,
                title=title,
                content=post_content,
                posting_time=posting_time,
                pillar=pillar,
                format=format_type
            ))

        i += 3

    return posts


def format_preview(posts: list[SocialPost], day_filter: Optional[str] = None) -> str:
    """Format posts for preview display."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "PARSED POSTS PREVIEW",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    filtered_posts = posts
    if day_filter:
        filtered_posts = [p for p in posts if p.day.lower() == day_filter.lower()]

    if not filtered_posts:
        lines.append(f"No posts found{f' for {day_filter}' if day_filter else ''}.")
        return "\n".join(lines)

    for post in filtered_posts:
        warning = " ⚠️ EXCEEDS LINKEDIN LIMIT" if post.exceeds_limit() else ""
        lines.extend([
            f"## {post.day} — {post.title}{warning}",
            f"   Characters: {post.char_count:,} / {LINKEDIN_CHAR_LIMIT:,}",
            f"   Posting time: {post.posting_time or 'Not specified'}",
            "",
            "   Content preview:",
            "   " + "-" * 40,
        ])

        # Show first 300 chars of content
        preview = post.content[:300]
        if len(post.content) > 300:
            preview += "..."
        for line in preview.split("\n"):
            lines.append(f"   {line}")

        lines.extend([
            "   " + "-" * 40,
            ""
        ])

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Total: {len(filtered_posts)} post(s)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ])

    return "\n".join(lines)


def format_results(results: list[PublishResult]) -> str:
    """Format publish results for display."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "BUFFER PUBLISH RESULTS",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    for result in results:
        status = "✓" if result.success else "✗"
        error_msg = f" — {result.error}" if result.error else ""
        lines.append(f"{status} {result.post.day} — {result.post.title}{error_msg}")

    lines.extend([
        "",
        f"Sent: {len(successes)} / {len(results)}",
    ])

    if failures:
        lines.append(f"Failed: {len(failures)}")

    if successes:
        lines.extend([
            "",
            "Next steps:",
            "1. Open Buffer → Drafts",
            "2. Add images to each post",
            "3. Schedule posting times",
            "4. Publish",
            "",
            "Buffer Drafts: https://publish.buffer.com/drafts"
        ])

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ])

    return "\n".join(lines)


def publish_posts(
    posts: list[SocialPost],
    backend: PublisherBackend,
    day_filter: Optional[str] = None,
    skip_monday: bool = True
) -> list[PublishResult]:
    """Publish posts using the specified backend."""
    results = []

    for post in posts:
        # Filter by day if specified
        if day_filter and post.day.lower() != day_filter.lower():
            continue

        # Skip Monday flagship by default (too long for LinkedIn)
        if skip_monday and post.day.lower() == "monday":
            continue

        result = backend.publish_draft(post)
        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Publish flagship content to Buffer (social) and Notion (long-form)"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to flagship markdown file (auto-detects latest if not specified)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview posts without publishing"
    )
    parser.add_argument(
        "--day", "-d",
        help="Publish only a specific day (e.g., 'tuesday')"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Test parsing only (no publishing)"
    )
    parser.add_argument(
        "--include-monday",
        action="store_true",
        help="Include Monday flagship post (usually too long for LinkedIn)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--notion",
        action="store_true",
        help="Publish Monday long-form article to Notion (for Substack editing)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Publish both social posts to Buffer AND long-form to Notion"
    )

    args = parser.parse_args()

    # Find file
    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return 1
    else:
        filepath = find_latest_flagship()
        if not filepath:
            print(f"Error: No pub-flagship-*.md files found in {CONTENT_DIR}", file=sys.stderr)
            return 1

    print(f"Reading: {filepath}")

    # Parse
    posts = parse_flagship_markdown(filepath)
    if not posts:
        print("Error: No posts found in file", file=sys.stderr)
        return 1

    # Test mode: just show parsed content
    if args.test:
        print(format_preview(posts, args.day))
        return 0

    # Dry run mode
    if args.dry_run:
        # Show social posts preview
        if not args.notion:
            print(format_preview(posts, args.day))

            skip_monday = not args.include_monday
            to_publish = [
                p for p in posts
                if (not args.day or p.day.lower() == args.day.lower())
                and (not skip_monday or p.day.lower() != "monday")
            ]

            print(f"\nWould publish {len(to_publish)} post(s) to Buffer.")
            if not args.include_monday and any(p.day.lower() == "monday" for p in posts):
                print("(Monday flagship excluded by default. Use --include-monday to include.)")

        # Show Notion preview
        if args.notion or args.all:
            article = parse_monday_article(filepath)
            if article:
                print("\n" + format_notion_preview(article))
                print("\nWould publish to Notion database.")
            else:
                print("\nNo Monday article found for Notion.")

        return 0

    # Handle --notion only (no Buffer)
    if args.notion and not args.all:
        notion_key = os.environ.get("NOTION_API_KEY")
        notion_db = os.environ.get("NOTION_DATABASE_ID")

        if not notion_key or not notion_db:
            print("Error: Missing Notion environment variables.", file=sys.stderr)
            print("Required: NOTION_API_KEY, NOTION_DATABASE_ID", file=sys.stderr)
            return 1

        article = parse_monday_article(filepath)
        if not article:
            print("Error: No Monday article found in file", file=sys.stderr)
            return 1

        publisher = NotionPublisher(notion_key, notion_db)

        # Test connection
        connected, message = publisher.test_connection()
        if not connected:
            print(f"Error: Could not connect to Notion: {message}", file=sys.stderr)
            return 1

        print(f"Publishing to Notion: {article.title}")
        result = publisher.publish_article(article)

        if args.json:
            output = {
                "file": str(filepath),
                "notion": {
                    "title": article.title,
                    "success": result.success,
                    "page_url": result.page_url,
                    "error": result.error
                }
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_notion_result(result, article))

        return 0 if result.success else 1

    # Real publishing: need Zapier credentials
    webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")
    profile_id = os.environ.get("BUFFER_PROFILE_ID")

    if not webhook_url or not profile_id:
        print("Error: Missing environment variables.", file=sys.stderr)
        print("Required: ZAPIER_WEBHOOK_URL, BUFFER_PROFILE_ID", file=sys.stderr)
        print("Export these variables in your shell before running this command.", file=sys.stderr)
        return 1

    # Initialize backend
    backend = ZapierBackend(webhook_url, profile_id)

    # Test connection
    connected, message = backend.test_connection()
    if not connected:
        print(f"Error: Could not connect to Zapier: {message}", file=sys.stderr)
        return 1

    # Publish
    skip_monday = not args.include_monday
    results = publish_posts(posts, backend, args.day, skip_monday)

    buffer_success = all(r.success for r in results)

    if args.json:
        output = {
            "file": str(filepath),
            "buffer_results": [
                {
                    "day": r.post.day,
                    "title": r.post.title,
                    "success": r.success,
                    "error": r.error,
                    "buffer_id": r.buffer_id
                }
                for r in results
            ]
        }
    else:
        print(format_results(results))

    # Handle --all: also publish to Notion
    notion_success = True
    if args.all:
        notion_key = os.environ.get("NOTION_API_KEY")
        notion_db = os.environ.get("NOTION_DATABASE_ID")

        if not notion_key or not notion_db:
            print("\nWarning: Skipping Notion - missing NOTION_API_KEY or NOTION_DATABASE_ID", file=sys.stderr)
            notion_success = False
        else:
            article = parse_monday_article(filepath)
            if not article:
                print("\nWarning: No Monday article found for Notion", file=sys.stderr)
                notion_success = False
            else:
                publisher = NotionPublisher(notion_key, notion_db)
                connected, message = publisher.test_connection()

                if not connected:
                    print(f"\nWarning: Could not connect to Notion: {message}", file=sys.stderr)
                    notion_success = False
                else:
                    print(f"\nPublishing to Notion: {article.title}")
                    notion_result = publisher.publish_article(article)

                    if args.json:
                        output["notion"] = {
                            "title": article.title,
                            "success": notion_result.success,
                            "page_url": notion_result.page_url,
                            "error": notion_result.error
                        }
                    else:
                        print(format_notion_result(notion_result, article))

                    notion_success = notion_result.success

    if args.json:
        print(json.dumps(output, indent=2))

    # Return non-zero if any failures
    return 0 if (buffer_success and notion_success) else 1


if __name__ == "__main__":
    sys.exit(main())
