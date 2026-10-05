---
name: client-icp-research
description: Research a business's target customers and produce an evidence-backed ICP and anti-ICP brief, buyer roles, prospect criteria, and a validation plan. Use to build or refresh targeting for a specific client offer.
---

# Client ICP Research

Turn a round of client and market research into decisions about whom to pursue,
whom to exclude, and what to learn next. Use the five-step research framework documented in the method reference. Deliver the research findings
and usable profile in one brief, not just a plan to do research later.

Invoke with: **“Use $client-icp-research for [client] and [offer]. Research the
market and produce an ICP and anti-ICP.”** Existing clients can add “refresh our
current profile” and supply its location.

## Shared foundation and host capabilities

This workflow performs a research round and produces the usable ICP/anti-ICP
brief. The companion `icp-personas` procedure supplies workflow definition,
buying-role analysis and journey mapping; do not reproduce its procedure here.
Before research, read [ICP & Personas](../icp-personas/SKILL.md) from this same
library. Use its workflow and buying-role sections as supporting methodology;
this workflow's research and brief contract controls this assignment. Do not
restart its full interview or require upstream files when equivalent context
is already supplied. Route persona/journey-only requests to `icp-personas` and
offer-packaging requests to `godfather-offer`.

In a consumer with a signed-release resolver, resolve both workflows through
that consumer's pin and report the selected release. If resolution fails, report
it instead of silently substituting another installation. In a Claude/ChatGPT
library package or direct source checkout, read the companion source relative
to this file. Use host-provided authorized web, source and document tools; no
particular connector, local script or private account is a prerequisite. Report
unavailable capabilities and preserve research/output limitations.

Then read [the brief template](templates/research-brief.md) for this engagement's
output and [method sources](references/method-sources.md) for the origin and
limits of the five-step framework. Shared examples are prompts for inquiry,
not client evidence, default price bands, or validated market-size rules.

## Establish the assignment

Resolve the business/client, specific offer/product, geography, customer type
(business or consumer), and decision the research should support. Reuse supplied
business material and prior discovery, positioning and ICP decisions. Where the
working environment has a client README or source register, read it and relevant
originals with the available authorized connections. Otherwise use the sources
provided by the user and public research. There is no default business, offer,
voice, repository path or output destination. Never mix different clients' evidence.

Ask only for missing information that materially changes the research, especially
an ambiguous client or offer. Do not run broad research on an unidentified
client. Missing historical customer data or an upstream file is not a reason
to stop: use supplied context and label the initial segment hypothesis.

Choose a bounded research scope appropriate to the assignment. A useful first
pass compares two or three plausible segments, reads customer evidence plus
public sources, and checks a small candidate sample. These are adjustable
working choices, not statistical thresholds. State the scope and proceed;
the request to research does not require another generic approval gate.

## Research round and evidence rules

Carry out the research with available read-only connectors and web/browser
tools. Search is discovery; open and read the relevant original material before
citing it as evidence. Read accessible transcripts before using a video's spoken content; use the
host's available transcript reader and disclose missing captions. Log inaccessible sources and what that prevents you
from concluding. A snippet or title does not establish what an unread source says.

Use these lanes where relevant and available:

- **Client evidence:** customer outcomes, delivery effort, retention, win/loss
  notes, interviews, sales calls, support questions, current offers and proof.
  Include poor fits and counterexamples, not only successful customers.
- **Buyer evidence:** public reviews, discussions, questions, and documented
  workflows from people plausibly in the segment. Capture the situation,
  current alternative, consequence, trigger, and language. Note selection bias.
- **Market and candidate evidence:** official company/product pages, relevant
  job descriptions, alternatives and competitor positioning, directories, and
  current market sources. Competitor claims show their positioning, not proof
  that a segment buys or achieves the advertised result.

For each material observation, record source ID, direct link or permissioned
pointer, date/access result, page/section/timestamp where useful, segment,
finding, and limits. Separate a short exact quotation from your interpretation.
Distinguish **observed**, **client-reported**, **inferred**, and **unknown**.
A repeated claim copied across sites is not independent corroboration.

Label the research round **completed within stated scope**, **partial**, or
**blocked**, with attempted/completed sources and material gaps. Separately label
the ICP **provisional** or **supported for a bounded pilot** and explain why.
Do not call it validated solely because a report, score, or source quota exists.
If access prevents substantive research, return an incomplete brief and targeted
questions; never invent findings to fill the template.

## Apply the five steps

### 1. Find the good fits

Compare who benefits, the conditions required to deliver the result, customer
effort, and whether serving them makes commercial sense. Check losses, churn,
and costly delivery for contrary evidence. Do not equate biggest invoice with
best customer or infer profitability without cost evidence. Historical customers
reflect prior reach; they do not reveal every viable segment.

