---
name: build-workflow
description: Build skills, agents, or hybrid workflows for Claude Code automation — decide the right automation shape, define the contract, implement, and validate.
---

# Build Workflow

Build skills, agents, or hybrid workflows for Claude Code automation — decide the right automation shape, define the contract, implement, and validate.


---

## Step 1: Decide What to Build

Ask one question: **Can I write the steps before I know the answer?**

| If... | Build... |
|-------|----------|
| Steps are the same every time | **Skill** — deterministic instruction set |
| Steps depend on what you discover | **Agent** — autonomous exploration |
| Process is repeatable but some steps need exploration | **Hybrid** — skill orchestrating agents |

### Heuristic Signals

| Signal | Points to... |
|--------|--------------|
| "Generate a [report/doc/asset]" | Skill |
| "Find where X happens" | Agent |
| "Investigate why Y broke" | Agent |
| "Run our standard [process]" | Skill |
| "Audit [complex system]" | Hybrid |
| "Create [N] variations" | Skill |
| "Explore and recommend" | Agent |
| "Coordinate [multiple services]" | Skill (multi-MCP) |
| "Analyze [unknown structure]" | Hybrid |

### Quick Examples

**Skill:** Weekly metrics report
→ Same data sources, same format, same calculations every time.

**Agent:** "Where does authentication happen in this codebase?"
→ Requires exploration; answer shapes the search path.

**Hybrid:** Cross-platform ad account audit
→ Known audit checklist (skill) + platform-specific exploration (agents).

### Choose the Artifact Type

Beyond the skill/agent/hybrid decision, consider the full menu of artifact shapes:

- skill
- script
- MCP server or tool
- ChatGPT Project kit
- custom GPT
- Codex repository workflow
- hybrid orchestration

> Entity note: ChatGPT Project kits, custom GPTs, and Codex repository workflows reflect this entity's multi-platform delivery stack; keep or trim per entity.

---

## Step 2: Design Your Solution

### If Skill → Design for Consistency

Skills are **recipes**: step-by-step instructions that produce consistent results.

**Design checklist:**
- [ ] Can someone follow these steps without AI judgment?
- [ ] Are inputs clearly defined?
- [ ] Are outputs predictable and verifiable?
- [ ] Does every run produce the same structure?

**Categories:**

| Category | Use When | Examples |
|----------|----------|----------|
| **Document & Asset Creation** | Creating consistent, high-quality output | docx, pptx, pdf, frontend-design |
| **Workflow Automation** | Multi-step processes needing consistent methodology | sprint-planning, code-review |
| **MCP Enhancement** | Adding workflow guidance on top of MCP tools | notion-project-setup, calendar-sync |

**MCP + Skills ("kitchen analogy"):**
- MCP = the professional kitchen (tools, ingredients, equipment)
- Skills = the recipes (step-by-step instructions on how to create value)

---

### If Agent → Design for Exploration

Agents are **investigators**: autonomous actors that adapt to what they discover.

**Design checklist:**
- [ ] Is the goal clearly defined?
- [ ] What does "done" look like?
- [ ] What should the agent return?
- [ ] What boundaries should it respect?

**Agent definition template:**
```
Goal: [What you want to know or accomplish]
Context: [What the agent needs to understand]
Return: [Structure of expected output]
Boundaries: [What NOT to do, scope limits]
```

**Example — Codebase exploration:**
```
Goal: Find all files involved in user authentication
Context: This is a Node.js backend with Express
Return: List of files with brief role descriptions
Boundaries: Don't modify any files; focus on auth, not authorization
```

---

### If Hybrid → Design for Orchestration

Hybrids are **conductors**: skills that delegate exploratory work to agents.

**Design checklist:**
- [ ] Which steps are deterministic? (Keep in skill)
- [ ] Which steps require discovery? (Delegate to agent)
- [ ] How do agent results flow back to the skill?
- [ ] What does the skill do with those results?

**Hybrid pattern:**
```
Skill Step 1: Collect inputs, validate
Skill Step 2: Delegate exploration → Agent(s)
Skill Step 3: Synthesize agent outputs
Skill Step 4: Generate final deliverable
```

**Example — Ad account audit:**
```
1. (Skill) Collect account access, identify platforms
2. (Agent) Spawn audit-google, audit-meta, audit-linkedin in parallel
3. (Skill) Combine findings into unified health score
4. (Skill) Generate executive summary + recommendations
```

---

### Define the Contract

Whatever shape you choose, document the contract before implementing:

- inputs
- outputs
- required tools
- success criteria
- failure modes
- validation method
- sharing surface

---

## Step 3: Implement

### Implementation Patterns

Choose the pattern(s) that fit your workflow:

**1. Sequential Orchestration** — Multi-step processes in specific order
```
Step 1: Create account → Step 2: Setup payment → Step 3: Create subscription
```

