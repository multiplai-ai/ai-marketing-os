# Landing Page Conversion Quality Audit

## Decision summary

- Quality score: **67/100**
- Evidence coverage: **80%**
- Confidence: **Medium** — the source and page copy are direct evidence, but mobile behavior, live performance, and measurement readiness are unknown.
- Primary conversion risk: The generic headline breaks continuity with the specific incident-handoff promise, while the eight-field form asks for more commitment than the page justifies.
- Best next action: Align the hero to the incident-handoff use case and reduce or sequence the form before promoting the article-derived posts.

## Conversion story

| Element | Normalized input | Page continuation |
|---|---|---|
| Source promise | Reduce dropped ownership with a documented incident-handoff rhythm. | The page promises general operational improvement and does not mention incidents or handoffs. |
| Audience | B2B software operations leaders coordinating support and engineering. | “Your organization” does not signal the role, company type, or cross-team use case. |
| Offer | A 20-minute review mapping the current incident handoff. | The 20-minute review is named, but the page calls it a general operations assessment. |
| CTA | Book a 20-minute workflow review. | The primary CTA matches; the form button changes to the generic “Submit.” |
| Conversion goal | Completed workflow-review booking. | A form is present, but booking completion and what happens next are not explained. |

## Scorecard

| Dimension | Weight | Status | Points | Evidence |
|---|---:|---|---:|---|
| Message match | 30% | Partial | 19.50 | H1 and hero paragraph are generic; offer and primary CTA partially continue the source. |
| Offer and CTA clarity | 20% | Strong | 20.00 | “Book a 20-minute workflow review” makes action and time commitment explicit. |
| Friction and usability | 15% | Weak | 4.50 | Eight required fields include phone and company revenue; the button says “Submit.” |
| Trust and substantiation | 15% | Partial | 9.75 | Privacy and terms are linked, but example logos and an anonymous testimonial provide limited substantiation. |
| Mobile and visual experience | 10% | Unknown | — | Text-only snapshot cannot establish responsive behavior or visual hierarchy. |
| Performance and measurement readiness | 10% | Unknown | — | No field data, diagnostics, event documentation, or tag evidence was supplied. |

Calculation: `(19.50 + 20.00 + 4.50 + 9.75) / (30 + 20 + 15 + 15) × 100 = 67.19`, displayed as **67/100**. Coverage: `80 / 100 × 100 = 80%`.

## Evidence ledger

| ID | Observation | Locator | Source type | Confidence |
|---|---|---|---|---|
| E1 | The source promises a documented incident-handoff rhythm. | `input.yaml`, `source_promise` | Documented context | High |
| E2 | The hero says “Streamline your operations” and describes a general assessment. | `landing-page-snapshot.md`, hero | Direct page evidence | High |
| E3 | Primary CTA names a 20-minute workflow review. | `landing-page-snapshot.md`, hero CTA | Direct page evidence | High |
| E4 | The form has eight required fields, including phone and company revenue. | `landing-page-snapshot.md`, “Tell us about your team” | Direct page evidence | High |
| E5 | Logos are labeled illustrative and the testimonial identifies only a role. | `landing-page-snapshot.md`, “Trusted by modern teams” | Direct page evidence | High |

## Prioritized recommendations

### 1. Continue the article's promise in the hero

- Finding and evidence: Message match is `Partial`; E1 promises incident-handoff improvement while E2 uses generic operations language.
- Why it matters: A visitor arriving from the article must reinterpret the offer instead of seeing the promised use case continue.
- Proposed change: Replace the headline with **“Turn incident handoffs into a repeatable operating rhythm.”** Add: **“In 20 minutes, map how support and engineering transfer ownership today and identify the first handoff to clarify.”**
- Impact / effort: High / Low
- Validate with: Compare CTA-start rate and qualified booking completion for the aligned variant against the current page, with audience and traffic source held stable.

### 2. Match form commitment to the 20-minute review

- Finding and evidence: Friction is `Weak`; E4 shows eight mandatory fields before the visitor knows what happens next.
- Why it matters: Phone and revenue requests add unexplained commitment to a diagnostic offer.
- Proposed change: Start with work email, company, and the handoff challenge. Collect qualification details during scheduling or a second step, and explain why each retained field is needed.
- Impact / effort: High / Medium
- Validate with: Measure form-start, field error, abandonment, completed booking, and qualified-booking rates. Do not optimize completion at the expense of lead quality.

### 3. Replace placeholders with attributable evidence

- Finding and evidence: Trust and substantiation are `Partial`; E5 labels logos illustrative and attributes the testimonial only to “VP, Operations.”
- Why it matters: Generic social validation cannot substantiate the operational outcome implied by the offer.
- Proposed change: Remove placeholder logos from a live page. Add a permissioned example naming the context, intervention, and observed result, or state plainly that the review is a new offer without customer evidence yet.
- Impact / effort: Medium / Medium
- Validate with: Run a five-person comprehension test asking what evidence supports the offer; monitor qualified booking rate after publishing genuine customer evidence.

## Copy alternatives

- Headline: **Turn incident handoffs into a repeatable operating rhythm.**
- Supporting copy: **Map how support and engineering transfer ownership today, then leave with one concrete handoff to clarify.**
- Primary CTA: **Book my 20-minute workflow review**
- Form button: **Choose a review time**
- Expectation cue: **You’ll answer three questions, choose a time, and receive the handoff map after the call.**

## Unknowns and next evidence

- Supply mobile and desktop screenshots or a responsive recording to assess layout, CTA visibility, controls, and obstruction.
- Supply dated field performance diagnostics to assess loading and interaction quality.
- Supply the conversion-event definition and a non-production test record to verify that a completed booking maps to the stated goal.
- Individual phone-call tracking is `N/A` unless calls are introduced as a conversion path; this does not excuse unknown booking-event tracking.
