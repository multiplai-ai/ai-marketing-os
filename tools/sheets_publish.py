#!/usr/bin/env python3
"""
Google Sheets Publish Tool
--------------------------
Publish markdown tables to Google Sheets, preserving all columns.

Usage:
    python3 tools/sheets_publish.py path/to/file.md           # Publish all tables
    python3 tools/sheets_publish.py path/to/file.md --dry-run # Preview only
    python3 tools/sheets_publish.py path/to/file.md --sheet-name "My Sheet"
    python3 tools/sheets_publish.py --test                    # Test connection

Environment variables (export explicitly):
    GOOGLE_SERVICE_ACCOUNT_PATH  - Path to service account JSON file
    GOOGLE_SHEETS_ID             - Target spreadsheet ID
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



@dataclass
class Table:
    """Represents a parsed markdown table."""
    name: str
    headers: list[str]
    rows: list[list[str]]


@dataclass
class PublishResult:
    """Result of publishing to Google Sheets."""
    success: bool
    sheet_url: Optional[str] = None
    worksheet_name: Optional[str] = None
    rows_written: int = 0
    error: Optional[str] = None


def parse_markdown_tables(content: str) -> list[Table]:
    """
    Parse all markdown tables from content.

    Returns list of Table objects with name (from preceding heading), headers, and rows.
    """
    tables = []
    lines = content.split('\n')

    current_heading = "Table"
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Track headings for table names
        if line.startswith('#'):
            # Extract heading text (remove # symbols)
            heading_text = re.sub(r'^#+\s*', '', line)
            if heading_text:
                current_heading = heading_text

        # Detect table start (line starting with |)
        if line.startswith('|') and '|' in line[1:]:
            table_lines = [line]
            i += 1

            # Collect all table lines
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1

            # Parse the table
            if len(table_lines) >= 2:  # Need at least header + separator
                table = parse_single_table(table_lines, current_heading)
                if table:
                    tables.append(table)

            continue

        i += 1

    return tables


def parse_single_table(lines: list[str], name: str) -> Optional[Table]:
    """Parse a single markdown table from its lines."""
    if len(lines) < 2:
        return None

    # Parse header row
    header_line = lines[0]
    headers = [cell.strip() for cell in header_line.split('|')[1:-1]]

    # Skip separator line (second line with dashes)
    # Verify it's a separator
    if len(lines) < 2 or not re.match(r'^[\|\s\-:]+$', lines[1]):
        return None

    # Parse data rows (starting from line 2)
    rows = []
    for line in lines[2:]:
        if line.strip():
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            # Pad or trim to match header count
            while len(cells) < len(headers):
                cells.append('')
            cells = cells[:len(headers)]
            rows.append(cells)

    return Table(name=name, headers=headers, rows=rows)


def extract_title(content: str, filepath: Path) -> str:
    """Extract title from H1 header or fallback to filename."""
    title_match = re.search(r'^# (.+?)$', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return filepath.stem.replace('-', ' ').replace('_', ' ').title()


class SheetsPublisher:
    """Publish markdown tables to Google Sheets."""

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, service_account_path: str, spreadsheet_id: str):
        self.service_account_path = Path(service_account_path).expanduser()
        self.spreadsheet_id = spreadsheet_id
        self._client = None

    def _get_client(self) -> 'gspread.Client':
        """Get or create authenticated gspread client."""
        if self._client is None:
            if gspread is None or Credentials is None:
                raise RuntimeError("gspread library not installed. Run: pip install gspread google-auth")

            creds = Credentials.from_service_account_file(
                str(self.service_account_path),
                scopes=self.SCOPES
            )
            self._client = gspread.authorize(creds)
        return self._client

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Google Sheets API."""
        if gspread is None:
            return False, "gspread library not installed. Run: pip install gspread google-auth"

        if not self.service_account_path.exists():
            return False, f"Service account file not found: {self.service_account_path}"

        try:
            client = self._get_client()
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            return True, f"Connected to: {spreadsheet.title}"
        except gspread.exceptions.SpreadsheetNotFound:
            return False, f"Spreadsheet not found. Make sure the service account has access to spreadsheet ID: {self.spreadsheet_id}"
        except gspread.exceptions.APIError as e:
            return False, f"API Error: {e}"
        except Exception as e:
            return False, str(e)

    def publish(
        self,
        filepath: Path,
        sheet_name: Optional[str] = None,
        dry_run: bool = False
    ) -> PublishResult:
        """Publish markdown tables to Google Sheets."""
        if gspread is None:
            return PublishResult(success=False, error="gspread library not installed")

        # Read file
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            return PublishResult(success=False, error=f"Could not read file: {e}")

        # Parse tables
        tables = parse_markdown_tables(content)
        if not tables:
            return PublishResult(success=False, error="No markdown tables found in file")

        # Use first table if multiple, or combine based on sheet_name
        if sheet_name:
            worksheet_name = sheet_name
            # Combine all tables into one
            all_rows = []
            headers = None
            for table in tables:
                if headers is None:
                    headers = table.headers
                    all_rows.append(headers)
                all_rows.extend(table.rows)
        else:
            # Use first table
            table = tables[0]
            worksheet_name = table.name
            headers = table.headers
            all_rows = [headers] + table.rows

        if dry_run:
            return PublishResult(
                success=True,
                sheet_url=f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}",
                worksheet_name=worksheet_name,
                rows_written=len(all_rows)
            )

        try:
            client = self._get_client()
            spreadsheet = client.open_by_key(self.spreadsheet_id)

            # Try to get or create worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                # Clear existing content
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=len(all_rows) + 10,
                    cols=len(headers) + 2
                )

            # Write data
            worksheet.update(all_rows, value_input_option='USER_ENTERED')

            # Format header row (bold)
            worksheet.format('1', {'textFormat': {'bold': True}})

            sheet_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit#gid={worksheet.id}"

            return PublishResult(
                success=True,
                sheet_url=sheet_url,
                worksheet_name=worksheet_name,
                rows_written=len(all_rows)
            )

        except gspread.exceptions.APIError as e:
            return PublishResult(success=False, error=f"API Error: {e}")
        except Exception as e:
            return PublishResult(success=False, error=str(e))


