"""Public acquisition tests: no authentication, safe paths, and failed-download isolation."""
from pathlib import Path
import io
import sys
import urllib.error
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import core_install


class Response(io.BytesIO):
    url = 'https://release-assets.githubusercontent.com/fixture'


def test_public_download_is_anonymous_and_exact(monkeypatch, tmp_path):
    seen = []
    def fetch(request, timeout):
        seen.append(request)
        assert timeout == 60
        assert not request.has_header('Authorization')
        return Response(b'fixture')
    monkeypatch.setattr(core_install.urllib.request, 'urlopen', fetch)
    paths = core_install.download_public_release('multiplai-ai/ai-marketing-os', '4.0.0-rc.13', tmp_path)
    assert len(paths) == len(seen) == 4
    assert all(p.read_bytes() == b'fixture' for p in paths)
    assert all(r.full_url.startswith('https://github.com/multiplai-ai/ai-marketing-os/releases/download/v4.0.0-rc.13/') for r in seen)
    assert len(list(tmp_path.iterdir())) == 4


@pytest.mark.parametrize('repo,version', [('a/../../private', '1.0.0'), ('https://evil.invalid/r', '1.0.0'), ('owner/repo','../../secret'), ('owner/repo','1.0.0?token=x')])
def test_invalid_channel_refused_without_download(monkeypatch, tmp_path, repo, version):
    monkeypatch.setattr(core_install.urllib.request, 'urlopen', lambda *a, **k: pytest.fail('network called'))
    with pytest.raises(core_install.CoreInstallError, match='invalid public release'):
        core_install.download_public_release(repo, version, tmp_path)
    assert not list(tmp_path.iterdir())


def test_failed_asset_keeps_previous_downloads(monkeypatch, tmp_path):
    previous = tmp_path / 'multiplai-core-1.0.0.tar.zst'
    previous.write_bytes(b'previous')
    calls = []
    def fetch(request, timeout):
        calls.append(request)
        if len(calls) == 2:
            raise urllib.error.URLError('fixture failure')
        return Response(b'incomplete-new-download')
    monkeypatch.setattr(core_install.urllib.request, 'urlopen', fetch)
    with pytest.raises(core_install.CoreInstallError, match='cannot download public release'):
        core_install.download_public_release('owner/repo', '1.0.0', tmp_path)
    assert previous.read_bytes() == b'previous'
    assert list(tmp_path.iterdir()) == [previous]


def test_http_redirect_refused(monkeypatch, tmp_path):
    response = Response(b'fixture')
    response.url = 'http://example.invalid/asset'
    monkeypatch.setattr(core_install.urllib.request, 'urlopen', lambda *a, **k: response)
    with pytest.raises(core_install.CoreInstallError, match='outside HTTPS'):
        core_install.download_public_release('owner/repo', '1.0.0', tmp_path)
    assert not list(tmp_path.iterdir())
