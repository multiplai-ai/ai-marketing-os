#!/usr/bin/env python3
"""
Notion Publish Tool
-------------------
Publish any markdown file to Notion database for collaboration and commenting.

Usage:
    python3 tools/notion_publish.py path/to/file.md           # Publish file
    python3 tools/notion_publish.py path/to/file.md --dry-run # Preview only
    python3 tools/notion_publish.py path/to/file.md --title "Custom Title"
    python3 tools/notion_publish.py --test                    # Test connection

Environment variables (export explicitly):
    NOTION_API_KEY      - Notion integration API key
    NOTION_DATABASE_ID  - Target database ID
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



@dataclass
class PublishResult:
    """Result of publishing to Notion."""
    success: bool
    page_url: Optional[str] = None
    page_id: Optional[str] = None
    error: Optional[str] = None


def parse_formatting(text: str) -> list[dict]:
    """Parse bold/italic formatting in text."""
    result = []

    # Handle **bold**
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
        # Numbered list
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": parse_rich_text(text.strip())
                }
            })
        # Horizontal rule
        elif line.strip() == '---':
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        # Code block
        elif line.strip().startswith('```'):
            code_lines = []
            language = line.strip()[3:] or "plain text"
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_lines)}}],
                    "language": language if language != "plain text" else "plain text"
                }
            })
        # Blockquote
        elif line.startswith('> '):
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": parse_rich_text(line[2:].strip())
                }
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
                    not re.match(r'^\d+\.\s', next_line) and
                    not next_line.startswith('> ') and
                    not next_line.strip().startswith('```') and
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


def extract_title(content: str, filepath: Path) -> str:
    """Extract title from H1 header or fallback to filename."""
    # Look for first H1 heading
    title_match = re.search(r'^# (.+?)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()

    # Fallback to filename (without extension)
    return filepath.stem.replace('-', ' ').replace('_', ' ').title()


class NotionPublisher:
    """Publish markdown files to Notion database."""

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
            return False, "requests library not installed. Run: pip install requests"

        try:
            response = requests.get(
                f"{self.NOTION_API_URL}/databases/{self.database_id}",
                headers=self.headers,
                timeout=10
            )
            if response.ok:
                db_data = response.json()
                title = db_data.get('title', [{}])
                db_name = title[0].get('plain_text', 'Database') if title else 'Database'
                return True, f"Connected to: {db_name}"
            else:
                error_msg = response.json().get('message', response.text[:100])
                return False, f"HTTP {response.status_code}: {error_msg}"
        except Exception as e:
            return False, str(e)

    def publish(self, filepath: Path, title: Optional[str] = None, dry_run: bool = False) -> PublishResult:
        """Publish markdown file to Notion database."""
        if requests is None:
            return PublishResult(success=False, error="requests library not installed")

        # Read file
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            return PublishResult(success=False, error=f"Could not read file: {e}")

        # Extract or use provided title
        page_title = title if title else extract_title(content, filepath)

        if dry_run:
            return PublishResult(
                success=True,
                page_url="https://notion.so/dry-run-preview",
                page_id="dry-run-id"
            )

        # Convert content to Notion blocks
        content_blocks = markdown_to_notion_blocks(content)

        # Notion API limits children to 100 blocks per request
        initial_blocks = content_blocks[:100]
        remaining_blocks = content_blocks[100:]

        page_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {"content": page_title}
                        }
                    ]
                }
            },
            "children": initial_blocks
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
                return PublishResult(success=False, error=f"HTTP {response.status_code}: {error_msg}")

            page_result = response.json()
            page_id = page_result["id"]
            page_url = page_result.get("url", f"https://notion.so/{page_id.replace('-', '')}")

            # Append remaining blocks if any (in chunks of 100)
            for i in range(0, len(remaining_blocks), 100):
                chunk = remaining_blocks[i:i+100]
                append_response = requests.patch(
                    f"{self.NOTION_API_URL}/blocks/{page_id}/children",
                    headers=self.headers,
                    json={"children": chunk},
                    timeout=30
                )
                if not append_response.ok:
                    print(f"Warning: Could not append all content blocks", file=sys.stderr)
                    break

            return PublishResult(
                success=True,
                page_url=page_url,
                page_id=page_id
            )

        except requests.exceptions.Timeout:
            return PublishResult(success=False, error="Request timed out")
        except requests.exceptions.RequestException as e:
            return PublishResult(success=False, error=str(e))


def format_output(result: PublishResult, filepath: Path, title: str, dry_run: bool = False) -> str:
    """Format the output for display."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "NOTION PUBLISH" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"File: {filepath}",
        f"Title: {title}",
        ""
    ]

    if result.success:
        lines.extend([
            "✓ Published successfully",
            "",
            f"Page URL: {result.page_url}",
        ])
    else:
        lines.extend([
            "✗ Failed to publish",
            f"Error: {result.error}",
        ])

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Publish any markdown file to Notion database"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to markdown file to publish"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview without publishing"
    )
    parser.add_argument(
        "--title", "-t",
        help="Override the page title (default: extracted from H1 or filename)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Notion connection only"
    )

    args = parser.parse_args()

    # Get credentials
    api_key = os.environ.get("NOTION_API_KEY")
    database_id = os.environ.get("NOTION_DATABASE_ID")

    if not api_key or not database_id:
        print("Error: Missing Notion credentials.", file=sys.stderr)
        print("Required environment variables: NOTION_API_KEY, NOTION_DATABASE_ID", file=sys.stderr)
        print("Export these variables in your shell before running this command.", file=sys.stderr)
        return 1

    publisher = NotionPublisher(api_key, database_id)

    # Test mode
    if args.test:
        connected, message = publisher.test_connection()
        if connected:
            print(f"✓ {message}")
            return 0
        else:
            print(f"✗ Connection failed: {message}", file=sys.stderr)
            return 1

    # Require file for publishing
    if not args.file:
        parser.print_help()
        return 1

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    # Test connection first
    connected, message = publisher.test_connection()
    if not connected:
        print(f"Error: Could not connect to Notion: {message}", file=sys.stderr)
        return 1

    # Read file to get title for preview
    content = filepath.read_text(encoding="utf-8")
    title = args.title if args.title else extract_title(content, filepath)

    # Publish
    result = publisher.publish(filepath, args.title, dry_run=args.dry_run)

    print(format_output(result, filepath, title, dry_run=args.dry_run))

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
