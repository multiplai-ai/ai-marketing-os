---
name: writing
description: Use when turning a real brain dump, transcript, interview, research set, or approved source packet into one source-faithful long-form article or newsletter.
---

# Writing

Use when turning a real brain dump, transcript, interview, research set, or approved source packet into one source-faithful long-form article or newsletter.

The workflow produces three connected artifacts: one format-neutral editorial source packet, one long-form draft, and one downstream marketing handoff. It does not draft social posts, run campaigns, publish content, or perform the landing-page audit.

## Core rule

Source comes before prose. Preserve the author's exact language, evidence, uncertainty, and judgment. Never invent lived experience, quotations, results, customers, facts, or certainty. Thin inputs trigger capture questions; they do not authorize generic filler.

## Inputs

- `topic_or_assignment`
- `voice_inputs`: transcripts, notes, rough arguments, interviews, or source articles
- `source_packet_ref`: an existing schema-valid packet, when available
- `writing_profile`: consumer-owned `writing-profile.yaml`
- `asset_catalog`: consumer-owned `writing-asset-catalog.yaml`
- `asset_type_id`: selected only after capture
- `source_refs`: research or evidence references
- `output_path`

Portable bindings may point to `writing_profile_ref`, `article_asset_catalog_ref`, `editorial_standard_ref`, `good_exemplar_refs`, `bad_exemplar_refs`, `default_output_root`, `additional_quality_gate_refs`, and an optional `production_log_ref`. Resolve every consumer path inside the consumer repository and validate it before use.

## Outputs

- source packet YAML conforming to `schemas/writing-source-packet.schema.yaml`;
- one Markdown draft whose frontmatter conforms to `schemas/writing-article.schema.yaml`;
- one YAML handoff conforming to `schemas/writing-handoff.schema.yaml`;
- unresolved claim IDs, checks run, and final status.

## 1. Resolve configuration

Load the writing profile and asset catalog. Validate them with:

```bash
python3 {core_tools}/validate_writing_config.py \
  --consumer-root {consumer_root} \
  --profile {profile_ref} \
  --catalog {catalog_ref}
```

Read the selected voice guide, editorial standard, approved good and bad exemplars, and additional gates in full. If configuration is missing, run `writing-setup`; do not substitute embedded brand conventions.

## 2. Capture a format-neutral source packet

Use an existing packet, a rich brain dump, or a guided interview. Capture:

- topic or assignment;
- thesis: the one argument the author wants to make;
- trigger: what happened or changed;
- tension and stakes;
- exact phrases with source references;
- firsthand evidence with sensitivity labels;
- claims classified as `firsthand`, `verified`, or `unresolved`, with evidence references and attribution;
- strongest counterargument;
- reader outcome;
- cutting-room material worth preserving;
- sensitive details that must be removed, generalized, or kept private.

Ask only for genuine gaps. The five core prompts are:

1. What is the one argument you want this piece to make?
2. What happened or changed that made it worth writing now?
3. What contradiction, disagreement, or unresolved pressure gives the idea energy?
4. What concrete consequence follows if the reader gets this wrong?
5. What should the reader understand, decide, or do afterward?

Do not paraphrase exact phrases during capture. Do not convert a numerical statement into a verified claim without evidence. Keep sensitive material in the packet so reviewers can make an explicit decision, but do not leak it into the draft.

Validate the packet using `writing_source_packet.py` or the source-packet schema. Report any missing capture questions.

## 3. Confirm packet and outline

Show the proposed thesis, opening pressure, evidence map, unresolved claims, counterargument, reader outcome, sensitive-detail treatment, and a short outline. Ask for confirmation when the source choice or sensitivity treatment would materially change the piece.

Do not choose the output format until capture is complete. One source packet can support multiple later renders without rewriting its evidence.

## 4. Select one long-form asset

Select exactly one catalog asset whose `kind` is `long_form`. Writing V1 rejects `social_post` render requests. Load that asset's editorial brief, template, standards, and approved examples.

Default Core choices are:

- `default-blog`: a search-aware article with opening pressure, thesis development, evidence and mechanism, implications, and an action section;
- `default-newsletter`: a reader-relationship format with subject/title, preview opening, promise, body arc, resource or action, and close.

No format is permanently primary. Choose the one that fits this assignment.

## 5. Render one source-faithful draft

Write one specific argument. Use concrete scenes, constraints, mechanisms, and consequences from the packet. Preserve useful asymmetry and exact language. Attribute verified external facts. Treat unresolved claims as unresolved; omit them, qualify them, or keep them visibly flagged for review.

Required frontmatter:

```yaml
schema_version: 1
artifact_type: long_form_article
status: incomplete | draft | review_ready
title: "Article title"
slug: article-title
created: YYYY-MM-DD
asset_type: default-blog
audience: "Specific reader"
thesis: "One source-supported argument"
source_packet_ref: path/to/source-packet.yaml
handoff_ref: path/to/handoff.yaml
unresolved_claim_ids: []
checks_run: []
```

Use `incomplete` when core capture or required evidence is missing. Use `draft` while material editorial or claim work remains. Use `review_ready` only after required gates pass and the article is safe for human review. A missing destination URL does not by itself prevent `review_ready`; it does prevent landing-audit readiness in the handoff.

## 6. Build the downstream handoff

The handoff lets later skills draft social posts and audit the destination without reinterpreting the article. It contains references rather than copied evidence wherever practical.

Record:

- article and source-packet references;
- message: core thesis, promised outcome, audience, supporting claim IDs, and exact phrase IDs;
- offer: name, summary, conversion goal, and primary CTA;
- destination: URL, desired action, message-match terms, and substantiation expectations;
- social angle candidates: angle, claim IDs, exact phrase IDs, and CTA posture only, never finished copy;
- landing-audit intake: traffic source, entry message, target audience, expected offer, CTA, substantiation, and destination URL;
- readiness for LinkedIn drafting and landing audit, with explicit blockers.

`linkedin_ready` requires a coherent message, supported claims or clearly safe source material, and at least one usable angle candidate. `landing_audit_ready` additionally requires a destination URL, expected offer, expected CTA, expected substantiation, target audience, and entry message. If the URL is missing, set `landing_audit_ready: false` and add a blocker even when the article is `review_ready`.

## 7. Run quality gates

Run the Core deterministic gate:

```bash
python3 {core_tools}/human_writing_gate.py {draft_path} --json
```

Then perform the human review required by `human-writing-standard` and every configured consumer gate. A regex cannot verify authentic voice. Compare the exact draft against the packet, voice guide, exemplars, sensitivity decisions, and editorial brief.

Before marking `review_ready`, confirm:

- every factual and experiential claim maps to packet evidence or remains explicitly unresolved;
- exact phrases are source-faithful and not misleading out of context;
- no private or anonymize-marked detail leaked into prose;
- the argument develops rather than filling a formula;
- the opening, sections, and close match the selected asset's purpose;
- the CTA and handoff promise do not exceed what the destination or offer can support;
- frontmatter, source packet, and handoff validate against their schemas;
- every gate actually run appears in `checks_run`.

## 8. Return a production receipt

Report:

```markdown
- Source packet: [path]
- Long-form draft: [path]
- Handoff: [path]
- Asset type: [id]
- Status: [incomplete | draft | review_ready]
- Unresolved claims: [IDs or none]
- Checks run: [list]
- LinkedIn handoff ready: [yes/no and blockers]
- Landing audit ready: [yes/no and blockers]
```

If configured, append only this receipt to the production log. Do not create social derivatives or publish anything.
