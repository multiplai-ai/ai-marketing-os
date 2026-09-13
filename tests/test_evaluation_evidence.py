import json
from pathlib import Path

from tools.check_evaluation_evidence import check, digest, WORKFLOWS, SCENARIOS


def fixture(root: Path):
    directory = root / 'examples/strategy-evaluation'
    directory.mkdir(parents=True)
    for workflow in WORKFLOWS:
        skill = root / f'sops/{workflow}/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('Use only provided evidence.')
    (root / 'input.md').write_text('Fictional packet')
    (root / 'output.md').write_text('Provisional draft')
    cases = [{'id': f'{workflow}-{scenario}', 'workflow': workflow, 'input_ref': 'input.md', 'output_ref': 'output.md'} for workflow in WORKFLOWS for scenario in SCENARIOS]
    (directory / 'cases.json').write_text(json.dumps({'cases': cases}))
    execution = {'actor': 'fixture-actor', 'performed_at': '2026-09-13', 'limitations': ['Synthetic checker fixture, not a workflow execution'],
                 'cases_sha256': digest(directory / 'cases.json'), 'cases': [{'id': case['id'], 'skill_sha256': digest(root / f"sops/{case['workflow']}/SKILL.md"), 'input_sha256': digest(root / 'input.md'), 'output_sha256': digest(root / 'output.md')} for case in cases]}
    (directory / 'execution.json').write_text(json.dumps(execution))
    review = {'reviewer': 'fixture-reviewer', 'limitations': ['Synthetic checker fixture'], 'execution_sha256': digest(directory / 'execution.json'), 'cases': [{'id': case['id'], 'verdict': 'pass', 'notes': 'Fixture judgment only'} for case in cases]}
    (directory / 'review.json').write_text(json.dumps(review))
    return directory


def test_changed_output_or_source_invalidates_evidence(tmp_path):
    fixture(tmp_path)
    assert check(tmp_path) == []
    (tmp_path / 'output.md').write_text('Changed claim')
    assert any('stale output_sha256' in error for error in check(tmp_path))
    (tmp_path / 'sops/discovery-intake/SKILL.md').write_text('Changed procedure')
    assert any('stale skill_sha256' in error for error in check(tmp_path))


def test_missing_case_and_altered_review_evidence_fail(tmp_path):
    directory = fixture(tmp_path)
    execution = json.loads((directory / 'execution.json').read_text())
    execution['cases'] = []
    (directory / 'execution.json').write_text(json.dumps(execution))
    errors = check(tmp_path)
    assert 'execution: missing, extra or duplicate cases' in errors
    assert 'execution evidence changed after review' in errors


def test_no_review_does_not_count_as_a_pass(tmp_path):
    directory = fixture(tmp_path)
    (directory / 'review.json').unlink()
    assert check(tmp_path)


def test_reduced_workflow_scope_cannot_keep_catalog_endorsements(tmp_path):
    directory = fixture(tmp_path)
    cases = json.loads((directory / 'cases.json').read_text())
    cases['cases'] = cases['cases'][:4]
    (directory / 'cases.json').write_text(json.dumps(cases))
    assert 'strategy evidence requires all six workflows and all four scenarios' in check(tmp_path)
