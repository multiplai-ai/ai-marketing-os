---
name: monthly-scorecard
description: Produce the question-grouped, traffic-light monthly scorecard for the recurring monthly review meeting. Sitewide by default; per-specialty available on request.
---

# entity Monthly Scorecard Runbook

Produce the question-grouped, traffic-light monthly scorecard for the recurring monthly review meeting. Sitewide by default; per-specialty available on request.

## Output artifact

A single `.xlsx` saved next to the source data with this naming pattern:

```text
{source-folder}/{YYYY-MM}-mtd-scorecard-{scope}.xlsx
```

Example: `April 1 to 30 2026 (final)/OUTPUT 2026-04-30/2026-04-mtd-scorecard-oncology.xlsx`

The file mirrors the executive slide-table layout:

- top red placeholder: `[Key diagnostic takeaway]`
- dark navy header band
- gray merged diagnostic/question groups on the left
- metric label, plain-language detail, metric-trend comparison, and colored status dot columns
- compact source/footer row

## When to use

- Monthly review meeting prep (recurring)
- User says "build the monthly scorecard," "make the April scorecard," "run the monthly meeting view"
- New monthly Tableau export has landed in `brains/entity/analysis/analysis-tableau-exports/`

## Required inputs

1. **Workbook:** `weekly-report-{YYYY-MM-DD}.xlsx` from the monthly Tableau export folder
2. **Scope:** `Sitewide` (default) or one of `Oncology | Gastro | Neuro | Derm | Psychiatry`
3. The workbook must contain the corresponding `V1 Scorecard - {Scope}` tab in the format produced by the standard weekly-report generator (MTD column at index 4, Goal at 6, vs Goal at 7, P3MA at 8, vs P3MA at 9, PY at 11, vs PY at 12).

## Section structure (do not change without asking)

The report has six question-grouped sections. Each section's metrics map to specific rows in `V1 Scorecard - {Scope}`. Keep this ordering so the output matches the monthly review slide format:

| Section question | Metric label | Source row in V1 Scorecard | Description format |
|---|---|---|---|
| Are minutes on track, overall; or does something look off? | MINUTES | `Total Minutes` | "Minutes {missed/beat} goal by X% ({actual} vs {goal} goal)" |
| | MINUTES/MANPI | `Mins/User (MANPI)` | "Average of {value} minutes per MANPI ({+/-X% vs goal} vs {goal} goal)" |
| Are MANPI on track? | MANPI | `Monthly Active (MANPI)` | "MANPI {missed/beat} goal by X% ({actual} vs {goal} goal)" |
| Is something wrong with email delivery? | SEND VOLUME | `Total Email Sends` | "Email average daily send volume {increased/decreased/was ~flat} to {MTD / days_elapsed}" |
| | EMAIL MINUTES | `Email Minutes` | "Email minutes {increased/decreased/were ~flat} to {value}" |
| | CONTENT | (not in V1; placeholder) | "Content volume not in this scorecard" or value if user provides |
| Is something wrong with content or curation? | CURATION | `Starts/Send (Email)` | "Email start rate {increased/decreased/was ~flat} by ~X%, to {value}%" |
| | QUALITY | (placeholder) | "N/A; Metric expected in {next month}" |
| Is there something wrong with Whitelist delivery? | SEND VOLUME | `WL Sends` | "WL email sends {increased/decreased/was ~flat} X% to {value}" |
| | WL CONVERSION | `WL Conversions` | "WL conversions {increased/decreased/was ~flat} to {value}" |
| Is there something wrong with site delivery pathways? | NON-EMAIL MINUTES | `Non-Email Minutes` | "Non-email minutes {increased/decreased/were ~flat} vs P3MA, at {value}" |

The metric-trend column always reads `(+/-X% P3MA; +/-Y% YoY)` using the `vs P3MA` and `vs PY` columns. Round to whole percent.

## Status dot rules

- **Green** - both period comparisons positive AND (if a goal exists) at-or-above goal.
- **Yellow** - mixed: one direction up, the other flat or down; or essentially flat (+/-2% on both).
- **Red** - missed goal by >5%, OR both period comparisons negative, OR a single comparison worse than -10%.
- For metrics with no clear goal (e.g., NON-EMAIL MINUTES, EMAIL MINUTES), grade on P3MA + PY only.

