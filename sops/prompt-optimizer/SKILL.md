---
name: prompt-optimizer
description: Transform rough prompts into high-performance, model-aware prompts — clear task framing, context, constraints, output shape, and success criteria — optimized for deep research and complex tasks.
---

# Prompt Optimizer

Transform rough prompts into high-performance, model-aware prompts — clear task framing, context, constraints, output shape, and success criteria — optimized for deep research and complex tasks.

> Core skill canon (Phase 4). Merged from .claude/commands/cto/prompt-optimizer.md (rich) + skills-core/skills/cto/prompt-optimizer.md (portable stub) on 2026-07-03.

---

## Step 1: Intake & Classification

When the user provides a rough prompt or describes a desired outcome, ask these targeted questions:

### Required Questions (ask all)

1. **Target model**: Which model will run this prompt?
   - Claude (Opus 4.5 / Sonnet)
   - ChatGPT (GPT-5 Pro / o3)
   - Both (generate two versions)

2. **Output type**: What kind of output do you need?
   - Research report / analysis
   - Strategy document / decision support
   - Code / technical implementation
   - Creative content / writing
   - Operational workflow / checklist

3. **Depth preference**: How comprehensive should the output be?
   - Executive summary (concise, decision-focused)
   - Balanced (moderate detail, actionable)
   - Comprehensive deep-dive (thorough, exhaustive)

### Conditional Questions (ask if relevant)

4. **Success criteria**: What does "done well" look like? (Ask if not obvious from context)

5. **Key constraints**: Any specific requirements? (Ask if complex task)
   - Time sensitivity (recent sources only?)
   - Source requirements (academic, industry, specific publications?)
   - Format requirements (specific structure, length limits?)
   - Audience (technical level, role, decision-maker?)

**Questioning discipline** (portable-stub guidance): when answers are already evident from context, do not re-ask — ask only for missing details that materially change the prompt.

---

## Step 2: Prompt Generation

After gathering inputs, generate the optimized prompt using the appropriate model format.

### For Claude: XML 4-Block Pattern

```xml
<instructions>
You are [ROLE with specific expertise relevant to task].

Behavioral guidance:
- [Key operating principle 1]
- [Key operating principle 2]
- If uncertain about any aspect, explicitly state your uncertainty rather than guessing
- Plan your approach before writing: outline structure, key points, and reasoning first
</instructions>

<context>
Background:
- [What the user is trying to accomplish]
- [Relevant constraints or requirements]
- [What is already known / given]

Assumptions (if inputs were incomplete):
- [Assumption 1]
- [Assumption 2]
</context>

<task>
[Specific deliverable with clear success criteria]

Success looks like:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]
</task>

<output_format>
Structure:
1. [Section 1 name] - [what it contains]
2. [Section 2 name] - [what it contains]
3. [Section 3 name] - [what it contains]

Requirements:
- Length: [specific guidance]
- Tone: [specific guidance]
- [Other format requirements]

Verification checklist (check before submitting):
- [ ] [Verification item 1]
- [ ] [Verification item 2]
</output_format>
```

### For ChatGPT: Signature Block Pattern

```
[Recommended Model]: GPT-5 Pro / [Reasoning mode] with [tools]
[Role]: [Expert persona with specific expertise]
[Scope]: In-scope: [what to cover] | Out-of-scope: [what to exclude]
[Format]: [Sections, structure, output type]
[Depth]: [Fast/Balanced/Thorough]
[Tools]: [Web browsing, Code interpreter, Calculator, None]
[Mode]: [Decision support / Tutor / Research / Critique / Simulator]
[Constraints]: [Length, tone, sources, uncertainty handling, audience]

---

**Task:**
[Clear description of the deliverable]

**Success Criteria:**
- [Criterion 1]
- [Criterion 2]

**Tactic:** Plan before you write. Internally outline steps, structure, and reasoning, then produce only the final answer.

**If inputs are vague or conflicting:** Begin with a "Restated Brief and Working Assumptions" section where you restate the assignment and list assumptions. If you truly cannot proceed, ask up to three specific clarifying questions, then continue.
```

