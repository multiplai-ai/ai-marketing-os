---
name: templates
description: Generate SVG templates for every platform with branded backgrounds, placeholder zones, and pre-placed logo lockups — built from brand components and tokens for consistent cross-platform production.
---

# Templates — Platform Templates

Generate SVG templates for every platform with branded backgrounds, placeholder zones, and pre-placed logo lockups — built from brand components and tokens for consistent cross-platform production.

> Core skill canon (Phase 4). Merged from .claude/commands/cd/templates.md (rich) + skills-core/skills/creative/templates.md (portable stub) on 2026-07-02.

Legacy adapter: previously invoked as the `/cd/templates` command via `.claude/commands/cd/templates.md`; that path is now an adapter, not the canonical mechanism.

## Goal

Create branded, reusable templates for the platforms and formats the team actually publishes. The system should reduce future design decisions, not create new ambiguity.

## Prerequisites

**HARD BLOCK:** `{brain}/creative/component-inventory.md` must exist.
→ If missing: STOP. Say "Run `/cd/components` first."

Depends on: `components` skill.

**Also loads:**
- `{brain}/creative/brand-guide.md`
- `{brain}/creative/tokens.json`
- `{brain}/creative/visual-research.md` (soft — for channel priorities)
- `{brain}/strategy/content-strategy.md` (soft — for primary channels)

Tool contract: SVG generation tooling is optional — templates are native SVG and can be generated directly.

## Inputs

1. **Entity name** (required)
2. Priority channels (optional — from visual-research/content-strategy if available; user confirms or adjusts the inventory in Step 2)

## Workflow

### Step 1: Resolve & Load

1. Map entity name to its `{brain}` directory
2. Verify `component-inventory.md` exists
3. Read tokens.json, brand-guide.md, component inventory (plus content strategy and priority channels if available)

### Step 2: Present Template Inventory

| Platform | Templates | Dimensions |
|----------|-----------|------------|
| **LinkedIn** | Single image post, carousel slide, banner | 1200x1200, 1080x1350, 1584x396 |
| **Instagram** | Square post, story/reel cover, carousel slide | 1080x1080, 1080x1920, 1080x1350 |
| **Twitter/X** | Post image, header | 1200x675, 1500x500 |
| **Ads** | Static landscape, static square, static story | 1200x628, 1080x1080, 1080x1920 |
| **Email** | Header banner, inline graphic | 600x200, 600x400 |
| **Web** | Hero section, OG image, feature card | 1440x800, 1200x630, 400x300 |
| **Presentation** | (optional channel) | define dimensions and content zones per format |

User confirms or adjusts. For each template, define dimensions and content zones. Templates should reflect actual publishing formats.

### Step 3: Generate Templates

For each template, generate native SVG with:
- Brand-standard background texture (from components — use approved components and tokens)
- Placeholder zones with descriptive `id` attributes: `headline-zone`, `subhead-zone`, `body-zone`, `image-zone` (image or diagram), `cta-zone` (if relevant), `logo-zone`
- Placeholder zones shown as dashed-border rectangles with label text
- Brand colors and typography specs as XML comments
- Logo lockup pre-placed in standard position (per brand-guide)
- Content safe zone (80% width) marked
- Usage notes

**Naming convention:** `{platform}-{variant}.svg`
Examples: `linkedin-single-post.svg`, `ads-static-landscape.svg`

### Step 4: Save Templates

Save to `{brain}/creative/templates/{platform}/`:
- `linkedin/`, `instagram/`, `twitter/`, `ads/`, `email/`, `web/`

### Step 5: Write Inventory

Generate `{brain}/creative/template-inventory.md`:
- Table: path, platform, dimensions, placeholder zones, usage notes
- Total count, last generated date

### Step 6: CHECKPOINT

User reviews templates. Adjust if needed.

## Output

- `{brain}/creative/templates/` — SVG files by platform
- `{brain}/creative/template-inventory.md` — manifest

## Quality Standard

- Templates should reflect actual publishing formats.
- Placeholder zones should be clear and reusable.
- The system should reduce future design decisions, not create new ambiguity.

## Adaptation Notes

- Codex is best for generating and organizing local SVG templates.
- ChatGPT can help choose which templates are worth building first.

## Foundation Complete

All 5 stages done. Run `/cd/status` to verify, or `/cd/produce` to create assets.
