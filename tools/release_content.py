"""Explicit member-distribution boundary, shared by the builder and source check.

This is an inclusion policy, not a license or proof of provenance. New top-level
content and documentation require an intentional policy update in a reviewed PR.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath

ROOT_FILES = {
    "AGENTS.md", "README.md", "CONTRIBUTING.md", "SECURITY.md", "NOTICE",
    "NOTICE.md", "LICENSE", "LICENSE.md", "pyproject.toml", ".gitignore",
    "provenance.yaml", "CODEOWNERS", "BEGINNER-GIT-WORKFLOW.md",
}
SOURCE_DIRS = {"sops", "tools", "schemas", "generated", "runtime", "templates", "tests", ".github"}
DOCUMENTS = {
    "docs/member-guide.md", "docs/capabilities.md", "docs/readiness-report.md",
    "docs/maintainer-guide.md", "releases/TRUST.md", "releases/trust/minisign.pub",
    "archive/brand-history.json", "docs/public-readiness.md", "docs/third-party-review.md",
    "docs/workflow-testing.md", "releases/channel.json",
}


def included(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return bool(parts) and (
        path in ROOT_FILES or path in DOCUMENTS or parts[0] in SOURCE_DIRS
        or path.startswith("examples/member-demo/")
        or path.startswith("examples/strategy-evaluation/")
    )


def path_issue(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if not parts or path.startswith("/") or any(p in {"..", "."} for p in parts):
        return "unsafe archive path"
    for part in parts:
        low = part.lower()
        if low == ".env" or low.startswith(".env."):
            return "environment files are never release inputs (use a named template)"
        if low in {".git", ".ssh", ".aws", "__pycache__", ".pytest_cache", ".ds_store", "node_modules", ".venv"}:
            return "local or generated state is not a release input"
        if low in {"id_rsa", "id_ed25519", "credentials.json", "token.json"} or low.endswith((".pem", ".key", ".p12", ".pfx", ".pyc")):
            return "credential or local binary path is not a release input"
    return None


# High-confidence checks; this cannot establish absence of every secret. Keep
# private operator documents out using included(), even when no pattern matches.
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)
HOST_PATH = re.compile(rb"/(?:Users|home)/[A-Za-z0-9_.-]+/")


def content_issues(path: str, data: bytes) -> list[str]:
    issues = []
    if any(pattern.search(data) for pattern in SECRET_PATTERNS):
        issues.append("possible credential material")
    # Test fixtures intentionally contain rejected inputs; still scan secrets.
    if not path.startswith("tests/") and HOST_PATH.search(data):
        issues.append("host-specific home path; use a consumer binding or environment variable")
    return issues
