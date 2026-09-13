---
name: ecosystem-partnerships
description: 'Run the entity''s ecosystem-partnership motion: keep the partner map current, drive a small monthly queue of warm relationship moves, execute the joint webinar / newsletter swap / podcast guesting playbooks, track partner-sourced leads, and participate in target communities without ever spamming them.'
---

# Ecosystem Partnerships

Run the entity's ecosystem-partnership motion: keep the partner map current, drive a small monthly queue of warm relationship moves, execute the joint webinar / newsletter swap / podcast guesting playbooks, track partner-sourced leads, and participate in target communities without ever spamming them.

> Shared social-growth procedure. Resolve the current consumer strategy and ownership policy before planning work.

## When To Use

- Monthly partner review: map upkeep, relationship-stage changes, and the next outreach queue
- Drafting partner outreach, podcast pitches, newsletter-swap proposals, or joint-webinar plans for human approval
- Preparing or debriefing a joint webinar, swap, guest episode, or community AMA/office-hours session
- Rolling up partner-sourced leads against benchmarks

Do not use this for conference CFPs and speaking slots — that is `speaking-events-pipeline` (a partner intro that leads to a stage still hands off there). Do not use it for the entity's own social posting — that is the weekly audience-growth loop and the content skills. Do not use it for paid sponsorships or paid newsletter-recommendation networks; this skill deliberately excludes them (see step 4).

## Operating Principle

The entity's buyers are already the paying customers of a dense vendor-and-operator ecosystem, and that ecosystem routes through a small number of named people, not properties. One good relationship typically unlocks a podcast slot, a community AMA, and a conference intro simultaneously — so the unit of work is the **relationship**, and the motion is **relationship-first, never pitch-first**: lead with a genuine contribution to their audience, and let the ask ride on established trust. The agent's leverage is research, drafting, sequencing, and logging; humans own every outbound message.

## Inputs

- Entity brain path (`{brain}`)
- Review month
- The entity's partner map doc (see Required Context)
- Partner queue state (dataset `ecosystem_partner_queue`: contacts, relationship stage, last touch, open threads)
- Standing quarterly commitments (e.g. webinars/swaps per quarter) and their current status
- Lead pipeline data for partner-sourced attribution

## Outputs

- Monthly partner review: `{brain}/content/partnerships/{month}-partner-review.md` — map changes, queue results, commitments status, lead rollup
- Monthly outreach queue: 3-5 warm moves, each drafted with rationale, awaiting human approval
- Playbook drafts as needed: joint-webinar run-of-show, swap copy, podcast pitches, community posts/AMA plans
- Partner-sourced lead rollup written to the lead pipeline dataset
- Proposed edits to the partner map doc when tiers or fit assessments change

## Required Context

Load before running:

1. `{brain}/BRAIN.md`
2. `{brain}/strategy/ecosystem-partner-map.md` — the tiered map is this skill's source of truth for who and why
3. `{brain}/strategy/positioning-strategy.md` — what the entity offers a partner's audience
4. `{brain}/strategy/content-strategy.md` — current pillars for webinar/swap/podcast angles
5. `{brain}/voice/voice-synthesis.md` — all outbound and community copy is public voice
6. `{brain}/runbooks/social-approval-matrix.md`, if present — who approves what
7. `{brain}/data-manifest.yaml` — resolve `ecosystem_partner_queue` (contact-level tracking) and the lead-pipeline dataset

Contact-level details (names, emails, threads, last-touch dates) live in the partner queue dataset, never in repo artifacts. The map doc holds strategy: who the partners are, tiers, fit, and plays.

## Safety And Approval Rules

- **Every outbound message — outreach email, DM, podcast pitch, swap proposal, community post, AMA answer prepared in advance — is human-approved before it goes anywhere.** Per the entity's approval matrix, partner/podcast outreach approval defaults to the entity owner.
- Relationship-first, never pitch-first: no first contact contains a pitch, a booking link, or a service offer.
- Community rules are binding per community (especially self-promotion rules); never export or quote member content; no bursts of activity that read as campaigns.
- No paid recommendation networks or incentivized subscriber acquisition without an explicit owner decision to revisit (see step 4 for why).
- Contact lists stay in the partner queue dataset (Notion or equivalent), not the repo.

## Workflow

### 1. Partner Map Upkeep

Monthly, reconcile the map doc and the queue dataset:

- Verify each partner's tier, fit scoring (audience = the entity's buyer, non-competitive, existing co-marketing muscle), and any news that changes fit
- Update relationship stage per partner: `cold → warm → active → recurring`
- Flag stale relationships: any `active`/`recurring` partner with no touch in 60+ days gets a re-warm candidate note
- Maintain the per-partner "give-first" dossier: their recent content, what the entity can genuinely contribute (data, a guest issue, a webinar topic at the audience intersection)
- Propose additions/removals to the map doc; the doc changes only with owner sign-off

### 2. Monthly Outreach Queue

Build a queue of **3-5 warm moves** — small on purpose; this motion compounds through consistency, not volume.

For each move provide:

- The partner, the relationship stage, and the specific play (intro, give-first contribution, swap proposal, webinar pitch, podcast pitch, AMA offer)
- A drafted message in entity voice
- Rationale: why this partner, why now, what signal makes it warm
- The expected next step if they respond

Rules: warm signals first (they engaged, published something adjacent, a mutual connection exists); **relationship-first, never pitch-first**; a cold-list blast is never a substitute for a thin queue — if fewer than 3 warm moves exist, ship fewer and say so. Queue goes to human approval; the agent logs outcomes and schedules follow-up timing.

