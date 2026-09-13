---
name: linkedin-post
description: Turn a raw idea into one voice-matched LinkedIn post, or turn a source article and its evidence into a deliberately varied batch of posts. The workflow protects the source's meaning, separates supported claims from opinion, and produces copy for human review rather than publishing it.
---

# LinkedIn Post

Turn a raw idea into one voice-matched LinkedIn post, or turn a source article and its evidence into a deliberately varied batch of posts. The workflow protects the source's meaning, separates supported claims from opinion, and produces copy for human review rather than publishing it.

**Use this skill when:**

- a voice memo, brain dump, topic, or rough draft should become one standalone post (`single_post`); or
- a completed long-form article should become a small campaign of evidence-backed posts (`article_batch`).

Do not use `article_batch` to invent a campaign from a thin topic. Draft or research the long-form source first.

## Modes and conditional references

Choose the mode before loading supporting material.

| Mode | Trigger | Required inputs | Load |
|---|---|---|---|
| `single_post` | One idea or one post requested | Raw idea, transcript, or draft | This file only |
| `article_batch` | Multiple posts requested from a completed article | Source article plus evidence ledger or evidence handoff | This file **and** `references/article-batch.md` |

If the user does not name a mode, use `article_batch` only when both the source article and evidence material are available. Otherwise use `single_post`.

Load `references/article-batch.md` only for `article_batch`. Its claim controls and batch contract do not add ceremony to a single-post request.

## Shared guardrails

1. **Match the supplied voice, not a house voice.** Use the entity's voice profile and exemplars when available. If they are absent, preserve the source language and use a clear, natural professional register. Say that voice matching is limited rather than inventing brand rules.
2. **Keep claims inside the evidence boundary.** Never improve copy by upgrading a possibility into a fact, adding a number, inventing a customer result, or implying firsthand experience that the source does not establish.
3. **Distinguish fact, inference, and opinion.** Facts need support. Inferences need qualifying language. Opinions need a clear point of view, not false authority.
4. **Protect meaning while changing form.** A hook may sharpen tension, but it must not distort the article, source, or speaker's position.
5. **Do not publish.** Return review-ready copy and any requested file artifacts. Publishing, scheduling, tagging people, and external messages require a separate authorized workflow.
6. **Treat platform conventions as choices, not universal laws.** Length, punctuation, capitalization, emoji, bullets, links, and closing questions should follow the supplied voice and campaign goal.

## Voice calibration

Before drafting, read any supplied voice profile and at least two relevant exemplars when they exist. Extract:

- tone and level of formality;
- sentence and paragraph rhythm;
- characteristic vocabulary or phrases;
- acceptable sharpness, humor, and vulnerability;
- formatting and punctuation tendencies;
- explicit banned phrases or anti-patterns.

Do not copy an exemplar's factual claims, personal history, or signature phrasing. Do not blend named creators or internal personalities unless the user explicitly supplies that direction.

When no profile or exemplars are available, use phrases from the raw input or article as the primary voice evidence. Flag this limitation once; do not block a useful draft.

---

# Mode A: `single_post`

This mode preserves the original high-touch workflow: intake, shape, hook options, draft, voice check, iteration, and clean output.

## 1. Intake

Classify the input and extract the material before writing.

| Input | Treatment |
|---|---|
| Brain dump or transcript | Find the central thesis, remove repetition, and preserve distinctive phrases |
| Short topic | Ask up to three targeted questions if a credible post would otherwise require invented specifics |
| Rough draft | Preserve intent and useful language; move directly to diagnosis and revision |
| Linked source | Treat the supplied content as source material; do not claim it was read if it is inaccessible |

Capture:

- the one point the reader should remember;
- specific examples, observations, numbers, and named tools that are actually supplied;
- phrases that sound distinctively like the author;
- the audience and desired response;
- material that belongs in a follow-up rather than this post.

If the input is thin, ask questions such as: "What happened that made you think this?", "What concrete example can you share?", or "What should the reader do differently?"

