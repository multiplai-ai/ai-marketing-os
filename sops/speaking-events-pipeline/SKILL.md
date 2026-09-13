---
name: speaking-events-pipeline
description: 'Run the entity''s speaking-engagement pipeline as calendar automation: a monthly CFP radar that never misses a submission window, event tiering, human-approved abstract drafting, and a from-stage conversion playbook that turns talks into tracked leads.'
---

# Speaking Events Pipeline

Run the entity's speaking-engagement pipeline as calendar automation: a monthly CFP radar that never misses a submission window, event tiering, human-approved abstract drafting, and a from-stage conversion playbook that turns talks into tracked leads.

> Shared social-growth procedure. Resolve the current consumer strategy and ownership policy before planning work.

## When To Use

- Monthly CFP radar sweep: checking every tracked event's submission window and raising deadline alerts
- Adding, re-tiering, or retiring events on the entity's speaking target list
- Drafting a CFP submission package (abstract, learning outcomes, bio, speaker assets) for a specific event
- Preparing the pre-event, at-event, and post-event playbook for a confirmed talk
- Rolling up talk-to-lead attribution for the monthly review

Do not use this for partner webinars, podcast guesting, or community AMAs — that is `ecosystem-partnerships`. Do not use it for social promotion drafting itself — route to `linkedin-post` / `writing` with the promo brief this skill produces. For the overall funnel review that consumes speaking-sourced leads, use the entity's funnel skill.

## Operating Principle

The speaking pipeline is a deadline problem before it is a content problem. CFPs typically close 2-3+ months before the event, and systematic speakers work 8-12 months ahead. **A missed CFP window is the failure mode** — an event can be a perfect ICP fit and still be worthless this cycle because the window closed silently. The radar's first job is deadline alerts; everything else (tiering, abstracts, conversion) hangs off a calendar that is never allowed to go stale.

The second principle: a talk is a funnel stage, not a brand moment. Every accepted talk ships with a conversion kit (QR-gated asset, unique URL, follow-up sequence) before the speaker walks on stage.

## Inputs

- Entity brain path (`{brain}`)
- Review month
- The entity's speaking targets doc (see Required Context)
- Current content pillars and positioning (for abstract drafting — pull live, never hard-code programming)
- CFP tracker state (dataset `speaking_cfp_tracker`)
- Any confirmed upcoming talks needing pre/at/post-event preparation

## Outputs

- Monthly CFP radar report: `{brain}/content/speaking/{month}-cfp-radar.md` — window status per tracked event, alerts, tier changes, submissions in flight
- Draft CFP submission packages queued for human approval (never submitted autonomously)
- Per-talk stage-conversion kit: gated-slides page brief, unique artifact URL, QR asset spec, follow-up sequence drafts
- Talk-to-lead attribution rollup (self-reported attribution mentions + unique-URL hits per talk)
- Updates to the tracker dataset and, where warranted, proposed edits to the targets doc

## Required Context

Load before running:

