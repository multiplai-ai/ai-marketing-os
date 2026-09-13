---
name: l2-microsite-report
description: Generate L2 microsite funnel analysis with the canonical report generator.
---

# L2 Microsite Report Runbook

Generate L2 microsite funnel analysis with the canonical report generator.

## Tool

- `{entity_tool:generate_l2_report}`

## Required Intake

Before running:

- Confirm the L1 site, such as Oncology.
- Confirm the export folder path.

## Command

```bash
python3 {entity_tool:generate_l2_report} --data-dir "<l2-export-folder>"
```

Use `--output-dir` only when the user needs a non-default output location.

## Required Input Files

- `L2_Active NPI.xlsx`
- `L2 Sends.xlsx`
- `L2_Starts.xlsx`
- `L2_Min.xlsx` or `L2_Min (1).xlsx`
- `L2 SR.xlsx`

## Expected Output

- `OUTPUT {YYYY-MM-DD}/l2-report-{YYYY-MM-DD}.xlsx`
- Exactly 9 tabs:
  - Executive Summary
  - Active Users
  - Sends per User
  - Start Rate %
  - Minutes per User
  - Minutes per Start
  - Total Minutes
  - Total Starts
  - Funnel Diagnostic

## Guardrails

- Do not use legacy scripts or CSV fallback paths.
- Do not recreate report logic outside the canonical tool.
- Verify the workbook exists and has exactly 9 tabs before sharing.
