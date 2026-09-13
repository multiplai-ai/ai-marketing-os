---
name: creative-suite
description: 'Standard operating procedure for the creative suite: explains the 5-stage foundation, production workflow, storage architecture, translation scripts, and tool integration — from visual research to campaign assets.'
---

# Creative Suite SOP

Standard operating procedure for the creative suite: explains the 5-stage foundation, production workflow, storage architecture, translation scripts, and tool integration — from visual research to campaign assets.

> Core skill canon (Phase 4). Merged from .claude/commands/cd/sop.md (rich) + skills-core/skills/creative/creative-suite-sop.md (portable stub) on 2026-07-02.

Legacy adapter: previously invoked as the `/cd/sop` command via `.claude/commands/cd/sop.md`; that path is now an adapter, not the canonical mechanism. Sibling skills were previously `/cd/...` commands — the bare core skill ids used below are canonical.

---

## Goal

Provide a portable operating guide for the creative foundation and production system. This is a reference workflow (no output artifact of its own) that orients an operator, explains how the skills chain together, and identifies the next step.

---

## What Is the Creative Suite?

The creative suite is a sequence of skills that take a brand from "we need a visual identity" to "here are production-ready assets across every channel."

Each skill builds on the one before it. The output of one becomes the required input for the next. Prerequisites are enforced — you can't skip stages.

**Core principle: Repo is hub, tools are adapters.** All brand foundations live in git as design tokens + SVGs + reference code. Downstream tools (Gamma, Pencil, Figma, Canva) consume from the repo via translation scripts. When tools change, update the script, not the library.

---

## The Five Foundation Stages (Run Once Per Brand)

```
research     → visual-research.md + references/ (harvested code + SVGs)
      ↓
mood         → mood-direction.md (feel, energy, prompts — NO colors/fonts)
      ↓
brand-guide  → brand-guide.md + tokens.json (colors, fonts, textures, rules, locked AI prompts)
      ↓
components   → components/ (native SVGs) + component-inventory.md
      ↓
templates    → templates/ (native SVGs) + template-inventory.md
```

1. `research` creates visual research and references.
2. `mood` turns research into approved mood direction.
3. `brand-guide` creates brand guidelines, tokens, and generated tool configs.
4. `components` creates reusable native SVG components.
5. `templates` creates platform-specific templates.

### Production (Run Per Campaign)

```
creative-produce → Routes by asset type, loads all context, produces on-brand output
```

6. `creative-produce` creates production-ready assets from the approved foundation.

### Supporting

```
creative-status → Show foundation progress for any entity
creative-suite-sop → This document
```

Use `creative-status` anytime to inspect progress and identify the next missing step.

---

## Storage Architecture

All creative artifacts live in `{brain}/creative/`. The structure:

```
{brain}/creative/
├── visual-research.md          ← Stage 1 output
├── mood-direction.md           ← Stage 2 output
├── brand-guide.md              ← Stage 3 output (human-readable)
├── tokens.json                 ← Stage 3 output (W3C design tokens, machine-readable)
├── component-inventory.md      ← Stage 4 manifest
├── template-inventory.md       ← Stage 5 manifest
├── references/                 ← Harvested code from research
│   ├── competitors/
│   ├── aspirational/
│   └── screenshots/
├── components/                 ← Native SVG components
│   ├── backgrounds/
│   ├── textures/
│   ├── buttons/
│   ├── badges/
│   ├── dividers/
│   ├── cards/
│   ├── icons/
│   └── logo/
├── templates/                  ← Platform SVG templates
│   ├── linkedin/
│   ├── instagram/
│   ├── twitter/
│   ├── ads/
│   ├── email/
│   ├── web/
│   └── og/
├── generated/                  ← Auto-generated from tokens.json
│   ├── variables.css
│   ├── tailwind.config.js
│   ├── gamma-prompts.md
│   ├── pencil-variables.json
│   └── figma-tokens.json
└── output/                     ← Production assets from creative-produce
```

### Three Storage Layers

| Layer | Format | Purpose | Example |
|-------|--------|---------|---------|
| **Design Tokens** | JSON (W3C DTCG) | Machine-readable values — colors, fonts, spacing | `tokens.json` |
| **Vector Assets** | Native SVG | Figma-editable components — backgrounds, textures, buttons | `components/backgrounds/light-paper-01.svg` |
| **Reference Code** | HTML + Tailwind | Harvested "vibe code" from inspiration sites | `references/aspirational/stripe-hero.html` |

