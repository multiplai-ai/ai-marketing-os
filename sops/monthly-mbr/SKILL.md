---
name: monthly-mbr
description: Prepare a monthly business review package from consumer-provided metrics, reports, and executive priorities.
---

# Monthly MBR Runbook

Prepare the consumer's monthly business review package. Resolve the executive
recipient, reporting scope, goals, input/output locations and all `{entity_tool:...}`
paths from its configuration. The analytics schema below is a conditional
engagement-report pattern, not a claim about the consumer's business. Use it only
when its metric and export contract matches. Private templates and generators
are not bundled with Core; verify them before running.

## What this produces

Four artifacts, each with a distinct audience:

| Artifact | Audience | Purpose |
|---|---|---|
| `weekly-report-YYYY-MM-DD.xlsx` (19 tabs) | Operators, analysts | Source of truth — Sitewide + scope-level + raw data |
| `YYYY-MM-sitewide-health-check.xlsx` | owner, exec team | Slide-style scorecard for the meeting |
| `MANPI and MINUTES Monthly Tracker - {Month YYYY}.xlsx` | Category Leads | Per-site actuals vs goals + comparisons |
| `YYYY-MM-MBR-narrative.pptx` (2 slides) | **the configured executive recipient** | What happened + why + actions |

The pptx is what the executive recipient sees. The other three are supporting context.

## Cadence

Run after the full-month Tableau export lands (typically a few business days after month-end). The standard cadence is:
- Day 1–3 of new month: full-month export from Tableau
- Day 4: build pipeline, refine narrative
- Day 5–7: monthly review meeting with the executive recipient

## Pipeline overview

```
CSV folder (3 Tableau exports)
        │
        ▼
  generate_weekly_report.py    → weekly-report-{date}.xlsx (19 tabs)
        │
        ├── entity_build_health_check.py     → health-check.xlsx
        │
        ├── entity_build_monthly_tracker.py  → tracker.xlsx
        │       (uses site-level-goals.json)
        │
        └── entity_build_mbr_narrative.py    → MBR-narrative.pptx
                (reads from report + tracker)
```

The orchestrator (`{entity_tool:run_monthly_mbr}`) runs all four in sequence and archives outputs.

## Required inputs

### Data exports from Tableau
Three files in a single folder, as **either `.csv` (UTF-16 TSV) or `.xlsx`** — the tracker loader takes whichever is present:
- `Activity Metrics`
- `Email Metrics`
- `Xanpi Metrics ` (trailing space in name)

The exports typically contain monthly aggregates for ~17 prior months plus a partial-month current-period row. **For final-month reporting**, filter out partial-month rows so the generator's "Days Elapsed" reads as the full month (e.g., 30/30 for April).

**Block-merged dates are handled automatically.** These Tableau crosstab exports stamp the date only on each block's `All Sites` header row and leave the per-site rows blank; `entity_build_monthly_tracker.py` forward-fills the date columns on load. (Before v1.3 this silently produced a tracker with only the Sitewide row populated.)

### Number-of-Video actual source
`VideosHistory - primary site.(xlsx|csv)` — videos created/published per site per month. Drop it in the same data folder (auto-detected) or pass `--videos-history`. The file is a diagonal matrix (each `report_date` row fills its matching `Month YYYY` column); the `Grand Total` row maps to the tracker's Sitewide row. The Activity Metrics export has **no** `videos_created` column, so this is the authoritative video-actual source. If the file is absent, the Number-of-Video actual is left blank (target still populates) rather than crashing.

### Tracker template
The prior month's Monthly Tracker xlsx — used as the layout source. The new month's tab is cloned from the prior month's tab and repopulated.

### Monthly Tracker formatting standard
Produce `MANPI and MINUTES Monthly Tracker - {Month YYYY}.xlsx` with the consumer-approved executive table template from the outset. The visible per-site table should use:
- hidden helper columns A:C and frozen panes at the visible table;
- four dark metric header bands: MANPI, MINUTES VIEWED (All NPI), Minutes/MANPI, and Number of Video;
- matching light subheaders by metric group;
- gray target columns, thick outer borders, and thick dividers between metric groups;
- bold left-aligned site names;
- green bold positive variance values and red bold negative variance values;
- a bottom `Sitewide` row using true `All Sites` export actuals for MANPI, minutes, and videos. Do not sum L1 MANPI into this row, because MANPI is not additive across sites.

This is now the default behavior in `{entity_tool:build_monthly_tracker}`; do not leave the tracker in plain workbook formatting and rely on a manual Google Sheets cleanup pass.

