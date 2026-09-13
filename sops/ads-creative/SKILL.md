---
name: ads-creative
description: 'Cross-platform creative quality audit covering ad copy, video, image, and format diversity across all platforms: detects creative fatigue, evaluates platform-native compliance, assesses message coverage, and produces production priority recommendations.'
---

# Ads Creative — Cross-Platform Creative Quality Audit

Cross-platform creative quality audit covering ad copy, video, image, and format diversity across all platforms: detects creative fatigue, evaluates platform-native compliance, assesses message coverage, and produces production priority recommendations.


Legacy adapter: previously invoked as the `/ads creative` sub-skill via `.claude/commands/cmo/distribution/ads/ads-creative/SKILL.md`; that path is now an adapter, not the canonical mechanism.

Triggers on: "creative audit", "ad creative", "creative fatigue", "ad copy", "ad design", "creative review".

---

## Goal

Assess whether ad creative is diverse, platform-native, fresh, and aligned with the conversion goal.

## Input / Output Contract

**Inputs:**

- creative_assets
- creative_performance
- platform_mix
- brand_guidelines (`{brain}/voice/visual-brand-guide.md` when available)

**Outputs:**

- Creative audit report: `{brain}/ads/creative/ads-creative-audit-{date}.md`

## Process

1. Collect creative assets or performance data from active platforms (active ads, performance data, screenshots, videos, copy, and placement context)
2. Read `tools/ads-references/platform-specs.md` for creative specifications
3. Read `tools/ads-references/benchmarks.md` for CTR/engagement benchmarks
4. Read `tools/ads-references/scoring-system.md` for weighted scoring algorithm
5. Evaluate creative quality per platform
6. Assess cross-platform creative consistency
7. Assess message coverage
8. Generate production priority recommendations

## Per-Platform Assessment

### Google Ads Creative
- RSA: ≥8 unique headlines, ≥3 descriptions per ad group
- RSA ad strength: "Good" or "Excellent"
- Pin usage: minimal and strategic (over-pinning kills RSA flexibility)
- Extensions: sitelinks (≥4), callouts (≥4), structured snippets, image
- PMax asset groups: text + image + video + optional product feed
- YouTube: video quality, hook, subtitles (see the ads-youtube core skill)

### Meta Ads Creative
- Format diversity: ≥3 formats active (image, video, carousel, collection)
- Creative volume: ≥5 creatives per ad set
- Fatigue detection: CTR declining >20% over 14 days = FAIL
- Video length: 15s max Stories/Reels, 30s max Feed
- UGC/testimonial content tested
- Advantage+ Creative enhancements enabled
- Headline under 40 chars, primary text under 125 chars

### LinkedIn Creative
- Thought Leader Ads active, ≥30% budget for B2B
- Format diversity: ≥2 formats tested (single image, carousel, video, document)
- Video ads tested
- Creative refresh: every 4-6 weeks
- Professional tone appropriate for platform

### TikTok Creative
- ≥6 creatives per ad group (Critical requirement)
- All video 9:16 vertical 1080x1920 (non-negotiable)
- Native-looking content (not corporate)
- Hook in first 1-2 seconds
- No creative active >7 days with declining CTR
- Spark Ads tested (~3% CTR vs ~2% standard)
- Sound-on optimization (never silent)
- Safe zone compliance: X:40-940, Y:150-1470
- Trending audio used

### Microsoft Creative
- RSA: ≥8 headlines, ≥3 descriptions
- Multimedia Ads tested (unique rich format)
- Ad copy optimized for Bing demographics (older, higher income, professional)
- Action Extension utilized (unique to Microsoft)
- Filter Link Extension tested

## Creative Fatigue Detection

Look for declining CTR, rising CPA, high frequency, stale assets, and repeated hooks.

### Signals of Fatigue
| Signal | Threshold | Action |
|--------|-----------|--------|
| CTR declining | >20% over 14 days | Refresh creative |
| Frequency (Meta) | >5.0 prospecting, >12.0 retargeting | New audience or creative |
| Watch time declining (TikTok) | <3s average | New hook needed |
| QS declining (Google) | Drop of 2+ points | Refresh ad copy |
| Engagement rate drop | >30% decline | Full creative overhaul |

### Refresh Cadence by Platform
| Platform | Recommended Refresh |
|----------|-------------------|
| Google Search | Every 8-12 weeks |
| Meta | Every 2-4 weeks |
| LinkedIn | Every 4-6 weeks |
| TikTok | Every 5-7 days (fastest fatigue) |
| Microsoft | Every 8-12 weeks |
| YouTube | Every 4-8 weeks |

## Message Coverage Assessment

Map creative to:

- pain points
- client
- offers
- objections
- personas
- funnel stages

## Format Diversity Matrix

Evaluate which formats are active per platform:

| Format | Google | Meta | LinkedIn | TikTok | Microsoft |
|--------|--------|------|----------|--------|-----------|
| Static Image | RSA image ext | ✅ | ✅ | ❌ | Multimedia |
| Video | YouTube, PMax | ✅ | ✅ | ✅ (required) | ❌ |
| Carousel | ❌ | ✅ | ✅ | ❌ | ❌ |
| Collection | ❌ | ✅ | ❌ | ❌ | ❌ |
| Document | ❌ | ❌ | ✅ | ❌ | ❌ |
| Shopping | PMax, Shopping | Catalog | ❌ | Shop | Shopping |

## Universal Creative Best Practices

### Cross-Platform Safe Zone
- 900x1000px usable area works across all vertical placements
- Keep critical elements centered and within safe margins
- Test on mobile devices (75%+ of ad impressions are mobile)

### Ad Copy Principles
- Lead with benefit, not feature
- Include clear CTA (what should they do next?)
- Match ad message to landing page (message match)
- Use numbers and specifics over vague claims
- Test emotional vs rational appeals

### Video Production Standards
- H.264 codec, AAC audio, MP4 container
- Minimum 720p (1080p preferred)
- Subtitles/captions always (accessibility + sound-off viewing)
- Brand mention within first 5s (awareness) or at CTA (performance)

For producing new on-brand creative from the recommendations, hand off to the visual-content and creative-produce core skills.

## Output

### Creative Quality Report

```
Cross-Platform Creative Health

Google:     ████████░░  X/X checks passing
Meta:       ██████████  X/X checks passing
LinkedIn:   ███████░░░  X/X checks passing
TikTok:     █████░░░░░  X/X checks passing
Microsoft:  ████████░░  X/X checks passing
```

### Deliverables

Save the audit report to `{brain}/ads/creative/ads-creative-audit-{date}.md` (legacy adapter filename: `CREATIVE-AUDIT-REPORT.md`). It contains:

- Per-platform creative assessment
- Fatigue alerts (any creative past refresh cadence)
- Format diversity gaps per platform
- Production priority list (most impactful creative to produce next)
- Quick Wins (format conversions, CTA changes, Spark Ads setup)

## Quality Standard

- Recommendations should specify creative formats, not just say "make more ads."
- Platform-native fit matters as much as brand consistency.
- Fatigue findings should cite performance or cadence evidence when available.

## Adaptation Notes

- Codex can work from local asset folders and exports.
- ChatGPT can help brainstorm creative wedges and copy variants.
