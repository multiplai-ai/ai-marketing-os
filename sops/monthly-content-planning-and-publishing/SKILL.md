---
name: monthly-content-planning-and-publishing
description: Plan monthly articles and social batches from quarterly priorities, then prepare approved content for publishing.
---

# Monthly Content Planning and Publishing SOP

Run this procedure once per month to turn one approved content theme and one long-form anchor article into a reviewed, scheduled batch of social posts.

## Operating model

```text
monthly theme + owner's source material
  -> anchor article draft in Ghost
  -> social batch brief
  -> social posts by approved format mix
  -> human review and revision
  -> approved posts scheduled in Publer
  -> performance and feedback notes
```

The system has three separate lanes:

1. **Strategy and long-form:** owner chooses the monthly topic, supplies the point of view, and owns the finished anchor article.
2. **Social production:** The content agent turns the approved source material into a complete monthly social batch.
3. **Live engagement:** owner currently owns comments, replies, relationship-building, Sales Navigator activity, and real-time posts. This lane is not part of the automated batch and should not block social production.

## Scope and current strategy

Resolve show names, cadence, audience, access model, channel mix, publishing tools,
CTA policy and source locations from the consumer's current strategy and SOP binding.
Core does not define a named newsletter or a one-show limit. Agree batch size with the
owner based on production/review capacity. Reserve capacity for timely work when useful.
The format examples below are optional structures, not the consumer's standing lineup.

## Roles and handoffs

| Role | Responsibility | Handoff |
|---|---|---|
| owner | Choose theme, provide source material, finish the anchor article, review social batch, give final approval, manage live engagement | Ghost draft + brain dump + research/links + CTA + publication date |
| Content agent | Read current strategy, create the social plan and batch, use approved exemplars, record construction notes, revise from feedback, prepare Publer-ready output | Draft batch + review sheet + construction notes |
| Supporting agents | Maintain Notion intake, mini briefs, research, exemplars, and deterministic workflow support | Linked records, source files, and evidence |
| Publer workflow | Schedule only approved posts with approved first comments, links, media, dates, and channels | Approved scheduling queue |

No agent should push unreviewed drafts directly into Publer.

## Required inputs

Before starting, load:

1. `brains/brand/strategy/content-strategy.md`
2. `brains/brand/strategy/README.md`
3. The approved quarterly theme map from `brains/brand/strategy/quarterly-content-planning-sop.md`
4. The current month's Notion content ideas and mini briefs
5. `brains/brand/content/personal/production-log.md`
6. Current LinkedIn exemplars, anti-patterns, and platform guidance in the brand repo
7. Any recent performance notes or final-post feedback from the previous month

For Operator Build ideas, also check the AI Growth Alpha Miner report and the Notion pipeline it feeds. A usable idea should have a mini brief before it enters the social batch.

## Phase 1 — Choose the month's theme and anchor

Run this during the first planning exchange of the month, using the approved quarterly plan as the guardrail.

owner provides, asynchronously or in a short working session:

- The month's theme.
- The primary pillar and perception.
- The concrete anchor article problem.
- A 15-minute WhisperFlow recording or equivalent brain dump.
- Any initial draft already created in Ghost.
- Research, links, examples, screenshots, tools, or source material.
- The desired publication date.
- The CTA and any free-versus-paid newsletter boundary.

The theme should already be approved through quarterly planning. If the topic changes materially, record the change and confirm the pillar/perception mapping before drafting social.

### Monthly source packet

Create or collect one source packet containing:

```markdown
# [Month YYYY] anchor article Source Packet

Theme: [theme]
Primary pillar: [pillar]
Primary perception: [perception]
anchor article working title: [title]
Ghost draft: [link or path]
WhisperFlow brain dump: [link or path]
Research and source links: [links]
Useful artifacts: [templates, skills, GitHub files, screenshots]
Newsletter CTA: [CTA]
Publication target: [date]
Social batch target: [number of posts]
Required format mix: [counts or percentages]
Real-time slots: [number]
```

owner owns the finished newsletter article, including research, links, images, thumbnail, CTA, and Ghost setup. The social agent may use the Ghost draft before publication, but must not rewrite or publish the newsletter unless separately assigned.

## Phase 2 — Select the social mix

Before generating posts, define the month's mix. The mix should reflect the source material, the quarterly strategy, available exemplars, and the need for audience growth.

Use a planning table like this:

