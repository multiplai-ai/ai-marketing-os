---
name: content-produce
description: 'End-to-end content production pipeline: takes a content item from brief through publish-ready (or runs any individual stage), with human checkpoints between stages.'
---

# Content Produce

End-to-end content production pipeline: takes a content item from brief through publish-ready (or runs any individual stage), with human checkpoints between stages.

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/content/produce.md (rich) + skills-core/skills/content/content-produce.md (portable stub) on 2026-07-02.

```
/produce                          # Interactive — assess what's ready, suggest next step
/produce brief <keyword>          # Stage 1: Generate content brief
/produce write <brief-file>       # Stage 2: Write article from brief
/produce qc <article-file>        # Stage 3: SEO/AEO quality check
/produce images <article-file>    # Stage 4: Generate feature image + social graphics
/produce publish <article-file>   # Stage 5: Push to Ghost + generate social + push to Publer
/produce all <keyword>            # Run stages 1-5 sequentially with checkpoints
```

## When To Use

- The user wants to move a content item forward and is unsure which step is next
- A content item needs briefing, drafting, QC, visuals, and publishing handoff
- A team wants one orchestration workflow instead of separate production steps

---

## Pipeline Stages

```
Stage 1          Stage 2         Stage 3         Stage 4              Stage 5
content-brief  → writing       → seo-qc        → templated_renderer → publish
   keyword         brief           draft           article              article
   ↓               ↓               ↓               ↓                    ↓
   brief.md        article.md      scorecard       feature-image.png    Ghost draft
                                   + fixes         social-graphics.png  Publer drafts
```

Before running anything, determine the current stage: inspect available artifacts and user intent, and identify whether the item already has a brief, draft, QC notes, visual assets, and a publishing destination. Route to the smallest useful next step.

---

## Stage 1: Content Brief

Run the `content-brief` skill with the target keyword.

**Input:** keyword or topic
**Output:** `{brain}/content/briefs/{keyword-slug}-brief.md`
**Checkpoint:** Show brief to user, confirm before writing.

---

## Stage 2: Write Article

Run the `writing` skill with the brief as context.

**Input:** brief file from Stage 1
**Output:** `{brain}/content/{content-type}-{date}.md`
**Checkpoint:** User reviews draft before QC.

---

## Stage 3: SEO/AEO Quality Check

Run the `seo-qc` skill on the draft.

**Input:** article file from Stage 2
**Output:** Scorecard (SEO score, AEO score, Content Quality score) + fix recommendations
**Action:** Apply recommended fixes, re-run QC until score > 80.
**Checkpoint:** Show final scores, confirm ready for images.

---

## Stage 4: Generate Images

Use the `visual-content` skill or the deterministic templated-rendering tools:

```bash
# Generate feature image
python3 tools/templated_renderer.py --render <article-file>

# Check result
python3 tools/image_resolver.py --resolve <slug>
```

**Input:** article file (reads title + content_type from frontmatter)
**Output:** `{brain}/content/images/{slug}-{type}.png`
**Checkpoint:** If no template exists for this content type, tell user which template to build in Templated.io (reference: `{brain}/creative-assets/templated-io-template-spec.md`).

> Entity note ({brain}=brand): the Templated.io template spec currently lives at `brands/organization/creative/templated-io-template-spec.md`.

---

## Stage 5: Publish

Run the `publish` distribution skill (or the publishing runbook/scripts for the entity's channels) with the article.

This handles:
1. Push article to Ghost as draft (with feature image if available)
2. Generate social post variants (LinkedIn + Twitter)
3. Push social posts to Publer as drafts with images

**Input:** article file
**Output:** Ghost draft URL + Publer draft count
**Final checkpoint:** Tell user to review drafts in the publishing dashboards before scheduling.

> Entity note ({brain}=brand): publishing targets are the brand Ghost account (review in Ghost Admin) and the brand Publer workspace (review in Publer dashboard) before scheduling.

---

## automation provider Integration (Optional)

If automation provider Power Agents are configured (see `{brain}/strategy/automation provider-power-agent-specs.md`), Stages 3-5 can be partially automated via grid processing:

1. Push article to automation provider "Article Processing" grid
2. Run Article Enricher agent (adds CTAs, links, meta)
3. Run Social Atomizer agent (generates platform variants)
4. Run Thumbnail Brief Generator (generates image text)
5. Pull results back for last-mile publishing

> Entity note ({brain}=brand): the automation provider spec currently lives at `brands/organization/strategy/automation provider-power-agent-specs.md`, and the "Article Processing" grid id is <configured-grid-id>.

Example (concrete, {brain}=brand):
```bash
# Push article to grid
python3 {automation_grid_tool} --grid <configured-grid-id> --file <article-file>

# After agents run, read results back
# (use automation provider MCP: read_grid with grid_id=<configured-grid-id>)
```

This is optional — all stages work without automation provider using local tools and skills.

---

## Interactive Mode

When invoked as just `/produce` with no arguments:

1. Check `{brain}/content/` for files with frontmatter `status: draft` or `status: wip`
2. Check `{brain}/content/briefs/` for unwritten briefs
3. Check image manifest for missing images
4. Suggest the most useful next action:
   - "You have 2 briefs without articles → run `/produce write`"
   - "You have 1 article that hasn't been QC'd → run `/produce qc`"
   - "You have 3 articles ready but no images → run `/produce images`"
   - "You have 1 article ready to publish → run `/produce publish`"

---

## Checkpoints & Production State

Stop for approval after:

- brief before drafting
- draft before QC fixes
- final QC before visual production
- publishing handoff before external posting

When running multiple stages, record what was completed, output paths, blockers, and the next recommended action in a production note or log (`{brain}/content/production-log.md`).

---

## File Routing

| Stage | Output Location |
|---|---|
| Brief | `{brain}/content/briefs/{keyword-slug}-brief.md` |
| Article | `{brain}/content/{content-type}-{date}.md` |
| Images | `{brain}/content/images/{slug}-{type}.png` |
| Production log | `{brain}/content/production-log.md` (multi-stage runs) |
| Social posts | Generated at publish time, pushed directly to Publer |
| Ghost draft | Created via API, URL returned |

---

## Quality Standard

- Do not skip checkpoints that change strategy, voice, or external publishing.
- Route to the smallest useful next step.
- Keep tool execution deterministic where scripts exist (tools/*.py are shared, not per-brain).
