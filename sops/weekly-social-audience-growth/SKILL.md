---
name: weekly-social-audience-growth
description: Run a weekly social audience-growth review and execution queue for configured LinkedIn and X channels.
metadata:
  title: Weekly Social Audience Growth
  type: recurring-runbook
  channels:
  - LinkedIn
  - X
  created: 2026-07-06
  status: active
  core_skill: social-audience-growth-weekly
---

# Weekly Social Audience Growth

Use this runbook for the consumer's configured publishing accounts, audience,
content roles and social channels. Resolve `{brain}`, the content owner, drafting
assistant, scheduler and approval rules from current consumer configuration.
Do not assume two contributors, named profiles, paid tooling or live connections.

Help the configured audience encounter useful, specific work aligned with the consumer's strategy.

## Existing Skill Stack

Use these existing skills in this order:

| Job | Skill Or Asset | Use |
|---|---|---|
| Strategy foundation | `content-strategy` | Quarterly/monthly pillar, audience, perception, and show strategy. |
| Monthly planning | `content-calendar` | Turns strategy into a 4-week publishing plan. |
| Weekly flagship + derivatives | `writing` | Produces Build Log/newsletter/article drafts and derivative LinkedIn/X ideas. |
| Single LinkedIn post | `linkedin-post` | Turns one idea, transcript, or hot take into a polished LinkedIn post. |
| Tool review content | `ai-tool-review` | Produces tool reviews and promo social posts. |
| Visual or video support | `visual-content`, `video-production`, `creative-produce` | Produces graphics, Skill Drop assets, and content visuals when needed. |
| Production orchestration | `content-produce` | Moves content from brief through draft, QC, visual, and publishing handoff. |
| Audience growth wrapper | `social-audience-growth-weekly` | Coordinates targeting, engagement, connection requests, X replies, metrics, and learning capture. |

Resolve supporting assets from the consumer's `{brain}`: its audience-growth
playbook, content strategy, research, approved tools and connection status. Core
publisher tools are available options; use the configured provider and verify
access. No scheduler or automation provider is universally active or retired.

Programming: resolve show names and cadence from the current consumer strategy and content calendar. Historical lineups are not defaults.

Targeting tooling: verify which account features and saved searches the consumer has. Use available mechanics and label missing access; do not presume a paid subscription is live.

## Drafting assistant scope

The drafting assistant owns:

- weekly target-audience focus
- social metrics review and learning capture
- comment, reply, connection, and warm-DM queue preparation
- draft language for comments, replies, DMs, and post variants
- content intelligence from LinkedIn, X, peer creators, and competitive tools
- routing the week's learnings back into the content calendar and writing workflow

The drafting assistant does not send, follow, connect, comment, reply, DM, schedule, or delete externally without owner approval unless a later approved automation grants that authority.

## Audience Lanes

Default priority order:

1. PE-backed CMOs, CCOs, VPs of Marketing, and growth leaders at $20M-$200M companies.
2. Fractional CMOs and consultants who need leverage and could become customers, partners, or advocates.
3. Technical founders at $500K-$20M B2B companies who need growth capability without hiring a full team.
4. AI-native agency founders, growth engineers, and peer creators with relevant audiences.
5. Existing brand subscribers, commenters, reposts, and profile viewers who match the buyer or amplifier profile.

Avoid optimizing for generic marketers who like AI content but are not buyers, partners, or useful amplifiers.

## Posting Lanes: owner + collaborator

The following two-contributor schedule illustrates one possible split. Adapt contributor count, roles and cadence to the consumer's approved strategy using `social-audience-growth-weekly`; do not assume these roles or publishing days already exist.

| | owner | collaborator |
|---|---|---|
| Lane | POV/authority: opinions, strategy, positioning, agency economics, client results | Build log/receipts: what we built, shipped, broke, and measured this week |
| Posting days | Mon / Wed / Fri | Tue / Thu |
| Volume | 3 posts/week, never >1/day | 2-3 posts/week, never >1/day |
| Voice source | `{brain}/voice/voice-synthesis.md` + exemplars | `{brain}/voice/collaborator/interim-guardrails.md` until his profile exists (intake: `voice/collaborator/voice-intake.md`) |
| Approves own posts | owner | collaborator |

Rules:

- Never the same content on both profiles in the same week. If both lanes touch a topic, each takes its own lane's angle.
- Cross-comment inside the golden hour: each leaves a substantive 10-15+ word comment on the other's post within 60 minutes of publish. No reciprocal-like patterns; tag each other occasionally, not every post.
- Staggered days mean organization shows up in the feed near-daily while neither person over-posts.
- Company pages stay props (weekly repost, zero creative effort); personal profiles carry the reach.
- Approval routing for everything in this runbook: `{brain}/runbooks/social-approval-matrix.md` (binding).

## Weekly Content Interview (owner + collaborator, 30 min)

The calendar-blocked 30-minute recorded interview is the week's content fuel and the one human creative act the engine depends on. the drafting assistant prepares questions in advance from the content pillars, last week's best comments and questions, and live pipeline conversations. The transcript feeds `writing` for the pillar piece and derivatives (1 pillar → 3 concepts → 3-5 derivatives each) and `linkedin-post` for standalone posts, split across both lanes: owner's segments fuel the POV lane, collaborator's segments fuel the build-log lane.

If the interview slips, the drafting assistant flags it in the weekly plan, proposes a rescheduled slot, and labels the week as drafting from reserves (prior transcripts and saved ideas). A skipped interview is the leading cause of a stalled collaborator lane; treat two consecutive misses as an escalation to owner.

## Weekly Cadence

### Monday: Plan The Loop

