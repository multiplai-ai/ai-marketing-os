---
name: content-calendar
description: Build a focused monthly content calendar from your content strategy — a 4-week calendar with themed content, GACCS briefs, distribution plans, and mileage maps, with production constraints enforced.
---

# Content Calendar

Build a focused monthly content calendar from your content strategy — a 4-week calendar with themed content, GACCS briefs, distribution plans, and mileage maps, with production constraints enforced.

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/content/content-calendar.md (rich) + skills-core/skills/content/content-calendar.md (portable stub) on 2026-07-02.

**When to use:** At the start of each month to plan that month's content production. Pull from content strategy for pillars, shows, and themes. Also useful whenever the team needs to align production, review, distribution, and repurposing before drafting.

**Cadence:** Monthly. Run in the last week of the preceding month.

**Recommended prerequisite:** Run `/content-strategy` first. Can work without it using defaults.

---

## Philosophy

This skill is **opinionated**. It enforces constraints that prevent the most common content failures: overproduction, lack of focus, and zero repurposing.

**Core principles:**
1. **One theme, one month.** A month-long theme creates compounding — each piece reinforces the others.
2. **Anchor first, derivatives second.** Start with the best piece and extract everything else from it.
3. **Redistribute, don't just create.** At least 2 slots per month should feature existing content, not new.
4. **Constraints are features.** Max 5 new pieces per week. The 30% juice rule. These protect quality.
5. **Plan fewer pieces with more mileage.** A good calendar focuses attention, compounds a theme, and leaves room for timely work.

---

## Required Context

- Target month
- Content strategy, if available (`{brain}/strategy/content-strategy.md`)
- Brand or messaging strategy, if available (`{brain}/strategy/brand-strategy.md`)
- Recent production or publishing log (`{brain}/content/production-log.md`)
- Team capacity and review constraints

---

## Workflow Overview

```
/content-calendar runs:

1. LOAD STRATEGY     → Read content-strategy artifact
2. THEME SELECTION   → Pick monthly theme from strategy rubric
3. GACCS BRIEF       → Full brief for the month's anchor piece
4. CALENDAR BUILD    → Map 4 weeks x shows (from strategy)
5. DISTRIBUTION PLAN → Assign tiers + channels per piece
6. MILEAGE MAP       → Plan repurposing chain (1 anchor → 3+ derivatives)
7. EXISTING CONTENT  → Identify redistribution slots
8. APPROVE & EXPORT  → Human review, production handoff, optional publishing
```

---

# Phase 1: Load Strategy Context

Before building the calendar, load the content strategy.

### Check for Content Strategy

Look for: `{brain}/strategy/content-strategy.md`

> Example ({brain}=brand): `brains/brand/strategy/content-strategy.md`

**If found:**
Extract:
- Content pillars (with funnel + perception mapping)
- Perception goals
- Show definitions (cadences, platforms, formats)
- Distribution tier defaults and channel defaults
- Monthly theme rubric
- Pillar rotation tracker (last featured dates)
- Content principles

Display summary and confirm: "Strategy loaded. Ready to build the [Month] calendar?"

**If not found:**
Proceed with clearly labeled assumptions and recommend creating a strategy before finalizing.

>
> Display: "No content strategy found. I'll use defaults:
> - **Pillars:** AI-Native Growth Systems, Healthcare Growth Playbooks, Scaling-Stage Lessons, Industry POV, Builder Stories
> - **Shows:** Saturday essay, Monday engagement, Wednesday visual, Thursday promo
> - **Distribution:** Substack + LinkedIn + Twitter (Tier 1)
>
> Recommend running `/content-strategy` for a stronger foundation. Proceed with defaults? [Yes/No]"

### Also Load

- `{brain}/strategy/brand-strategy.md` — for message hierarchy and perceptions (if exists)
- `{brain}/content/production-log.md` — to check what's been published recently (if exists)

---

# Phase 2: Monthly Theme Selection

Pick the theme for this month using the strategy's rubric.

### Theme Generation

Generate 3-4 candidate themes based on:

1. **Pillar Rotation (40%):** Which pillar hasn't been featured recently? Check rotation tracker.
2. **Perception Reinforcement (35%):** Which perception statement needs the most reinforcement? Check if any perception has been underserved.
3. **Timeliness (25%):** What's happening in the market/industry that creates urgency or relevance?