---

## How Upstream Skills Feed Downstream

| Upstream Skill | Produces | Consumed By |
|----------------|----------|-------------|
| Discovery Intake (`discovery-intake`) | `{brain}/strategy/discovery-intake.md` | `research` (soft — extracts positioning, ICP, competitors) |
| Positioning Strategy (`positioning-strategy`) | `{brain}/strategy/positioning-strategy.md` | `research`, `mood` (extracts differentiation) |
| Brand Strategy (`brand-strategy`) | `{brain}/strategy/brand-strategy.md` | `mood`, `brand-guide` (extracts voice, personality) |
| `research` | `visual-research.md` + `references/` | `mood` (hard block) |
| `mood` | `mood-direction.md` | `brand-guide` (hard block) |
| `brand-guide` | `brand-guide.md` + `tokens.json` | `components` (hard block), `creative-produce` |
| `components` | `components/` + `component-inventory.md` | `templates` (hard block), `creative-produce` |
| `templates` | `templates/` + `template-inventory.md` | `creative-produce` |

**Hard block** = skill refuses to run without the upstream artifact.
**Soft** = skill extracts what it can, proceeds with explicit assumptions if missing.

---

## Translation Scripts

These read `tokens.json` and output tool-specific configs:

| Script | Input | Output |
|--------|-------|--------|
| `tools/tokens_to_css.py` | `tokens.json` | `generated/variables.css` |
| `tools/tokens_to_tailwind.py` | `tokens.json` | `generated/tailwind.config.js` |
| `tools/tokens_to_gamma.py` | `tokens.json` | `generated/gamma-prompts.md` |
| `tools/tokens_to_pencil.py` | `tokens.json` | `generated/pencil-variables.json` |
| `tools/tokens_to_figma.py` | `tokens.json` | `generated/figma-tokens.json` |

---

## Tool Roles

| Tool | Role | When to Use |
|------|------|-------------|
| **Claude Code** | Orchestrator + SVG generator | Always — runs skills, generates native SVG, manages tokens |
| **Gamma** | AI image generator | Backgrounds, textures, visual content (locked brand prompts) |
| **Figma** | Precision editor | Final brand asset refinement, component library editing |
| **Pencil** | UI-to-code generator | Web/app UI design that becomes React/Tailwind code |
| **Canva** | Speed compositor | Quick social graphics, client collaboration |

Portable-context equivalents (from the stub, for non-Claude-Code runtimes):

- Codex: filesystem orchestration, SVG/HTML generation, token export, and repo maintenance
- ChatGPT: collaborative creative direction, critique, and stakeholder-friendly explanation
- External design/image tools: rendering, refinement, and handoff when needed

---

## Key Design Principles

1. **Repo is hub, tools are adapters.** When tools change, update the translation script, not the library.
2. **Upstream determines downstream.** Strategy suite → creative foundation → production. No skipping. Upstream strategy should shape downstream creative decisions.
3. **Capture code, not screenshots.** Harvested references stored as HTML/Tailwind/SVG, not PNGs.
4. **Design tokens are the source of truth.** `tokens.json` feeds everything.
5. **Explicit prerequisites with hard blocks.** Missing upstream artifact = stop and redirect.
6. **Checkpoints at every stage.** User approves before proceeding.
7. **Locked prompts stored as artifacts.** AI image prompts generated once, stored permanently.
8. **Campaign-aware production.** Every asset connects to a campaign or content calendar item.
9. **Native SVG for all components and templates.** Never HTML-to-SVG conversion. Components and templates should be native, editable, and reusable.
10. **Production never rewrites the visual system.** Producing assets consumes the foundation; it does not fork it.
11. **Tool-specific prompts and configs are generated from stable artifacts**, never hand-maintained.

---

## Quality Standard

- Stages should be completed in order unless the user explicitly approves a scoped exception.
- Missing artifacts should create a clear next action, not silent degradation.
- Production outputs should include source files and notes, not only final images.

---

## Quick Reference

- **Check foundation progress:** `creative-status`
- **Start a new brand:** `research` → follow the chain
- **Produce assets:** `creative-produce` (requires complete foundation)
- **All artifacts save to:** `{brain}/creative/`

---

## Adaptation Notes

- This is a reference workflow and can be invoked at any time.
- Generated adapters should preserve it as a portable SOP, not a slash-command manual.