### 3. Joint Webinar Playbook

When a webinar play is approved with a partner:

- Agree terms upfront and in writing: lead-sharing, brand usage, promotion commitments per side, and account-conflict handling ("first introduction wins")
- Benchmark: a well-promoted two-partner webinar reaches **300-500 registrants split across both audiences**; registration→attendance benchmark 40-56%
- The entity supplies thought leadership; the partner typically supplies audience and webinar ops — pick partners with an existing webinar machine
- Draft: topic at the audience intersection, run-of-show, promo copy for both sides, and the post-webinar follow-up split
- Where the entity's diagnostic/audit funnel exists, the webinar CTA routes into it with a webinar-specific artifact URL
- Track against standing quarterly commitments (e.g. 1 joint webinar + 2 swaps/guest features per quarter) and nag when the pipeline won't hit them

### 4. Newsletter Swaps (Organic Monthly Cadence)

Target **one organic swap or guest feature per month** with on-ICP newsletters from the map:

- Format hierarchy, worst to best: bare text mention < themed feature with context < guest takeover/co-created issue — push for the richest format the relationship supports
- Benchmark: subscribers from cross-promotion open at **60-70%**, versus 30-40% for paid acquisition
- **Skip paid recommendation networks** (SparkLoop-style, Boosts): the inventory skews consumer/creator, the ICP filter is weak, and the documented failure mode is subscribers who don't remember opting in (sub-15-20% opens, elevated spam complaints). Volume is not the goal; the entity's buyer is
- Draft swap copy for both directions; log send dates and measure new-subscriber engagement at 30 days

### 5. Podcast Guesting Circuit

- Maintain the target show list (8-12 shows from the partner map) with host research, prior-episode notes, and a suggested angle per show tied to current pillars
- Draft pitches per show; human-approved before sending; track pitch → booking → air date in the queue dataset
- Every episode gets a **unique artifact URL** pointing at the entity's diagnostic/audit, mentioned on air and in show notes — the episode leaves an attribution fingerprint
- On air date, trigger repurposing: clips and posts handed to the social lanes in voice-profile register
- Benchmark, labeled: podcast guest→client conversion ≈ **10% (practitioner claim, not independently verified)** — use it for prioritization, not forecasting
- Cadence note: 3-4 placements/month is a heavy admin burden by practitioner consensus; the agent absorbs exactly that burden (research, pitching, follow-up timing, logging)

### 6. Partner-Sourced Lead Tracking

- Every partner-originated lead is tagged to its partner and play in the lead pipeline dataset (leads live in the approved CRM/Notion pipeline, never the repo)
- Dual attribution: unique artifact URLs per play + the required free-text "how did you hear about us?" field, categorized monthly
- Benchmark: a mature program with **~10 active partners ≈ 3-5 qualified leads/month** — report actuals against this band, and label the band as a benchmark, not a promise
- Monthly rollup answers: which partners sourced conversations, which plays produced them, and where the next quarter's approval time should go

### 7. Community Participation Rules

Community presence is a partnership play wearing community clothes — the highest-leverage motion is **negotiated formats** (a recurring AMA or office hours arranged with the community operator, who then does the promotion), not ambient posting.

- Qualify communities by role density: are actual buyers present, or practitioners
- Contribute first, promote last: helpful, promotion-free answers where the entity has genuine expertise; brand mentions only where organically relevant
- Hard rules: never auto-post; per-community rules encoded and checked (especially self-promotion rules — one ban sets the entity back months); no quoting or exporting member content; a monthly cap on anything resembling a mention; paid/moderated communities beat free groups (better members, gatekeeper vouching)
- **Every community post, reply, and AMA plan is human-approved**, routed per the approval matrix
- Prefer shared assets that are practical tools/templates over gated ebooks; conversion should feel like a natural next step, not a funnel shove

## Quality Gates

- Outreach queue is 3-5 moves with explicit warm rationale; a thin honest queue beats a padded cold one
- Zero pitch-first messages: first contact contains a contribution or a genuine question, never an offer
- Every play (webinar, swap, episode, AMA) has a unique artifact URL before it goes live
- Benchmarks in reports carry their labels: documented fact vs practitioner claim vs internal hypothesis
- Monthly review separates relationship progress (stage movement, touches) from pipeline results (leads, calls) — early months will show the former without the latter, and that is the expected shape

## Failure Modes

| Failure | Response |
|---|---|
| Fewer than 3 warm moves available | Ship the smaller queue and spend the gap on give-first dossier work; do not pad with cold outreach |
| Partner unresponsive after 2 approved follow-ups | Park at current stage with a 90-day re-warm date; move approval time to responsive partners |
| Webinar registrations far below the 300-500 band | Debrief promotion commitments per side before blaming the topic; log the delta against what was agreed upfront |
| Swap partner's list underperforms (low opens from swapped subscribers) | Check ICP match before format; drop the partner from the swap rotation if two swaps underperform |
| Community rules unclear or recently changed | Pause activity in that community until rules are re-verified; never test boundaries |
| Partner-sourced leads at zero after a quarter of active plays | Audit attribution capture first (URLs live? free-text field required?) before concluding the channel fails — dark channels under-report by default |
| Owner approval becomes the bottleneck | Batch the queue for a single weekly approval pass; propose (do not enact) any change to approval tiers |
