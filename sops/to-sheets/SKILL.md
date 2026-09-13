---
name: to-sheets
description: Publish markdown tables to Google Sheets while preserving columns.
---

# Google Sheets Publishing Runbook

Publish markdown tables to Google Sheets while preserving columns.

## Tool

- `tools/sheets_publish.py`

## Workflow

1. Confirm the markdown file and target worksheet name.
2. Preview table extraction:

```bash
python3 tools/sheets_publish.py <file.md> --dry-run
```

3. Publish:

```bash
python3 tools/sheets_publish.py <file.md>
```

4. Return the Sheet URL and worksheet name.

## Useful Options

```bash
python3 tools/sheets_publish.py <file.md> --sheet-name "Q1 Data"
python3 tools/sheets_publish.py --test
```

## Required Environment

```bash
GOOGLE_SERVICE_ACCOUNT_PATH=
GOOGLE_SHEETS_ID=
```

## Use Sheets Instead Of Notion When

- The document has wide tables.
- The user needs filtering, formulas, sorting, or data QA.
- The table has more columns than Notion is comfortable reviewing.