Without customers, start from the offer's credible capabilities and a reachable
group. Treat expected benefit, willingness to pay, and economics as hypotheses.

### 2. Understand the purchase

Apply the shared workflow and buying-role analysis to the actual offer, whether
software, a service, or a consumer product. Research the problem or desired
progress, current workaround/alternative, consequence, reason to act, purchase
participants, objections, and implementation needs.

Prefer accounts of actual episodes to hypothetical willingness-to-buy answers.
Preserve buyer language with evidence references. Do not fabricate quotations,
budgets, titles, daily routines, or personal motivations. If interviews would
resolve a gap, prepare the questions; do not claim interviews happened or contact
people without separate authorization.

### 3. Choose a group and define the anti-ICP

Compare candidate segments on evidence of need, solution/delivery fit, ability
to buy and implement, commercial viability, reachability, and sufficient market
opportunity. Recommend a first segment for this offer and explain the tradeoff
against alternatives. Leave unsupported market-size and pricing estimates unknown.

Classify profile criteria as **must-have**, **useful clue**, or **hypothesis**,
with rationale and evidence. Use firmographics only when they help explain or
find fit. An illustrative employee range is not a universal qualification rule.

Make the **anti-ICP** a separate, usable exclusion table. Each exclusion needs
an observable condition or discovery question, the reason it undermines this
offer's value/delivery/economics, evidence status, action, and reconsideration
condition. Include lookalikes that meet surface filters but lack the relevant
workflow or cannot benefit from this offer. A speculative exclusion remains a
question to test, not a proven disqualifier.

Keep these decisions distinct:

| Finding | Treatment |
| --- | --- |
| Confirmed incompatibility with this offer or its delivery requirements | Anti-ICP: exclude from this offer; state any viable alternative separately. |
| Good fit, no current buying priority or temporary implementation capacity | Nurture/defer; record a revisit trigger, not a permanent anti-ICP label. |
| Need, budget, authority, capacity, or criterion not established | Research/qualify; unknown is neither failure nor confirmation. |

For consumers, use the relevant person/household, use situation, and purchase
constraints; do not force company size or B2B job titles into the profile.

### 4. Find real prospects

Test whether the profile can identify real candidates from accessible evidence.
For B2B, a small public account sample (for example, up to ten) is a useful
first pass; adapt to scope and access. Show which criteria each meets, sources,
fit status, timing clues and their dates, relevant buying roles, and unknowns.
Include borderline/excluded cases when available to test the boundaries.

Hiring, funding, or a new leader can justify investigation; none proves pain,
budget, or intent for this offer. Keep fit and timing separate. Prefer relevant
roles to collected personal contact details. For consumer markets, use aggregate
audience/channel examples and documented customer situations; no named-person
prospect list is required. Report coverage gaps rather than manufacturing rows.

### 5. Test and use it

Specify the next learning action, question, evidence to collect, owner or owner
needed, and revisit date/trigger. A small interview or outreach test is a proposed
next step, not an executed campaign. Explain how the profile changes list
selection, messaging, qualification, proof, and delivery decisions.

Separate interest, qualified conversations, paid purchases, successful adoption,
and profitable retention. One weak campaign cannot distinguish a bad ICP from
an ineffective offer, message, channel, contact choice, or timing. When refreshing
a profile, record which assumption changed, why, and what action changes with it.

## Deliver and check

Use [the brief template](templates/research-brief.md). Put the recommended ICP,
anti-ICP, confidence limits, and next action first; include research findings,
evidence ledger, candidate check, buyer roles/journey, and pilot plan in the same
document. Keep unknown fields visible instead of inventing filler.

Before handing off, trace every material inclusion and exclusion to evidence
or a labeled hypothesis. Check that two teammates could apply the criteria;
that an unready good fit was not called an anti-ICP; and that the recommended
group can plausibly receive value from this specific offer. Surface conflicting
evidence. No model score supplies client approval.

Resolve the output location from the user's request and current business context.
Prefer an editable document or downloadable Word file where host tools support
it, and verify its contents before linking. Use an approved external destination
only when established for this work; do not silently create a third-party storage
requirement. Keep business outputs out of this shared library. Keep raw exports,
recordings, personal contact data and sensitive quotations out of public Git.
If a source register applies, update safe pointers/checksums only after successful
save/readback. If saving is unavailable, provide the useful brief in chat and name
the unsaved artifact; a temporary path is not a verified durable handoff.

Return the brief link or inline brief, research coverage/gaps, ICP recommendation,
anti-ICP exclusions, and next validation action. This skill does not launch ads,
update CRM qualification rules, send outreach, or publish client material.
