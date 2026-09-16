---
name: geo-citation-network-mapper
description: Map which domains AI engines cite when answering questions in a vertical. Output a citation network table + ranked earned-mention target list so the operator knows *where to go get mentioned* to influence citations.
---

# GEO Citation Network Mapper

Map which domains AI engines cite when answering questions in a vertical. Output a citation network table + ranked earned-mention target list so the operator knows *where to go get mentioned* to influence citations.


Operationalizes the GEO method guide's content heuristics's domain concentration findings (Signal 2) and the GEO method guide's workflow sequence's off-site strategy (Step 5).

**Default scope:** B2B SaaS companies selling to mid-market and enterprise buyers.

## Goal

Identify the domains AI engines cite in a category and prioritize where the brand should earn mentions. Distinguish owned fixes from earned-mention plays.

## When to use

- **New client onboarding** — baseline the vertical's citation network before any optimization work
- **Earned-media / PR planning** — prioritize which publications, communities, and aggregators to pitch
- **Competitive intelligence** — see which domains cite competitors but not you
- **Quarterly refresh** — citation networks shift as AI providers change retrieval
- **Post-tactic validation** — rerun to confirm a specific domain actually increased your citation share after outreach

## Inputs (asked at intake)

| Input | Required? | Source / default |
|---|---|---|
| Vertical / category label | Yes | User |
| Brands CSV (primary + competitors) | Yes | User (or reuse from `geo-share-of-answers`) |
| Client identifier (for output path) | Yes | User |
| **Ingestion mode** — pick ONE: | Yes — **ASK** | See below |
| ↪ Existing SoA `runs.csv` | If mode A | Output from `geo-share-of-answers` |
| ↪ Profound / Peec / ZipTie export | If mode B | User (they already pay for the subscription) |
| ↪ Prompt set for fresh run | If mode C | `geo-prompt-set-builder` output (or hand-built) |
| Top-N earned-mention targets | No | 20 |
| Min citation threshold for network.csv | No | 2 |

## Workflow

Read the full procedure before starting. Paths beginning `tools/` are relative to the AI Marketing OS installation, not the client folder. Resolve them using the installation's `tool_roots` receipt. `{brain}` is the client's context/output directory from its binding. Keep inputs and outputs there; never copy this procedure into the client directory. If a required tool, source, or binding is unavailable, stop and report it.

### 1. Intake + ingestion choice (REQUIRED ASK)

Before running anything, confirm the vertical, brands file, and output path, then **explicitly ask**:

> Citation data source — pick one:
> - **(A) Reuse existing SoA `runs.csv`** — free, instant. Uses citations already captured in a prior `geo-share-of-answers` run.
> - **(B) Import from a citation-tracking tool** — free (already paid via subscription). Supports Profound V1; Peec / ZipTie deferred to V2. Provide the exported CSV.
> - **(C) Fresh run via the GEO suite's run engine** — **paid, costs ~$2–10 depending on prompt count and adaptive sampling.** Uses `run_suite()` from the SoA tool with 3 initial runs/prompt, adaptive sampling up to 15 runs/prompt until 95% Wilson CI half-width ≤ 6pp per entity.

Default to **(A)** if an SoA `runs.csv` exists for this client / vertical. Look in `{brain}/geo/share-of-answers/` — if any dated directory has `runs.csv`, list the dates and ask which to use. If none exist, default to **(C)** and surface the cost estimate.

### 2. Pre-flight cost estimate (mode C only)

The tool prints:
- **Best case** — stops after initial 3 runs/prompt
- **Worst case** — hits the 15-run/prompt cap

Aborts if worst-case exceeds `--max-cost` (default $10). Asks for confirmation unless `--no-confirm` is passed. Mode A / B run instantly with zero API cost.

### 3. Run

The tool:
1. Ingests citations from the chosen source
2. (Mode C only) Runs adaptive sampling — starts at 3 runs/prompt, adds 2 per pass until all tracked entities reach 95% Wilson CI half-width ≤ 6pp, cap 15
3. Extracts each cited URL's domain via `tldextract` (eTLD+1, with subpath preservation for `reddit.com` and `stackexchange.com`)
4. Aggregates to domain level: citation_count, topic_count, prompt_count, surface_count, primary/secondary split
5. Categorizes every domain: rule-based knowledge base (~200 curated domains) → Claude Haiku fallback for unknowns → `unknown` if LLM also fails
6. Writes 3 output files

### 4. Surface the analysis

