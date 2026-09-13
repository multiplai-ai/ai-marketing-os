---
name: social-growth-os
description: 'The plain-language entry point for running an entity''s social growth system day to day. This skill is written for an operator with zero marketing background: it tells the agent exactly what to prepare, tells the operator exactly what to decide, and defines every marketing term it uses. The operator supplies judgment about their business and approvals; the skill supplies the marketing judgment.'
---

# Social Growth OS

The plain-language entry point for running an entity's social growth system day to day. This skill is written for an operator with zero marketing background: it tells the agent exactly what to prepare, tells the operator exactly what to decide, and defines every marketing term it uses. The operator supplies judgment about their business and approvals; the skill supplies the marketing judgment.

> Core skill canon. Created 2026-07-08 as the partner-facing orchestrator for the social growth extension. Routes into `social-audience-growth-weekly`, `writing`, `linkedin-post`, `audit-funnel`, `ecosystem-partnerships`, `speaking-events-pipeline`, and `content-calendar`.

## When To Use

- An operator says "run my daily queue," "what do I do today," or asks for their daily/weekly/monthly social routine
- Daily execution: approving queued actions, golden-hour replies, ICP commenting, logging inbound signals
- Weekly cadence: kicking off the audience-growth loop and the voice-interview-to-content chain
- Monthly cadence: funnel review, partner and speaking pipeline reviews, next month's content theme
- Reporting: "how are we doing?" answered against realistic expectation bands, in plain words

Do not use this for a single post draft (`linkedin-post`), the flagship writing bundle (`writing`), paid social (`ads-linkedin` and the paid-media suite), or deep strategy work (`content-strategy`, `positioning-strategy`). This skill coordinates; the routed skills do the specialist work.

## Roles

Two humans and the agent. Names and specifics live in the entity brain; the skill only assumes the roles exist.

- **Operator:** runs the daily loop in ~45 minutes. Approves/edits/rejects queued actions, executes engagement, logs inbound signals. Needs zero marketing knowledge.
- **Principal:** the established voice of the entity. Async-approves anything published under their name, records interview segments, takes qualified sales calls, approves partner and event outreach.
- **Agent:** drafts everything, builds queues with rationale, tracks metrics against expectation bands, flags decisions. Never sends anything external on its own.

## Required Context

Load before running any mode:

1. `{brain}/BRAIN.md`
2. `{brain}/voice/voice-synthesis.md` (and any per-person voice profiles or interim guardrails under `{brain}/voice/`)
3. `{brain}/runbooks/social-approval-matrix.md` — the binding approval matrix
4. `{brain}/runbooks/weekly-social-audience-growth.md`, if present
5. `{brain}/data-manifest.yaml` for dataset pointers (see Datasets below)

If the approval matrix runbook is missing, stop and ask the entity owner to confirm approvals before queuing anything external. Do not guess an approval route.

## Approvals (binding)

The full matrix lives in `{brain}/runbooks/social-approval-matrix.md` and wins over anything written here. The shape of it:

- Content published under a person's name is approved by that person.
- Comments, replies, and connection requests are approved by the operator.
- DM openers are approved by the operator (by the principal if sent as the principal). Warm signals only, never pitch-first.
- Newsletter issues and external-facing partner, event, or funnel outreach are approved by the principal.

The agent drafts every word and attaches a one-line rationale to every queued action ("why this person, why now"). Humans approve, edit, or reject; they never start from a blank page.

## Modes

Pick the mode from what the operator asks for. "Run my daily queue" is daily mode. "Plan the week" or "review the week" is weekly mode. "Monthly review" is monthly mode. "How are we doing?" is report mode.

### Daily Mode (operator, ~45 minutes)

Build one queue with four blocks, in this order. Every external action carries a draft and a rationale.

**1. Golden-hour reply loop (do this first, it is time-sensitive).**
If a post went live in the last 60-90 minutes, draft a reply to every comment on it for the author to approve and send. Replies should add value, ask a follow-up, or anchor the topic; never a bare "thanks!". Why first: the first 60-90 minutes after posting largely determine a post's total reach, and authors who reply in that window see roughly 30% more engagement. Comments are weighted around 15x likes by the platform, so this loop is the growth engine, not the posting.

**2. Approval queue.**
Present everything awaiting approval, grouped by approver: queued comments, connection requests, DM openers, post drafts, anything the weekly plan scheduled for today. The operator approves/edits/rejects their items; the agent packages the principal's items for async Slack approval.

