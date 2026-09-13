---
name: to-notion
description: Publish a markdown file to a Notion database for collaboration and comments.
---

# Notion Publishing Runbook

Publish a markdown file to a Notion database for collaboration and comments.

## Tool

- `tools/notion_publish.py`

## Workflow

1. Confirm the markdown file and title.
2. Preview if helpful:

```bash
python3 tools/notion_publish.py <file.md> --dry-run
```

3. Publish:

```bash
python3 tools/notion_publish.py <file.md>
```

4. Return the Notion page URL.

## Useful Options

```bash
python3 tools/notion_publish.py <file.md> --title "Custom Title"
python3 tools/notion_publish.py --test
```

## Required Environment

```bash
NOTION_API_KEY=
NOTION_DATABASE_ID=
```

## Guardrails

- Use Notion for prose review and comments.
- Use Google Sheets instead when wide tables, formulas, filtering, or sorting are the real need.
- Do not claim a page was created unless the tool returns a page URL.
