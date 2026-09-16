---
name: geo-content-restructure
description: Rewrite a single page (URL or local markdown) into a citation-ready, structured-briefing format — front-loaded answer, Q&A H2s, entity richness, definitive language, chunk independence — while preserving voice, named entities, numbers, and factual accuracy.
---

# GEO Content Restructure

Rewrite a single page (URL or local markdown) into a citation-ready, structured-briefing format — front-loaded answer, Q&A H2s, entity richness, definitive language, chunk independence — while preserving voice, named entities, numbers, and factual accuracy.



Operationalizes the GEO method guide's content heuristics's citation mechanics and the GEO method guide's workflow sequence's Step 4 (content structure for citation). Uses the sibling core skill `geo-audit` for pre/post scoring so the rubric is consistent across the suite.

**Goal (portable statement):** make an existing page easier for AI engines to cite while preserving the original facts, intent, and brand voice.

**Default scope:** B2B SaaS companies selling to mid-market and enterprise buyers. Also works for regulated verticals (medical / legal / financial) — the skill auto-detects YMYL content and raises a hard pause before any claim is rewritten.

**This is the most complex skill in the suite.** Go slow. Never execute a rewrite without operator approval at the checkpoint. Never add facts that are not in the source.

## When to use

- Restructuring top 10–100 pages on an entity site (run page by page; batch via shell loop)
- Single-page rework — e.g., a key landing page underperforming on the GEO method guide's content heuristics signals
- Templating a new content format — rewrite one exemplar, then humans replicate the pattern
- Treated-vs-control experiments — rewrite a subset, leave the rest untouched, measure citation lift after 4+ weeks

## Inputs (asked at intake)

| Input | Required? | Source / default |
|---|---|---|
| Source (URL or local `.md` / `.html` path) | Yes | User |
| Entity identifier (for output path) | Yes | User |
| Voice profile path | Yes | `{brain}/voice/voice-synthesis.md` (entity default) or a page/campaign-specific override under `{brain}/voice/` |
| Target persona | No | Inherits from voice profile |
| Preserve sections | No | User flags any section that must NOT be changed (legal disclaimer, regulatory copy, schema markup, etc.) |
| Length budget | No | ≤120% of source word count (soft); 150% hard fail; 50% floor |
| Constraints | No | Regulatory rules, brand do/don't, compliance language |

Also useful at intake (from the portable stub): prior `geo-audit` findings and the target prompts or queries the page should win.

## Workflow

Read the full procedure before starting. Paths beginning `tools/` are relative to the AI Marketing OS installation, not the client folder. Resolve them using the installation's `tool_roots` receipt. `{brain}` is the client's context/output directory from its binding. Keep inputs and outputs there; never copy this procedure into the client directory. If a required tool, source, or binding is unavailable, stop and report it.

### Stage 0 — Intake + source load

- [ ] 1. Confirm: source, entity, voice profile path, any preserve sections
- [ ] 2. Load source via `geo_restructure_diff.py load_source()` semantics — URL fetched, local file read; content extracted to clean text
- [ ] 3. Set the output directory: `.tmp/geo/content-restructure/<slug>/` for working files

### Stage 1 — Pre-audit + fact extraction + YMYL gate

Run all three in parallel — they are independent, and the operator sees them together.

```bash
# Pre-audit (uses geo-audit's rubric — no re-implementation)
python3 tools/geo_audit.py --url <source-url> --output .tmp/geo/content-restructure/<slug>/pre-audit/

# Facts: numbers, entities, quoted claims the rewrite must preserve
python3 tools/geo_restructure_diff.py extract-facts \
    --source <source> --output .tmp/geo/content-restructure/<slug>/

# YMYL classification — exit 10 if medical / legal / financial
python3 tools/geo_restructure_diff.py detect-ymyl \
    --source <source> --output .tmp/geo/content-restructure/<slug>/
```

**YMYL gate (HARD PAUSE):** if `detect-ymyl` exits 10, stop and say in chat:

> This content is flagged as YMYL — top category: `<medical|legal|financial>` at `X%` term density. Restructure will rearrange existing claims but **not add, modify, or soften any clinical / legal / financial claim**. Confirm before proceeding. If any claim needs to change, that is a content edit, not a restructure — route to the subject-matter expert first.

Wait for explicit confirmation before changing regulated claims or proceeding through this checkpoint.

### Stage 2 — Voice load

Read the voice profile at the path from intake. Extract:
- Hard-no anti-patterns (always enforced)
- Voice-specific DOs/DON'Ts (may be the entity operator's personal-voice audit DOs or an entity style guide)
- Sample passages from the source itself — these reveal the original voice's actual register, sentence length, and technical tone, which must survive the restructure


