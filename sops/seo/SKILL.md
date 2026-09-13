---
name: seo
description: Run an advisory SEO audit using GSC, GA4, site data, and structured findings that produce an executive summary, prioritized issue backlog, and action plan (xlsx + markdown).
---

# SEO Audit

Run an advisory SEO audit using GSC, GA4, site data, and structured findings that produce an executive summary, prioritized issue backlog, and action plan (xlsx + markdown).

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/distribution/seo.md (rich) + skills-core/skills/ops/seo.md (portable stub) on 2026-07-03.

Legacy command name: `mktg-seo` (invoked as `/cmo/distribution/seo`) — legacy; use skill id `seo`.

## Goal

Produce an advisory SEO audit with prioritized findings, evidence, recommendations, quick wins, and a clear action plan. Advisory-only workflow: structured intake → guided analysis → xlsx output with exec summary.

## When To Use

- Auditing a client or owned website
- Reviewing GSC and GA4 exports
- Prioritizing SEO work for a content, product, or marketing team
- Creating an executive summary plus implementation backlog

## Workflow Overview

```
1. INTAKE → User provides data via structured Google Sheet
2. ANALYSIS → Work through priority-ordered audit framework
3. OUTPUT → Generate .xlsx file (via document-skills:xlsx) + executive summary
```

---

## 1. Intake Requirements

### Ideal Data Sources

Request client provide a Google Sheet with the following tabs/exports:

| Tab | Source | Contents |
|-----|--------|----------|
| GSC Performance | Google Search Console → Performance → Export | Queries, pages, clicks, impressions, CTR, avg position (last 90 days) |
| GA4 Landing Pages | GA4 → Reports → Engagement → Landing Pages → Export | Landing pages, sessions, engagement rate, conversions |
| Site Info | Manual | Domain, CMS, hosting, known issues, priority pages |
| Keyword Targets | Manual | Current target keywords, priority/tier, current ranking if known |
| Competitors | Manual | 3-5 competitor URLs for comparison |

### Fallback for Limited Access

If client lacks GSC/GA4 access:
- Manual completion of Site Info tab (domain, CMS, known issues, priority pages)
- Screenshots of key GSC/GA4 reports
- List of 10-20 target keywords with expected intent
- Competitor URLs for manual comparison
- Known business goals

### Intake Questions

Ask before starting analysis:
1. What is the primary business goal for this site? (leads, sales, awareness, etc.)
2. What are your top 3 priority pages or content areas?
3. Any known technical issues or recent site changes?
4. Who is the target audience / ideal customer?
5. What CMS/platform is the site built on?

Document which data sources are available and which assumptions are being made.

---

## 2. Audit Framework

Work through in priority order. For each area, document:
- **Issue**: What's wrong
- **Impact**: High / Medium / Low
- **Evidence**: Data or observation supporting the finding
- **Fix**: Specific recommendation
- **Priority**: Critical / High / Medium / Low

### Priority 1: Crawlability & Indexation

**Robots.txt Checks:**
- [ ] robots.txt exists and is accessible at /robots.txt
- [ ] No unintended `Disallow` rules blocking important pages
- [ ] Sitemap reference included
- [ ] No blocking of CSS/JS that affects rendering
- [ ] User-agent rules are correct (not blocking Googlebot)

**XML Sitemap Checks:**
- [ ] Sitemap exists and is valid XML
- [ ] Sitemap URL is in robots.txt
- [ ] Sitemap submitted in GSC
- [ ] Only canonical, indexable URLs included
- [ ] Last modified dates are accurate
- [ ] No 404s, redirects, or non-200 URLs in sitemap
- [ ] Large sites have sitemap index structure

**Site Architecture:**
- [ ] Important pages within 3 clicks from homepage
- [ ] Logical hierarchy (home → category → subcategory → page)
- [ ] No orphan pages (pages with no internal links)
- [ ] Faceted navigation handled properly (if e-commerce)
- [ ] Pagination uses rel="next/prev" or load-more patterns

**Index Status (from GSC):**
- [ ] Check Coverage report for errors
- [ ] Review "Excluded" pages - intentional or problematic?
- [ ] Identify pages marked "Discovered - currently not indexed"
- [ ] Check for soft 404 issues
- [ ] Review any manual actions

### Priority 2: Technical Foundations