As a tie-breaker between closely scored candidates, favor the theme with the most **available client, stories, or assets** already on hand.

Recommend one theme and explain the tradeoff. Ask for confirmation if the theme choice materially changes the calendar.

### Display Format

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONTHLY THEME CANDIDATES — [Month Year]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on your strategy, here are theme candidates:

1. [THEME NAME]
   Pillar: [Pillar] (last featured: [Month])
   Perception: [Which perception it serves]
   Timeliness: [Why now]
   Score: [Weighted score]

2. [THEME NAME]
   Pillar: [Pillar] (last featured: [Month])
   Perception: [Which perception it serves]
   Timeliness: [Why now]
   Score: [Weighted score]

3. [THEME NAME]
   Pillar: [Pillar] (last featured: [Month])
   Perception: [Which perception it serves]
   Timeliness: [Why now]
   Score: [Weighted score]

RECOMMENDED: #[N] — [Why this is the top pick]

Which theme for [Month]?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# Phase 3: GACCS Brief (Anchor Piece)

Build a full brief for the month's anchor piece using the GACCS framework.

### The GACCS Framework

Every anchor piece needs five elements defined upfront:

| Element | Question | Why It Matters |
|---------|----------|---------------|
| **Goal** | What business outcome does this piece serve? | Connects content to strategy |
| **Audience** | Who specifically is this for? | Prevents "everyone" thinking |
| **Creative** | What's the angle, format, and hook? | Ensures differentiation |
| **Channels** | Where will this be published and distributed? | Prevents "publish and pray" |
| **Stakeholders** | Who needs to review, contribute, or approve? | Prevents bottlenecks |

### GACCS Brief Workshop

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GACCS BRIEF — [Month] Anchor Piece
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Theme: [Selected theme]

GOAL: What should this piece achieve?
  Options: Build awareness, establish expertise, generate leads,
  start conversations, drive sign-ups
  → [User input or pre-fill from strategy]

AUDIENCE: Who is this piece FOR?
  Be specific — role, stage, mindset.
  → [User input or pre-fill from ICP]

CREATIVE: What's the angle?
  - Working title: ___
  - Format: [Essay / Guide / Framework / Case study / Manifesto]
  - Hook concept: [What makes someone stop and read?]
  - Core argument: [The one thing the reader should believe after reading]

CHANNELS: Where does this go?
  - Primary: [From Tier 1 defaults]
  - Extended: [From Tier 2 — which channels for this specific piece?]
  - Amplification: [From Tier 3 — is this piece worth paid/outreach?]

STAKEHOLDERS: Who's involved?
  - Writer: [DRI]
  - Reviewer: [If applicable]
  - Contributors: [If applicable]
  - Design: [If visual assets needed]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Display Format

```markdown
## GACCS Brief — [Month] Anchor

**Title:** [Working title]
**Theme:** [Monthly theme]
**Pillar:** [Content pillar]

| Element | Detail |
|---------|--------|
| **Goal** | [Specific goal] |
| **Audience** | [Specific audience] |
| **Creative** | [Format + hook + core argument] |
| **Channels** | Tier 1: [channels] / Tier 2: [channels] / Tier 3: [channels] |
| **Stakeholders** | Writer: [X] / Reviewer: [X] |

**Publish Target:** [Week of month + day]

Confirm brief or adjust?
```

---

# Phase 4: 4-Week Calendar Build

Map content across 4 weeks using the show definitions from strategy.

### Calendar Generation Logic

For each week:
1. Map shows to the weekly schedule (from strategy or defaults)
2. Tie each piece to the monthly theme (different angle per week)
3. Designate the anchor piece week (usually Week 1 or 2)
4. Include redistribution slots (at least 2/month)
5. Include flex slots (1-2/month for reactive/timely content)

Plan anchor-first, then derivative pieces. Keep the total realistic for the available team capacity and review constraints.

### Constraint Enforcement

**Before generating, check these rules:**

