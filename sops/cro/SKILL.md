---
name: cro
description: 'Conversion rate optimization audits for landing pages and key webpages: fetch the page, analyze it through a priority-ordered 7-dimension framework, and output prioritized recommendations with specific copy alternatives.'
---

# CRO Audit

Conversion rate optimization audits for landing pages and key webpages: fetch the page, analyze it through a priority-ordered 7-dimension framework, and output prioritized recommendations with specific copy alternatives.


## When To Use

- Auditing a landing page, homepage, pricing page, signup page, or campaign page
- Reviewing why traffic is not converting
- Preparing copy and UX improvements before an experiment

## Workflow Overview

```
1. CONTEXT INTAKE → Gather business context upfront
2. PAGE FETCH     → Retrieve page content via WebFetch (or provided copy)
3. CRO ANALYSIS   → Work through priority-ordered framework
4. OUTPUT         → Markdown with recommendations + copy alternatives
```

---

## Modes

### Depth Toggle
- **Quick audit** (default): Top 5 issues, fixes, copy alternatives. Fast turnaround.
- **Comprehensive**: Full 7-dimension framework analysis, test hypotheses, detailed recommendations.

### Output Format Toggle
- **Internal**: Rough notes, shorthand, for refinement. Good for first pass.
- **Client-ready**: Polished prose, clear rationale, shareable with stakeholders.

---

## 1. Context Intake

Before fetching the page, ask these questions and wait for responses. Pre-fill answers from `{brain}/context/` and `{brain}/strategy/` (ICP, positioning) when auditing the entity's own pages — only ask for what the brain doesn't already know.

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRO AUDIT — Context Intake
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I need some context to make this audit useful. Quick answers are fine.

1. INDUSTRY / BUSINESS TYPE
   What does this company do? (SaaS, e-commerce, services, etc.)

2. TARGET AUDIENCE
   Who is the ideal visitor? (Job title, company size, pain points)

3. PRIMARY CONVERSION GOAL
   What action should visitors take? (signup, demo request, purchase, contact, etc.)

4. TRAFFIC SOURCES
   How do visitors typically arrive? (paid ads, organic, email, referral)
   (Optional - say "unknown" if not sure)

5. CURRENT CONVERSION RATE
   What's the current conversion rate, if known?
   (Optional - say "unknown" if not available)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Processing Context

After user responds:
1. Note the **conversion goal** - this is the lens for all analysis
2. Identify **audience pain points** - these should be addressed on page
3. Flag **traffic source implications** - cold traffic needs more context than warm
4. Adjust expectations based on **industry benchmarks** if CVR provided

---

## 2. Page Fetch

If URL not provided with command invocation:
```markdown
What URL should I analyze?
```

Use **WebFetch** to retrieve page content. A URL, local HTML, screenshot notes, or pasted page copy all work as inputs.

If page fetch fails:
- Check URL is valid and publicly accessible
- Try with/without www prefix
- Ask user if page requires authentication
- If blocked, ask user to paste page content directly
- If the page cannot be fetched at all, continue from provided content and state the limitation in the output

---

## 3. CRO Analysis Framework

Analyze in priority order. Each dimension scored 1-5:

| Score | Meaning |
|-------|---------|
| 5 | Excellent - nothing to fix |
| 4 | Good - minor improvements possible |
| 3 | Adequate - clear room for improvement |
| 2 | Weak - significant issues |
| 1 | Critical - major conversion blocker |

### Dimension 1: Value Proposition Clarity

**The 5-Second Test:** Can a visitor understand WHAT this is and WHY it matters within 5 seconds?

**Check for:**
- [ ] Clear statement of what the product/service does
- [ ] Obvious benefit to the visitor (not just features)
- [ ] Differentiation from alternatives
- [ ] No jargon or insider language
- [ ] Visual clarity - key message not buried

**Red flags:**
- Vague headline ("The future of X")
- Feature-first messaging (vs benefit-first)
- Industry jargon the visitor might not know
- Competing messages fighting for attention
- Value prop below the fold

### Dimension 2: Headline Effectiveness

**The headline is the most important conversion element.** Most visitors decide to stay or leave based on headline alone.

