import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from human_writing_gate import evaluate


def test_rejects_contrast_stack_and_synthetic_language():
    report = evaluate("Not strategy. Not systems. Not judgment. Just content. This is where the magic happens. In today's rapidly evolving landscape, teams can unlock unprecedented value.")
    assert not report.passed
    assert any("contrast" in item for item in report.errors)
    assert len(report.errors) >= 3


def test_recognizes_grounded_positive_signals():
    text = 'We tested the checkout with 17 buyers because the previous flow delayed every approval. One operator said, “I cannot tell who owns the next step.” We measured a two-day cost, then changed the handoff.'
    report = evaluate(text)
    assert report.passed
    assert {"specific_number", "source_quote", "first_person_evidence", "concrete_consequence"} <= set(report.positive_signals)
