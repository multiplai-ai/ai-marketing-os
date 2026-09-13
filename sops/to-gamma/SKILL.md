---
name: to-gamma
description: Publish a markdown file to Gamma as a presentation, document, or webpage.
---

# Gamma Publishing Runbook

Publish a markdown file to Gamma as a presentation, document, or webpage.

Use Gamma as the default final share surface for organization, brand, and
client-facing recommendations, proposals, reports, leave-behinds, and polished
async docs. See `docs/runbooks/publishing/client-facing-deliverables.md`.

## Tool

- `tools/gamma_create_presentation.py`

## Workflow

1. Confirm the markdown file and desired format: `presentation`, `document`, or `webpage`.
2. Preview the structure if needed:

```bash
python3 tools/gamma_create_presentation.py <file.md> --dry-run
```

3. Publish:

```bash
python3 tools/gamma_create_presentation.py <file.md>
```

4. For organization artifacts, apply the brand context from:
   - `brains/organization/creative/brand-guide.md`
   - `brains/organization/creative/tokens.json`
   - `brains/organization/creative/generated/gamma-prompts.md`
5. Return the Gamma URL and tell the user what still needs human review in Gamma.

## Useful Options

```bash
python3 tools/gamma_create_presentation.py <file.md> --title "Custom Title"
python3 tools/gamma_create_presentation.py <file.md> --format document
python3 tools/gamma_create_presentation.py <file.md> --format webpage
python3 tools/gamma_create_presentation.py <file.md> --theme-name "organization"
python3 tools/gamma_create_presentation.py <file.md> --additional-instructions "Use the current approved brand guide and tokens resolved from the consumer binding."
python3 tools/gamma_create_presentation.py --test
```

For organization artifacts, prefer a saved Gamma theme named `organization`
when it exists. If there is no saved theme, pass concise
`--additional-instructions` from the brand guide and use the image-style prompt
from `brains/organization/creative/generated/gamma-prompts.md`.

## Required Environment

```bash
GAMMA_API_KEY=
```

## Guardrails

- Use `---` on its own line for slide breaks.
- Do not substitute an unstyled Google Doc for a client-facing Gamma deliverable.
- Do not substitute a local markdown preview if Gamma publishing fails.
- Report API failures clearly and stop.
