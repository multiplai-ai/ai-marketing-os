# YouTube Transcript CLI Reference

## Contents

- [Dependency](#dependency)
- [Command forms](#command-forms)
- [Accepted video references](#accepted-video-references)
- [Options](#options)
- [Single-video examples](#single-video-examples)
- [Batch manifest](#batch-manifest)
- [Markdown output](#markdown-output)
- [Exit behavior](#exit-behavior)

## Dependency

The parsing and formatting functions load without third-party packages. Fetching requires `youtube-transcript-api`:

```bash
python3 -m pip install youtube-transcript-api
```

Verify the installed package without fetching a video:

```bash
python3 -c "from importlib.metadata import version; print(version('youtube-transcript-api'))"
```

## Command Forms

```text
python3 tools/youtube_transcript.py [options] <video_id_or_url> <output_path>
python3 tools/youtube_transcript.py --stdout [options] <video_id_or_url>
python3 tools/youtube_transcript.py --batch <json_file> [options] <output_dir>
```

`--stdout` and `--batch` are mutually exclusive.

## Accepted Video References

- Raw 11-character video ID
- `youtube.com/watch?v=<id>`
- `youtu.be/<id>`
- `youtube.com/embed/<id>`
- `youtube-nocookie.com/embed/<id>`
- `youtube.com/shorts/<id>`
- `youtube.com/live/<id>`
- `youtube.com/v/<id>`
- Mobile and music YouTube watch URLs
- The same recognized hosts without an explicit `https://` scheme

The parser validates the hostname. A non-YouTube URL containing `v=<id>` or a YouTube-looking path is rejected.

## Options

| Option | Meaning |
|---|---|
| `--title TEXT` | Set the Markdown H1 for single-video output. |
| `--timestamp-interval N` | Emit a timestamp marker after at least `N` seconds; positive integer, default `30`. |
| `--stdout` | Print Markdown rather than write a file. |
| `--batch FILE` | Read a JSON list and write one Markdown file per item. |

The fetcher requests English captions in this order: `en`, `en-US`, `en-GB`.

## Single-Video Examples

Write a temporary transcript:

```bash
python3 tools/youtube_transcript.py \
  "https://youtu.be/spNAUEgq_A8" \
  ".tmp/youtube-transcripts/spNAUEgq_A8.md"
```

Set a title and use 60-second timestamp spacing:

```bash
python3 tools/youtube_transcript.py \
  --title "Source interview" \
  --timestamp-interval 60 \
  "spNAUEgq_A8" \
  ".tmp/youtube-transcripts/source-interview.md"
```

Inspect on stdout:

```bash
python3 tools/youtube_transcript.py --stdout "spNAUEgq_A8"
```

Prefer a file for long transcripts so terminal output does not overwhelm the task context.

## Batch Manifest

Use a JSON list. Each item requires `video_id` or `url`; `title` and `slug` are optional.

```json
[
  {
    "url": "https://youtu.be/spNAUEgq_A8",
    "title": "Source interview",
    "slug": "source-interview"
  },
  {
    "video_id": "spNAUEgq_A8",
    "title": "Second source"
  }
]
```

Run it with:

```bash
python3 tools/youtube_transcript.py \
  --batch videos.json \
  ".tmp/youtube-transcripts"
```

Explicit and generated slugs are sanitized before joining the output directory. Duplicate output filenames fail rather than overwrite an earlier item silently. The command continues through the manifest, prints a success/failure total, and exits nonzero if any item fails.

## Markdown Output

Each file contains:

1. A title heading.
2. The validated video ID.
3. A canonical YouTube watch URL.
4. Timestamp markers at the configured interval.
5. Caption text grouped into readable paragraphs.

The tool does not summarize, correct, or enrich caption text.

## Exit Behavior

| Code | Meaning |
|---|---|
| `0` | All requested transcripts were written or printed. |
| `1` | Fetch, input-file, output-write, or one-or-more batch-item failure. |
| `2` | Invalid CLI shape, such as missing positional arguments. |

Recognized fetch failures distinguish disabled captions, no English transcript, and unavailable video. Other client or network errors are reported as failures. No metadata-based fallback occurs.
