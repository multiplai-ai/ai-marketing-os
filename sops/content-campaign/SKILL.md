---
name: content-campaign
description: Plan and brief coordinated content campaigns for launches, series, and events — producing campaign briefs with launch tier assignments, GACCS briefs, asset lists, and success metrics.
---

# Content Campaign

Plan and brief coordinated content campaigns for launches, series, and events — producing campaign briefs with launch tier assignments, GACCS briefs, asset lists, and success metrics.

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/content/content-campaign.md (rich) + skills-core/skills/content/content-campaign.md (portable stub) on 2026-07-02.

**When to use:** When planning a coordinated content push — product launches, feature launches, content series, event promotions (webinar, workshop, conference talk), partnership announcements, brand moments, or any major thought-leadership push that needs more coordination than the regular calendar.

**Cadence:** As needed. Not a regular cadence — triggered by launches, series, or events.

**Recommended prerequisite:** Run `/content-strategy` first for pillars and distribution tiers. (Dependency: `content-strategy`.)

---

## Philosophy

This skill is **opinionated**. Campaigns fail when everything is treated as equally important. The tier system forces honest prioritization. Campaign scope should match strategic importance — not everything is a major launch.

**Core principles:**
1. **Not everything is a Tier 1 launch.** If everything is a big deal, nothing is. 1-2 Tier 1 campaigns per year, max.
2. **GACCS before assets.** Define what you're trying to achieve before listing what you need to make.
3. **Earned reach > paid reach for personal brands.** The LinkedIn flywheel (organic → Thought Leader Ads → engager qualification) compounds. Pure paid does not.
4. **Define failure upfront.** If you don't know what failure looks like, you can't learn from it.

---

## Required Context

- What is being launched or promoted
- Campaign type
- Dates and key milestones
- Directly responsible individual (DRI)
- Budget or amplification constraints
- Relevant content strategy and current calendar, if available

If strategy artifacts are missing, continue from user inputs and mark assumptions.

---

## Workflow Overview

```
/content-campaign runs:

1. LOAD CONTEXT       → Read content-strategy + current calendar
2. CAMPAIGN SCOPING   → Define what, type, when, DRI
3. LAUNCH TIER        → Assign Tier 1/2/3 based on scope
4. CAMPAIGN GACCS     → Full brief (goal, audience, creative, channels, stakeholders)
5. ASSET LIST         → Generate tier-appropriate asset list with owners + deadlines
6. LINKEDIN FLYWHEEL  → Plan organic → TL Ads → engager qualification (optional)
7. SUCCESS METRICS    → Define success and failure criteria
```

---

# Phase 1: Load Context

Before building a campaign, load relevant strategy and calendar context.

### Check for Artifacts

1. **Content Strategy:** `{brain}/strategy/content-strategy.md`
   - Extract: pillars, distribution tiers, perceptions, principles

2. **Current Calendar:** `{brain}/content/calendar-YYYY-MM.md` (current month)
   - Extract: theme, scheduled content, available slots

3. **Brand Strategy:** `{brain}/strategy/brand-strategy.md`
   - Extract: message hierarchy, key messages, USPs

Also review, where present: messaging hierarchy and any documented campaign constraints.

Resolve `{brain}` from the active entity binding; do not infer it from a brand
name in the request or silently substitute another entity. Paths are
repository-relative after resolution.

**Example (concrete paths):** for a brain named `organization`, these resolve to
`brains/organization/strategy/content-strategy.md`,
`brains/organization/content/calendar-2026-07.md`, and
`brains/organization/strategy/brand-strategy.md` when present.

**If strategy found:**
Display summary: "Loaded content strategy + [month] calendar. [N] slots available this month."

**If not found:**
Display: "No content strategy found. I'll work with your inputs. Recommend running `/content-strategy` for distribution tiers and pillar alignment."

Proceed regardless — campaigns can work standalone (mark assumptions when working without strategy artifacts).

---

# Phase 2: Campaign Scoping

Define the campaign's basic parameters: campaign name, campaign type, target audience, start/end dates and milestones, DRI, budget range, and business objective.

