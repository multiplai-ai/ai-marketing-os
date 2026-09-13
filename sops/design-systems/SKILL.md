---
name: design-systems
description: Build comprehensive, production-ready design systems through a staged, collaborative workflow — translate brand voice and positioning into an approved mood direction, locked color and typography, a tiered token architecture, and implementation-ready component guidance.
---

# Design Systems

Build comprehensive, production-ready design systems through a staged, collaborative workflow — translate brand voice and positioning into an approved mood direction, locked color and typography, a tiered token architecture, and implementation-ready component guidance.


Legacy adapters: previously invoked as the `/design-systems` command via `.claude/commands/cmo/strategy/design-systems.md`, and exposed as an MCP skill via `products/organization-skills-mcp/skills/strategy/design-systems.md`. Those paths are now adapters, not the canonical mechanism.

**When to use:**

- After brand strategy is defined. This skill translates brand voice and positioning into a complete visual design system.
- Before creating branded visual assets, landing pages, or UI systems.
- When visual direction needs to become reusable implementation guidance.

**Prerequisites:** Run `/brand-strategy` first, or have brand context ready.

---

## Input / Output Contract

**Inputs:**

- brand_strategy_artifact — `{brain}/strategy/brand-strategy.md` (or equivalent brand inputs)
- positioning_artifact — `{brain}/strategy/positioning-strategy.md` (positioning and competitive context)
- visual_references — reference brands or mood boards
- anti_references — visual styles to avoid
- implementation_targets — CSS, Tailwind, Figma, or content templates

**Outputs (staged strategy artifacts, saved under `{brain}/strategy/`):**

- `{brain}/strategy/mood-direction.md`
- `{brain}/strategy/palette-typography.md`
- `{brain}/strategy/design-system.md`
- `{brain}/strategy/design-tokens.json`
- `{brain}/strategy/design-tokens.css`
- `{brain}/strategy/tailwind.extend.js` (if applicable)
- `.tmp/visuals/palette-preview-*.html` and `.tmp/visuals/style-tile-final.html` (working previews)

> Path note: legacy invocations saved these artifacts to `projects/[project-name]/...` (rich command) or `{workspace}/projects/{project}/...` (portable stub). Canonical location is now `{brain}/strategy/`. If one entity genuinely needs multiple design systems, namespace them as `{brain}/strategy/design-systems/<project>/...`.

**Tool contracts (optional capabilities, not required steps):** optional_html_preview, optional_token_export.

---

## Philosophy

This skill produces **opinionated, production-ready design systems** — not generic templates.

**Core principles:**

1. **Staged decision-making.** Agree on feel before colors. Lock colors before building tokens. Each checkpoint prevents wasted work. Separate decisions by stage: agree on feel before choosing colors, then lock palette and typography before building tokens and components.

2. **Collaborative not one-shot.** Generate options at each stage, get approval, then proceed. Never bulldoze through to implementation.

3. **Token architecture with tiers.** Primitives (raw values) → Semantic (intent) → Component (specific usage). This structure enables maintainability and theming.

4. **Implementation-ready outputs.** Every decision maps to usable code: CSS custom properties, Tailwind config, or component specs. Nothing stays abstract.

---

## Staged Workflow

```
/design-systems          → Stage 1: Mood direction (full flow start)
/design-systems palette  → Stage 2: Color & typography (requires mood approval)
/design-systems build    → Stage 3: Full system build (requires palette approval)
/design-systems extract  → Extract tokens from a live URL → skip to Stage 3
/design-systems status   → Show current stage and what's locked
```

> **Shortcut — extract from URL:** `/design-systems extract [URL]` runs `/design-extract`,
> which reverse-engineers a live site's colors, typography, and spacing, generates
> `palette-typography.md` automatically, and feeds directly into Stage 3.

### The Three Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│  Stage 1: INSPIRATION                                               │
│  ─────────────────────                                              │
│  • Collect reference inputs (brands, mood boards, anti-references)  │
│  • Generate 2-3 mood concepts (feel/energy only, NO colors)         │
│  • User approves a mood direction                                   │
│  • Output: mood-direction.md                                        │
│                                                                     │
│  ↓ CHECKPOINT: Mood approved                                        │
├─────────────────────────────────────────────────────────────────────┤
│  Stage 2: PALETTE                                                   │
│  ───────────────────                                                │
│  • Based on approved mood, propose 2-3 color palette options        │
│  • Propose 2-3 typography pairings                                  │
│  • Generate simple preview HTML for each option                     │
│  • User selects palette AND typography                              │
│  • Output: palette-typography.md                                    │
│                                                                     │
│  ↓ CHECKPOINT: Palette and typography locked                        │
├─────────────────────────────────────────────────────────────────────┤
│  Stage 3: SYSTEM BUILD                                              │
│  ─────────────────────                                              │
│  • Generate full color scales (50-900) from locked colors           │
│  • Build complete token architecture                                │
│  • Spec all components with states                                  │
│  • Generate implementation starters (CSS, Tailwind)                 │
│  • Output: design-system.md + code artifacts                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