These are heuristics. Sanity-check edge cases, such as a metric with a huge YoY lift because the prior-year base was near zero; treat that as program-launch context and grade green only if P3MA is also healthy.

## Workflow

### Step 1 - Confirm scope and source file

- Ask the user the **scope** (Sitewide vs specialty) if not specified. Default to Sitewide.
- Confirm the source workbook path. If multiple workbooks exist in the monthly export folder, use the most recent.

### Step 2 - Run the deterministic builder

Use the deterministic builder script in `tools/`:

```bash
python3 {entity_tool:build_monthly_scorecard} \
  --source "brains/entity/analysis/analysis-tableau-exports/{MM-mon-YYYY}/{export-folder}/OUTPUT {YYYY-MM-DD}/weekly-report-{YYYY-MM-DD}.xlsx" \
  --scope Oncology
```

The script loads the workbook with `openpyxl` and reads `V1 Scorecard - {Scope}` with `data_only=True`. It pulls the rows listed in the table above and reads the Summary tab for `Data Through`, `Month`, and `Days Elapsed`.

### Step 3 - Compute derived values

The script computes:

- **Daily avg email send volume** = `Total Email Sends MTD / Days Elapsed`
- **vs Goal phrasing**: if `vs Goal` is negative, use "missed goal by {abs}%"; if positive, use "beat goal by {abs}%"
- rounded percent comparisons in whole integers
- large absolute counts in compact slide notation (`K`, `MM`)

### Step 4 - Apply status dot rules

Per the rules above. When in doubt between yellow and red, default to red because the meeting is meant to surface concerns.

### Step 5 - Build the workbook

The deterministic builder renders the slide-style table:

- row 1: `[Key diagnostic takeaway]` placeholder
- row 2: dark navy header band with `Diagnostic`, `Metric Trend`, and `vs Goal`
- column A: gray merged diagnostic/question groups
- column B: metric label
- column C: plain-language metric detail
- column D: metric trend
- column E: colored status dot character `●`
- footer row: `Source: {Scope} MTD Engagement Report, {month range}`

### Step 6 - Save and confirm

Save to `{source-folder}/{YYYY-MM}-mtd-scorecard-{scope}.xlsx` (lowercase scope). Open or render-preview it when practical. Reply with a compact text summary of the same data so the user can read it without opening the file.

## Interpretive guidance

- This is a **Bucket A (health & trend) view** per owner's reporting framework - directional, not for diagnostics. Do not overload it with detail.
- The CONTENT and QUALITY rows are intentional placeholders; if the user wants those wired up, they need a content production data source outside the standard weekly report.
- If the source workbook is from a partial month (Days Elapsed < days in month), the footer should still say MTD and use the actual through-date, e.g. `Apr 1-26, 2026`.
- Specialty-level scopes use the same template; goals and target ranges differ but the structure is identical.

## Data quality checks

- If `vs P3MA` or `vs PY` is blank for a row, render the comparison as `(n/a P3MA; +/-X% YoY)`; do not fabricate.
- If a goal is blank, drop the "vs Goal" phrasing and use "{value} {metric}" instead.
- WL year-over-year deltas can be astronomical because the program launched mid-prior-year. When the YoY base is <100K, append a footnote to the chat summary explaining the small base.

## Output format

- Excel file (artifact) saved alongside source data.
- Chat summary: compact markdown table with section / metric / value / comparison / status, plus 1-2 lines flagging anything notable (small bases, missing data, partial month).

**Do NOT:**

- Add new sections without asking; the meeting expects this exact structure.
- Change the diagnostic question wording; the section headers are calibrated to the meeting agenda and slide format.
- Output the table as a chat-only response without producing the `.xlsx` file.

## Change log

- **v1.1** (2026-05-11) - Standardized the screenshot-matched slide-table format and added `{entity_tool:build_monthly_scorecard}` as the deterministic builder for future runs.
- **v1.0** (2026-04-28) - Initial version. Sitewide default; six-section question structure mirroring April 2026 monthly meeting template.
