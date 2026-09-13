from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates/writing"


def test_required_templates_are_portable_and_complete():
    required = {
        "source-packet.template.yaml": "topic_or_assignment",
        "blog-article/editorial-brief.template.md": "## Required source and evidence",
        "blog-article/draft.template.md": "## Evidence and mechanism",
        "blog-article/editorial-standard.template.md": "source-supported",
        "newsletter/editorial-brief.template.md": "## Body arc and depth",
        "newsletter/draft.template.md": "## Preview opening",
        "newsletter/editorial-standard.template.md": "reader relationship",
        "social-post-type.template.md": "## Evidence references",
        "handoff.template.yaml": "landing_audit",
    }
    forbidden = ("MITL", "Hanna", "Ghost", "Publer", "MultiplAI")
    for relative, marker in required.items():
        text = (TEMPLATES / relative).read_text()
        assert marker in text
        assert not any(term in text for term in forbidden)
        assert "{{" not in text
