---
name: ai-tool-review
description: Write a product-review style AI tool evaluation with a decisive verdict, differentiated alternatives, and promo social posts, grounded in firsthand testing and the entity's real voice.
---

# AI Tool Review

Write a product-review style AI tool evaluation with a decisive verdict, differentiated alternatives, and promo social posts, grounded in firsthand testing and the entity's real voice.


**Core principle:** You're testing these tools so your readers don't have to. Evaluate like a growth engineer, not a casual user. Every review answers: Can this plug into a real marketing workflow? Does the output hold up when real money is behind it?

> Entity note ({brain}=brand): runs weekly as the "AI Tool Reviews" series on Substack, framed as "Good Housekeeping for AI marketing tools."

---

## When To Use

- Reviewing an AI marketing, content, sales, analytics, or productivity tool
- Turning a transcript or testing notes into a publishable review
- Creating a recurring editorial series with a consistent verdict structure

---

## Workflow Overview

```
/ai-tool-review runs:

1. VOICE LOAD         → Load {brain}/voice/voice-synthesis.md + 2 social exemplars
2. BRAND LOAD         → Load {brain}/strategy/brand-strategy.md for the closing pitch
3. TOOL RESEARCH      → Web search for tool details, pricing, competitors, ratings
4. TRANSCRIPT/INPUT   → Process user's transcript, notes, or testing observations
5. ARTICLE CREATION   → Full review article (6 sections + close)
6. PROMO POSTS        → LinkedIn + Twitter promo posts
7. OUTPUT             → Single markdown file ready for the publication channel

Produces: 1 review article + 1 LinkedIn promo + 2 Twitter posts
```

---

## Step 1: Voice & Brand Load

### Voice Load (Required)

1. Read `{brain}/voice/voice-synthesis.md`
2. Read at least 2 exemplars from `{brain}/voice/voice-exemplars/social/`
3. Apply voice profile throughout (see Voice Rules below)

If voice files are unavailable, ask for a short writing sample or proceed with explicit, stated assumptions.

### Brand Load (Required)

1. Read `{brain}/strategy/brand-strategy.md`
2. Extract: main message, supporting arguments, client points, brand voice
3. Use for the closing pitch section

---

## Step 2: Tool Research

Before writing, gather current data on the tool:

1. **Web search** for the tool name + "review," "pricing," "alternatives"
2. **Collect:**
   - Official name, correct spelling, and URL
   - What it does (feature summary)
   - Pricing tiers and plan limits
   - User ratings (G2, Capterra, etc.) or reputation signals
   - Funding/company background (if notable)
   - Direct competitors (3-5)
3. **Cross-reference** against the user's firsthand experience from the transcript

Keep verified research facts clearly separated from the author's firsthand experience. Any pricing, ratings, or company details must be re-verified at run time, never assumed from prior runs.

---

## Step 3: Process User Input

The user will provide one of:
- **Transcript** (voice memo, Loom, screen recording with narration)
- **Written notes** (bullets, observations, raw thoughts)
- **Conversation** (answering prompts about their experience)

### If Transcript

1. Identify the **core verdict** — do they recommend it or not?
2. Extract **specific observations** — what worked, what didn't, exact moments of friction or delight
3. Note **natural phrases** — how they describe the tool in their own words
4. Mark **stories with detail** — the tested use case and specific scenarios they walked through
5. Capture **comparison points** — how they compared it to alternatives
6. Note **who should and should not use the tool**, in their framing

### If No Input Provided

Ask the user these prompts:

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI TOOL REVIEW — Input Capture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WHAT TOOL? Name, URL, what category it's in.

2. WHAT DID YOU TEST? Walk me through what you actually did
   with it. What was your use case?

3. FIRST IMPRESSION? What was setup/onboarding like?

4. WHAT WORKED? Specific things that impressed you or
   saved you time.

5. WHERE DID IT BREAK? Specific moments of friction,
   limitation, or disappointment.

6. WOULD YOU USE IT AGAIN? For what? For whom?

7. WHAT ELSE IS OUT THERE? Other tools you've tried
   or would consider instead?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 4: Article Creation

### Article Structure (6 Sections)

**Target length:** 1,200-1,800 words (unless the publication channel requires otherwise)
**Tone:** Direct, evaluative, builder-mindset. Like a product review on Wirecutter or Good Housekeeping — not a blog post, not a listicle.

---

#### Section 1: Why I'm Reviewing AI Tools (Series Intro)

**Length:** 3-4 paragraphs
**Purpose:** Establish credibility and frame the series

