---
name: design-extract
description: Extract a design system from a live URL — reverse-engineers colors, typography, spacing, borders, and shadows into a usable token architecture that feeds directly into `/design-systems` Stage 3.
---

# Design Extract

Extract a design system from a live URL — reverse-engineers colors, typography, spacing, borders, and shadows into a usable token architecture that feeds directly into `/design-systems` Stage 3.

> Core skill canon (Phase 4). Merged from .claude/commands/cmo/strategy/design-extract.md (rich) + skills-core/skills/strategy/design-extract.md (portable stub) on 2026-07-02.

Extract an existing website's design system and feed it into `/design-systems` Stage 3 (full system build) — skipping the manual mood/palette exploration stages.

**When to use:**
- You have a live site (yours or a reference) and want to pull its design tokens into a structured, production-ready design system
- A user wants to model an existing site or reference
- A brand has a live website but no reusable token system
- A design system should start from observed colors, type, spacing, radii, and shadows

---

## Flow

```
User provides URL
    ↓
Run tools/extract_design_tokens.py → raw extraction JSON
    ↓
Claude analyzes: identifies primary/secondary/accent,
    picks dominant font pairings, categorizes spacing scale
    ↓
Present extracted values for user confirmation/adjustment
    ↓
Auto-generate palette-typography.md (Stage 2 artifact)
    with status: approved
    ↓
Hand off to /design-systems Stage 3 (full system build)
    → design-system.md, design-tokens.json, design-tokens.css,
      tailwind.extend.js, style-tile-final.html
```

---

## Step 1: Get URL and Target Project

Ask the user for:

1. **URL to extract from** (required)
2. **Project name** — determines output path at `{brain}/projects/<project-name>/`
   - If user is already working in an entity context, use that entity's project directory
3. **Extraction goal** — whether the extraction should preserve the site's current look or use it only as inspiration

If not provided, ask:

```
What URL should I extract design tokens from?
And what project should the design system live under?
(e.g., "{brain}/projects/my-brand/")
```

---

## Step 2: Run Extraction Tool

Run the extraction tool with a screenshot (when local execution is available):

```bash
python tools/extract_design_tokens.py "[URL]" --output .tmp --screenshot
```

**If the tool fails:** Report the error and suggest alternatives:
- Try a different URL (the homepage is usually best)
- Check if the site requires JavaScript rendering time (SPAs)
- Try without `--screenshot` if that's the issue
- Fall back to manual interpretation from screenshots or CSS snippets the user provides

**If successful:** Read the output JSON from `.tmp/extracted-tokens-[domain].json`

---

## Step 3: Analyze and Present Extraction

Read the extraction JSON and present a structured summary for user review.

### Analysis Template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTRACTED DESIGN TOKENS — [domain]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Color Palette (extracted)

| Role        | Hex     | Confidence | Notes |
|-------------|---------|------------|-------|
| Primary     | #XXXXXX | High/Med   | [Why this was picked — e.g., "Most frequent chromatic color, used in CTAs and links"] |
| Secondary   | #XXXXXX | High/Med   | [Context] |
| Accent      | #XXXXXX | Med/Low    | [Context] |
| Surface     | #XXXXXX | High       | [Context] |
| Text        | #XXXXXX | High       | [Context] |
| Border      | #XXXXXX | Med        | [Context] |

### Color Notes
- [Any ambiguities — e.g., "Site uses 12 shades of gray; picked #6B7280 as the dominant neutral"]
- [Whether the site appears to be dark-themed or light-themed]
- [If CSS variables were found, note any color tokens already defined]

## Typography (extracted)

| Role     | Font          | Confidence | Notes |
|----------|---------------|------------|-------|
| Heading  | [Font Name]   | High/Med   | [Usage context] |
| Body     | [Font Name]   | High/Med   | [Usage context] |
| Mono     | [Font Name]   | Med/Low    | [If found] |

### Type Scale
[List the extracted font sizes in order, noting which is the base size]

## Spacing

- **Base unit:** [Npx]
- **Scale:** [4 / 8 / 12 / 16 / 24 / 32 / 48 / 64]

## Shape Language

- **Border radii:** [Most common values]
- **Shadow style:** [Description of shadow approach]

## CSS Variables Found
[If the site defines CSS custom properties, list the most relevant ones —
this indicates the site already has a token system we can reference]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Interpretation Rules

When analyzing the extraction, state confidence and rationale for each role assignment. Do not treat frequency analysis as truth without interpretation.

**Colors:**
- The most frequent chromatic color (not text, not background) = **primary**
- The second most frequent chromatic color = **secondary**
- Third = **accent** (or if no third, skip accent)
- Most frequent very-light color (luminance > 0.9) = **surface**
- Most frequent very-dark color (luminance < 0.1) = **text**
- If the site is dark-themed (dark surfaces, light text), flag this and invert the surface/text assignments

