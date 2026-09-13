---
name: creative-produce
description: 'Campaign-aware production routing: loads brand tokens, components, and templates to produce on-brand assets from an approved creative foundation, routing by asset type — static visuals, content visuals, or multi-channel campaigns.'
---

# Creative Produce

Campaign-aware production routing: loads brand tokens, components, and templates to produce on-brand assets from an approved creative foundation, routing by asset type — static visuals, content visuals, or multi-channel campaigns.


Legacy adapter: previously invoked as the `/cd/produce` command via `.claude/commands/cd/produce.md`; that path is now an adapter, not the canonical mechanism.

Distinct from the `content-produce` core skill (merged from `.claude/commands/cmo/content/produce.md`), which orchestrates the written-content pipeline (brief → article → QC → publishing handoff). This skill produces branded visual/creative assets. They intersect at content visuals — see "Relationship to content-produce" at the end.

**Goal:** Create branded production assets from the entity's approved creative foundation. Routes by asset type, loads all context automatically, enforces brand compliance.

---

## Prerequisites

**HARD BLOCK:** All three must exist:

- `{brain}/creative/brand-guide.md`
- `{brain}/creative/components/` (with SVGs)
- `{brain}/creative/templates/` (with SVGs)

→ If missing: STOP. Run `creative-status` (legacy: `/cd/status`) to check what's missing, and recommend the next missing foundation stage.

The portable stub additionally requires before producing:

- `{brain}/creative/tokens.json`
- `{brain}/creative/component-inventory.md`
- `{brain}/creative/template-inventory.md`
- reusable components or templates for the requested channel

**Auto-loaded every production run:**

- `{brain}/creative/tokens.json`
- `{brain}/creative/generated/gamma-prompts.md` (locked AI prompts)
- `{brain}/creative/component-inventory.md`
- `{brain}/creative/template-inventory.md`
- CMO strategy docs (soft — for campaign context): `{brain}/strategy/positioning-strategy.md`, `{brain}/strategy/brand-strategy.md`, `{brain}/strategy/icp-personas.md`

## Inputs

1. **Entity (brain) name** (required)
2. **What to produce** — user describes the asset(s)

## Workflow

### Step 1: Campaign Context

Ask user / capture:

- What campaign or content calendar item? (or one-off?)
- Goal: awareness, conversion, engagement?
- Channels: LinkedIn, Instagram, ads, email, web?
- Audience, offer, formats, deadline, and success metric

### Step 2: Asset Scope

Classify the request:

- **Single asset** — one visual, one channel
- **Multi-format batch** — same concept across channels
- **Full campaign set** — multiple concepts across channels
- **Content visual or diagram**
- **Ad creative exploration**

### Step 3: Route to Sub-Workflow

---

#### Route A: Static Visual (ads, social graphics)

1. **Copy generation** — minimum 30 headline + subheadline pairs, organized by messaging wedge
2. User selects 5-10 for current batch
3. **Shot list** — 30-50 specific shot descriptions:
   - Each: composition, subject, mood, color treatment, texture
   - Uses locked Gamma prompts from `{brain}/creative/generated/gamma-prompts.md`
4. User selects/ranks shots
5. **Gamma image generation** — TWO prompts per call:
   - **Prompt A (Image Style):** Locked prompt from `{brain}/creative/generated/gamma-prompts.md`
   - **Prompt B (Input Text):** Business context + brand guidelines + global rules + specific shot description
6. **Assembly** — combine images + copy overlays using templates
7. **QC checklist** (see below)

#### Route B: Content Visual (infographics, diagrams, frameworks)

1. Analyze content → determine visual type (framework, process, matrix, comparison, etc.)
2. Extract elements: title, sections, labels, relationships
3. Load brand tokens → generate native SVG or HTML with exact brand values, using the approved tokens/templates
4. **QC checklist**

#### Route C: Multi-Channel Campaign

1. Create unified creative brief
2. Per-channel production (adapt copy to channel voice from brand-guide overrides)
3. Select template per channel, produce via Route A or B
4. **Batch QC** — cross-channel consistency

---

### Step 4: Quality Control (All Routes)

Mandatory checklist:

- [ ] All colors match tokens.json exactly (no approximations)
- [ ] Typography matches type scale (correct fonts, weights, sizes)
- [ ] Textures applied to all surfaces (no flat fills)
- [ ] Logo placed correctly per brand-guide
- [ ] Contrast ratios meet WCAG AA
- [ ] No anti-pattern violations
- [ ] Asset dimensions match platform specs
- [ ] CTA uses brand button style
- [ ] Copy is direct, action-oriented, no banned phrases

## Non-Negotiable Production Rules

1. **Always load entity context first** — never produce from brand profile alone
2. **Minimum 30 ad copies per batch** (headline + subheadline pairs)
3. **Two prompts per Gamma call** — Image Style (locked) + Input Text (per shot)
4. **Gamma is a visual factory** — NEVER send copy for text generation
5. **30-50 shot descriptions per shot list** (separate analysis step)
6. **Copy is TEXT OVERLAY** — never generated inside images
7. **Use exact token values** — no "close enough" colors or fonts
8. **Native SVG always** — real `<text>`, `<rect>`, `<pattern>`, `<filter>` elements

## Quality Standard

- Never invent a new visual system during production.
- Keep text as editable overlay or native vector text where possible.
- Use exact brand values rather than approximations.
- Make the production log clear enough for another teammate to reproduce the work.

## Output

- Assets saved to `{brain}/creative/output/{campaign-name}/`
- Production log (`{brain}/creative/output/{campaign-name}/production-log.md`): what was generated, tools used, prompts used — plus prompt notes and source files

## After Production

Distribute via the `content-campaign`/distribution flow (legacy: `/cmo/distribution/publish`) or manually upload to platforms.

## Tool Contracts

- `native_svg_generation`
- `optional_image_generation_prompting` (Gamma, per the two-prompt rule above)

## Adaptation Notes

- Codex is best for SVG/HTML asset generation and file organization.
- ChatGPT is useful for creative briefing, copy exploration, and campaign direction.

## Relationship to content-produce

`content-produce` (from `.claude/commands/cmo/content/produce.md`) owns the written-content pipeline: briefs, article drafting, content QC, article images, and Ghost/Publer publishing handoff. `creative-produce` owns brand-system visual production from the creative foundation (tokens, components, templates, locked Gamma prompts). Overlap: both can generate content visuals/images and both write a production log; when a written article needs branded infographics or diagrams, Route B here is the producer and `content-produce` is the consumer. Keep the ids distinct.