**Must include:**
- What this series is (AI tool reviews from a practitioner, not a casual user)
- Why the author is qualified (drawn from `{brain}/strategy/` client points: role, company, relevant operating experience, testing tools in real workflows)
- How you evaluate (can it plug into a real workflow? does the output hold up with real money behind it?)
- Why readers should care (the space is overwhelming, you're cutting through noise)

> Entity note ({brain}=brand): the qualification framing is — organization founder, enterprise experience at AmEx/Verizon/UHG, testing tools in real client workflows. Series framing: "Good Housekeeping for AI marketing tools."

**Note:** This section stays largely consistent across reviews. Adjust the opening hook to match the tool category being reviewed (ad creation, SEO, content, analytics, etc.).

---

#### Section 2: The Tool

**Length:** 4-6 paragraphs
**Purpose:** Objective overview of what the tool is and does

**Must include:**
- Tool name (correct spelling) and what it claims to do
- How it works (onboarding, core workflow, key features)
- Who's behind it (funding, company context if notable)
- Pricing (specific tiers, what features live where)
- Popularity (G2/Capterra ratings, community buzz, adoption signals)
- Competitors (3-5 direct alternatives, named)

**Voice note:** Factual and informative here. Save opinions for sections 3-5.

---

#### Section 3: Bottom Line Up Front (BLUF)

**Length:** 3-5 short paragraphs
**Purpose:** The verdict, stated clearly before the detail

**Structure:**
- **Overall verdict:** One of: "Recommend" / "Conditional recommendation" / "Do not recommend" — with a one-sentence summary
- **Recommend for:** Who benefits most and for what use case (be specific)
- **Do not recommend for:** Who should skip it and why (be specific)
- **Best for:** The ideal user profile in one sentence

**Voice note:** Be decisive. Hedge on scope ("good for X, not for Y"), not on opinion. The reader should know exactly what to do after reading this section alone.

---

#### Section 4: What I Liked (Pros)

**Length:** 4-6 items, each 2-4 sentences
**Purpose:** Specific things that worked well

**Format:** Bold heading per item + explanation

**Rules:**
- Every pro must come from firsthand testing (never from marketing copy)
- Be specific: "onboarding took 4 minutes" not "onboarding was easy"
- Explain WHY it matters for a real workflow, not just that it exists
- If a feature is impressive but not ready, say so (e.g., "nice bonus" vs. "core value")

---

#### Section 5: What I Disliked (Cons)

**Length:** 4-6 items, each 2-4 sentences
**Purpose:** Specific friction points, limitations, and deal-breakers

**Format:** Bold heading per item + explanation

**Rules:**
- Lead with the biggest deal-breaker first
- Be specific about WHERE in the workflow things broke down
- Distinguish between "fixable with better inputs" vs. "structural limitation"
- Don't soften real problems — if the UI is bad, say it's bad
- Note if the issue is specific to this tool or category-wide

---

#### Section 6: Better Alternatives to Consider

**Length:** 3-5 alternatives, each 2-3 sentences
**Purpose:** Help readers find the right tool even if this one isn't it — help the reader choose, don't merely list competitors

**Format:** Bold tool name + what it's best for + price point if known

**Must include:**
- At least 3 named alternatives with specific use-case differentiation
- A "my recommended approach" paragraph — often a workflow recommendation rather than a single tool
- Price points where available

**Close with:** The brand pitch (see below)

---

### The Brand Pitch (Closing Section)

Every review ends with a brief, natural bridge to the entity's offer, built from `{brain}/strategy/brand-strategy.md`. Not a hard sell — a "if this feels like a lot, this is what we do" transition. Adapt the first sentence to match the tool category reviewed (e.g., "If building an ad creative pipeline feels like a lot..." or "If choosing between 15 SEO tools feels overwhelming...").

Resolve any closing offer and CTA from the consumer's current approved positioning.
Do not inherit a pitch, staffing-replacement claim, time-to-results promise, pricing
comparison or destination URL from a shared example. Omit unsupported claims and
verify the offer is current before adding it to a review.

---

### Article Closing

After the pitch, end with an italicized reader question:

> *Have you tried [Tool] or any of the other [category] tools? Which ones are you using in your workflow right now? I'm testing a new one every few weeks, and I'd love to hear what's actually working for you.*

---

## Step 5: Promo Posts

Create at least one LinkedIn post and one short X/Twitter post (plus an optional newsletter intro or social teaser). Promos should reveal the verdict and tension without replacing the full review.

### LinkedIn Promo

**Length:** 100-150 words
**Tone:** Sharp, substantive — per the loaded voice profile

> Entity note ({brain}=brand): the target register is the "Elena + Sam blend" from the brand voice synthesis.

**Structure:**
1. What you tested (tool name + category)
2. The one-line verdict
3. The best thing about it (1 sentence)
4. The worst thing about it (1 sentence)
5. "Full review with my recommendation + alternatives on Substack. Link in comments."

**Rules:**
- No hashtags
- No engagement bait
- No emojis
- Don't give away the full review — give enough to click through

### Twitter Promo

**Tweet 1:** The BLUF in 2-3 sentences. Verdict + the core tension. Link to the full review.

**Tweet 2 (Reply thread):** Zoom in on the most interesting finding or the biggest problem. Should stand alone as a valuable observation even without clicking through.

**Rules:**
- Sharper and more provocative than LinkedIn
- Can use fragments and casual register
- No hashtags

---

## Step 6: Output

### File Location

`{brain}/content/ai-tool-review-[tool-name]-YYYY-MM-DD.md`

Single markdown file: article + promo posts together, ready for the publication channel.

### File Format

```markdown
---
title: "AI Tool Review: [Tool Name] — [Subtitle Question]"
type: product-review
series: AI Tool Reviews
pillar: Industry POV / AI-Equipped Growth Engineering
platform: Substack
status: draft
created: YYYY-MM-DD
---

# AI Tool Review: [Tool Name] — [Subtitle Question]

## Why I'm Reviewing AI Tools (And Why You Should Care)

[Series intro — 3-4 paragraphs]

---

## The Tool: [Tool Name]

[Objective overview — 4-6 paragraphs]

---

## Bottom Line Up Front

[Verdict — 3-5 short paragraphs]

---

## What I Liked

[Pros — 4-6 bolded items with explanations]

---

## What I Disliked

[Cons — 4-6 bolded items with explanations]

---

## Better Alternatives to Consider

[3-5 alternatives + "my recommended approach"]

---

## The Pitch

[Brand closing — adapted opening line + standard pitch from {brain}/strategy/]

---

*[Reader question]*

---

## Promo Posts

### LinkedIn Promo

[100-150 words]

### Twitter Promo — Tweet 1

[BLUF + link]

### Twitter Promo — Tweet 2 (Reply Thread)

[Standalone observation]
```

(The `pillar` and `platform` frontmatter values above are the brand defaults; set per entity.)

---

## Voice Rules (All Formats)

### Do
- Use the user's exact phrases from their transcript/notes
- Be specific (tool names, price points, feature names, time spent)
- State opinions directly — "this is good," "this doesn't work"
- Ground every claim in firsthand testing
- Keep the builder-mindset: "here's what I found when I actually used it"

### Don't
- Use em-dashes (use commas, parentheses, or restructure)
- Use engagement bait, hashtags, or emojis
- Invent features or experiences not in the user's input
- Hedge opinions ("it might potentially be somewhat useful")
- Use "AI-powered" as a differentiator (per brand voice guidelines)
- Use formulaic hook-framework-lesson-question structure

### AI-Tell Anti-Patterns (Kill on Sight)
- Perfect parallel bullet lists with identical structure/length
- Em-dash + rhetorical question chains
- Thesis-statement closers that package the lesson in a bow
- Teaser bait openers ("What I found surprised me.")
- Spec-sheet formatting in personal posts
- Every section mirroring perfectly — real observations are asymmetric

---

## Quality Checklist

Before finalizing:

- [ ] Correct tool name and spelling throughout
- [ ] Pricing is current and sourced (re-verified at run time)
- [ ] BLUF verdict is clear, decisive, and scoped (not wishy-washy)
- [ ] Every pro/con traces to firsthand testing or clearly cited research
- [ ] At least 3 named alternatives with differentiated use cases that help the reader choose
- [ ] Brand pitch is included but not heavy-handed
- [ ] No em-dashes anywhere
- [ ] Reads like a product review by a trusted operator who tested the tool in a real workflow — not a blog post or ad
- [ ] LinkedIn promo doesn't give away the full review
- [ ] Twitter promo stands alone as valuable

---

## Quick Actions

After running /ai-tool-review, common follow-ups:

- "Sharpen the verdict" → Rewrites BLUF with stronger language
- "Add more detail to [section]" → Expands specific section with more testing observations
- "This doesn't sound like me" → Re-extracts from user input, reduces AI voice
- "Make the promo posts punchier" → Rewrites social posts with sharper hooks
- "Add a comparison table" → Creates feature/price comparison grid for alternatives section

---

## Adaptation Notes

- Repo-native agents are best when transcripts, notes, and brain files live in the repo; chat surfaces are useful for live interview capture and review refinement.
- Any current pricing, ratings, or company details should be re-verified at run time.