### Other Surfaces (portable-stub additions)

Use the style that fits the target when it is neither of the above:

- **Codex**: repository context, file paths, verification commands, and edit boundaries
- **Model-agnostic**: plain sections with no vendor assumptions

Whatever the surface, the built prompt should include: role or expertise frame, context, task, output format, constraints, quality bar, uncertainty handling, and verification or citation requirements when relevant.

---

## Step 3: Task-Type Overlays

Apply these overlays based on the output type identified in Step 1.

### Research & Analysis Overlay

Add to prompt:
- **Source requirements**: Prefer reputable sources (academic papers, official reports, credible industry publications). Favor recent material for fast-changing domains.
- **Citation style**: Use inline source notes for major claims (e.g., [Source: McKinsey 2025])
- **Time sensitivity handling**: Clearly distinguish structural/slow-changing facts from time-sensitive conditions. Flag speculative or potentially stale information.
- **Scenario analysis**: For forward-looking topics, produce 2-3 scenarios with different assumptions

Required sections for research:
1. Restated brief and assumptions
2. Factor/subtopic map
3. Evidence and analysis by subtopic
4. Integrated view and tradeoffs
5. Actionable takeaways
6. Open questions and uncertainties
7. Key sources
8. Executive summary

### Strategy & Decision Support Overlay

Add to prompt:
- **Decision framing**: What decision does this inform? What are the options?
- **Stakeholder lens**: Who is the decision-maker? What do they care about?
- **Tradeoff analysis**: Explicitly surface tradeoffs between options
- **Recommendation clarity**: Lead with recommendation, then supporting evidence

Required sections:
1. Recommendation (1-3 bullets)
2. Why (evidence/rationale)
3. Alternatives considered
4. Tradeoffs and risks
5. Next steps

### Technical/Code Overlay

Add to prompt:
- **Existing patterns**: Follow existing codebase conventions if specified
- **Error handling**: Include appropriate error handling
- **Testing approach**: Suggest or include test cases
- **Security awareness**: Flag any security considerations

Required sections:
1. Approach/architecture
2. Implementation
3. Edge cases handled
4. Testing notes
5. Caveats/limitations

### Creative/Content Overlay

Add to prompt:
- **Voice/tone**: [Specific voice characteristics]
- **Audience**: [Who is reading this?]
- **Goal**: [What should the reader feel/do/think?]
- **Anti-patterns**: Avoid [specific AI-tells, cliches, or unwanted patterns]

---

## Step 4: Best Practices Checklist

Before presenting the optimized prompt, verify it includes:

### Structure & Clarity
- [ ] Organized in clear blocks (not verbose paragraphs)
- [ ] Role/persona is specific and relevant
- [ ] Task is unambiguous with measurable success criteria
- [ ] Output format is explicitly specified

### Uncertainty & Edge Cases
- [ ] Instructions for handling ambiguity/incomplete inputs
- [ ] "If unsure, say so" instruction included
- [ ] Assumptions section (if any were made)

### Execution Quality
- [ ] Plan-before-write instruction for complex tasks
- [ ] Verification checklist for output quality
- [ ] Constraints tied to audience/purpose (not arbitrary)

### Model-Specific
- [ ] **Claude**: Uses XML tags, 4-block pattern
- [ ] **ChatGPT**: Uses Signature block, includes Tools line

---

## Step 5: Output & Refinement

Present the optimized prompt to the user with:

1. **The optimized prompt** (in a code block for easy copy/paste)
2. **Brief explanation** of key enhancements made
3. **Offer to adjust** based on feedback
4. **Usage notes**: state what inputs the user should replace and what result they should expect

### Sample Response