| Constraint | Rule | What Happens if Violated |
|-----------|------|------------------------|
| **Max pieces/week** | ≤ 5 new pieces per week | Push back: "That's [N] pieces in Week [X]. Which one should we drop or move?" |
| **30% juice rule** | ≤ 30% product-focused pieces in the month | Warn: "[N]% of pieces are product-focused. That's above the 30% guideline. Which ones should shift to educational?" |
| **Redistribution** | ≥ 2 redistribution slots per month | Warn: "No redistribution slots. Which weeks should feature existing content instead of new?" |
| **Anchor derivatives** | Anchor must generate ≥ 3 derivative pieces | Warn: "Only [N] derivatives from the anchor. Add mileage slots." |
| **Flex slots** | 1-2 slots/month for reactive content | Note: "No flex slots. Consider leaving 1 slot open for timely content." |

### Display Format

```markdown
## [Month Year] Content Calendar

**Theme:** [Monthly theme]
**Anchor Piece:** [Title]
**Pillar:** [Primary pillar]

### Week 1: [Date Range]

| Day | Type | Title/Topic | Platform | Status |
|-----|------|-------------|----------|--------|
| Sat | Flagship Essay | [Title — angle for week 1] | Substack + Twitter | New |
| Mon | Engagement | [Topic] | LinkedIn + Twitter | New |
| Wed | Visual | [Visual concept] | LinkedIn + Twitter | New |
| Thu | Promo/Lead Magnet | [Topic] | LinkedIn + Twitter | New |

### Week 2: [Date Range]

| Day | Type | Title/Topic | Platform | Status |
|-----|------|-------------|----------|--------|
| Sat | Flagship Essay | [Title — angle for week 2] | Substack + Twitter | New |
| Mon | Engagement | [Topic] | LinkedIn + Twitter | Redistribute |
| Wed | Visual | [Visual concept] | LinkedIn + Twitter | New |
| Thu | Promo/Lead Magnet | [Topic] | LinkedIn + Twitter | New |

### Week 3: [Date Range]
[Same format]

### Week 4: [Date Range]
[Same format]

---

**Production Summary:**
- Total new pieces: [N]
- Redistributed pieces: [N]
- Flex slots: [N]
- Product-focused: [N/total] ([%]) — [OK / Warning]
- Anchor derivatives: [N] — [OK / Warning]
```


---

# Phase 5: Distribution Plan

Assign distribution tiers and channels to each piece on the calendar.

### Default Assignment

Using distribution tier defaults from content strategy:
- **All pieces:** Tier 1 channels (publish on primary platforms)
- **Strong pieces:** Add Tier 2 channels (extended distribution)
- **Anchor + best performer:** Tier 3 channels (paid/outreach amplification)

For each piece, define:
- Primary channel
- Secondary channels
- Amplification plan (if any)
- Reuse or republishing opportunity
- Owner and production date

### Display Format

```markdown
## Distribution Plan — [Month]

### Tier 1 (Every Piece)
All [N] pieces publish to: [Tier 1 channel list]

### Tier 2 (Extended — [N] pieces)
| Piece | Additional Channels | Why |
|-------|-------------------|-----|
| [Title] | [Channels] | [Rationale] |
| [Title] | [Channels] | [Rationale] |

### Tier 3 (Amplification — [N] pieces)
| Piece | Amplification | Budget | Expected Reach |
|-------|--------------|--------|---------------|
| [Anchor piece] | [Channel — e.g., TL Ads] | [Budget] | [Estimate] |

Confirm distribution plan or adjust?
```

---

# Phase 6: Mileage Map

Plan the repurposing chain for the anchor piece.

### The Mileage Principle

One excellent piece of content should generate 3+ derivative pieces. This is how you get more mileage without more effort.

Derivative types to consider: social posts and excerpts, short-form clips or carousels, visual frameworks, engagement posts, email or newsletter mentions, sales enablement or lead magnet fragments, and guest pitches.

### Mileage Map Template

```markdown
## Mileage Map — [Anchor Piece Title]

**Source:** [Anchor piece — format, word count, platform]

### Derivative Chain

[Anchor Piece]
  ├── Social excerpt 1 → LinkedIn (key insight, 150 words)
  ├── Social excerpt 2 → Twitter thread (3-5 tweets)
  ├── Visual framework → LinkedIn + Twitter (infographic from core model)
  ├── Engagement post → LinkedIn (poll or hot take from contrarian angle)
  ├── Email teaser → Newsletter (excerpt + link)
  ├── [Optional] Short-form clip or carousel → [Platform]
  ├── [Optional] Lead magnet / sales enablement fragment → [Asset]
  └── [Optional] Guest pitch → [Publication] (reframe for their audience)

### Derivative Details

| # | Derivative | Platform | Source Section | Publish Date |
|---|-----------|----------|---------------|-------------|
| 1 | [Description] | [Platform] | [Which part of anchor] | [Date] |
| 2 | [Description] | [Platform] | [Which part of anchor] | [Date] |
| 3 | [Description] | [Platform] | [Which part of anchor] | [Date] |

**Total mileage:** 1 anchor → [N] derivatives
```