Read `network_analysis.md` and post inline in chat:
- Top-10 domain concentration % (benchmark vs. the GEO method guide's content heuristics: Education 59.5%, Healthcare 13%)
- Category distribution of citations (publisher / society / UGC / aggregator / vendor / owned / docs / video / encyclopedia / unknown)
- Top-5 earned-mention targets (brief — full list is in `earned_mentions.md`)

Do NOT summarize the gating section — surface the exact warnings so the report discipline survives.

### 5. Recommend actions

For each priority source, define the earned-mention path such as profile update, partner page, contributed content, PR, review generation, or documentation improvement.

## Outputs

### File schemas

**`citation_network.csv`** — one row per domain:
```
domain, category, citation_count, topic_count, prompt_count,
ai_surfaces, primary_citations, secondary_citations,
citation_share_pct, outreach_angle, effort, sample_url
```

**`earned_mentions.md`** — ranked top-N targets table:
- Ranked by **composite score** = citation_share × log1p(topic_count). Volume alone is misleading — a domain cited 100× on one topic is less valuable than one cited 60× across 10 topics.
- Each row includes category, citation share, topic breadth, surface coverage, effort estimate, and templated outreach angle.

**`network_analysis.md`** — network-level report:
- Adaptive sampling report (mode C only) — shows final Wilson CI half-widths per entity
- Domain concentration (top-10 and top-30 share) + vertical benchmark verdict
- Category distribution table
- Gap analysis — top domains where competitors appear but you don't; under-represented categories
- Competitor presence table
- Methodology section + full the GEO method guide's measurement rules / 04 gating warnings

### Storage

- Client / entity work: `{brain}/geo/citation-network/<vertical-slug>_<YYYY-MM-DD>/`
- brand / personal: `brains/brand/geo/citation-network/<vertical-slug>_<YYYY-MM-DD>/`

Mode C also writes a reusable `runs.csv` in the same directory — so a fresh run can be re-ingested later (mode A) without re-hitting APIs.

## Quality Standard

- Do not treat every cited domain as equally actionable.
- Distinguish owned fixes from earned-mention plays.
- Prioritize shopping-intent sources when pipeline impact matters.

## Acceptance criteria for "done"

- [ ] Ingestion source chosen explicitly (A / B / C) and captured in run log
- [ ] (Mode C) Cost preflight shown; user confirmed before paid calls fired
- [ ] (Mode C) Adaptive sampling ran until 95% Wilson CI half-width ≤ 6pp per entity OR cap reached; final CIs reported in `network_analysis.md`
- [ ] `citation_network.csv` has ≥1 row with `category != "unknown"` (rule-based coverage working)
- [ ] `earned_mentions.md` ranks by composite score (share × topic breadth), not raw count
- [ ] `network_analysis.md` includes: concentration metric, category distribution, gap analysis, competitor view, gating section
- [ ] Aggregates across ≥50 prompts × ≥3 runs recommended; small samples flagged as directional
- [ ] ≥80% of domains categorized automatically (rules + LLM); remainder marked `unknown` for manual review
- [ ] Gating warnings from the GEO method guide's measurement rules + 04 included verbatim in `network_analysis.md`

## Implementation notes

### Companion tool: YES — `tools/geo_citation_network.py`

Skill is a thin orchestration layer; the tool handles ingestion, aggregation, categorization, adaptive sampling, and output generation.

### Reuses SoA run engine

Mode C imports `run_suite()` from `tools/geo_share_of_answers.py` — the exact same provider clients, citation parsers, and parallelism model. No duplicated run logic.

### Adaptive sampling — implementation

Sequential sampling based on [Graphite's "Demystifying Randomness in AI"](https://graphite.io/five-percent/demystifying-randomness-in-ai) methodology:
- Each run is a Bernoulli trial for entity visibility
- Pass 1: `--runs-per-prompt` (default 3) runs/prompt/surface
- After each pass, compute 95% Wilson score interval half-width for each tracked entity (primary brand + each competitor)
- If any entity's half-width > `--target-ci-half-width` (default 6.0pp), add `--step-runs` (default 2) more runs/prompt
- Cap at `--max-runs-per-prompt` (default 15). Report actual sample sizes; repeated model responses are not independent observations of the whole market.

### Domain categorization

1. **Owned** — if `raw_domain` matches the primary brand's domain in `brands.csv`
2. **Vendor** — if matches any competitor domain
3. **Rule-based** — curated dict of ~200 known domains (publishers, societies, UGC, aggregators, encyclopedias, docs, video)
4. **Regex fallback** — `.gov`/`.mil`→society, `.edu`→society, `wordpress.com`/`blogspot.com`→ugc, etc.
5. **Optional LLM classification** — off by default. Use `--llm-categorize` only after approving external data transmission and additional API usage; unclassified domains remain `unknown`.
6. **Unknown** — LLM returns none / errors out — flagged for manual review.

The portable stub's role taxonomy (review site, marketplace, analyst or media, documentation, community, partner, competitor-owned, owned site) maps onto these categories; the rule-based knowledge base above is canonical.

### Domain key policy

- Default: eTLD+1 (e.g. `montecarlodata.com`, `medscape.com`)
- Subpath-significant: `reddit.com` and `stackexchange.com` preserve first subpath segment, so `reddit.com/r/cardiology` is distinct from `reddit.com/r/datascience`. These are valid outreach targets at the sub-community level.

### Earned-mention composite score

```
score = (citation_count / total_citations) × (1 + log1p(topic_count))
```

Rewards domains that appear across many topics, not just high raw counts. Owned domains are excluded from the earned list (they're your own). Competitor (vendor) domains stay in the network CSV but rarely rank well as "earned" targets — flagged as "competitive" outreach angle.

When manually re-ranking, the portable stub's prioritization lenses still apply as qualitative overlays: shopping-intent frequency, attainability, competitor presence, and business relevance.

### Authority estimation

Deferred to V2 — no paid SEO tools in V1 (Moz/Ahrefs API hook left open in implementation comments).

### Safe defaults

- `--min-citations 2` in network.csv — drops one-off noise
- Categorization LLM is OFF by default; imported CSV analysis is offline
- Fresh-run cost ceiling at $10 — hard abort above

## CLI cheat sheet

Example — concrete literal paths for an example client `acme` (substitute your `{brain}` paths):

```bash
# Mode A — reuse existing SoA runs (fastest, free)
python3 tools/geo_citation_network.py \
    --from-runs clients/acme/geo/share-of-answers/2026-04-10/runs.csv \
    --prompts-for-topics clients/acme/geo/prompts.csv \
    --brands clients/acme/geo/brands.csv \
    --output clients/acme/geo/citation-network/observability_2026-04-17/ \
    --vertical "data observability"

# Mode B — import from Profound (free, already subscribed)
python3 tools/geo_citation_network.py \
    --from-profound clients/acme/geo/profound-export-2026-04-17.csv \
    --brands clients/acme/geo/brands.csv \
    --output clients/acme/geo/citation-network/observability_2026-04-17/ \
    --vertical "data observability"

# Mode C — fresh run (paid, adaptive sampling)
python3 tools/geo_citation_network.py \
    --prompts clients/acme/geo/prompts.csv \
    --brands clients/acme/geo/brands.csv \
    --output clients/acme/geo/citation-network/observability_2026-04-17/ \
    --vertical "data observability" \
    --runs-per-prompt 3 \
    --max-runs-per-prompt 15 \
    --target-ci-half-width 6.0 \
    --max-cost 10

# Skip LLM categorization (keep it all rule-based + "unknown")
python3 tools/geo_citation_network.py ... --no-llm-categorize

# Restrict surfaces (e.g., if a provider is rate-limited)
python3 tools/geo_citation_network.py ... --surfaces anthropic,google,perplexity
```

## Optional external citation exports

Use only a real, connected provider or a supplied CSV. Inspect its schema and map fields into the documented input format. Do not assume a generic citation MCP exists. Save the source, export date and transformation notes with the run.

## Out of scope (deferred to V2)

- **Authority estimation** (Moz / Ahrefs API) — skip in V1; hook left in code for future integration
- **Peec.ai / ZipTie import parsers** — V1 supports Profound only
- **Native automation provider MCP ingestion** (no manual export step) — V1 goes via Profound-compatible CSV
- **Contact / journalist discovery** — V1 flags `outreach_angle` by category template; actual editor/contact research deferred
- **Sentiment analysis** on whether competitor mentions are positive/negative
- **Live competitive dashboard** — V1 is snapshot reports; dashboard defers until ≥3 weeks of data
- **Auto-outreach** — `/cmo/distribution/publish` handles drafting once a target list is approved

## Risks / open questions

- **Citation extraction accuracy** depends entirely on the upstream source. Mode C relies on `geo-share-of-answers` URL extraction — test with that skill first.
- **English-language domain bias** — international verticals may have different networks. Flag in intake if vertical is non-US.
- **Stale networks** — citation networks shift as AI providers change retrieval. Recommend quarterly refresh, stamped in output filename.
- **Small-sample noise** — aggregating on <50 prompts produces directional data only. Flagged in `network_analysis.md` gating section.

## Adaptation Notes

- Codex can parse runs.csv and produce target CSVs.
- ChatGPT can help plan outreach strategy from the target list.

## References

- [GEO method and measurement limits](../geo-audit/references/method.md). This guide replaces the legacy external framework corpus; it is not necessary to locate a Core checkout.

- Methodology ref: [Graphite — Demystifying Randomness in AI](https://graphite.io/five-percent/demystifying-randomness-in-ai)
- Tool: `tools/geo_citation_network.py`
- Upstream skill (feeds Mode A): `geo-share-of-answers`
- Sibling skill (generates prompts for Mode C): `geo-prompt-set-builder`
- Downstream skill (turns findings into initiatives): `geo-plan`
