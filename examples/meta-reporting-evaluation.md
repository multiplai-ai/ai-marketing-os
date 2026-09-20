# Meta reporting pilot evaluation — 2026-09-20

Base: `895b678e9af33294b14cb04cc5ebbcdc0f2e4a74`. Actor: Codex implementation task. Independent reviewer: `reporting_validation` subagent, synthetic inputs only, no live requests or repository edits.

| Case | Source and action | Observed output |
| --- | --- | --- |
| Normal | `tests/test_meta_reporting.py`, report day has 999 spend/1 order; seven preceding days have 800 spend/61 orders. Run daily reporting. | Day CPA 999; baseline CPA 13.114754098360656; report day excluded. Donor and paid metrics separate. Repeated CLI input keeps the same run ID. |
| Missing | Remove API goal field/type; separately remove API credential and part of required date coverage. | Explicit failure, no zero-conversion substitute, no network request without token, no report for incomplete coverage. |
| Wrong route | Reuse an account A output directory from account B. | Both history read and save reject the mismatch. Same-account history remains readable. |
| Untrusted | Ad/ledger text contains an instruction to raise budget, Markdown image syntax and an HTML image tag. | Text is never executed as an instruction; final Markdown escapes HTML and Markdown metacharacters. No Meta write method exists. |

Independent review initially found five issues: cross-account history, missing goal configuration, incomplete-day timestamps, unescaped report text and dollar-specific currency display. All were fixed and independently retested. Five checked-in regression cases now cover those fixes; 17 reporting tests pass on Python 3.12.

Additional tests cover duplicate rows, exported total-row exclusion, short months, Monday-Sunday windows, unmapped spend, separate recorded approval/execution states, API cursor pagination, overlapping purchase aliases and unsafe returned pagination URLs. The adapter follows a cursor on its fixed Meta host, never the returned URL.

Limits: deterministic tool behavior and bounded skill interpretation were evaluated. This is not live API attribution reconciliation, a rendered-document security test, a blinded evaluation of agent-generated recommendations, approval from a human maintainer, scheduler verification or delivery verification. Independent retest found no additional substantive regression within that scope.
