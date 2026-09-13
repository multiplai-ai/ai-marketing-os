# AI Marketing OS

A shared library of marketing workflows you can use with a local AI agent.
Start with a business source packet, produce a content brief, and review a draft
against those same facts. Your business context and outputs live in your own
workspace.

The source is available under the [MIT License](LICENSE). AI subscriptions,
API usage, and optional services are separate. The first release is a preview:
start with the three tested starter workflows before exploring the broader library.

## Create your first workspace

Install **Python 3.12, Git, zstd, and Minisign**. On macOS with Homebrew,
`brew install python@3.12 git zstd minisign` provides these prerequisites.
Then run:

```bash
git clone https://github.com/multiplai-ai/ai-marketing-os.git
cd ai-marketing-os
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[publishing]'
python tools/start_member.py --workspace ../my-marketing
```

Setup anonymously downloads the pinned public release, verifies both signatures
and the digest, and creates a separate workspace. It refuses to overwrite existing
work. The source checkout pins the public signing key; obtain this checkout from
the repository above and review [release trust](releases/TRUST.md).

Open `my-marketing` in Codex and ask:

> Use content-brief and context/business-context.md to create an offline brief
> for bicycle repair scheduling. Save it in content/briefs/. Cite packet source
> IDs, label live search research as not checked, and use the walkthrough CTA.
> Do not publish.

The starting packet describes a fictional workshop. Review the result, then
replace the packet with your own source-backed facts. Keep the Python environment
active for agent terminal commands. For setup details, an explicit skill resolver,
updates, and troubleshooting, see the [member guide](docs/member-guide.md).

## What is included

- **content-brief:** turn a business packet into a local, evidence-limited brief.
- **human-writing-standard:** review prose and unsupported claims against sources.
- **writing-setup:** create your writing configuration and calibrate voice with review.
- **80 additional workflows:** inspect the [catalog](docs/capabilities.md) and opt in
  deliberately. Live integrations remain unverified and may require separate tools.

Six GEO workflows and their inherited adaptations are excluded pending rights
review. The [test plan](docs/workflow-testing.md) distinguishes automated checks,
recorded agent outputs, and the human workflow tests still worth doing.

## Development and ownership

Use `python -m pip install -e '.[dev,publishing]'`, then
`python tools/check_core.py`. Optional `web`, `google`, `llm`, and `video` extras
support other integrations. Browser workflows also require
`python -m playwright install chromium`.

This repository is the canonical home for future shared procedure changes.
Edit `sops/<id>/SKILL.md`, regenerate adapters, validate, and submit a reviewed PR.
See [contributing](CONTRIBUTING.md). Existing private history and signed releases
remain private; old consumers retain their pins until a reviewed migration.
