---
name: weekly-audience-report
description: Produce a weekly audience-growth narrative and audit workbook from consumer-configured analytics exports, with optional authorized Confluence publishing.
---

# Weekly Audience / User Growth Report

Produce a weekly narrative and an Excel drill-down workbook. Reuse supplied
exports and business context. Resolve the consumer's metric definitions, export
schema, goals, comparison basis and reporting dates before calculation.

This Core procedure does not bundle the consumer's report builder. Resolve
`{entity_tool:build_user_growth_report}` from consumer configuration and inspect
its supported CLI. If it is missing, report that prerequisite; do not claim the
report can run solely from this SOP.

## Inputs and deliverables

Resolve `{export_folder}`, `{data_through}`, `{output_dir}`, `{goals_json}` and
the configured input files. Verify every required file and requested comparison
period is present. Ask only for missing required values.

Expected deliverables in the dated output folder:

1. `{YYYY-MM}-user-growth-narrative.md` — weekly narrative with seven sections.
2. `{YYYY-MM}-user-growth-report.xlsx` — headline totals and supporting segment,
   source, site and unsubscribe breakdowns, with source precision retained.

Do not assume source filenames, encoding or site-level goal paths. If the
consumer uses point-in-time active-user snapshots plus activity exports, verify
the snapshot dates and formats separately. Optional exports may leave a section
unavailable; label that gap rather than inventing data.

## Narrative sections

1. **Overall user growth:** active and new users against the configured prior
   period, baseline and goals.
2. **Sites or segments doing well vs struggling:** supported changes with their
   absolute bases and the consumer's inclusion thresholds.
3. **Frequency segment migration:** movement between the configured frequency
   groups. State the observation window and any monthly lag.
4. **Unsubscribe rates:** total and available reason/type breakdowns. Use the
   configured denominator and enough history to support trend claims.
5. **On-site activity:** starts, time spent or the available engagement measures
   by referral source and device, separating email where the exports support it.
6. **New registrations:** source and site/segment breakdowns. Keep registrations
   distinct from newly active users.
7. **What to watch:** a short list tied to the material findings and missing data.

## Build and verify

Invoke the configured builder with verified input paths, data-through date,
goal file and output directory. Inspect its help before constructing a command;
placeholder syntax here is configuration notation, not an executable command.

Retain the source exports in approved private storage and record the inputs used.
Reconcile headline figures and selected subgroup calculations with the workbook.
Check that chart labels, narrative comparisons and workbook dates agree.

- Use the latest eligible snapshot on or before data-through for stock metrics.
- Compare flows over like periods; label pacing assumptions separately from
  actuals. Never compare a partial-period flow with an unadjusted full period.
- Do not force totals to reconcile across differently filtered populations.
  Record each population and label directional comparisons.
- Read small-base changes in absolute values as well as percentages.
- Missing/unavailable is not zero. Late-arriving segments keep their own dates.
- Determine whether a metric's increase or decrease is desirable from its
  definition, rather than coloring every increase green.

Use consumer formatting conventions in the narrative; retain full numeric
precision in the audit workbook. Inspect the rendered workbook and narrative
before operator review. Confirm that automated ranking reflects the meaningful
story rather than merely the largest percentage swing.

## Optional Confluence publishing

Resolve `{confluence_cloud_id}`, `{confluence_space_id}`,
`{confluence_parent_page_id}` and `{confluence_parent_page_url}` from the current
consumer binding. Verify the destination exists, is accessible and is not
archived. Never reuse IDs or destination names from another installation.

Prepare the narrative and workbook for operator review. Publish only when the
requested write is authorized under the user's communication rules. Inspect
the installed connector's available methods and content formats before use.
If the connector is missing or access fails, return the local deliverables and
identify the missing connection; do not claim publication succeeded.

Use the configured title convention, for example
`{Month} {Year} Weekly Audience Report — {date range} (data through {date})`.
When the page title replaces the document's leading H1, avoid duplicating it in
the body. Search for the matching report before an update or retry. Verify the
published content and intended workbook attachment, then return their links.
