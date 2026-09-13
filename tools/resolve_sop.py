#!/usr/bin/env python3
"""Resolve one local or exact-pinned core SOP for an operating repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from consumer_sops import (
    ConsumerSopError,
    find_repo_root,
    materialize_package,
    resolution_receipt,
    resolve_sop,
)
from core_install import CoreInstallError, ensure_core_install


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer-root", type=Path, default=Path.cwd())
    parser.add_argument("--sop-id", required=True)
    parser.add_argument("--core-root", type=Path)
    parser.add_argument("--materialize", type=Path)
    parser.add_argument("--require-installed", action="store_true")
    parser.add_argument("--ensure-installed", action="store_true")
    parser.add_argument("--release-dir", type=Path)
    parser.add_argument("--public-key-file", type=Path)
    parser.add_argument("--allow-unsigned-development", action="store_true")
    parser.add_argument("--repository", default=None)
    args = parser.parse_args()
    try:
        root = find_repo_root(args.consumer_root)
        if args.ensure_installed:
            ensure_core_install(
                root,
                release_dir=args.release_dir,
                public_key_file=args.public_key_file,
                allow_unsigned=args.allow_unsigned_development,
                repository=args.repository,
            )
        package, binding, binding_path, lock = resolve_sop(
            root,
            args.sop_id,
            args.core_root,
            require_installed=args.require_installed or args.ensure_installed,
        )
        receipt = resolution_receipt(root, package, binding, binding_path, lock)
        if args.materialize:
            receipt["materialized_path"] = str(materialize_package(package, args.materialize))
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (ConsumerSopError, CoreInstallError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
