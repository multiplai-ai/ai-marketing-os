"""Public Claude plugin packaging checks."""
from __future__ import annotations

import json
from pathlib import Path
import zipfile

import yaml

from tools.build_claude_plugin import build


ROOT = Path(__file__).resolve().parents[1]


def test_marketplace_points_to_local_plugin() -> None:
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    entry = marketplace["plugins"][0]

    assert plugin["name"] == "ai-marketing-os"
    assert plugin["skills"] == ["./sops/"]
    assert entry["name"] == plugin["name"]
    assert entry["version"] == plugin["version"]
    assert entry["source"] == "./"


def test_every_manifest_workflow_is_discoverable_by_claude() -> None:
    manifest = yaml.safe_load((ROOT / "sops/manifest.yaml").read_text())
    expected = set(manifest["sops"])
    discovered = {
        path.parent.name
        for path in (ROOT / "sops").glob("*/SKILL.md")
    }

    assert discovered == expected
    assert len(discovered) == 83


def test_removed_pointer_tree_does_not_return() -> None:
    assert not (ROOT / "generated/codex/skills").exists()


def test_uploadable_plugin_has_manifest_and_all_workflows(tmp_path: Path) -> None:
    target = build(ROOT, tmp_path, "4.0.0-rc.14")
    with zipfile.ZipFile(target) as archive:
        names = set(archive.namelist())

    assert ".claude-plugin/plugin.json" in names
    assert ".claude-plugin/marketplace.json" in names
    assert len([name for name in names if name.startswith("sops/") and name.endswith("/SKILL.md")]) == 83
    assert not any(name.startswith("generated/") for name in names)
