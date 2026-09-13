---
name: seo-qc
description: 'Post-draft optimization and quality check for articles before publishing: takes a draft, scores it across SEO, AEO, and content quality dimensions, and recommends prioritized fixes.'
---

# SEO/AEO Quality Check

Post-draft optimization and quality check for articles before publishing: takes a draft, scores it across SEO, AEO, and content quality dimensions, and recommends prioritized fixes.


**Input:** `$ARGUMENTS` = file path to draft article (example: `{brain}/content/article-example.md`)

**Related core skills:** drafts typically come from `content-produce`; voice anti-patterns are defined in `writing`.

---

## Step 1: Load Article + Context

1. Read the article at `$ARGUMENTS`
2. Extract frontmatter: `title`, `content_type`, `slug`, `status`, target keyword (if present)
3. Resolve the article type, length guidance and required structure from the current
   consumer content strategy and approved brief. Do not infer a named show or word
   range from an old shared filename example. Flag missing requirements explicitly.
4. Load voice profile: `{brain}/voice/voice-synthesis.md`
5. Load content strategy: `{brain}/strategy/content-strategy.md` (if exists)

---

## Step 2: SEO Checks

Run each check and record pass/fail + details:

### 2a. Title & H1
- H1 heading present
- Target keyword appears in H1 (or close variant)
- Title length: 50-60 characters ideal
- Title is compelling (not just keyword-stuffed)

### 2b. Meta Description
- Present in frontmatter (`description` or `meta_description` field)
- Length: 150-155 characters
- Includes target keyword naturally
- Reads as a compelling search result snippet

### 2c. Heading Structure
- H2/H3 hierarchy is clean (no skipped levels)
- Heading count fits the approved brief and content complexity
- At least 2 subheadings include keyword variants or related terms
- Closing section serves the current brief and CTA

### 2d. Internal Links
- Count links to the entity's owned properties
- Target: 3-5 internal links
- Links use natural anchor text (not "click here" or bare URLs)

Resolve approved owned properties from the consumer source register; do not assume a shared newsletter domain.

### 2e. External Authority Links
- Count links to external domains
- Target: 2-4 external links
- Links point to credible sources (research, named experts, tool docs)
- No links to direct competitors

### 2f. Word Count
- Count words in article body (exclude frontmatter)
- Compare to target range for content type
- Flag if under minimum or over maximum

### 2g. Image Alt Text
- Check all images for alt text presence
- Alt text should be descriptive, include keyword where natural

### 2h. URL Slug
- Slug present in frontmatter
- 3-6 words, hyphenated, includes primary keyword
- No stop words, no dates unless necessary

---

## Step 3: AEO Checks (AI Engine Optimization)

### 3a. Direct Q&A Pairs
- Article explicitly poses and answers questions AI models would surface
- Look for patterns: "What is...?", "How do you...?", "Why does...?"
- Target: 2-3 clear question-answer sequences in the article

### 3b. Extractable Definitions
- At least 1-2 paragraphs that define a concept in 2-3 clean sentences
- These should work as standalone snippets an AI could quote verbatim
- Check: Could you pull this paragraph out and it would make sense alone?

### 3c. Structured Data Opportunities
- **Article schema:** Does frontmatter have enough for Article structured data? (title, author, datePublished, description, image)
- **FAQ schema:** Are there 2+ Q&A pairs that could be marked up as FAQ?
- **HowTo schema:** Does the article contain step-by-step instructions?
- Note which schemas apply and what's missing

### 3d. Citation-Worthy Statements
- Count specific, quotable claims with numbers, named sources, or data
- Target: 3-5 per article
- Examples: "X increased by 40%", "According to [named source]", "[Specific tool] costs $X/mo"
- Flag if the article is mostly opinion without concrete anchors

### 3e. First-Paragraph Snippet
- Does the first paragraph (after the hook) summarize the article's core argument?
- Could an AI model extract the first 2-3 sentences as a useful answer?
- If the opening is purely narrative, flag as "weak snippet lead"

---

## Step 4: Content Quality Checks

### 4a. Opening Hook
- Does the first paragraph create tension, curiosity, or a story?
- Does it avoid rushing to the thesis?
- Is it specific (not generic "In today's world..." or "Everyone knows...")?

### 4b. CTA Presence
- At least 1 newsletter subscribe CTA (soft, mid-article or end)
- At least 1 contextual CTA (lead magnet, service, or resource)
- CTAs sound like the author's voice, not inserted ads

