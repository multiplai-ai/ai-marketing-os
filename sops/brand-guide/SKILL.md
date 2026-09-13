---
name: brand-guide
description: Lock in every visual decision — colors, typography, textures, buttons, imagery, AI prompts — and compile into both a human-readable brand guide and machine-readable W3C design tokens.
---

# Brand Guide

Lock in every visual decision — colors, typography, textures, buttons, imagery, AI prompts — and compile into both a human-readable brand guide and machine-readable W3C design tokens.


Legacy adapters: previously invoked as the `/cd/brand-guide` command via `.claude/commands/cd/brand-guide.md`, and exposed as an MCP skill at `products/organization-skills-mcp/skills/creative/brand-guide.md`; those paths are now adapters, not the canonical mechanism.

**Goal:** Lock the visual system into human-readable guidelines and machine-readable tokens. 7 sub-stages with checkpoints. Produces brand-guide.md (human-readable) + tokens.json (W3C DTCG machine-readable). Runs translation scripts for CSS, Tailwind, Gamma, Pencil, Figma.

---

## Prerequisites

**HARD BLOCK:** `{brain}/creative/mood-direction.md` must exist.
→ If missing: STOP. Say "Run `/cd/mood` first." (Skill dependency: `mood`.)

**Soft (load if available):**
- `{brain}/creative/visual-research.md` + `{brain}/creative/references/`
- `{brain}/strategy/brand-strategy.md`

## Inputs

1. **Entity name** (required)
2. Mood direction artifact (hard requirement, see above)
3. Visual research artifact (soft)
4. Brand strategy artifact (soft)
5. Implementation targets (which translation outputs matter: CSS, Tailwind, Gamma, Figma, Pencil)

## Workflow

### Step 1: Resolve & Load

1. Resolve entity name to its `{brain}` directory
2. Verify `{brain}/creative/mood-direction.md` exists
3. Read: mood-direction.md, visual-research.md, references/, brand-strategy.md (if exists)

### Sub-Stage A: Colors

1. Generate 2-3 palette options, each with:
   - **Primary palette** (4-5 colors): background, text, text-secondary, darkest, surface
   - **Extended palette** (5-8 colors): accent, callout, border, hover, status colors
   - **Contrast ratios** (WCAG AA minimum, AAA preferred)
   - **Color rules**: what's allowed, what's not, opacity, gradient policy
2. Present with hex codes, RGB, usage rules, and contrast checks
3. **CHECKPOINT: User selects palette** — ask for approval before moving on

### Sub-Stage B: Typography

1. Generate 2-3 pairings, each with:
   - Display/headline font (weight, size range, source)
   - Body font (weight, size range, source)
   - Mono/code font (weight, size range, source)
   - Full type scale: Display, H1, H2, H3, H4, Body, Body Small, Caption, Label, Code
   - Line heights, letter spacing, max line length
   - Font sources (Google Fonts URL, license, Canva/Figma availability, fallback stack)
2. **CHECKPOINT: User selects typography**

### Sub-Stage C: Textures & Surfaces

1. Define surface treatments from mood direction:
   - List each texture: name, description, opacity range, implementation (SVG `<pattern>`, `<filter>`, CSS)
   - Surface depth policy: flat vs layered, shadow approach
   - Rule: "every surface textured" vs "selective texture"
   - Layering order: base color → texture → content
2. User reviews

### Sub-Stage D: Buttons & Interactive Elements

1. Define for Primary, Secondary, Ghost CTAs:
   - Background, text color, font, font-style, font-weight, font-size
   - Padding, border-radius, border
   - Hover, active, focus, disabled states
2. Shape language: border-radius, shadow, border-width, border-color

### Sub-Stage E: Imagery Rules

1. Subjects, composition, color treatment, avoid list
2. Icon style: stroke weight, caps, sizes, color rules, icon set
3. Logo usage: placement, minimum size, clear space, dark/light variants

### Sub-Stage F: Voice-Visual Alignment

1. Map each brand voice trait to visual execution
2. Channel-specific overrides: LinkedIn, Instagram, Twitter, Email, Website, Ads, Video, PDF

### Sub-Stage G: AI Prompt Generation

1. Generate **locked prompts** (stored permanently, loaded by `/cd/produce`):
   - **Gamma Image Style** — positive + negative keywords, visual rules
   - **Midjourney template** — style keywords, parameters
   - **General AI image prompt** — tool-agnostic
2. **CHECKPOINT: User locks AI prompts**

### Final Compilation

1. Write `{brain}/creative/brand-guide.md` — human-readable, all sections
2. Write `{brain}/creative/tokens.json` — W3C DTCG format with all values (use semantic names where possible):
   - `brand` (name, tagline, personality)
   - `color` (primary, accent, status — each token has `$value`, `$type`, `$description`)
   - `typography` (display, h1-h4, body, bodySmall, caption, label, code — each with fontFamily, fontWeight, fontSize, lineHeight, letterSpacing)
   - `spacing` (base, scale array)
   - `shape` (borderRadius, cardRadius, borderWidth, borderColor, shadow)
   - `button` (primary, secondary, ghost — full specs)
   - `texture` (each texture with opacity, description, implementation)
   - `imagery` (style, subjects, avoid, positivePrompt, negativePrompt, gammaImageStyle)
   - `icon` (style, strokeWeight, caps, sizes, color)
   - `logo` (type, minimumWidth, clearSpace, placement)
   - `layout` (maxLineLength, contentSafeZone, margins, sectionPadding)

3. Run translation scripts (optional tool contract — run per implementation targets):
```bash
python3 tools/tokens_to_css.py {brain}/creative/tokens.json -o {brain}/creative/generated/variables.css
python3 tools/tokens_to_tailwind.py {brain}/creative/tokens.json -o {brain}/creative/generated/tailwind.config.js
python3 tools/tokens_to_gamma.py {brain}/creative/tokens.json -o {brain}/creative/generated/gamma-prompts.md
python3 tools/tokens_to_figma.py {brain}/creative/tokens.json -o {brain}/creative/generated/figma-tokens.json
python3 tools/tokens_to_pencil.py {brain}/creative/tokens.json -o {brain}/creative/generated/pencil-variables.json
```

## Output

- `{brain}/creative/brand-guide.md`
- `{brain}/creative/tokens.json`
- `{brain}/creative/generated/` — CSS, Tailwind, Gamma, Figma, Pencil configs

## Quality Standard

- Every major visual decision should trace back to mood and strategy.
- Tokens should be implementation-ready.
- Accessibility and contrast should be documented.

## Anti-Patterns

- Never skip a sub-stage checkpoint
- Never use approximate colors — exact hex codes only
- Never generate AI prompts that include text/copy — visual prompts only
- Anti-patterns section in brand-guide.md is mandatory

## Adaptation Notes

- Codex can write token files and translation artifacts.
- ChatGPT can help stakeholders choose between visual options.

## Next Step

→ Run `/cd/components` to build the SVG component library.
