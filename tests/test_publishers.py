"""Offline publisher regressions: no test contacts Ghost or Substack."""

import builtins
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

from tools import ghost_publisher as ghost
from tools import substack_publisher as substack
from tools.markdown_utils import extract_frontmatter, extract_title, markdown_to_html, parse_tags


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def article(tmp_path):
    path = tmp_path / "article.md"
    path.write_text('---\ntitle: "A useful guide: September"\ntags:\n  - Research\n  - How-to\nsubtitle: A short introduction\n---\n\n# A useful guide\n\nA **bold** idea.\n\n- First\n- Second\n', encoding="utf-8")
    return path


@pytest.mark.parametrize("script", ["ghost_publisher.py", "substack_publisher.py"])
def test_help_works_without_site_packages(script):
    result = subprocess.run([sys.executable, "-S", str(ROOT / "tools" / script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "--dry-run" in result.stdout


@pytest.mark.parametrize("module", [ghost, substack])
def test_cli_dry_run_is_credential_free_and_offline(module, article, capsys):
    with patch.dict(os.environ, {}, clear=True), patch.object(module, "requests", None), patch.object(sys, "argv", ["publisher", "--draft", str(article), "--dry-run"]):
        assert module.main() == 0
    output = capsys.readouterr().out
    assert "[DRY RUN]" in output
    assert "A useful guide: September" in output
    assert "<strong>bold</strong>" in output


@pytest.mark.parametrize("module", [ghost, substack])
def test_dry_run_cannot_test_live_connection(module):
    with patch.object(sys, "argv", ["publisher", "--test", "--dry-run"]), patch.object(module, "requests", Mock()) as requests:
        with pytest.raises(SystemExit) as exc:
            module.main()
        assert exc.value.code == 2
        assert requests.mock_calls == []


@pytest.mark.parametrize("module", [ghost, substack])
def test_missing_live_credentials_is_actionable(module, article, capsys):
    with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", ["publisher", "--draft", str(article)]):
        assert module.main() == 1
    assert "Export these environment variables" in capsys.readouterr().err


def test_import_does_not_read_dotenv_or_mutate_environment():
    script = '''
import builtins, os
from pathlib import Path
before = dict(os.environ)
original_open = builtins.open
original_read_text = Path.read_text
def guarded_open(file, *args, **kwargs):
    assert not str(file).endswith('.env'), 'implicit credential read'
    return original_open(file, *args, **kwargs)
def guarded_read(path, *args, **kwargs):
    assert path.name != '.env', 'implicit credential read'
    return original_read_text(path, *args, **kwargs)
builtins.open = guarded_open
Path.read_text = guarded_read
import tools.ghost_publisher, tools.substack_publisher
assert dict(os.environ) == before
'''
    result = subprocess.run([sys.executable, "-S", "-c", script], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_yaml_frontmatter_preserves_strings_lists_and_multiline_text():
    fm, body = extract_frontmatter('\ufeff---\r\ntitle: "A title: with colon"\r\ntags: [one, two]\r\ndescription: |\r\n  First line\r\n  Second line\r\n---\r\n\r\n# Heading\r\nBody')
    assert fm["title"] == "A title: with colon"
    assert fm["tags"] == ["one", "two"]
    assert fm["description"] == "First line\nSecond line\n"
    assert body == "# Heading\r\nBody"
    assert extract_title(body, Path("fallback-name.md")) == "Heading"
    assert extract_title("plain body", Path("fallback-name.md")) == "fallback name"


@pytest.mark.parametrize("content", ["---\ntitle: broken\n", "---\n- list\n---\n", "---\ntitle: [\n---\n", "---\ntitle: one\ntitle: two\n---\n", "---\n1: number key\n---\n"])
def test_malformed_frontmatter_is_rejected(content):
    with pytest.raises(ValueError):
        extract_frontmatter(content)


@pytest.mark.parametrize("module", [ghost, substack])
def test_bad_metadata_reports_error_without_traceback(module, tmp_path, capsys):
    path = tmp_path / "invalid.md"
    path.write_text("---\ntitle: [bad, title]\n---\nBody")
    with patch.object(sys, "argv", ["publisher", "--draft", str(path), "--dry-run"]):
        assert module.main() == 1
    output = capsys.readouterr()
    assert "must be a string" in output.out + output.err
    assert "Traceback" not in output.out + output.err


def test_markdown_renders_tables_and_fenced_code():
    rendered = markdown_to_html("| Name | Count |\n| --- | --- |\n| Demo | 2 |\n\n```python\nprint('demo')\n```")
    assert "<table>" in rendered
    assert '<code class="language-python">' in rendered
    assert parse_tags(" one, two, ") == ["one", "two"]
    assert parse_tags([" one ", "two"]) == ["one", "two"]
    with pytest.raises(ValueError):
        parse_tags(["one", 2])


def test_missing_render_dependency_has_install_instruction():
    original = builtins.__import__
    def blocked(name, *args, **kwargs):
        if name == "markdown":
            raise ImportError("missing")
        return original(name, *args, **kwargs)
    with patch("builtins.__import__", side_effect=blocked), pytest.raises(ImportError, match="publishing"):
        markdown_to_html("# Hello")


def test_ghost_mocked_create_payload_and_error_paths():
    client = ghost.GhostClient("https://example.invalid/", "unused")
    response = Mock(ok=True)
    response.json.return_value = {"posts": [{"id": "42", "status": "draft", "url": "https://example.invalid/article/"}]}
    with patch.object(client, "_auth_header", return_value={"Authorization": "Ghost test"}), patch.object(ghost, "requests") as requests:
        requests.post.return_value = response
        ok, result = client.create_post("Title", "<p>Body</p>", tags=["Demo"])
        assert ok and "editor/post/42" in result
        assert requests.post.call_args.kwargs["json"] == {"posts": [{"title": "Title", "html": "<p>Body</p>", "status": "draft", "featured": False, "visibility": "public", "tags": [{"name": "Demo"}]}]}
        assert requests.post.call_args.kwargs["timeout"] == 30
        response.ok = False
        response.status_code = 422
        response.text = "Invalid title"
        response.json.return_value = {"errors": [{"message": "Invalid title", "context": "title required"}]}
        assert client.create_post("", "body") == (False, "HTTP 422: Invalid title — title required")
        requests.post.side_effect = RuntimeError("offline failure")
        assert client.create_post("Title", "body") == (False, "Post creation error: offline failure")


def test_ghost_schedule_offsets_and_page_payload():
    client = ghost.GhostClient("https://example.invalid", "")
    with patch.object(ghost, "requests", None), patch.object(ghost, "jwt", None):
        ok, preview = client.create_post("Title", "body", scheduled_at="2030-03-15T09:00:00-04:00", dry_run=True)
        assert ok
        payload = json.loads(preview.split("Payload:\n")[1])["posts"][0]
        assert payload["published_at"] == "2030-03-15T13:00:00Z"
        assert payload["status"] == "scheduled"
        ok, preview = client.create_post("Page", "body", is_page=True, newsletter_slug="members", scheduled_at="ignored", dry_run=True)
        assert ok
        page = json.loads(preview.split("Payload:\n")[1])["pages"][0]
        assert "newsletter" not in page and "published_at" not in page
        assert client.create_post("Title", "body", scheduled_at="invalid", dry_run=True)[0] is False


def test_ghost_connection_auth_failure_and_missing_dependency():
    client = ghost.GhostClient("https://example.invalid", "unused")
    with patch.object(client, "_auth_header", return_value={}), patch.object(ghost, "requests") as requests:
        requests.get.return_value = Mock(ok=False, status_code=401)
        assert client.test_connection() == (False, "Authentication failed — check GHOST_ADMIN_API_KEY")
    with patch.object(ghost, "requests", None):
        assert "publishing" in client.test_connection()[1]


def test_substack_mocked_login_create_and_error_paths(article):
    client = substack.SubstackPublisher("author@example.invalid", "unused", "example")
    login = Mock(ok=True)
    created = Mock(ok=True)
    created.json.return_value = {"id": 42}
    with patch.object(substack, "requests") as requests:
        session = requests.Session.return_value
        session.post.side_effect = [login, created]
        assert client.create_draft(article) == (True, "Draft created: https://example.substack.com/publish/post/42")
        payload = session.post.call_args.kwargs["json"]
        assert payload["draft_title"] == "A useful guide: September"
        assert "<strong>bold</strong>" in payload["draft_body"]
        assert "<h1>" not in payload["draft_body"]
        assert payload["audience"] == "everyone"
        assert session.post.call_args.kwargs["timeout"] == 30
        failed = Mock(ok=False, status_code=403, text="Forbidden")
        failed.json.return_value = {"error": "Draft access denied"}
        session.post.side_effect = [failed]
        assert client.create_draft(article) == (False, "HTTP 403: Draft access denied")
        session.post.side_effect = RuntimeError("offline failure")
        assert client.create_draft(article) == (False, "Draft creation error: offline failure")


def test_substack_login_failure_does_not_create_draft(article):
    client = substack.SubstackPublisher("author@example.invalid", "unused", "example")
    with patch.object(substack, "requests") as requests:
        requests.Session.return_value.post.return_value = Mock(ok=False, status_code=401)
        assert client.create_draft(article) == (False, "Invalid email or password")
        assert requests.Session.return_value.post.call_count == 1
        assert client.session is None
        assert client.create_draft(article) == (False, "Invalid email or password")
        assert requests.Session.return_value.post.call_count == 2
        assert requests.Session.return_value.post.call_args.args[0] == "https://substack.com/api/v1/login"