## 2. Shape

Select a structure based on the material rather than forcing a branded content type. Useful shapes include:

- **Point of view:** a defensible claim with reasoning and an implication;
- **How-to:** a process with practical context and one meaningful judgment;
- **Review:** a clear verdict, evidence, and who the subject is or is not for;
- **Build note:** a real change, the messy middle, and what the author learned;
- **Story:** a concrete scene that earns a broader observation.

Choose the shortest length that lets the idea land. Avoid prescribing fixed character bands or claiming an engagement advantage without current, applicable data.

Before drafting, briefly state the proposed shape, core thread, and material being left out. For an interactive request, get confirmation when that will materially affect the result. If the user asked for direct execution, make the choice and proceed.

## 3. Hooks

Offer three to five genuinely different hook directions when the workflow is interactive. Vary the underlying angle, not just synonyms. Common options include:

- a concrete observation or result supported by the input;
- a defensible counterpoint to a familiar belief;
- a recent, specific scene;
- an honest admission or tension;
- the consequence for a clearly defined audience.

Never manufacture recency, a result, a client anecdote, or a controversy for stopping power. Explain each option in one short line, recommend one, and let the user choose or redirect. When the user requested a finished draft without an intermediate selection, choose the most faithful option and proceed.

## 4. Draft

Build the post around one coherent thread:

1. Open with the chosen hook.
2. Establish only the context needed to understand it.
3. Support the point with supplied evidence, an example, reasoning, or a useful process.
4. End with an implication, decision, or next step that follows from the body.

Use specifics where the source supports them. Vary paragraph length naturally. A list is appropriate when it makes a process easier to use; it does not need artificial symmetry. A question or call to action is optional and should serve the reader rather than function as generic engagement bait.

## 5. Voice and integrity check

Before showing the draft, check:

- Does this sound consistent with the supplied voice evidence?
- Did the draft retain the author's strongest language without mimicking an exemplar?
- Is every factual assertion traceable to the input or clearly framed as opinion/inference?
- Did any unsupported number, result, customer story, quotation, or firsthand claim slip in?
- Is the hook paid off by the body?
- Are sentence fragments, repeated transitions, parallel lists, or one-line paragraphs being used intentionally rather than mechanically?
- Does the close feel earned, or does it package the post in a generic lesson/question?
- Would the author plausibly say this aloud?

Revise before presenting if any answer fails.

## 6. Iterate and output

When feedback targets one section, change that section unless the change creates a consistency problem elsewhere. Re-run the voice and integrity check after every material revision.

Return the final post as clean copy without drafting notes. If file output is requested, save it to the operating repository's approved social-content location; do not assume a universal content-root convention. Optionally list unused material for comments or a follow-up after the clean copy.

---

# Mode B: `article_batch`

Read and follow `references/article-batch.md`. This mode must produce:

1. a source and evidence audit;
2. a deliberately diverse batch of review-ready LinkedIn posts;
3. a compact coverage map showing the distinct job of each post;
4. a landing-page handoff for conversion review.

The source article is the message boundary. The evidence ledger or handoff is the claim boundary. If there is not enough supported material for the requested count, return fewer strong posts and name the gap. Never pad the batch with invented claims, generic filler, or paraphrases of the same post.

## Quality standard

A successful result is:

- specific without becoming less accurate;
- recognizably voiced without importing somebody else's identity;
- varied in argument, evidence, structure, and reader job;
- useful to a B2B reader, not merely promotional;
- explicit about evidence gaps;
- ready for human review and a downstream landing-page audit.

## Portability notes

- Paths and output locations come from the operating repository, not this skill.
- Voice profiles, exemplars, evidence ledgers, and brand constraints are inputs, not embedded defaults.
- If a platform limit or current best practice matters, verify it against a current authoritative source or state it as a configurable constraint.
- Adapters may add entity-specific validation, but they must not weaken the evidence boundary or silently publish content.