### 4c. Readability
- Sentence length variation (mix of 8-word and 25-word sentences)
- Paragraph length: mostly 2-4 sentences, some 1-sentence for punch
- No jargon without explanation
- No em-dashes (per voice rules)
- No bullet/numbered lists in Build Log (woven into prose)

### 4d. Voice Match
- Read against `{brain}/voice/voice-synthesis.md`
- Also check for specificity and client: concrete details, evidence, and examples rather than generic assertions
- Check for AI-tell anti-patterns from the `writing` skill:
  - Perfect parallel bullet lists
  - Em-dash + rhetorical question chains
  - Thesis-statement closers that package the lesson in a bow
  - Formulaic closing questions
  - Consultant jargon packaging
- Does it sound like the author or like a template got filled in?

> Entity note ({brain}=organization): the author voice benchmark is owner; the em-dash and no-bullet rules in 4c come from this entity's voice rules.

---

## Step 5: Output Scorecard

Present results in this format, and save the scorecard as an artifact to `{brain}/ops/seo/qc-{slug}-{date}.md`:

```markdown
# SEO/AEO QC — [Article Title]

**File:** [path]
**Content Type:** [type from current consumer brief]
**Word Count:** [X] words ([within range / X words short / X words over])
**Overall Score:** [0-100] / 100

---

## Category Scores

| Category | Score | Status |
|----------|-------|--------|
| SEO | [0-40] / 40 | [Pass / Needs Work / Fail] |
| AEO | [0-30] / 30 | [Pass / Needs Work / Fail] |
| Content Quality | [0-30] / 30 | [Pass / Needs Work / Fail] |

---

## Issues Found

### Critical (fix before publish)
- [Issue with line reference and specific fix]

### Important (should fix)
- [Issue with line reference and specific fix]

### Minor (nice to have)
- [Issue with line reference and specific fix]

---

## Quick Wins (auto-fixable)
- [ ] [Thing that can be fixed right now with a specific edit]

## Deeper Rewrites
- [ ] [Section that needs rethinking, with guidance on direction]

---

## Missing Metadata (for structured data)
- [ ] meta_description: [suggested text if missing]
- [ ] og_title: [suggested text if missing]
- [ ] og_description: [suggested text if missing]
- [ ] slug: [suggested slug if missing]
- [ ] FAQ schema pairs: [list Q&A pairs found in article]
```

Include replacement copy where useful.

### Scoring Guide

**SEO (40 points)**
- Title/H1: 8 pts
- Meta description: 6 pts
- Heading structure: 6 pts
- Internal links: 6 pts
- External links: 4 pts
- Word count: 4 pts
- Image alt text: 3 pts
- URL slug: 3 pts

**AEO (30 points)**
- Q&A pairs: 8 pts
- Extractable definitions: 6 pts
- Structured data readiness: 6 pts
- Citation-worthy statements: 6 pts
- First-paragraph snippet: 4 pts

**Content Quality (30 points)**
- Opening hook: 8 pts
- CTA presence: 6 pts
- Readability: 8 pts
- Voice match: 8 pts

---

## Step 6: Auto-Fix (Optional)

After presenting the scorecard, ask:

> "Want me to auto-fix the quick wins? I can: [list applicable fixes]"

**Auto-fixable items:**
- Generate missing `meta_description` in frontmatter
- Generate missing `og_title` and `og_description`
- Generate or clean up `slug`
- Add FAQ schema block (as HTML comment at end of article)
- Suggest internal links by searching the entity's owned property via WebSearch for related published articles (e.g. `site:<your-owned-domain>`; the owned property is recorded in the brain — see the entity note above)

**Not auto-fixed (require author judgment):**
- Rewriting the opening hook
- Restructuring headings
- Adding external authority links (need to verify relevance)
- Voice rewrites
- Adding CTAs (placement is editorial)

If user confirms, apply fixes directly to the file and re-run the scorecard to show improvement.

---

## Quick Actions

After running `/seo-qc`, common follow-ups:

- "Fix the quick wins" → Apply auto-fixable items, re-score
- "Suggest internal links" → WebSearch the owned property (`site:<your-owned-domain> [topic]`), recommend 3-5 with anchor text
- "Generate FAQ schema" → Extract Q&A pairs, output JSON-LD block
- "Rewrite the meta" → Generate 3 meta description options to choose from
- "Check another article" → Run on a different file path

---

## Quality Standard

- Every recommendation should be actionable.
- Do not flatten voice in the name of SEO.
- AEO improvements should make answers clearer, not spammy.

## Adaptation Notes

- Codex can parse local markdown drafts and write QC reports.
- ChatGPT can help rewrite sections interactively with the author.
