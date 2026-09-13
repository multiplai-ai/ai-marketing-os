import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from writing_config import safe_consumer_ref, validate_catalog, validate_profile


def write(root, ref, text="# substantive\n"):
    path = root / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def configured_root(tmp_path):
    refs = ["voice.md", "good.md", "bad.md", "brief.md", "template.md", "standard.md", "taste.md", "owned.md", "category.md"]
    for ref in refs:
        write(tmp_path, ref)
    profile = {"schema_version": 1, "author_id": "author", "voice_guide_ref": "voice.md", "good_exemplars": [{"id": "g", "path": "good.md", "calibration_notes": "Keep scenes.", "approved": True}], "bad_exemplars": [{"id": "b", "path": "bad.md", "rejection_notes": "Too generic.", "approved": True}]}
    base = {"editorial_brief_ref": "brief.md", "template_ref": "template.md", "standards_refs": ["standard.md"], "good_exemplar_refs": ["good.md"], "bad_exemplar_refs": ["bad.md"], "required_inputs": ["editorial_source_packet"], "quality_gates": ["human-writing-standard"]}
    catalog = {"schema_version": 1, "asset_types": [dict(base, id="blog", kind="long_form"), dict(base, id="post", kind="social_post", evidence_classes={"taste": ["taste.md"], "owned_performance": ["owned.md"], "category_performance": ["category.md"]})]}
    return profile, catalog


def test_valid_configuration(tmp_path):
    profile, catalog = configured_root(tmp_path)
    assert validate_profile(tmp_path, profile) == []
    assert validate_catalog(tmp_path, catalog) == []


def test_missing_empty_and_duplicate_references_fail(tmp_path):
    profile, catalog = configured_root(tmp_path)
    (tmp_path / "brief.md").write_text("")
    catalog["asset_types"].append(dict(catalog["asset_types"][0]))
    errors = validate_catalog(tmp_path, catalog)
    assert any("empty" in error for error in errors)
    assert any("duplicate" in error for error in errors)


def test_safe_ref_rejects_escape(tmp_path):
    try:
        safe_consumer_ref(tmp_path, "../outside.md")
    except ValueError as exc:
        assert "escapes" in str(exc)
    else:
        raise AssertionError("escape accepted")