Also read [Writing](../writing/SKILL.md) for source-faithfulness and the selected client's voice rules. Apply that client's approved profile, not another author's stylistic habits.

### Stage 3 — Identify the implied page question

Extract the source's H1 and intro (first 150 words). What single question is this page trying to answer? Write it as a literal user query.

If the source serves multiple distinct questions, pick the primary one (highest-value intent — usually the shopping-intent variant). Flag the others for a separate page; do not try to fix multi-intent bloat in the rewrite itself.

**Structural diagnosis checklist (from portable stub)** — while identifying the question, look for:

- weak opening answer
- missing direct definitions
- unclear headings
- buried client
- missing FAQ or comparison sections
- lack of sourceable claims

### Stage 4 — Generate the restructure plan

Draft a structured plan document. Do not write any section copy yet except the first-150-word front-load preview.

**Plan must include:**

1. **Pre-audit scorecard** — copy from `pre-audit/*.md`
2. **Implied page question** — the literal user query
3. **Proposed new H1** — definitive form (not question form for H1)
4. **Proposed H2 set** — `old → new` mapping table. Target ≥60% of H2s in question form per the GEO method guide's content heuristics Signal 2
5. **Draft first 150 words** — the front-loaded answer. This is the only copy drafted at plan stage; it shows how the voice will land
6. **Section-by-section transformation plan** — for each source section, note: keep as-is / rewrite opener for definitiveness / merge with X / split / delete / new section. One-liner per section
7. **Length budget projection** — current word count vs target (≤120%)
8. **Entities + numbers table** — everything `extract-facts` pulled. Mark any that will be dropped with explicit rationale (e.g., "drop '2017 — background context no longer relevant; no replacement claim")
9. **Preserve-flagged sections** — quote them verbatim and mark "UNCHANGED"
10. **YMYL flag** — if set, repeat the clinical-accuracy constraint

### Stage 5 — Checkpoint (GATE — NON-NEGOTIABLE)

Post the plan in chat. Wait for the operator's explicit response:
- **"go"** / **"approved"** → execute
- **"change X"** → revise plan, repost, wait again
- **"stop"** → write plan to `<slug>_plan.md` and exit cleanly

Do NOT proceed to execution without explicit approval. The rewrite burns cycles — a bad plan reviewed at this gate saves more than a bad rewrite caught at post-audit.

### Stage 6 — Execute the rewrite

Write the rewrite as `<slug>_restructured.md`. Rules:

**Structural:**
- H1 in definitive form
- ≥60% of H2s in question form (target 100% where natural)
- First 30% of content answers the implied question directly (definitional "X is Y" pattern)
- Each H2 section is self-contained — remove "as mentioned above", "this", "these" cross-refs
- Front-load each paragraph: high-info sentence in the middle or early, not buried
- Where useful (from portable stub): concise definitions, comparison tables, summary boxes, and next-step CTAs — structure-only additions; they must be built from claims already in the source, never new facts

**Claims and facts:**
- Preserve every entity from the facts list (case-insensitive substring match counts)
- Preserve every number from the facts list verbatim (`44.2%` stays `44.2%`, not "about 44%")
- Do NOT introduce any new number. If a claim needs quantification, leave it unquantified
- For YMYL content: do NOT modify any clinical / legal / financial claim. Restructure the prose *around* the claim; the claim itself is inviolable
- Preserve-flagged sections go in unchanged

**Voice:**
- Apply the selected client's voice constraints and preserve the source's meaning.
- No filler phrases ("when it comes to", "in today's landscape", "it's important to note")
- No perfectly parallel bullet lists
- No rhetorical-question chains after em-dashes
- Match the source's register — a clinical page stays clinical; a marketing page keeps its energy

**Length:**
- Target ≤120% of source word count
- If running long during execution, tighten in real time — do not emit over the soft ceiling and ask later
- Hard fail at 150% — if the rewrite needs that much, the plan was wrong; back up

**Inline change markers** — use `<!-- REWRITTEN: <short note> -->` ONLY for structural or claim-level changes:
- New or substantially reworded H2
- Section-level restructures (merges, splits, reorders)
- Section deletions (marker at the previous heading boundary)
- Any passage where a claim's phrasing changed, even if the fact stayed the same

Do NOT mark sentence-level cosmetic edits inline (hedging → definitive, filler removal, readability polish). Those go in `<slug>_changes.md` only.

### Stage 7 — Post-audit + validation report

