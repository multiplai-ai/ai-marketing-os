from __future__ import annotations

import sys
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from check_client_scrub import contains_term  # noqa: E402


def test_generic_proof_language_is_not_treated_as_a_client_name() -> None:
    assert not contains_term("Add proof points and customer evidence.", "Proof")


def test_capitalized_proof_client_name_is_detected() -> None:
    assert contains_term("Approved for Proof delivery.", "Proof")


def test_other_entity_names_remain_case_insensitive() -> None:
    assert contains_term("remove multiplai-specific paths", "MultiplAI")


def test_standard_title_case_proof_terminology_is_allowed():
    assert not contains_term('Proof Points; Types of Proof; Social Proof; Matching Proof to Claims', 'Proof')
    assert contains_term('Proof Points for Proof delivery', 'Proof')
