---
name: writing-setup
description: Use when a repository needs portable writing configuration, a new long-form asset type, or calibrated voice and social-post evidence.
---

# Writing Setup

Use when a repository needs portable writing configuration, a new long-form asset type, or calibrated voice and social-post evidence.

## Contract

Setup writes only consumer-owned files under `config/writing/`. It may configure multiple long-form formats without choosing a permanent primary format. It stores social post types and their evidence, but does not draft social copy.

## 1. Choose setup mode

Use `initial` for a repository without writing configuration. Use `incremental` to add or refine formats while preserving approved files. Never replace approved configuration unless the user explicitly authorizes replacement.

Run:

```bash
python3 {core_tools}/scaffold_writing_setup.py --consumer-root . --mode initial
```

## 2. Interview for voice and taste

Ask how the author speaks when explaining something they know well, which tendencies should remain, which should be edited, and what the writing must never imply. Record source-backed preferences, not celebrity voice blends.

For every proposed good example, ask what specifically should be repeated. For every bad example, ask what failed. Candidates remain unapproved until a human supplies those notes and approves canonical use.

## 3. Configure assets

Keep the default blog/article and newsletter formats unless the user removes them. Add formats through an editorial brief, draft template, editorial standard, required inputs, and quality gates. Do not force a primary long-form format; `writing` selects one after source capture.

## 4. Calibrate social types without drafting

For each proposed social type, keep three evidence classes separate:

- `taste`: examples the user likes and why;
- `owned_performance`: the author's first-party outcomes;
- `category_performance`: broader market observations.

Document purpose, use condition, source requirements, structure, media and CTA posture, positive guidance, anti-patterns, and the performance hypothesis. Human approval is required before an example or type becomes canonical.

## 5. Validate and report

Run:

```bash
python3 {core_tools}/validate_writing_config.py \
  --consumer-root . \
  --profile config/writing/writing-profile.yaml \
  --catalog config/writing/writing-asset-catalog.yaml
```

Return the profile path, catalog path, configured asset IDs, candidates awaiting approval, preserved files, validation result, and any blockers. Do not generate a draft during setup.