### Site-level goals
`{goals_json}` — refreshed when any of three source workbooks updates:
1. **Pharma model** — `{engagement_goals_workbook}`. Source for MAU / Minutes / Mins-per-Active goals on Pharma sites.
2. **FY content planning** — `{content_planning_workbook}`. Source for `videos_published` (Number-of-Video target) on all configured sites.
3. **Device business plan** — `{segment_goals_workbook}`. Source for MAU / Minutes / Mins-per-Active goals on the three Device sites (Orthopaedics, Neurosurgery, Radiology).

See "Goals refresh" section below.

## Slide 1 — Sitewide Health Diagnostic

### Structure
- **Title** — `Sitewide {Month} Community Health Diagnostic`
- **Diagnosis statement** (red, bold) — one sentence on the so-what
- **Bulleted narrative** — Minutes / Email / Mins-per-MANPI / MANPI / WL / Non-Email Minutes / Scope rollups / Bright spots / Recovery sites
- **Source line** at bottom

### Diagnosis heuristics (auto-generated, refine before sending)

The tool generates a starting diagnosis based on these patterns:

| Data pattern | Generated statement |
|---|---|
| Mins/MANPI exceeds goal AND MANPI misses goal by >10% | "MAU shortfall is the primary minutes bottleneck — depth-per-user is healthy" |
| MANPI and Mins/MANPI both miss goal | "Both breadth (MAU) and depth (mins/MANPI) are missing target" |
| Curation rate -10% P3MA AND email sends growing | "Email engine continues to outscale content depth and targeting precision" |
| Total Minutes within ±3% of goal | "Minutes tracking close to goal; metric mix is balanced" |
| Total Minutes <-10% of goal | "Minutes missing goal materially — multiple drivers contributing" |

**Operator review:** Read the data with fresh eyes and rewrite the diagnosis for emphasis. The heuristic is a starting point, not the final framing.

### Bright spots / recovery sites
- **Bright spots** = top 6 sites with Minutes vs target ≥ -2%, displayed in order
- **Recovery sites** = bottom 5 sites with Minutes vs target (worst-first)
- Device sites (Orthopaedics, Neurosurgery, Radiology) are excluded since they have no Pharma goals

## Slide 2 — Priority Engagement Actions

### Structure (4 themes, durable across months)

