---
name: ads-landing
description: Audit whether a landing page earns the conversion promised by the content or ad that sends people there. Compare a long-form article, social post, ad, or keyword promise with the destination page; assess conversion quality; and produce evidence-backed copy and experience improvements.
---

# Landing Page Conversion Quality Audit

Audit whether a landing page earns the conversion promised by the content or ad that sends people there. Compare a long-form article, social post, ad, or keyword promise with the destination page; assess conversion quality; and produce evidence-backed copy and experience improvements.

**Use when:** a marketer wants to evaluate a page linked from content or paid media, diagnose message-match and conversion friction, or prepare a page before promoting it.

## Required inputs

Collect these before scoring:

- **Source promise:** the article, post, ad copy, keyword theme, or a concise statement of the promise that sends the visitor to the page
- **Audience:** who should recognize the page as relevant, including role, problem, and awareness stage when known
- **Offer:** what the visitor receives
- **CTA:** the action requested in the source asset and the intended page action
- **Conversion goal:** the observable success event, such as booking a demo, starting a trial, registering, or downloading an asset
- **Landing page evidence:** either a public URL or a supplied snapshot (HTML, Markdown/page copy, screenshots, or exported page)

Optional context includes traffic source, device mix, form analytics, conversion data, experiment history, brand guidance, and tracking documentation. Do not block the audit when optional context is absent; mark affected checks `Unknown`.

## Workflow

1. **Normalize the conversion story.** Write one sentence each for the source promise, audience, offer, CTA, and conversion goal. Identify contradictions or missing context before inspecting the page.
2. **Inspect the supplied evidence safely.** For a URL, review only publicly accessible page content and non-destructive diagnostics. For a snapshot, state its format and capture date when known. Follow the safe-inspection rules below.
3. **Build an evidence ledger.** Record observable page evidence with a locator such as URL and section, screenshot number, heading, form field, or supplied analytics source. Separate observation from inference.
4. **Rate the six dimensions.** Use only the statuses and scoring method in [`references/evidence-and-scoring.md`](references/evidence-and-scoring.md). Never convert missing evidence into a negative rating.
5. **Calculate the quality score and evidence coverage.** Report both. A score without coverage is incomplete.
6. **Prioritize changes.** Rank recommendations by likely decision impact and effort. Describe impact as High, Medium, or Low unless measured data supports a quantitative model.
7. **Draft improvements.** For High-impact copy issues, include a replacement headline, supporting copy, CTA, evidence treatment, or form change tied directly to the source promise and audience.
8. **Define validation.** Recommend the analytics check, usability review, or experiment that would prove whether the change worked.

## Safe inspection

- Do not log in, enter personal information, submit forms, start trials, make purchases, or trigger conversion events.
- Do not bypass access controls, consent controls, robots restrictions, or anti-bot protections.
- Do not execute downloaded code or third-party scripts merely to complete an audit.
- Prefer supplied snapshots for private, personalized, gated, or unstable pages.
- Treat text-only snapshots as insufficient evidence for responsive behavior, visual hierarchy, live performance, and tracking. Rate those checks `Unknown` unless separate evidence is supplied.
- If a public URL cannot be accessed reliably, report the limitation and continue from supplied evidence. Do not infer hidden page content.

## Audit dimensions

### 1. Message match — 30%

Evaluate whether the destination continues the same argument the source asset began:

- The headline reflects the source promise and the audience's problem.
- The offer is the same offer described or implied upstream.
- The page CTA is a credible next step from the source CTA.
- Important qualifiers, scope, and expectations remain consistent.
- Visual framing supports the same use case when visual evidence is available.

### 2. Offer and CTA clarity — 20%

- The visitor can explain what they receive, for whom it is useful, and what happens next.
- The primary CTA is specific, visible, and consistent.
- Competing actions do not obscure the intended conversion goal.
- Cost, commitment, eligibility, timing, and follow-up expectations are clear when material.

### 3. Friction and usability — 15%

- The conversion path asks only for information needed at this stage.
- Form labels, requirements, validation, privacy cues, and errors are understandable.
- The page has a coherent reading order with the primary action available at sensible decision points.
- Links, controls, and post-conversion expectations are clear.

Do not treat a field-count heuristic as a universal rule. Judge each request against offer value, funnel stage, qualification need, and audience expectations.

