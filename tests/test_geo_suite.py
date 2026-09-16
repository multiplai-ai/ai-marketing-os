"""Offline handoff checks for the migrated GEO workflows."""
import csv
from pathlib import Path

from tools import geo_plan, geo_share_of_answers as soa


def test_plan_reads_current_public_audit_label(tmp_path):
    (tmp_path / "page_audit.md").write_text("**Heuristic content score:** 73.5/100\n")
    result = geo_plan.parse_audit_dir(tmp_path)
    assert result["urls_audited"] == 1
    assert result["avg_score"] == 73.5


def test_failed_api_sample_is_not_a_brand_miss(tmp_path):
    rows = [
        dict(brand_cited="primary", intent_type="shopping", ai_surface="openai", competitor_citations=""),
        dict(brand_cited="error", intent_type="shopping", ai_surface="openai", competitor_citations=""),
    ]
    path = tmp_path / "runs.csv"
    with path.open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    baseline = geo_plan.parse_runs_csv(tmp_path)
    assert baseline["goal_a"]["overall_share"] == 100
    trend = soa.append_trends_csv(tmp_path, path, ["openai"])
    assert list(csv.DictReader(trend.open()))[0]["overall_share"] == "100.0"


def test_all_geo_workflows_have_real_procedures_and_no_private_corpus_dependency():
    root = Path(__file__).resolve().parents[1]
    for skill in (root / "sops").glob("geo-*/SKILL.md"):
        source = skill.read_text()
        assert len(source.splitlines()) >= 100
        assert "core/skills/" not in source
        assert "references/geo-aeo/" not in source
