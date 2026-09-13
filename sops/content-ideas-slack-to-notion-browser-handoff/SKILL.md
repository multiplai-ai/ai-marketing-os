---
name: content-ideas-slack-to-notion-browser-handoff
description: Set up a Slack-to-Notion content intake workflow and next-day mini briefs using consumer-configured channels and databases.
---

# Codex handoff: Slack `{slack_channel_name}` → Notion Content Pipeline → next-day mini briefs

Resolve `{slack_workspace_id}`, `{slack_channel_id}`, `{slack_channel_name}`,
`{content_pipeline_database_id}`, `{content_pipeline_data_source_id}`,
`{content_pipeline_url}` and `{notion_integration_name}` from the consumer's
configuration or supplied context. Resolve a schedule/timezone only if recurring
brief generation is requested. Reuse known values; ask for missing required
ones. Never execute unresolved placeholders or infer a destination from examples.

Start by verifying the selected Slack workspace/channel and Notion database with
read-only access. No connection or recurring job is presumed live. Inspect
existing automation before creating a replacement. Configure external writes
only within the user's authorization and communication policy. A test message
must be posted by the user when that policy prohibits sending on their behalf.

## Goal

Set up an intake workflow so every message posted to Slack `{slack_channel_name}` becomes a Notion Content Pipeline row with the correct capture status for the brief agent to generate mini briefs the next day.

Desired end state:

1. The owner or team posts an idea in Slack `{slack_channel_name}`.
2. Automation creates a Notion Content Pipeline item.
3. The item is marked `Stage = Mini Brief Needed` and contains the raw Slack message plus source link.
4. The brief agent's next-day cron processes those rows, writes a structured mini brief, and updates them to `Stage = Briefed`.
5. Content planning happens from Notion, not Slack.

## Ownership / scope

- **Codex task:** Use browser control to configure the Slack-side automation and Notion views/properties as needed.
- **Brief agent task after setup:** Verify Notion rows are being created correctly and wire/update the brief agent mini-brief cron if it is not already live.
- **Source of truth:** Notion Content Pipeline.
- **Capture surface:** Slack `{slack_channel_name}`.

Reuse the configured Content Pipeline. An inaccessible database is a connection blocker, not permission to create a replacement.

## Existing Notion target

Use the canonical Content Pipeline database:

- **Database ID:** `{content_pipeline_database_id}`
- **Data source ID:** `{content_pipeline_data_source_id}`
- **Known URL:** `{content_pipeline_url}`
- **Integration:** `{notion_integration_name}`

Map these intended semantics onto the verified database properties:

- Slack content ideas should be created/updated here.
- Use `Source = Slack Intake`.
- Use `Intake Channel = Slack {slack_channel_name}` or the actual Slack channel ID if the schema expects it.
- Use `Raw Idea` for the original Slack message text.
- Use `Mini Brief` for the brief agent's structured brief.
- Leave `Target Publish Date` blank until owner schedules the idea.

## Required Notion field mapping

When a Slack message is captured, create a Notion item with these values:

| Notion field | Capture value |
|---|---|
| Title / `Post Idea` / `Name` | Short title from the message. If no AI title step exists, use first ~80 characters. |
| `Stage` | `Mini Brief Needed` |
| `Source` | `Slack Intake` |
| `Intake Channel` | `Slack {slack_channel_name}` or actual channel ID |
| `Raw Idea` | Full Slack message text |
| `Source Link` | Slack permalink, if the automation tool exposes it |
| `Brief Created` | `false` |
| `Ready for Calendar` | `false` |
| `Target Publish Date` | blank |
| `Mini Brief` | blank |
| `Needs owner` | blank/false unless the message explicitly asks for owner input |

Important: the Slack capture automation must **not** set `Stage = Briefed`. `Briefed` means the brief agent has already produced a mini brief. New Slack captures should land as `Mini Brief Needed`.

## Preferred browser-control implementation

Use one of these, in order of preference based on what owner already has logged in and available in the browser:

1. **Zapier** — fastest if owner already has Slack + Notion connected.
2. **Make** — good if available and easier to inspect mappings.
3. **n8n** — best if owner wants more durable/self-hosted control, but only if an n8n workspace is already available.
4. **Slack Workflow Builder** — acceptable if it can write to Notion directly in this workspace; otherwise use it only to call a webhook.

### MVP Zapier / Make pattern

