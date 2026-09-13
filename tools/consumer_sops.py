#!/usr/bin/env python3
"""Shared implementation for operating-repository SOP ergonomics."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


SOP_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MEANINGFUL_BINDING_KEYS = (
    "connector_aliases",
    "credential_aliases",
    "approver",
    "policy_refs",
    "output_refs",
)
CONSUMER_BOOTSTRAP_MODULES = (
    "resolve_sop.py",
    "consumer_sops.py",
    "core_install.py",
)


class ConsumerSopError(RuntimeError):
    """A configuration cannot be resolved safely."""


@dataclass(frozen=True)
class SopPackage:
    sop_id: str
    metadata: dict[str, Any]
    skill_markdown: str
    source_type: str
    source_ref: str


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConsumerSopError(f"missing required file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConsumerSopError(f"expected a YAML object: {path}")
    return data


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    raise ConsumerSopError(f"not inside a Git repository: {start}")


def entity_id(root: Path) -> str:
    entity_file = root / "entity.yaml"
    if entity_file.is_file():
        value = load_yaml(entity_file).get("id")
        if isinstance(value, str) and value.strip():
            return value.strip()
        raise ConsumerSopError(f"entity.yaml has no valid id: {entity_file}")
    raise ConsumerSopError(f"missing required file: {entity_file}")


def validate_package(
    sop_id: str,
    metadata: dict[str, Any],
    skill: str,
    source: str,
    *,
    require_frontmatter: bool,
) -> None:
    errors: list[str] = []
    if not SOP_ID.fullmatch(sop_id):
        errors.append(f"invalid SOP id: {sop_id!r}")
    if metadata.get("id") != sop_id:
        errors.append(f"SOP id/path mismatch: {sop_id}")
    for key in ("version", "title", "maturity", "inputs", "outputs", "tools"):
        if key not in metadata:
            errors.append(f"{sop_id}: missing {key}")
    if not skill.strip():
        errors.append(f"{sop_id}: empty SKILL.md")
    if require_frontmatter:
        frontmatter = parse_frontmatter(skill)
        if frontmatter.get("name") != sop_id:
            errors.append(f"{sop_id}: SKILL.md frontmatter name must match id")
        if not str(frontmatter.get("description", "")).strip():
            errors.append(f"{sop_id}: SKILL.md frontmatter requires description")
    if errors:
        raise ConsumerSopError(f"{source}: " + "; ".join(errors))


def parse_frontmatter(markdown: str) -> dict[str, Any]:
    if not markdown.startswith("---\n"):
        return {}
    end = markdown.find("\n---\n", 4)
    if end < 0:
        return {}
    parsed = yaml.safe_load(markdown[4:end])
    return parsed if isinstance(parsed, dict) else {}


def discovery_description(package: SopPackage) -> str:
    explicit = str(parse_frontmatter(package.skill_markdown).get("description", "")).strip()
    if explicit:
        return explicit
    body = package.skill_markdown
    paragraphs = re.split(r"\n\s*\n", body)
    summary = next(
        (
            " ".join(paragraph.split())
            for paragraph in paragraphs
            if paragraph.strip()
            and not paragraph.lstrip().startswith(("#", "---", ">", "-", "*", "```"))
        ),
        "",
    )
    prefix = f"Use when the task requires {package.metadata['title']}."
    description = f"{prefix} {summary}".strip()
    return description[:600].rstrip()


def load_local_package(root: Path, sop_id: str) -> SopPackage | None:
    package = root / "sops" / sop_id
    if not package.exists():
        return None
    metadata = load_yaml(package / "sop.yaml")
    skill_path = package / "SKILL.md"
    if not skill_path.is_file():
        raise ConsumerSopError(f"incomplete local SOP package: {package}")
    skill = skill_path.read_text(encoding="utf-8")
    validate_package(sop_id, metadata, skill, str(package), require_frontmatter=True)
    return SopPackage(sop_id, metadata, skill, "local", str(package))


def load_core_lock(root: Path) -> dict[str, Any]:
    data = load_yaml(root / ".multiplai" / "core.lock.yaml")
    core = data.get("core")
    sops = data.get("sops")
    if not isinstance(core, dict) or not isinstance(sops, list):
        raise ConsumerSopError("core lock requires core object and sops array")
    if "repository" in core and (not isinstance(core["repository"], str) or
            not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", core["repository"])):
        raise ConsumerSopError("core lock has invalid repository")
    if "access" in core and core["access"] not in ("public", "private"):
        raise ConsumerSopError("core lock has invalid access")
    if core.get("access") == "public" and "repository" not in core:
        raise ConsumerSopError("public core lock requires repository")
    commit = core.get("commit")
    digest = core.get("digest")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ConsumerSopError("core lock has invalid commit")
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ConsumerSopError("core lock has invalid digest")
    if any(not isinstance(item, str) or not SOP_ID.fullmatch(item) for item in sops):
        raise ConsumerSopError("core lock contains an invalid SOP id")
    if len(sops) != len(set(sops)):
        raise ConsumerSopError("core lock contains duplicate SOP ids")
    return data


def locate_core_root(consumer_root: Path, explicit: Path | None = None) -> Path:
    candidates = []
    if explicit is not None:
        candidates.append(explicit)
    candidates.extend((consumer_root.parent / "multiplai-core", Path(__file__).resolve().parents[1]))
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / ".git").exists() and (resolved / "sops").is_dir():
            return resolved
    raise ConsumerSopError("cannot locate multiplai-core; pass --core-root")


def git_show(core_root: Path, commit: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=core_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ConsumerSopError(f"cannot read pinned core object {commit}:{relative_path}: {detail}")
    return result.stdout


def load_core_package(core_root: Path, lock: dict[str, Any], sop_id: str) -> SopPackage:
    commit = lock["core"]["commit"]
    metadata_text = git_show(core_root, commit, f"sops/{sop_id}/sop.yaml")
    skill = git_show(core_root, commit, f"sops/{sop_id}/SKILL.md")
    metadata = yaml.safe_load(metadata_text)
    if not isinstance(metadata, dict):
        raise ConsumerSopError(f"invalid pinned core metadata for {sop_id}")
    source_ref = f"{core_root}@{commit}:sops/{sop_id}"
    # RC2 and earlier core releases predate Codex skill frontmatter. The
    # adapter derives safe discovery metadata from sop.yaml for those exact
    # pinned releases; newly authored local SOPs must include frontmatter.
    validate_package(sop_id, metadata, skill, source_ref, require_frontmatter=False)
    return SopPackage(sop_id, metadata, skill, "core", source_ref)


def load_installed_core_package(root: Path, lock: dict[str, Any], sop_id: str) -> SopPackage:
    from core_install import CoreInstallError, verify_core_install

    try:
        receipt = verify_core_install(root)
    except CoreInstallError as exc:
        raise ConsumerSopError(str(exc)) from exc
    install_root = Path(receipt["install_root"])
    package = install_root / "sops" / sop_id
    metadata = load_yaml(package / "sop.yaml")
    skill_path = package / "SKILL.md"
    if not skill_path.is_file():
        raise ConsumerSopError(f"installed core SOP is incomplete: {package}")
    skill = skill_path.read_text(encoding="utf-8")
    validate_package(sop_id, metadata, skill, str(package), require_frontmatter=False)
    return SopPackage(sop_id, metadata, skill, "installed-core", str(package))


def load_binding(root: Path, sop_id: str, entity: str) -> tuple[dict[str, Any] | None, Path | None]:
    path = root / "config" / "sop-bindings" / f"{sop_id}.yaml"
    if not path.exists():
        return None, None
    data = load_yaml(path)
    errors = []
    if data.get("sop_id") != sop_id:
        errors.append("sop_id does not match filename")
    if data.get("entity") != entity:
        errors.append(f"entity must be {entity!r}")
    values = data.get("values")
    if not isinstance(values, dict) or not values:
        errors.append("values must be a non-empty object; delete an unnecessary binding")
    forbidden = {"steps", "procedure", "instructions", "runbook"}.intersection(data)
    if forbidden:
        errors.append(f"forbidden procedure keys: {', '.join(sorted(forbidden))}")
    if errors:
        raise ConsumerSopError(f"{path}: " + "; ".join(errors))
    return data, path


def resolve_sop(
    consumer_root: Path,
    sop_id: str,
    core_root: Path | None = None,
    *,
    require_installed: bool = False,
) -> tuple[SopPackage, dict[str, Any] | None, Path | None, dict[str, Any] | None]:
    root = find_repo_root(consumer_root)
    entity = entity_id(root)
    local = load_local_package(root, sop_id)
    lock = load_core_lock(root)
    locked = sop_id in lock["sops"]
    if local and locked:
        raise ConsumerSopError(f"duplicate SOP ownership for {sop_id}: local and core lock")
    if local:
        binding, binding_path = load_binding(root, sop_id, entity)
        if binding is not None:
            raise ConsumerSopError(f"local SOP {sop_id} must not have a core binding: {binding_path}")
        return local, None, None, None
    if not locked:
        raise ConsumerSopError(f"SOP {sop_id!r} is neither local nor allowed by the core lock")
    receipt = root / ".multiplai" / "core.install.json"
    if receipt.exists() or require_installed:
        package = load_installed_core_package(root, lock, sop_id)
    else:
        resolved_core = locate_core_root(root, core_root)
        package = load_core_package(resolved_core, lock, sop_id)
    binding, binding_path = load_binding(root, sop_id, entity)
    return package, binding, binding_path, lock


def resolution_receipt(
    root: Path,
    package: SopPackage,
    binding: dict[str, Any] | None,
    binding_path: Path | None,
    lock: dict[str, Any] | None,
) -> dict[str, Any]:
    tool_roots = [str(root / "tools")]
    if package.source_type == "installed-core":
        install_root = Path(package.source_ref).resolve().parents[1]
        tool_roots.append(str(install_root / "tools"))
    return {
        "schema_version": 1,
        "entity": entity_id(root),
        "consumer_root": str(root),
        "sop_id": package.sop_id,
        "source_type": package.source_type,
        "source_ref": package.source_ref,
        "sop_version": package.metadata.get("version"),
        "binding": str(binding_path) if binding_path else None,
        "binding_values": binding.get("values") if binding else None,
        "core": lock.get("core") if lock else None,
        "context_root": str(root / "context"),
        "tool_roots": tool_roots,
        "skill_sha256": hashlib.sha256(package.skill_markdown.encode()).hexdigest(),
    }


def materialize_package(package: SopPackage, destination: Path) -> Path:
    target = destination.resolve() / package.sop_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(package.skill_markdown, encoding="utf-8")
    (target / "sop.yaml").write_text(
        yaml.safe_dump(package.metadata, sort_keys=False), encoding="utf-8"
    )
    return target


def _minisign_public_key(text: str) -> str:
    """Return one pinned Minisign key line or reject malformed trust input."""
    import base64
    import binascii

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lower().startswith(("untrusted comment:", "trusted comment:"))
    ]
    if len(lines) != 1:
        raise ConsumerSopError("Minisign trust root must contain exactly one public key")
    key = lines[0]
    try:
        decoded = base64.b64decode(key, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ConsumerSopError("Minisign trust root is not valid base64") from exc
    if len(decoded) != 42 or decoded[:2] not in {b"Ed", b"ED"}:
        raise ConsumerSopError("Minisign trust root has an invalid public-key payload")
    return key


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".{path.name}.",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        handle.flush()
        temporary = Path(handle.name)
    temporary.chmod(0o644)
    temporary.replace(path)


def _bootstrap_directory_errors(root: Path) -> list[str]:
    errors = []
    for path in (
        root / ".multiplai",
        root / ".multiplai" / "tools",
        root / ".multiplai" / "trust",
    ):
        if path.is_symlink():
            errors.append(f"consumer bootstrap directory must not be a symlink: {path}")
    return errors


def validate_consumer_bootstrap(
    root: Path,
    *,
    source_tools: Path | None = None,
) -> list[str]:
    """Validate tracked bootstrap modules and the independently pinned trust root."""
    root = find_repo_root(root)
    source = (source_tools or Path(__file__).resolve().parent).resolve()
    target = root / ".multiplai" / "tools"
    errors = _bootstrap_directory_errors(root)
    for name in CONSUMER_BOOTSTRAP_MODULES:
        expected = source / name
        actual = target / name
        if actual.is_symlink():
            errors.append(f"consumer bootstrap module must not be a symlink: {actual}")
        elif not actual.is_file():
            errors.append(f"missing consumer bootstrap module: {actual}")
        elif expected.is_file() and actual.read_bytes() != expected.read_bytes():
            errors.append(f"consumer bootstrap module is stale: {actual}")
    trust = root / ".multiplai" / "trust" / "minisign.pub"
    if trust.is_symlink():
        errors.append(f"consumer trust root must not be a symlink: {trust}")
    elif not trust.is_file():
        errors.append(f"missing pinned core trust root: {trust}")
    else:
        try:
            _minisign_public_key(trust.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ConsumerSopError) as exc:
            errors.append(f"invalid pinned core trust root {trust}: {exc}")
    return errors


def write_consumer_bootstrap(
    root: Path,
    *,
    source_tools: Path | None = None,
    trust_source: Path | None = None,
) -> None:
    """Install the minimum consumer-owned resolver without replacing trust decisions."""
    root = find_repo_root(root)
    source = (source_tools or Path(__file__).resolve().parent).resolve()
    directory_errors = _bootstrap_directory_errors(root)
    if directory_errors:
        raise ConsumerSopError(directory_errors[0])
    module_content: dict[str, str] = {}
    for name in CONSUMER_BOOTSTRAP_MODULES:
        path = source / name
        if not path.is_file():
            raise ConsumerSopError(f"missing bootstrap source module: {path}")
        module_content[name] = path.read_text(encoding="utf-8")

    trust_target = root / ".multiplai" / "trust" / "minisign.pub"
    trust_content: str | None = None
    if trust_target.exists():
        if trust_target.is_symlink() or not trust_target.is_file():
            raise ConsumerSopError(f"consumer trust root must be a regular file: {trust_target}")
        _minisign_public_key(trust_target.read_text(encoding="utf-8"))
    else:
        source_key = trust_source or Path(__file__).resolve().parents[1] / "releases" / "trust" / "minisign.pub"
        if not source_key.is_file():
            raise ConsumerSopError(
                f"cannot initialize consumer trust root; missing reviewed key: {source_key}"
            )
        trust_content = _minisign_public_key(source_key.read_text(encoding="utf-8")) + "\n"

    target = root / ".multiplai" / "tools"
    for name, content in module_content.items():
        _atomic_write(target / name, content)
    if trust_content is not None:
        _atomic_write(trust_target, trust_content)


def adapter_text(package: SopPackage) -> str:
    description = discovery_description(package)
    quoted_description = json.dumps(description)
    if package.source_type == "local":
        route = (
            f"Canonical source: `sops/{package.sop_id}/SKILL.md`. Read that file completely "
            "before procedural work. Do not edit or copy a core version."
        )
    else:
        route = (
            "Resolve the exact pinned procedure before procedural work:\n\n"
            "```bash\n"
            "ROOT=\"$(git rev-parse --show-toplevel)\"\n"
            f"python3 \"$ROOT/.multiplai/tools/resolve_sop.py\" --consumer-root \"$ROOT\" --sop-id {package.sop_id} --ensure-installed\n"
            "```\n\n"
            "Then read `SKILL.md` from the absolute `source_ref` directory in the JSON "
            "receipt completely. Read `tool_roots` from the receipt and, for each relative "
            "tool path declared by the SOP, use the first listed root where that path exists. "
            "Invoke the selected tool by absolute path. That directory is the verified "
            "read-only installation. Do not read a core working tree's current copy as a "
            "substitute for the pinned commit. Never execute runtime tools from an unverified "
            "core working tree."
        )
    return (
        "---\n"
        f"name: {package.sop_id}\n"
        f"description: {quoted_description}\n"
        "---\n\n"
        f"# Routed SOP: {package.metadata['title']}\n\n{route}\n"
    )


def generate_adapters(consumer_root: Path, core_root: Path | None = None) -> dict[str, str]:
    root = find_repo_root(consumer_root)
    lock = load_core_lock(root)
    local_ids = {
        path.name for path in (root / "sops").iterdir() if path.is_dir()
    } if (root / "sops").is_dir() else set()
    duplicates = local_ids.intersection(lock["sops"])
    if duplicates:
        raise ConsumerSopError(f"duplicate local/core SOP ids: {', '.join(sorted(duplicates))}")
    adapters: dict[str, str] = {}
    for sop_id in sorted(local_ids.union(lock["sops"])):
        package, _, _, _ = resolve_sop(root, sop_id, core_root)
        adapters[sop_id] = adapter_text(package)
    return adapters


def write_adapters(root: Path, adapters: dict[str, str]) -> None:
    write_consumer_bootstrap(root)
    target = root / ".agents" / "skills"
    temporary = Path(tempfile.mkdtemp(prefix="skills-", dir=target.parent if target.parent.exists() else root))
    try:
        for sop_id, content in adapters.items():
            package = temporary / sop_id
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text(content, encoding="utf-8")
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary.replace(target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def validate_consumer(root: Path, core_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        root = find_repo_root(root)
        entity = entity_id(root)
        lock = load_core_lock(root)
    except ConsumerSopError as exc:
        return [str(exc)]
    local_ids = set()
    if (root / "sops").is_dir():
        for package in sorted((root / "sops").iterdir()):
            if not package.is_dir():
                continue
            local_ids.add(package.name)
            try:
                load_local_package(root, package.name)
            except ConsumerSopError as exc:
                errors.append(str(exc))
    duplicates = local_ids.intersection(lock["sops"])
    if duplicates:
        errors.append(f"duplicate local/core SOP ids: {', '.join(sorted(duplicates))}")
    binding_dir = root / "config" / "sop-bindings"
    if binding_dir.is_dir():
        for path in sorted(binding_dir.glob("*.yaml")):
            sop_id = path.stem
            if sop_id in local_ids:
                errors.append(f"local SOP must not have a binding: {path}")
            if sop_id not in lock["sops"]:
                errors.append(f"binding targets an unlocked core SOP: {path}")
            try:
                load_binding(root, sop_id, entity)
            except ConsumerSopError as exc:
                errors.append(str(exc))
    try:
        expected = generate_adapters(root, core_root)
        adapter_root = root / ".agents" / "skills"
        actual_ids = {p.name for p in adapter_root.iterdir() if p.is_dir()} if adapter_root.is_dir() else set()
        if actual_ids != set(expected):
            errors.append("generated adapter set is stale; run generate_consumer_adapters.py")
        for sop_id, content in expected.items():
            path = adapter_root / sop_id / "SKILL.md"
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                errors.append(f"generated adapter is stale: {path}")
    except ConsumerSopError as exc:
        errors.append(str(exc))
    errors.extend(validate_consumer_bootstrap(root))
    return errors
