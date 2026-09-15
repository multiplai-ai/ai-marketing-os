# Workflow testing order

Start with one fictional or approved non-sensitive business packet. Record the
input, exact skill revision, actual output and what required correction. A
passing technical check does not establish strategy quality or live integration.

| Priority | Test | Automated/offline coverage | What the subscriber or owner should judge |
| --- | --- | --- | --- |
| 1 | Fresh setup → content brief → prose review | Signed installation, three adapters, binding/receipt checks, existing eight editorial cases | Does a fresh agent find the skill? Is the first output useful without setup coaching? Is the copy accurate and recognizably yours? |
| 2 | Discovery → positioning → ICP → brand → content → suite review | New 24-case offline strategy run with actual linked outputs and separate review; see recorded evidence | Do recommendations match a real business? Are alternatives meaningful? Is the plan feasible? Review one real packet through the chain. |
| 3 | Customize → signed update → rollback | Consumer-context/config preservation and signature/receipt regression coverage | Can you upgrade and return to the prior version without losing your changes or confusing the agent? |
| 4 | One selected publishing destination | Local previews, missing-credential/dependency checks, publisher regressions | Review the draft/preview in the real destination; publication remains a separate authorized action. |
| 5 | Design, GEO, video, reports and scheduled/VPS work | Optional dependency startup, controlled GEO HTML fixture, runtime boundary tests | Test only the integrations you intend to offer, using their actual consumer configuration and approved inputs. |

Suggested first session: 10 minutes on fresh setup, 15 minutes on a useful brief
and prose revision, then 20–30 minutes reviewing a strategy chain for one real
business. Treat those as planning estimates, not measured completion times.
Do not ask subscribers to test all 84 included procedures at once.

## Recorded evidence

- Editorial examples: `examples/member-demo/evaluations/`.
- Strategy cases, inputs, actual outputs and review: `examples/strategy-evaluation/`.
- `python tools/check_evaluation_evidence.py` checks complete case coverage and
  unchanged inputs, skills, upstream outputs and review records. It does not
  judge quality or independently prove that the recorded actor followed a skill.
- The strategy run uses one authoring agent across cases. It is not a blind,
  isolated, multi-model or repeated experiment; review limitations are recorded.
- Live APIs, publication, real-world outcomes and fresh Codex/Claude/Cursor
  discovery are outside these offline runs.

If a source or procedure changes, the old result becomes stale. Run the affected
case and its downstream chain again; do not update hashes to re-label an old
output as freshly evaluated. Keep failed cases and corrections visible.

For the controlled comparison required before moving existing private consumers
to AI Marketing OS, use the [consumer cutover test plan](cutover-testing.md).
