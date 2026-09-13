---
name: geo-audit
description: Audit how easily AI answer engines can discover, understand, and cite a website, then produce a prioritized improvement plan grounded in site evidence and available performance data.
---

# GEO Audit

Use this workflow to evaluate a website for generative engine optimization
(GEO): the work of making useful, accurate web content easier for AI answer
engines to understand and cite.

The audit produces evidence and recommendations. It does not promise rankings,
mentions, citations, traffic, or revenue. Treat observations from sampled AI
answers as a dated snapshot because results can vary by model, location, account,
and time.

## Good uses

- Establish a baseline before improving a website for AI search visibility.
- Find pages that contain strong expertise but are difficult to quote or cite.
- Compare the site's topic coverage with visible competitors.
- Review whether important commercial pages are also clear, crawlable, and useful.
- Recheck the site after a major redesign, migration, or content update.

## What to provide

Required:

- The primary website domain.
- The business, audience, and offers the site should represent accurately.
- The topics or questions for which the organization wants to be useful.

Helpful when available:

- A list of important URLs.
- Three to five competitor domains.
- Google Search Console query and page exports for the last 90 days.
- GA4 landing-page and conversion exports for the last 90 days.
- Ahrefs, Semrush, or similar page and keyword exports.
- A dated sample of relevant questions asked in AI answer engines.

Missing optional data reduces confidence; it does not automatically block the
audit. Say which conclusions cannot be made without each missing source.

## Before beginning

1. Confirm the domain, audience, offer, and desired business outcome.
2. Confirm where the audit should be saved. If no location is supplied, return
   the result in chat and propose `geo/audits/YYYY-MM-DD/`.
3. Record the audit date and every source used.
4. Separate website observations, supplied performance data, sampled AI answers,
   and analyst hypotheses throughout the work.
5. Ask before accessing a private account, changing a website, publishing copy,
   or spending money.

## Workflow

### 1. Define the questions that matter

Create a small question set before reviewing pages. Group questions into:

- **Category questions:** what the product, service, or topic is.
- **Problem questions:** how the audience describes the need or challenge.
- **Comparison questions:** alternatives, differences, pricing, and selection.
- **Trust questions:** evidence, experience, safety, limitations, and fit.
- **Action questions:** implementation, purchase, signup, or next steps.

Use customer language and supplied research when possible. Label invented or
untested questions as hypotheses. Keep the first audit focused; 15 to 30
questions is usually enough.

### 2. Build the evidence inventory

For every source, record its date range, file or URL, and status: received,
checked, unavailable, or skipped.

Use available data to identify:

- Pages already earning search impressions or engaged visits.
- Pages associated with conversions or important offers.
- Topics for which competitors appear stronger.
- Questions that the site should answer but currently does not.
- Pages the organization considers commercially or strategically important.

Do not treat estimated third-party traffic as measured first-party performance.
Do not treat an AI answer sample as stable market share.

### 3. Select priority pages

Propose 10 to 20 pages using the evidence inventory. Balance:

- Existing organic visibility.
- Business importance.
- Relevance to the question set.
- Conversion or engagement evidence.
- Obvious content gaps.

Show the proposed list and selection reason for each page. Get the user's
confirmation before running a large audit. For a quick review, one to five pages
may be enough.

### 4. Inspect technical access

For the domain and each priority page, review:

- HTTP availability and redirects.
- `robots.txt` rules relevant to common search and AI crawlers.
- `noindex`, `nosnippet`, canonical, and other restrictive directives.
- Whether meaningful content is present in the returned HTML.
- Structured data that accurately describes the page.
- Clear titles and heading structure.
- Optional `llms.txt` presence, without treating it as a ranking requirement.

Use `tools/geo_audit.py` when local Python tools are available. The tool provides
a reproducible first pass; inspect its evidence and do not present its numeric
score as an industry standard.

Example:

```bash
python3 tools/geo_audit.py \
  --url https://example.com/important-page \
  --domain example.com \
  --output geo/audits/YYYY-MM-DD/page-scorecards/
```

The optional GEO dependencies are installed with `python -m pip install -e
'.[geo]'`. If the tool or dependencies are unavailable, complete a manual review
and say which automated checks were skipped.

### 5. Review answer and citation usefulness

For each priority page, assess whether a reader or answer engine can find:

- A direct explanation of the page's subject near the beginning.
- Descriptive headings that match real audience questions.
- Self-contained sections that remain understandable when quoted alone.
- Specific entities, examples, dates, quantities, and definitions where useful.
- Clear attribution for research, statistics, and claims.
- Original evidence, experience, examples, or expert judgment.
- The organization and author's relevant identity or credentials.
- Limitations, tradeoffs, and appropriate qualification.
- A clear relationship between the page, the audience's problem, and the offer.

Flag unsupported claims, fake precision, hidden text, doorway pages, keyword
stuffing, and mass-produced near-duplicates as risks. Do not recommend tactics
that make the content less accurate or useful to people.

### 6. Sample AI answers when requested

If the user wants an observed answer baseline and the necessary tools are
available, run the confirmed question set across the selected AI surfaces.
Record:

- Date, product, model or surface when visible, account state, and location when
  relevant.
- Whether the organization is mentioned.
- Which sources are cited.
- Which competitors or alternatives appear.
- Whether the answer addresses the question accurately.

Do not automate around platform restrictions. Do not call a small prompt sample
“share of market.” Report it as an observed citation or mention rate for that
specific sample.

### 7. Produce the audit

Create:

1. `data-inventory.md` — what was checked, the date range, and what is missing.
2. `page-scorecards/` — one review per priority page, when multiple pages were
   audited.
3. `diagnostic.md` — the decision-ready summary.

The diagnostic must include:

- Business goal and audit scope.
- Evidence and limitations.
- Technical access findings.
- Topic and question coverage.
- Page-level strengths and weaknesses.
- Observed AI-answer findings, if sampled.
- A prioritized improvement table with evidence, affected pages, expected
  mechanism, effort, owner, and validation method.
- A 30-day starting plan limited to work supported by the findings.

Use three priority levels:

- **Now:** blocks access, accuracy, or understanding on important pages.
- **Next:** strengthens evidence, structure, coverage, or trust.
- **Later:** useful experiments with weaker evidence or higher effort.

Recommendations should explain why the change may help and how to check it.
Avoid guaranteed outcomes.

## Done when

- The domain, audience, questions, sources, and audit date are recorded.
- Every data source is marked received, checked, unavailable, or skipped.
- Priority pages are confirmed or the limited quick-review scope is explicit.
- Technical and content evidence is separated from hypotheses.
- Each recommendation links to a finding and a validation method.
- Sampled AI answers include enough context to reproduce the observation.
- Missing evidence and unsupported conclusions are visible.
- No website change, publication, account action, or spend occurs without
  separate authorization.

## Related workflows

- Use `seo` for a broader traditional search audit.
- Use `seo-qc` to review a completed article before publication.
- Use `content-brief` when the audit identifies a new article to create.
- Use `cro` when the primary problem is page conversion rather than visibility.