### Scoping Workshop

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMPAIGN SCOPING — What Are We Launching?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WHAT IS THE CAMPAIGN?
   What are you launching, promoting, or building momentum for?
   →

2. CAMPAIGN TYPE:
   [ ] Product launch (new product, feature, or major update)
   [ ] Content series (multi-part content with a theme)
   [ ] Event promotion (webinar, workshop, conference talk)
   [ ] Brand moment (milestone, announcement, thought leadership push)
   [ ] Partnership/collab (joint effort with another brand/person)

3. TIMELINE:
   - Start date: ___
   - End date: ___
   - Key milestone dates: ___

4. DRI (Directly Responsible Individual):
   Who owns this campaign end-to-end?
   →

5. BUDGET:
   - $0 (organic only)
   - $100-500 (light paid amplification)
   - $500-2000 (meaningful paid + tools)
   - $2000+ (significant investment)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# Phase 3: Launch Tier Assignment

Assign a tier based on campaign scope. The skill recommends; the user confirms. Ask for confirmation especially when the recommended tier changes asset scope, budget, or timeline.

### Launch Tier Framework

| Tier | Frequency | Scope | Channels | Assets | Budget |
|------|-----------|-------|----------|--------|--------|
| **Tier 1** | 1-2/year | All channels, multi-week buildup, maximum effort | All owned + paid + earned + outreach | 8-12 assets | $1000+ |
| **Tier 2** | 1/quarter | Email + social + 1-2 additional, dedicated assets | Owned + select paid | 4-6 assets | $200-1000 |
| **Tier 3** | Monthly+ | Publish + share on owned channels | Owned only | 2-3 assets | $0-200 |

### Tier Recommendation Logic

Score based on:

| Factor | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|
| Strategic importance | Critical to annual goals | Important to quarterly goals | Supports ongoing goals |
| Audience impact | New audience acquisition | Existing audience deepening | Audience maintenance |
| Revenue potential | Direct revenue or major pipeline | Pipeline contribution | Brand building |
| Effort justified | Yes — worth weeks of prep | Yes — worth a week of prep | Handled in normal flow |
| Novelty | First time, landmark moment | Notable but not unprecedented | Regular cadence |

### Display Format

```markdown
## Launch Tier Assignment

**Campaign:** [Name]
**Recommended Tier:** [1 / 2 / 3]

**Scoring:**
| Factor | Assessment | Points |
|--------|-----------|--------|
| Strategic importance | [Assessment] | [1-3] |
| Audience impact | [Assessment] | [1-3] |
| Revenue potential | [Assessment] | [1-3] |
| Effort justified | [Assessment] | [1-3] |
| Novelty | [Assessment] | [1-3] |
| **Total** | | **[X/15]** |

**Tier thresholds:** 12-15 = Tier 1 / 8-11 = Tier 2 / 5-7 = Tier 3

**What this tier means:**
- Channels: [What's included]
- Assets: [How many to create]
- Timeline: [How much prep time]
- Budget: [Expected investment]

Confirm tier or adjust?
```

---

# Phase 4: Campaign GACCS Brief

Build a full campaign brief using the GACCS framework (Goal, Audience, Creative, Channels, Stakeholders).