```bash
python3 tools/geo_restructure_diff.py diff-report \
    --source <source> \
    --rewrite .tmp/geo/content-restructure/<slug>/<slug>_restructured.md \
    --output .tmp/geo/content-restructure/<slug>/
```

This writes `<slug>_audit_diff.md` with:
- Verdict (PASS / PASS WITH CAVEATS / BELOW TARGET / FAIL)
- Pre/post overall scores + per-signal delta table
- Length-budget status
- Number preservation — dropped and **added** (added = potential hallucination)
- Entity preservation rate
- Quoted claims from source (for manual paraphrase-drift check)
- YMYL status
- Voice markers diff (em-dashes, hedging, filler, parentheticals, sentence-starter variety, avg sentence length)
- Section mapping (source H2 → rewrite H2 with word overlap)

Tool exit codes:
- **0** — Heuristic PASS (net ≥+15, no regressions, no added numbers, length in budget)
- **1** — BELOW TARGET (net <+15 or has signal regressions) — revise before shipping
- **2** — FAIL (added numbers = potential hallucination, or length out of hard bounds) — stop and fix

### Stage 8 — Voice gate (before declaring done)

Compare the rewrite against the selected voice profile and approved examples. Check sentence rhythm, technical register, point of view, and the strength of claims. Preserve useful uncertainty: never change “might” to “is” merely to sound more definitive.

- Remove filler and unsupported teaser claims.
- Use the client's punctuation and formatting preferences; there is no universal quota for parentheticals, named frameworks, or question headings.
- Compare original and rewrite passages side by side. Explain material voice drift and correct it before delivery.
- Treat automated voice counts and score changes as review aids, not substitutes for reading.
- Report fact preservation, locked-section preservation, and voice consistency separately.

### Stage 9 — Write changes rationale

