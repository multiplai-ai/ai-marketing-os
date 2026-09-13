---
name: social-audience-growth-weekly
description: Run the weekly organic audience-growth operation for an entity's founder or personal-brand social channels. The skill turns strategy, publishing plans, performance data, and target-audience signals into a weekly execution queue for LinkedIn and X.
---

# Social Audience Growth Weekly

Run the weekly organic audience-growth operation for an entity's founder or personal-brand social channels. The skill turns strategy, publishing plans, performance data, and target-audience signals into a weekly execution queue for LinkedIn and X.

> Core skill canon. Created 2026-07-06 to wrap existing content, publishing, and LinkedIn GTM assets into one operator-run weekly workflow.

## When To Use

- Weekly audience growth for a founder, operator, or personal-brand profile
- Growing qualified followership on LinkedIn and X through content, commenting, connection requests, replies, and warm conversations
- Translating content performance into next week's audience targeting and post ideas
- Building a repeatable agent-owned plan while keeping external social actions human-approved

Do not use this for paid social campaign audits. Use `ads-linkedin` or the paid-media suite for LinkedIn Ads. For a single post draft, use `linkedin-post`. For the weekly flagship writing bundle, use `writing`.

## Operating Principle

Audience growth is a loop, not a posting calendar:

```text
target audience -> useful visibility -> conversations -> qualified follows -> content intelligence -> sharper targeting
```

The goal is not raw follower count. The goal is more of the right people seeing, saving, replying to, and remembering the entity's point of view.

## Inputs

- Entity brain path (`{brain}`)
- Target week
- Audience segment or ICP focus for the week
- Current content calendar or publishing plan, if available
- Recent social performance metrics, if available
- Competitive or peer-set observations, if available
- Any business CTA or campaign priority for the week

## Outputs

- Weekly audience-growth plan: `{brain}/content/social-audience-growth/{week-start}-weekly-plan.md`
- Metrics and learning summary: `{brain}/content/social-audience-growth/{week-start}-weekly-review.md`
- External execution queue pointer in the approved task/CRM system, if used
- Draft comments, replies, DM openers, and connection-request rationale for human approval
- Content intelligence notes to feed `content-calendar`, `writing`, and `linkedin-post`

## Required Context

Load these before planning:

1. `{brain}/BRAIN.md`
2. `{brain}/voice/voice-synthesis.md`
3. `{brain}/runbooks/weekly-social-audience-growth.md`, if present
4. `{brain}/strategy/linkedin-gtm-playbook.md`, if present
5. `{brain}/strategy/content-strategy.md`, if present
6. `{brain}/data-manifest.yaml` for social metrics, competitive intelligence, and execution queue pointers

If the entity-specific runbook is missing, proceed with the portable workflow below and clearly label assumptions.

## Safety And Platform Rules

- Do not send posts, DMs, replies, comments, follows, connection requests, or deletes without explicit human approval or a pre-approved automation rule.
- Do not automate logged-in scraping, mass following, mass DMs, or actions that bypass platform limits.
- Keep target lists and contact-level details in an approved CRM, Notion database, spreadsheet, or platform tool. Repo artifacts should summarize strategy and learnings, not store large contact lists.
- Do not pitch on first contact. The first move is visibility, usefulness, or a genuine question.
- Optimize for qualified audience fit and conversation quality before volume.

## Two-Person Lane Split

When the entity runs two people on the same audience, split them into distinct content lanes instead of duplicating effort:

- **Voice A (POV/authority lane):** the established voice. Opinions, strategy, positioning, market arguments, client results.
- **Voice B (builder/receipts lane):** the operator voice. "Here's what we built, shipped, and measured this week." This lane requires evidence, not marketing insight, which makes it the right lane for a non-marketer.

Rules:

- **Stagger posting days** (for example A on Mon/Wed/Fri, B on Tue/Thu). The audience experiences the combined cadence, so staggering makes the entity visible near-daily without either person exceeding 1 post/day.
- **Cross-comment, don't cross-post.** Each person leaves a substantive 10-15+ word comment on the other's posts within the golden hour. No reciprocal-like patterns, no tagging on every post.
- **Never duplicate content.** The same idea never appears on both profiles in the same week; if both lanes touch a topic, each treats it from its own lane's angle.
- Person-level specifics (who owns which lane, which days) live in the entity runbook, not here.

## Weekly Workflow

### 1. Load Strategy And Current Priorities

Identify:

- Primary ICP segment for the week
- Business priority or CTA, if any
- Active content theme, flagship topic, tool review, capability demo or campaign
- Current channel assumptions for LinkedIn and X
- Any no-go topics, sensitive client references, or timing constraints

Output a one-paragraph operating brief before building the queue.

### 2. Review Last Week's Performance

Collect a weekly snapshot from the available metrics sources:

- LinkedIn: followers, profile views, post impressions or reach if available, reactions, comments, reposts, saves, connection requests sent and accepted
- X: followers, impressions or views, replies, reposts, quote posts, profile visits, link clicks if available
- Conversation quality: DMs started, replies received, warm follow-ups, qualified conversations
- Content quality: top posts by comments, saves, shares, or replies, not only likes
- Audience quality: notable ICP followers, commenters, or connectors