Create the weekly plan for the coming Monday-Friday.

Inputs:

- last week's LinkedIn and X metrics
- current content calendar and publishing plan
- current business priority or CTA
- warm signals from profile views, comments, reposts, inbound requests, and DMs
- peer or competitor observations from Favikon, Socialinsider, Metricool, or manual review

Outputs:

- weekly audience lane
- daily engagement/comment/reply queue
- connection-request batch description
- warm-DM draft set, if earned
- saved-idea capture prompts for the week
- approval list for owner

Save summary to `{brain}/content/social-audience-growth/{week-start}-weekly-plan.md`.

### Tuesday-Friday: Execute With Approval

Each day, the drafting assistant prepares:

- 3-5 LinkedIn posts worth commenting on
- 4-6 X posts worth replying to or quote-posting
- connection-request batch description
- 1-3 warm follow-up drafts, only when the signal is earned
- content ideas sparked by audience comments or questions

owner approves or edits before anything goes external.

### Friday: Review And Feed The Machine

Run the weekly review after the Friday Build Log window.

Review:

- LinkedIn post performance: comments, saves, shares, profile views, follower growth
- X post/reply performance: replies, reposts, quote posts, profile visits, follower growth
- connection requests sent, accepted, and acceptance rate
- warm DMs started and replies received
- qualified conversations active
- best audience lane
- strongest content question, objection, or topic from the week

Save summary to `{brain}/content/social-audience-growth/{week-start}-weekly-review.md`.

## Warm DM Exemplar: Connection-Building From Profile Views, Comments, And New Connections

Use this as the quality bar when the drafting assistant drafts optional warm DMs for owner approval. The point is to turn a light signal into a relationship-building conversation, not to pitch.

### Fictional example

The operator has just connected with a person who wrote about measuring content
quality. This invented draft illustrates the pattern; it is not a message
received from a real contact or evidence of campaign performance:

> Thanks for connecting, [Name]. Your point about measuring useful replies rather than just impressions gave me something to think about.

Use this only when the referenced detail is true of the actual recipient. Do
not invent familiarity or reuse the fictional detail as if it were observed.

### Why It Works

- Short enough to feel like a real human note, not a campaign sequence.
- Warm without being overly familiar.
- Specific enough to refer to a real idea in the recipient's post when used with verified context.
- Names the shared topic area without turning it into a pitch.
- Opens the door to conversation without asking for time, attention, a call, a newsletter signup, or a favor.

### Reusable Pattern

1. Simple greeting or connection acknowledgment.
2. One evidence-of-attention detail from the signal: post, comment, profile view context, shared thread, or recurring topic.
3. One concise appreciation of the recipient's thinking, angle, or question.
4. Optional light conversational bridge, only if it does not create pressure.
5. No pitch, no link, no calendar ask, no disguised sales question in the first DM.

### Draft template

```text
Pleasure to connect, [Name]. I saw your [post/comment/profile note] on [specific topic] and liked the way you framed [specific idea/tension].
```

Optional softer variant when the signal is a profile view or new connection rather than a specific comment:

```text
Pleasure to connect, [Name]. I took a quick look at your recent posts and liked how you're thinking about [specific topic/tension].
```

Quality check before sending to owner for approval:

- Would this still feel true if read aloud by owner?
- Is the detail specific enough to prove the drafting assistant looked, but not so detailed it feels creepy?
- Is there zero ask in the message?
- Could the recipient reply naturally with one sentence?

## Operating Metrics

Primary metrics:

- qualified LinkedIn follower growth
- qualified X follower growth
- profile views from ICP audience
- comments and replies from ICP audience
- connection request acceptance rate, target above 40%
- warm conversations started
- qualified conversations active

Secondary metrics:

- post reach/impressions
- engagement rate
- saves and reposts
- Ghost clicks from first comments
- brand subscriber conversions where attributable

Volume is never the north star by itself.

## Data Pointers

Logical datasets live in `{brain}/data-manifest.yaml`:

- `social_platform_metrics_weekly`
- `social_competitive_intel_weekly`
- `social_growth_execution_queue`

The exact tool URLs or database IDs can be filled in once owner confirms the source of truth for metrics and queues. Until then, the drafting assistant should use available platform exports, screenshots, or manual summaries and clearly label gaps.

## Weekly Plan Template

```markdown
# Social Audience Growth Plan - Week Of YYYY-MM-DD

## Audience Lane
[Primary audience focus and why this week]

## Content Context
[This week's approved content, CTA or campaign priority]

## Last Week's Signals
- LinkedIn:
- X:
- Qualified conversations:
- Content intelligence:

## Daily Queue
| Day | LinkedIn Focus | X Focus | Connection Batch | Warm Follow-ups | Content Notes |
|---|---|---|---|---|---|
| Monday | | | | | |
| Tuesday | | | | | |
| Wednesday | | | | | |
| Thursday | | | | | |
| Friday | | | | | |

## Approval Needed
- [ ] Comments/replies:
- [ ] DMs:
- [ ] Posts:
- [ ] Connection batch:
```

## Weekly Review Template

```markdown
# Social Audience Growth Review - Week Of YYYY-MM-DD

## Scoreboard
| Metric | LinkedIn | X | Notes |
|---|---:|---:|---|
| Followers | | | |
| Follower change | | | |
| Profile views | | | |
| Posts published | | | |
| Comments/replies made | | | |
| Connection requests sent | | n/a | |
| Connection requests accepted | | n/a | |
| Warm conversations started | | | |

## What Worked
- 

## What Did Not Work
- 

## Audience Learning
- 

## Content Learning
- 

## Next Week's Test
- 
```