---

# Phase 7: Existing Content Check

Identify content to redistribute (not just new creation). Review recently published or evergreen content and choose redistribution candidates before adding more net-new work.

### The "Default to Less" Principle

Before creating new content for every slot, check what already exists that could be:
- **Reshared** — High-performing past content shared again (with new intro)
- **Updated** — Older content refreshed with new data or examples
- **Reframed** — Same core idea, different angle or format
- **Compiled** — Multiple related pieces combined into a guide

### Existing Content Workshop

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXISTING CONTENT — What Can We Redistribute?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Think about content you've already published that:

1. PERFORMED WELL — What got the most engagement/shares/replies?
   →

2. IS STILL RELEVANT — What older piece is just as true today?
   →

3. FITS THE THEME — What existing content connects to "[theme]"?
   →

4. DESERVES A SECOND LIFE — What did you put work into but didn't get enough reach?
   →

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Slot Assignment

After user responds, assign redistribution content to specific calendar slots:

```markdown
## Redistribution Slots — [Month]

| Week | Day | Original Piece | Redistribution Type | New Angle |
|------|-----|---------------|-------------------|-----------|
| [W] | [Day] | "[Original title]" | Reshare / Update / Reframe | [How it's repackaged] |
| [W] | [Day] | "[Original title]" | Reshare / Update / Reframe | [How it's repackaged] |

**New vs. Redistributed:** [N] new / [N] redistributed = [ratio]
```

---

# Phase 8: Export to Production

After calendar approval, export to production systems for tracking and scheduling. Publishing integrations are optional — the calendar artifact stands alone if export tooling isn't configured for this entity.

### Step 1: Notion Production Database

Push the calendar to a Notion database — one card per content piece + associated assets.

"Push to Notion? This creates one card per content piece + associated assets for monthly visibility."

```bash
# Preview what will be created
python3 tools/notion_content_db.py --publish <calendar-file> --dry-run

# Create all items in Notion
python3 tools/notion_content_db.py --publish <calendar-file>
```

This creates:
- Content items with: show, channel, pillar, publish date, CTA, status
- Asset items for every downloadable/DM deliverable (linked to parent content)
- Status tracking: To Produce → Produced → Scheduled → Published


### Step 2: Bulk Production Sessions

Produce content by channel/format (not weekly):

1. **Session 1:** All long-form articles — use `/writing`
2. **Session 2:** All social posts — use `/writing`
3. **Session 3:** All visuals — use `/visual-content`
4. **Session 4:** All assets (lead magnets, downloadables, offers)

As each piece is produced, update Notion status to "Produced."


### Step 3: Push to Platforms

After production is complete, push to scheduling tools:

**Social posts → Metricool:**
```bash
# Preview schedule
python3 tools/metricool_publisher.py --dry-run {brain}/content/social-posts-YYYY-MM.json

# Push all social posts with scheduled dates/times
python3 tools/metricool_publisher.py --publish {brain}/content/social-posts-YYYY-MM.json

# Or extract directly from calendar (placeholder text — needs writing first)
python3 tools/metricool_publisher.py --from-calendar <calendar-file> --dry-run
```

**Long-form articles → Substack drafts:**
```bash
# Preview
python3 tools/substack_publisher.py --draft {brain}/content/build-log-YYYY-MM-DD.md --dry-run

# Create draft
python3 tools/substack_publisher.py --draft {brain}/content/build-log-YYYY-MM-DD.md
```

> Example ({brain}=brand): `python3 tools/metricool_publisher.py --publish brains/brand/content/social-posts-2026-07.json`

After pushing, update Notion status to "Scheduled."

### First-Time Setup

Before first use, set up the Notion database:
```bash
python3 tools/notion_content_db.py --setup --parent-page-id <NOTION_PAGE_ID>
```
Then add the returned database ID to `.env` as `NOTION_CONTENT_DB_ID`.

