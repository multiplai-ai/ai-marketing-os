# AI Marketing OS

AI Marketing OS gives Claude or Codex a library of practical marketing
workflows. You bring your business documents and judgment; the AI uses the
relevant workflow to help research, plan, write, review, or analyze the work.

This is a set of reusable instructions for your AI assistant. It is not a
dashboard and you do not need to learn the repository's code to use it.

## What can it help with?

- Build positioning, ideal-customer, brand, and content strategy
- Turn source material into briefs, articles, newsletters, and LinkedIn posts
- Plan content calendars and campaigns
- Review SEO, landing pages, creative, and paid advertising
- Audit how well AI answer engines can understand and cite a website
- Create campaign assets, visual directions, and shareable marketing visuals

[Browse the workflow library](docs/capabilities.md) or follow the
[five-minute guide](START-HERE.md).

## Use it with Claude — recommended

Most people should install AI Marketing OS as a Claude plugin. Once installed,
Claude can choose a workflow automatically from your request, or you can select
one from Claude's `/` or `+` menu.

### Claude Desktop, Claude on the web, or Cowork

1. Open the repository's [Releases](https://github.com/multiplai-ai/ai-marketing-os/releases) page.
2. Open the newest release and download the file whose name starts with
   `ai-marketing-os-claude-plugin-`.
3. In Claude, open **Customize**, then **Plugins**.
4. Choose the option to upload a custom plugin and select the downloaded ZIP file.
5. Open a folder or project containing the source material you want Claude to use.

If your organization manages plugins, an owner can add this GitHub repository
to the organization's plugin library so members can install it from **Browse
plugins**. Claude plugins are available on paid Claude plans; organization
settings determine who may add or share them.

### Claude Code

Inside Claude Code, run:

```text
/plugin marketplace add multiplai-ai/ai-marketing-os
/plugin install ai-marketing-os@multiplai-marketing
```

Start a new session, then ask in normal language:

> Read the documents in this folder and help me create a content strategy.
> Tell me what information is missing before you begin. Do not publish anything.

Claude can also run a specific workflow, such as
`/ai-marketing-os:content-brief` or `/ai-marketing-os:linkedin-post`.

## Your first useful workflow

Put a business overview, notes, transcript, or other source material in the
folder you share with Claude. Then try:

> Use the content-brief workflow. Create a brief for an article that helps
> [audience] understand [topic]. Use only the supplied files for business claims,
> identify missing evidence, and save the result as a draft. Do not publish it.

Claude will read the workflow, inspect the sources you provided, ask for
important missing information, and create a reviewable output. It should keep
unsupported claims visibly separate from facts.

## Use it with Codex

Codex users can clone the repository and create a separate starter workspace.
Install **Python 3.12, Git, zstd, and Minisign** first; the
[setup guide](docs/member-guide.md#install-prerequisites) has the commands:

```bash
git clone https://github.com/multiplai-ai/ai-marketing-os.git
cd ai-marketing-os
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[publishing]'
python tools/start_member.py --workspace ../my-marketing
```

Open `my-marketing` in Codex. The setup adds three starter skills and a fictional
example without changing your source checkout. See the [member guide](docs/member-guide.md)
for installation details.

## Where are the actual workflows?

The full workflows are in [`sops/`](sops). Each workflow folder contains:

- `SKILL.md` — the instructions Claude or Codex follows
- `sop.yaml` — a small technical record of its inputs, outputs, and maturity

For example, [`sops/content-brief/SKILL.md`](sops/content-brief/SKILL.md) is the
complete content-brief workflow. There is no separate “Core” repository required
to read or use these workflows. “Core” in older files means this shared library.

## A few honest limits

Start with the workflows marked **Good place to start** in the
[workflow library](docs/capabilities.md). Some workflows have not been tested
with every account, connector, operating
system, or business. A workflow may need source files, account access, or a
separate integration. Claude should explain what it needs before taking action.

The GEO suite includes [prompt-set building](sops/geo-prompt-set-builder/SKILL.md),
[answer visibility measurement](sops/geo-share-of-answers/SKILL.md),
[site auditing](sops/geo-audit/SKILL.md),
[citation mapping](sops/geo-citation-network-mapper/SKILL.md),
[page restructuring](sops/geo-content-restructure/SKILL.md), and
[action planning](sops/geo-plan/SKILL.md). Start with your business context and
priority pages; add API measurement only when the inputs and budget are ready.
The inherited third-party reference corpus remains excluded. The source is MIT licensed; AI
subscriptions, APIs, connectors, and third-party services are separate.

## Using the library from a client workspace

Keep the client's facts, voice examples and outputs in its own workspace.
The small skill routers resolve a signed, pinned AI Marketing OS release from
one shared cache outside the client folders. They then read the complete
procedure and supporting files there. A missing or changed installation is an
error: the assistant must stop, show it, and never improvise the missing skill.
Existing users can deliberately restore their previous Core pin if needed;
Core is a rollback source, not a second place to maintain marketing workflows.
See the [cutover and comparison guide](docs/cutover-testing.md).

## Contributing

This repository is the canonical home for shared workflows. Maintainers edit
`sops/<workflow>/SKILL.md`, validate the change, and submit a reviewed pull
request. See [CONTRIBUTING.md](CONTRIBUTING.md).
