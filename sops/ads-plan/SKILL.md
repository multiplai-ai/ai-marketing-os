---
name: ads-plan
description: 'Strategic paid advertising planning with industry-specific templates: platform selection, campaign architecture, budget planning, creative strategy, tracking setup, and a phased implementation roadmap.'
---

# Strategic Paid Advertising Plan

Strategic paid advertising planning with industry-specific templates: platform selection, campaign architecture, budget planning, creative strategy, tracking setup, and a phased implementation roadmap.

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/distribution/ads/ads-plan/SKILL.md (rich) + skills-core/skills/paid-media/ads-plan.md (portable stub) on 2026-07-02.

Legacy adapter: previously invoked via `.claude/commands/cmo/distribution/ads/ads-plan/SKILL.md`; that path is now an adapter, not the canonical mechanism.

Use when the user says "ad plan", "ad strategy", "campaign planning", "media plan", "PPC strategy", or "advertising plan".

---

## Process

### 1. Discovery
- Business type, products/services, target audience
- Current advertising status (active platforms, spend, performance)
- Goals: brand awareness, lead generation, e-commerce sales, app installs
- Budget range (monthly/quarterly)
- Timeline and urgency
- In-house team capacity vs agency needs
- Pull upstream strategy context where available: `{brain}/strategy/positioning-strategy.md`, `{brain}/strategy/icp-personas.md`, `{brain}/strategy/brand-strategy.md`

### 2. Competitive Analysis
- Identify top 3-5 competitors
- Analyze their ad presence across platforms (Google Ads Transparency, Meta Ad Library)
- Estimate competitor spend levels and platform mix
- Identify messaging themes and creative approaches
- Note keyword/audience gaps (opportunities competitors are missing) — gaps worth testing

### 3. Platform Selection
- Load industry template from `tools/ads-plan-assets/` directory
- Match business type to recommended platform mix
- Read `tools/ads-references/budget-allocation.md` for platform selection matrix
- Read `tools/ads-references/conversion-tracking.md` for tracking setup requirements
- Choose primary, secondary, and testing channels
- Assess platform fit based on:
  - Target audience demographics per platform
  - Product/service type suitability
  - Budget requirements per platform (minimums)
  - Sales cycle length and attribution needs
  - Creative capabilities and content availability

### 4. Campaign Architecture

Define campaign structure, naming, objectives, audiences, retargeting, and testing lanes.

#### Naming Convention
```
[Platform]_[Objective]_[Audience]_[Geo]_[Date]
```
Example: `META_CONV_Prospecting_US_2026Q1`

#### Campaign Structure Template
```
Account
├── Brand Campaign (always-on, protect brand terms)
├── Non-Brand Prospecting
│   ├── Campaign 1: [Top Funnel - Awareness]
│   │   ├── Ad Group/Set 1: [Audience A]
│   │   └── Ad Group/Set 2: [Audience B]
│   ├── Campaign 2: [Mid Funnel - Consideration]
│   │   ├── Ad Group/Set 1: [Interest-based]
│   │   └── Ad Group/Set 2: [Lookalike/Similar]
│   └── Campaign 3: [Bottom Funnel - Conversion]
│       ├── Ad Group/Set 1: [High-intent]
│       └── Ad Group/Set 2: [Custom audience]
├── Retargeting
│   ├── Website Visitors (7-30 days)
│   ├── Engaged Users (video views, social engagement)
│   └── Cart Abandoners / Form Starters
└── Testing
    └── New audiences, formats, or messaging
```

### 5. Budget Planning

Assign spend across proven, scaling, and testing channels. Note minimum viable budgets and learning-phase requirements.

#### Monthly Budget Distribution
Read `tools/ads-references/budget-allocation.md` for the 70/20/10 framework.

| Tier | Allocation | Purpose |
|------|-----------|---------|
| Proven (70%) | Primary platforms with proven ROI | Revenue engine |
| Scaling (20%) | Platforms showing promise | Growth engine |
| Testing (10%) | New platforms or strategies | Innovation |

#### Budget Pacing
- Month 1-2: heavy testing, expect higher CPA (learning)
- Month 3-4: optimize based on data, tighten targeting
- Month 5-6: scale winners, kill losers, expand
- Ongoing: 70/20/10 maintenance with quarterly reviews

### 6. Creative Strategy

Specify needed formats, messaging wedges, asset count, refresh cadence, and production constraints.

#### Content Pillars
- **Pain Point**: address specific problems your audience faces
- **Social client**: testimonials, case studies, reviews
- **Product Demo**: show the product/service in action
- **Offer**: promotions, free trials, lead magnets
- **Education**: teach something valuable related to your product