If metrics are unavailable, note the gap and use the qualitative signals available from platform notifications and recent post activity.

### 3. Choose This Week's Audience Focus

Pick one primary audience lane for the week. Score candidates against:

| Factor | Question |
|---|---|
| ICP fit | Is this person or group close to the buyer, partner, or creator audience we want? |
| Signal strength | Did they view, comment, like, follow, post about the topic, or share relevant pain? |
| Relationship path | Is there a credible reason to engage or connect this week? |
| Content fit | Can this week's content help them without forcing a pitch? |

Prioritize warm signals first:

1. People who commented on or saved/reposted the entity's content
2. Profile viewers and inbound connection requests that match ICP
3. Second-degree ICPs connected to known clients, peers, or trusted creators
4. People posting about the week's theme or pain point
5. Cold search matches only after warm lists are exhausted

### 4. Build The Weekly Execution Queue

Create a weekday queue with conservative volume caps unless the entity runbook overrides them:

| Action | Weekly Default | Quality Bar |
|---|---:|---|
| LinkedIn comments | 40-50 total | 2-3 specific sentences that add a point, example, or useful question |
| LinkedIn connection requests | 50 total | ICP fit plus a clear reason; blank request is allowed when the profile is a clean fit |
| Warm DMs | 5-15 total | Only to warm signals; no first-message pitch |
| X replies or quote posts | 20-30 total | Add a sharper framing, example, or useful disagreement |
| Saved ideas | 10-15 total | Each tagged using the consumer’s current content-type map |

For each day, provide:

- target audience lane
- 3-5 comment or reply targets
- connection-request batch description
- 1-3 warm follow-up drafts, if earned
- content-intelligence notes to capture
- golden-hour reply block for any post publishing that day (see below)

**Golden-hour reply loop:** the first 60-90 minutes after a post goes live largely determine its total reach, and authors who reply to comments in that window see roughly +30% engagement. For every publishing day, schedule a reply block immediately after the posting slot: draft a substantive reply to every comment (add value, ask a follow-up, or anchor the topic; never a bare thanks) for the author to approve and send. Comments are weighted roughly 15x likes, so this loop, not the posting itself, is the growth engine while the audience is small.

### 5. Sync With Content Production

Map the execution queue to the week's content:

- Use `content-calendar` for monthly alignment.
- Use `writing` for flagship articles and derivative social posts.
- Use `linkedin-post` for standalone hot takes, reader-intel posts, or operator POV posts.
- Use `ai-tool-review` for tool reviews.
- Use `visual-content`, `video-production`, or `creative-produce` when a Skill Drop or visual asset is part of the week.
- Use publishing runbooks or approved tools for scheduling drafts.

For X, do not merely cross-post LinkedIn copy. Compress the idea, sharpen the hook, and use replies or quote posts when the conversation context is the asset.

### 6. Prepare Human Approval Handoff

Before anything external happens, deliver:

- Queue summary and rationale
- Draft comments/replies/DMs where the configured assistant is proposing language
- Posts or post variants requiring review
- Any external URLs or profiles that need manual review
- Explicit list of actions grouped by required approver

If `{brain}/runbooks/social-approval-matrix.md` is present, route every action to the approver it names; that matrix is binding and overrides any default routing here. If it is absent, route all external actions to the entity owner.

### 7. Friday Review And Learning Capture

At the end of the week, produce a review that answers:

- What audience lane worked best?
- Which posts or comments generated qualified replies?
- Which connection sources had the best acceptance rate?
- Which X replies or quote posts created useful reach?
- What should be repeated, stopped, or tested next week?
- Which questions or objections should feed next week's content?

Grade the week against the expectation bands before judging any single metric. Founder-led social ramps on a known curve: first qualified inbound conversations typically arrive in weeks 4-8, real pipeline in months 4-6, and 3-5%/month follower growth with 4-8% engagement rate is healthy for a small account once established. State explicitly where the entity is on that ramp; a below-band week inside a normal ramp is variance, not failure, and the review should say so in plain words. The documented failure mode is a novice operator quitting at month 2 because a normal ramp looked like a flatline.

Save durable learnings in the weekly review artifact. Promote process-level lessons to the entity runbook; promote reusable lessons to this core skill only when they are generalizable.

## Quality Gates

- At least 70% of suggested targets should match the chosen ICP lane.
- No DM opener may pitch a service, paid product, or booking link in the first message.
- Comments must be specific enough that they could not be copied onto any post in the feed.
- Every post draft must contain at least one receipt: a concrete number, artifact, screenshot, or named real example. No receipt, no post. Purely generic AI-written posts earn roughly 45% fewer interactions; the receipt is the enforceable antidote.
- Weekly review must separate facts from hypotheses.
- Metrics should include at least one audience-quality signal, not only follower count.

## Failure Modes

| Failure | Response |
|---|---|
| No metrics access | Run qualitative review, log missing dataset, and ask the owner to connect or export the source. |
| Target list too cold | Reduce connection volume and focus on comments, replies, and peer-set visibility for one week. |
| Acceptance rate below target | Tighten ICP filters before increasing volume. |
| No qualified conversations | Revisit audience lane and content relevance; do not increase DM volume as the first fix. |
| External tool unavailable | Report the exact unavailable tool and provide a manual queue instead. |
