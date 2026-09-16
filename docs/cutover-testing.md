# Consumer cutover test plan

Use this plan before changing an existing operating repository from its pinned
historical shared-workflow release to AI Marketing OS. It compares the same work
on both versions; it does not assume that a passing package test proves useful
agent behavior.

## What stays unchanged during the comparison

- The AI product, model, account, and available tools.
- The business packet, prompt, destination, and success criteria.
- The reviewer and the time allowed for first-pass work.

Use fictional or approved non-sensitive packets. Keep client data and account
access inside the operating repository; do not copy either into the public
library or a public test record.

## Test set for the first cutover session

Run the current private pin and the exact AI Marketing OS release candidate for
each selected route. Save both outputs with the workflow id, model, source
revision, and date.

| Route | Example workflow | What to compare |
| --- | --- | --- |
| Writing | `content-brief` then `writing` | Does the agent ask for missing evidence, use the supplied source, and produce a useful draft? |
| Strategy | `discovery-intake` through `content-strategy` | Does each handoff preserve the business facts and yield a feasible next decision? |
| Search visibility | `seo` and `geo-audit` | Are technical findings traceable to page evidence and are recommendations appropriately qualified? |
| Advertising | `ads-audit` or `ads-landing` | Does the review identify material issues without inventing account data? |
| Reporting | one report workflow used by the operating repository | Does the output use the supplied data at the correct scope and label gaps? |
| Setup and discovery | Claude plugin and Codex starter setup | Can a fresh user find and invoke the intended workflow without Core access? |

The full GEO suite is now included. Compare prompt building, answer measurement,
citation mapping, audit, page restructuring, and planning using the same input
packet. API calls require configured credentials and an approved budget.

## Review rubric

For each pair of outputs, record pass, needs revision, or fail for:

1. Correct workflow selection and clear handling of missing inputs.
2. Faithfulness to the supplied business facts and evidence.
3. Useful structure, recommendations, and next steps.
4. Appropriate limits: no invented metrics, citations, client facts, or outcome promises.
5. Time to a reviewable first draft and the amount of human correction needed.

Record material differences plainly. A more polished output is not enough if it
becomes less accurate, less useful, or less safe.

## Technical checks

Before reviewing agent outputs, verify the release candidate with:

```bash
python tools/check_core.py
python -m pytest -q
```

Then test a fresh Claude plugin installation and a fresh Codex starter setup.
For an operating repository, record the exact release receipt with each result.
The owner authorized cutover on September 15, 2026. Keep a verified prior pin
for deliberate rollback while comparing real outputs; a failed resolver must
stop work rather than silently use generic instructions or switch libraries.

## Go/no-go decision

The owner has approved the routing cutover and will review output quality in
the next working session. Setup must work without private Core access and every
workflow in the consumer's lock must exist in AI Marketing OS. Record comparison
failures and explicitly roll back the affected consumer if necessary.

After acceptance, migrate one operating repository at a time: update its lock,
router generation, installer default, documentation, and validation together;
test the installed result; then move to the next repository. Keep the private
repository read-only throughout. A later technical rename of legacy artifact
filenames is separate compatibility work, not a prerequisite for one canonical
workflow source.

## Retired workflow gate after rc.16

The signed `v4.0.0-rc.16` artifact remains a complete, immutable rollback source.
Consumers pinned to it do not depend on a maintainer's working tree and do not
need to change merely because a later release removes a workflow.

Before advancing a consumer beyond rc.16, remove or localize every subscribed
workflow in this retired set:

```text
artifact-to-presentation
audit-funnel
build-workflow
calendar-email-task-handling
content-ideas-slack-to-notion-browser-handoff
daily-brief-cron-prompt
dev-process
ecosystem-partnerships
engagement-report
granola-api-access
growth-operator-hiring
growth-operator-onboarding
hermes-runtime-recovery
jira-marketing
l2-microsite-report
mcp-skill-release-newsletter
monthly-content-planning-and-publishing
monthly-mbr
monthly-scorecard
morning-brief-setup
prompt-optimizer
publish
quarterly-content-planning
routing-and-notifications
scrape-website
social-audience-growth-weekly
social-growth-os
speaking-events-pipeline
sync-repo
to-gamma
to-notion
to-sheets
vps-agent-update
vps-phase0-2-cutover
weekly-audience-report
weekly-executive-update
weekly-kpi-report
weekly-social-audience-growth
whitelist-email-refresh
youtube-transcript
```

Move a still-active procedure into the operating repository that owns its
context and destinations. Delete obsolete Hermes, VPS, generic software, and
repo-maintenance procedures instead of recreating them locally. Do not update a
lock until every requested workflow resolves from either the new shared release
or an explicitly reviewed local package.