**2. Multi-MCP Coordination** — Workflows spanning multiple services
```
Phase 1: Export from Figma → Phase 2: Upload to Drive → Phase 3: Create Linear tasks
```

**3. Iterative Refinement** — Output improves with iteration
```
Draft → Validate → Refine → Re-validate → Finalize
```

**4. Context-Aware Selection** — Same outcome, different tools based on context
```
Large files → cloud storage | Collaborative docs → Notion | Code → GitHub
```

**5. Domain-Specific Intelligence** — Specialized knowledge beyond tool access
```
Check compliance rules → Process if passed → Log audit trail
```

**6. Agent Delegation** — Skill orchestrates exploratory work
```
Collect inputs (skill) → Delegate analysis (agents) → Synthesize (skill)
```

**7. Parallel Agent Dispatch** — Multiple agents run concurrently
```
Spawn audit-google | audit-meta | audit-creative → Combine findings
```

**8. Pure Agent** — When skill is wrong choice entirely
```
Goal defined → Agent explores autonomously → Returns findings
```

---

### Break the Build Into Parts

Design the implementation as:

- reusable instructions
- deterministic code
- adapter glue
- tests or checks
- teammate setup notes

---

### Skill Implementation

**File structure:**
```yaml
---
name: skill-name-in-kebab-case
description: What it does. Use when [specific triggers].
---

# Skill Name

[One-line summary]

## Step 1: [First Action]
[Clear instructions]

## Step 2: [Second Action]
[Clear instructions]

## Output
[What gets produced and where]
```

**YAML reference:**

Required:
```yaml
name: skill-name-in-kebab-case
description: What it does. Use when [specific triggers].
```

Optional (for distribution):
```yaml
license: MIT
compatibility: Requires Python 3.9+, network access
metadata:
  author: Your Name
  version: 1.0.0
  mcp-server: server-name
```

**Output location:** `sops/<skill-name>/SKILL.md` (canon). `.claude/commands/<skill-name>.md` remains the legacy executable adapter until Phase 5.

---

### Agent Implementation

Invoke agents using the Task tool:

```markdown
## Step N: [Exploratory Step]

Use the Task tool:
- **subagent_type:** Explore | Plan | general-purpose
- **prompt:** [Goal + context + what to return]
```

**Available agent types:**

| Type | Use For |
|------|---------|
| `Explore` | Finding files, searching code, answering codebase questions |
| `Plan` | Designing implementation strategies |
| `general-purpose` | Research, multi-step tasks, complex searches |
| `Bash` | Git operations, command execution |

**Example — Delegating codebase exploration:**
```markdown
## Step 2: Identify Authentication Files

Use the Task tool:
- **subagent_type:** Explore
- **prompt:** Find all files related to user authentication in this codebase. Return a list of file paths with a one-line description of each file's role in the auth flow.
```

---

### Hybrid Implementation

Combine skill structure with agent delegation:

```markdown
---
name: cross-platform-audit
description: Audit ad accounts across Google, Meta, and LinkedIn. Use when reviewing multi-platform ad performance.
---

# Cross-Platform Ad Audit

Comprehensive audit across advertising platforms.

## Step 1: Identify Platforms

Ask the user which platforms to audit:
- Google Ads
- Meta Ads
- LinkedIn Ads

## Step 2: Run Platform Audits (parallel agents)

For each selected platform, use the Task tool:

**Google Ads:**
- subagent_type: audit-google
- prompt: Run the Google Ads audit checklist. Return findings in the standard scoring format.

**Meta Ads:**
- subagent_type: audit-meta
- prompt: Run the Meta Ads audit checklist. Return findings in the standard scoring format.

**LinkedIn Ads:**
- subagent_type: audit-linkedin
- prompt: Run the LinkedIn Ads audit checklist. Return findings in the standard scoring format.

## Step 3: Synthesize Results

Combine agent outputs:
1. Calculate aggregate health score
2. Identify cross-platform issues
3. Prioritize recommendations by impact

## Step 4: Generate Deliverable

Create executive summary with:
- Overall health score
- Platform-by-platform breakdown
- Top 5 recommendations
- Implementation roadmap
```

---

## Step 3.5: Validate Skill Quality (Skills Only)

For skills that will be used frequently or enforce discipline, validate quality using **superpowers:writing-skills**:

### When to Use Full Validation

| Skill Type | Validation Level |
|------------|------------------|
| Discipline-enforcing (TDD, verification, debugging) | **Full** — pressure testing, rationalization tables |
| Frequently-used (reports, asset creation) | **Standard** — baseline test, CSO check |
| One-off utilities, simple references | **Skip** — functional test only |

### Full Validation Checklist

1. **Baseline test:** Run the scenario WITHOUT the skill. Document what breaks.
2. **Write minimal skill:** Address only the failures you observed.
3. **Verify compliance:** Run WITH skill. Agent should now follow it.
4. **Pressure test:** Add time pressure, sunk cost, authority pressure.
5. **Build rationalization table:** Document excuses, add explicit counters.
6. **CSO check:** Description says "Use when..." not "This skill does..."