Write `<slug>_changes.md`:
- Section-by-section: what changed, why (cite the GEO method guide's content heuristics principle), what was preserved
- Voice-preservation notes
- Open questions flagged for human reviewer (e.g., "I changed 'might' to 'is' in paragraph 3 — verify clinical accuracy")
- Explicit list of anything from the facts table that was dropped and why

### Stage 10 — Surface summary in chat

Post inline:

> **Restructure complete — `<slug>`**
>
> - **Audit:** pre `X`/100 → post `Y`/100 (**net +Z**)
> - **Regressions:** `<list or "none">`
> - **Preservation:** `E`% entities, `N` numbers dropped, **`A` numbers added (hallucination check required if >0)**
> - **Length:** `W` words (`R`x of source)
> - **Voice gate:** `<pass/fail + short detail>`
> - **YMYL:** `<flagged + category | not flagged>`
>
> **Files:**
> - `<slug>_restructured.md` — rewrite ready for review
> - `<slug>_audit_diff.md` — validation report
> - `<slug>_changes.md` — section-by-section rationale
>
> **Next:** operator reviews rewrite. If approved, move to `{brain}/geo/restructured/<slug>.md` or the entity's CMS. Do NOT auto-publish.

## Output

### Files produced

| File | Purpose |
|---|---|
| `pre-audit/<slug>_audit.md` | Baseline the GEO method guide's content heuristics scorecard |
| `facts.json` | Numbers, entities, quoted claims from source (preservation target) |
| `ymyl_report.json` | YMYL classification output |
| `<slug>_plan.md` | Restructure plan (written at checkpoint; archived whether approved or not) |
| `<slug>_restructured.md` | The rewrite, ready for CMS paste after review |
| `<slug>_audit_diff.md` | Pre/post scorecard + preservation + voice + length + section mapping |
| `<slug>_changes.md` | Section-by-section rationale + open questions for reviewer |

### Storage

- Working files: `.tmp/geo/content-restructure/<slug>/` (disposable)
- Approved rewrite → operator moves to `{brain}/geo/restructured/<slug>.md` (with `{slug}-diff.md` and `{slug}-changes.md` alongside) or the entity's CMS

## Acceptance criteria for "done"

- [ ] Pre-audit run and baseline scorecard saved
- [ ] Facts extracted (numbers + entities + quoted claims) and shown at checkpoint
- [ ] YMYL gate triggered for medical/legal/financial content with explicit operator confirmation before execution
- [ ] Restructure plan posted; operator-approved before execution (no silent execution)
- [ ] Post-audit and any score shortfall are reported; do not distort accurate content to force a 15-point improvement
- [ ] No signal regresses post-rewrite (any regression flagged in chat)
- [ ] Zero added numbers in rewrite (or every addition explicitly justified and acknowledged by operator)
- [ ] Entity preservation rate ≥90% (or dropped entities explicitly justified)
- [ ] Length within budget (50% floor, 120% soft ceiling, 150% hard fail)
- [ ] Voice gate passes — universal AI-tells (always) + voice-specific (conditional on profile)
- [ ] First 30% of rewrite directly answers the implied page question
- [ ] Headings match reader intent; question format is used where natural
- [ ] Preserve-flagged sections are unchanged (byte-for-byte)
- [ ] SEO signals preserved — canonical tags, internal links, schema markup documented in changes.md for the CMS paste step (the rewrite is markdown; the CMS render must re-apply these)
- [ ] All outputs in the right directories

## Quality Standard

- Preserve facts and voice.
- Improve extractability without keyword stuffing.
- Document changes clearly for reviewer trust.

## CLI cheat sheet

```bash
# Stage 1: pre-audit
python3 tools/geo_audit.py --url https://example.com/page --output .tmp/geo/content-restructure/slug/pre-audit/

# Stage 1: facts
python3 tools/geo_restructure_diff.py extract-facts \
    --source https://example.com/page \
    --output .tmp/geo/content-restructure/slug/

# Stage 1: YMYL gate (exit 10 = YMYL detected)
python3 tools/geo_restructure_diff.py detect-ymyl \
    --source https://example.com/page \
    --output .tmp/geo/content-restructure/slug/

# Stage 7: post-audit + preservation + voice + length + section map
python3 tools/geo_restructure_diff.py diff-report \
    --source https://example.com/page \
    --rewrite .tmp/geo/content-restructure/slug/slug_restructured.md \
    --output .tmp/geo/content-restructure/slug/

# Local markdown input (also supported) — example with a concrete legacy client path
python3 tools/geo_restructure_diff.py extract-facts \
    --source clients/acme/content/old-page.md \
    --output .tmp/geo/content-restructure/old-page/
```

## Out of scope (deferred to V2)

- **Auto-publishing to CMS** — V1 ends with a markdown draft for human review; publishing is a separate workflow
- **Multi-page batch restructure** — V1 is one page at a time; batch via shell loop if needed. A dedicated batch mode is V2
- **A/B variant generation** — V2 (generate 2-3 rewrites for split testing)
- **Image / asset suggestions** — V2 (e.g., "add a diagram of X here for chunk independence")
- **Translation / localization** — V2
- **Schema markup generation** — V2; V1 documents existing schema in changes.md for manual re-application
- **Automated voice-profile loader** — V1 reads a single file path; a registry that auto-picks the right profile for an entity is V2
- **SEO signal re-application to the rewrite** — V1 produces markdown; canonical / internal links / schema must be re-applied by the CMS step

## Risks + operating notes

- **Voice drift is the #1 risk.** The structured-briefing format can sound robotic if applied mechanically. Voice gate is the primary defense; operator checkpoint is the secondary
- **Clinical / factual hallucination.** For YMYL content, the hard rule is: restructure prose around claims; never modify claims themselves. The number-preservation check catches most of this; paraphrase-drift on quoted claims is the operator's last-mile review
- **SEO regression.** Markdown drafts don't carry canonical tags or internal links. The CMS paste step must re-apply these — `changes.md` enumerates what was on the source so nothing drops
- **Over-fitting to AI.** Pages restructured for AI can feel weird to humans. Read the rewrite out loud at least once before approval
- **Entity drop on short-word matches.** The preservation check does case-insensitive substring + head-fallback. If you see a dropped entity that's actually preserved (e.g., "Honeycomb Inc." → "Honeycomb"), it's a false positive — verify manually, don't rewrite to satisfy the tool

## Adaptation Notes

- Codex is well suited to file-based rewrites and diff generation.
- ChatGPT can help review tone and stakeholder-friendly rationale.

## References

- [GEO method and measurement limits](../geo-audit/references/method.md). This guide replaces the legacy external framework corpus; it is not necessary to locate a Core checkout.

- `{brain}/voice/voice-synthesis.md` — the entity operator's personal voice profile
- [Writing](../writing/SKILL.md) — source-faithful drafting and client voice review.
- `tools/geo_audit.py` — pre/post scoring engine (`audit_url`, `audit_html`)
- `tools/geo_restructure_diff.py` — facts extraction, YMYL gate, diff-report
- Upstream: `geo-audit` — uses the same the GEO method guide's content heuristics rubric
- Downstream: `geo-share-of-answers` rerun 4+ weeks after publish to measure citation lift (the GEO method guide's workflow sequence Step 7)