| Format | Planned count | Job | Default CTA |
|---|---:|---|---|
| Operator Build | `[N]` | Show a specific skill, workflow, tool, or artifact operators can use | Try it, comment, follow, or visit the public GitHub file |
| Reaction / Market Response | `[N]` | Join a relevant conversation with an opinionated operator perspective | Comment, disagree, or follow |
| Operator POV | `[N]` | Publish original philosophical, strategic, or sharp operator takes | React, comment, or follow |
| anchor article promotion | `[N]` | Build awareness and qualified readership for the monthly guide | Follow the approved CTA and access model |
| Real-time reserve | `[N]` | Leave room for timely news, launches, or audience response | Determined at publication time |

The counts must add up to the approved batch size. A anchor article promotion may also be packaged as an Operator POV, Reaction, or practical excerpt; label the primary job so the batch does not become repetitive.

### Format requirements

#### Operator Build

Use for a specific thing we built or tested recently:

- State the operator problem.
- Explain what the skill, workflow, tool, or artifact does.
- Show how to use it in daily work.
- Link to the public GitHub skill file or artifact when available.
- Attach a Loom or screen-share walkthrough when useful, but do not make video a requirement.
- Tag tools, people, or sources that influenced the build when appropriate.
- Do not require a subscription to access the practical artifact.

Primary source: AI Growth Alpha Miner report → Notion content pipeline → mini brief.

#### Reaction / Market Response

Use for something recently watched, read, heard, or studied:

- Identify the source.
- State what it gets right or wrong.
- Add owner's own interpretation.
- Explain the implication for real operators, agencies, or marketing teams.
- Take a clear position; never manufacture controversy just for reach.
- Tag the person, publication, or source when relevant.

Do not produce a summary with no original point of view.

#### Operator POV

Use for original, unapologetically sharp takes:

- A pattern seen in operator work.
- A philosophical belief about AI-driven marketing.
- A diagnosis of what teams are getting wrong.
- A strong distinction or contrarian claim.

These posts may be less actionable than Operator Build posts. Their job is to create recognition and reaction, but they must still reinforce a pillar or perception and must never be lukewarm.

#### anchor article promotion

Plan the monthly arc across:

- Pre-publication theses, questions, and diagnostics.
- Publication announcement and reader fit.
- Practical excerpts, frameworks, or objections.
- Follow-up learnings, responses, and additional angles.

Use the arc to support the guide without turning the entire month's feed into newsletter promotion.

## Phase 3 — Generate the batch

The content agent should:

1. Read the complete source packet.
2. Read the current strategy, format definitions, platform guidance, exemplars, anti-patterns, and recent feedback.
3. Extract distinct ideas from the long-form piece before drafting.
4. Assign each idea to the approved format mix.
5. Draft the full batch in one reviewable artifact.
6. Include the planned publication date, format, pillar, perception, CTA, first comment, media, source link, and any required tags for every post.
7. Keep posts meaningfully different in angle, structure, hook, and CTA.
8. Preserve real-time slots rather than filling every slot with another derivative.

### Draft output schema

Store the batch as one file per month. Each post should use this structure:

```markdown
## Post [NN] — [Working title]

- Format: [Operator Build / Reaction / Market Response / Operator POV / anchor article promotion]
- Platform: LinkedIn
- Target date: [YYYY-MM-DD]
- Pillar: [pillar]
- Perception: [P#]
- Job: [reach / engagement / authority / newsletter conversion]
- CTA: [CTA]
- Source: [anchor article / Notion mini brief / external source / original POV]
- Tags: [people, tools, publications]
- Media: [none / image / Loom / screen recording]
- First comment: [comment or none]
- Status: Draft

### Post copy

[Draft]
```

Use source links in the first comment when that is the platform-appropriate pattern. Do not hide important context or a required disclosure.

## Phase 4 — Human review gate

The content agent must deliver the complete batch for review before any post is scheduled.

Use a review sheet or equivalent durable table with these columns:

| Post | Format | Copy | owner decision | Feedback | Revision status | Final copy | Scheduling status |
|---|---|---|---|---|---|---|---|
| `[NN]` | `[format]` | `[link]` | Approve / Revise / Reject | `[notes]` | Pending / Revised / Accepted | `[link or text]` | Not scheduled / Approved / Scheduled |

owner reviews for:

- Correct pillar and perception.
- Clear difference between post types.
- Human, authentic voice and appropriate length.
- Strong enough hook and specific enough point.
- No repetitive “read the newsletter” CTAs.
- Correct ratio of post types.
- Accurate claims, source attribution, tags, links, and first comments.
- Useful public artifacts where promised.
- Fit for LinkedIn and the intended audience.

### Revision loop