### Standard Validation Checklist

1. **Baseline test:** Quick run without skill to verify it's needed.
2. **Functional test:** Run with skill, confirm expected output.
3. **CSO check:** Verify description triggers correctly.

**Reference:** For full methodology, invoke `superpowers:writing-skills`.

---

## Step 4: Functional Test

> **Note:** This step covers basic functional testing. For quality validation (baseline testing, pressure scenarios, rationalization tables), see Step 3.5.

### Triggering Tests
```
Should trigger:
- "Help me [exact phrase users would say]"
- "[Paraphrased version of request]"

Should NOT trigger:
- "[Unrelated request that sounds similar]"
- "[Request handled by different skill]"
```

### Functional Tests
- [ ] Valid outputs generated
- [ ] Scripts execute without errors (if applicable)
- [ ] Agent delegations return expected structure
- [ ] Edge cases handled
- [ ] Error messages are helpful

### For Hybrids
- [ ] Agent results correctly flow to synthesis step
- [ ] Parallel agents complete before synthesis begins
- [ ] Missing agent results handled gracefully

### Performance Comparison
Document before/after:
- Messages needed to complete task
- Token consumption
- Failed attempts requiring retry

---

## Step 5: Self-Improvement Loop

When skills or tools fail in production:

1. **Identify** what broke (exact failure, not symptoms)
2. **Fix** the tool or skill
3. **Verify** the fix works with the original scenario
4. **Update** the skill if you discovered new edge cases
5. **Document** what you learned (add to Common Mistakes or Troubleshooting)

**The goal:** Every failure makes the system stronger. Don't just fix — improve.

---

## Output Artifact

When this skill is used to spec a new workflow (rather than implement one directly), save the workflow spec to `{brain}/workflows/{slug}-workflow-spec.md`.

Provide the smallest implementation plan that gets the workflow usable.

---

## Quality Standard

- Use a script when deterministic reliability matters.
- Use a skill when procedural judgment matters.
- Use an agentic pattern only when discovery changes the path.

---

## Adaptation Notes

> Entity note: platform-fit guidance below reflects this entity's tool stack.

- Codex is well suited for implementing scripts, tests, and repo-native skills.
- ChatGPT is well suited for collaborative workflow design and nontechnical teammate onboarding.

---

## Troubleshooting

### Skill Won't Upload
| Error | Cause | Fix |
|-------|-------|-----|
| "Could not find SKILL.md" | Wrong filename | Must be exactly `SKILL.md` (case-sensitive) |
| "Invalid frontmatter" | YAML formatting | Check `---` delimiters, closed quotes |
| "Invalid skill name" | Spaces or capitals | Use `kebab-case` only |

### Skill Doesn't Trigger
- Description too vague → Add specific trigger phrases
- Missing file types → Mention `.docx`, `.pdf`, etc. if relevant
- Debug: Ask Claude "When would you use the [skill-name] skill?"

### Skill Triggers Too Often
- Add negative triggers: "Do NOT use for [specific case]"
- Be more specific about scope
- Clarify relationship to other skills

### Instructions Not Followed
- Too verbose → Use bullets and numbered lists
- Critical steps buried → Move to top with `## Important` header
- Ambiguous → Replace "validate properly" with explicit checklist

### Anti-Patterns

**Signs you built the wrong thing:**

| Symptom | Problem | Fix |
|---------|---------|-----|
| Skill has "investigate" or "explore" steps | Trying to be deterministic about discovery | Delegate those steps to agents |
| Agent does the same steps every time | Wasting exploration overhead | Convert to skill |
| Skill has many if/else branches | Logic too complex for static instructions | Consider agent or hybrid |
| Agent keeps asking for clarification | Goals not clear enough | Refine goal definition or use skill |
| Hybrid agents return unusable data | No structure specified | Add explicit return format to prompts |

**The wrong abstraction costs more than no abstraction.**

If you're fighting the pattern, you probably chose wrong. Revisit Step 1.

---

## Quick Reference

### When to use each

| Build a... | When... |
|------------|---------|
| Skill | Same steps, predictable output |
| Agent | Discovery-driven, adapts to findings |
| Hybrid | Repeatable process with exploratory phases |

### File locations

- Skills (canon): `sops/<skill-name>/SKILL.md` — `.claude/commands/<skill-name>.md` is the legacy executable adapter until Phase 5
- Agent definitions: Within skills or inline Task tool calls
- Outputs: Per skill specification (usually `.tmp/` or cloud services); workflow specs go to `{brain}/workflows/{slug}-workflow-spec.md`

### Task tool parameters

```
subagent_type: Explore | Plan | general-purpose | Bash | [custom]
prompt: [Goal + context + expected return format]
description: [3-5 word summary]
model: sonnet | opus | haiku (optional)
run_in_background: true | false (optional)
```
