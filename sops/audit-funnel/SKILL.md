---
name: audit-funnel
description: 'Run an entity''s assessment-led sales funnel: a scored diagnostic survey that produces an instant personalized report, segmented follow-up, and a tracked pipeline from completed audit to closed engagement. The skill maintains the instrument, scores responses deterministically, gates every outbound touch behind human approval, and reviews funnel performance monthly against benchmarks.'
---

# Audit Funnel

Run an entity's assessment-led sales funnel: a scored diagnostic survey that produces an instant personalized report, segmented follow-up, and a tracked pipeline from completed audit to closed engagement. The skill maintains the instrument, scores responses deterministically, gates every outbound touch behind human approval, and reviews funnel performance monthly against benchmarks.

> Shared audit-funnel procedure. Resolve the current consumer scoring/report generator and verify it before running; this skill supplies judgment, coordination and the approval workflow.

## When To Use

- Processing new diagnostic survey responses into scored reports and follow-up
- Maintaining or revising the audit instrument (questions, scoring, fixes, report copy)
- Running the monthly funnel review (stage conversion vs benchmarks)
- Preparing call-prep context for a booked results walkthrough
- Planning the webinar feeder for the funnel

Do not use this for the survey platform's technical setup or the Notion database creation (wiring-checklist items owned by the entity owner), for drafting social content that promotes the funnel (use `writing` / `linkedin-post` with the entity voice gates), for partner co-hosted webinar outreach (use `ecosystem-partnerships`), or for proposal pricing (the owner prices; comp ranges in the strategy doc are benchmarks, not prices).

## Operating Principle

The diagnostic measures exactly what the paid offers fix, so every response is pre-discovery. The funnel's value chain is: comparable scoring → credible band + benchmark → three fixes that feel unmistakably theirs → one low-friction CTA → segmented persistence for 14 days. Consistency is the product: reports must be deterministic and auditable, which is why scoring lives in a tool, not in generation.

## Inputs

- Entity brain path (`{brain}`)
- New survey responses (dataset: `audit_funnel_responses` in `{brain}/data-manifest.yaml`)
- Pipeline state (dataset: `lead_pipeline`)
- Booking URL (runtime config from the owner; never hardcoded in repo files)
- For monthly mode: review month and prior review artifact, if any

## Outputs

- Scored prospect reports (markdown from `tools/audit_report.py`), queued for human sanity check
- Follow-up sequence drafts per score band, queued for approval
- Pipeline record updates (stages, scores, next actions) in the entity lead-pipeline database
- Monthly funnel review: `{brain}/operations/audit-funnel/{month}-funnel-review.md`

## Required Context

Load before operating:

1. `{brain}/BRAIN.md`
2. `{brain}/strategy/audit-funnel-design.md` — funnel architecture and design rationale
3. `{brain}/marketing/audit-funnel/survey-questions.md`, `scoring-model.md`, `fix-library.md`, `report-template.md`, `followup-sequences.md` — the instrument (all five carry machine-readable contracts consumed by `tools/audit_report.py`)
4. `{brain}/marketing/audit-funnel/webinar-playbook.md` — the monthly feeder
5. `{brain}/operations/lead-pipeline-notion-schema.md` — pipeline stages, properties, views
6. `{brain}/data-manifest.yaml` — dataset pointers for `audit_funnel_responses` and `lead_pipeline`
7. The entity's approval matrix runbook, if present — it is binding for every outbound touch

## Approval Gates And Data Rules (binding)

- **Every report is human-approved before it is sent.** Generated ≠ sent. The operator sanity-checks score plausibility, fix relevance, and merge-field correctness.
- **Every outbound touch is human-approved**: sequence emails, replies, DMs, webinar follow-ups. No auto-send, ever.
- **Contact data lives only in the entity's lead-pipeline database (Notion), never in the repo.** Repo artifacts carry aggregates and record links only. Response files passed to the scoring tool are transient inputs (`.tmp/`), not committed.
- Proposals and pricing are owner-only. The skill prepares audit-derived discovery points; it does not send or price proposals.
- If the scoring tool fails validation or produces implausible output: STOP, report expected-vs-actual, and ask. Do not hand-edit the tool or hand-compute a score to route around it.

## Workflow

### 1. Instrument Maintenance

The survey questions, scoring model, fix library, report template, and sequences live in brain files, not in the survey platform and not in code. The platform implements the brain files.

- Any wording change to questions or fixes: edit the brain file first, then flag the owner to sync the platform. Never let the platform drift ahead of the repo.
- Never change question IDs, dimension keys, band ranges, or fix IDs without a migration note: stored responses and pipeline records reference them.
- After any edit to the five instrument files, run `python3 tools/audit_report.py --selftest` to confirm the machine-readable contracts still parse.
- Revision triggers: completion rate below floor (see design doc), a dimension that never differentiates respondents, fixes that repeatedly miss on calls (log which, propose replacements in the fix library).

