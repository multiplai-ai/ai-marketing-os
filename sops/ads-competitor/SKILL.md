---
name: ads-competitor
description: 'Competitor ad intelligence analysis across Google, Meta, LinkedIn, TikTok, Microsoft, and YouTube: analyze competitor ad copy, creative strategy, keyword targeting, and estimated spend, and turn them into messaging, platform, creative, and budget opportunities.'
---

# Competitor Ad Intelligence

Competitor ad intelligence analysis across Google, Meta, LinkedIn, TikTok, Microsoft, and YouTube: analyze competitor ad copy, creative strategy, keyword targeting, and estimated spend, and turn them into messaging, platform, creative, and budget opportunities.

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/distribution/ads/ads-competitor/SKILL.md (rich) + skills-core/skills/paid-media/ads-competitor.md (portable stub) on 2026-07-02.

## When To Use

Use when user says "competitor ads", "ad spy", "competitive analysis", "competitor PPC", or "ad intelligence".

## Process

1. Identify target competitors (from user input or industry analysis) — confirm direct competitors, aspirational competitors, and category substitutes
2. Read `tools/ads-references/benchmarks.md` for industry CPC/CTR/CVR baselines
3. Research competitor ad presence across platforms
4. Analyze ad copy, creative, and messaging themes
5. Estimate competitor spend and keyword strategy
6. Identify gaps and opportunities
7. Generate competitive intelligence report

## Data Sources

### Free Intelligence Sources
| Source | Platform | What You Can Find |
|--------|----------|------------------|
| Google Ads Transparency Center | Google | Active ads, formats, geo targeting |
| Meta Ad Library | Meta/Instagram | All active ads, creative, copy, spend range |
| LinkedIn Ad Library | LinkedIn | Active ads from company pages |
| TikTok Creative Center | TikTok | Top ads, trending creative, hashtags |
| Microsoft Ads | Microsoft | Limited — use auction insights |

YouTube ad activity surfaces through the Google Ads Transparency Center (search by advertiser) and public channel activity.

### Google Ads Auction Insights
Available from the user's own Google Ads account:
- Impression share vs competitors
- Overlap rate (how often you compete)
- Outranking share (who wins more often)
- Top of page rate and absolute top of page rate
- Available for Search and Shopping campaigns

### Platform-Specific Research

#### Google
- Ads Transparency Center: search by advertiser name or domain
- Search for competitor brand terms to see their ads live
- Auction Insights for impression share comparison

#### Meta
- Ad Library: filter by advertiser, country, platform (FB/IG), date range
- Shows creative (image/video), ad copy, active dates
- Shows platform placement (Facebook, Instagram, Audience Network)

#### LinkedIn
- Ad Library: search by company name
- Shows Sponsored Content, Message Ads
- Limited data compared to Meta Ad Library

#### TikTok
- Creative Center: top-performing ads by industry, country, objective
- Hashtag analytics: trending sounds and hashtags
- No per-advertiser library — use Creative Center for industry trends

## Competitive Analysis Framework

### 1. Ad Copy Analysis
For each competitor, document:
- **Headlines**: primary messages and value propositions
- **CTAs**: what action they're driving (free trial, demo, buy now, learn more)
- **Offers**: pricing, discounts, free shipping, trials
- **Tone**: professional, casual, urgent, educational, emotional
- **USPs**: unique selling propositions they emphasize
- **Pain points**: customer problems they address
- **client claims**: evidence, stats, and social client they cite
- **Objections addressed**: which buyer objections the copy pre-empts
- **Audience signals**: who the ad is speaking to (role, segment, stage)

### 2. Creative Strategy Analysis
- **Formats used**: image, video, carousel, collection, document
- **Visual style**: photography, illustration, UGC, stock, branded
- **Hooks**: opening lines and visual hooks used to stop the scroll
- **Video approach**: studio quality vs UGC vs animated; motion and product-shot patterns
- **Creative volume**: how many active ads (indicator of testing velocity)
- **Refresh frequency**: how often new creatives appear (refresh cadence)

