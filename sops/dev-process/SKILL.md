---
name: dev-process
description: 'Development lifecycle orchestrator — the entry point for all development work: route the request through understand, plan, implement, debug, review, and ship stages instead of jumping straight to code, mapping each stage to the right superpower.'
---

# Dev Process — Lifecycle Orchestrator

Development lifecycle orchestrator — the entry point for all development work: route the request through understand, plan, implement, debug, review, and ship stages instead of jumping straight to code, mapping each stage to the right superpower.

> Core skill canon (Phase 4). Merged from .claude/commands/cto/dev-process.md (rich) + skills-core/skills/cto/dev-process.md (portable stub) on 2026-07-03.

Legacy adapter: previously invoked as the `/cto:dev-process` command via `.claude/commands/cto/dev-process.md`; that path is now an adapter, not the canonical mechanism.

You are the entry point for all development work. Your job is to determine what stage of development the user is at and invoke the right superpower.

---

## When To Use

- Any development request where the stage (understand / plan / implement / debug / review / ship) is not already fixed
- Starting fresh dev work — this skill routes before any code is written

## Input / Output Contract

**Inputs:**

- user_request
- repo_context
- current_stage (if already known)

**Outputs:**

- Optional plan or handoff artifact: `{brain}/workflows/dev-plan-{slug}.md`

## The Development Lifecycle

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│ 1. Understand│ ──▶ │ 2. Plan  │ ──▶ │ 3. Implement│
└─────────────┘     └──────────┘     └─────────────┘
                                            │
                                            ▼
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│  6. Ship    │ ◀── │ 5. Review│ ◀── │  4. Debug   │
└─────────────┘     └──────────┘     └─────────────┘
```

## Stage Detection & Routing

Analyze the user's request and current context to determine the stage:

### Stage 1: Understand (Creative / Research)
**Signals:** "build", "create", "add feature", "new", "I want to...", or any creative work — an ambiguous idea, new feature, or unclear problem
**Action:** Invoke `superpowers:brainstorming`
**Why:** Prevents jumping to code before understanding the problem space

### Stage 2: Plan (Design / Architecture)
**Signals:** "implement", brainstorming just completed, spec exists, requirements are clear
**Action:** Invoke `superpowers:writing-plans`
**Why:** Creates bite-sized implementation plan with exact file paths and test design

### Stage 3: Implement (Build / Execute)
**Signals:** Plan exists, ready to code, "execute the plan", "let's build"
**Action:** Choose based on context:
- **Multiple independent tasks?** → Invoke `superpowers:subagent-driven-development`
- **Sequential plan execution?** → Invoke `superpowers:executing-plans`
- **Writing code?** → Invoke `superpowers:test-driven-development` (TDD for each unit)

### Stage 4: Debug (Fix / Investigate)
**Signals:** "bug", "broken", "failing", "error", "not working", test failures, regression
**Action:** Invoke `superpowers:systematic-debugging`
**Why:** Prevents guess-and-check. Forces hypothesis → evidence → fix cycle.

### Stage 5: Review (Validate / QA)
**Signals:** Implementation complete, "I'm done", "ready to review", tests passing
**Action:** Invoke `superpowers:verification-before-completion` first, then `superpowers:requesting-code-review`
**Why:** Verification catches things you missed. Code review catches things verification missed.

### Stage 6: Ship (Integrate / Merge)
**Signals:** Review approved, "ready to merge", "ship it", all checks pass — changes are ready to package, commit, or publish
**Action:** Invoke `superpowers:finishing-a-development-branch`
**Why:** Handles the merge strategy decision (squash, rebase, merge commit)

## Portable Stage Actions (fallback)

When the superpowers skills are unavailable (portable / non-Claude environments), apply the stage directly:

- Understand: clarify goals, constraints, and users
- Plan: define files, steps, risks, and tests
- Implement: make scoped edits and run checks
- Debug: reproduce, isolate, hypothesize, fix, verify
- Review: look for bugs, regressions, and missing tests
- Ship: summarize, package, and hand off cleanly

## How to Use This Skill

1. **Read the user's request**
2. **Identify the stage** using signals above
3. **Announce:** "This is a Stage N ([name]) task. Invoking [superpower]."
4. **Invoke the superpower** using the Skill tool
5. **Follow the superpower's instructions exactly**

If the stage is ambiguous, ask: "Are we starting fresh (understand), or do you already have a plan (implement)?"

## Preserve Boundaries

Respect existing worktree changes, avoid unrelated refactors, and keep validation proportional to risk.

## Record Decisions

For larger work, save the plan or handoff artifact. Optionally save to `{brain}/workflows/dev-plan-{slug}.md`.

## Quick Reference

| Stage | Superpower | One-liner |
|-------|-----------|-----------|
| Understand | `brainstorming` | Define the problem before solving it |
| Plan | `writing-plans` | Design the solution before building it |
| Implement | `executing-plans` / `subagent-driven-development` / `test-driven-development` | Build it right |
| Debug | `systematic-debugging` | Find the root cause, not the symptom |
| Review | `verification-before-completion` → `requesting-code-review` | Prove it works |
| Ship | `finishing-a-development-branch` | Integrate cleanly |

## Quality Standard

- Stage should match the user's real need.
- Implementation should follow plan and verification.
- Debugging should be evidence-led.

## Adaptation Notes

- Codex can apply this directly in repository work.
- ChatGPT can use it as a planning and review rubric.
