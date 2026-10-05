"""Verify portable packaging, canonical routing, and unsafe-input rejection."""
import json
from pathlib import Path
import zipfile
import pytest
import yaml
from tools.build_chatgpt_plugin import build

ROOT=Path(__file__).resolve().parents[1]


def test_library_package_preserves_every_workflow_and_reference(tmp_path):
    version=json.loads((ROOT/'.claude-plugin/plugin.json').read_text())['version']
    path=build(ROOT,tmp_path,version)
    first=path.read_bytes()
    assert build(ROOT,tmp_path,version).read_bytes()==first
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        manifest=json.loads(z.read('ai-marketing-os/plugin.json'))
        assert manifest['name']=='ai-marketing-os'
        assert manifest['version']==version
        assert len(manifest['extensions']['com.openai']['interface']['shortDescription'])<=30
        ids=yaml.safe_load((ROOT/'sops/manifest.yaml').read_text())['sops']
        assert {x.split('/')[2] for x in names if x.startswith('ai-marketing-os/skills/') and x.endswith('/SKILL.md')}==set(ids)
        for sid in ids:
            router=z.read(f'ai-marketing-os/skills/{sid}/SKILL.md').decode()
            assert f'../../sops/{sid}/SKILL.md' in router
            for source in (ROOT/f'sops/{sid}').rglob('*'):
                if source.is_file() and '__pycache__' not in source.parts and source.suffix not in {'.pyc','.pyo'} and source.name != '.DS_Store':
                    assert z.read('ai-marketing-os/'+source.relative_to(ROOT).as_posix())==source.read_bytes()
        assert not any('/.git/' in x or '/.claude-plugin/' in x for x in names)


def fixture(root):
    (root/'.claude-plugin').mkdir()
    (root/'.claude-plugin/plugin.json').write_text(json.dumps({'name':'ai-marketing-os','version':'1.0.0','description':'Example','author':{'name':'Example'}}))
    (root/'sops/demo').mkdir(parents=True)
    (root/'sops/manifest.yaml').write_text('sops: [demo]\n')
    (root/'sops/demo/SKILL.md').write_text('---\nname: demo\ndescription: Example\n---\nExample')


def test_rejects_wrong_version_and_inventory(tmp_path):
    fixture(tmp_path)
    with pytest.raises(ValueError,match='version'): build(tmp_path,tmp_path/'dist','2.0.0')
    (tmp_path/'sops/manifest.yaml').write_text('sops: [other]\n')
    with pytest.raises(ValueError,match='inventory'): build(tmp_path,tmp_path/'dist','1.0.0')


def test_rejects_symlink(tmp_path):
    fixture(tmp_path)
    (tmp_path/'sops/demo/link.md').symlink_to(tmp_path/'sops/demo/SKILL.md')
    with pytest.raises(ValueError,match='symlink'): build(tmp_path,tmp_path/'dist','1.0.0')