### 2. Response Intake And Scoring

For each new completed response in `audit_funnel_responses`:

1. Create or update the pipeline record (stage: `Audit completed`) with qualification fields (role, team size, ICP segment, self-reported source, artifact URL).
2. Write the response answers to a transient JSON file and score it:
   `python3 tools/audit_report.py --responses <file> --booking-url <url> ...` (dry run first; `--write` to save the report artifact).
3. Record score, band, weakest dimension, and follow-up segment on the pipeline record.
4. Sanity-check the tool's output yourself before queuing: does the band match the answers? Do the three fixes address the weakest dimensions? If the tool errors or the output is implausible, stop per the gate above.

### 3. Report Generation And Sanity-Check Gate

- Queue the generated report for the operator's sanity check with a one-line rationale ("score 38, Assisted, weakest: delivery; fixes 1-2 target delivery, fix 3 tooling").
- Only after approval: report goes out through the approved channel, pipeline stage → `Report sent`, and the instant-booking link must be live on the results page/report.
- Reports are score + benchmark + top 3 fixes + one CTA, under 5 minutes to read. Resist additions; comprehensive free reports kill conversion by giving the roadmap away.

### 4. Follow-Up Sequence Execution

- Map band → segment via the scoring model; draft the segment's touches from `followup-sequences.md` with merge fields filled from the pipeline record.
- Queue each touch for approval on its send-day offset. Check exit conditions before every send: booked call, replied, or unsubscribed all stop the sequence immediately (see the sequences file for stage moves).
- A reply always beats the sequence: draft a personal response for approval instead of the next canned touch.
- Sequence exhausted → stage `Nurture`, prospect enters the monthly webinar/newsletter orbit.

### 5. Pipeline Tracking

- Keep every active record's `Next action` and due date current; the operator's daily queue is only as good as these fields.
- Stage discipline per the schema doc: no skipping `Report sent`; no record parked >14 days without a dated next action or a move to `Nurture`.
- For records reaching `Call booked`: assemble call prep for the closer (score, band, weakest dimension, probe quotes, qualification, source) on the pipeline record. The audit's discovery points are the personalization that makes proposals outperform (audit-personalized ~34% vs 17% generic).

### 6. Monthly Funnel Review

Produce `{brain}/operations/audit-funnel/{month}-funnel-review.md` with aggregates only:

| Stage conversion | Benchmark |
|---|---|
| Assessment start → completion | 55-70% (floor 50%, redesign below 45%) |
| Completed audit → booked call | ~20% |
| Call → proposal | ~50% |
| Proposal → close | ~25% median (34%+ audit-personalized, 3-option) |
| Planning math | 1,000 visitors → ~120 audits → 20-30 calls → 3-5 closes |
| Webinar feeder | reg→attend 40-56%; attendees → live audit 20-40% |

Also cover: volume vs the entity's ramp expectation bands (do not let a normal ramp read as failure), source-channel mix (self-reported + artifact URLs), score-band distribution vs close rate (the qualification-logic validation), sequence performance by touch, instrument health (per-question drop-off), and 1-3 recommended changes with owner and evidence. Separate facts from hypotheses explicitly.

## Quality Gates

- Zero unresolved merge fields in any sent report or email (the tool's selftest enforces this for reports).
- Every sent report traceable to a tool run, not hand-assembled.
- 100% of outbound touches carry an approval record.
- Monthly review states benchmarks next to actuals and labels every number FACT or HYPOTHESIS.
- No contact-level data in any repo artifact this skill produces.

## Failure Modes

| Failure | Response |
|---|---|
| Scoring tool errors on a response | Stop, report expected-vs-actual, ask. Never hand-score. |
| Report reads generic for a specific respondent | Check probe answers were captured; flag instrument or fix-library gap; do not pad the report. |
| Completion rate below floor | Diagnose per-question drop-off before proposing question changes; propose edits to the brain file, owner approves. |
| Low scorers close as often as high scorers | Flag the scoring model for re-weighting in the monthly review; do not silently adjust weights. |
| Sequence getting unsubscribes above ~2% per touch | Pause the segment's queue, flag copy for revision against the entity voice profile. |
| Booking link missing or dead | Halt report sends entirely until the owner confirms the URL; a report without instant booking wastes the funnel's best conversion mechanic. |
| Pipeline database unreachable | Queue updates locally in `.tmp/`, notify the operator, never fall back to committing contact data to the repo. |
