#!/usr/bin/env python3
"""Review memory candidates using operator-selected consumer ownership routes."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import yaml
from hermes_common import HermesError

KINDS = {"personal_policy", "entity_fact", "procedure_improvement", "generic_tool"}
DEFAULT_ROUTES = {"procedure_improvement": {"multiplai-core"}, "generic_tool": {"multiplai-core"}}
FORBIDDEN = ("raw transcript", "email body", "calendar content", "token", "secret key", "session cookie", "client dataset")
DESTINATION = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*(?:/[a-zA-Z0-9][a-zA-Z0-9_.-]*)?$")


def load_routes(path: Path | None) -> dict[str, set[str]]:
    if path is None:
        return DEFAULT_ROUTES
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "routes"} or data["schema_version"] != 1:
        raise HermesError("invalid memory routing policy")
    routes = data["routes"]
    if not isinstance(routes, dict) or not routes or set(routes) - KINDS:
        raise HermesError("invalid memory routing policy kinds")
    for destinations in routes.values():
        if not isinstance(destinations, list) or not destinations or any(not isinstance(d, str) or not DESTINATION.fullmatch(d) or d in {'.', '..'} for d in destinations):
            raise HermesError("memory routes must list explicit repository identifiers")
    # Ownership categories must not silently share a destination. Generic tools
    # and shared procedures may share Core; private policy and entity facts may not.
    # Compare repository slugs case-insensitively and conservatively treat a
    # qualified and short name as aliases. Cross-owner same-slug destinations
    # are ambiguous here and must be renamed or handled by a deployment router.
    aliases = lambda values: {value.rsplit("/", 1)[-1].casefold() for value in values}
    core = {"multiplai-core"} | aliases(routes.get("procedure_improvement", [])) | aliases(routes.get("generic_tool", []))
    personal = aliases(routes.get("personal_policy", []))
    entity = aliases(routes.get("entity_fact", []))
    if personal & entity or personal & core or entity & core:
        raise HermesError("memory ownership routes overlap")
    return {kind: {destination.casefold() for destination in destinations} for kind, destinations in routes.items()}


def review(path: Path, routes_path: Path | None = None) -> dict:
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {"schema_version", "kind", "agent", "source_task", "observed_at", "scope", "sensitivity", "confidence", "proposed_destination", "summary"}
    if not isinstance(d, dict) or set(d) != required or d.get("schema_version") != 1:
        raise HermesError("invalid memory candidate contract")
    if not all(isinstance(d[key], str) and d[key].strip() for key in required - {"schema_version", "confidence"}):
        raise HermesError("invalid memory candidate contract")
    if isinstance(d["confidence"], bool) or not isinstance(d["confidence"], (int, float)):
        raise HermesError("invalid memory candidate contract")
    if d["kind"] not in KINDS or d["scope"] not in {"profile", "entity", "repository", "core"} or d["sensitivity"] not in {"public", "internal", "confidential"} or not 0 <= d["confidence"] <= 1:
        raise HermesError("memory candidate is not promotable")
    try:
        datetime.fromisoformat(d["observed_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise HermesError("invalid observed_at") from exc
    if any(term in d["summary"].lower() for term in FORBIDDEN):
        raise HermesError("memory candidate contains prohibited raw/private material")
    routes = load_routes(routes_path)
    route = d["proposed_destination"].casefold()
    if route not in routes.get(d["kind"], set()):
        raise HermesError("memory destination does not match ownership route; configure an operator-approved --routes policy")
    return {"accepted": True, "route": route, "auto_merge": False, "requires_pr_review": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--routes", type=Path, help="operator-approved consumer routing YAML; never supplied by candidate content")
    args = parser.parse_args()
    try:
        print(json.dumps(review(args.candidate, args.routes), sort_keys=True))
        return 0
    except (HermesError, OSError, yaml.YAMLError) as exc:
        print(json.dumps({"accepted": False, "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
