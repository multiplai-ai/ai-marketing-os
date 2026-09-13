#!/usr/bin/env python3
"""Preserve supplied writing evidence in a portable editorial source packet."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

from writing_config import load_yaml, validate_document


CAPTURE_QUESTIONS = {
    "thesis": "What is the one argument you want this piece to make?",
    "trigger": "What happened or changed that made this worth writing now?",
    "tension": "What contradiction, disagreement, or unresolved pressure gives the idea energy?",
    "stakes": "What concrete consequence follows if the reader gets this wrong?",
    "reader_outcome": "What should the reader understand, decide, or do afterward?",
}


def _items(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def extract_source_packet(voice_input: str, answers: dict) -> dict:
    """Build a packet from supplied fields; do not synthesize unsupported prose."""
    supplied_refs = _items(answers.get("source_input_refs"))
    source_ref = str(answers.get("source_ref") or (supplied_refs[0] if supplied_refs else "inline-voice-input"))
    quoted = re.findall(r'["“]([^"”]{3,})["”]', voice_input or "")
    exact_phrases = _items(answers.get("exact_phrases"))
    if not exact_phrases:
        exact_phrases = [
            {"id": f"phrase-{index}", "text": text.strip(), "source_ref": source_ref}
            for index, text in enumerate(quoted, 1)
        ]
    evidence = []
    for index, item in enumerate(_items(answers.get("firsthand_evidence")), 1):
        if isinstance(item, dict):
            evidence.append(item)
        elif str(item).strip():
            evidence.append({"id": f"evidence-{index}", "summary": str(item).strip(), "source_ref": source_ref, "sensitivity": "unknown"})
    claims = []
    for index, item in enumerate(_items(answers.get("claims")), 1):
        if isinstance(item, dict):
            claims.append(item)
        elif str(item).strip():
            claims.append({"id": f"claim-{index}", "text": str(item).strip(), "support_status": "unresolved", "evidence_refs": [], "attribution": ""})
    return {
        "schema_version": 1,
        "topic_or_assignment": str(answers.get("topic_or_assignment") or "").strip(),
        "source_input_refs": [str(item) for item in (supplied_refs or [source_ref])],
        "thesis": str(answers.get("thesis") or "").strip(),
        "trigger": str(answers.get("trigger") or "").strip(),
        "tension": str(answers.get("tension") or "").strip(),
        "stakes": str(answers.get("stakes") or "").strip(),
        "exact_phrases": exact_phrases,
        "firsthand_evidence": evidence,
        "claims": claims,
        "counterargument": str(answers.get("counterargument") or "").strip(),
        "reader_outcome": str(answers.get("reader_outcome") or "").strip(),
        "cutting_room": [str(item) for item in _items(answers.get("cutting_room"))],
        "sensitive_details": [str(item) for item in _items(answers.get("sensitive_details"))],
    }


def missing_capture_questions(packet: dict) -> list[str]:
    """Return only questions for missing core capture areas."""
    return [question for field, question in CAPTURE_QUESTIONS.items() if not str(packet.get(field, "")).strip()]


def validate_source_packet(packet: dict) -> list[str]:
    errors = validate_document("writing-source-packet.schema.yaml", packet)
    if errors:
        return errors
    groups = {
        "exact_phrases": [item["id"] for item in packet["exact_phrases"]],
        "firsthand_evidence": [item["id"] for item in packet["firsthand_evidence"]],
        "claims": [item["id"] for item in packet["claims"]],
    }
    for label, ids in groups.items():
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: duplicate IDs are not allowed")
    source_refs = set(packet["source_input_refs"])
    for phrase in packet["exact_phrases"]:
        if phrase["source_ref"] not in source_refs:
            errors.append(f"exact_phrases.{phrase['id']}: unknown source_ref {phrase['source_ref']}")
    evidence_ids = set(groups["firsthand_evidence"])
    for evidence in packet["firsthand_evidence"]:
        if evidence["source_ref"] not in source_refs:
            errors.append(f"firsthand_evidence.{evidence['id']}: unknown source_ref {evidence['source_ref']}")
    known_evidence = source_refs | evidence_ids
    for claim in packet["claims"]:
        unknown = set(claim["evidence_refs"]) - known_evidence
        if unknown:
            errors.append(f"claims.{claim['id']}: unknown evidence refs: {', '.join(sorted(unknown))}")
        if claim["support_status"] == "verified" and not claim["evidence_refs"]:
            errors.append(f"claims.{claim['id']}: verified claims require evidence_refs")
        if claim["support_status"] == "verified" and not claim["attribution"].strip():
            errors.append(f"claims.{claim['id']}: verified claims require attribution")
    return errors


def validate_render_request(root: Path, request: dict, catalog: dict) -> list[str]:
    """Validate a V1 request and reject social rendering."""
    errors = validate_document("writing-render-request.schema.yaml", request)
    assets = {item.get("id"): item for item in catalog.get("asset_types", []) if isinstance(item, dict)}
    selected = assets.get(request.get("asset_type_id"))
    if selected is None:
        errors.append(f"asset_type_id: unknown asset type: {request.get('asset_type_id', '')}")
    elif selected.get("kind") != "long_form":
        errors.append("asset_type_id: Writing V1 renders long_form assets only")
    for field in ("source_packet_ref", "output_path"):
        value = request.get(field)
        if isinstance(value, str):
            candidate = (root.resolve() / value).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{field}: path escapes consumer root")
    return errors


def validate_article_frontmatter(frontmatter: dict) -> list[str]:
    """Validate the portable fields at the top of a long-form artifact."""
    return validate_document("writing-article.schema.yaml", frontmatter)


def validate_handoff(handoff: dict, packet: dict | None = None) -> list[str]:
    """Validate handoff shape, readiness claims, and optional packet references."""
    errors = validate_document("writing-handoff.schema.yaml", handoff)
    if errors:
        return errors
    landing = handoff["landing_audit"]
    readiness = handoff["readiness"]
    landing_required = {
        "destination_url": landing["destination_url"],
        "entry_message": landing["entry_message"],
        "target_audience": landing["target_audience"],
        "expected_offer": landing["expected_offer"],
        "expected_cta": landing["expected_cta"],
        "expected_proof": landing["expected_proof"],
    }
    missing = [field for field, value in landing_required.items() if not value]
    if readiness["landing_audit_ready"] and missing:
        errors.append("readiness.landing_audit_ready: true with missing " + ", ".join(missing))
    if not landing["destination_url"] and readiness["landing_audit_ready"]:
        errors.append("readiness.landing_audit_ready: destination URL is required")
    if not landing["destination_url"] and not readiness["blockers"]:
        errors.append("readiness.blockers: explain the missing destination URL")
    destination_url = handoff["destination"]["url"]
    if destination_url and landing["destination_url"] and destination_url != landing["destination_url"]:
        errors.append("destination.url and landing_audit.destination_url must match")
    if readiness["linkedin_ready"] and not handoff["social_angle_candidates"]:
        errors.append("readiness.linkedin_ready: at least one social angle candidate is required")
    if packet is not None:
        claim_ids = {item.get("id") for item in packet.get("claims", [])}
        phrase_ids = {item.get("id") for item in packet.get("exact_phrases", [])}
        used_claims = set(handoff["message"]["supporting_claim_ids"])
        used_phrases = set(handoff["message"]["exact_phrase_ids"])
        for angle in handoff["social_angle_candidates"]:
            used_claims.update(angle["claim_ids"])
            used_phrases.update(angle["exact_phrase_ids"])
        if used_claims - claim_ids:
            errors.append("handoff references unknown claim IDs: " + ", ".join(sorted(used_claims - claim_ids)))
        if used_phrases - phrase_ids:
            errors.append("handoff references unknown exact phrase IDs: " + ", ".join(sorted(used_phrases - phrase_ids)))
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice-input", type=Path)
    parser.add_argument("--answers", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)
    try:
        answers = load_yaml(args.answers)
        voice = args.voice_input.read_text(encoding="utf-8") if args.voice_input else ""
        packet = extract_source_packet(voice, answers)
        errors = validate_source_packet(packet)
        if args.validate and errors:
            for error in errors:
                print(f"- {error}")
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(yaml.safe_dump(packet, sort_keys=False), encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps({"source_packet": str(args.output), "missing_questions": missing_capture_questions(packet)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
