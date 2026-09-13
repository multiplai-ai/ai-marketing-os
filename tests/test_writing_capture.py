import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from writing_source_packet import extract_source_packet, missing_capture_questions, validate_source_packet


def test_rich_capture_preserves_source_fields_and_unresolved_claim():
    voice = 'After 14 interviews I said, “The handoff is where trust disappears.”'
    answers = {"topic_or_assignment": "Trust in handoffs", "source_input_refs": ["notes/interview.md"], "thesis": "Ownership must be visible.", "trigger": "A launch stalled.", "tension": "Automation hid ownership.", "stakes": "A buyer waited two days.", "firsthand_evidence": ["We interviewed 14 operators."], "claims": ["The change increased conversion 20%."], "counterargument": "More automation can reduce delay.", "reader_outcome": "Inspect one handoff.", "cutting_room": ["A second example."], "sensitive_details": ["Customer name"]}
    packet = extract_source_packet(voice, answers)
    assert packet["exact_phrases"][0]["text"] == "The handoff is where trust disappears."
    assert packet["claims"][0]["support_status"] == "unresolved"
    assert packet["firsthand_evidence"][0]["summary"] == "We interviewed 14 operators."
    assert missing_capture_questions(packet) == []
    assert validate_source_packet(packet) == []


def test_thin_capture_requests_only_five_core_gaps():
    packet = extract_source_packet("AI strategy", {"topic_or_assignment": "AI strategy"})
    questions = missing_capture_questions(packet)
    assert len(questions) == 5
    assert any("argument" in item for item in questions)


def test_verified_claim_requires_evidence_and_attribution():
    packet = extract_source_packet("Source", {"topic_or_assignment": "Topic", "source_ref": "notes.md", "thesis": "A", "trigger": "B", "tension": "C", "stakes": "D", "reader_outcome": "E", "claims": [{"id": "claim-1", "text": "Conversion rose.", "support_status": "verified", "evidence_refs": [], "attribution": ""}]})
    errors = validate_source_packet(packet)
    assert any("evidence_refs" in error for error in errors)
    assert any("attribution" in error for error in errors)
