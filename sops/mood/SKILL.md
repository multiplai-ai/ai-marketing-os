---
name: mood
description: 'Mood board and visual direction skill: turn visual research into 2-3 mood concepts and an approved mood direction — defining feel, energy, texture, and composition, but NOT colors or fonts (those come in the brand-guide step) — plus tool-agnostic AI image prompts.'
---

# Mood

Mood board and visual direction skill: turn visual research into 2-3 mood concepts and an approved mood direction — defining feel, energy, texture, and composition, but NOT colors or fonts (those come in the brand-guide step) — plus tool-agnostic AI image prompts.


Legacy adapter: previously invoked as the `/cd/mood` command via `.claude/commands/cd/mood.md`; that path is now an adapter, not the canonical mechanism. A second adapter existed at `products/organization-skills-mcp/skills/creative/mood.md` (MCP skill).

**Goal:** Select the brand's visual feel before making concrete palette, typography, or component decisions.

---

## Prerequisites

**HARD BLOCK:** `{brain}/creative/visual-research.md` must exist.
→ If missing: STOP. Say "Run the research skill (`/cd/research`) first to build the visual research foundation."

> Stub exception (portable contexts): the hard block may be relaxed only if the user explicitly wants a fast exploratory pass without visual research. In the core canon, the hard block is the default.

**Soft (load if available):**
- `{brain}/strategy/brand-strategy.md` — voice and personality traits

**Dependencies:** research (produces the visual research artifact this skill consumes).

## Input / Output Contract

**Inputs:**

1. **Entity name** (required) — e.g., "organization", "Acme Health"
2. visual_research_artifact — `{brain}/creative/visual-research.md`
3. brand_strategy_artifact — `{brain}/strategy/brand-strategy.md` (optional)
4. user_preferences (checkpoint selections and hybridization requests)

**Outputs:**

- `{brain}/creative/mood-direction.md`

---

## Workflow

### Step 1: Resolve Entity Directory ({brain})

Map entity name to the entity's brain directory:
- Check `brands/{name}/` first, then `clients/{name}/`, then `products/{name}/`
- Set `{brain}` to the resolved path
- Verify `{brain}/creative/visual-research.md` exists — if not, STOP

### Step 2: Load Context

Read in order:
1. `{brain}/creative/visual-research.md` — competitive analysis, pattern findings
2. `{brain}/creative/references/` — scan harvested code files for structural patterns
3. `{brain}/strategy/brand-strategy.md` (if exists) — extract personality traits, voice descriptors

### Step 3: Extract Brand Personality

From brand strategy (or ask user if missing):
- What 3-5 personality traits need visual expression?
- What mood should someone feel when they encounter this brand? (emotional response)
- What's the brand's "energy" — calm authority? bold disruption? warm expertise?
- Competitive contrast — where must this brand feel different from its competitors?
- Visual constraints — any hard limits the mood must respect?

### Step 4: Generate 2-3 Mood Concepts

Each concept includes:

| Dimension | Description |
|-----------|-------------|
| **Mood Name** | 2-3 words capturing the essence |
| **Feel / Energy** | 3-5 descriptors (warm, technical, editorial, etc.) |
| **Visual Metaphor** | What real-world thing does this look/feel like? |
| **Texture Direction** | Smooth vs rough, flat vs layered, matte vs glossy |
| **Composition Approach** | Dense vs spacious, grid vs organic, symmetrical vs dynamic |
| **Imagery Direction** | Photographic vs illustrated vs diagrammatic vs abstract |
| **Emotional Temperature** | Warm vs cool, approachable vs authoritative |
| **"Inspired by" References** | Which harvested references from research inform this |
| **Differentiation** | What makes this different from competitors (from research) |

**CRITICAL RULE: No colors. No fonts.** Those decisions come in the brand-guide step (`/cd/brand-guide`). Mood is about FEEL, not specifics. If you catch yourself writing hex codes or font names, stop.

### Step 5: CHECKPOINT — Present Concepts

Present all 2-3 concepts side by side. Ask user:
- "Which concept resonates? Or should I hybridize elements from multiple?"
- User selects one or describes a hybrid

### Step 6: Expand Selected Direction

Build out the chosen concept into a full mood direction:

1. **Detailed feel description** — 2-3 paragraphs capturing the visual experience
2. **Composition rules** — alignment, whitespace, hierarchy, grid approach
3. **Texture approach** — how textured vs clean, layering order, depth
4. **Imagery direction** — subjects, treatments, what to avoid
5. **"Is / Is Not" table** — clear boundaries

| This IS | This IS NOT |
|---------|-------------|
| (from the mood) | (opposite) |

6. **AI image prompts** — Tool-agnostic positive and negative keyword lists that capture this mood. These are mood-level prompts, not brand-specific — they'll be refined in the brand-guide step.
7. **Connection to strategy** — How this mood maps to positioning anchor, brand personality, and competitive differentiation, and the implications for the next brand-guide step

### Step 7: CHECKPOINT — Mood Direction Approved

Present the full mood direction. User confirms or requests adjustments.

## Output

Save to `{brain}/creative/mood-direction.md` with sections:
- Mood Direction Name
- Feel & Energy
- Visual Metaphor
- Composition Rules
- Texture Approach
- Imagery Direction
- What This Is / What This Is Not
- AI Prompt Keywords (Positive)
- AI Prompt Keywords (Negative)
- Connection to Strategy
- Reference Mapping

## Quality Standard

- Mood describes feel, not implementation.
- Concepts should be meaningfully different.
- The approved direction should make later color and typography choices easier.

## Anti-Patterns

- Never include specific colors (hex codes, color names beyond mood descriptors like "warm" or "cool")
- Never include specific fonts
- Never copy a reference directly — "inspired by" means differentiated adaptation
- Never skip the "Is / Is Not" table — it's the most useful boundary-setting tool
- Never skip the strategy connection — mood must tie back to business positioning

## Adaptation Notes

- ChatGPT works well for collaborative mood exploration.
- Codex is useful when mood work needs to be stored alongside repo strategy artifacts.

## Next Step

→ Run the brand-guide skill (`/cd/brand-guide`) to lock in colors, typography, and design tokens.