# Entry Point: Status Check

When invoked with `status` or at the start of any invocation:

### Check Project State

```
1. Look for: {brain}/strategy/mood-direction.md
   - If found with status: approved → Stage 1 complete
   - If not found → Stage 1 needed

2. Look for: {brain}/strategy/palette-typography.md
   - If found with status: approved → Stage 2 complete
   - If not found → Stage 2 needed (after Stage 1)

3. Look for: {brain}/strategy/design-system.md
   - If found → Stage 3 complete
```

Resume from the latest approved stage instead of restarting.

### Status Display Template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN SYSTEM STATUS — [Project Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stage 1: Mood Direction    [✓ Complete / ○ Pending]
Stage 2: Palette & Type    [✓ Complete / ○ Pending]
Stage 3: Full System       [✓ Complete / ○ Pending]

Current stage: [Stage N]
Next action: [What to do]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# Foundation Check (All Stages)

Before any stage, load prerequisite artifacts.

### Check for Brand Strategy Artifact

Look for: `{brain}/strategy/brand-strategy.md`

**If found:**
Extract:
- Voice character and tone attributes
- Brand personality traits
- Main message and USPs
- "We say / We don't say" guidelines
- Target emotional response
- Category expectations and visual constraints

**If not found:**
Display: "I need brand strategy first. Please run `/brand-strategy` to define voice and messaging, or provide brand context manually."

If user wants to proceed without:
Ask for minimum inputs:
- 3-5 adjectives describing the brand
- Target emotional response
- Reference brands (2-4 for visual inspiration)

### Check for Positioning Artifact

Look for: `{brain}/strategy/positioning-strategy.md`