1. `{brain}/BRAIN.md`
2. `{brain}/strategy/speaking-events-targets.md` (or the entity's year-stamped variant, e.g. `speaking-events-2026-targets.md`) — the tiered target list is the radar's source of truth
3. `{brain}/strategy/content-strategy.md` — current pillars for abstract drafting
4. `{brain}/strategy/positioning-strategy.md` — the anchor every pitch angle keys to
5. `{brain}/voice/voice-synthesis.md` — abstracts and bios are public voice
6. `{brain}/runbooks/social-approval-matrix.md`, if present — who approves what
7. `{brain}/data-manifest.yaml` — resolve dataset `speaking_cfp_tracker` (event windows, submission status, contacts) and the lead-pipeline dataset for attribution

Contact-level details (organizer names, emails, submission threads) live in the tracker dataset, never in repo artifacts.

## Safety And Approval Rules

- **No CFP submission, organizer email, or outreach of any kind goes out without explicit human approval.** Per the entity's approval matrix, external CFP/partner outreach approval defaults to the entity owner. The agent researches, drafts, tracks, and nags; humans send.
- Abstracts, bios, and any public-facing copy pass the entity's voice gates before approval.
- No scraping that violates event-site terms; window checks use public pages, Sessionize/PaperCall listings, and organizer announcements.
- Contact lists and submission correspondence stay in the tracker dataset (Notion or equivalent), not the repo.

## Workflow

### 1. Monthly CFP Radar Sweep

For **every** event on the target list, verify the current CFP window state — do not skip events that "aren't due yet"; silent window changes are exactly what the radar exists to catch.

- Check the event site, Sessionize/PaperCall listing, and organizer channels for: CFP open date, close date, submission channel, and any format changes
- Classify each event: `window-open`, `opens-soon` (announced, not yet open), `closed-this-cycle` (track next edition), `unknown` (needs manual confirmation — flag it)
- Raise alerts at three thresholds: **CFP opens**, **closes in 21 days**, **closes in 7 days**
- Because CFPs close 2-3+ months pre-event and strong pipelines work 8-12 months ahead, the radar always tracks the *next* edition of closed events — a `closed-this-cycle` event is a scheduling entry, not a dead row
- Log every window change in the tracker dataset; summarize the sweep in the monthly radar report

### 2. Event Tiering

Maintain each event's tier on the targets doc; propose re-tiering when audience, format, or ICP fit changes.

| Tier | Definition | Role in pipeline |
|---|---|---|
| 1 | Perfect-ICP national stages — the entity's exact buyer in the room, topic authority on the entity's positioning | Submit on an 8-12 month horizon; expect low single-digit acceptance rates initially; highest prep investment |
| 2 | Adjacent or virtual stages — right buyer, entity's topic is a differentiator rather than the theme; virtual summits | Steady submission cadence; faster cycles; good source of recorded footage |
| 3 | Local and rolling reps — e.g. AMA chapters and similar rolling-CFP venues | Work immediately and continuously: low stakes, builds the speaker video assets that Tier 1 organizers select on |

Tier 3 is not optional filler — organizers select on demonstrated stage competence (practitioner claim from the speaking circuit), so Tier 3 reps and their recordings are the admission ticket to Tier 1.

### 3. Abstract And Pitch Drafting

When a window opens (or an alert fires), draft the full submission package from the entity's **current** content pillars and positioning — pulled live from `content-strategy.md` and `positioning-strategy.md`, never from memory or hard-coded show names.

Package contents (tailor to what the event asks for):

- Session title + abstract in the event's language and format
- Three learning outcomes
- Speaker bio variant (short/long) in entity voice
- Speaker video link and prior-talk references from the tracker
- Suggested track and any format notes

Maintain a reusable talk inventory (2-3 evergreen abstracts keyed to the positioning; the targets doc holds the entity-specific templates) and tailor per event rather than writing from scratch.

**Gate: every submission package is human-approved and human-submitted.** Queue it with the event, deadline, and rationale.

### 4. Pre-Event Promotion

For each accepted talk, brief the social lanes 2-4 weeks out:

- Hand the promotion brief to the entity's social skills (`linkedin-post`, `writing`, the weekly audience-growth loop) — this skill does not draft the posts itself
- Promotion angles: the problem the talk solves, a receipt or artifact from the material, and a reason for ICP attendees to find the speaker at the event
- Respect all volume guardrails and approval routing owned by the social skills

### 5. At-Event Conversion

Before the talk, ship the stage-conversion kit:

- **QR-gated slides where the gate is the entity's free diagnostic/audit** — the QR code from stage points at a talk-specific page; slides/recording access is exchanged for taking the audit (email captured in the audit flow)
- Benchmark: gated slides convert **35-50% of session attendees** (documented range; the audience is already emotionally committed)
- The gate asset is always the audit, not a generic lead magnet — it moves attendees directly into the conversion funnel rather than a passive list
- Unique artifact URL per talk (see step 6) printed into the deck, verbally repeated, and on the final slide

### 6. Post-Event Follow-Up And Attribution

Run the documented follow-up cadence as drafts for approval:

- <24h: personalized LinkedIn touches to attendees who engaged
- <48h: value-asset email to gated-slides opt-ins
- Day 3-4: direct outreach to high-priority leads
- Day 5-7: nurture sequence entry
- Week 2: recap content published to the social lanes

Attribution is dual-source, per the entity's attribution spine:

- **Unique artifact URL per talk** — every gated-slides page and QR code is talk-specific, so the channel leaves a fingerprint
- **Self-reported attribution** — the required free-text "how did you hear about us?" field on the audit and booking forms; categorize mentions monthly (self-reported attribution catches roughly 90% of what click-path software misses — practitioner-published research, directionally strong)

Roll talk→audit→call→proposal counts into the monthly radar report and the lead pipeline dataset.

## Quality Gates

- Every tracked event has a window state and a next-check date after each sweep; `unknown` states are flagged for manual confirmation, never silently carried
- No submission package leaves the queue without human approval; no exceptions for "low stakes" Tier 3 venues
- Abstracts must key to the entity's current positioning anchor and name a concrete outcome for the event's audience
- Every accepted talk has its conversion kit (gated asset + unique URL + follow-up drafts) complete before the event date
- Attribution rollup separates verified counts (URL hits, audit completions) from self-reported mentions

## Failure Modes

| Failure | Response |
|---|---|
| CFP window closed before the radar caught it | Log the miss with the detection gap, add the next edition with an earlier check date, and tighten the sweep source list for that event |
| Event CFP details unverifiable | Mark `unknown`, flag for manual confirmation in the radar report; do not guess deadlines |
| No current content pillars available (strategy refresh in flight) | Draft from positioning anchor only, label the gap, and flag that abstracts need a re-pass after the refresh |
| Submission rejected | Log outcome + any organizer feedback in the tracker; rejection on Tier 1 is expected early — track sent-vs-accepted rate rather than treating each rejection as a signal to stop |
| Talk accepted but conversion kit not ready | Escalate before the event; a talk without the gated-audit kit is a known-bad outcome, not an acceptable fallback |
| Attribution shows zero leads from a repeated venue | Propose de-tiering at the next quarterly review rather than immediately dropping — speaking compounds slowly |