**Core Web Vitals (targets):**
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | ≤2.5s | 2.5-4s | >4s |
| INP (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms |
| CLS (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 |

**Technical Checks:**
- [ ] HTTPS implemented sitewide (no mixed content)
- [ ] Proper HTTP → HTTPS redirects
- [ ] Mobile-friendly (responsive design)
- [ ] Page speed acceptable (check PageSpeed Insights)
- [ ] No render-blocking resources above fold
- [ ] Images optimized (WebP, lazy loading, proper sizing)
- [ ] Clean URL structure (no excessive parameters, readable)
- [ ] Canonical tags present and correct
- [ ] Hreflang implemented (if multi-language/region)
- [ ] Structured data present and valid (test in Rich Results Test)

**Common Technical Issues:**
- Redirect chains (more than 2 hops)
- 302 redirects that should be 301s
- Parameter URLs causing duplicate content
- JavaScript rendering issues (content not visible to crawlers)
- Slow server response time (TTFB > 600ms)

### Priority 3: On-Page Optimization

**Title Tags:**
- [ ] Every page has a unique title
- [ ] Primary keyword included, preferably near beginning
- [ ] Length: 50-60 characters (or 580px display width)
- [ ] Brand name at end (if included)
- [ ] Compelling for clicks (not just keywords)
- [ ] No duplicate titles across pages

**Meta Descriptions:**
- [ ] Every page has a unique meta description
- [ ] Length: 150-160 characters
- [ ] Includes primary keyword naturally
- [ ] Contains call-to-action or value proposition
- [ ] Matches search intent

**Heading Structure:**
- [ ] Single H1 per page
- [ ] H1 contains primary keyword and describes page content
- [ ] Logical heading hierarchy (H1 → H2 → H3, no skipping)
- [ ] Headings break up content and aid scannability
- [ ] Keywords in H2s where natural

**Content Optimization:**
- [ ] Primary keyword in first 100 words
- [ ] Related/semantic keywords included naturally
- [ ] Content length appropriate for topic and competition
- [ ] Content matches search intent (informational, transactional, etc.)
- [ ] No thin content pages (< 300 words for key pages)
- [ ] Content is original (not duplicated from other sources)
- [ ] No keyword cannibalization between similar pages

**Image Optimization:**
- [ ] Descriptive file names (not IMG_1234.jpg)
- [ ] Alt text on all images (descriptive, keyword where relevant)
- [ ] Images compressed appropriately
- [ ] Lazy loading implemented for below-fold images

**Internal Linking:**
- [ ] Key pages have sufficient internal links
- [ ] Anchor text is descriptive (not "click here")
- [ ] No broken internal links
- [ ] Important pages linked from navigation or prominent positions
- [ ] Related content linked contextually within body content

### Priority 4: Content Quality

**E-E-A-T Assessment (Experience, Expertise, Authoritativeness, Trustworthiness):**
- [ ] Author information present on content pages
- [ ] Author has demonstrable expertise in topic
- [ ] About page with company/author credentials
- [ ] Contact information easily findable
- [ ] Privacy policy and terms present
- [ ] Trust signals (testimonials, reviews, certifications)
- [ ] Content shows first-hand experience (for YMYL topics especially)
- [ ] Sources cited where making factual claims

**Content Depth:**
- [ ] Content comprehensively covers topic
- [ ] Answers common questions / addresses user needs
- [ ] Includes supporting media (images, videos, charts)
- [ ] Updated regularly / not stale
- [ ] Better than top 3 competitors for target keywords
- [ ] Answerability for search and AI surfaces

**User Engagement Indicators (from GA4):**
- [ ] Engagement rate by page (low = content issues)
- [ ] Average engagement time (compare to content length)
- [ ] Scroll depth (if tracking)
- [ ] Bounce rate in context (high for blog posts may be normal)

### Priority 5: Authority & Links

**Backlink Profile (if data available):**
- [ ] Number of referring domains
- [ ] Quality of linking sites (relevance, authority)
- [ ] Anchor text distribution (not over-optimized)
- [ ] No toxic/spammy links
- [ ] Comparison to top competitors

**Internal Linking Structure:**
- [ ] PageRank flow to priority pages
- [ ] Hub pages linking to related content
- [ ] No dead ends (pages with no outbound internal links)
- [ ] Footer/sidebar links used strategically

**Competitive Position:**
- [ ] Domain authority/rating vs competitors
- [ ] Content gaps (topics competitors rank for, you don't)
- [ ] Backlink gap (sites linking to competitors, not you)
- [ ] Linkable asset opportunities

---

## 3. Common Issues by Site Type

### SaaS / Product Sites
- Homepage too vague (doesn't explain what product does)
- Feature pages targeting same keywords (cannibalization)
- Pricing page not optimized for "[product] pricing" searches
- Comparison pages missing ("[product] vs [competitor]")
- Integration pages not targeting partner keywords
- Help docs not capturing long-tail support queries

### E-commerce Sites
- Category pages thin on content
- Product descriptions duplicated from manufacturer
- Faceted navigation creating duplicate content
- Out-of-stock products not handled properly
- Reviews not structured data marked up
- Size/color variants creating duplicate URLs

### Content / Blog Sites
- Author pages missing or weak E-E-A-T signals
- Outdated content not refreshed
- Keyword cannibalization between similar posts
- Category/tag pages indexable but thin
- No internal linking strategy between related posts
- Featured snippets opportunities missed

### Local Business Sites
- Google Business Profile not optimized
- NAP inconsistent across citations
- Location pages thin/template-y
- No local structured data (LocalBusiness schema)
- Reviews not actively managed
- Local keywords not targeted in content

---

## 4. Prioritize the Action Plan

Group recommendations into:

- Critical
- High
- Quick Win
- Long-Term

For each action, include affected pages, expected impact, dependencies, and owner if known.

---

## 5. Output Generation

Save the markdown summary to `{brain}/ops/seo/seo-audit-{domain}-{date}.md`.

> Example ({brain}=clients/acme): `clients/acme/ops/seo/seo-audit-acme.com-2026-07-03.md`

### Excel Workbook Structure

Generate `.xlsx` file using `document-skills:xlsx`, saved to `{brain}/ops/seo/seo-audit-{domain}-{date}.xlsx`, with these tabs:

**Tab 1: Executive Summary**
| Section | Contents |
|---------|----------|
| Site Overview | Domain, audit date, data sources used |
| Health Score | Overall score 1-100 with category breakdown |
| Top 5 Issues | Most critical problems with impact |
| Quick Wins | High-impact, low-effort fixes |
| Next Steps | Prioritized action items |

**Tab 2: Technical Issues**
| Column | Description |
|--------|-------------|
| Issue | Description of the problem |
| Category | Crawlability / Technical / Speed |
| Impact | High / Medium / Low |
| Evidence | Data or observation |
| Recommendation | Specific fix |
| Priority | Critical / High / Medium / Low |
| Effort | Low / Medium / High |

**Tab 3: On-Page Issues**
Same columns as Technical Issues. Categories: Titles / Metas / Headings / Content / Images / Links

**Tab 4: Content Issues**
Same columns as Technical Issues. Categories: E-E-A-T / Depth / Engagement / Freshness

**Tab 5: Keyword Analysis**
| Column | Description |
|--------|-------------|
| Keyword | Target keyword |
| Current URL | Page currently ranking (if any) |
| Current Position | GSC average position |
| Clicks (90d) | GSC clicks |
| Impressions (90d) | GSC impressions |
| CTR | Click-through rate |
| Opportunity Score | Priority ranking (1-10) |
| Notes | Recommendations |

**Tab 6: Action Plan**
| Column | Description |
|--------|-------------|
| Priority Tier | Critical / High / Quick Win / Long-term |
| Action | Specific task |
| Page(s) Affected | URLs |
| Expected Impact | What improvement to expect |
| Dependencies | What's needed to complete |
| Status | Not Started / In Progress / Complete |

**Tab 7: Raw Data**
Include source data for reference (GSC export, etc.)

### Executive Summary (Markdown)

After generating xlsx, provide markdown summary:

```markdown
## SEO Audit: [Domain]
**Date:** [Date]
**Data Sources:** [GSC, GA4, manual review, etc.]

### Overall Health: [Score]/100

### Top Priority Issues
1. [Issue 1] - [Impact]
2. [Issue 2] - [Impact]
3. [Issue 3] - [Impact]

### Quick Wins
- [Quick win 1]
- [Quick win 2]
- [Quick win 3]

### Recommended Next Steps
1. [Action 1]
2. [Action 2]
3. [Action 3]

### Category Scores
| Category | Score | Status |
|----------|-------|--------|
| Crawlability & Indexation | X/100 | [Good/Needs Work/Critical] |
| Technical Foundations | X/100 | [Good/Needs Work/Critical] |
| On-Page Optimization | X/100 | [Good/Needs Work/Critical] |
| Content Quality | X/100 | [Good/Needs Work/Critical] |
| Authority & Links | X/100 | [Good/Needs Work/Critical] |
```

---

## 6. Related Skills

| Skill | Purpose | Status |
|-------|---------|--------|
| `cro` | Conversion rate optimization for landing pages (formerly `page-cro` placeholder) | Core skill |
| `content-brief` | SEO-informed content briefs for writers | Core skill |
| `writing` | Long-form content production against keyword targets | Core skill |
| `programmatic-seo` | Template-based page generation at scale | Not yet active |
| `schema-markup` | Structured data implementation guidance | Not yet active |
| `analytics-tracking` | GA4/GTM setup and event tracking | Not yet active |

---

## Quality Standard

- Recommendations should be specific enough for implementation.
- Every major finding should include evidence.
- The executive summary should be understandable without SEO expertise.
- The action plan should separate urgency from ease.

## Adaptation Notes

- Codex can work directly with local CSV exports and generate local markdown or spreadsheet artifacts.
- ChatGPT can support advisory walkthroughs when the user uploads exports into a Project.
- Web search or crawl tooling is useful but optional; the audit should still work from structured exports.

---

## Execution Checklist

When running this skill:

1. [ ] Collect intake data (Google Sheet or manual info)
2. [ ] Ask clarifying questions about goals/priorities
3. [ ] Work through Priority 1-5 audit framework
4. [ ] Document all issues with Impact/Evidence/Fix/Priority
5. [ ] Identify quick wins (high impact, low effort)
6. [ ] Generate xlsx output via `document-skills:xlsx`
7. [ ] Write executive summary markdown to `{brain}/ops/seo/`
8. [ ] Deliver both outputs to client