**Typography:**
- If only one font family found → use for both heading and body
- If two found → the one with fewer occurrences is likely headings (used in fewer places but more prominent)
- Look for monospace fonts in code blocks / technical elements

**Spacing:**
- Identify the base unit (usually 4px or 8px)
- If the spacing values don't follow a clean scale, note this and propose the closest clean scale

---

## Step 4: User Confirmation

Ask the user to confirm or adjust the extracted values:

```markdown
Does this extraction look right? Adjustments I'd recommend reviewing:

1. **Primary color** — [any concerns about the pick]
2. **Font pairing** — [any concerns]
3. **[Any other ambiguity]**

Options:
- **Proceed as-is** — I'll generate the full design system from these values
- **Adjust** — Tell me what to change (e.g., "use #2563EB as primary instead")
- **Re-extract** — Try a different URL or page
```

**STOP and wait for user confirmation before proceeding.** Never mark extracted values as approved without user confirmation.

---

## Step 5: Generate palette-typography.md

Once the user approves (with any adjustments), generate the Stage 2 artifact.

Save to: `{brain}/projects/<project-name>/palette-typography.md`

Also persist a copy of the raw extraction JSON alongside it as `{brain}/projects/<project-name>/extracted-tokens.json` so the extraction survives `.tmp` cleanup.

```markdown
---
title: Palette & Typography — [Project Name]
created: YYYY-MM-DD
status: approved
source: extracted from [URL]
extraction-date: YYYY-MM-DD
---

# Palette & Typography

> Extracted from [URL] and confirmed by user.

## Color Palette

| Role | Color | Hex | Source |
|------|-------|-----|--------|
| Primary | [Name] | [#hex] | [Extracted: most frequent chromatic / User adjusted] |
| Secondary | [Name] | [#hex] | [Source] |
| Accent | [Name] | [#hex] | [Source] |
| Surface | [Name] | [#hex] | [Source] |
| Text Primary | [Name] | [#hex] | [Source] |
| Text Secondary | [Name] | [#hex] | [Source] |

## Typography

| Role | Font | Weights | Source |
|------|------|---------|--------|
| Headings | [Font name] | [weights found] | [Extracted / Adjusted] |
| Body | [Font name] | [weights found] | [Extracted / Adjusted] |
| Mono | [Font name] | [weights found] | [If found] |

## Shape Language

| Property | Value | Source |
|----------|-------|--------|
| Border radius | [Xpx] | [Most common extracted value] |
| Shadow style | [Description] | [Extracted pattern] |
| Spacing density | [Compact/Balanced/Spacious] | [Based on spacing scale] |

---

*Extracted: YYYY-MM-DD from [URL]*
*Approved: YYYY-MM-DD*
*Ready for: Stage 3 (Full System Build)*
```

Include notes on any user adjustments so downstream stages know which values were extracted versus overridden.

---

## Step 6: Hand Off to Stage 3

After saving `palette-typography.md`, tell the user:

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTRACTION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Saved: {brain}/projects/<project-name>/palette-typography.md (status: approved)

Ready to build the full design system. This will generate:
- design-system.md (complete spec)
- design-tokens.json (token architecture)
- design-tokens.css (CSS custom properties)
- tailwind.extend.js (Tailwind config)
- style-tile-final.html (visual preview)

Shall I proceed with the full build? (This runs /design-systems build)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If user says yes, invoke `/design-systems build` which will pick up the `palette-typography.md` and run Stage 3.

---

## Edge Cases

### Dark-themed sites
If the extraction shows light text on dark backgrounds (surface luminance < 0.3):
- Flag this to the user
- Ask if the design system should be dark-first or light-first
- Adjust surface/text color assignments accordingly

### Sites with existing CSS variables
If the extraction finds CSS custom properties (e.g., `--color-primary`, `--spacing-4`):
- Present these alongside the computed values
- The CSS variables may be more authoritative than frequency analysis
- Suggest using the variable values over the computed values

### SPAs / JS-heavy sites
If the extraction returns sparse results:
- The page may not have fully rendered
- Suggest trying with a longer wait time
- Suggest extracting from a specific subpage with more content

### Web fonts not loading
If only system fonts are detected:
- Check if fonts loaded (the page may use `font-display: swap`)
- Look for Google Fonts / Adobe Fonts link tags in the HTML
- Suggest checking the site's `<head>` for font references

---

## Quality Checklist

- [ ] Extraction tool ran successfully
- [ ] JSON output is valid and complete
- [ ] Color roles assigned with clear rationale
- [ ] Font families identified (not just system fallbacks)
- [ ] Spacing scale is coherent
- [ ] User reviewed and confirmed/adjusted values
- [ ] palette-typography.md generated with status: approved
- [ ] User prompted to continue to Stage 3

---

## Adaptation Notes

- Codex can run the extraction script and write artifacts.
- ChatGPT can perform manual interpretation when the user uploads screenshots or CSS snippets.
