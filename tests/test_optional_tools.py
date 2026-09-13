"""Offline startup and optional integration contracts; never call live services."""
from pathlib import Path
import os
import subprocess
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.check_offline_cli import discover_tools, GUARD
from tools.optional_dependencies import MissingOptionalDependency, launch_chromium

BLOCK_OPTIONAL = '''
import importlib.abc
import sys
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'requests', 'playwright', 'trafilatura', 'bs4', 'textstat', 'readability', 'tldextract', 'google', 'PIL', 'openai', 'anthropic', 'dotenv'}:
            raise ModuleNotFoundError('blocked optional dependency: ' + fullname)
sys.meta_path.insert(0, BlockOptional())
'''


def run_tool(tmp_path, name, *args, block=True):
    (tmp_path / 'sitecustomize.py').write_text(GUARD + (BLOCK_OPTIONAL if block else ''))
    env = {'PATH': os.environ.get('PATH', ''), 'HOME': str(tmp_path),
           'PYTHONPATH': os.pathsep.join((str(tmp_path), str(ROOT), str(ROOT / 'tools'))),
           'PYTHONDONTWRITEBYTECODE': '1'}
    return subprocess.run([sys.executable, str(ROOT / 'tools' / f'{name}.py'), *args],
                          cwd=tmp_path, env=env, text=True, capture_output=True, timeout=30)


def test_discovery_includes_new_executable_without_allowlist(tmp_path):
    tools = tmp_path / 'tools'
    tools.mkdir()
    (tools / 'new_tool.py').write_text('if __name__ == "__main__":\n    pass\n')
    (tools / 'library.py').write_text('def main(): pass\n')
    (tools / 'check_core.py').write_text('if __name__ == "__main__": pass\n')
    assert discover_tools(tmp_path) == ('new_tool',)


@pytest.mark.parametrize('name,args,extra', [
    ('web_scraper', ['https://example.invalid', 'out'], 'web'),
    ('extract_design_tokens', ['https://example.invalid'], 'web'),
    ('generate_design_visual', ['--prompt', 'fictional tile', '--output', 'tile.png'], 'google'),
    ('geo_audit', ['--url', 'https://example.invalid', '--output', 'out'], 'geo'),
    ('gamma_create_presentation', ['--test'], 'publishing'),
    ('templated_renderer', ['--test'], 'publishing'),
])
def test_missing_integration_is_actionable_before_network(tmp_path, name, args, extra):
    result = run_tool(tmp_path, name, *args)
    assert result.returncode == 2, result.stdout + result.stderr
    assert f".[{extra}]" in result.stderr
    assert 'Traceback' not in result.stderr
    assert 'Network access forbidden' not in result.stderr


@pytest.mark.parametrize('name', [
    'web_scraper', 'extract_design_tokens', 'generate_design_visual', 'geo_audit',
    'gamma_create_presentation', 'templated_renderer',
])
def test_help_with_all_optional_packages_absent(tmp_path, name):
    result = run_tool(tmp_path, name, '--help')
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'usage:' in result.stdout


def test_gamma_dry_run_without_dependency_or_credentials(tmp_path):
    draft = tmp_path / 'draft.md'
    draft.write_text('# Fictional Demo\n\nA short offline draft.\n')
    result = run_tool(tmp_path, 'gamma_create_presentation', str(draft), '--dry-run')
    assert result.returncode == 0, result.stdout + result.stderr


def test_templated_dry_run_without_dependency_or_credentials(tmp_path):
    draft = tmp_path / 'draft.md'
    draft.write_text('# Fictional Demo\n\nA short offline draft.\n')
    result = run_tool(tmp_path, 'templated_renderer', '--render', str(draft), '--dry-run')
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / 'content').exists()


def test_playwright_missing_browser_has_install_command():
    class MissingBrowser:
        def launch(self, **kwargs):
            raise RuntimeError("Executable doesn't exist at browser cache")
    with pytest.raises(MissingOptionalDependency, match='python -m playwright install chromium'):
        launch_chromium(MissingBrowser(), headless=True)


def test_playwright_other_runtime_errors_are_preserved():
    class BrokenBrowser:
        def launch(self, **kwargs):
            raise RuntimeError('unrelated browser failure')
    with pytest.raises(RuntimeError, match='unrelated browser failure'):
        launch_chromium(BrokenBrowser())


def test_optional_extras_cover_packages_used_by_geo_llm_and_visuals():
    extras = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['optional-dependencies']
    assert any(item.startswith('textstat') for item in extras['geo'])
    assert any(item.startswith('readability-lxml') for item in extras['geo'])
    assert any(item.startswith('anthropic') for item in extras['llm'])
    assert any(item.startswith('openai') for item in extras['llm'])
    assert any(item.startswith('Pillow') for item in extras['google'])


def test_no_implicit_dotenv_reads_on_tool_import(tmp_path):
    # A synthetic dotenv next to copied scripts forces old exists/read loaders
    # to trigger; the smoke guard forbids reading even a credential-free fixture.
    import shutil
    fixture = tmp_path / 'core'
    shutil.copytree(ROOT / 'tools', fixture / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
    (fixture / '.env').write_text('CORE_SYNTHETIC_TEST_MARKER=must-not-load\n')
    (tmp_path / 'sitecustomize.py').write_text(GUARD)
    modules = ('generate_design_visual', 'geo_audit', 'gamma_create_presentation', 'templated_renderer',
               'buffer_publisher', 'metricool_publisher', 'publer_publisher',
               'notion_content_db', 'notion_publish', 'sheets_publish')
    code = 'import runpy,sys; [runpy.run_path(p, run_name="offline_import") for p in sys.argv[1:]]'
    result = subprocess.run([sys.executable, '-c', code,
                             *(str(fixture / 'tools' / f'{name}.py') for name in modules)],
                            cwd=tmp_path, env={'PATH': os.environ.get('PATH', ''),
                            'HOME': str(tmp_path), 'PYTHONPATH': os.pathsep.join((str(tmp_path), str(fixture), str(fixture / 'tools')))},
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('status', [404, 429, 500])
def test_gamma_error_response_does_not_verify_credentials(monkeypatch, capsys, status):
    from tools import gamma_create_presentation as gamma
    from types import SimpleNamespace
    client = SimpleNamespace(get=lambda *args, **kwargs: SimpleNamespace(status_code=status),
                             exceptions=SimpleNamespace(RequestException=RuntimeError))
    monkeypatch.setattr(gamma, 'require_dependency', lambda *args: client)
    monkeypatch.setenv('GAMMA_API_KEY', 'fixture')
    assert gamma.test_connection() is False
    assert 'credentials accepted' not in capsys.readouterr().out