Trigger:

```text
Slack: New message posted to channel
Channel: {slack_channel_id}
```

Action:

```text
Notion: Create database item
Database: Content Pipeline
```

Optional intermediate step:

```text
Formatter / AI step: generate short title from Slack message text
```

Use the Slack workspace, channel and message timestamp as an intake identity. Check whether the automation retries deliveries and prevent duplicate Notion rows for the same message. Keep classification and drafting in the separate brief step.

## Browser-control steps for Codex

### 1. Inspect Notion first

Using the browser:

1. Open the Content Pipeline URL: `{content_pipeline_url}`.
2. Confirm it is the content/social pipeline owner expects.
3. Inspect the database properties and exact option names.
4. Confirm the `Stage` options include at least:
   - `Mini Brief Needed`
   - `Briefed`
5. Confirm the following properties exist or identify equivalents:
   - `Raw Idea`
   - `Mini Brief`
   - `Source`
   - `Intake Channel`
   - `Brief Created`
   - `Ready for Calendar`
   - `Source Link`
   - `Target Publish Date`

If setup authorization includes schema changes, add missing properties to the existing database. Otherwise report the proposed changes. Suggested property types:

| Property | Type |
|---|---|
| `Raw Idea` | Text / rich text |
| `Mini Brief` | Text / rich text |
| `Source` | Select |
| `Intake Channel` | Select or text |
| `Brief Created` | Checkbox |
| `Ready for Calendar` | Checkbox |
| `Source Link` | URL |
| `Target Publish Date` | Date |

### 2. Create or inspect Notion views

In Notion UI, create or confirm these views:

1. `Slack Intake`
   - Filter: `Source = Slack Intake`
2. `Mini Brief Needed`
   - Filter: `Stage = Mini Brief Needed`
3. `Briefed Ideas`
   - Filter: `Stage = Briefed`
4. `Calendar Ready`
   - Filter: `Ready for Calendar = true`
5. `Publishing Calendar`
   - Calendar view using `Target Publish Date`

Inspect the available connector capabilities; use browser control when it does not support saved views.

### 3. Configure Slack → Notion automation

In Zapier/Make/n8n using browser control:

1. Select the Slack account/workspace.
2. Trigger on new messages in `{slack_channel_name}`.
3. Exclude bot messages if the tool offers that option, to avoid loops.
4. Connect Notion.
5. Select the Content Pipeline database.
6. Map fields exactly per the table above.
7. Enable the workflow only when recurring capture is authorized and the test item verifies correctly. Record the confirmed workspace, channel and database in the consumer setup record.

### 4. Test with a harmless Slack message

Have the owner post a test message, or post only if their communication policy and explicit authorization permit it, in `{slack_channel_name}`, for example:

```text
Test intake for the mini-brief workflow: AI agents need better briefing queues, not just more prompts.
```

Then verify in Notion:

- A new row exists in Content Pipeline.
- `Stage = Mini Brief Needed`.
- `Source = Slack Intake`.
- `Raw Idea` contains the full Slack text.
- `Source Link` is populated if the automation supports permalinks.
- `Brief Created = false`.
- `Ready for Calendar = false`.
- `Mini Brief` is blank.

After verification, either delete/archive the test row or leave it clearly marked as test. Ask owner before deleting anything if it is not obviously a disposable test.

## Next-day mini-brief behavior

If recurring mini-brief generation is authorized, configure the requested schedule and timezone. Reuse the matching job and process Content Pipeline rows matching:

- `Stage = Mini Brief Needed`
- `Brief Created = false`
- Prefer `Source = Slack Intake`, but allow blank source if context clearly came from the Slack intake automation
- Exclude terminal stages such as `Published`, `Archived`, `Cancelled`, `Live`

For each usable row, the brief agent should write this structure into `Mini Brief`:

```md
## Mini Brief

### Core Idea
<one-sentence framing>

### Target Audience
<who this is for>

### Angle
<why this matters / owner or brand point of view>

### Hook Options
- <hook 1>
- <hook 2>
- <hook 3>

### Supporting Points / Examples
- <supporting detail>
- <supporting detail>

### Suggested Channel
<LinkedIn / X / newsletter / blog / other>

### CTA
<what the reader should do or think next>
```

Then update:

