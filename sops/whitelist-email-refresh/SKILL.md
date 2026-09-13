---
name: whitelist-email-refresh
description: Refresh the weekly performance tracker for entity's whitelist email program (BULK + BET). Updates the tracker in place — never regenerates from scratch.
---

# entity Whitelist Email Refresh Runbook

Refresh the weekly performance tracker for entity's whitelist email program
(BULK + BET). Updates the tracker in place — never regenerates from scratch.

> Merged 2026-07-02 (Phase 3): this runbook absorbed the richer operating detail
> that had accumulated in the skill copy (`.claude/commands/cmo/ops/entity-whitelist-email-refresh.md`).
> This file is the entity canon; the skill is the invocation surface.

## Canonical Workbook

`brains/entity/projects/Whitelist Email Tracker/Whitelist_Email_Analysis.xlsx`

This workbook is the persistent artifact. Refresh it in place unless the user
explicitly approves replacing it. If the user uploads a new file, confirm
whether it replaces the canonical workbook or appends as new week's data.

## When To Use

- Weekly BULK + BET email performance refresh (start of week, once the prior
  Monday–Sunday is complete).
- New daily-send data is available.
- The user asks for the whitelist email dashboard, weekly tracker, or program
  health update.

## Required Sheets

1. `Daily Performance_Full Data_dat` — columns (any order, matching names):
   `Day`, `mail_type` (`bulk`/`bet`, lowercase), `send_date`, `site_name`,
   `source`, `NPI User Conversion`, `NPI w/ Sends`, `Sends`, `Starts`.
2. `Weekly Tracker` — standard template (inputs in B5:D9, four sections).
3. Optional: `Whitelist Ingestion` — WL → User conversion context (reference
   only; not wired into formulas).

## Workflow

1. **Load new data** — append or replace rows in `Daily Performance_Full Data_dat`.
   Verify row count grew; check `mail_type` values are all `bulk` or `bet`.
2. **Identify the reporting week** — most recent complete Monday–Sunday. If the
   latest week is partial (<7 days), flag it in Section 5 Notes; report numbers
   but mark as partial.
3. **Update week anchors** — `Weekly Tracker` B5:D9: current week / prior /
   two weeks ago / three weeks ago / partial-latest (optional). Dates `YYYY-MM-DD`.
4. **Roll forward the history table** — Section 2 (Rolling Weekly History,
   starting row 35): insert a new row above the last populated row, copy
   formulas from the row above, enter Week Start (Mon) and Week End (Sun) in
   columns A–B. Formulas C–N auto-populate.
5. **Review status flags** — scan Status column (H) in Section 1 for ⚠️ Below
   flags; note magnitude and one-week-dip vs trend (WoW Δ column + Section 2).
6. **Specialty-level check** — Section 3: top 3 specialties by conversion rate;
   any specialty with >10% WoW drop in sends or conversions; any specialty in
   the red band (<0.01% conv rate) with meaningful volume (>50K sends).
7. **Write weekly notes** — Section 5 row: top-line result (sends, conversions,
   conv rate, WoW), one or two watch-items, recommended actions.
8. **Deliver summary in chat** — 4–6 lines: week ending, totals with WoW,
   BULK vs BET split, 1–2 winners, 1–2 concerns, data-quality issues.

## Primary KPIs & current targets

**Lead with these:**
- Total NPI Conversions — target ≥ 850/week.
- NPI Conversion Rate, Total — target ≥ 0.020%.
- Week-over-week Δ on total conversions.

**Channel diagnostic:** BULK conv rate vs BET conv rate — they mail different
specialties and perform very differently. BULK typically higher (primary care,
psych, surgical); BET lower (Cardio, Heme/Onc, Neuro, Derm).

**Volume / delivery:** Total Sends — target ≥ 5.5M/week; alert if ±15% outside
the rolling 4-week average. Also Starts and Start Rate.

Targets are editable in Weekly Tracker column G rows 15–26. Review quarterly.

## Interpretation Rules

- **Always split BULK and BET**; never aggregate their conversion rates blindly.
- A single week below target = watch; **two consecutive weeks below = act**.
- **Heme/Onc, Cardiology, Neurology, Dermatology** — watch especially:
  high-volume BET specialties with structurally weak conversion; small movement
  × big volume = material impact.
- **Adult & Family Medicine** is the biggest BULK specialty; any WoW move there
  drives the program-level number.
- **Dental, Podiatry, Plastic Surgery, Anesthesiology, Emergency Medicine** —
  low/zero send volume; don't flag on conversion rate when sends <10K/week.
- Partial weeks are never compared to complete weeks on absolute KPIs — only
  rates are comparable.

## Data quality checks

- `mail_type` must be exactly `bulk` or `bet` (lowercase); flag anything else.
- Site names must match the canonical list in Weekly Tracker Section 3
  (rows 45–72); new names won't appear until added.
- `Sends = 0` with `Conversions > 0` = data error — investigate.
- A specialty dropping to zero sends after consistent volume = likely campaign
  pause or data issue, not performance.

## Guardrails

- Do not regenerate the tracker from scratch.
- Do not change formula structure.
- Do not add sheets unless the user explicitly asks.