def format_output(
    result: PublishResult,
    filepath: Path,
    tables: list[Table],
    dry_run: bool = False
) -> str:
    """Format the output for display."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "GOOGLE SHEETS PUBLISH" + (" (DRY RUN)" if dry_run else ""),
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"File: {filepath}",
        f"Tables found: {len(tables)}",
    ]

    if tables:
        for i, table in enumerate(tables, 1):
            lines.append(f"  {i}. {table.name}: {len(table.headers)} columns, {len(table.rows)} rows")

    lines.append("")

    if result.success:
        lines.extend([
            "✓ Published successfully",
            "",
            f"Worksheet: {result.worksheet_name}",
            f"Rows written: {result.rows_written}",
            "",
            f"Sheet URL: {result.sheet_url}",
        ])
    else:
        lines.extend([
            "✗ Failed to publish",
            f"Error: {result.error}",
        ])

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def format_dry_run_preview(tables: list[Table]) -> str:
    """Format detailed preview of tables for dry run."""
    lines = [
        "",
        "TABLE PREVIEW",
        "─────────────",
    ]

    for table in tables:
        lines.append(f"\n{table.name}")
        lines.append("─" * len(table.name))

        # Show headers
        header_str = " | ".join(table.headers)
        lines.append(f"Headers: {header_str}")

        # Show first few rows
        lines.append(f"Rows: {len(table.rows)}")
        for row in table.rows[:3]:
            row_str = " | ".join(cell[:30] + "..." if len(cell) > 30 else cell for cell in row)
            lines.append(f"  → {row_str}")
        if len(table.rows) > 3:
            lines.append(f"  ... and {len(table.rows) - 3} more rows")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Publish markdown tables to Google Sheets"
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
        "--sheet-name", "-s",
        help="Override the worksheet name (default: from table heading)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Google Sheets connection only"
    )

    args = parser.parse_args()

    # Get credentials
    service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH", "~/.config/google-service-account.json")
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_ID")

    def check_credentials():
        """Check if credentials are configured."""
        if not spreadsheet_id or spreadsheet_id == "your-spreadsheet-id-here":
            print("Error: Missing Google Sheets configuration.", file=sys.stderr)
            print("Required environment variables: GOOGLE_SERVICE_ACCOUNT_PATH, GOOGLE_SHEETS_ID", file=sys.stderr)
            print("Export these variables in your shell before running this command.", file=sys.stderr)
            return False
        return True

    # Test mode - requires credentials
    if args.test:
        if not check_credentials():
            return 1
        publisher = SheetsPublisher(service_account_path, spreadsheet_id)
        connected, message = publisher.test_connection()
        if connected:
            print(f"✓ {message}")
            return 0
        else:
            print(f"✗ Connection failed: {message}", file=sys.stderr)
            return 1

    # Require file for publishing/preview
    if not args.file:
        parser.print_help()
        return 1

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    # Parse tables first (for preview and publishing)
    content = filepath.read_text(encoding="utf-8")
    tables = parse_markdown_tables(content)

    if not tables:
        print("Error: No markdown tables found in file", file=sys.stderr)
        return 1

    # Dry run - just preview tables, no credentials needed
    if args.dry_run:
        worksheet_name = args.sheet_name if args.sheet_name else tables[0].name
        total_rows = sum(len(t.rows) for t in tables) + 1  # +1 for header
        result = PublishResult(
            success=True,
            sheet_url="<will be generated on publish>",
            worksheet_name=worksheet_name,
            rows_written=total_rows
        )
        print(format_output(result, filepath, tables, dry_run=True))
        print(format_dry_run_preview(tables))
        return 0

    # Real publish - requires credentials
    if not check_credentials():
        return 1

    publisher = SheetsPublisher(service_account_path, spreadsheet_id)
    connected, message = publisher.test_connection()
    if not connected:
        print(f"Error: Could not connect to Google Sheets: {message}", file=sys.stderr)
        return 1

    # Publish
    result = publisher.publish(filepath, args.sheet_name, dry_run=False)

    print(format_output(result, filepath, tables, dry_run=False))

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