**3. ICP commenting (10-15 comments).**
Supply 10-15 target posts from ICP-adjacent feeds (people who match the ideal customer profile, communities they read, creators they follow, target accounts) with a drafted comment for each. Quality bar: 2-3 specific sentences that add a point, example, or useful question; specific enough that it could not be pasted under any other post. This is how strangers become warm audience while follower counts are still small.

**4. Inbound signal logging.**
Capture the day's inbound signals into the `lead_pipeline` dataset: ICP-matching profile viewers, inbound connection requests, DM replies, comments from potential buyers, and especially anyone who says a variant of "I've been reading your posts." Always record the self-reported source. Most social-driven pipeline is untrackable by click analytics; what people say on calls and in DMs is the attribution system.

### Weekly Mode

Two jobs, routed:

**1. The audience-growth loop.** Run `social-audience-growth-weekly` for the plan (Monday) or the review (Friday). That skill owns targeting, the execution queue, metrics capture, and learning. This skill just invokes it and translates its outputs into operator language.

**2. The voice interview → content chain.** The weekly 30-minute recorded interview is the system's single mandatory creative act by humans. The agent prepares the interview kit beforehand: questions generated from the content pillars, last week's best comments and questions, and live pipeline conversations. Afterward, the transcript becomes the week's content fuel: route it to `writing` for the pillar piece and derivatives, and `linkedin-post` for standalone posts (1 pillar → ~3 concepts → 3-5 derivatives each). Drafts route to approvers per the matrix. If the interview did not happen, flag it loudly; the content engine has no other raw material and thin weeks trace back to skipped interviews.

### Monthly Mode

Route to the specialist skills and assemble one plain-language summary of decisions needed:

| Job | Skill |
|---|---|
| Funnel review: audit completions, stage conversion vs benchmarks, follow-up performance | `audit-funnel` |
| Partner map upkeep, outreach queue, webinar and swap planning | `ecosystem-partnerships` |
| CFP radar sweep: open windows, deadlines, pitch drafts | `speaking-events-pipeline` |
| Next month's theme and publishing plan | `content-calendar` |

Every outbound action these skills produce still routes through the approval matrix (partner/CFP outreach goes to the principal).

### Report Mode

Report metrics against the expectation bands, in operator language. Never present a raw dashboard and walk away.

**The expectation bands (from converging research, treat as hypotheses to validate):**

| Phase | What is normal | What it feels like |
|---|---|---|
| Weeks 1-4 | Consistency building, small numbers, little visible response | Like shouting into a void. This is normal, not failure. |
| Weeks 4-8 | First qualified conversations from inbound | A few "saw your post" DMs and comments from real potential buyers. |
| Months 2-3 | 3-5%/month follower growth once established; 4-8% engagement rate at small scale | Steady, not explosive. Flat weeks still happen. |
| Months 4-6 | Real pipeline: inbound leads compound, "I've been reading your stuff" on calls | The inflection. Most people quit right before this. |

Rules for the report:

- Always show where the entity is on the ramp before showing this week's numbers.
- Lead with leading indicators the operator controls (posting consistency both lanes, comments/day executed, interview completed, signals logged) before lagging ones (followers, leads, calls).
- Prefer audience quality over volume: ICP share of engagers beats follower count.
- Separate facts from hypotheses. If a number is below band, propose one specific test, not a panic pivot.
- Say explicitly when a below-band week is within normal variance. The documented failure mode for novice operators is quitting at month 2 because a normal ramp looked like failure.

## Two-Lane Operation

When the entity runs two people (see the lane-split section in `social-audience-growth-weekly`), this skill enforces:

- Each person posts only in their own lane (POV/authority vs builder/receipts). Never the same content on both profiles in the same week.
- Staggered posting days so the combined presence is near-daily without either person exceeding 1 post/day.
- Cross-commenting is queued as part of the golden-hour loop: each person leaves a substantive 10-15+ word comment on the other's post within the first hour. No reciprocal-like patterns, no tagging on every post.

## Quality Bars (non-negotiable)