| Field | Value after mini brief |
|---|---|
| `Stage` | `Briefed` |
| `Mini Brief` | populated |
| `Brief Created` | `true` |
| `Ready for Calendar` | `true` if usable for planning |
| `Last Agent Touch` | today, if property exists |

If the row is too vague to brief:

- Keep `Stage = Mini Brief Needed` or move to a clarification status if one exists.
- Set `Needs owner = true`, if the property exists.
- Add a short note explaining what context is missing.

## Status semantics

Use these definitions consistently:

| Stage | Meaning |
|---|---|
| `Mini Brief Needed` | Raw idea captured; the brief agent should process it. |
| `Briefed` | the brief agent generated a usable mini brief. |
| `Ready to Draft` | A human/agent can draft a post from the brief. |
| `Ready to Schedule` | Draft exists and can be scheduled. |
| `Scheduled` | Publish date selected. |
| `Published` | Published. |
| `Archived` | Not using. |

Again: Slack automation creates `Mini Brief Needed`; the brief agent creates `Briefed`.

## Verification checklist before closing

Codex should report back with:

- Automation platform used: Zapier / Make / n8n / Slack Workflow Builder / other.
- Slack trigger channel confirmed: `{slack_channel_name}`.
- Notion target database confirmed: Content Pipeline.
- Exact mapped fields.
- Link or screenshot path for the automation configuration, if available.
- Link to the test Notion row.
- Whether the test row was left in place, archived, or deleted.
- Any fields that were missing and had to be created.
- Any blocker requiring owner, especially login/OAuth/permission prompts.

## Common blockers

### Notion database not visible in the automation tool

Likely the Notion integration connected to Zapier/Make/n8n does not have access to the Content Pipeline database.

Fix in Notion:

1. Open Content Pipeline.
2. Click `...`.
3. Go to `Connections` / `Connect to`.
4. Add the relevant Notion integration for the automation tool.

Do not create a new database as a workaround unless owner approves it.

### Notion API / Hermes cannot see the database

Make sure Content Pipeline is connected to `{notion_integration_name}`.

### Slack channel not available in Zapier/Make

Possible causes:

- The Slack app is not installed in the workspace.
- The Slack app is not invited to the private channel.
- The channel is private and hidden from the integration.

Fix: have the owner connect the intended app to the configured channel. Do not broaden channel visibility or switch to a public channel as an access workaround.

### Slack permalink not available

Proceed without it for MVP if necessary. Put Slack timestamp/channel/user into the Notion page body or `Raw Idea` field if available. Source link is useful, not worth blocking setup.

### Thread replies vs. top-level messages

MVP should capture top-level messages in `{slack_channel_name}`. If thread replies contain important context, configure the automation to include them only if the platform supports it cleanly. Otherwise the brief agent can use the raw top-level idea and owner can paste extra context into the same Notion row later.

## Do not do

- Do not set captured ideas to `Briefed` before the brief agent writes a mini brief.
- Do not create a parallel content database without first inspecting the existing Content Pipeline.
- Do not make Slack the source of truth.
- Do not auto-draft or auto-schedule posts from this intake automation.
- Do not send or publish content externally.
- Do not delete real rows/messages without owner approval.

## Handoff summary for Codex prompt

Use this as the concise instruction if starting Codex fresh:

```text
Use browser control to set up Slack {slack_channel_name} intake into the existing Notion Content Pipeline.

Target Notion database: {content_pipeline_url}
Database ID: {content_pipeline_database_id}
Data source ID: {content_pipeline_data_source_id}

Configure Slack new-message automation for {slack_channel_name} using Zapier/Make/n8n/Slack Workflow Builder, whichever owner has available in browser.

Each Slack message should create a Notion row with:
- Stage = Mini Brief Needed
- Source = Slack Intake
- Intake Channel = Slack {slack_channel_name}
- Raw Idea = full Slack message text
- Source Link = Slack permalink if available
- Brief Created = false
- Ready for Calendar = false
- Mini Brief blank
- Target Publish Date blank

Inspect Notion first and reuse existing fields/options. Add missing properties only in the existing database. Create or confirm views: Slack Intake, Mini Brief Needed, Briefed Ideas, Calendar Ready, Publishing Calendar.

Have the user supply one harmless Slack test message unless agent sending is explicitly permitted, and verify the Notion row. Report the automation platform used, field mappings, test row link, and blockers. Do not publish, schedule, delete real content, or create a parallel Notion database without owner approval.
```