1. owner marks each post **Approve**, **Revise**, or **Reject**.
2. For revisions, owner gives concrete notes where possible.
3. The content agent revises the full set or the specified posts.
4. owner approves the final versions.
5. Only approved versions enter the Publer queue.

Do not send a batch directly to Publer before this gate. The current failure mode is generating posts, seeing that they are weak inside Publer, and abandoning the batch. The review gate exists to catch that earlier and make the feedback reusable.

## Phase 5 — Capture construction feedback

Feedback given during review must be recorded in a central construction-notes file, not left only in chat.

Capture:

- Patterns owner liked.
- Patterns owner rejected.
- Words, phrases, structures, hooks, or CTAs to avoid.
- Posts that were stronger after revision.
- Final versions that differ materially from the generated versions.
- Platform-specific observations.

Translate repeated feedback into:

- **Exemplars:** final posts that should be imitated.
- **Anti-patterns:** rejected patterns that should not recur.
- **Rules:** concise durable guidance for the drafting tool or agent.

Never reintroduce a specifically rejected phrase or style without an explicit reason. For example, if owner says never to use a particular word, record that as a standing anti-pattern.

If owner publishes a materially edited version, store the final version next to the generated version and label it **Final published version**. Final human edits are training data for the next batch.

## Phase 6 — Schedule approved posts

After final approval:

1. Confirm every approved post has a date, channel, copy, CTA, first comment, link, media, and tags.
2. Confirm the monthly mix and weekly cadence one more time.
3. Push only approved posts into Publer.
4. Spot-check the Publer preview for formatting, links, media, mentions, and first comments.
5. Record the scheduling timestamp and status.

Scheduling is a mechanical handoff. It is not a second editorial review and it must not be used to bypass the human review gate.

## Phase 7 — Live engagement and real-time posts

owner currently owns:

- Monitoring comments on live posts.
- Replying and liking comments.
- Following up with people who engage.
- Sales Navigator lists and relationship-building.
- Timely posts that were not known during monthly planning.

When a real-time post replaces a planned slot, record the substitution in the monthly batch file. When it is additive, record it as an extra post and note the capacity impact.

## Phase 8 — Close the month and update the system

At the end of the month, add performance notes to the batch record. Keep them practical and directional rather than pretending the data proves more than it does.

Capture:

- Impressions and reach.
- Relevant engagement, comments, shares, saves, and profile visits.
- Follows or qualified audience growth.
- Newsletter clicks or subscriptions where applicable.
- GitHub clicks, skill usage signals, or Loom engagement for Operator Build.
- Which formats and angles earned the strongest qualified response.
- Which posts were weak, repetitive, or rejected.
- Any audience language worth feeding into the next theme or mini brief.

Then update:

1. The monthly batch file.
2. The construction feedback ledger.
3. The production log.
4. The format exemplar and anti-pattern library.
5. The next month's planning inputs.

## Monthly file package

Create one durable package for each month under the brand content workspace. At minimum, it should contain:

```text
[month]-content-batch/
  source-packet.md
  social-batch.md
  review-sheet.md
  construction-notes.md
  performance-notes.md
```

Use the existing brand content and production-log conventions when choosing the exact directory. Do not leave the final batch, feedback, or performance notes only in Slack, Publer, or chat.

## Completion checklist

- [ ] Monthly theme is within the approved quarterly plan.
- [ ] Theme maps to a pillar and perception.
- [ ] owner supplied the anchor article draft or source packet.
- [ ] owner owns the finished Ghost newsletter, links, images, CTA, and publication date.
- [ ] Social platform scope is explicit; default is LinkedIn only.
- [ ] Post count and format mix are approved.
- [ ] Operator Build ideas have Notion mini briefs when sourced from the AI Growth Alpha Miner report.
- [ ] Social batch is stored as one durable reviewable artifact.
- [ ] Every post has format, pillar, perception, CTA, source, and status metadata.
- [ ] Human review happened before Publer scheduling.
- [ ] Revision feedback was recorded centrally.
- [ ] Only approved final versions were scheduled.
- [ ] Real-time substitutions were logged.
- [ ] End-of-month performance notes were added.
- [ ] Exemplars, anti-patterns, and final human edits were fed back into the system.

## Related sources

- [brand content strategy](content-strategy.md)
- [Quarterly content planning SOP](quarterly-content-planning-sop.md)
- [brand strategy index](README.md)
- [Production log](../content/personal/production-log.md)
- [Demand-gen playbook](brand-Demand-Gen-Content-Playbook.pptx)