For Metricool: sign up for Advanced plan ($47-59/mo), add `METRICOOL_API_TOKEN` to `.env`.
For Substack: add `SUBSTACK_EMAIL`, `SUBSTACK_PASSWORD`, `SUBSTACK_SUBDOMAIN` to `.env`.

---

## Monthly Batch and Publishing Handoff

Use this handoff after the calendar itself is approved. It converts an approved
plan into a reviewable production batch while keeping strategy, production,
and live engagement responsibilities explicit.

### 1. Assign operating lanes

Name the owner for each lane; do not hardcode people or platforms in this
reusable skill.

| Lane | Responsibility |
|---|---|
| Strategy / long-form | Supplies the approved theme, source material, anchor brief, CTA rules, and final strategic review |
| Production / social | Drafts the approved batch, adaptations, metadata, and supporting assets |
| Live engagement | Handles replies, timely posts, substitutions, and audience feedback that cannot be safely pre-scheduled |

One person may own more than one lane, but every lane must have an explicit
owner and review window.

### 2. Assemble the source packet

Production starts only when the packet includes:

- approved monthly theme and anchor GACCS brief
- content strategy, voice guidance, and conversion pathway
- approved source material, client, links, and factual constraints
- calendar dates, channels, target formats, and CTA rules
- production capacity, reviewers, deadlines, and known blackout dates
- recent exemplars, anti-patterns, and performance notes

Flag missing inputs and assumptions before drafting. Never invent client,
customer examples, or approval.

### 3. Lock the batch mix

Turn the calendar into an explicit format-and-count table. Separate planned
batch items from a small real-time reserve for reactive work.

| Format / channel | Planned count | Source | Owner | Review gate |
|---|---:|---|---|---|
| [Format] | [N] | [Anchor / approved source] | [Owner] | [Reviewer] |

Re-run the calendar constraints after substitutions: no more than five
net-new pieces per week, at least two redistribution slots, at least three
anchor derivatives, one or two flex opportunities, and no more than 30%
conversion-oriented content.

### 4. Build production records

Each batch item must carry enough metadata to review and schedule without
guesswork:

- unique ID, working title, channel, format, and planned date
- theme, pillar, perception, source, and relationship to the anchor
- draft copy plus visual or asset requirements
- CTA, destination, owner, reviewer, and status
- factual citations or client notes where required
- adaptation notes when one idea appears on multiple channels

Use the entity's approved artifact format (Markdown, JSON, database, or
spreadsheet). Tool choice belongs in the entity binding, not this skill.

### 5. Human review gate

Present the complete batch for item-level **Approve**, **Revise**, or **Reject**
decisions. Do not schedule, publish, send, or create external drafts until the
authorized reviewer has approved the relevant item. Record requested changes
and rerun any affected constraint checks.

Construction feedback should update a small feedback ledger:

| Item | Decision | Feedback | Durable update |
|---|---|---|---|
| [ID] | Approve / Revise / Reject | [Reason] | Exemplar / anti-pattern / rule / none |

Promote repeated feedback into the entity's voice exemplars, anti-patterns, or
production rules so the next batch improves.

### 6. Schedule approved items only

After approval, export only approved records through configured scheduling or
draft tools. Use a dry run where available, then spot-check dates, channels,
links, media, formatting, time zones, and approval status. Record external IDs
or URLs in the production record. Failed or unapproved items remain drafts.

### 7. Log live substitutions

When the live-engagement owner replaces or adds a timely item, log what changed,
why, who approved it, and which planned item moved or was dropped. Recheck the
weekly load and conversion ratio rather than silently expanding the calendar.

### 8. Close the month

At month end, attach available reach, engagement, conversion, qualitative
feedback, and production-effort evidence. Record Continue / Change / Stop
recommendations and update the production log, redistribution candidates, and
next planning packet.

The durable monthly package contains the approved calendar, source packet,
production batch, review decisions, scheduling receipts, substitution log, and
performance notes.

Monthly execution is complete only when:

- [ ] every batch item traces to an approved strategy source
- [ ] the format mix and capacity constraints pass
- [ ] each item has an explicit human decision
- [ ] only approved items were exported or scheduled
- [ ] scheduling spot-checks and receipts were recorded
- [ ] live substitutions were logged
- [ ] feedback and month-end evidence were carried into the next cycle

---

# Output Artifacts

