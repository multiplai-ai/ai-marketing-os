# Article Batch Contract

Use this reference only when the `linkedin-post` skill is running in `article_batch` mode.

## Purpose

Turn one completed long-form article into a small set of LinkedIn posts that create different reasons to read, trust, discuss, or act. The batch is a campaign derived from the article, not a sequence of interchangeable summaries.

## Required inputs

1. **Source article** — the exact draft or final article being promoted.
2. **Evidence ledger or evidence handoff** — structured claim support from the writing or research workflow.

Strongly recommended:

- audience and campaign objective;
- voice profile plus relevant exemplars;
- destination page URL or identifier;
- offer and primary conversion action;
- desired batch size (default: four, acceptable range: three to six).

If the evidence material is missing, do not label the output evidence-backed. Ask for it or produce only a clearly labeled editorial extraction that contains no new factual claims.

## Normalize the evidence

Convert the supplied ledger or handoff into this working table before drafting:

| Claim ID | Exact claim | Status | Source | Safe use |
|---|---|---|---|---|
| C1 | Verbatim or faithful claim | `supported`, `inference`, `opinion`, or `unsupported` | Citation, source note, or article location | Allowed wording and qualification |

Apply these controls:

- **Supported:** May be used within the scope and precision the source supports. Keep material qualifiers and timeframes.
- **Inference:** Attribute or qualify it as an inference. Do not rewrite it as settled fact.
- **Opinion:** Present it as the author's judgment or recommendation.
- **Unsupported:** Exclude it from published copy. Put it in the evidence-gap list if it matters.
- **Conflicting or stale:** Flag it for review and omit it unless the conflict is resolved.

The article can establish the author's argument and language, but a repeated claim does not become independently verified through repetition. Never create a citation, statistic, quote, customer outcome, or firsthand experience that is absent from the inputs.

## Step 1: Source and evidence audit

Read the whole article and evidence material. Record:

- central thesis;
- intended reader and their problem;
- article promise and practical payoff;
- strongest supported claims and proof points;
- author opinions worth isolating;
- examples or scenes that can stand alone;
- useful methods, steps, or decisions;
- unsupported, conflicting, or ambiguous claims;
- exact destination and conversion action, if supplied.

Stop and ask for clarification only when ambiguity changes the factual meaning or destination. Otherwise make a conservative choice and state it in the handoff.

## Step 2: Design a diverse batch

Assign every post a distinct **reader job** before drafting. Choose the jobs supported by the material; do not force all of them.

| Reader job | What the post does | Suitable material |
|---|---|---|
| Reframe | Changes how the reader sees the problem | Defensible thesis or counterpoint |
| Prove | Builds confidence with evidence | Supported data, example, or comparison |
| Teach | Gives the reader a useful action | Method, checklist, decision rule |
| Reveal | Shows how the author reached the conclusion | Process, mistake, or build note |
| Diagnose | Helps the reader recognize a costly pattern | Symptoms, tradeoffs, or failure modes |
| Invite | Connects the article to a relevant next step | Clear audience, destination, and offer |

Default to four posts. A valid batch of four should normally use at least three different reader jobs, at least two different structures, and different opening ideas. Diversity is semantic, not cosmetic.

Reject a proposed post when:

- its core claim and payoff duplicate another post;
- it is only a summary of the article;
- it depends on unsupported evidence;
- removing the hook would make it indistinguishable from another draft;
- its only purpose is to fill the requested count.

## Step 3: Draft each post

For each post, define privately before writing:

- reader job;
- one-sentence angle;
- target reader;
- claim IDs used;
- intended response;
- destination relationship: direct link, soft reference, or no link.

Then draft a standalone post. Each post must make sense even if the reader never sees the others. It should deliver value before asking for attention or a click.

Link behavior is a campaign choice. Do not assert a universal reach penalty or hide the destination by default. Follow the user's channel strategy, and make clear which post points directly to the page.

Run the shared voice and integrity check on every post. Also compare the batch side by side for repeated hooks, repeated paragraph skeletons, redundant examples, identical closes, and accidental claim drift.

## Step 4: Coverage map

Return a compact table before or after the clean drafts:

| Post | Reader job | Distinct angle | Evidence used | Intended response | Link approach |

Evidence used must list claim IDs, or `opinion only` when no factual support is needed. This is a review aid, not copy for publication.

If fewer posts can be supported than requested, state: `Delivered N of M requested posts` and list the specific evidence or angle gap. Do not pad.

## Step 5: Landing-page handoff

Create a handoff that lets a conversion or landing-page audit compare the campaign promise with the destination. Use `not supplied` rather than guessing.

```yaml
landing_page_handoff:
  destination_url: "..."
  campaign_objective: "..."
  target_audience: "..."
  primary_conversion_action: "..."
  source_article_title: "..."
  source_article_promise: "..."
  post_promises:
    - post_id: P1
      reader_job: "..."
      promise: "..."
      evidence_ids: [C1]
  required_message_match:
    - "What the landing page must confirm for the click to feel coherent"
  proof_available:
    - claim_id: C1
      proof: "..."
      source: "..."
  evidence_gaps:
    - "Unsupported or missing proof that the auditor must not assume"
  constraints_or_assumptions:
    - "Any conservative decision made during the batch"
```

The handoff reports what the social copy promises. It does not score the page, infer page content that was not supplied, or pre-decide the audit.

## Output order

1. Evidence gaps or blockers, if any.
2. Coverage map.
3. Clean post drafts labeled `P1`, `P2`, and so on.
4. Landing-page handoff.

Keep citations or source notes with the review material when they would interrupt the public post's voice. The reviewer must still be able to trace every factual claim to the normalized evidence table.
