---
name: engagement-report
description: Generate deterministic entity engagement reports from Tableau exports.
---

# Engagement Report Runbook

Generate deterministic entity engagement reports from Tableau exports.

## Tools

- Monthly report: `{entity_tool:generate_daily_report}`
- Weekly report: `{entity_tool:generate_weekly_report}`

## Required Intake

Before running tools, confirm:

- Report type: monthly, MTD/pacing, or weekly.
- Target period.
- Data folder path.
- Weekly scopes if different from the default Sitewide + Oncology.

If the stated period conflicts with dates inferred from exports, stop and flag the mismatch.

## Monthly Report

```bash
python3 {entity_tool:generate_daily_report} --data-dir "<export-folder>"
```

Expected output:

- `OUTPUT {YYYY-MM-DD}/daily-report-{YYYY-MM-DD}.xlsx`
- 18 tabs: `Summary`, all registered views for two scopes, and `Raw Data`

## Weekly Report

```bash
python3 {entity_tool:generate_weekly_report} --data-dir "<export-folder>"
```

Optional site-level scopes can be added to the standard Sitewide + Oncology run:

```bash
python3 {entity_tool:generate_weekly_report} --data-dir "<export-folder>" --site-scopes "gastro,neuro,derm,psychiatry"
```

Expected output:

- `OUTPUT {YYYY-MM-DD}/weekly-report-{YYYY-MM-DD}.xlsx`
- 19 tabs: `Summary`, all registered views for two scopes, `L1 Outlier Analysis`, and `Raw Data`
- Custom site-scope runs add 8 tabs per added scope.

To generate the local Confluence-ready Markdown file from the workbook:

```bash
python3 {entity_tool:generate_confluence_report} --xlsx "<path-to-weekly-report.xlsx>"
```

To publish that Markdown to Confluence and attach the Excel workbook:

```bash
python3 {entity_tool:publish_confluence_report} \
  --md "<path-to-weekly-report-confluence.md>" \
  --attach "<path-to-weekly-report.xlsx>" \
  --space-key "<space-key>" \
  --parent-id "<parent-page-id>"
```

Required Confluence env vars:

- `CONFLUENCE_BASE_URL` (example: `https://entity.atlassian.net/wiki`)
- `CONFLUENCE_EMAIL`
- `CONFLUENCE_API_TOKEN`

Optional defaults:

- `CONFLUENCE_SPACE_KEY`
- `CONFLUENCE_PARENT_PAGE_ID`

Publishing behavior:

- If `--page-id` is provided, update that page.
- If `--page-id` is omitted, upsert by page title within the target space.
- Use `--dry-run` before first publish to confirm title, space, parent, and attachment path.

## Required Input Files

- `Activity Metrics.xlsx` or `Activity Metrics.csv`
- `Email Metrics.xlsx` or `Email Metrics.csv`
- `Xanpi Metrics.xlsx`, `Xanpi Metrics .xlsx`, `Xanpi Metrics.csv`, or legacy `Xanpi Metrics .csv`

## Guardrails

- Do not recreate report logic in an ad hoc script.
- Do not silently accept renamed browser downloads such as `(1)` copies.
- Do not compare partial weeks to complete weeks on absolute KPIs.
- Weekly report is for momentum signal; monthly report is for attainment.
