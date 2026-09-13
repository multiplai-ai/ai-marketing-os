---
name: ads
description: 'Comprehensive paid advertising audit and optimization for any business type: routes paid media requests to the right workflow, then runs full multi-platform audits (Google, Meta, LinkedIn, TikTok, Microsoft), platform deep dives, conversion tracking health checks, creative quality assessment, budget allocation optimization, bidding strategy evaluation, and compliance verification.'
---

# Ads — Multi-Platform Paid Advertising Audit & Optimization

Comprehensive paid advertising audit and optimization for any business type: routes paid media requests to the right workflow, then runs full multi-platform audits (Google, Meta, LinkedIn, TikTok, Microsoft), platform deep dives, conversion tracking health checks, creative quality assessment, budget allocation optimization, bidding strategy evaluation, and compliance verification.


Legacy adapter: previously invoked as the `/ads` command via `.claude/commands/cmo/distribution/ads/ads/SKILL.md`; that path is now an adapter, not the canonical mechanism.

Orchestrates 12 specialized sub-skills and 6 subagents. Industry detection for SaaS, e-commerce, local service, B2B enterprise, info products, mobile app, real estate, healthcare, finance, and agency.

Triggers on: "ads", "PPC", "paid advertising", "Google Ads", "Meta Ads", "Facebook Ads", "LinkedIn Ads", "TikTok Ads", "Microsoft Ads", "Bing Ads", "ad audit", "campaign audit", "ROAS", "conversion tracking", "creative fatigue", "bid strategy".

---

## When To Use

- Starting a paid media audit
- Choosing between a full audit, a platform deep dive, creative review, landing page review, budget review, competitor scan, or strategic plan
- Triaging a vague ads performance question

## Input / Output Contract

**Inputs:**

- business_context
- active_platforms
- ad_account_exports
- campaign_goal

**Outputs:**

