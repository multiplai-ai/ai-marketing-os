---
name: weekly-executive-update
description: Draft a weekly executive update from a locked KPI table, source evidence, and consumer-defined priorities.
---

# Weekly Executive Update Runbook

Draft the weekly update for the consumer-configured executive and business scope.
Resolve `{executive_recipient}`, `{business_scope}`, `{report_output_dir}`,
the metric contract and contributing teams from current consumer context.
Do not infer people or destinations from an older report. The metric set below
is an inherited engagement-report pattern; use it only when the consumer
contract adopts those definitions.

## Required Intake

Collect before drafting:

- KPI table for the locked 8 metrics.
- User's read on the numbers.
- Updates from the consumer-configured contributing teams.
- User's own weekly update.
- Any ask, risk, or escalation.

## Locked KPI Metrics

- Minutes
- Active Users Annual
- Active Users Monthly
- Mins/Active User Monthly
- Mins/Active User Annual
- Email Minutes
- Non-Email Minutes
- Email Sends/Annual Active User

## Calculation Rules

- Use paced minutes for per-user MTD pace metrics.
- Use paced email sends for Email Sends/Annual Active User.
- Use P3MA denominators for P3MA per-user metrics.
- Use `—` when a raw MTD value does not apply.
- Include plus/minus signs on deltas.

## Email Structure

1. Subject: `Weekly Update — {business_scope} — Week of [Month DD]`
2. Executive summary: exactly 5 tight bullets.
3. KPI table with the 8 locked metrics.
4. Detailed breakdown expanding the same executive-summary themes.

## Voice

- Confident and direct.
- Facts first, then interpretation.
- Attribute wins to people.
- Surface risks clearly.
- No corporate filler.

## Output

Save the approved markdown to:

`{report_output_dir}/YYYY-MM-DD-weekly-update.md`

Keep business artifacts in approved consumer storage, not shared Core source.

If Gmail drafting tools are available, create a draft only. Do not send.

## Guardrails

- Do not fabricate KPI data.
- Do not add metrics unless the user asks.
- Do not skip user review before creating an external draft.
- If Gmail tools are unavailable, say so and provide the approved markdown/HTML instead.
