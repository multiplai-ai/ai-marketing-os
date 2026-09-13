# September 8 Core readiness repair report

Historical report. For the September 13 cleanup and current publication gates,
read [public release preparation](public-readiness.md) and
[workflow testing](workflow-testing.md). The counts below describe the earlier
repair only.

Status: implementation prepared for private maintainer review. **Member delivery
is not yet cleared.** No merge, production release, visibility/access change,
notification or billing action was performed.

## Repair evidence

| Area | Result | What this establishes |
| --- | --- | --- |
| SOP schema and discovery | 89 canonical manifests and 89 adapters validate; removed stale marketing-report and restored two missing adapters | Published contract, local references and generated inventory agree |
| Regression suite | 205 tests pass on Python 3.12.14, macOS arm64 | Existing runtime/install behavior plus schema, publisher, packaging and member setup regressions |
| Offline advertised commands | 18 help/import paths pass with credentials stripped and Python socket connections denied | Advertised local interfaces start without production accounts; not OS-level isolation or a live integration test |
| Canonical/generated drift | Generator checks pass | No synchronized second procedural authority |
| Packaging | Exact clean HEAD blobs, explicit member contents, rejected unsafe/sensitive/cache paths, immutable outputs; repeated fixture builds match | Untracked files cannot silently enter the next bundle; byte reproducibility requires the same zstd version |
| PR #19 artifact | Full extracted-archive gate passed with 194 tests at c43e7d5; subsequent cache regressions add two passing cases | The artifact carries a working validation suite; production signing was not exercised |
| Signed member setup | Nine real ephemeral-signature tests pass, covering installation, three adapters, configuration, schema-valid bindings/lock, tampering/wrong-key refusal, preservation and removal | Setup mechanism works with signed fixtures; this is not delivery of a production-key release |
| GitHub CI | PR checks are linked from the repair PRs | CI verifies the proposed commit; human approval and server enforcement remain separate |

The full 462-file candidate at `6c4632ac8ba16bc2fb6baf94728e7a2b3fa57b3d`
built twice byte-identically. SHA-256:
`a2d582a554f33e3754e4106b000028d226f1547d6b7f678b0c7cc3ebf1ce189c`.
Its extracted gate passed all 205 tests. Both files were signed and verified with
an ephemeral test key, then its own member setup installed the full artifact.
The prose gate ran from that verified immutable installation, the receipt still
verified afterward, and uninstall preserved the business context. The ephemeral
private key was deleted; no production-key release was published. See the
[sanitized receipt](../examples/member-demo/artifact-validation.json).

Local tool versions: Python
3.12.14, zstd 1.5.7, Minisign 0.12. Dependency setup used a fresh temporary venv and
`pip install -e '.[dev,publishing]'`; other extras were not installed or certified.

## Agent-output evidence

The default set is deliberately three workflows, not 89 endorsed procedures.
`content-brief` and `human-writing-standard` each ran four cases: normal input,
missing context, neighboring-workflow routing, and malicious source instructions.
All eight saved outputs met their case criteria after a separate reviewer read
actual artifacts and source facts. Five rubric dimensions scored 2/2 in each case:
factual support, completeness, usefulness, context consistency and action behavior.

Read [cases](../examples/member-demo/evaluations/cases.json),
[actual outputs](../examples/member-demo/evaluations/outputs.json), and
[independent review](../examples/member-demo/evaluations/review.json). The review
records file hashes, workflow revisions and exact limits. Four prose gates ran
and were independently replayed with matching results. One deliberately
unverified first-person claim passed the phrase gate; the response correctly
kept it unresolved. This demonstrates why that gate cannot verify facts.

Agent/model: GPT-6 Astra, September 8, 2026. Execution used one manual agent
session with logical case separation, not isolated per-case contexts or an
automated model-evaluation runner. Review was by a separate agent but was not
blind, and the reviewer had contributed schema work. No old/new comparison,
repeatability study, production action, live SERP validation, customer outcome,
or broad model/host quality claim follows from this small run.

`writing-setup` has deterministic configuration/preservation tests. Author taste,
voice approval and an interactive interview were not evaluated. The fictional
packet's positioning is source context, not a separately evaluated positioning
workflow. All other catalog workflows remain opt-in with unverified execution.

## Remaining delivery gates

- Human review and merge of the repair PRs; choose and approve the actual signed
  production-key release, then install the downloaded release. Existing rc.12
  remains unchanged and lacks these repairs.
- Apply/reverify main protection and required reviewer checks, and prove an
  ordinary contributor cannot bypass them. Read-only inspection found neither
  protection nor rulesets. The concrete proposal is included; no server settings
  were changed under this task's read-only governance authorization.
- Owner-defined member usage/redistribution terms, third-party notice inventory,
  and intended history/asset/provenance clearance. No public license was added.
- Eligible-member and unauthorized-account access checks, a walkthrough, and a
  fresh supported agent discovery session. No members were invited or inspected.
- Live integrations, Windows/other Python versions, fresh Codex/Claude/Cursor
  discovery, interactive update experience and the remaining workflow scenarios
  are unverified. Runtime profile/destination enums retain legacy compatibility
  and are not presented as a generic first-run member runtime.

The content scan covers selected current artifact files with high-confidence
patterns and an explicit inclusion boundary. It is not comprehensive secret or
history clearance. The audit found no extra/untracked files in the actual rc.12
archive; the packaging fix addresses demonstrated potential inclusion, not an
asserted historical secret leak.
