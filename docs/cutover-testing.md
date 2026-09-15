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

Do not test `geo-plan`, citation mapping, prompt-set building, content
restructure, or share-of-answers through the public library. Those workflows
are not included in AI Marketing OS today.

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
For an operating repository, do this in a separate disposable test copy. Do not
change its live lock, generated routers, installer, or default repository
during the comparison.

## Go/no-go decision

The owner decides after reviewing the recorded outputs. A cutover can proceed
only when the selected workflows pass the rubric, setup works without private
Core access, and every workflow in the consumer's lock exists in AI Marketing
OS or has been moved or retired deliberately.

After acceptance, migrate one operating repository at a time: update its lock,
router generation, installer default, documentation, and validation together;
test the installed result; then move to the next repository. Keep the private
repository read-only throughout. A later technical rename of legacy artifact
filenames is separate compatibility work, not a prerequisite for one canonical
workflow source.