**Check for:**
- [ ] Communicates core value/benefit
- [ ] Specific (not generic)
- [ ] Addresses visitor's problem or desire
- [ ] Creates curiosity or emotional response
- [ ] Matches traffic source expectations (ad copy → landing page message match)

**Headline formulas that work:**
- [Outcome] without [pain point]
- Get [specific result] in [timeframe]
- The [adjective] way to [achieve goal]
- Stop [pain], start [benefit]
- [Number] [audience] use [product] to [outcome]

**Red flags:**
- Company-centric ("We are the leading...")
- Buzzword salad ("AI-powered synergy platform")
- Too clever/abstract (sacrifices clarity for cleverness)
- Mismatched with subhead (should work together)

### Dimension 3: CTA Hierarchy

**One page, one primary action.** Everything else is a distraction.

**Check for:**
- [ ] Single, clear primary CTA
- [ ] CTA copy is value-focused (not "Submit")
- [ ] CTA button stands out visually (contrast, size, whitespace)
- [ ] CTA appears above the fold
- [ ] CTA repeated at logical scroll points
- [ ] Secondary CTAs (if present) are clearly subordinate

**CTA copy patterns that convert:**
- Action + Benefit: "Start saving time"
- Get + Outcome: "Get your free report"
- Reduce friction: "See how it works" > "Request demo"
- First person: "Start my free trial" (sometimes outperforms)

**Red flags:**
- Multiple competing CTAs ("Buy now" AND "Learn more" AND "Contact us")
- Generic copy ("Submit", "Click here", "Learn more")
- CTA buried below fold
- Poor contrast (button blends into page)
- No CTA visible without scrolling

### Dimension 4: Visual Hierarchy

**Visitors scan, they don't read.** Visual hierarchy guides attention to what matters.

**Check for:**
- [ ] F-pattern or Z-pattern alignment
- [ ] Clear information hierarchy (headline > subhead > body > CTA)
- [ ] Sufficient whitespace around key elements
- [ ] Scannable content (short paragraphs, bullets, bold key phrases)
- [ ] Visual cues directing attention to CTA
- [ ] Mobile-friendly layout / mobile readability (if checkable)

**Red flags:**
- Wall of text
- Too many competing visual elements
- CTA doesn't stand out
- Key content below the fold with no scroll cues
- Cluttered, overwhelming design

### Dimension 5: Trust Signals

**Visitors need reasons to trust you.** Especially for cold traffic and high-commitment conversions.

**Check for:**
- [ ] Social client (testimonials, reviews, case studies)
- [ ] Credibility indicators (logos, media mentions, certifications)
- [ ] Specificity in claims (numbers beat vague claims)
- [ ] Security indicators (for payment pages)
- [ ] Contact information / company presence

**Trust signal hierarchy (strongest to weakest):**
1. Specific results ("47% increase in conversions")
2. Named testimonials with photos/titles
3. Logo bar with recognizable brands
4. Review counts / ratings
5. Generic testimonials
6. Certification badges
7. "As seen in" media mentions

**Red flags:**
- No social client whatsoever
- Generic testimonials ("Great product!" - John D.)
- Claims without evidence
- No visible contact/company info
- Looks like a scam (poor design, too many promises)

### Dimension 6: Objection Handling

**Visitors have concerns.** The page should address them before they become reasons to leave.

**Common objections by conversion type:**

| Conversion Type | Common Objections |
|-----------------|-------------------|
| SaaS signup | Is it hard to set up? What if I don't like it? What's the real cost? |
| Demo request | Will they hard-sell me? How long will this take? Is this relevant to me? |
| Purchase | Is this worth the price? What if it doesn't work? Can I return it? |
| Lead gen | Will they spam me? What happens after I submit? |

**Check for:**
- [ ] Addresses price/value concern (if applicable)
- [ ] Addresses "Is this for me?" (audience fit)
- [ ] Addresses difficulty/complexity concerns
- [ ] Addresses risk (guarantees, free trials, easy cancellation)
- [ ] FAQ section covering common questions

