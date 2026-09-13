import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from writing_source_packet import validate_article_frontmatter, validate_handoff, validate_render_request


CATALOG = {"asset_types": [{"id": "default-blog", "kind": "long_form"}, {"id": "default-newsletter", "kind": "long_form"}, {"id": "post", "kind": "social_post"}]}


def request(asset):
    return {"schema_version": 1, "source_packet_ref": "content/source.yaml", "asset_type_id": asset, "asset_kind": "long_form", "output_path": f"content/{asset}.md"}


def test_one_packet_can_render_either_default_long_form(tmp_path):
    assert validate_render_request(tmp_path, request("default-blog"), CATALOG) == []
    assert validate_render_request(tmp_path, request("default-newsletter"), CATALOG) == []


def test_social_render_is_rejected(tmp_path):
    errors = validate_render_request(tmp_path, request("post"), CATALOG)
    assert any("long_form" in error for error in errors)


def test_article_frontmatter_and_missing_url_handoff_contract():
    article = {"schema_version": 1, "artifact_type": "long_form_article", "status": "review_ready", "title": "Visible ownership", "slug": "visible-ownership", "created": "2026-09-01", "asset_type": "default-blog", "audience": "B2B operators", "thesis": "Ownership must stay visible.", "source_packet_ref": "content/source.yaml", "handoff_ref": "content/handoff.yaml", "unresolved_claim_ids": [], "checks_run": ["human-writing-standard"]}
    assert validate_article_frontmatter(article) == []
    handoff = {"schema_version": 1, "article_ref": "content/article.md", "source_packet_ref": "content/source.yaml", "message": {"core_thesis": "Ownership must stay visible.", "promised_outcome": "Find a hidden handoff.", "audience": "B2B operators", "supporting_claim_ids": [], "exact_phrase_ids": []}, "offer": {"name": "", "summary": "", "conversion_goal": "", "primary_cta": ""}, "destination": {"url": "", "desired_action": "", "message_match_terms": [], "proof_expectations": []}, "social_angle_candidates": [], "landing_audit": {"traffic_source": "LinkedIn organic", "entry_message": "", "target_audience": "B2B operators", "expected_offer": "", "expected_cta": "", "expected_proof": [], "destination_url": ""}, "readiness": {"linkedin_ready": False, "landing_audit_ready": False, "blockers": ["Destination URL is missing."]}}
    assert validate_handoff(handoff) == []


def test_handoff_cannot_claim_landing_readiness_without_url():
    handoff = {"schema_version": 1, "article_ref": "a.md", "source_packet_ref": "s.yaml", "message": {"core_thesis": "A", "promised_outcome": "B", "audience": "C", "supporting_claim_ids": [], "exact_phrase_ids": []}, "offer": {"name": "", "summary": "", "conversion_goal": "", "primary_cta": ""}, "destination": {"url": "", "desired_action": "", "message_match_terms": [], "proof_expectations": []}, "social_angle_candidates": [], "landing_audit": {"traffic_source": "LinkedIn organic", "entry_message": "", "target_audience": "C", "expected_offer": "", "expected_cta": "", "expected_proof": [], "destination_url": ""}, "readiness": {"linkedin_ready": False, "landing_audit_ready": True, "blockers": []}}
    assert any("missing" in error or "URL" in error for error in validate_handoff(handoff))