1. **Content Curation & Start Rate**
2. **Foundational MAU Work** (Acquisition + Reactivation)
3. **Prioritize & Analyze Recovery Specialties**
4. **Scale Bright Spots** (Replicate What's Working)

Each theme has: Theme label / one-sentence context / 3 action bullets.

### Auto-population

The tool fills in:
- **Recovery specialty names** — bottom 3 by Minutes vs target
- **MAU laggards** — bottom 2 by MANPI vs target
- **Bright spot names** — top 3 by Minutes vs target

### Operator review (REQUIRED before sending)

The auto-generated action specifics are placeholders. Replace with concrete commitments:
- Specific Category Lead names (not "Category Lead")
- Dates and owners (not "next week")
- Named tests or analyses (not "test cohort")
- Confirmed executive sponsors (not "ringfenced executive sponsor")

The 4-theme structure itself is durable — don't re-architect unless the month's story genuinely demands a different frame.

## Status dot rules (Health Check)

Carries from the original scorecard runbook (`monthly-scorecard.md`):

- **Green** — both period comparisons positive AND (if a goal exists) at-or-above goal
- **Yellow** — mixed: one direction up, the other flat or down; or essentially flat (±2% on both)
- **Red** — missed goal by >5%, OR both period comparisons negative, OR a single comparison worse than -10%

When in doubt between yellow and red, default to red — the meeting is meant to surface concerns.

## Goals refresh procedure

Three source workbooks feed `site-level-goals.json`. Run whichever extractor(s) match the file you received:

### 1. Pharma model — MAU / Minutes / Mins-per-Active for the configured primary business segment
File: `{engagement_goals_workbook}` (planning team owns).

```bash
python3 {entity_tool:extract_site_goals} \
    --source "/path/to/new model file.xlsx"
```

This rewrites `site-level-goals.json` end-to-end (pulls site × month × metric from `Community Goals` tab) and archives the source to `{engagement_goals_archive}`.

**Run this first if both #1 and #2/#3 changed** — the other two extractors merge into the JSON, so they need it to exist.

### 2. FY content planning — `videos_published` (Number-of-Video target) for all configured sites
File: `{content_planning_workbook}` (`Final Goals` tab; content planning team owns).

```bash
python3 {entity_tool:extract_video_goals} \
    --source "{content_planning_workbook}"
```

Merges `videos_published` per site/month into `site-level-goals.json`.

### 3. Device business plan — MAU / Minutes / Mins-per-Active for Orthopaedics, Neurosurgery, Radiology
File: `{segment_goals_workbook}` (Device team owns).

```bash
python3 {entity_tool:extract_device_goals} \
    --source "{segment_goals_workbook}"
```

Merges Device-only goals into `site-level-goals.json` under each site's the consumer-defined period-goals map (sibling to the Pharma `_note` flag).

The monthly tracker tool reads all three sources from the merged JSON automatically — no other code changes needed.

### Site name mappings
- Tracker uses "Cardiology"; Pharma model uses "Cardiovascular"
- Tracker uses "Allergy, Asthma, Immunology"; FY content uses "Allergy, Asthma & Immunology"
- Tracker uses "Hematology & Oncology"; FY content uses "Oncology & Hematology"
- Tracker uses "Gastroenterology & Hepatology"; FY content uses "Gastroenterology"
- Tracker uses "Obstetrics/Gynecology"; FY content uses "Obstetrics & Gynecology"
- Tracker uses "Orthopaedics"; Device file uses "Orthopedics"

All mappings are handled by the extractors. New site naming variants → update the relevant extractor's `*_TO_TRACKER` dict.

## Known data quality items

- **"Number of Video" — target vs actual definition** — Target is `videos_published` (new videos planned for the month, from the configured content-planning workbook, via `site-level-goals.json`). Actual is the per-site monthly count from **`VideosHistory - primary site`** (videos created/published that month). The Activity Metrics export does **not** carry a `videos_created` column, so VideosHistory is the source. **Do not** use `videos_active (Monthly Aggregation Only)` — that's videos *watched*, not videos *published*, and runs 10–40× larger.
- **WL YoY% comparisons** — the configured WL program may have a short comparison history, so YoY% can be in the hundreds-of-thousands. Always read P3MA, not YoY, for WL channel.
- **Small specialty bases** — sites under ~1,500 MANPI can show big YoY% swings on small absolute deltas. Apply judgment when including in narrative.
- **Device sites in Bright Spot / Recovery rankings** — Orthopaedics, Neurosurgery, and Radiology now have full goals (MAU, Minutes, Mins/Active, Number-of-Video) and are eligible for the auto-ranked Bright Spot / Recovery lists in Slide 1. Prior versions of the runbook excluded them; that exclusion no longer applies.

## File paths

| Item | Location |
|---|---|
| Goals JSON | `{goals_json}` |
| FY model archive | `{engagement_goals_archive}` |
| Output archive | `{report_output_dir}/YYYY-MM-DD/` |
| Pipeline tools | `tools/entity_*.py`, `{entity_tool:generate_weekly_report}` |
| Skill | `.claude/commands/cmo/ops/entity-monthly-mbr.md` |

## Change log

- **v1.0** (2026-05-04) — Initial. Builds on the earlier `monthly-scorecard.md` runbook (which now covers only the slide-style scorecard step within the broader MBR pipeline).
- **v1.1** (2026-05-04 — April MBR session) — Added two sidecar goal extractors (`entity_extract_video_goals.py`, `entity_extract_device_goals.py`). Number-of-Video target is now sourced from the configured content-planning workbook; Device BU goals (Ortho/Neuro/Radio) are sourced from the segment-goals workbook. Tracker tool now reads `videos_created` (not `videos_active`) for the Number-of-Video actual. Narrative tool falls back to computing % to target from raw cells when openpyxl strips formula cache.
- **v1.2** (2026-06-08 — May MBR session) — Made the May 2026 executive table styling the default Monthly Tracker output format: metric color bands, gray target columns, thick section dividers, hidden helper columns, frozen panes, red/green variance formatting, and a true `Sitewide` bottom row sourced from `All Sites` actuals.
- **v1.3** (2026-07-08 — June MBR session) — Tracker generator hardened for raw exports: (1) accepts `.xlsx` inputs as well as `.csv`; (2) forward-fills block-merged date columns on load (fixes a silent bug where only the Sitewide row populated); (3) sources the Number-of-Video actual from `VideosHistory - primary site` (auto-detected or `--videos-history`), since the Activity export lacks `videos_created`; missing video source now leaves the actual blank instead of crashing.
