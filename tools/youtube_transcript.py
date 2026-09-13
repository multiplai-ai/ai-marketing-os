#!/usr/bin/env python3
"""Fetch YouTube transcripts and render source-faithful Markdown.

Usage:
    python3 tools/youtube_transcript.py <video_id_or_url> <output_path>
    python3 tools/youtube_transcript.py --stdout <video_id_or_url>
    python3 tools/youtube_transcript.py --batch <json_file> <output_dir>

Requires: python3 -m pip install youtube-transcript-api
"""

import argparse
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import parse_qs, urlparse

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
SCHEMELESS_YOUTUBE_RE = re.compile(
    r"^(?:(?:www|m|music)\.)?youtube\.com(?:/|$)"
    r"|^(?:www\.)?youtube-nocookie\.com(?:/|$)"
    r"|^youtu\.be(?:/|$)",
    re.IGNORECASE,
)
YOUTUBE_HOSTS = {
    "youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtube-nocookie.com",
}
YOUTUBE_PATH_PREFIXES = {"embed", "shorts", "live", "v"}
YouTubeTranscriptApi = None


def extract_video_id(video_ref: str) -> str:
    """Return the video ID from a raw ID or a supported YouTube URL."""
    if not isinstance(video_ref, str):
        raise ValueError("YouTube video reference must be a string")

    video_ref = video_ref.strip()
    if VIDEO_ID_RE.fullmatch(video_ref):
        return video_ref

    candidate = video_ref
    if SCHEMELESS_YOUTUBE_RE.search(candidate):
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"Could not extract YouTube video ID from: {video_ref}")

    host = parsed.hostname.lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    path_parts = [part for part in parsed.path.split("/") if part]

    if host in YOUTUBE_HOSTS:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if VIDEO_ID_RE.fullmatch(query_id):
            return query_id
        if (
            len(path_parts) > 1
            and path_parts[0] in YOUTUBE_PATH_PREFIXES
            and VIDEO_ID_RE.fullmatch(path_parts[1])
        ):
            return path_parts[1]

    if host == "youtu.be" and path_parts and VIDEO_ID_RE.fullmatch(path_parts[0]):
        return path_parts[0]

    raise ValueError(f"Could not extract YouTube video ID from: {video_ref}")


def get_transcript_api():
    """Load youtube-transcript-api lazily so local parsing needs no dependency."""
    global YouTubeTranscriptApi
    if YouTubeTranscriptApi is not None:
        return YouTubeTranscriptApi
    try:
        from youtube_transcript_api import YouTubeTranscriptApi as Api
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: python3 -m pip install youtube-transcript-api"
        ) from exc
    YouTubeTranscriptApi = Api
    return YouTubeTranscriptApi


def _normalize_segment(segment) -> dict:
    """Normalize object- and mapping-style transcript client responses."""
    if isinstance(segment, Mapping):
        text = segment["text"]
        start = segment["start"]
        duration = segment["duration"]
    else:
        text = segment.text
        start = segment.start
        duration = segment.duration
    return {"text": str(text), "start": float(start), "duration": float(duration)}


def fetch_transcript(video_ref: str) -> list[dict]:
    """Fetch English transcript rows for a YouTube ID or URL."""
    video_id = extract_video_id(video_ref)
    fetched = get_transcript_api()().fetch(
        video_id, languages=["en", "en-US", "en-GB"]
    )
    return [_normalize_segment(segment) for segment in fetched]


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS or MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def to_markdown(
    segments: list[dict],
    video_id: str,
    title: str = "",
    timestamp_interval: int = 30,
) -> str:
    """Render transcript rows as Markdown with periodic source timestamps."""
    if timestamp_interval <= 0:
        raise ValueError("timestamp_interval must be a positive integer")
    video_id = extract_video_id(video_id)
    heading = " ".join(str(title or video_id).split()) or video_id
    lines = [
        f"# {heading}",
        "",
        f"**Video ID:** `{video_id}`",
        f"**URL:** https://www.youtube.com/watch?v={video_id}",
        "",
        "---",
        "",
    ]

    current_paragraph = []
    last_stamp = None
    for segment in segments:
        text = str(segment["text"]).replace("\n", " ").strip()
        if not text:
            continue
        start = float(segment["start"])
        if last_stamp is None or start - last_stamp >= timestamp_interval:
            if current_paragraph:
                lines.extend([" ".join(current_paragraph), ""])
                current_paragraph = []
            lines.append(f"**[{format_timestamp(start)}]**")
            last_stamp = start
        current_paragraph.append(text)

    if current_paragraph:
        lines.append(" ".join(current_paragraph))
    return "\n".join(lines) + "\n"


