---
name: scrape-website
description: Scrape articles from an index page into markdown files for research or read-later workflows.
---

# Website Scraping Runbook

Scrape articles from an index page into markdown files for research or read-later workflows.

## Tool

- `tools/web_scraper.py`

## Prerequisites

- Python 3.10+
- Playwright browser installed
- `trafilatura`

## Basic Usage

```bash
python3 tools/web_scraper.py "<index-url>" "<output-dir>"
```

## Useful Options

```bash
python3 tools/web_scraper.py "<url>" "Library/Site/" --limit 3
python3 tools/web_scraper.py "<url>" "Library/Site/" --substack
python3 tools/web_scraper.py "<url>" "Library/Site/" --link-selector "article a.title"
python3 tools/web_scraper.py "<url>" "Library/Site/" --delay 3
python3 tools/web_scraper.py "<url>" "Library/Site/" --no-skip-existing
```

## Output

Markdown files with frontmatter:

```markdown
---
source:
scraped:
title:
author:
date:
---
```

## Guardrails

- The scraper only captures content visible without authentication.
- Increase delay if rate-limited.
- If no article links are found, inspect the page and supply a custom CSS selector.