**Red flags:**
- No mention of pricing (when it matters)
- No risk reversal (guarantee, trial, refund policy)
- Obvious questions left unanswered
- Assumes too much knowledge about product/process

### Dimension 7: Friction Points

**Every obstacle reduces conversions.** Remove unnecessary friction.

**Check for:**
- [ ] Form length appropriate to offer value (fewer fields = higher conversion)
- [ ] Clear next steps after conversion
- [ ] No unnecessary distractions (navigation on landing pages)
- [ ] Fast page load (perceived) / technical friction, if visible
- [ ] Mobile-friendly experience
- [ ] No broken elements or confusion

**Form optimization:**
- Every field should justify its existence
- First name only > First + Last
- Email only > Email + Phone
- Multi-step forms can outperform long single-step
- Progress indicators reduce abandonment

**Red flags:**
- Too many form fields for the offer
- Required phone number for low-commitment offer
- Unclear what happens after submission
- Distracting navigation or links
- Slow loading elements

---

## 4. Common Issues by Page Type

### SaaS Landing Pages
- Headline focuses on product, not outcome
- Too many features listed (overwhelms)
- No clear single CTA (multiple paths)
- Testimonials from unknown users
- Free trial with credit card = friction

### Lead Generation Pages
- Form asks for too much info upfront
- Lead magnet value not clearly communicated
- No preview of what they'll receive
- "Subscribe to our newsletter" (weak value prop)
- No privacy reassurance

### E-commerce Product Pages
- Key info below the fold (price, CTA)
- Insufficient product photos
- No reviews or social client
- Shipping/returns info hidden
- Size/spec info missing

### Service / Agency Pages
- No specific outcomes or results
- Process is unclear
- Pricing completely hidden
- No case studies with specifics
- CTA is "Contact us" (vague)

---

## 5. Prioritization Standard

For each issue identified, document:

- problem
- evidence (from the page itself)
- impact (High/Medium/Low)
- recommended fix
- implementation effort
- test hypothesis (comprehensive mode)

Priorities must separate high-impact fixes from polish.

---

## 6. Output Structure

### Quick Audit Output

```markdown
## CRO Quick Audit: [Page/URL]
**Date:** [Date]
**Conversion Goal:** [Goal from intake]

### Summary Verdict
[1-2 sentence overall assessment]

### Overall Score: [X]/35
[Sum of 7 dimensions, each scored 1-5]

### Top 5 Priority Fixes

**1. [Issue Name]**
- **Problem:** [What's wrong]
- **Impact:** High/Medium
- **Fix:** [Specific recommendation]

**2. [Issue Name]**
...

### Copy Alternatives

**Current Headline:**
> [Current headline]

**Recommended Alternatives:**
1. [Alternative 1] - *[Why it works]*
2. [Alternative 2] - *[Why it works]*

**Current CTA:**
> [Current CTA text]

**Recommended Alternatives:**
1. [Alternative 1] - *[Why it works]*
2. [Alternative 2] - *[Why it works]*
```

### Comprehensive Audit Output

