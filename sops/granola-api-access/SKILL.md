---
name: granola-api-access
description: Fetch authorized Granola meeting notes through a consumer-configured API account and optional local helper.
---

# Granola API access

Resolve `{profile_name}`, `{profile_root}`, the selected Granola account and
`{notes_output_dir}` from consumer configuration. If a fetch helper is used,
resolve `{entity_tool:fetch_granola_notes}` and verify its path and CLI. The helper
is not bundled with Core. Ask only for missing required values; never execute
unresolved placeholders or infer an account from examples.

Fetch only notes within the user's authorized scope. Keep note bodies and
transcripts in approved private consumer storage. This runbook does not establish
that the current profile has an active connection.

## API reference and connection verification

Granola's public API base URL is:

```text
https://public-api.granola.ai
```

Do **not** use `https://api.granola.ai` for notes. That host returns `404 {"message":"Not Found"}` for the notes API.

The inherited procedure uses these endpoints. Verify them against the provider documentation or installed connector before relying on them; no current live test is implied:

| Endpoint | Purpose |
|---|---|
| `GET /v1/notes` | List accessible notes, paginated; supports date filters. |
| `GET /v1/notes/{note_id}` | Fetch a single note with metadata, summary, transcript, attendees, and calendar event details. |
| `GET /v1/folders` | List accessible folders, paginated. |

Auth header:

```http
Authorization: Bearer <GRANOLA_API_KEY>
```

The profile env var is:

```dotenv
GRANOLA_API_KEY=<redacted>
```

Store it through the consumer's protected credential mechanism or profile environment, never in shared source.

## Hermes profile configuration

For the selected consumer profile:

```bash
hermes -p {profile_name} config env-path
# {profile_root}/.env
```

Add the key to that file if missing:

```dotenv
GRANOLA_API_KEY=grn_...
```

If an authorized configuration change requires reloading the process environment, use the installed runtime's supported scoped restart; inspect help first:

```bash
hermes -p {profile_name} gateway restart
```

For specialist profiles that need their own Granola access, repeat in that profile's `.env` only if the credential scope permits it. Do not copy owner/private meeting-note access into client specialists by default.

## Smoke test

Use a no-secret smoke test from a Hermes terminal session:

```bash
python3 - <<'PY'
import json, os, urllib.request
key = os.environ.get('GRANOLA_API_KEY')
print('GRANOLA_API_KEY present:', bool(key))
if key:
    req = urllib.request.Request(
        'https://public-api.granola.ai/v1/notes?page_size=1',
        headers={'Authorization': 'Bearer ' + key, 'User-Agent': 'Hermes Granola smoke test'},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())
    print(json.dumps({
        'status': 'ok',
        'notes_count': len(data.get('notes', [])),
        'hasMore': data.get('hasMore'),
        'fields': sorted(data.keys()),
    }, indent=2))
PY
```

Expected: key present, HTTP 200, and JSON fields `notes`, `hasMore`, and `cursor`.

## Fetching notes for an operating day

If the consumer helper is installed and supports these flags, resolve its path and the requested date window before using this pattern:

```bash
python3 {entity_tool:fetch_granola_notes} \
  --created-after {created_after_utc} \
  --out-json {notes_output_dir}/granola-notes.json \
  --out-md {notes_output_dir}/granola-notes.md
```

Verify the configured helper:
- reads `GRANOLA_API_KEY` from the environment;
- uses the intended account's protected credential source;
- pages through `GET /v1/notes`;
- fetches each detail via `GET /v1/notes/{note_id}`;
- writes raw JSON and a readable Markdown summary only to the approved output directory.

Use the consumer's retention policy for fetched notes and transcripts. Verify the output is excluded from Git before writing inside a checkout. Do not upload raw notes to other applications unless the task authorizes that destination.

## Query parameters to use

Useful list-note params from docs:

| Param | Notes |
|---|---|
| `created_after` | ISO date or datetime. Convert the consumer timezone's day boundaries to UTC. |
| `created_before` | ISO date or datetime. |
| `updated_after` | Use for incremental sync jobs. |
| `updated_before` | Use for bounded backfills. |
| `cursor` | Continue pagination when `hasMore` is true. |
| `page_size` | Page size; default from docs is small, so set explicitly for batch pulls. |

Honor the current provider rate-limit response and any `Retry-After` header. Bound retries and report an incomplete fetch; do not assume historical rate limits still apply.

## Operational notes

- List Notes excludes notes that have not generated a summary/transcript yet; Get Note may return 404 for notes still processing or never summarized.
- Preserve `web_url` in any task body or Notion source note so owner can click back to the source Granola note.
- If task capture is authorized, resolve the configured destination and create only owner-owned or owner-follow-up tasks. Otherwise draft proposed tasks. Do not capture every attendee's commitments into the owner's board.
- If a Granola task creation workflow is used repeatedly, make the extraction idempotent by searching Notion for an existing title/source URL before creating pages.

## Example cURL

```bash
curl --request GET \
  --url 'https://public-api.granola.ai/v1/notes?created_after={created_after_utc}&page_size=20' \
  --header "Authorization: Bearer ${GRANOLA_API_KEY}"
```
