---
name: publish
description: Use this when content is ready to move from local markdown into publishing systems. This is a tool-backed procedure, not a model-authored marketing skill.
---

# Publishing Runbook

Use this when content is ready to move from local markdown into publishing systems. This is a tool-backed procedure, not a model-authored marketing skill.

## Scope

- Generate or verify images for an article or social post.
- Push article/newsletter content to Ghost as a draft.
- Push social posts to Publer as drafts.
- Keep final human review in Ghost/Publer before scheduling.

## Tools

- `tools/image_resolver.py`
- `tools/templated_renderer.py`
- `tools/ghost_publisher.py`
- `tools/publer_publisher.py`

Deprecated but preserved for reference:

- `tools/buffer_publisher.py`
- `tools/metricool_publisher.py`

## Workflow

1. Confirm the content file path and destination: Ghost, Publer, or both.
2. Run image resolution before publishing:

```bash
python3 tools/image_resolver.py --resolve <content-slug>
```

3. Generate missing branded images when templates exist:

```bash
python3 tools/templated_renderer.py --render <content-file>
```

4. Publish article to Ghost as a draft:

```bash
python3 tools/ghost_publisher.py --draft <content-file>
```

5. Publish social posts to Publer as drafts:

```bash
python3 tools/publer_publisher.py --publish <social-posts-json>
```

6. Tell the user to review in Ghost Admin and Publer before scheduling.

## Required Environment

```bash
GHOST_URL=
GHOST_ADMIN_API_KEY=
PUBLER_API_KEY=
PUBLER_WORKSPACE_ID=
TEMPLATED_API_KEY=
```

## Guardrails

- Never present a local dry run as if it published externally.
- If a publishing tool fails, report the exact tool and error.
- If images are missing and no template exists, ask whether to proceed without images or pause to create the template.