#### Creative Production Plan
| Priority | Asset Type | Platforms | Quantity |
|----------|-----------|-----------|----------|
| P1 | Product/service videos (15-30s) | Meta, TikTok, YouTube | 5-10 |
| P2 | Static images with copy | Google, Meta, LinkedIn | 10-15 |
| P3 | Carousel/collection | Meta, LinkedIn | 3-5 |
| P4 | UGC/testimonial video | TikTok, Meta | 3-5 |
| P5 | Long-form video (1-3 min) | YouTube | 2-3 |

### 7. Tracking Setup Plan

Before launching any ads, ensure tracking is configured:

| Platform | Client-Side | Server-Side | Priority |
|----------|------------|-------------|----------|
| Google | gtag.js | Enhanced Conversions, GTM SS | P1 |
| Meta | Pixel | CAPI | P1 |
| LinkedIn | Insight Tag | CAPI (2025) | P2 |
| TikTok | Pixel | Events API + ttclid | P2 |
| Microsoft | UET Tag | Enhanced Conversions | P2 |

### 8. Implementation Roadmap

Create a phased plan covering tracking setup, launch, optimization, and reporting.

#### Phase 1 — Foundation (Weeks 1-2)
- Install all tracking pixels and server-side tracking
- Set up conversion events and goals
- Create campaign structure and naming conventions
- Build initial audiences (custom, lookalike/predictive)
- Produce first batch of creative assets

#### Phase 2 — Launch (Weeks 3-4)
- Launch campaigns on primary platform(s) first
- Set conservative budgets and bidding (Maximize Clicks / Lowest Cost)
- Monitor daily for the first 7 days
- Verify conversion tracking is firing correctly

#### Phase 3 — Optimize (Weeks 5-8)
- Analyze initial data (minimum 2 weeks of data)
- Adjust bidding strategies based on conversion volume
- Kill underperforming ad groups/creatives (3x Kill Rule)
- Launch secondary platforms
- Begin A/B testing (creative, landing pages, audiences)

#### Phase 4 — Scale (Weeks 9-12)
- Scale winning campaigns (20% rule)
- Expand to testing platforms (10% budget)
- Implement advanced strategies (ABM, Shopping feeds, Smart+)
- Monthly performance reviews

## Industry Templates

Load from `tools/ads-plan-assets/` directory based on detected or specified business type:
- `saas.md` — SaaS companies
- `ecommerce.md` — E-commerce stores
- `local-service.md` — Local service businesses
- `b2b-enterprise.md` — B2B enterprise
- `info-products.md` — Info products and courses
- `mobile-app.md` — Mobile app companies
- `real-estate.md` — Real estate
- `healthcare.md` — Healthcare
- `finance.md` — Financial services
- `agency.md` — Marketing agencies
- `generic.md` — General business template

## Output

Save plan deliverables under `{brain}/ads/plans/`:

### Deliverables
- `{brain}/ads/plans/ads-strategy-{date}.md` — Complete strategic advertising plan
- `{brain}/ads/plans/campaign-architecture-{date}.md` — Campaign structure with naming conventions
- `{brain}/ads/plans/budget-plan-{date}.md` — Budget allocation with monthly pacing
- `{brain}/ads/plans/creative-brief-{date}.md` — Creative production plan with specifications
- `{brain}/ads/plans/tracking-setup-{date}.md` — Tracking implementation checklist
- `{brain}/ads/plans/implementation-roadmap-{date}.md` — Phased rollout timeline

For a lightweight engagement, a single consolidated plan at `{brain}/ads/plans/ads-plan-{date}.md` is acceptable (the portable stub's default artifact).

Example (legacy command output names): `ADS-STRATEGY.md`, `CAMPAIGN-ARCHITECTURE.md`, `BUDGET-PLAN.md`, `CREATIVE-BRIEF.md`, `TRACKING-SETUP.md`, `IMPLEMENTATION-ROADMAP.md` written to the working directory.

### KPI Targets
| Metric | Month 1 | Month 3 | Month 6 | Month 12 |
|--------|---------|---------|---------|----------|
| ROAS | Baseline | Target -20% | Target | Target +20% |
| CPA | Baseline | Target +30% | Target | Target -10% |
| CVR | Baseline | +10% | +20% | +30% |
| CTR | Baseline | +15% | +25% | +30% |
| Budget | Testing | Optimizing | Scaling | Maintaining |

## Quality Standard

- Platform choices should match audience and budget reality.
- Tracking requirements should be explicit before launch.
- The plan should distinguish launch essentials from later tests.

## Adaptation Notes

- Codex can use `tools/ads-plan-assets/` templates for business-type-specific plans.
- ChatGPT is useful for media strategy workshop conversations.
