"""Regression cases for metadata and generated discovery defects missed by rc.12 CI."""
from pathlib import Path
import shutil
import pytest
import yaml

from tools.validate_sop_canon import validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def canon(tmp_path):
    (tmp_path / "schemas").mkdir()
    shutil.copy(ROOT / "schemas/sop.schema.yaml", tmp_path / "schemas/sop.schema.yaml")
    package = tmp_path / "sops/example"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text("---\nname: example\ndescription: Draft a fixture example.\n---\n\n# Example\n")
    (package / "sop.yaml").write_text(yaml.safe_dump({
        "id": "example", "version": "1.0.0", "title": "Example",
        "maturity": "internal", "inputs": [], "outputs": [], "tools": [],
        "approval_classes": [], "tests": [], "source_provenance": "portable-core-v1",
    }))
    (tmp_path / "sops/manifest.yaml").write_text("sops: [example]\n")
    (tmp_path / "provenance.yaml").write_text("sop_count: 1\n")
    return tmp_path


def test_repository_obeys_published_contract():
    assert validate(ROOT) == []


def test_valid_package(canon):
    assert validate(canon) == []


@pytest.mark.parametrize("key,value", [
    ("inputs", [{"dataset": "responses"}]),
    ("outputs", [{"artifact_path": "example.md"}]),
    ("version", "not-semver"), ("maturity", "invented-status"),
    ("unknown_key", True), ("source_provenance", "/private/path"),
    ("source_provenance", "../outside"), ("source_provenance", "C:\\private\\path"),
    ("approval_classes", "review"), ("tests", "tests/test_example.py"),
])
def test_schema_rejects_invalid_metadata(canon, key, value):
    path = canon / "sops/example/sop.yaml"
    data = yaml.safe_load(path.read_text())
    data[key] = value
    path.write_text(yaml.safe_dump(data))
    assert validate(canon)


@pytest.mark.parametrize("key", ["source_provenance", "approval_classes", "tests", "version"])
def test_schema_requires_contract_fields(canon, key):
    path = canon / "sops/example/sop.yaml"
    data = yaml.safe_load(path.read_text())
    del data[key]
    path.write_text(yaml.safe_dump(data))
    assert any("required property" in error for error in validate(canon))


@pytest.mark.parametrize("content", ["[broken", "[]", "null"])
def test_invalid_yaml_reports_error_instead_of_crashing(canon, content):
    (canon / "sops/example/sop.yaml").write_text(content)
    assert validate(canon)


@pytest.mark.parametrize("header", [
    "# Missing frontmatter\n", "---\nname: example\n", "---\n[]\n---\n",
    "---\nname: wrong\ndescription: text\n---\n",
    "---\nname: example\ndescription: []\n---\n",
])
def test_invalid_discovery_metadata(canon, header):
    (canon / "sops/example/SKILL.md").write_text(header)
    assert validate(canon)


@pytest.mark.parametrize("reference", ["tests/absent.py", "../outside.py"])
def test_declared_tests_must_exist_inside_repository(canon, reference):
    (canon.parent / "outside.py").write_text("pass\n")
    path = canon / "sops/example/sop.yaml"
    data = yaml.safe_load(path.read_text())
    data["tests"] = [reference]
    path.write_text(yaml.safe_dump(data))
    assert any("declared test" in error for error in validate(canon))


@pytest.mark.parametrize("reference", ["tools/missing.py", "[guide](references/missing.yaml)"])
def test_missing_referenced_resources(canon, reference):
    path = canon / "sops/example/SKILL.md"
    path.write_text(path.read_text() + reference + "\n")
    assert any("missing tool" in error or "missing package reference" in error for error in validate(canon))


@pytest.mark.parametrize("relative", ["sops/manifest.yaml", "provenance.yaml", "sops/example/SKILL.md"])
def test_required_inventory_files(canon, relative):
    (canon / relative).unlink()
    assert validate(canon)


def test_manifest_inventory_must_match(canon):
    (canon / "sops/manifest.yaml").write_text("sops: [example, removed]\n")
    assert any("manifest" in error for error in validate(canon))
