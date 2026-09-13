---
name: artifact-to-presentation
description: Use this as the default workflow for analytical reports, executive narratives, dashboards, and visual recommendations that may need to become Google Slides, Google Docs, Confluence pages, or other stakeholder-facing deliverables.
---

# Artifact-First Reporting And Presentation Runbook

Use this as the default workflow for analytical reports, executive narratives, dashboards, and visual recommendations that may need to become Google Slides, Google Docs, Confluence pages, or other stakeholder-facing deliverables.

## Default Path

```
raw sources
  -> analysis layer
  -> required standard views
  -> structured report spec
  -> Codex artifact storyboard
  -> revision loop
  -> final Gamma / Slides / Docs / Confluence package
```

## When To Use

Use this by default when the output needs any of the following:

- A strong narrative or recommendation.
- Charts, scorecards, diagrams, or visual explanations.
- Stakeholder review before publishing.
- A final artifact that will be shared in Confluence, Google Slides, Google Docs, or a client workspace.

Skip directly to the final format only when the user explicitly asks for a direct deliverable, the asset is trivial, or timing makes a review artifact unnecessary. If skipping, state the assumption.

## Workflow

### 1. Build The Analysis Layer

Create or identify the durable source-of-truth analysis files before designing the final story.

Typical outputs:

- Clean workbook, CSV, or JSON with calculated metrics.
- Source notes describing date coverage, pacing factors, filters, and missing data.
- Reproducible script or command when the work is recurring.

Guardrails:

- Keep calculations separate from presentation copy.
- Flag partial-period data clearly.
- Do not hide assumptions inside chart labels only.

### 2. Produce Required Standard Views

For recurring reports, always produce the standard reports, views, workbooks, or scorecards the audience already expects before adding new analysis.

Examples:

- Monthly business review scorecards.
- Weekly or monthly KPI tracker tabs.
- Standard audience/user-growth scorecards.
- Existing workbook tabs that serve as the source of truth.

Guardrails:

- Do not replace expected standard views with a novel artifact, even when the new analysis is stronger.
- New visuals and recommendations should follow, annotate, or extend the standard readout.
- If a standard input is missing, produce the standard view with a labeled gap or caveat rather than silently omitting it.
- When the same report has a deterministic runbook or skill, run that first and use its workbook as the source of truth for later visuals.

### 3. Create A Structured Report Spec

Write the report as a structured spec before building the final presentation.

Recommended fields:

- `title`
- `audience`
- `decision_needed`
- `source_files`
- `date_coverage`
- `pacing_or_normalization`
- `slides_or_sections`
- `metrics`
- `visuals`
- `recommendations`
- `open_questions`

The spec can be JSON, Markdown frontmatter plus sections, or a small project-specific schema. Favor whatever is easiest to reuse.

### 4. Build A Codex Artifact Storyboard

Create a reviewable artifact that is pleasant to revise before committing to Slides or Docs.

Good storyboard forms:

- HTML report with slide-like 16:9 sections.
- Markdown report with embedded chart images or tables.
- Local prototype deck when the work is already slide-native.

Design for later export:

- Keep sections close to slide/page boundaries.
- Prefer visuals that can be rebuilt as native charts, tables, shapes, or text.
- Avoid depending on interactions, hover states, animations, or HTML-only layout tricks for the core argument.
- Use the artifact to tune story, emphasis, chart selection, and recommendations.

### 5. Revise Until Approved

Treat the storyboard as the fast iteration surface.

Revise:

- Narrative spine.
- Headlines and executive framing.
- Chart choice and annotations.
- What-we-should-do recommendations.
- Risks, caveats, and open questions.

Do not publish to the final destination until the story is coherent enough that a reviewer is reacting to judgment, not basic structure.

### 6. Generate The Final Deliverable

Choose the final format based on audience:

| Destination | Use When |
|---|---|
| Gamma | Default for client-facing recommendations, proposals, reports, leave-behinds, and polished async docs |
| Google Slides | Visual executive readout, meeting narrative, decision deck |
| Google Docs | Text-heavy memo, operating plan, policy, detailed analysis |
| Confluence | Team distribution wrapper, searchable archive, async summary |
| HTML | Interactive internal artifact, hosted report, exploratory analysis |

Client-facing surface rule:

- Default organization, brand, and client-facing deliverables to Gamma.
- Do not share raw Google Doc publishes as final client-facing artifacts unless the content truly needs document form.
- If Google Docs is the final surface, produce a branded Microsoft Word document first, upload/convert it in Drive, and pass export/readback QA.
- Use Google Slides instead of Gamma only when the output is truly deck-native or needs native editable slides.
- Follow `docs/runbooks/publishing/client-facing-deliverables.md` before handoff.

For Gamma:

- Use `docs/runbooks/publishing/to-gamma.md`.
- For organization artifacts, load the brand guide, tokens, and Gamma prompts from `brains/organization/creative/`.
- Treat the returned Gamma as the share artifact only after the user has reviewed or the workflow has verified the generated structure.

For Google Slides:

- Build or import a native editable deck whenever practical.
- Recreate approved storyboard visuals as native slide text, shapes, charts, and tables where possible.
- Use raster images only when a visual cannot reasonably be rebuilt natively.
- Verify the imported Google Slides deck with readback and rendered thumbnails.

For Google Docs:

- Keep headings, tables, and charts editable where possible.
- Use images only for complex visuals that do not need editing.
- Use Google Docs as the final client-facing surface only for intentionally text-heavy deliverables.
- Build a branded `.docx` first, upload/convert it in Drive, and verify that the styling survives conversion.
- Avoid Office-mode files as final publish artifacts.
- Verify headings, table styling, spacing, links, and export/rendered output before handoff.

For Confluence:

- Use Confluence as the wrapper: short executive summary, decision asks, links/embeds to the durable deck/doc, and attachments when needed.
- Do not treat Confluence as the only home for a complex visual report unless it preserves the visuals well enough for the audience.

### 7. Archive And Handoff

Store durable artifacts in the relevant entity folder.

Recommended paths:

- Analysis layer: `{entity_dir}/analysis/`
- Report narrative or spec: `{entity_dir}/analysis/` or `{entity_dir}/strategy/`
- Client-specific recurring SOPs: `clients/{client}/runbooks/`
- Temporary previews and generated intermediates: `.tmp/`

Final handoff should include:

- Final link or file path.
- What was verified.
- Any assumptions, missing data, or caveats.
- Recommended next action.

## Quality Bar

A good artifact-first report has:

- One clear answer to the user's operating question.
- A visible chain from data to inference to recommendation.
- Visuals that clarify the argument rather than decorate it.
- A final format that preserves the approved visual hierarchy.
- Enough source context for another agent or teammate to reproduce the work.

## Platform Honesty

Do not present a storyboard, local HTML file, or local PPTX as if it has been published to Google Slides, Google Docs, Confluence, or another external platform.

If final-platform publishing fails, report the failure and provide the best local artifact as a fallback.
