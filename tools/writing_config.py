#!/usr/bin/env python3
"""Load and validate consumer-owned writing configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema
import yaml


CORE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = CORE_ROOT / "schemas"


def load_yaml(path: Path) -> dict:
    """Load a YAML mapping with a useful error for malformed inputs."""
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"could not read YAML {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"expected a YAML mapping: {path}")
    return payload


def safe_consumer_ref(root: Path, value: str, *, require_file: bool = True) -> Path:
    """Resolve a consumer-relative path without allowing traversal."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("reference must be a non-empty relative path")
    raw = Path(value)
    if raw.is_absolute():
        raise ValueError(f"reference must be relative to consumer root: {value}")
    resolved_root = root.resolve()
    candidate = (resolved_root / raw).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"reference escapes consumer root: {value}") from exc
    if require_file and not candidate.is_file():
        raise ValueError(f"referenced file does not exist: {value}")
    return candidate


def _schema_errors(name: str, payload: dict) -> list[str]:
    schema = load_yaml(SCHEMA_ROOT / name)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
        where = ".".join(str(part) for part in error.absolute_path) or "document"
        errors.append(f"{where}: {error.message}")
    return errors


def _check_ref(root: Path, label: str, value: str, *, substantive: bool = False) -> list[str]:
    try:
        path = safe_consumer_ref(root, value)
        if substantive and not path.read_text(encoding="utf-8").strip():
            return [f"{label}: referenced file is empty: {value}"]
    except (ValueError, OSError) as exc:
        return [f"{label}: {exc}"]
    return []


def validate_profile(root: Path, profile: dict) -> list[str]:
    """Return all correctable profile errors."""
    errors = _schema_errors("writing-profile.schema.yaml", profile)
    if errors:
        return errors
    errors.extend(_check_ref(root, "voice_guide_ref", profile["voice_guide_ref"], substantive=True))
    for group in ("good_exemplars", "bad_exemplars"):
        for item in profile[group]:
            errors.extend(_check_ref(root, f"{group}.{item['id']}", item["path"], substantive=True))
    for field in (
        "writing_profile_ref",
        "article_asset_catalog_ref",
        "editorial_standard_ref",
    ):
        if profile.get(field):
            errors.extend(_check_ref(root, field, profile[field]))
    if profile.get("production_log_ref"):
        try:
            safe_consumer_ref(root, profile["production_log_ref"], require_file=False)
        except ValueError as exc:
            errors.append(f"production_log_ref: {exc}")
    for field in ("good_exemplar_refs", "bad_exemplar_refs", "additional_quality_gate_refs"):
        for index, ref in enumerate(profile.get(field, [])):
            errors.extend(_check_ref(root, f"{field}[{index}]", ref, substantive=True))
    if profile.get("default_output_root"):
        try:
            safe_consumer_ref(root, profile["default_output_root"], require_file=False)
        except ValueError as exc:
            errors.append(f"default_output_root: {exc}")
    return errors


def validate_catalog(root: Path, catalog: dict) -> list[str]:
    """Return all correctable asset-catalog errors."""
    errors = _schema_errors("writing-asset-catalog.schema.yaml", catalog)
    if errors:
        return errors
    ids = [item["id"] for item in catalog["asset_types"]]
    if len(ids) != len(set(ids)):
        errors.append("asset_types: duplicate asset IDs are not allowed")
    for asset in catalog["asset_types"]:
        asset_id = asset["id"]
        for field in ("editorial_brief_ref", "template_ref"):
            errors.extend(_check_ref(root, f"{asset_id}.{field}", asset[field], substantive=True))
        for field in ("standards_refs", "good_exemplar_refs", "bad_exemplar_refs"):
            for index, ref in enumerate(asset[field]):
                errors.extend(_check_ref(root, f"{asset_id}.{field}[{index}]", ref, substantive=True))
        if asset["kind"] == "social_post":
            for evidence_class, refs in asset["evidence_classes"].items():
                for index, ref in enumerate(refs):
                    errors.extend(_check_ref(root, f"{asset_id}.{evidence_class}[{index}]", ref, substantive=True))
    return errors


def validate_document(schema_name: str, payload: dict[str, Any]) -> list[str]:
    """Validate another writing contract by schema filename."""
    return _schema_errors(schema_name, payload)
