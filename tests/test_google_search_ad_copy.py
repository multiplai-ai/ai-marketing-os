"""Behavioral checks for the static RSA validator, not copy-performance tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "sops/google-search-ad-copy/scripts/validate_rsa.py"
spec = importlib.util.spec_from_file_location("validate_rsa", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


@pytest.fixture
def packet():
    return {"ads": [{"name": "Sample", "headlines": ["Monthly Bookkeeping Help",
            "Know What Your Plan Includes", "See Our Monthly Close Process"],
        "descriptions": ["Explore bookkeeping packages and see how our monthly close process works.",
                         "Get help organizing your books. Book an introductory call to discuss your needs."],
        "paths": ["bookkeeping", "packages"]}]}


@pytest.mark.parametrize("field,limit", [("headlines", 30), ("descriptions", 90), ("paths", 15)])
def test_character_boundaries_include_whitespace(packet, field, limit):
    packet["ads"][0][field][0] = "a " + "b" * (limit - 2)
    assert validator.validate(packet)["status"] == "format_pass"
    packet["ads"][0][field][0] += "x"
    assert validator.validate(packet)["status"] == "fail"


@pytest.mark.parametrize("field,amount", [("headlines", 2), ("headlines", 16),
                                        ("descriptions", 1), ("descriptions", 5), ("paths", 3)])
def test_rsa_asset_count_bounds(packet, field, amount):
    packet["ads"][0][field] = [f"Asset {i}" for i in range(amount)]
    assert validator.validate(packet)["status"] == "fail"


def test_selected_packet_counts_and_optional_paths(packet):
    del packet["ads"][0]["paths"]
    result = validator.validate(packet)
    assert result["status"] == "format_pass"
    assert [row["count"] for row in result["counts"]] == [24, 28, 29, 73, 80]


def test_case_and_spacing_do_not_hide_duplicates(packet):
    packet["ads"][0]["headlines"][1] = "MONTHLY  BOOKKEEPING HELP"
    assert any("duplicate" in error for error in validator.validate(packet)["errors"])


@pytest.mark.parametrize("text", [" leading", "trailing ", "line\nbreak", "hidden\u200btext", ""])
def test_empty_or_hidden_text_is_not_silently_trimmed(packet, text):
    packet["ads"][0]["headlines"][0] = text
    assert validator.validate(packet)["status"] == "fail"


def test_double_width_count_and_manual_verification(packet):
    packet["ads"][0]["headlines"][0] = "漢" * 15
    result = validator.validate(packet)
    assert result["counts"][0]["count"] == 30
    assert result["status"] == "manual_review"
    packet["ads"][0]["headlines"][0] += "漢"
    assert validator.validate(packet)["status"] == "fail"


@pytest.mark.parametrize("text", ["{KeyWord:Books}", "Bookkeeping Help!"])
def test_review_flags_do_not_claim_a_format_pass(packet, text):
    packet["ads"][0]["headlines"][0] = text
    assert validator.validate(packet)["status"] == "manual_review"


@pytest.mark.parametrize("payload", [None, {}, {"ads": []}, {"ads": [None]},
                                     {"ads": [{"headlines": None}]}])
def test_malformed_packet_returns_failure(payload):
    assert validator.validate(payload)["status"] == "fail"


def test_cli_status_and_invalid_json(packet, tmp_path):
    path = tmp_path / "ads.json"
    for text, code, status in [(json.dumps(packet), 0, "format_pass"),
                                ("{bad json", 1, "fail")]:
        path.write_text(text)
        result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
        assert result.returncode == code
        assert json.loads(result.stdout)["status"] == status
    review_packet = deepcopy(packet)
    review_packet["ads"][0]["headlines"][0] = "Bookkeeping Help!"
    path.write_text(json.dumps(review_packet))
    result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "manual_review"
