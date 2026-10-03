"""Regression tests for evidence loss and false readiness, using fictional inputs."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("vsl_pipeline", Path(__file__).parents[1] / "tools/vsl_pipeline.py")
vsl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vsl)


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)
        self.seed()

    def put(self, stage, extra):
        data = {"schema_version": 1, "stage": stage, "dependencies": vsl.upstream(self.run, stage), "holds": []}
        data.update(extra)
        vsl.write(self.run / (stage + ".json"), data)

    def edit(self, stage, edit):
        p = self.run / (stage + ".json")
        data = vsl.read(p)
        edit(data)
        vsl.write(p, data)

    def seed(self):
        videos = []
        for i in range(3):
            key = "video-id-0" + str(i)
            path = self.run / (key + ".md")
            url = "https://www.youtube.com/watch?v=" + key
            path.write_text(f"**Video ID:** `{key}`\n{url}\n**[00:00]**\nFictional test caption.")
            videos.append({"id": key, "url": url, "transcript_path": str(path), "sha256": vsl.digest(path)})
        reqs = [{"id": "M" + str(i), "video_id": x["id"], "timestamp": "00:00", "rule": "Test rule", "kind": "editorial", "application": "Test application"} for i, x in enumerate(videos)]
        self.put("methods", {"videos": videos, "requirements": reqs})
        sources = [{"id": str(i), "url": "https://example.com/" + str(i), "observed_on": "2026-10-02", "excerpt": "Fictional evidence " + str(i)} for i in range(3)]
        quotes = [{"id": "Q" + str(i), "source_id": str(i), "text": s["excerpt"], "audience_fit": "Test", "bias": "Fictional", "category": "pain"} for i, s in enumerate(sources)]
        self.put("research", {"sources": sources, "quotes": quotes, "coverage": {s: {"status": "complete", "note": "Fixture"} for s in ("forums", "amazon_reviews", "competitor_google_reviews")}})
        insights = [{"id": "H" + str(i), "category": c, "interpretation": "Test", "quote_ids": ["Q0", "Q1"], "limitation": "Fictional"} for i, c in enumerate(("pain", "fear", "desire", "objection", "failed_alternative", "messaging"))]
        self.put("halo", {"insights": insights})
        self.put("offer", {"name": "Example", "promise": "Test", "cta": "Apply", "qualification": ["Test"], "exclusions": ["Test"], "deliverables": ["Test"], "commercial": {"normal_price": 100, "discounted_price": 50, "turnaround": "Test", "approval_ref": "Fixture only"}, "hooks": [{"id": str(i), "angle": "Angle " + str(i), "text": "Test", "insight_ids": ["H0"]} for i in range(5)], "test_plan": "Not a real plan"})
        self.put("script", {"speaker": "Fictional", "language": "en", "claims": [{"id": "C1", "type": "illustration", "source_ref": "fixture", "statement": "Invented"}], "sections": [{"id": "S1", "purpose": "cta", "text": "A fictional sentence for structural testing only. " * 90, "claim_ids": ["C1"], "requirement_ids": ["M0", "M1", "M2"]}], "alternate_hooks": [{"id": "A1", "text": "First"}, {"id": "A2", "text": "Second"}], "coverage": [{"requirement_id": "M" + str(i), "section_ids": ["S1"], "disposition": "addressed", "rationale": "Fictional"} for i in range(3)], "review": {k: {"outcome": "advisory_ready", "evidence": "Test", "limits": "Not human review"} for k in ("human_writing", "voice", "format")}})
        self.put("shots", {"shots": [{"id": "V1", "section_id": "S1", "mode": "talking_head", "visual": "Test", "on_screen": "Test", "assets": ["Test"], "asset_status": "ready", "production_note": "Test"}]})

    def test_structural_pass_never_means_market_or_owner_approval(self):
        report = vsl.chain(self.run)
        self.assertEqual("structurally_ready", report["status"])
        self.assertFalse(report["market_validated"])
        self.assertFalse(report["owner_approved"])

    def test_portable_recorded_fixture_preserves_evidence_holds(self):
        fixture = Path(__file__).parents[1] / "sops/vsl-production/fixtures/evaluation/inputs"
        for source in fixture.iterdir():
            shutil.copy2(source, self.run / source.name)
        report = vsl.chain(self.run)
        self.assertEqual([], report["defects"])
        self.assertEqual("needs_evidence", report["status"])
        self.assertFalse(report["owner_approved"])
        self.assertFalse(report["market_validated"])

    def test_quote_must_exist_verbatim(self):
        self.edit("research", lambda d: d["quotes"][0].update(text="Invented buyer quote"))
        self.assertTrue(vsl.evaluate(self.run, "research")["defects"])

    def test_one_source_video_can_supply_the_rubric(self):
        self.edit("methods", lambda d: d.update(videos=d["videos"][:1], requirements=d["requirements"][:1]))
        self.assertEqual("structurally_ready", vsl.evaluate(self.run, "methods")["status"])

    def test_empty_video_rubric_is_blocked(self):
        self.edit("methods", lambda d: d.update(videos=[], requirements=[]))
        self.assertEqual("blocked", vsl.evaluate(self.run, "methods")["status"])

    def test_every_selected_video_still_needs_requirements(self):
        self.edit("methods", lambda d: d["requirements"].pop())
        self.assertIn("Not all source videos", " ".join(vsl.evaluate(self.run, "methods")["defects"]))

    def test_duplicate_quotes_fail(self):
        self.edit("research", lambda d: d["quotes"].append(dict(d["quotes"][0], id="duplicate")))
        self.assertIn("duplicate quotation", " ".join(vsl.evaluate(self.run, "research")["defects"]))

    def test_citation_timestamp_must_exist(self):
        self.edit("methods", lambda d: d["requirements"][0].update(timestamp="99:99"))
        self.assertTrue(vsl.evaluate(self.run, "methods")["defects"])

    def test_changed_caption_blocks_chain_without_json_change(self):
        path = Path(vsl.read(self.run / "methods.json")["videos"][0]["transcript_path"])
        path.write_text(path.read_text() + "\nChanged")
        self.assertEqual("blocked", vsl.chain(self.run)["status"])

    def test_changed_business_source_blocks_chain(self):
        path = self.run / "business.md"
        path.write_text("Original")
        self.edit("offer", lambda d: d.update(local_sources=[{"path": str(path), "sha256": vsl.digest(path)}]))
        path.write_text("Changed")
        self.assertIn("Changed local source", " ".join(vsl.evaluate(self.run, "offer")["defects"]))

    def test_upstream_edit_invalidates_downstream(self):
        self.edit("halo", lambda d: d.update(holds=["Changed research interpretation"]))
        self.assertIn("Stale", " ".join(vsl.evaluate(self.run, "script")["defects"]))
        with self.assertRaises(ValueError):
            vsl.render(self.run, self.run / "rendered")

    def test_missing_surfaces_are_holds_not_passes(self):
        self.edit("research", lambda d: d["coverage"]["amazon_reviews"].update(status="missing"))
        r = vsl.evaluate(self.run, "research")
        self.assertFalse(r["defects"])
        self.assertEqual("needs_evidence", r["status"])
        with self.assertRaises(ValueError):
            vsl.prepare(self.run, "halo")
        vsl.prepare(self.run, "halo", draft=True)

    def test_invalid_price_pair_fails(self):
        self.edit("offer", lambda d: d["commercial"].update(discounted_price=200))
        self.assertTrue(vsl.evaluate(self.run, "offer")["defects"])

    def test_missing_prices_stay_open(self):
        self.edit("offer", lambda d: d["commercial"].update(normal_price=None, discounted_price=None))
        self.assertEqual("needs_evidence", vsl.evaluate(self.run, "offer")["status"])

    def test_fixed_offer_does_not_require_discount_anchor(self):
        self.edit("offer", lambda d: d.update(commercial={"pricing_model": "fixed", "price": 100, "turnaround": "Fixture", "approval_ref": "Fixture only"}))
        self.assertEqual("structurally_ready", vsl.evaluate(self.run, "offer")["status"])

    def test_free_offer_still_needs_terms_approval(self):
        self.edit("offer", lambda d: d.update(commercial={"pricing_model": "free", "turnaround": "Fixture", "approval_ref": None}))
        report = vsl.evaluate(self.run, "offer")
        self.assertEqual(["Commercial terms need owner decision: approval_ref"], report["holds"])

    def test_free_offer_rejects_price_conflict(self):
        self.edit("offer", lambda d: d["commercial"].update(pricing_model="free"))
        self.assertTrue(vsl.evaluate(self.run, "offer")["defects"])

    def test_fixed_offer_rejects_invalid_prices(self):
        for price in (-1, 0, True, "100"):
            with self.subTest(price=price):
                self.edit("offer", lambda d: d.update(commercial={"pricing_model": "fixed", "price": price, "turnaround": "Fixture", "approval_ref": "Fixture only"}))
                self.assertTrue(vsl.evaluate(self.run, "offer")["defects"])

    def test_unknown_pricing_model_is_blocked(self):
        self.edit("offer", lambda d: d["commercial"].update(pricing_model="unknown"))
        self.assertTrue(vsl.evaluate(self.run, "offer")["defects"])

    def test_missing_method_coverage_fails(self):
        self.edit("script", lambda d: d["coverage"].pop())
        self.assertTrue(vsl.evaluate(self.run, "script")["defects"])

    def test_unknown_claim_fails(self):
        self.edit("script", lambda d: d["sections"][0].update(claim_ids=["missing"]))
        self.assertTrue(vsl.evaluate(self.run, "script")["defects"])

    def test_results_need_substantiation(self):
        self.edit("script", lambda d: d["claims"][0].update(type="result"))
        self.assertEqual("needs_evidence", vsl.evaluate(self.run, "script")["status"])

    def test_unknown_or_missing_shots_fail(self):
        self.edit("shots", lambda d: d["shots"][0].update(section_id="not-in-script"))
        self.assertTrue(vsl.evaluate(self.run, "shots")["defects"])

    def test_malformed_artifact_is_controlled_failure(self):
        (self.run / "shots.json").write_text("[]")
        self.assertEqual("blocked", vsl.evaluate(self.run, "shots")["status"])

    def test_receipt_preserves_exact_stage_snapshot(self):
        report = vsl.evaluate(self.run, "script")
        vsl.stamp(report, self.run)
        saved = vsl.read(next((self.run / "receipts").glob("*.json")))
        self.assertEqual(vsl.read(self.run / "script.json"), saved["artifact_snapshot"])

    def test_render_has_spoken_copy_and_entire_shot_map(self):
        vsl.render(self.run, self.run / "rendered")
        self.assertIn("S1", (self.run / "rendered/shot-list.md").read_text())
        self.assertIn("Fictional", (self.run / "rendered/recording-script.md").read_text().replace("fictional", "Fictional"))
        self.assertFalse(vsl.read(self.run / "rendered/package-status.json")["market_validated"])
        self.assertTrue((self.run / "rendered/recording-script.md").read_text().startswith("# VSL recording draft"))


if __name__ == "__main__":
    unittest.main()
