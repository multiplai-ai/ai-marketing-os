"""Deterministic contracts for the standalone GEO Audit tool."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import geo_audit


def test_url_slug_is_stable_and_safe() -> None:
    assert geo_audit.url_to_slug("https://example.com/resources/AI-answer-guide/") == "resources-AI-answer-guide"
    assert geo_audit.url_to_slug("https://example.com/") == "example-com"


def test_weighted_score_stays_within_report_range() -> None:
    signals = [
        geo_audit.ContentSignal("first_30_answer", 100, "High", "fixture"),
        geo_audit.ContentSignal("qa_h2s", 0, "High", "fixture"),
    ]
    assert geo_audit.compute_overall_score(signals) == 50.0


@pytest.mark.integration
def test_local_html_audit_never_needs_network(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pytest.importorskip("bs4")
    pytest.importorskip("textstat")
    import nltk
    from nltk.corpus.reader import CMUDictCorpusReader
    from textstat.backend.utils import get_cmudict

    corpus = tmp_path / "nltk_data/corpora/cmudict"
    corpus.mkdir(parents=True)
    (corpus / "cmudict").write_text(
        "TEAMS 1 T IY1 M Z\nPLAN 1 P L AE1 N\nWORKSHOP 1 W ER1 K SH AA2 P\n"
    )
    monkeypatch.setattr(nltk.data, "path", [str(tmp_path / "nltk_data")])
    monkeypatch.setattr(nltk.corpus, "cmudict", CMUDictCorpusReader(str(corpus), ["cmudict"]))
    get_cmudict.cache_clear()

    def deny(*args, **kwargs):
        raise AssertionError("local HTML audit must stay offline")

    import socket
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    html = "<html><head><title>Fictional Workshop</title></head><body><main>" \
        "<h1>How do teams plan a workshop?</h1><p>" + (
            "Teams plan a workshop by choosing one task and writing a short brief. "
            "The fictional Acorn team saves notes in a shared folder. "
        ) * 8 + "</p></main></body></html>"

    result = geo_audit.audit_html(
        html,
        "https://example.invalid/workshop",
        domain=None,
        brand=None,
        run_remote_checks=False,
    )
    assert result.fetch_ok
    assert result.word_count > 100
    assert 0 <= result.overall_score <= 100
    report = geo_audit.write_audit_md(result, tmp_path)
    assert report.is_file()
    assert "not industry benchmarks or guarantees" in report.read_text()
    get_cmudict.cache_clear()
