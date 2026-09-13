#!/usr/bin/env python3
"""Run mechanically testable human-writing checks without claiming voice authenticity."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


GENERIC_PHRASES = (
    "in today's rapidly evolving landscape",
    "it's no secret that",
    "this is where the magic happens",
    "unlock unprecedented value",
    "game-changer",
)
ENGAGEMENT_BAIT = (
    "like if you agree",
    "comment below",
    "share this with someone",
)
SUMMARY_BOWS = (
    "in conclusion",
    "to sum it all up",
    "at the end of the day",
)


@dataclass(frozen=True)
class GateReport:
    passed: bool
    errors: list[str]
    warnings: list[str]
    metrics: dict[str, int | float]
    positive_signals: list[str]


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def evaluate(text: str) -> GateReport:
    """Evaluate deterministic anti-patterns and observable positive signals."""
    normalized = " ".join(text.lower().split())
    errors: list[str] = []
    warnings: list[str] = []
    sentences = _sentences(text)
    words = re.findall(r"\b[\w'-]+\b", text)
    for phrase in GENERIC_PHRASES:
        if phrase in normalized:
            errors.append(f"generic or synthetic phrase: {phrase}")
    for phrase in ENGAGEMENT_BAIT:
        if phrase in normalized:
            errors.append(f"engagement bait: {phrase}")
    for phrase in SUMMARY_BOWS:
        if phrase in normalized:
            warnings.append(f"possible summary-bow closer: {phrase}")
    contrast = re.search(
        r"\bnot\s+[^.!?]{1,50}[.!?]\s+not\s+[^.!?]{1,50}[.!?]\s+(?:not\s+[^.!?]{1,50}[.!?]\s+)?just\s+",
        text,
        re.IGNORECASE,
    )
    if contrast:
        errors.append("stacked 'not X, not Y, just Z' contrast")
    short_sentences = sum(len(re.findall(r"\b[\w'-]+\b", item)) <= 4 for item in sentences)
    if len(sentences) >= 4 and short_sentences / len(sentences) > 0.6:
        warnings.append("machine-gun rhythm: more than 60% of sentences have four words or fewer")
    paragraph_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    if len(paragraph_lines) >= 6 and sum(len(_sentences(line)) <= 1 for line in paragraph_lines) / len(paragraph_lines) > 0.75:
        warnings.append("repeated one-line paragraph pattern")
    positive: list[str] = []
    if re.search(r"\b\d+(?:[.,]\d+)?(?:%|x|\b)", text, re.IGNORECASE):
        positive.append("specific_number")
    if re.search(r"(?:^|\s)[\"“][^\"”]{3,}[\"”]", text):
        positive.append("source_quote")
    if re.search(r"\b(?:I|we)\s+(?:saw|built|tested|measured|learned|asked|heard|watched|reviewed)\b", text, re.IGNORECASE):
        positive.append("first_person_evidence")
    if re.search(r"\b(?:because|so that|which meant|cost|lost|delayed|blocked|resulted in)\b", text, re.IGNORECASE):
        positive.append("concrete_consequence")
    if len(words) >= 80 and len(positive) < 2:
        warnings.append("few observable grounding signals; compare the draft with its source packet")
    metrics: dict[str, int | float] = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "short_sentence_count": short_sentences,
        "generic_phrase_count": sum("generic or synthetic" in error for error in errors),
    }
    return GateReport(not errors, errors, warnings, metrics, positive)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("file", nargs="?", type=Path)
    source.add_argument("--text")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        text = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    report = evaluate(text)
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        print("PASS" if report.passed else "FAIL")
        for error in report.errors:
            print(f"ERROR: {error}")
        for warning in report.warnings:
            print(f"WARNING: {warning}")
        if report.positive_signals:
            print("POSITIVE: " + ", ".join(report.positive_signals))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