def slugify(text: str) -> str:
    """Turn a label into a filename-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", str(text).lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")[:80]


def _fetch_error(video_id: str, error: Exception) -> str:
    messages = {
        "TranscriptsDisabled": "transcripts disabled",
        "NoTranscriptFound": "no English transcript found",
        "VideoUnavailable": "video unavailable",
    }
    detail = messages.get(type(error).__name__)
    if detail:
        return f"SKIP {video_id}: {detail}"
    return f"FAIL {video_id}: {error}"


def process_video(
    video_ref: str,
    output_path: Path,
    title: str = "",
    timestamp_interval: int = 30,
) -> bool:
    """Fetch and save one transcript; return whether it succeeded."""
    try:
        video_id = extract_video_id(video_ref)
    except ValueError as exc:
        print(f"  FAIL {video_ref}: {exc}", file=sys.stderr)
        return False

    try:
        segments = fetch_transcript(video_id)
    except Exception as exc:
        print(f"  {_fetch_error(video_id, exc)}", file=sys.stderr)
        return False

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            to_markdown(segments, video_id, title, timestamp_interval),
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        print(f"  FAIL {video_id}: could not write {output_path}: {exc}", file=sys.stderr)
        return False

    print(f"  OK   {video_id} -> {output_path.name} ({len(segments)} segments)")
    return True


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _load_batch(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read batch JSON {path}: {exc}") from exc
    if not isinstance(payload, list):
        raise ValueError("batch JSON must be a list of objects")
    if any(not isinstance(item, dict) for item in payload):
        raise ValueError("every batch item must be an object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--batch", type=Path, help="JSON list of {video_id|url, title?, slug?}"
    )
    mode.add_argument("--stdout", action="store_true", help="Print Markdown to stdout")
    parser.add_argument("--title", default="", help="Title for single-video output")
    parser.add_argument(
        "--timestamp-interval",
        type=_positive_int,
        default=30,
        help="Positive seconds between timestamp markers (default: 30)",
    )
    parser.add_argument(
        "args", nargs="*", help="Single: <video_id_or_url> <output_path>"
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    opts = parser.parse_args(argv)

    if opts.batch:
        if len(opts.args) != 1:
            print("ERROR: --batch requires one output_dir", file=sys.stderr)
            return 2
        try:
            items = _load_batch(opts.batch)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

        output_dir = Path(opts.args[0])
        successes = failures = 0
        seen_paths = set()
        for index, item in enumerate(items, 1):
            video_ref = item.get("video_id") or item.get("url")
            if not isinstance(video_ref, str) or not video_ref.strip():
                print(f"  FAIL batch item {index}: missing video_id or url", file=sys.stderr)
                failures += 1
                continue
            title = item.get("title") or video_ref
            if not isinstance(title, str):
                print(f"  FAIL batch item {index}: title must be a string", file=sys.stderr)
                failures += 1
                continue
            slug_source = item.get("slug") or title
            slug = slugify(slug_source) or f"video-{index}"
            output_path = output_dir / f"{slug}.md"
            if output_path in seen_paths:
                print(f"  FAIL batch item {index}: duplicate output {output_path.name}", file=sys.stderr)
                failures += 1
                continue
            seen_paths.add(output_path)
            if process_video(
                video_ref, output_path, title, opts.timestamp_interval
            ):
                successes += 1
            else:
                failures += 1
        print(f"\nDone: {successes} ok, {failures} failed")
        return 0 if failures == 0 else 1

    if opts.stdout:
        if len(opts.args) != 1:
            print("ERROR: --stdout requires one video ID or URL", file=sys.stderr)
            return 2
        try:
            video_id = extract_video_id(opts.args[0])
            segments = fetch_transcript(video_id)
            markdown = to_markdown(
                segments, video_id, opts.title, opts.timestamp_interval
            )
        except Exception as exc:
            reference = opts.args[0]
            try:
                reference = extract_video_id(reference)
            except ValueError:
                pass
            print(f"FAIL {reference}: {exc}", file=sys.stderr)
            return 1
        print(markdown, end="")
        return 0

    if len(opts.args) != 2:
        parser.print_help(sys.stderr)
        return 2
    video_ref, output_path = opts.args[0], Path(opts.args[1])
    return 0 if process_video(
        video_ref, output_path, opts.title, opts.timestamp_interval
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
