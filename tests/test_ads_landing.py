from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "sops" / "ads-landing"
SKILL = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
SCORING = (PACKAGE / "references" / "evidence-and-scoring.md").read_text(encoding="utf-8")
FIXTURE = PACKAGE / "fixtures" / "neutral-b2b"


class AdsLandingContractTests(unittest.TestCase):
    def test_metadata_exposes_portable_conversion_story(self) -> None:
        metadata = yaml.safe_load((PACKAGE / "sop.yaml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["version"], "0.2.0")
        self.assertEqual(
            metadata["inputs"],
            [
                "source_promise",
                "audience",
                "offer",
                "cta",
                "conversion_goal",
                "landing_page_url_or_snapshot",
            ],
        )
        self.assertNotIn("{brain}", "\n".join(metadata["outputs"]))

    def test_scoring_contract_has_complete_status_set_and_weights(self) -> None:
        for status in ("Strong", "Partial", "Weak", "Fail", "Unknown", "N/A"):
            self.assertRegex(SCORING, rf"\| {re.escape(status)} \|")
        weights = [30, 20, 15, 15, 10, 10]
        self.assertEqual(sum(weights), 100)
        for weight in weights:
            self.assertIn(f"| {weight}% |", SCORING)
        self.assertIn("quality score =", SCORING)
        self.assertIn("evidence coverage =", SCORING)

    def test_skill_requires_safe_inspection_and_claims_discipline(self) -> None:
        required = (
            "Do not log in",
            "Do not bypass access controls",
            "Never claim a specific conversion-rate",
            "mark affected checks `Unknown`",
            "A score without coverage is incomplete",
        )
        for phrase in required:
            self.assertIn(phrase, SKILL)

    def test_removed_stale_paths_and_scrub_corruption(self) -> None:
        corpus = SKILL + "\n" + SCORING
        for stale in (
            "tools/ads-references",
            "{brain}",
            "client match",
            "social client",
            "client blocks",
            "CVR drops ~7%",
            "75%+ of ad clicks",
        ):
            self.assertNotIn(stale, corpus)

    def test_neutral_fixture_is_reproducible(self) -> None:
        fixture_input = yaml.safe_load((FIXTURE / "input.yaml").read_text(encoding="utf-8"))
        report = (FIXTURE / "expected-audit.md").read_text(encoding="utf-8")
        self.assertEqual(fixture_input["landing_page_evidence"], "landing-page-snapshot.md")
        earned = 30 * 0.65 + 20 * 1.0 + 15 * 0.30 + 15 * 0.65
        score = round(100 * earned / 80)
        self.assertEqual(score, 67)
        self.assertIn("Quality score: **67/100**", report)
        self.assertIn("Evidence coverage: **80%**", report)
        self.assertIn("Performance and measurement readiness | 10% | Unknown", report)


if __name__ == "__main__":
    unittest.main()