### Primary Output File

Save to: `{brain}/content/calendar-YYYY-MM.md`

> Example ({brain}=brand): `brains/brand/content/calendar-2026-07.md`

### Output Structure

```markdown
---
title: Content Calendar — [Month Year]
theme: [Monthly Theme]
pillar: [Primary Pillar]
strategy: content-strategy.md
created: YYYY-MM-DD
status: draft
---

# Content Calendar — [Month Year]

## Executive Summary
[2-3 sentences: Theme, anchor piece, key stats (total pieces, new vs. redistributed)]

---

## 1. Monthly Theme
[From Phase 2 — theme selection with rationale]

## 2. Anchor Brief (GACCS)
[From Phase 3]

## 3. 4-Week Calendar
[From Phase 4 — full calendar with constraint checks]

## 4. Distribution Plan
[From Phase 5]

## 5. Mileage Map
[From Phase 6 — anchor repurposing chain]

## 6. Redistribution Slots
[From Phase 7]

---

## Production Checklist

- [ ] Anchor piece drafted by [date]
- [ ] Week 1 content ready by [date]
- [ ] Week 2 content ready by [date]
- [ ] Week 3 content ready by [date]
- [ ] Week 4 content ready by [date]
- [ ] All visuals created
- [ ] Distribution plan executed per tier assignments

---

## Next Steps

This calendar connects to:
- **Writing** (`/writing`) — Run weekly to produce each piece
- **Content Campaign** (`/content-campaign`) — If a campaign overlaps this month
- **Visual Content** (`/visual-content`) — For weekly infographics

---

## Methodology Notes

Built using the organization Content System:
- GACCS Brief (Goal, Audience, Creative, Channels, Stakeholders)
- 4 Parallel Streams calendar framework
- Distribution Tiers (1/2/3)
- Mileage / Repurposing chains
- "Default to less" redistribution principle
```

---

# Quality Checklist

Before finalizing, verify:

- [ ] Monthly theme is specific enough to guide 4 weeks of content
- [ ] GACCS brief has all 5 elements filled (no blanks)
- [ ] Max 5 new pieces per week (constraint enforced)
- [ ] At most 30% product-focused pieces (juice rule enforced)
- [ ] At least 2 redistribution slots in the month
- [ ] Anchor piece generates 3+ derivatives (mileage map complete)
- [ ] 1-2 flex slots left for reactive/timely content
- [ ] Every piece has a distribution tier assigned
- [ ] Every piece has a role, not just a date
- [ ] Calendar connects to content strategy pillars and perceptions
- [ ] Calendar is realistic for the available team capacity
- [ ] Production dates are realistic

---

# Anti-Patterns (Never Do)

**DON'T:**
- Plan 7+ new pieces per week ("just to have options")
- Make every piece product-focused (violates 30% rule)
- Create all new content with zero redistribution
- Build a calendar disconnected from content strategy
- Skip the GACCS brief ("I'll figure it out when I write it")
- Treat the mileage map as optional
- Fill every slot — leave room for reactive content

**DO:**
- Start with the anchor piece and derive everything else
- Enforce constraints — they protect quality
- Include redistribution slots every month
- Connect every piece to the monthly theme
- Use the GACCS brief to prevent "blank page" syndrome
- Leave flex slots for timely content
- Track what performs for next month's redistribution

---

# Quick Actions

After running `/content-calendar`:

- "Adjust theme to [X]" → Regenerates calendar with new theme
- "Swap [piece] for [piece]" → Moves content between weeks/slots
- "Add a campaign overlay" → Integrates `/content-campaign` into the calendar
- "Generate GACCS for Week [N]" → Builds brief for a non-anchor piece
- "Show mileage for [piece]" → Builds repurposing chain for any piece
- "Flag as product-focused" → Re-checks 30% juice rule
- "Export to Notion DB" → Creates production cards in Notion content database
- "Push social to Metricool" → Schedules all social posts in Metricool
- "Push articles to Substack" → Creates article drafts in Substack

---

# Portability Notes

From the portable stub — guidance for running this skill outside the primary harness:

- ChatGPT Projects work well for collaborative calendar review and stakeholder input.
- Codex is useful when the calendar depends on local strategy files, CSV exports, or production logs.
- MCP clients can expose this as a reusable planning workflow while keeping publishing integrations optional.
