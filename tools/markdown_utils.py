"""Shared Markdown parsing for optional publishing integrations.

Parsing never loads credentials or connects to a service. Install the publishing
extra for YAML frontmatter and Markdown rendering: ``pip install '.[publishing]'``.
"""

import re
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Read an optional opening YAML mapping, preserving the remaining Markdown.

    Empty frontmatter is allowed; malformed, duplicate-key, non-mapping, and
    unclosed frontmatter raise ValueError rather than being silently published.
    """
    content = content.removeprefix("\ufeff")
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, content
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
    if end is None:
        raise ValueError("Frontmatter is missing its closing --- delimiter")
    try:
        import yaml
    except ImportError as exc:
        raise ImportError("YAML frontmatter requires PyYAML; install with: pip install '.[publishing]'") from exc

    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            if not isinstance(key, str):
                raise ValueError("Frontmatter keys must be strings")
            if key in result:
                raise ValueError(f"Duplicate frontmatter key: {key}")
            result[key] = loader.construct_object(value_node)
        return result

    UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        metadata = yaml.load("".join(lines[1:end]), Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML frontmatter: {exc}") from exc
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("Frontmatter must be a YAML mapping")
    return metadata, "".join(lines[end + 1:]).lstrip("\r\n")


def extract_title(content: str, filepath: Path) -> str:
    """Use the first H1 or a readable filename when no title is supplied."""
    _, body = extract_frontmatter(content)
    heading = re.search(r"^#\s+(.+?)\s*#*\s*$", body, re.MULTILINE)
    return heading.group(1).strip() if heading else filepath.stem.replace("-", " ").replace("_", " ")


def strip_title_heading(body: str) -> str:
    """Remove only a leading H1 (including a file with no final newline)."""
    return re.sub(r"\A[\r\n]*# [^\r\n]*(?:\r?\n|$)", "", body, count=1)


def text_field(metadata: dict, name: str, default: str = "") -> str:
    """Reject YAML objects where the publisher expects a text value."""
    value = metadata.get(name)
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError(f"Frontmatter '{name}' must be a string")
    return value


def parse_tags(value) -> list[str]:
    """Accept YAML string lists or the legacy comma-separated representation."""
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, list) or any(not isinstance(tag, str) for tag in value):
        raise ValueError("Frontmatter 'tags' must be a string or a list of strings")
    return [tag.strip() for tag in value if tag.strip()]


def markdown_to_html(content: str) -> str:
    """Render author-supplied Markdown, including tables and fenced code.

    Raw HTML is preserved for trusted author drafts; this is not an HTML sanitizer.
    """
    try:
        import markdown
    except ImportError as exc:
        raise ImportError("Markdown rendering requires Markdown; install with: pip install '.[publishing]'") from exc
    return markdown.markdown(content, extensions=["extra", "sane_lists"])
