---
name: weekly-kpi-report
description: Build a weekly program-success report from the required Tableau exports with the consumer-configured report generator.
---

# Weekly Program Success KPI Report

Produce a Word report and, when requested and authorized, a Confluence version
with the source document attached. This shared procedure supplies the validation
and publishing sequence. Business-specific program definitions, export schemas,
watchlists and generator code must come from the consumer configuration.

## Resolve the report contract

Reuse the supplied week-ending date, export folder and prior report. Ask only
for missing required inputs. Before running, resolve:

- `{report_contract}`: metric definitions, required export names/formats,
  program/group mappings, comparison window and anomaly rules;
- `{input_dir}` and `{output_dir}` in approved consumer storage;
- `{entity_tool:compile_kpi}`, `{entity_tool:build_kpi}` and, if needed,
  `{entity_tool:build_confluence_html}`, `{entity_tool:publish_to_confluence}`;
- for publishing, `{confluence_cloud_id}`, `{confluence_space_id}`,
  `{confluence_parent_page_id}` and `{confluence_parent_page_url}`.

These generator tools and business data are not bundled with Core. Verify that
configured tool paths exist, dependencies are installed and their actual CLI
matches the intended invocation. If the generator or report contract is missing,
report that prerequisite; do not substitute an unrelated client's implementation.
Never execute unresolved placeholders or infer destination IDs from examples.

Keep source exports and credentials in approved private storage. Verify ignore
rules before placing data inside a consumer checkout. Preserve prior inputs or
use a dated run folder instead of silently overwriting last week's evidence.

## Collect and validate the exports

Use the exact required files from the consumer's report contract, including any
CSV companion exports. Verify the number, filenames, formats, reporting window
and data-through date agree. Do not assume a fixed number of files.

Common input checks, where the contract requires them:

- Aggregate total rows are present when unique counts require deduplication.
- Detail rows are not summed as a substitute for distinct program/user totals.
- Rolling-window feeds cover the same extraction date as weekly snapshots.
- CSV encoding and delimiter match the loader, even if a TSV uses `.csv`.
- Prior-week inputs exist for comparisons; unavailable deltas are labeled.

Document missing data, stale exports and unexpected columns. Repair mappings
only after verifying the source meaning. Do not manufacture totals or silently
convert fractions into percentages without checking the metric definition.

## Build and inspect

Run the configured compiler, then the document builder, using a dated output
folder. Preserve the normalized data artifact and source-to-output traceability.
Generate Confluence HTML only if that output is needed.

The selected host must actually support Python execution, file handling and the
required libraries. Check those capabilities rather than assuming a named chat
product can execute or publish. A local machine is one option; a connected
remote environment is another. If publishing is unavailable, return the Word
artifact for manual upload without claiming the page was created.

Before publishing, inspect the document and compare against source data:

- Headline totals reconcile to the defined program/group scope.
- Unique counts use the prescribed aggregation basis.
- Priority delivery, watchlist and at-risk classifications follow configured
  thresholds and program definitions.
- Week-over-week changes compare like periods; decreases are investigated rather
  than assumed wrong.
- Nonzero activity paired with zero unique counts is explained or corrected.
- Methodology notes identify material source anomalies and missing comparisons.

Render and inspect the Word document using the available document workflow.
Present the artifact for operator review. Do not publish unresolved discrepancies.

## Publish when authorized

Verify read access to the configured parent and space before preparing the page.
Use the existing authorization for the requested write, subject to the user's
communication rules. If publication is not authorized, provide the artifact and
exact destination for review.

Use a title such as `R{revision} — Week ending {date}` only if the consumer uses
that convention. Resolve the next revision from existing reports. Search by the
report's week and identity before writing: update an existing matching page only
when the task authorizes replacement, otherwise create the intended new page.
Do not promise idempotency unless the configured publisher enforces it.

After a permitted publish, verify page content and the Word attachment and
return their links. For a timeout or ambiguous result, inspect the destination
before retrying so the operation does not create duplicates.

## Troubleshooting and ownership

| Symptom | Check |
|---|---|
| Missing-column error | Compare current export headings with the configured column map. |
| Pacing off by a factor of 100 | Confirm fraction/percentage representation against the data contract. |
| Unique counts missing despite activity | Inspect aggregate rows and deduplication basis. |
| Source totals differ from detail sum | Apply only documented anomaly rules; surface unexplained differences. |
| Publisher returns 401/403 | Report the selected account's access failure; let the owner repair its credential or permission. |

Change shared procedure here through a reviewed Core PR. Change consumer-only
program lists, definitions and tools in their owning repository. Preserve one
canonical authority rather than copying this SOP into the generator directory.
