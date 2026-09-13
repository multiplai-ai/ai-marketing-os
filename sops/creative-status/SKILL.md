---
name: creative-status
description: 'Creative foundation progress check: report which Creative Director foundation stages are complete for an entity (or all entities), what''s missing, and what to run next.'
---

# Creative Status

Creative foundation progress check: report which Creative Director foundation stages are complete for an entity (or all entities), what's missing, and what to run next.

> Core skill canon (Phase 4). Merged from .claude/commands/cd/status.md (rich) + skills-core/skills/creative/creative-status.md (portable stub) on 2026-07-02.

Legacy adapter: previously invoked as the `/cd/status` command via `.claude/commands/cd/status.md`; that path is now an adapter, not the canonical mechanism.

**Goal:** Report creative foundation progress for one entity or all entities, distinguish hard blockers from soft missing context, and recommend the next core skill to run.

---

## Input / Output Contract

**Inputs (user provides ONE of):**

1. **Entity name** — e.g., "organization", "Acme Health"
2. **No input** — check all entities with creative directories

Supporting inputs (from the stub contract):

- entity_name
- entity_dir — resolved to `{brain}` (see Step 1)
- workspace_manifest — `WORKSPACE.yaml` entity registry

**Outputs:**

- Status report rendered in-conversation (Step 4 / Step 5 formats)
- Optionally save a status report to `{brain}/creative/status-report.md`

**Dependencies:** none (this skill only reads; every creative skill's artifact is a soft input).

**Tool contracts:** filesystem_artifact_check.

---

## Workflow

### Step 1: Resolve Entity Directory ({brain})

Map entity name to the entity's brain directory:

- Canonical (brain schema): `brains/{name}/`
- Legacy (creative-director-main workspace layout): check `brands/{name}/` first, then `clients/{name}/`, then `products/{name}/`
- If ambiguous, check `WORKSPACE.yaml` for the entity registry

Set `{brain}` to the resolved path.

If no entity is provided, scan known entity directories for `creative/` subdirectories (see Step 5).

### Step 2: Check Foundation Artifacts

For `{brain}/creative/`, check existence of each artifact:

| Stage | Skill | Artifact | Status Check |
|-------|-------|----------|-------------|
| 1. Research | `/cd/research` | `visual-research.md` | File exists and has content |
| 1b. References | `/cd/research` | `references/` directory | Directory exists with ≥1 file |
| 2. Mood | `/cd/mood` | `mood-direction.md` | File exists and has content |
| 3. Brand Guide | `/cd/brand-guide` | `brand-guide.md` | File exists and has content |
| 3b. Tokens | `/cd/brand-guide` | `tokens.json` | File exists and is valid JSON |
| 3c. Generated | `/cd/brand-guide` | `generated/` directory | Contains ≥1 generated file |
| 4. Components | `/cd/components` | `component-inventory.md` | File exists and has content |
| 4b. SVGs | `/cd/components` | `components/` directory | Directory exists with ≥1 SVG |
| 5. Templates | `/cd/templates` | `template-inventory.md` | File exists and has content |
| 5b. SVGs | `/cd/templates` | `templates/` directory | Directory exists with ≥1 SVG |

Treat JSON validity and non-empty directories as part of the check when file access allows it.

### Step 3: Check Upstream CMO Context

Also check for CMO strategy artifacts that feed the creative foundation:

| CMO Artifact | Location | Used By |
|-------------|----------|---------|
| Discovery | `{brain}/strategy/discovery-intake.md` | `/cd/research` (soft) |
| Positioning | `{brain}/strategy/positioning-strategy.md` | `/cd/research` (soft) |
| Brand Strategy | `{brain}/strategy/brand-strategy.md` | `/cd/mood`, `/cd/brand-guide` (soft) |
| ICP & Personas | `{brain}/strategy/icp-personas.md` | `/cd/research` (soft) |
| Content Strategy | `{brain}/strategy/content-strategy.md` | `/cd/templates` (soft) |

These are soft dependencies for creative work — missing strategy context degrades quality but does not block.

### Step 4: Output Status Report

Format:

```
## Creative Director Status: {Entity Name}
Brain: {brain}

### Foundation Progress
| # | Stage | Status | Artifact |
|---|-------|--------|----------|
| 1 | Research | ✅ Complete / ❌ Missing | visual-research.md |
| 2 | Mood | ✅ Complete / ❌ Missing | mood-direction.md |
| 3 | Brand Guide | ✅ Complete / ❌ Missing | brand-guide.md + tokens.json |
| 4 | Components | ✅ Complete / ❌ Missing | components/ + inventory |
| 5 | Templates | ✅ Complete / ❌ Missing | templates/ + inventory |

### CMO Strategy Context
| Artifact | Status |
|----------|--------|
| Discovery | ✅ / ❌ |
| Positioning | ✅ / ❌ |
| Brand Strategy | ✅ / ❌ |
| ICP & Personas | ✅ / ❌ |
| Content Strategy | ✅ / ❌ |

### Production Ready?
{Yes — all 5 stages complete, /cd/produce available}
{No — next step: run /cd/{next-stage}}

### Next Action
→ Run `/cd/{next-incomplete-stage}` to continue the foundation.
```

Optionally save this report to `{brain}/creative/status-report.md`.

### Step 5: If Checking All Entities

If no entity specified, scan all entity directories for `creative/` subdirectories and output a summary table.

Example (concrete literals for illustration only):

```
## Creative Director Status: All Entities

| Entity | Dir | Research | Mood | Brand Guide | Components | Templates | Production Ready |
|--------|-----|----------|------|-------------|------------|-----------|-----------------|
| organization | brains/organization/ | ✅ | ✅ | ✅ | ❌ | ❌ | No |
| Acme Health | brains/acme-health/ | ❌ | ❌ | ❌ | ❌ | ❌ | No |
```

> Legacy (creative-director-main): the pre-Phase-4 workspace showed these entities at `brands/organization/` and `clients/entity/`; under the brain schema each entity resolves to `brains/<entity>/`.

---

## Quality Standard

- Distinguish hard blockers from soft missing context.
- Do not claim production readiness unless brand guide, tokens, components, and templates exist.
- Use clear file paths so teammates can fix missing artifacts quickly.

## Adaptation Notes

- Codex can perform filesystem checks directly.
- ChatGPT can use uploaded folder listings or manually supplied artifact inventories.
