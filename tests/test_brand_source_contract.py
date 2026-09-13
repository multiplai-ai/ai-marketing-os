"""Guard the shared/consumer brand boundary, not visual style quality."""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]


def test_retired_identity_is_absent_from_active_procedures():
    forbidden = ('cinetype', 'pt sans narrow', 'ptsansnarrow',
                 'creative-director-main/brands', '@hannahuffman',
                 'warm plum/cream', 'no gradients. ever.', 'paper speckle always',
                 'replace a 10-person marketing team', 'one monthly paid builder',
                 'monthly builder\'s log / field guide', 'marketer-in-the-loop.ghost.io')
    for path in (ROOT / 'sops').rglob('*.md'):
        text = path.read_text().lower()
        for term in forbidden:
            assert term not in text, (path, term)


def test_brand_workflows_require_consumer_sources_and_no_archive_fallback():
    for name in ('video-production', 'visual-content', 'components'):
        text = (ROOT / 'sops' / name / 'SKILL.md').read_text()
        assert "Core supplies no fallback brand identity." in text
        assert "Do not search Git history or archive manifests" in text
        assert "including the current approved Figma page" in text


def test_history_manifest_has_only_retrieval_metadata():
    manifest = json.loads((ROOT / 'archive/brand-history.json').read_text())
    assert len(manifest['source_commit']) == 40
    assert manifest['status'] == 'Historical retrieval only; not for creative production'
    assert len(manifest['paths']) == len(set(manifest['paths']))
    assert list((ROOT / 'archive').glob('*.md')) == []


def test_pencil_font_shortcuts_follow_token_roles_not_font_brand_names():
    spec = importlib.util.spec_from_file_location('pencil', ROOT / 'tools/tokens_to_pencil.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    values = []
    module.flatten_typography({
        'display': {'fontFamily': {'$value': 'Fixture Display'}},
        'body': {'fontFamily': {'$value': 'Fixture Body'}},
        'code': {'fontFamily': {'$value': 'Fixture Code'}},
    }, values)
    shortcuts = {v['name']: v['value'] for v in values if v['name'].startswith('font-')}
    assert shortcuts == {'font-display': 'Fixture Display', 'font-body': 'Fixture Body', 'font-code': 'Fixture Code'}