**If found:**
Extract:
- Primary anchor (what you're positioned against)
- Core differentiation
- Category context

---

# Stage 1: Inspiration & Mood

**Goal:** Agree on the visual feel before making any concrete decisions about colors or fonts.

**Entry:** `/design-systems` (fresh start)

### 1.1 Collect Reference Inputs

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAGE 1: MOOD EXPLORATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let's establish the visual feel before committing to colors.

1. REFERENCE BRANDS (2-4, any industry)
   Who has the visual vibe you want? Not competitors —
   aspirational references.

   Examples: "Stripe's clarity", "Linear's precision",
   "Notion's warmth", "Vercel's confidence"

2. MOOD BOARD LINKS (if available)
   Cosmos.so, Figma, Pinterest, Are.na collections

3. SCREENSHOTS OF SITES/APPS YOU LIKE
   Share any references that capture the feel you want

4. ANTI-REFERENCES (what to avoid)
   What visual styles should we NOT do?

   Examples: "Corporate blue", "Overly playful/startup-y",
   "Dark/gamer aesthetic", "Generic SaaS template"

5. DESIGN PHILOSOPHY (3-5 words)
   What feeling should the design evoke?

   Examples: "Bold and confident", "Calm and trustworthy",
   "Playful but professional", "Technical and precise"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 1.2 Generate Mood Concepts (2-3)

For each concept, produce ONLY feel/energy — NO specific colors or fonts yet.

**Mood Concept Template:**

```markdown
## Mood Concept [N]: [Name]

**Vibe (one sentence):**
[What energy/feeling this direction evokes]

**Reference alignment:**
[How this connects to the user's reference brands]

**Visual energy:**
- [Descriptor 1] — e.g., "Clean lines, generous whitespace"
- [Descriptor 2] — e.g., "Subtle animations, smooth transitions"
- [Descriptor 3] — e.g., "Sharp geometry, no softness"

**Shape language tendency:**
- Edges: [Sharp / Rounded / Mixed]
- Density: [Spacious / Balanced / Compact]
- Contrast: [High / Moderate / Subtle]

**Emotional keywords:**
[3-5 words that capture the feel]

**Best for:**
[What kind of brand/product this works well for]

**Avoid if:**
[When this direction would be wrong]
```

### 1.3 Mood Concept Comparison

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MOOD COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Concept 1: [Name] | Concept 2: [Name] | Concept 3: [Name] |
|--------|-------------------|-------------------|-------------------|
| Feel | [3 words] | [3 words] | [3 words] |
| Energy | [low/med/high] | [low/med/high] | [low/med/high] |
| Edges | [sharp/rounded] | [sharp/rounded] | [sharp/rounded] |
| Best for | [use case] | [use case] | [use case] |
```

### 1.4 Stage 1 Checkpoint

Ask user:
- "Which mood concept resonates most with your brand?"
- "Would you like a hybrid of any concepts?"
- "Any adjustments to the selected mood?"

**STOP and wait for approval before proceeding.**

### 1.5 Stage 1 Output

Save to: `{brain}/strategy/mood-direction.md`

```markdown
---
title: Mood Direction — [Project Name]
created: YYYY-MM-DD
status: approved
---

# Mood Direction

## Selected Concept: [Name]

**Vibe:** [One sentence description of the feel/energy]

**References:**
- [Reference 1 — what we're taking from it]
- [Reference 2 — what we're taking from it]
- [Reference 3 — what we're taking from it]

**Avoid:**
- [Anti-reference 1]
- [Anti-reference 2]

**Visual Energy:**
- [Descriptor 1]
- [Descriptor 2]
- [Descriptor 3]

**Shape Language:**
- Edges: [Sharp / Rounded / Mixed]
- Density: [Spacious / Balanced / Compact]
- Contrast: [High / Moderate / Subtle]

**Feel Keywords:** [Keyword 1], [Keyword 2], [Keyword 3], [Keyword 4]

---

*Approved: YYYY-MM-DD*
*Ready for: Stage 2 (Palette & Typography)*
```

---

# Stage 2: Color & Typography

**Goal:** Lock in the specific colors and fonts that express the approved mood.

**Entry:** `/design-systems palette` (or continues from Stage 1)

**Prerequisite:** Approved `mood-direction.md` from Stage 1

### 2.0 Prerequisite Check

```
Look for: {brain}/strategy/mood-direction.md

If NOT found or status != approved:
  Display: "Stage 2 requires an approved mood direction.
           Run /design-systems first to complete Stage 1."
  STOP

If found:
  Load mood direction context
  Proceed with Stage 2
```

### 2.1 Generate Palette Options (2-3)

Based on the approved mood, propose 2-3 color palette options. Each option should cover primary, secondary, accent, neutral, and status colors.

**Palette Option Template:**

```markdown
## Palette Option [N]: [Name]

**Rationale:**
[How this palette expresses the approved mood]

**Colors:**

| Role | Color | Hex | Why |
|------|-------|-----|-----|
| Primary | [Name] | [#hex] | [Connection to mood] |
| Secondary | [Name] | [#hex] | [Purpose] |
| Accent | [Name] | [#hex] | [Usage] |
| Surface | [Name] | [#hex] | [Background usage] |
| Text | [Name] | [#hex] | [Readability] |

**Accessibility notes:** [Contrast expectations for text-on-primary, text-on-surface; any WCAG concerns]

**Mood alignment:** [How this connects to approved feel keywords]

**Best for:** [When to choose this option]
```

### 2.2 Generate Typography Options (2-3)

Based on the approved mood, propose 2-3 typography pairings.

**Typography Option Template:**

```markdown
## Typography Option [N]: [Pairing Name]

**Rationale:**
[How this pairing expresses the approved mood]

**Fonts:**

| Role | Font | Weight | Why |
|------|------|--------|-----|
| Headings | [Font name] | [weights] | [Character/feel] |
| Body | [Font name] | [weights] | [Readability/match] |
| Mono/Code | [Font name] | [weights] | [Technical elements] |

**Shape language:**
- Border radius: [Sharp 2-4px / Moderate 6-8px / Rounded 12-16px / Pill]
- Shadow style: [None / Subtle / Moderate / Pronounced]

**Mood alignment:** [How this connects to approved feel keywords]

**Licensing:** [Free/Google Fonts / Paid / System]
```

### 2.3 Generate Preview HTML

For each palette + typography combination worth showing:

Save to: `.tmp/visuals/palette-preview-[option-name].html`

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family={{HEADING_FONT}}:wght@400;500;600;700&family={{BODY_FONT}}:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: '{{BODY_FONT}}', system-ui, sans-serif;
      background: {{BG_COLOR}};
      padding: 48px;
    }

    .preview {
      max-width: 800px;
      margin: 0 auto;
    }

    .header {
      margin-bottom: 48px;
    }

    .option-name {
      font-family: '{{HEADING_FONT}}', system-ui, sans-serif;
      font-size: 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: {{TEXT_SECONDARY}};
      margin-bottom: 8px;
    }

    .palette-name {
      font-family: '{{HEADING_FONT}}', system-ui, sans-serif;
      font-size: 32px;
      font-weight: 700;
      color: {{TEXT_PRIMARY}};
    }

    /* Color swatches */
    .colors {
      display: flex;
      gap: 16px;
      margin-bottom: 48px;
    }

    .swatch {
      width: 120px;
      height: 100px;
      border-radius: {{RADIUS}}px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 12px;
    }

    .swatch-name {
      font-size: 12px;
      font-weight: 600;
    }

    .swatch-hex {
      font-size: 11px;
      font-family: monospace;
      opacity: 0.8;
    }

    /* Typography samples */
    .typography {
      margin-bottom: 48px;
    }

    .type-h1 {
      font-family: '{{HEADING_FONT}}', system-ui, sans-serif;
      font-size: 48px;
      font-weight: 700;
      color: {{TEXT_PRIMARY}};
      margin-bottom: 16px;
      letter-spacing: -0.02em;
    }

    .type-h2 {
      font-family: '{{HEADING_FONT}}', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 600;
      color: {{TEXT_PRIMARY}};
      margin-bottom: 16px;
    }

    .type-body {
      font-size: 16px;
      color: {{TEXT_SECONDARY}};
      line-height: 1.6;
      max-width: 600px;
      margin-bottom: 24px;
    }

    /* Component samples */
    .components {
      display: flex;
      gap: 24px;
      flex-wrap: wrap;
    }

    .btn {
      padding: 12px 24px;
      border-radius: {{RADIUS}}px;
      font-size: 14px;
      font-weight: 600;
      font-family: '{{BODY_FONT}}', system-ui, sans-serif;
      cursor: pointer;
      border: 2px solid transparent;
    }

    .btn-primary {
      background: {{PRIMARY_COLOR}};
      color: {{PRIMARY_TEXT}};
    }

    .btn-secondary {
      background: transparent;
      color: {{PRIMARY_COLOR}};
      border-color: {{PRIMARY_COLOR}};
    }

    .card {
      background: {{SURFACE_COLOR}};
      border-radius: {{RADIUS_LG}}px;
      padding: 24px;
      box-shadow: {{SHADOW}};
      max-width: 300px;
    }

    .card-title {
      font-family: '{{HEADING_FONT}}', system-ui, sans-serif;
      font-size: 18px;
      font-weight: 600;
      color: {{TEXT_PRIMARY}};
      margin-bottom: 8px;
    }

    .card-text {
      font-size: 14px;
      color: {{TEXT_SECONDARY}};
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="preview">
    <div class="header">
      <div class="option-name">Palette Option</div>
      <div class="palette-name">{{PALETTE_NAME}}</div>
    </div>

    <div class="colors">
      <div class="swatch" style="background: {{PRIMARY_COLOR}}; color: {{PRIMARY_TEXT}};">
        <span class="swatch-name">Primary</span>
        <span class="swatch-hex">{{PRIMARY_COLOR}}</span>
      </div>
      <div class="swatch" style="background: {{SECONDARY_COLOR}}; color: {{SECONDARY_TEXT}};">
        <span class="swatch-name">Secondary</span>
        <span class="swatch-hex">{{SECONDARY_COLOR}}</span>
      </div>
      <div class="swatch" style="background: {{ACCENT_COLOR}}; color: {{ACCENT_TEXT}};">
        <span class="swatch-name">Accent</span>
        <span class="swatch-hex">{{ACCENT_COLOR}}</span>
      </div>
      <div class="swatch" style="background: {{TEXT_PRIMARY}}; color: {{BG_COLOR}};">
        <span class="swatch-name">Text</span>
        <span class="swatch-hex">{{TEXT_PRIMARY}}</span>
      </div>
    </div>

    <div class="typography">
      <div class="type-h1">Display Heading</div>
      <div class="type-h2">Section Heading</div>
      <div class="type-body">Body text sample demonstrating the reading experience. Good typography balances readability with personality. This pairing creates the feel we agreed on in the mood direction.</div>
    </div>

    <div class="components">
      <button class="btn btn-primary">Primary Button</button>
      <button class="btn btn-secondary">Secondary</button>
      <div class="card">
        <div class="card-title">Card Component</div>
        <div class="card-text">Sample card showing elevation, border radius, and text hierarchy in action.</div>
      </div>
    </div>
  </div>
</body>
</html>
```

### 2.4 Option Comparison Table

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PALETTE & TYPOGRAPHY OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COLOR PALETTES:

| Aspect | Option 1: [Name] | Option 2: [Name] | Option 3: [Name] |
|--------|------------------|------------------|------------------|
| Primary | [hex] | [hex] | [hex] |
| Feel | [3 words] | [3 words] | [3 words] |
| Best for | [use case] | [use case] | [use case] |

TYPOGRAPHY PAIRINGS:

| Aspect | Option A: [Name] | Option B: [Name] |
|--------|------------------|------------------|
| Heading | [Font] | [Font] |
| Body | [Font] | [Font] |
| Radius | [style] | [style] |
| Best for | [use case] | [use case] |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2.5 Stage 2 Checkpoint

Ask user:
- "Which color palette resonates most?"
- "Which typography pairing feels right?"
- "Any adjustments to the selected options?"

**STOP and wait for both selections before proceeding.**

### 2.6 Stage 2 Output

Save to: `{brain}/strategy/palette-typography.md`

```markdown
---
title: Palette & Typography — [Project Name]
created: YYYY-MM-DD
status: approved
mood-source: mood-direction.md
---

# Palette & Typography

## Color Palette

| Role | Color | Hex | Why |
|------|-------|-----|-----|
| Primary | [Name] | [#hex] | [Connection to mood] |
| Secondary | [Name] | [#hex] | [Purpose] |
| Accent | [Name] | [#hex] | [Usage] |
| Surface | [Name] | [#hex] | [Background usage] |
| Text Primary | [Name] | [#hex] | [Main text] |
| Text Secondary | [Name] | [#hex] | [Supporting text] |

## Typography

| Role | Font | Weights | Why |
|------|------|---------|-----|
| Headings | [Font name] | [400, 600, 700] | [Character/feel] |
| Body | [Font name] | [400, 500, 600] | [Readability] |
| Mono | [Font name] | [400, 500] | [Technical elements] |

## Shape Language

| Property | Value | Rationale |
|----------|-------|-----------|
| Border radius | [Xpx] | [Sharp/Rounded feel] |
| Shadow style | [Description] | [Elevation approach] |
| Spacing density | [Compact/Balanced/Spacious] | [Layout feel] |

---

*Approved: YYYY-MM-DD*
*Ready for: Stage 3 (Full System Build)*
```

---

# Stage 3: Full System Build

**Goal:** Generate the complete design system from locked decisions.

**Entry:** `/design-systems build` (or continues from Stage 2)

**Prerequisite:** Approved `palette-typography.md` from Stage 2

### 3.0 Prerequisite Check

```
Look for: {brain}/strategy/palette-typography.md

If NOT found or status != approved:
  Display: "Stage 3 requires approved palette and typography.
           Run /design-systems palette first to complete Stage 2."
  STOP

If found:
  Load palette-typography.md
  Load mood-direction.md for context
  Proceed with Stage 3
```

### 3.1 Token Architecture Build

Build the full three-tier token system based on locked palette and typography.

#### Tier 1: Primitive Tokens

Generate full color scales from the locked primary/secondary/accent colors.

```json
{
  "primitives": {
    "colors": {
      "gray": {
        "50": "#F9FAFB",
        "100": "#F3F4F6",
        "200": "#E5E7EB",
        "300": "#D1D5DB",
        "400": "#9CA3AF",
        "500": "#6B7280",
        "600": "#4B5563",
        "700": "#374151",
        "800": "#1F2937",
        "900": "#111827"
      },
      "brand": {
        "50": "{{BRAND_50}}",
        "100": "{{BRAND_100}}",
        "200": "{{BRAND_200}}",
        "300": "{{BRAND_300}}",
        "400": "{{BRAND_400}}",
        "500": "{{BRAND_500}}",
        "600": "{{BRAND_600}}",
        "700": "{{BRAND_700}}",
        "800": "{{BRAND_800}}",
        "900": "{{BRAND_900}}"
      },
      "accent": {
        "50": "{{ACCENT_50}}",
        "100": "{{ACCENT_100}}",
        "500": "{{ACCENT_500}}",
        "600": "{{ACCENT_600}}",
        "700": "{{ACCENT_700}}"
      },
      "success": {
        "50": "#ECFDF5",
        "500": "#10B981",
        "700": "#047857"
      },
      "warning": {
        "50": "#FFFBEB",
        "500": "#F59E0B",
        "700": "#B45309"
      },
      "error": {
        "50": "#FEF2F2",
        "500": "#EF4444",
        "700": "#B91C1C"
      }
    },
    "spacing": {
      "0": "0",
      "1": "4px",
      "2": "8px",
      "3": "12px",
      "4": "16px",
      "5": "20px",
      "6": "24px",
      "8": "32px",
      "10": "40px",
      "12": "48px",
      "16": "64px",
      "20": "80px",
      "24": "96px"
    },
    "typography": {
      "fontFamily": {
        "sans": "{{FONT_SANS}}, system-ui, sans-serif",
        "mono": "{{FONT_MONO}}, monospace"
      },
      "fontSize": {
        "xs": "12px",
        "sm": "14px",
        "base": "16px",
        "lg": "18px",
        "xl": "20px",
        "2xl": "24px",
        "3xl": "30px",
        "4xl": "36px",
        "5xl": "48px"
      },
      "fontWeight": {
        "normal": "400",
        "medium": "500",
        "semibold": "600",
        "bold": "700"
      },
      "lineHeight": {
        "tight": "1.25",
        "normal": "1.5",
        "relaxed": "1.75"
      },
      "letterSpacing": {
        "tight": "-0.02em",
        "normal": "0",
        "wide": "0.05em"
      }
    },
    "borderRadius": {
      "none": "0",
      "sm": "4px",
      "md": "{{RADIUS_MD}}",
      "lg": "{{RADIUS_LG}}",
      "xl": "{{RADIUS_XL}}",
      "full": "9999px"
    },
    "shadow": {
      "none": "none",
      "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
      "md": "0 4px 6px rgba(0, 0, 0, 0.07)",
      "lg": "0 10px 15px rgba(0, 0, 0, 0.1)",
      "xl": "0 20px 25px rgba(0, 0, 0, 0.15)"
    },
    "transition": {
      "fast": "150ms ease",
      "normal": "200ms ease",
      "slow": "300ms ease"
    },
    "breakpoints": {
      "sm": "640px",
      "md": "768px",
      "lg": "1024px",
      "xl": "1280px",
      "2xl": "1536px"
    }
  }
}
```

#### Tier 2: Semantic Tokens

Intent-based tokens that reference primitives.

```json
{
  "semantic": {
    "background": {
      "default": "{primitives.colors.white}",
      "surface": "{primitives.colors.gray.50}",
      "muted": "{primitives.colors.gray.100}",
      "emphasis": "{primitives.colors.brand.500}",
      "inverse": "{primitives.colors.gray.900}"
    },
    "text": {
      "primary": "{primitives.colors.gray.900}",
      "secondary": "{primitives.colors.gray.600}",
      "muted": "{primitives.colors.gray.400}",
      "inverse": "{primitives.colors.white}",
      "brand": "{primitives.colors.brand.600}",
      "link": "{primitives.colors.brand.600}",
      "linkHover": "{primitives.colors.brand.700}"
    },
    "border": {
      "default": "{primitives.colors.gray.200}",
      "muted": "{primitives.colors.gray.100}",
      "emphasis": "{primitives.colors.brand.500}",
      "focus": "{primitives.colors.brand.500}"
    },
    "interactive": {
      "default": "{primitives.colors.brand.500}",
      "hover": "{primitives.colors.brand.600}",
      "active": "{primitives.colors.brand.700}",
      "disabled": "{primitives.colors.gray.300}"
    },
    "feedback": {
      "success": "{primitives.colors.success.500}",
      "successBg": "{primitives.colors.success.50}",
      "warning": "{primitives.colors.warning.500}",
      "warningBg": "{primitives.colors.warning.50}",
      "error": "{primitives.colors.error.500}",
      "errorBg": "{primitives.colors.error.50}",
      "info": "{primitives.colors.brand.500}",
      "infoBg": "{primitives.colors.brand.50}"
    },
    "typography": {
      "display": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.5xl}",
        "fontWeight": "{primitives.typography.fontWeight.bold}",
        "lineHeight": "{primitives.typography.lineHeight.tight}",
        "letterSpacing": "{primitives.typography.letterSpacing.tight}"
      },
      "heading1": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.4xl}",
        "fontWeight": "{primitives.typography.fontWeight.bold}",
        "lineHeight": "{primitives.typography.lineHeight.tight}"
      },
      "heading2": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.3xl}",
        "fontWeight": "{primitives.typography.fontWeight.semibold}",
        "lineHeight": "{primitives.typography.lineHeight.tight}"
      },
      "heading3": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.2xl}",
        "fontWeight": "{primitives.typography.fontWeight.semibold}",
        "lineHeight": "{primitives.typography.lineHeight.normal}"
      },
      "body": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.base}",
        "fontWeight": "{primitives.typography.fontWeight.normal}",
        "lineHeight": "{primitives.typography.lineHeight.relaxed}"
      },
      "small": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.sm}",
        "fontWeight": "{primitives.typography.fontWeight.normal}",
        "lineHeight": "{primitives.typography.lineHeight.normal}"
      },
      "label": {
        "fontFamily": "{primitives.typography.fontFamily.sans}",
        "fontSize": "{primitives.typography.fontSize.xs}",
        "fontWeight": "{primitives.typography.fontWeight.semibold}",
        "letterSpacing": "{primitives.typography.letterSpacing.wide}",
        "textTransform": "uppercase"
      }
    }
  }
}
```

### 3.2 Component Specifications

Document core components with full state documentation.

#### Component Spec Template

```markdown
## Component: [Name]

**Purpose:** [What this component does]

### Variants

| Variant | Background | Text | Border | Use Case |
|---------|------------|------|--------|----------|
| Primary | {semantic.interactive.default} | {semantic.text.inverse} | none | Main CTA |
| Secondary | transparent | {semantic.interactive.default} | {semantic.border.emphasis} | Secondary action |
| Ghost | transparent | {semantic.text.primary} | none | Tertiary action |
| Destructive | {semantic.feedback.error} | {semantic.text.inverse} | none | Dangerous action |

### States

| State | Modifier | Visual Change |
|-------|----------|---------------|
| Default | — | Base appearance |
| Hover | :hover | Background darkens 10%, cursor pointer |
| Active | :active | Background darkens 15%, slight scale(0.98) |
| Focus | :focus-visible | 2px ring {semantic.border.focus}, 2px offset |
| Disabled | :disabled | Opacity 0.5, cursor not-allowed |

### Sizes

| Size | Padding | Font Size | Min Height |
|------|---------|-----------|------------|
| sm | {spacing.2} {spacing.3} | {fontSize.sm} | 32px |
| md | {spacing.3} {spacing.4} | {fontSize.base} | 40px |
| lg | {spacing.4} {spacing.6} | {fontSize.lg} | 48px |

### Accessibility

- Minimum touch target: 44×44px
- Focus ring visible on keyboard navigation
- ARIA: role="button" (default), aria-disabled for disabled state
- Color contrast: Minimum 4.5:1 for text
```

#### Core Components to Specify

1. **Buttons** — Primary, Secondary, Ghost, Destructive
2. **Inputs** — Text, Select, Checkbox, Radio, Toggle
3. **Cards** — Basic, Interactive, Elevated
4. **Navigation** — Header, Sidebar item, Breadcrumbs, Tabs
5. **Alerts** — Success, Warning, Error, Info
6. **Modals** — Dialog, Confirmation, Side sheet
7. **Typography** — Display, Headings, Body, Small, Label

### 3.3 Pattern Library

Define common page patterns with specifications.

#### Pattern Template

```markdown
## Pattern: [Name]

**Use case:** [When to use this pattern]

### Layout

```
┌─────────────────────────────────────────────┐
│  [ASCII wireframe of the layout]            │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Component placement                 │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Token Specifications

| Element | Token | Value |
|---------|-------|-------|
| Container padding | {spacing.16} | 64px |
| Title | {typography.display} | 48px bold |
| Subtitle | {typography.body} | 16px, {text.secondary} |
| CTA spacing | {spacing.8} | 32px from text |

### Responsive Behavior

| Breakpoint | Changes |
|------------|---------|
| Desktop (>1024px) | [Layout description] |
| Tablet (768-1024px) | [Layout changes] |
| Mobile (<768px) | [Stacked layout, reduced spacing] |
```

#### Core Patterns to Define

1. **Hero Sections** — Centered, Left-aligned, With image
2. **Feature Grids** — 3-column, Alternating row
3. **Pricing Tables** — Tiered comparison
4. **Testimonial Sections** — Quote cards, Carousel
5. **CTA Sections** — Simple, With image
6. **Footer Layouts** — Simple, Multi-column

### 3.4 Implementation Starters

Generate production-ready code artifacts.

#### CSS Custom Properties

```css
:root {
  /* Primitives - Colors */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;

  --color-brand-50: {{BRAND_50}};
  --color-brand-100: {{BRAND_100}};
  --color-brand-200: {{BRAND_200}};
  --color-brand-300: {{BRAND_300}};
  --color-brand-400: {{BRAND_400}};
  --color-brand-500: {{BRAND_500}};
  --color-brand-600: {{BRAND_600}};
  --color-brand-700: {{BRAND_700}};
  --color-brand-800: {{BRAND_800}};
  --color-brand-900: {{BRAND_900}};

  /* Primitives - Spacing */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-12: 48px;
  --spacing-16: 64px;

  /* Primitives - Typography */
  --font-sans: {{FONT_SANS}}, system-ui, sans-serif;
  --font-mono: {{FONT_MONO}}, monospace;

  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 20px;
  --text-2xl: 24px;
  --text-3xl: 30px;
  --text-4xl: 36px;
  --text-5xl: 48px;

  /* Primitives - Border Radius */
  --radius-sm: 4px;
  --radius-md: {{RADIUS_MD}};
  --radius-lg: {{RADIUS_LG}};
  --radius-xl: {{RADIUS_XL}};
  --radius-full: 9999px;

  /* Primitives - Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Semantic - Background */
  --bg-default: #FFFFFF;
  --bg-surface: var(--color-gray-50);
  --bg-muted: var(--color-gray-100);
  --bg-emphasis: var(--color-brand-500);

  /* Semantic - Text */
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-600);
  --text-muted: var(--color-gray-400);
  --text-inverse: #FFFFFF;

  /* Semantic - Border */
  --border-default: var(--color-gray-200);
  --border-emphasis: var(--color-brand-500);

  /* Semantic - Interactive */
  --interactive-default: var(--color-brand-500);
  --interactive-hover: var(--color-brand-600);
  --interactive-active: var(--color-brand-700);

  /* Semantic - Feedback */
  --success: #10B981;
  --success-bg: #ECFDF5;
  --warning: #F59E0B;
  --warning-bg: #FFFBEB;
  --error: #EF4444;
  --error-bg: #FEF2F2;
}
```

#### Tailwind Config Extension

```javascript
// tailwind.extend.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '{{BRAND_50}}',
          100: '{{BRAND_100}}',
          200: '{{BRAND_200}}',
          300: '{{BRAND_300}}',
          400: '{{BRAND_400}}',
          500: '{{BRAND_500}}',
          600: '{{BRAND_600}}',
          700: '{{BRAND_700}}',
          800: '{{BRAND_800}}',
          900: '{{BRAND_900}}',
        },
        accent: {
          50: '{{ACCENT_50}}',
          100: '{{ACCENT_100}}',
          500: '{{ACCENT_500}}',
          600: '{{ACCENT_600}}',
          700: '{{ACCENT_700}}',
        },
      },
      fontFamily: {
        sans: ['{{FONT_SANS}}', 'system-ui', 'sans-serif'],
        mono: ['{{FONT_MONO}}', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '{{RADIUS_MD}}',
        lg: '{{RADIUS_LG}}',
        xl: '{{RADIUS_XL}}',
      },
      boxShadow: {
        'card': '0 4px 6px rgba(0, 0, 0, 0.07)',
        'card-hover': '0 10px 15px rgba(0, 0, 0, 0.1)',
      },
    },
  },
};
```

### 3.5 Final Style Tile

Generate comprehensive HTML style tile showing the complete system.

Save to: `.tmp/visuals/style-tile-final.html`

(Use the HTML template from Stage 2 preview but expanded with full component showcase)

---

# Output Artifacts

### Stage 1 Output

| File | Content |
|------|---------|
| `{brain}/strategy/mood-direction.md` | Approved mood direction |

### Stage 2 Output

| File | Content |
|------|---------|
| `{brain}/strategy/palette-typography.md` | Locked colors and fonts |
| `.tmp/visuals/palette-preview-*.html` | Preview files for options |

### Stage 3 Output

| File | Content |
|------|---------|
| `{brain}/strategy/design-system.md` | Complete design system |
| `{brain}/strategy/design-tokens.json` | Full token architecture JSON |
| `{brain}/strategy/design-tokens.css` | CSS custom properties |
| `{brain}/strategy/tailwind.extend.js` | Tailwind config (if applicable) |
| `.tmp/visuals/style-tile-final.html` | Complete style tile |

Generate token artifacts when the surface supports file output.

### Final Design System Output Structure

```markdown
---
title: Design System — [Company/Product Name]
created: YYYY-MM-DD
status: complete
mood-source: mood-direction.md
palette-source: palette-typography.md
---

# Design System — [Company/Product Name]

## Executive Summary
[2-3 sentences: Visual direction, key design decisions, implementation approach]

---

## 1. Foundation
[Mood direction summary, brand essence from brand-strategy]

## 2. Color System
[Full color scales, application rules, accessibility notes]

## 3. Typography
[Hierarchy, scale, font choices, usage guidelines]

## 4. Spacing & Layout
[Spacing scale, grid system, density guidelines]

## 5. Component Specifications
[Core components with variants, states, accessibility]

## 6. Pattern Library
[Page patterns with wireframes and token specs]

## 7. Motion Design
[Animation principles, transition tokens, micro-interactions]

## 8. Do's and Don'ts
[Visual examples of correct vs incorrect application]

## 9. Implementation Guide
[Tech stack recommendations, code starters, file references]

---

## Appendix: Full Token Reference
[Complete token JSON]
```

---

# Quality Checklist

### Stage 1 Checklist
- [ ] Reference inputs collected (brands, mood boards, anti-references)
- [ ] 2-3 mood concepts generated (feel only, no colors)
- [ ] Clear differentiation between concepts
- [ ] User approved a mood direction
- [ ] mood-direction.md saved with status: approved

### Stage 2 Checklist
- [ ] Mood direction loaded from Stage 1
- [ ] 2-3 palette options generated with rationale
- [ ] 2-3 typography pairings proposed
- [ ] Preview HTML generated for comparison
- [ ] User selected both palette AND typography
- [ ] palette-typography.md saved with status: approved

### Stage 3 Checklist
- [ ] Palette/typography loaded from Stage 2
- [ ] Full color scales generated (50-900)
- [ ] Token architecture follows Primitive → Semantic tiers
- [ ] All core components have full state specifications
- [ ] Accessibility documented (contrast ratios, focus, touch targets)
- [ ] Pattern library includes responsive behavior
- [ ] CSS custom properties are production-ready
- [ ] Output connects back to brand strategy
- [ ] No generic "SaaS template" feel — reflects brand personality

### Quality Standard (summary)

- Mood, palette, and system build should be approved in sequence.
- Tokens should be semantic, not only raw hex values.
- Components should include variants, states, accessibility, and responsive behavior.
- The final system should reflect the brand, not a generic template.

---

# Anti-Patterns (Never Do)

**DON'T:**
- Skip stages or bulldoze to implementation
- Generate colors/fonts in Stage 1 (mood only!)
- Proceed without checkpoint approval
- Use only hex codes without semantic naming
- Define components without states
- Forget accessibility
- Create tokens that don't map to implementation

**DO:**
- Get approval at each checkpoint
- Generate multiple options at each stage
- Build decisions incrementally
- Connect every decision to mood direction
- Document all component states
- Include WCAG compliance notes

---

# Integration

| Upstream | What It Provides |
|----------|------------------|
| `/discovery-intake` | Business context, audience, product type |
| `/positioning-strategy` | Competitive anchor, differentiation |
| `/brand-strategy` | Voice, personality, messaging (recommended) |

| Downstream | What It Receives |
|------------|------------------|
| `/visual-content` | Can reference design tokens for visual consistency |
| Landing page builds | Uses patterns and component specifications |
| Product UI | Uses token architecture for theming |

---

# Quick Actions

After completing all stages:

- "Refine the color palette" → Adjusts palette-typography.md, re-runs Stage 3
- "Add dark mode tokens" → Generates dark theme variant
- "Spec out [component]" → Deep-dive on specific component
- "Generate hero pattern" → Creates pattern spec with HTML preview
- "Export for Figma" → Formats tokens for Figma variables

**Extract from existing site:**
- "Extract design system from [URL]" → Runs `/design-extract` to reverse-engineer tokens from a live URL and feed into Stage 3

---

# Adaptation Notes

- Codex can generate local token files and preview HTML when file access is available.
- ChatGPT can run the staged decision workflow inside a Project with shared references.
- MCP clients should expose preview and token export as optional capabilities rather than required steps.