- Routing note (optional): `{brain}/ads/ads-router-{date}.md`
- Audit reports and action plans per the invoked sub-skill

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/ads audit` | Full multi-platform audit with parallel subagent delegation |
| `/ads google` | Google Ads deep analysis (Search, PMax, YouTube) |
| `/ads meta` | Meta Ads deep analysis (FB, IG, Advantage+) |
| `/ads youtube` | YouTube Ads specific analysis |
| `/ads linkedin` | LinkedIn Ads deep analysis (B2B, Lead Gen) |
| `/ads tiktok` | TikTok Ads deep analysis (Creative, Shop, Smart+) |
| `/ads microsoft` | Microsoft/Bing Ads deep analysis (Copilot, Import) |
| `/ads creative` | Cross-platform creative quality audit |
| `/ads landing` | Landing page quality assessment for ad campaigns |
| `/ads budget` | Budget allocation and bidding strategy review |
| `/ads plan <business-type>` | Strategic ad plan with industry templates |
| `/ads competitor` | Competitor ad intelligence analysis |

## Routing Workflow

Route a paid media request to the right workflow and produce a clear next action.

### 1. Classify the request

Identify whether the user needs:

- full multi-platform audit
- platform deep dive
- strategic plan
- budget and bidding review
- creative audit
- landing page review
- competitor intelligence

### 2. Detect context

Capture business type, active platforms, monthly spend, conversion goal, data available, and urgency.

### 3. Route to the right skill

Use:

- `ads-audit` for full account health
- `ads-plan` for strategy and architecture
- `ads-budget` for spend and bidding
- `ads-competitor` for competitive intelligence
- `ads-creative` for creative fatigue and format quality
- `ads-landing` for post-click conversion quality
- platform skills (`ads-google`, `ads-meta`, `ads-linkedin`, `ads-microsoft`, `ads-tiktok`, `ads-youtube`) for platform deep dives

### 4. Produce a routing note

Document the chosen path, required inputs, expected output, and any immediate blockers.
Optionally save to `{brain}/ads/ads-router-{date}.md`.

## Orchestration Logic

When the user invokes `/ads audit`, delegate to subagents in parallel:
1. Collect account data (exports, screenshots, or API access details)
2. Detect business type and identify active platforms
3. Spawn subagents: audit-google, audit-meta, audit-creative, audit-tracking, audit-budget, audit-compliance
4. Collect results and generate unified report with Ads Health Score (0-100)
5. Create prioritized action plan with Quick Wins

For individual commands (`/ads google`, `/ads meta`, etc.), load the relevant
sub-skill directly.

## Industry Detection

Detect business type from ad account signals:
- **SaaS**: trial_start/demo_request events, pricing page targeting, long attribution windows
- **E-commerce**: purchase events, product catalog/feed, Shopping/PMax campaigns
- **Local Service**: call extensions, location targeting, store visits, directions events
- **B2B Enterprise**: LinkedIn Ads active, ABM lists, high CPA tolerance ($50+), long sales cycle
- **Info Products**: webinar/course funnels, lead gen forms, low-ticket offers
- **Mobile App**: app install campaigns, in-app events, deep linking
- **Real Estate**: listing feeds, property-specific landing pages, geo-heavy targeting
- **Healthcare**: HIPAA compliance flags, healthcare-specific ad policies
- **Finance**: Special Ad Categories declared, financial products compliance
- **Agency**: multiple client accounts, white-label reporting needs

## Quality Gates

Hard rules — never violate these:
- Never recommend Broad Match without Smart Bidding (Google)
- 3x Kill Rule: flag any ad group/campaign with CPA >3x target for pause
- Budget sufficiency: Meta ≥5x CPA per ad set, TikTok ≥50x CPA per ad group
- Learning phase: never recommend edits during active learning phase
- Compliance: always check Special Ad Categories for housing/employment/credit/finance
- Creative: never run silent video ads on TikTok (sound-on platform)
- Attribution: default to 7-day click / 1-day view (Meta), data-driven (Google)

## Reference Files

Load these on-demand as needed — do NOT load all at startup.

**Path resolution:** All references are in `tools/ads-references/`.
When sub-skills or agents reference `ads/references/*.md`, resolve to
`tools/ads-references/*.md`.

- `tools/ads-references/scoring-system.md` — Weighted scoring algorithm and grading thresholds
- `tools/ads-references/benchmarks.md` — Industry benchmarks by platform (CPC, CTR, CVR, ROAS)
- `tools/ads-references/bidding-strategies.md` — Bidding decision trees per platform
- `tools/ads-references/budget-allocation.md` — Platform selection matrix, scaling rules, MER
- `tools/ads-references/platform-specs.md` — Creative specifications across all platforms
- `tools/ads-references/conversion-tracking.md` — Pixel, CAPI, EMQ, ttclid implementation
- `tools/ads-references/compliance.md` — Regulatory requirements, ad policies, privacy
- `tools/ads-references/google-audit.md` — 74-check Google Ads audit checklist
- `tools/ads-references/meta-audit.md` — 46-check Meta Ads audit checklist
- `tools/ads-references/linkedin-audit.md` — 25-check LinkedIn Ads audit checklist
- `tools/ads-references/tiktok-audit.md` — 25-check TikTok Ads audit checklist
- `tools/ads-references/microsoft-audit.md` — 20-check Microsoft Ads audit checklist

## Scoring Methodology

### Ads Health Score (0-100)

Per-platform score using weighted algorithm from `tools/ads-references/scoring-system.md`.
Cross-platform aggregate weighted by budget share:

```
Aggregate = Sum(Platform_Score x Platform_Budget_Share)
```

### Grading

| Grade | Score | Action Required |
|-------|-------|-----------------|
| A | 90-100 | Minor optimizations only |
| B | 75-89 | Some improvement opportunities |
| C | 60-74 | Notable issues need attention |
| D | 40-59 | Significant problems present |
| F | <40 | Urgent intervention required |

### Priority Levels

- **Critical**: Revenue/data loss risk (fix immediately)
- **High**: Significant performance drag (fix within 7 days)
- **Medium**: Optimization opportunity (fix within 30 days)
- **Low**: Best practice, minor impact (backlog)

## Sub-Skills

This skill orchestrates 12 specialized sub-skills:

1. **ads-audit** — Full multi-platform audit with parallel delegation
2. **ads-google** — Google Ads deep analysis (Search, PMax, YouTube)
3. **ads-meta** — Meta Ads deep analysis (FB, IG, Advantage+)
4. **ads-youtube** — YouTube Ads specific analysis
5. **ads-linkedin** — LinkedIn Ads deep analysis
6. **ads-tiktok** — TikTok Ads deep analysis
7. **ads-microsoft** — Microsoft/Bing Ads deep analysis
8. **ads-creative** — Cross-platform creative quality audit
9. **ads-landing** — Landing page quality for ad campaigns
10. **ads-budget** — Budget allocation and bidding strategy
11. **ads-plan** — Strategic ad planning with industry templates
12. **ads-competitor** — Competitor ad intelligence

## Subagents

For parallel analysis during full audits:
- `audit-google` — Google Ads checks (G01-G74)
- `audit-meta` — Meta Ads checks (M01-M46)
- `audit-creative` — Creative quality for LinkedIn, TikTok, Microsoft
- `audit-tracking` — Conversion tracking health across all platforms
- `audit-budget` — Budget, bidding, structure for LinkedIn, TikTok, Microsoft
- `audit-compliance` — Compliance, settings, performance across all platforms

## Quality Standard

- Ask for the smallest missing input that changes the route.
- Do not run a full audit when a narrower deep dive would answer the question.
- Keep platform recommendations tied to business model and conversion goal.

## Adaptation Notes

- Codex can use local exports and reference files from `tools/ads-references/`.
- ChatGPT can support strategy discussion and account-data interpretation when files are uploaded.
