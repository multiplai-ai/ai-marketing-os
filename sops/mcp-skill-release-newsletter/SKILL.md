---
name: mcp-skill-release-newsletter
description: Prepare a newsletter announcing MCP or skill releases from verified product changes and approved source material.
---

# MCP Skill Release Newsletter Workflow

Use this workflow whenever the consumer publishes a new MCP skill release, skill-suite update, or subscriber-only tooling announcement in Ghost.

Use the consumer's current series naming, audience, access model and voice. Explain verified changes, practical next steps and setup limits.

## Trigger Phrases

Use this workflow when the request sounds like:

- "Publish a new MCP skill release update."
- "Create the Ghost newsletter for a new skill drop."
- "Make the thumbnail for the New Skills post."
- "Send the MCP update to Ghost."
- "Use the same format as the New Skills / GEO suite announcement."

## Source Inputs

Collect or infer:

- Skill or suite name.
- What changed: new skills, scripts, docs, workflows, fixes, or access changes.
- User outcome: what paid subscribers can now do faster or better.
- Access level: free subscribers, paid members, beta group, or public.
- Installation/update instructions.
- Links: package, GitHub repo, documentation, research references, or usage examples.
- Known caveats: API costs, setup requirements, failure modes, expected first-week feedback.

## Editorial Pattern

Use this structure for the Ghost post body:

```md
Hey -

Shipped {skill_or_suite_name} to the MCP today. {One crisp sentence on who gets it and what to do first.}

{Number} new skills/tools under {suite/category}:

- {skill-name} - {plain-English job}
- {skill-name} - {plain-English job}
- {skill-name} - {plain-English job}

Why I built this. {Before/after market context. Name the gap this solves. Keep it practical.}

The typical invocation chain:

{skill-a} -> {skill-b} -> {skill-c}

Runs {cost/time/effort expectation}. You get {deliverables/outcome}.

Companion tools / setup. {Install/update instructions, repo link, required API keys, caveats.}

The research behind it. {Optional 1-3 references that shaped the design.}

If you run into anything weird - {support promise and feedback loop}.

Happy {doing-the-thing}!

- owner @ brand
```

## Ghost Post Settings

Default settings for MCP skill release updates:

- Post type: Ghost post, not page.
- Template: `Feature Release` when available, otherwise default post template.
- Access: usually paid members only for subscriber-only skill drops; public only when the release is intended as acquisition content.
- Newsletter audience: the subscribed user newsletter/audience appropriate to the access level.
- Primary tag: `feature-release`, `release-notes`, or the relevant public topic tag.
- Internal tags: `#feature-release-template`, `#mcp-update`, `#skill-drop`.
- Excerpt: one sentence naming the subscriber outcome.
- Do not publish without explicit approval. Uploading/saving a draft feature image is okay when requested.

## Subject And Preview Patterns

Subject patterns:

- New Skills: {outcome}
- New in the MCP: {specific capability}
- Now live: {skill_or_suite_name}
- {skill_or_suite_name}: {job-to-be-done} in {time}

Preview text patterns:

- Paid subscribers can now {outcome} with {skill_or_suite_name}.
- A quick skill drop for {audience}: {what changed}, how to use it, and what to try first.
- This update adds {capability}, so you can {benefit}.

## Thumbnail Production

Resolve the current consumer brand guide, design library, font sources, approved logo
page and newsletter image requirements through its repository instructions and binding.
Reuse the selected thumbnail components and current show/series naming. A prior release
post does not establish current branding, layout, membership packaging or product claims.

Set dimensions from the current channel requirement. Build and inspect the editable
source and export using approved fonts and artwork. Check legibility, cropping and font
loading. Keep working media in the consumer's approved temporary location and final media
in its durable delivery location. Record the source links and production approval state.
Upload a feature image only within the user's authorized draft/publishing scope.

## Upload-To-Ghost Checklist

1. Open the target Ghost draft in Admin.
2. Confirm the post title and access setting before changing anything.
3. Remove any old generic feature image if it is clearly the wrong thumbnail.
4. Click `Add feature image`.
5. Select the inspected export from the consumer's approved working location.
6. Wait for Ghost to finish uploading and autosaving.
7. Confirm the feature image appears at the top of the editor.
8. Confirm the post remains a draft unless the user explicitly asked to publish.

## Quality Bar

The finished post should feel like a useful operator note, not a launch press release. It should tell paid subscribers what shipped, why it matters, how to use it, what it costs or requires, and how to get help if something breaks.

The finished thumbnail should use the current approved identity and remain legible in the selected channel's web and email preview contexts.
