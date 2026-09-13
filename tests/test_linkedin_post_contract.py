from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "sops" / "linkedin-post"
SKILL = PACKAGE / "SKILL.md"
BATCH_REFERENCE = PACKAGE / "references" / "article-batch.md"
FIXTURE = ROOT / "tests" / "fixtures" / "linkedin-post"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path):
    return yaml.safe_load(read(path))


def test_metadata_declares_portable_v020_contract():
    metadata = load_yaml(PACKAGE / "sop.yaml")

    assert metadata["id"] == "linkedin-post"
    assert metadata["version"] == "0.2.0"
    assert "mode" in metadata["inputs"]
    assert "source_article" in metadata["inputs"]
    assert "evidence_ledger_or_handoff" in metadata["inputs"]
    assert "review_ready_linkedin_post" in metadata["outputs"]
    assert "source_and_evidence_audit" in metadata["outputs"]
    assert "review_ready_linkedin_post_batch" in metadata["outputs"]
    assert "landing_page_handoff" in metadata["outputs"]
    assert "tests/test_linkedin_post_contract.py" in metadata["tests"]


def test_single_post_flow_and_conditional_batch_reference_are_explicit():
    skill = read(SKILL)

    assert "`single_post`" in skill
    assert "intake, shape, hook options, draft, voice check, iteration" in skill
    assert "`article_batch`" in skill
    assert "Load `references/article-batch.md` only for `article_batch`" in skill
    assert BATCH_REFERENCE.is_file()


def test_package_has_no_embedded_entity_voice_or_unsupported_benchmarks():
    package_text = read(SKILL) + "\n" + read(BATCH_REFERENCE)
    forbidden = (
        "Entity note",
        "Emily Kramer",
        "Elena Verna",
        "Lenny Rachitsky",
        "Meg Gowell",
        "Jason Widup",
        "579 posts",
        "3.56%",
        "core/skills/youtube-transcript/SKILL.md",
        "No em-dashes",
        "MultiplAI",
        "Marketer in the Loop",
    )

    for marker in forbidden:
        assert marker not in package_text

    assert "do not assume a universal" in package_text.lower()


def test_batch_contract_requires_evidence_diversity_and_no_padding():
    reference = read(BATCH_REFERENCE)

    for status in ("supported", "inference", "opinion", "unsupported"):
        assert f"**{status.title()}:**" in reference
    assert "at least three different reader jobs" in reference
    assert "Diversity is semantic, not cosmetic" in reference
    assert "Do not pad" in reference
    assert "landing_page_handoff:" in reference
    assert "required_message_match:" in reference
    assert "evidence_gaps:" in reference


def test_synthetic_fixture_has_traceable_claims_and_excludes_unsupported_claim():
    request = load_yaml(FIXTURE / "request.yaml")
    evidence = load_yaml(FIXTURE / "evidence.yaml")
    expected = load_yaml(FIXTURE / "expected-contract.yaml")
    article = read(FIXTURE / "article.md")

    assert request["mode"] == "article_batch"
    assert request["batch_size"] == expected["delivered_posts"]
    assert "fictional" in article.lower() and "synthetic" in article.lower()

    claims = {item["id"]: item for item in evidence["claims"]}
    assert set(expected["excluded_claims"]) == {
        claim_id for claim_id, claim in claims.items() if claim["status"] == "unsupported"
    }

    used_ids = {
        claim_id
        for post_claims in expected["claim_usage"].values()
        for claim_id in post_claims
    }
    assert used_ids <= claims.keys()
    assert used_ids.isdisjoint(expected["excluded_claims"])
    assert len(set(expected["reader_jobs"])) >= 3


def test_fixture_handoff_fields_match_reference_template():
    reference = read(BATCH_REFERENCE)
    expected = load_yaml(FIXTURE / "expected-contract.yaml")
    template_match = re.search(
        r"```yaml\nlanding_page_handoff:\n(?P<body>.*?)```", reference, re.DOTALL
    )

    assert template_match is not None
    template = yaml.safe_load("landing_page_handoff:\n" + template_match.group("body"))
    assert set(expected["required_handoff_fields"]) == set(
        template["landing_page_handoff"].keys()
    )