### Campaign GACCS Workshop

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMPAIGN GACCS BRIEF — [Campaign Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tier: [Assigned tier]

GOAL: What does success look like for this campaign?
  Be specific — a number, a behavior change, a milestone.
  → Primary goal: ___
  → Secondary goal: ___

AUDIENCE: Who is the primary audience?
  Not "everyone." The specific person who should care most.
  → Primary: ___
  → Secondary: ___

CREATIVE: What's the creative approach?
  → Campaign concept/tagline: ___
  → Key message (one sentence): ___
  → Tone: [Urgent / Exciting / Educational / Provocative / ___]
  → Visual approach: ___

CHANNELS: Where will this campaign run?
  (Pre-filled based on tier — owned, earned, paid, and partner channels as appropriate)
  Tier 1: All owned + paid + earned + outreach
  Tier 2: Owned + select paid
  Tier 3: Owned only
  → Specific channels: ___

STAKEHOLDERS: Who's involved?
  → DRI: ___
  → Contributors: ___
  → Reviewers/Approvers: ___
  → External partners: ___

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Display Format

```markdown
## Campaign Brief — [Campaign Name]

**Tier:** [1/2/3]
**Timeline:** [Start] → [End]
**DRI:** [Name]

| Element | Detail |
|---------|--------|
| **Goal (Primary)** | [Specific, measurable goal] |
| **Goal (Secondary)** | [Secondary goal] |
| **Audience (Primary)** | [Specific audience] |
| **Audience (Secondary)** | [Secondary audience] |
| **Creative Concept** | [Campaign concept/tagline] |
| **Key Message** | [One sentence] |
| **Tone** | [Tone descriptor] |
| **Channels** | [Channel list by tier] |

**Stakeholders:**
| Role | Who | Responsibility |
|------|-----|---------------|
| DRI | [Name] | Overall ownership |
| [Role] | [Name] | [What they do] |

Confirm brief or adjust?
```

---

# Phase 5: Asset List

Generate a tier-appropriate asset list with owners and deadlines. For each asset, capture: format, purpose, channel, owner, due date, dependencies, and review status. Avoid overbuilding for Tier 3 and underbuilding for Tier 1.

### Asset Templates by Tier

**Tier 1 Assets (8-12):**

| # | Asset | Format | Owner | Deadline | Status |
|---|-------|--------|-------|----------|--------|
| 1 | Teaser post (1 week before) | Social post | | | |
| 2 | Teaser post (3 days before) | Social post | | | |
| 3 | Launch anchor piece | Long-form article | | | |
| 4 | Launch announcement post | Social post (LinkedIn) | | | |
| 5 | Launch announcement post | Social post (Twitter) | | | |
| 6 | Email announcement | Newsletter | | | |
| 7 | Visual framework/infographic | Image | | | |
| 8 | Demo/walkthrough video | Loom / Video | | | |
| 9 | Week 2 follow-up post | Social post | | | |
| 10 | Customer/user spotlight | Social client piece | | | |
| 11 | Paid ad creative | Thought Leader Ad | | | |
| 12 | Outreach email template | DM / Email | | | |

**Tier 2 Assets (4-6):**

| # | Asset | Format | Owner | Deadline | Status |
|---|-------|--------|-------|----------|--------|
| 1 | Anchor piece | Long-form or guide | | | |
| 2 | Launch post (LinkedIn) | Social post | | | |
| 3 | Launch post (Twitter) | Social post | | | |
| 4 | Email announcement | Newsletter | | | |
| 5 | Supporting visual | Image/infographic | | | |
| 6 | Follow-up post (Day 3-5) | Social post | | | |

**Tier 3 Assets (2-3):**

| # | Asset | Format | Owner | Deadline | Status |
|---|-------|--------|-------|----------|--------|
| 1 | Main piece | Article / Post | | | |
| 2 | Social promo | LinkedIn + Twitter | | | |
| 3 | Email mention | Newsletter blurb | | | |

### Display Format

```markdown
## Asset List — [Campaign Name] (Tier [N])

| # | Asset | Format | Owner | Deadline | Status |
|---|-------|--------|-------|----------|--------|
[Populated based on tier + campaign specifics]

**Total assets:** [N]
**Timeline:** [First asset date] → [Last asset date]
**Dependencies:** [Any assets that depend on others]

Confirm asset list or adjust?
```

---

# Phase 6: Amplification — LinkedIn Flywheel (Optional)

Plan the amplification path: organic post → paid/boosted post → audience qualification → outreach/follow-up. The canonical implementation is the LinkedIn organic → Thought Leader Ads → engager qualification → outreach flywheel. Keep this phase optional and budget-aware.

**When to include:** Tier 1 and Tier 2 campaigns with budget for LinkedIn Thought Leader Ads. Skip for Tier 3 or $0 budget campaigns.

### The LinkedIn Flywheel

```
Step 1: ORGANIC POST
  Publish anchor content on LinkedIn
  Goal: Initial engagement (likes, comments, shares)
       ↓
Step 2: THOUGHT LEADER ADS
  Boost the organic post as a Thought Leader Ad
  Target: ICP-matched audience (from content strategy)
  Budget: [Based on campaign budget]
  Goal: Expand reach beyond organic network
       ↓
Step 3: ENGAGER QUALIFICATION
  Build audience of people who engaged with the boosted post
  Filter: Title, company size, industry matches ICP
  Goal: Identify high-quality prospects
       ↓
Step 4: OUTREACH
  Warm outreach to qualified engagers
  Message: Reference specific engagement, offer value
  Goal: Start conversations, not pitch
```

### Flywheel Plan Template

```markdown
## LinkedIn Flywheel — [Campaign Name]

### Step 1: Organic Post
- **Content:** [Which campaign asset]
- **Publish date:** [Date]
- **Engagement target:** [N] likes, [N] comments

### Step 2: Thought Leader Ads
- **Post to boost:** [Same post or specific variation]
- **Budget:** $[X] over [N] days
- **Targeting:**
  - Titles: [Target titles]
  - Company size: [Range]
  - Industry: [Industries]
- **Expected reach:** [Estimate based on budget]

### Step 3: Engager Qualification
- **Wait period:** [3-5 days after ad starts]
- **Qualification criteria:**
  - Engagement type: [Comment > Like > View]
  - ICP match: [Minimum criteria]
  - Action: [Save to list / tag in CRM]

### Step 4: Outreach
- **Channel:** [LinkedIn DM / Email]
- **Message template:** [Personalized — reference their comment/engagement]
- **Timing:** [When to reach out — within [N] days of engagement]
- **Goal:** [Conversation, not pitch]

**Total Flywheel Budget:** $[X]
**Expected Qualified Engagers:** [Estimate]
```

---

# Phase 7: Success Metrics

Define what success AND failure look like for this campaign. Document: primary success metric, secondary success metric, leading indicators, failure threshold, qualitative signal, and post-campaign review date.

### Metrics Framework

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUCCESS METRICS — [Campaign Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Define targets for each level:

SUCCESS looks like:
  → Primary metric: ___ (target: ___)
  → Secondary metric: ___ (target: ___)
  → Leading indicators: ___
  → Qualitative signal: ___

GOOD ENOUGH looks like:
  → Minimum viable outcome: ___

FAILURE looks like:
  → Below this, we learn and adjust: ___
  → Root cause to investigate if failure: ___

LEARNING GOALS (regardless of outcome):
  → What do we want to learn from this campaign?
  → What hypothesis are we testing?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Display Format

```markdown
## Success Metrics — [Campaign Name]

| Level | Metric | Target | How Measured |
|-------|--------|--------|-------------|
| **Success** | [Primary metric] | [Target] | [Measurement method] |
| **Success** | [Secondary metric] | [Target] | [Measurement method] |
| **Leading indicator** | [Early signal] | [Target] | [Measurement method] |
| **Good enough** | [Minimum viable] | [Threshold] | [Measurement method] |
| **Failure** | [Below this threshold] | [Number] | [Measurement method] |

**Qualitative Success Signal:** [What does "feeling like it worked" look like?]

**Learning Goals:**
- [Hypothesis being tested]
- [What we'll know after, regardless of outcome]

**Post-Campaign Review Date:** [Date — 1-2 weeks after campaign ends]
```

---

# Output Artifacts

### Primary Output File

Save to: `{brain}/content/campaigns/campaign-[name]-YYYY-MM-DD.md`

Use a slugified version of the campaign name (lowercase, hyphens).

### Output Structure

```markdown
---
title: Campaign Brief — [Campaign Name]
tier: [1/2/3]
type: [launch/series/event/brand-moment/partnership]
timeline: [Start] → [End]
status: draft
strategy: content-strategy.md
created: YYYY-MM-DD
---

# Campaign Brief — [Campaign Name]

## Executive Summary
[2-3 sentences: What this is, what tier, key goal, timeline]

---

## 1. Campaign Scope
[From Phase 2]

## 2. Launch Tier
[From Phase 3 — tier assignment with scoring]

## 3. Campaign Brief (GACCS)
[From Phase 4]

## 4. Asset List
[From Phase 5 — with owners and deadlines]

## 5. LinkedIn Flywheel
[From Phase 6 — if applicable]

## 6. Success Metrics
[From Phase 7 — with success/failure definitions]

---

## Campaign Checklist

- [ ] GACCS brief approved
- [ ] All assets assigned to owners
- [ ] Asset deadlines set
- [ ] Distribution channels confirmed
- [ ] Paid budget approved (if applicable)
- [ ] Success metrics agreed
- [ ] Post-campaign review scheduled

---

## Next Steps

This campaign connects to:
- **Content Calendar** (`/content-calendar`) — Overlay campaign onto monthly calendar
- **Writing** (`/writing`) — Produce campaign content pieces
- **Visual Content** (`/visual-content`) — Create campaign visuals
- **Publish** (`/publish`) — Schedule and publish campaign content

---

## Methodology Notes

Built using the organization Content System:
- Launch Tiers (1/2/3)
- GACCS Brief (Goal, Audience, Creative, Channels, Stakeholders)
- LinkedIn Flywheel (Organic → TL Ads → Engager Qualification → Outreach)
- Asset list templates by tier
- Success/failure metric definition
```

> Entity note ({brain}=brand): the methodology label "organization Content System" is inherited from the original organization-authored command; keep or rebrand the label per brain, but the frameworks themselves (Launch Tiers, GACCS, LinkedIn Flywheel) are entity-generic.

---

# Quality Checklist

Before finalizing, verify:

- [ ] Campaign type is clearly defined (launch, series, event, brand moment, partnership)
- [ ] Tier assignment is honest (not everything is Tier 1)
- [ ] GACCS brief has all 5 elements filled with specifics (no "TBD") — and is complete before asset production begins
- [ ] Asset list matches the assigned tier (not over-scoped for Tier 3, not under-scoped for Tier 1)
- [ ] Every asset has a purpose, an owner, and a deadline
- [ ] Success metrics include a failure definition (not just success)
- [ ] LinkedIn flywheel is included only when budget supports it
- [ ] Post-campaign review date is scheduled
- [ ] Campaign connects to content calendar (doesn't exist in isolation)
- [ ] Timeline is realistic given asset count and available resources

---

# Anti-Patterns (Never Do)

**DON'T:**
- Treat every launch as Tier 1 (inflation kills urgency)
- Skip the GACCS brief ("we'll figure it out as we go")
- Create 12 assets for a Tier 3 campaign (scope matches tier)
- Define only success metrics (define failure too)
- Plan the LinkedIn flywheel without budget for Thought Leader Ads
- Launch a campaign disconnected from the content calendar
- Create assets without owners or deadlines

**DO:**
- Be honest about tier assignment (most things are Tier 2 or 3)
- Complete the GACCS brief before listing assets
- Match asset count to tier scope
- Define what failure looks like so you can learn from it
- Use the LinkedIn flywheel only when budget supports it
- Overlay campaigns onto the existing calendar
- Schedule a post-campaign review

---

# Quick Actions

After running `/content-campaign`:

- "Upgrade to Tier [N]" → Re-scopes campaign for a different tier
- "Add asset: [description]" → Adds asset to the list with owner/deadline
- "Build flywheel plan" → Creates LinkedIn flywheel (if skipped initially)
- "Adjust timeline to [dates]" → Re-sequences asset deadlines
- "Generate outreach template" → Creates warm outreach DM template for flywheel
- "Overlay on calendar" → Shows how campaign fits into current month's content calendar
- "Export to Notion" → Formats for Notion page creation

---

# Portability & Adaptation Notes

From the portable stub — guidance for running this skill outside Claude Code:

- ChatGPT Projects work well when multiple reviewers need to shape messaging and assets.
- Codex is useful for overlaying a campaign against local calendar files.
- MCP surfaces should keep production exports optional because every team uses different systems (tool contracts: `optional_calendar_overlay`, `optional_production_database_export`).