> Here's your optimized prompt for [Claude/ChatGPT]:
>
> ```
> [The optimized prompt]
> ```
>
> **Key enhancements:**
> - Added explicit success criteria from your [X] goal
> - Included [research/technical/creative] overlay for [task type]
> - Added uncertainty handling instructions
> - Specified [format/structure] aligned with [audience]
>
> Would you like me to adjust the depth, add/remove sections, or modify the tone?

### Output Artifact

Optionally save the optimized prompt to `{brain}/prompts/optimized-{slug}.md`.

---

## Quick Reference: When to Use Each Pattern

| Scenario | Claude Pattern | ChatGPT Pattern |
|----------|----------------|-----------------|
| Deep research | XML 4-block + Research overlay | Signature + Thorough depth + Web |
| Quick analysis | XML 4-block (lean) | Signature + Fast depth |
| Code generation | XML 4-block + Technical overlay | Signature + Code interpreter |
| Strategy memo | XML 4-block + Decision overlay | Signature + Decision support mode |
| Creative writing | XML 4-block + Creative overlay | Signature + appropriate mode |

---

## Examples

### Example Input
> "Help me write a prompt to research the competitive landscape for AI writing tools"

### Example Questions
1. Target model? → "Claude Opus 4.5"
2. Output type? → "Research report"
3. Depth? → "Comprehensive deep-dive"
4. Success criteria? → "Understand top 10 competitors, their positioning, pricing, and differentiation"
5. Constraints? → "Focus on tools launched in last 2 years, include pricing tiers"

### Example Output (Claude)

```xml
<instructions>
You are a market intelligence analyst specializing in B2B SaaS and AI/ML product landscapes.

Behavioral guidance:
- Prioritize accuracy over comprehensiveness—only include claims you can substantiate
- Distinguish between public information and informed speculation
- If uncertain about specific data points (e.g., exact pricing), note the uncertainty
- Plan your research structure before writing: identify categories of analysis, then populate each systematically
</instructions>

<context>
Background:
- The user needs to understand the competitive landscape for AI writing tools
- This is for strategic decision-making (likely product positioning or investment)
- Focus is on tools launched in the last 2 years

Scope:
- In-scope: Top 10 competitors, positioning, pricing, differentiation, target markets
- Out-of-scope: Technical architecture details, employee counts, funding history (unless directly relevant)
</context>

<task>
Produce a comprehensive competitive landscape analysis of AI writing tools.

Success looks like:
- Clear understanding of the top 10 players and how they differentiate
- Pricing transparency across tiers (or acknowledgment where data is unavailable)
- Actionable insights on positioning gaps and opportunities
- Recent enough to reflect 2024-2025 market dynamics
</task>

<output_format>
Structure:
1. Executive Summary (3-5 key insights)
2. Market Overview (size, growth, key trends)
3. Competitor Profiles (top 10, each with: positioning, target market, pricing, key differentiators)
4. Competitive Matrix (table comparing key dimensions)
5. Gap Analysis (underserved segments, positioning opportunities)
6. Open Questions (what couldn't be determined, what requires primary research)
7. Sources

Requirements:
- Length: Comprehensive (2000-3000 words)
- Tone: Analytical, objective, decision-useful
- Include inline source citations for specific claims

Verification checklist:
- [ ] All 10 competitors have consistent data coverage
- [ ] Pricing information is current (or uncertainty noted)
- [ ] Matrix is complete and scannable
- [ ] Insights are actionable, not just descriptive
</output_format>
```

---

## Quality Standard

- The prompt should be specific enough to reduce guessing.
- It should avoid overfitting to one model unless requested.
- Output requirements should be testable or reviewable.

---

## Adaptation Notes

- This skill may intentionally reference model differences, but the prompt body should stay portable when possible.

---

## Relationship to PromptMaster

> Entity note: This section references the entity-specific PromptMaster v3 framework and its GPT-side features; retained as-is from the rich source.

This skill provides a lighter, guided workflow specifically optimized for dual-model output (Claude vs ChatGPT). For more comprehensive prompt orchestration with GPT-specific features (Aulë oversight, advanced routing, mode layering), see the full PromptMaster v3 framework.
