---
name: morning-brief-setup
description: Configure or restore a consumer-owned daily and weekly morning brief with verified data sources and delivery settings.
---

# Morning Brief System — Setup Runbook

Configure a reusable weekly operating board that a daily brief can refresh.
This is a setup procedure, not a record of any running installation. No account,
connection, schedule or delivery destination is presumed live.

## Resolve the consumer configuration

Reuse values already supplied in the task or consumer bindings. Resolve only the
connections this task needs:

- `{profile_root}`, the selected runtime/profile and its supported CLI;
- `{timezone}`, requested daily/weekly schedules and selected model;
- `{planning_page_id}`, `{planning_page_url}`, `{notion_integration_name}`;
- `{calendar_accounts}` and the separately configured token path for each account;
- optional `{meeting_notes_database_id}`, `{meeting_notes_data_source_id}` and
  `{linear_team_id}`;
- optional `{delivery_destination}` and permission to deliver messages there.

Keep token contents and account records out of this shared source and generated
reports. Never run an unresolved placeholder or guess which account to use.
Ask for missing required values; skip optional integrations with a clear note.
Respect the consumer's communication policy. Setting up a brief does not itself
authorize sending messages, creating tasks or enabling recurring writes.

## Verify connections before rebuilding

Inspect existing jobs before creating replacements. Record each relevant job's
name, schedule, timezone, destination and last known result in the consumer's
private setup record. Preserve existing working jobs until a replacement is
verified; do not create duplicates.

Use read-only checks to verify the selected calendar accounts, Notion parent
page and optional task/meeting-note sources. Record each as `verified`, `not
configured`, `access denied` or `failed`, with the check time. Check available
CLI help or connector schemas before using an integration; this repository does
not ship the Google Workspace helper used by some consumer installations.

For Google OAuth, use the consumer's own cloud project and registered client.
Keep each account's token separate. If authorization is missing or expired,
report the affected connection and have the owner complete its provider flow.
Do not copy tokens between identities as a repair.

For Notion, inspect the actual properties and accessible data sources. With an
API that supports data sources, fetch the database metadata and select the
intended data source explicitly before querying it. Do not assume the first
source is correct. Use the installed connector's supported API version.

Meeting-note date fields vary: select the configured meeting date, or disclose
created-time filtering as a fallback. Do not infer that a particular property
exists from another installation.

## Build the operating board

The consumer chooses its workweek, domains and timezone. Resolve the date range
using that timezone, including daylight-saving transitions; do not hardcode a
UTC offset. A typical board uses weekdays as columns and major calendar items
plus the consumer's work domains as rows.

1. Determine the week to prepare. Search under the configured parent for the
   corresponding board before creating a page.
2. Pull the requested calendar range from verified accounts. Include both timed
   and all-day events. Preserve date-only all-day values; do not invent times.
3. Deduplicate shared events by ID, then normalized title/start/end where useful.
   Retain the configured calendar/domain labels.
4. Pull relevant tasks from the configured team, following pagination. Include
   due, overdue, blocked or in-progress items that affect the requested week.
5. Exclude generic calendar blockers while retaining real named appointments.
6. Preserve manual edits, checked items and prior-day cells when refreshing.
7. If task synchronization is authorized, resolve checked task identifiers and
   meeting actions to the correct team, search for duplicates, then apply only
   the permitted updates. Otherwise prepare suggested changes for review.
8. Generate the board or preview with a source-refresh time and explicit missing
   sources. Do not describe unavailable sources as successfully refreshed.

Keep the daily procedure canonical in `sops/daily-brief-cron-prompt/SKILL.md`.
Resolve its consumer bindings before using it; do not maintain a second shared
copy of that procedure in a profile or this setup runbook. Consumer-specific
schedule/configuration belongs in the consumer repository.

## Enable and verify only the requested automation

Use the selected runtime's supported scheduler. Resolve the job prompt, timezone,
schedule, model, profile and destination before creating or updating a job.
A recurring schedule must be explicitly requested or already authorized. Prefer
updating the matching existing job to creating a duplicate.

Run a local preview first. If page writes are authorized, verify the resulting
board exists and contains the intended content. Test external delivery only
when permitted by the user's communication rules; otherwise return its exact
draft. A short link notification can be used when requested, but never claim a
board is ready if page creation or verification failed.

Report the verified setup, unresolved connections, next scheduled run and whether
external delivery was tested. An untested connection remains unverified. On
failure, preserve the last working configuration and report the failed step
without deleting unrelated jobs or changing account access.
