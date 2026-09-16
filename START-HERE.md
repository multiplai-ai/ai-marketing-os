# Start here

You do not need to read the code in this repository. AI Marketing OS is a
library of instructions that teaches your AI assistant how to approach common
marketing work.

## The basic idea

1. Install the library in Claude or set up a Codex workspace.
2. Give the assistant a folder with useful source material.
3. Describe the outcome you want in normal language.
4. The assistant selects a workflow, tells you what is missing, and creates a draft.
5. You review decisions and approve any action that affects the outside world.

Your source material might include a business overview, customer interviews,
research, brand guidance, a draft article, campaign results, or exported data.
More relevant source material usually produces a better result.

## Choose a first task

| If you want to… | Start with | Ask Claude… |
| --- | --- | --- |
| Clarify your market position | [Strategy Suite](sops/strategy-suite/SKILL.md) | “Review what we already have and guide me through the next missing strategy decision.” |
| Define your best customers | [ICP & Personas](sops/icp-personas/SKILL.md) | “Build our ideal-customer profiles from these interviews and sales notes. Show assumptions separately.” |
| Plan what to publish | [Content Strategy](sops/content-strategy/SKILL.md) | “Create a content strategy from our positioning, customer research, and business goals.” |
| Prepare an article | [Content Brief](sops/content-brief/SKILL.md) | “Turn these sources into a content brief. Flag missing research and unsupported claims.” |
| Write from real source material | [Writing](sops/writing/SKILL.md) | “Draft an article from this transcript and brief. Preserve the speaker’s meaning and voice.” |
| Improve a draft | [Human Writing Standard](sops/human-writing-standard/SKILL.md) | “Review this draft for generic language and claims the sources do not support.” |
| Draft a LinkedIn post | [LinkedIn Post](sops/linkedin-post/SKILL.md) | “Turn this idea into one LinkedIn post for review. Do not publish it.” |
| Review paid advertising | [Ads Audit](sops/ads-audit/SKILL.md) | “Audit these ad exports and explain the three highest-priority problems.” |
| Review a website or landing page | [Landing Page Audit](sops/ads-landing/SKILL.md) | “Compare this page with the promise that sends people there and recommend improvements.” |
| Improve visibility in AI answers | [GEO Audit](sops/geo-audit/SKILL.md) | “Audit these priority pages for AI search visibility. Separate observations from assumptions and give me a 30-day plan.” |

## Install in Claude

In Claude Desktop, Claude on the web, or Cowork, download the newest file whose
name starts with `ai-marketing-os-claude-plugin-` from the repository's
[Releases](https://github.com/multiplai-ai/ai-marketing-os/releases) page. Then
open **Customize → Plugins**, choose the option to upload a custom plugin, and
select the downloaded ZIP file. Installed skills appear in Claude's `/` or `+`
menu. You can select one, or simply describe the task and let Claude choose.

For Claude Code:

```text
/plugin marketplace add multiplai-ai/ai-marketing-os
/plugin install ai-marketing-os@multiplai-marketing
```

## Give Claude a useful working folder

Create a folder for your business or project. Add only the files relevant to
the work. A simple starting folder could look like this:

```text
my-business/
├── business-overview.md
├── customer-notes.md
├── brand-voice.md
└── current-draft.md
```

Open that folder in Cowork or Claude Code. Claude will create outputs there only
when you ask it to. Keep credentials and private keys out of the folder.

## What to expect

The workflows help the assistant work systematically. They do not supply facts
about your business, approve strategy for you, or provide access to marketing
accounts. When evidence is missing, the assistant should ask, label an
assumption, or provide a partial result rather than inventing an answer.

Drafting and publishing are separate. Asking for a brief, article, analysis, or
plan does not authorize the assistant to email, post, schedule, spend money, or
change an account.

## Browse everything

The [workflow library](docs/capabilities.md) groups the available workflows by
the job they help accomplish. Each name links directly to the full instructions.
Start with one workflow and one real task. You do not need to configure the entire library.
