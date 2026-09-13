# Evidence and scoring

Use this contract for every landing-page conversion quality audit. It prevents a polished-looking score from overstating what the available page evidence can prove.

## Evidence hierarchy

Record the source type and locator for every material finding:

1. **Measured first-party evidence:** supplied analytics, experiment results, field performance data, or documented event tests, including date range and segment
2. **Direct page evidence:** publicly observed page content, supplied HTML, screenshots, recording, or exported page copy
3. **Documented context:** supplied campaign brief, source asset, audience definition, offer, CTA, tracking plan, or research
4. **Inference:** a reasoned interpretation based on the above, explicitly labeled as inference
5. **External context:** current, cited benchmarks or research, labeled with source and publication date

External context cannot establish what the audited page does. Vendor claims and generic benchmarks cannot be treated as measured outcomes for the user's page.

## Allowed statuses

| Status | Numeric value | Use when |
|---|---:|---|
| Strong | 100 | Direct evidence shows the criterion is complete, coherent, and suited to the stated conversion decision. |
| Partial | 65 | The criterion is materially present but has a meaningful gap, inconsistency, or qualification. |
| Weak | 30 | Some relevant element exists, but it is unlikely to support the intended decision without substantial improvement. |
| Fail | 0 | Direct evidence shows the criterion is absent, contradictory, broken, or materially misleading. |
| Unknown | excluded | The criterion is applicable, but available evidence cannot support a judgment. |
| N/A | excluded | The criterion genuinely does not apply to this conversion path; explain why. |

Use `Unknown`, not `Fail`, for inaccessible pages, unobserved mobile behavior, unavailable performance data, or undocumented tracking. Use `N/A` sparingly; lack of evidence is never a reason for `N/A`.

## Dimension weights

| Dimension | Weight |
|---|---:|
| Message match | 30% |
| Offer and CTA clarity | 20% |
| Friction and usability | 15% |
| Trust and substantiation | 15% |
| Mobile and visual experience | 10% |
| Performance and measurement readiness | 10% |
| **Total** | **100%** |

## Calculations

For each dimension with a scored status (`Strong`, `Partial`, `Weak`, or `Fail`):

`earned weighted points = dimension weight × numeric value / 100`

Then normalize over only the weights that could be scored:

`quality score = 100 × sum(earned weighted points) / sum(scored dimension weights)`

Round the displayed quality score to the nearest whole number. Preserve the unrounded value if further calculations are needed.

Calculate evidence coverage separately:

`evidence coverage = 100 × sum(scored dimension weights) / (100 − sum(N/A dimension weights))`

`Unknown` therefore reduces evidence coverage but does not depress the quality score. `N/A` changes neither score nor coverage when correctly justified.

## Confidence

Start with the coverage band, then lower confidence when source quality or a critical unknown warrants it:

- **High:** at least 80% evidence coverage, predominantly direct or measured evidence, and no critical unknown that could reverse the decision
- **Medium:** 50–79% coverage, or at least 80% coverage with a critical technical/experience unknown or substantial reliance on documented context
- **Low:** below 50% coverage, inaccessible/unstable evidence, or inference carries most conclusions

Confidence describes the audit's evidence, not the page's quality. Explain any downgrade in one sentence.

## Claims discipline

- Describe recommendation impact as High, Medium, or Low unless measured data supports a number.
- Do not repeat rules such as “every second costs X% conversion” as universal facts.
- Do not turn industry averages into forecasts.
- If modeling a scenario, label it as a scenario and show baseline, assumptions, range, and calculation.
- Pair each proposed change with a validation method: funnel event check, usability task, session review, field-data comparison, or controlled experiment.