### 3. Messaging Themes
Categorize competitor messaging into themes:
| Theme | Competitor A | Competitor B | Your Brand |
|-------|-------------|-------------|------------|
| Price/Value | ✅ Primary | ⚠️ Secondary | ? |
| Quality/Premium | ❌ | ✅ Primary | ? |
| Speed/Convenience | ⚠️ Secondary | ❌ | ? |
| Trust/Authority | ✅ Primary | ✅ Primary | ? |
| Innovation | ❌ | ⚠️ Secondary | ? |

### 4. Keyword Intelligence (Google/Microsoft)
- Brand keyword bidding: are competitors bidding on your brand?
- Keyword overlap: which non-brand terms do you both target?
- Keyword gaps: terms competitors rank for that you don't target
- Match type strategy: estimated match types from ad triggers

### 5. Spend Estimation
- Meta Ad Library shows spend ranges for political/social ads
- Google Auction Insights + impression share = directional spend estimate
- Third-party tools (SEMrush, SpyFu) for more precise estimates
- Manual estimation formula:
  ```
  Estimated Monthly Spend = Impressions × CPM / 1000
  or
  Estimated Monthly Spend = Clicks × Estimated CPC
  ```

## Gap & Opportunity Identification

### Platform Gaps
- Which platforms are competitors NOT on? (opportunity to own)
- Which platforms are they underspending on? (opportunity to outspend)
- Where are competitors overreliant on a single platform? (concentration = vulnerability)

### Messaging Gaps
- What customer pain points are NO competitors addressing?
- What value propositions are underrepresented in the market?
- What content formats are competitors not using?
- What weak messaging territories can you claim?

### Audience Gaps
- What demographics/segments are competitors not targeting?
- What geographic markets are underserved?
- What funnel stages are competitors neglecting?

### Creative Gaps
- What ad formats are competitors not using? (video, UGC, Spark Ads)
- What creative styles are missing from the competitive landscape?
- What platform-specific features are competitors not leveraging?

### Landing Page Opportunities
- Where do competitor ads send traffic, and how strong is the post-click experience?
- What landing page angles, offers, or client are competitors missing that you can win on?

## Competitive Response Strategy

### When Competitors Bid on Your Brand
- Always run brand campaigns to defend (low CPC, high CTR)
- Dynamic keyword insertion to show your brand prominently
- Sitelinks to key pages (pricing, features, reviews)
- Ad copy that emphasizes unique differentiators
- Consider bidding on competitor brand terms (know the rules)

### When You're Outspent
- Focus on efficiency over volume (better targeting, creative, landing pages)
- Target long-tail keywords competitors ignore
- Use Exact match for precision (less waste)
- Double down on retargeting (lower CPA than prospecting)
- Compete on creative quality, not budget

## Output

### Deliverables
- `{brain}/ads/competitive/COMPETITOR-INTELLIGENCE-REPORT.md` — Full competitive analysis
  - Per-competitor ad presence summary
  - Ad copy and messaging analysis
  - Creative strategy comparison
  - Estimated spend levels
  - Keyword overlap and gaps
- `{brain}/ads/competitive/COMPETITIVE-GAPS.md` — Opportunities identified from competitor analysis
  - Platform gaps
  - Messaging opportunities
  - Audience segments to target
  - Creative format opportunities
- Strategic recommendations for competitive positioning
- Priority actions to gain competitive advantage

For a single dated run artifact (portable-stub convention), save to `{brain}/ads/competitive/ads-competitor-{date}.md`.

## Quality Standard

- Distinguish observed evidence from inference.
- Focus on actionable gaps, not a catalog of screenshots.
- Do not copy competitor creative; translate patterns into strategy.

## Adaptation Notes

- This workflow benefits from browsing or user-provided screenshots.
- Codex can organize findings into local research files.
