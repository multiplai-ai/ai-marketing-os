---
name: research
description: 'Visual research & competitive analysis: harvest competitor and aspirational brand references as code (HTML/Tailwind/SVG), analyze visual patterns, and synthesize structured research that feeds the creative foundation.'
---

# Research

Visual research & competitive analysis: harvest competitor and aspirational brand references as code (HTML/Tailwind/SVG), analyze visual patterns, and synthesize structured research that feeds the creative foundation.

> Core skill canon (Phase 4). Merged from .claude/commands/cd/research.md (rich) + skills-core/skills/creative/research.md (portable stub) on 2026-07-02.

Legacy adapter: previously invoked as the `/cd/research` command via `.claude/commands/cd/research.md`; that path is now an adapter, not the canonical mechanism. The stub also registered an MCP adapter at `products/organization-skills-mcp/skills/creative/research.md`.

**Goal:** Build a visual research foundation that shows what the market looks like, what the brand should avoid, and where visual differentiation is available.

**When to use:** First stage of the Creative Director suite. Run this before `/cd/mood`.

**Prerequisites (soft — extract what's available, proceed with assumptions if missing):**
- `{brain}/strategy/discovery-intake.md`
- `{brain}/strategy/positioning-strategy.md`
- `{brain}/strategy/icp-personas.md`
- `{brain}/strategy/brand-strategy.md`

---

## Inputs

1. **Entity name** (required) — e.g., "organization", "Acme Health"
2. **Competitor URLs** (user provides) — live websites to analyze
3. **Aspirational brand references** (URLs or descriptions) — brands outside the space whose visual approach is worth studying
4. **Anti-references** (what to avoid) — "don't look like X"
5. **Screenshots or mood board links** (optional) — any pre-collected reference material

**Tool contracts (from portable stub):** `optional_web_fetch`, `optional_screenshot_capture` — WebFetch and screenshot capture are used when available; the skill degrades gracefully without them.

---

## Workflow

### Step 1: Resolve the Brain

Identify which entity brain this research belongs to and set `{brain}` to that entity's brain root (per the brain schema, spec §3). Create the `{brain}/creative/` workspace if it doesn't exist.

> Legacy (pre-Phase 4 workspace layout): the original command resolved an `{entity-dir}` by checking `brands/{name}/` first (lowercase, slugified), then `clients/{name}/`, then `products/{name}/`, and consulted `WORKSPACE.yaml` for the entity registry when ambiguous. Under the brain schema those paths map to `{brain}`.

Confirm with user: "Working in `{brain}/creative/` — correct?"

### Step 2: Load CMO Strategy Context

Read available strategy artifacts from `{brain}/strategy/`:

| Artifact | Extract | Used For |
|----------|---------|----------|
| `discovery-intake.md` | Business context, customer language, competitors mentioned | Framing the visual research |
| `positioning-strategy.md` | Positioning anchor, differentiation, competitive set | Knowing what to differentiate FROM |
| `icp-personas.md` | Target audience, their sophistication, their world | Informing visual taste level |
| `brand-strategy.md` | Voice, personality, tone attributes | Connecting visual feel to verbal identity |

**If any artifacts are missing:**
- Note explicitly which are missing and what assumptions you're making
- Example: "No positioning strategy found. Assuming differentiation needs are general — will revisit after `/cd/mood`."
- Do NOT stop. Proceed with what's available.

### Step 3: Collect References

If the user hasn't provided URLs yet, ask:

```
I need reference URLs to analyze. Please provide:

1. COMPETITOR SITES (2-5)
   Direct competitors — the brands your audience is comparing you to.
   → URLs:

2. ASPIRATIONAL REFERENCES (2-3)
   Brands outside your space whose visual approach you admire.
   Not "I want to look like them" — "I like how they FEEL."
   → URLs or descriptions:

3. ANTI-REFERENCES (optional)
   Anything you explicitly don't want to look like.
   → URLs or descriptions:
```

Also gather any screenshots or mood board links the user already has on hand.

**If user provides no URLs at all:** Do not proceed without at least 2-3 competitor sites. Push back: "I need at least 2 competitor URLs to establish a visual baseline. Who are your closest competitors?"

### Step 4: Create Directory Structure

Create the following directories (if they don't exist):

```
{brain}/creative/
{brain}/creative/references/
{brain}/creative/references/competitors/
{brain}/creative/references/aspirational/
{brain}/creative/references/screenshots/
```

### Step 5: Automated Baseline Analysis

For EACH competitor and aspirational URL, use WebFetch to pull and analyze the site. Extract and document:

| Dimension | What to Look For |
|-----------|-----------------|
| **Color palette** | Primary, secondary, accent colors. Background treatment. Dark vs light mode. Monochrome vs multi-color. |
| **Typography** | Headline fonts (serif, sans, display). Body fonts. Weight usage. Size hierarchy. Letter-spacing patterns. |
| **Spacing & grid** | Dense vs spacious. Fixed grid vs organic. Padding ratios. Whitespace philosophy. |
| **Layout patterns** | Hero approach. Card systems. Sections vs continuous scroll. Asymmetry vs symmetry. |
| **Button styles** | Border-radius (pill vs square vs rounded). Fill vs outline vs ghost. CTA language style. |
| **Imagery approach** | Photography vs illustration vs abstract. People vs objects vs diagrams. Crop style. |
| **Texture & depth** | Flat vs layered. Shadows vs no shadows. Grain, noise, paper textures. Gradients. |
| **Motion & interaction** | Animation cues, hover behavior, scroll effects, interaction personality. |
| **Trust & client patterns** | Logos, testimonials, stats, certifications — how credibility is signaled. |
| **Category conventions** | Patterns that read as "expected" for this category — the table stakes. |
| **Overall energy** | Corporate vs casual. Technical vs warm. Minimal vs maximal. Restrained vs expressive. |

**Per-site output format:**

```markdown
### [Site Name] — [URL]

**Category:** Competitor / Aspirational
**First impression:** [2-3 word gut reaction to the visual feel]

**Color:** [Description + extracted hex values where possible]
**Typography:** [Font names if identifiable, weight/size patterns]
**Spacing:** [Dense/moderate/spacious, grid structure]
**Layout:** [Key patterns — hero type, section structure, card usage]
**Buttons:** [Shape, fill, style]
**Imagery:** [Type, treatment, subjects]
**Texture/Depth:** [Flat/layered, shadow/no shadow, effects]
**Motion/Trust:** [Interaction cues, client/credibility patterns — if observable]
**Energy:** [Overall feel in 3-5 descriptors]

**What works well:** [1-3 specific things worth noting]
**What to avoid:** [1-2 things that don't align with this brand's needs]
```

### Step 6: Save Harvested Code

If WebFetch captures any usable HTML, Tailwind, or SVG code from reference sites, save them as individual files:

- **Competitor code** → `{brain}/creative/references/competitors/{site-name}-{element}.html`
- **Aspirational code** → `{brain}/creative/references/aspirational/{site-name}-{element}.html`

Add a comment header to each file:

```html
<!-- Source: {URL} -->
<!-- Captured: {date} -->
<!-- Element: {what this is — hero section, nav, card grid, etc.} -->
<!-- Notes: {why this is worth keeping} -->
```

**Save code snippets, not screenshots.** Code is reusable; screenshots are dead ends.

### Step 7: Manual Enrichment Checkpoint

After automated analysis, prompt the user for additional references:

```
ENRICHMENT CHECKPOINT

Automated analysis complete. If you have additional references, add them now:

- SuperDesign Chrome ext grabs (clean Tailwind HTML)
- SVG Gobbler grabs (SVGs from reference sites)
- CSS Peeper grabs (color palettes, font stacks)
- Any other screenshots, PDFs, or code snippets

Save files directly to:
  {brain}/creative/references/competitors/
  {brain}/creative/references/aspirational/
  {brain}/creative/references/screenshots/

When ready, say "continue" and I'll synthesize everything.
```

Wait for user confirmation before proceeding.

### Step 8: Synthesize Research

Analyze ALL references (automated + manually added) and synthesize findings across these dimensions:

**8.1 Visual Pattern Analysis**
- What patterns repeat across competitors? (This is the category baseline — the table stakes.)
- Which of those patterns are overused? (Candidates to subvert.)
- What are the whitespace and density norms for the category?
- What patterns repeat across aspirational brands? (This is the aspiration target.)
- Where do competitors converge? (Opportunities to differentiate by breaking convention.)

**8.2 Color Trends**
- Dominant palette families across the competitive set
- Color temperature (warm vs cool)
- Background approaches (white, dark, colored, textured)
- Accent usage (how many brands use a single accent vs multi-color)

**8.3 Typography Trends**
- Serif vs sans-serif dominance
- Display/decorative font usage
- Weight distribution (heavy headline + light body vs uniform)
- Monospace or technical font presence

**8.4 Texture & Depth Patterns**
- Flat design prevalence
- Shadow/elevation usage
- Grain, noise, paper texture usage
- Gradient approaches

**8.5 Differentiation Opportunities**
Map visual patterns back to business differentiation from CMO strategy:
- "If positioning says 'we're the human alternative to automated tools,' what visual patterns reinforce humanity vs automation?"
- "If the competitive set is all dark + techy, is there an opportunity in light + warm?"
- "What visual conventions can we break without losing category credibility?"

**8.6 Anti-Patterns & Risks**
From user-provided anti-references AND from the competitive analysis:
- What patterns would make this brand blend in rather than stand out?
- What approaches conflict with the brand personality?
- What risks to avoid — moves that would cost category credibility or trust?

### Step 9: CHECKPOINT — Present Research Synthesis

Present the full synthesis to the user for review. Format:

```
RESEARCH SYNTHESIS — {Entity Name}

Here's what I found across {N} competitor and {N} aspirational references.

[Full synthesis from Step 8]

Does this capture the landscape accurately?
Anything to add, correct, or re-weight before I write the artifact?
```

Wait for user approval before writing the final artifact.

### Step 10: Write Output Artifact

Save the complete research document to `{brain}/creative/visual-research.md`.

---

## Output Artifact

**Save to:** `{brain}/creative/visual-research.md`

**Structure:**

```markdown
---
title: Visual Research — {Entity Name}
created: {YYYY-MM-DD}
status: complete
entity: {entity-name}
competitors_analyzed: [{list}]
aspirational_analyzed: [{list}]
anti_references: [{list}]
cmo_context_loaded: [discovery, positioning, icp, brand-strategy — or "missing"]
---

# Visual Research — {Entity Name}

## Research Overview

**Objective:** Establish the visual landscape for {entity name} — what competitors look like, what aspirational brands feel like, and where the differentiation opportunity lives.

**CMO Context Used:**
- Positioning: {summary or "not available"}
- ICP: {summary or "not available"}
- Brand personality: {summary or "not available"}

**Assumptions (if CMO context was incomplete):**
- {List any assumptions made due to missing strategy docs}

---

## Competitor Analysis

### {Competitor 1 Name} — {URL}
{Per-site analysis from Step 5}

### {Competitor 2 Name} — {URL}
{Per-site analysis from Step 5}

[...repeat for all competitors]

---

## Aspirational References

### {Reference 1 Name} — {URL}
{Per-site analysis from Step 5}

[...repeat for all aspirational references]

---

## Visual Pattern Analysis

### Category Baseline (What Competitors Share)
{Patterns that repeat across the competitive set — this is what "default" looks like}

### Aspiration Patterns (What We Admire)
{Patterns from aspirational brands that could elevate this brand above the baseline}

---

## Color Trends
{From Step 8.2}

## Typography Trends
{From Step 8.3}

## Texture & Depth Patterns
{From Step 8.4}

---

## Differentiation Opportunities
{From Step 8.5 — connected back to business positioning}

## Anti-Patterns (What to Avoid)
{From Step 8.6}

---

## Raw Reference Index

| # | Name | URL | Type | Key Takeaway |
|---|------|-----|------|-------------|
| 1 | {name} | {url} | Competitor | {one-line} |
| 2 | {name} | {url} | Aspirational | {one-line} |
| 3 | {name} | {description} | Anti-reference | {one-line} |

## Harvested Code Files

| File | Source | Element | Location |
|------|--------|---------|----------|
| {filename} | {site} | {what it is} | references/competitors/ |

---

## Next Step

Run `/cd/mood` to create the visual direction from this research.
```

---

## Quality Checklist

Before finalizing, verify:

- [ ] At least 2 competitor sites analyzed with WebFetch
- [ ] Color, typography, spacing, layout, buttons, imagery, texture all covered per site
- [ ] Differentiation opportunities connect back to business positioning (not just "be different")
- [ ] Anti-patterns are specific (not just "avoid being boring")
- [ ] Harvested code files saved with source headers
- [ ] User approved the synthesis before the final artifact was written
- [ ] Output saved to `{brain}/creative/visual-research.md`
- [ ] Directory structure created under `{brain}/creative/references/`

**Quality standard (from portable stub):**
- Separate objective pattern analysis from taste opinions.
- Connect visual recommendations back to strategy.
- Make the next mood-direction step (`/cd/mood`) easier.

---

## Anti-Patterns (Never Do)

**DON'T:**
- Skip WebFetch analysis and just describe sites from memory
- Save screenshots instead of code — code is reusable, screenshots are dead ends
- Analyze visual patterns in isolation from business strategy
- Present "differentiation" that's just aesthetic preference without strategic rationale
- Proceed without at least 2 competitor URLs
- Write the artifact without user checkpoint approval

**DO:**
- Extract specific hex values, font names, spacing patterns — concrete data, not vibes
- Map every visual observation back to "so what does this mean for differentiation?"
- Save reusable code with clear source attribution
- Ask for manual enrichment — user often has chrome extension grabs ready
- Note assumptions explicitly when CMO strategy docs are missing

---

## Quick Actions

After running this skill:

- "Add more competitors" -> Re-run Steps 5-9 with additional URLs, append to artifact
- "Deep dive on {site}" -> Expanded analysis of one reference
- "Compare {site A} vs {site B}" -> Side-by-side visual comparison
- "What should I grab with SuperDesign?" -> Specific elements to harvest from identified sites

**Next step:** Run `/cd/mood` to create the visual direction from this research.

---

## Adaptation Notes

- Codex can organize local research artifacts and screenshots.
- ChatGPT can help synthesize reference sets when users upload images or links.