```markdown
## CRO Comprehensive Audit: [Page/URL]
**Date:** [Date]
**Conversion Goal:** [Goal from intake]
**Target Audience:** [Audience from intake]
**Traffic Sources:** [Sources from intake]

---

### Summary Verdict
[2-3 sentence overall assessment with key insight]

### Overall Score: [X]/35

| Dimension | Score | Status |
|-----------|-------|--------|
| Value Proposition Clarity | X/5 | [Good/Needs Work/Critical] |
| Headline Effectiveness | X/5 | [Good/Needs Work/Critical] |
| CTA Hierarchy | X/5 | [Good/Needs Work/Critical] |
| Visual Hierarchy | X/5 | [Good/Needs Work/Critical] |
| Trust Signals | X/5 | [Good/Needs Work/Critical] |
| Objection Handling | X/5 | [Good/Needs Work/Critical] |
| Friction Points | X/5 | [Good/Needs Work/Critical] |

---

### Detailed Analysis

#### 1. Value Proposition Clarity (X/5)
[Analysis with evidence from page]
- **Issue:** [If any]
- **Recommendation:** [Specific fix]

#### 2. Headline Effectiveness (X/5)
...

[Continue for all 7 dimensions]

---

### Priority Fixes (Ranked by Impact)

| Priority | Issue | Impact | Effort | Fix |
|----------|-------|--------|--------|-----|
| 1 | [Issue] | High | [Low/Med/High] | [Fix] |
| 2 | [Issue] | High | [Low/Med/High] | [Fix] |
...

---

### A/B Test Hypotheses

**Test 1: [Test Name]**
- **Hypothesis:** If we [change], then [metric] will [improve] because [reason]
- **Control:** [Current state]
- **Variant:** [Proposed change]
- **Primary metric:** [What to measure]
- **Expected lift:** [Estimate if possible]

**Test 2: [Test Name]**
...

---

### Copy Alternatives

**Headline Options**

Current:
> [Current headline]

Alternatives:
1. **[Alternative 1]**
   - *Rationale:* [Why this works for the audience/goal]

2. **[Alternative 2]**
   - *Rationale:* [Why this works]

3. **[Alternative 3]**
   - *Rationale:* [Why this works]

**Subheadline Options**

Current:
> [Current subhead]

Alternatives:
1. **[Alternative 1]** - *[Rationale]*
2. **[Alternative 2]** - *[Rationale]*

**CTA Options**

Current:
> [Current CTA]

Alternatives:
1. **[Alternative 1]** - *[Rationale]*
2. **[Alternative 2]** - *[Rationale]*

**client Block / Objection-Handling Rewrites**
[For high-impact trust or objection sections, provide replacement copy]

**Key Section Rewrites**
[If any major body copy needs work, provide alternatives]

---

### Next Steps

1. [Highest priority action]
2. [Second priority action]
3. [Third priority action]
```

### Output Artifact

When auditing pages for an entity, save the audit to `{brain}/content/cro/cro-audit-{slug}-{date}.md`.

Example (`{brain}` = `brains/brand`): `brains/brand/content/cro/cro-audit-homepage-2026-07-02.md`

Ad-hoc audits with no owning entity may be delivered inline as markdown.

---

## 7. Output Format Adjustment

### For Internal Notes
- Use shorthand, abbreviations
- Skip rationale explanations
- Bullet points over prose
- Focus on "what to fix" not "why"
- Can be rough/incomplete

### For Client-Ready
- Full sentences, professional tone
- Include rationale for each recommendation
- Explain the "why" behind issues
- Formatted for easy sharing
- Executive summary at top

---

## 8. Quality Standard

- Recommendations must connect to the stated conversion goal.
- Copy alternatives must be specific, not abstract advice.
- Priorities must separate high-impact fixes from polish.
- Copy alternatives for an entity's own pages should respect that entity's voice profile (`{brain}/voice/`).

---

## 9. Related Skills

| Skill | Purpose |
|-------|---------|
| `seo` | SEO audits with technical + content analysis |
| `writing` | Content creation with voice preservation |
| `document-skills:xlsx` | Excel output for structured deliverables |
| `document-skills:pptx` | Presentation output for client decks |

---

## Execution Checklist

When running this skill:

1. [ ] Ask mode questions (quick vs comprehensive, internal vs client-ready)
2. [ ] Collect context intake (all 5 questions; pre-fill from `{brain}/context/` and `{brain}/strategy/` where possible)
3. [ ] Fetch page via WebFetch (or use provided copy; state the limitation if unfetchable)
4. [ ] Score all 7 CRO dimensions
5. [ ] Identify top issues by impact
6. [ ] Generate copy alternatives for headline + CTA (minimum)
7. [ ] Format output per selected mode
8. [ ] For comprehensive: include test hypotheses
9. [ ] Deliver markdown output; save entity audits to `{brain}/content/cro/`

---

## Quick Actions

Common follow-ups after running this skill:

- "Make this client-ready" → Reformat with full rationale and polish
- "Give me more headline options" → Generate 5-10 additional alternatives
- "Focus on [specific dimension]" → Deep dive on one area
- "Write the test brief for [test]" → Full A/B test documentation
- "Compare to [competitor URL]" → Fetch and compare
