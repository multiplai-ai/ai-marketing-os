from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


def validate(name, payload):
    schema = yaml.safe_load((ROOT / "schemas" / name).read_text())
    jsonschema.Draft202012Validator(schema).validate(payload)


VALID_PROFILE = {
    "schema_version": 1,
    "author_id": "example-author",
    "voice_guide_ref": "context/voice/guide.md",
    "good_exemplars": [{"id": "good-1", "path": "context/voice/good.md", "calibration_notes": "Specific scenes.", "approved": True}],
    "bad_exemplars": [{"id": "bad-1", "path": "context/voice/bad.md", "rejection_notes": "Generic claims.", "approved": True}],
}


VALID_CATALOG = {
    "schema_version": 1,
    "asset_types": [{
        "id": "default-blog", "kind": "long_form",
        "editorial_brief_ref": "config/writing/brief.md",
        "template_ref": "config/writing/template.md",
        "standards_refs": ["config/writing/standard.md"],
        "good_exemplar_refs": [], "bad_exemplar_refs": [],
        "required_inputs": ["editorial_source_packet"],
        "quality_gates": ["human-writing-standard"],
    }, {
        "id": "operator-build", "kind": "social_post",
        "evidence_classes": {"taste": [], "owned_performance": [], "category_performance": []},
        "editorial_brief_ref": "config/writing/social-brief.md",
        "template_ref": "config/writing/social-template.md",
        "standards_refs": [], "good_exemplar_refs": [], "bad_exemplar_refs": [],
        "required_inputs": ["operator_evidence"], "quality_gates": ["human-writing-standard"],
    }],
}


def test_valid_profile_and_catalog():
    validate("writing-profile.schema.yaml", VALID_PROFILE)
    validate("writing-asset-catalog.schema.yaml", VALID_CATALOG)


@pytest.mark.parametrize("mutation", [
    lambda p: p["good_exemplars"][0].pop("calibration_notes"),
    lambda p: p["bad_exemplars"][0].update({"approved": False}),
    lambda p: p.update({"unknown": True}),
    lambda p: p.update({"voice_guide_ref": "/tmp/guide.md"}),
    lambda p: p.update({"voice_guide_ref": "../guide.md"}),
])
def test_profile_rejects_unsafe_or_uncalibrated_values(mutation):
    import copy
    payload = copy.deepcopy(VALID_PROFILE)
    mutation(payload)
    with pytest.raises(jsonschema.ValidationError):
        validate("writing-profile.schema.yaml", payload)


def test_social_asset_requires_three_evidence_classes():
    import copy
    payload = copy.deepcopy(VALID_CATALOG)
    payload["asset_types"][1]["evidence_classes"].pop("owned_performance")
    with pytest.raises(jsonschema.ValidationError):
        validate("writing-asset-catalog.schema.yaml", payload)


def test_render_request_is_long_form_only():
    request = {"schema_version": 1, "source_packet_ref": "content/source.yaml", "asset_type_id": "post", "asset_kind": "social_post", "output_path": "content/post.md"}
    with pytest.raises(jsonschema.ValidationError):
        validate("writing-render-request.schema.yaml", request)