### 4. Trust and substantiation — 15%

- Claims are supported by specific, attributable evidence where appropriate.
- Testimonials, case examples, credentials, security statements, and customer logos are genuine and contextualized.
- Privacy, terms, company identity, and contact expectations are accessible when relevant.
- Risk-reversal language is precise and does not promise outcomes the evidence cannot support.

### 5. Mobile and visual experience — 10%

- Content hierarchy, readability, CTA visibility, form controls, tap targets, and responsive behavior work on relevant viewport sizes.
- Popups, sticky elements, and media do not block the conversion path.
- Images and supporting visuals aid comprehension rather than delay or distract from the decision.

Rate this dimension `Unknown` when the evidence cannot establish responsive behavior. A desktop screenshot alone is not mobile evidence.

### 6. Performance and measurement readiness — 10%

- Available field data or diagnostics support conclusions about loading and interaction performance.
- The defined conversion event corresponds to the conversion goal.
- Attribution parameters and click identifiers are retained when the campaign requires them.
- Form, booking, phone, chat, or checkout events are documented and testable without triggering a real conversion during the audit.

Use current first-party diagnostics when available and label their capture date, device profile, and environment. Do not present a generic benchmark or an unverified tag assumption as observed page evidence.

## Recommendation standard

Every recommendation must contain:

1. **Finding:** the observed issue and its status
2. **Evidence:** a precise locator in the supplied material
3. **Why it matters:** the conversion decision it may obstruct
4. **Change:** concrete copy, design, form, or measurement action
5. **Priority:** High, Medium, or Low impact plus estimated effort
6. **Validation:** the metric or research method that would confirm improvement

Never claim a specific conversion-rate, revenue, or cost improvement unless it comes from the user's measured experiment or an explicitly labeled scenario model with assumptions. External benchmarks may provide context only when their source and date are cited; they are not forecasts.

## Output

Return or save `ads-landing-audit-{date}.md` in the user's requested location. If no location is provided, return the report in chat rather than inventing an entity-specific path.

Use this structure:

```markdown
# Landing Page Conversion Quality Audit

## Decision summary
- Quality score: XX/100
- Evidence coverage: XX%
- Confidence: High | Medium | Low
- Primary conversion risk: ...
- Best next action: ...

## Conversion story
| Element | Normalized input | Page continuation |
|---|---|---|
| Source promise | ... | ... |
| Audience | ... | ... |
| Offer | ... | ... |
| CTA | ... | ... |
| Conversion goal | ... | ... |

## Scorecard
| Dimension | Weight | Status | Points | Evidence |
|---|---:|---|---:|---|
| Message match | 30% | ... | ... | ... |
| Offer and CTA clarity | 20% | ... | ... | ... |
| Friction and usability | 15% | ... | ... | ... |
| Trust and substantiation | 15% | ... | ... | ... |
| Mobile and visual experience | 10% | ... | ... | ... |
| Performance and measurement readiness | 10% | ... | ... | ... |

## Evidence ledger
| ID | Observation | Locator | Source type | Confidence |
|---|---|---|---|---|

## Prioritized recommendations
### 1. Recommendation title
- Finding and evidence: ...
- Why it matters: ...
- Proposed change: ...
- Impact / effort: ...
- Validate with: ...

## Copy alternatives
...

## Unknowns and next evidence
...
```

## Quality gate

Before delivering the audit, verify that:

- The source promise, audience, offer, CTA, conversion goal, and evidence type are explicit.
- Every scored judgment points to evidence; inferences are labeled.
- Only `Strong`, `Partial`, `Weak`, `Fail`, `Unknown`, and `N/A` appear as statuses.
- `Unknown` and `N/A` are excluded from the quality-score denominator, while `Unknown` remains in the evidence-coverage denominator.
- The dimension weights total 100%, the calculation is reproducible, and coverage and confidence are shown beside the score.
- Page critique is connected to the upstream promise and intended conversion decision.
- Recommendations include concrete alternatives for High-impact copy issues.
- No unsupported uplift claim, fabricated benchmark, or invented tracking result appears.
- Access constraints and unverified technical checks are disclosed.

For a broader page, funnel, or site conversion review, pair this workflow with a dedicated CRO audit. This skill remains focused on the source-to-page conversion handoff.