- **Receipt requirement:** every post draft contains at least one concrete number, artifact, screenshot, or named real example. No receipt, no draft leaves the queue. Purely generic AI-written posts earn roughly 45% fewer interactions; receipts are the antidote and a checklist item anyone can verify.
- **Volume guardrails:** 3-5 posts/week per person, never more than 1/day (reach per post drops 40%+ past that). Consistency beats volume; a sustainable 3x/week beats an abandoned daily streak.
- **No external links in post bodies** (roughly -60% reach; link-in-first-comment is now also penalized). Links live in the profile, featured section, and newsletter CTA lines.
- **Voice gates:** every draft passes the entity voice profile (`{brain}/voice/voice-synthesis.md` or the person's own profile/guardrails), plus the AI-tell anti-patterns checklist in `writing`, plus the question "would a human actually write it this way?"
- **No engagement bait**, ever ("comment YES", "like if you agree"). Detected and penalized, and it is not the brand.

## Safety And Platform Rules

Consistent with `social-audience-growth-weekly`, and binding:

- Nothing external without the approval named in `{brain}/runbooks/social-approval-matrix.md`.
- No automation that bypasses platform limits; no mass actions; no logged-in scraping.
- Contact lists and lead-level data live in the approved CRM dataset (Notion), never in repo artifacts. Repo artifacts summarize strategy and learnings.
- No pitching on first contact, in any channel. The conversion ladder is: engager → connection → conversational DM → offered call. Never skip rungs.
- Optimize for qualified audience fit and conversation quality before volume.

## Datasets

Resolve these logical IDs through `{brain}/data-manifest.yaml`; never hard-code URLs:

- `social_platform_metrics_weekly` — weekly platform metrics
- `social_growth_execution_queue` — the external-action queue
- `social_competitive_intel_weekly` — creator/competitor intelligence
- `lead_pipeline` — inbound signals and lead tracking (people data lives here, not in the repo)
- `audit_funnel_responses` — diagnostic funnel completions (monthly mode)
- `speaking_cfp_tracker` — CFP windows and deadlines (monthly mode)
- `ecosystem_partner_queue` — partner outreach queue (monthly mode)

If a dataset is missing or unreachable, say exactly which one, run the mode with what is available, and label the gap. Do not fabricate metrics.

## Plain-Language Glossary

Define these on first use in any operator-facing output. Never assume marketing vocabulary.

- **ICP (ideal customer profile):** a specific description of the people most likely to buy. Not "marketers" but "owners of 10-50 person marketing agencies deciding how to adopt AI."
- **Lane:** the content territory one person owns, so two people never blur together. A POV/authority lane argues what the market should do; a builder/receipts lane shows what we actually built and measured this week.
- **Receipt:** the concrete client inside a post; a real number, screenshot, artifact, or named example. "We cut onboarding from 6 hours to 40 minutes" is a receipt. "AI saves time" is not.
- **Golden hour:** the first 60-90 minutes after a post goes live, when the platform decides how far to spread it. Author replies in this window materially lift reach.
- **Impressions:** how many times a post appeared on screens. Attention, not interest.
- **Engagement rate:** reactions + comments + shares divided by impressions. Interest, not just attention. 4-8% is healthy for a small account.
- **Connection request:** asking someone on LinkedIn to join your network. Blank requests to clean ICP fits are fine; a note only when genuinely personalized.
- **DM opener:** the first direct message to someone who showed a warm signal. A question or something useful, never a pitch.
- **Warm signal:** evidence someone noticed you: commented, followed, viewed your profile, replied. Warm signals earn outreach; cold outreach does not.
- **Qualified conversation:** a genuine back-and-forth with someone who matches the ICP and has the problem you solve.
- **Pipeline:** the set of qualified conversations that could become paying engagements.
- **Pillar / derivative:** the pillar is the week's one substantial piece (newsletter, article, interview); derivatives are the smaller posts cut from it.
- **Self-reported attribution:** asking "how did you hear about us?" and writing the answer down. It catches the majority of what click tracking misses.

## Failure Modes

| Failure | Response |
|---|---|
| Interview skipped | Flag it, propose a rescheduled slot, and draft from prior transcripts and saved ideas while labeling the week as running on reserves. |
| Approval bottleneck (principal) | Batch approvals 2x/day in Slack; if latency persists past two weeks, flag a matrix-tier revisit as a decision for the entity owner. |
| Metrics unavailable | Run the mode qualitatively, name the missing dataset, ask the owner to connect the source. |
| Operator anxiety about slow results | Report mode, expectation bands first. Show position on the ramp and leading indicators before any lagging number. |
| A queued action looks off-ICP or off-voice | Pull it, say why, replace it. Never send borderline actions to hit volume numbers. |
| Routed skill unavailable | Report exactly which skill/tool is unavailable and provide a manual checklist for that job. Never silently substitute. |
