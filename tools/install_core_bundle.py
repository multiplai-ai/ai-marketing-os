#!/usr/bin/env python3
"""Install or verify the core release pinned by an operating repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from consumer_sops import ConsumerSopError, find_repo_root, load_core_lock
from core_install import (
    CoreInstallError,
    ensure_core_install,
    install_core_bundle,
    remove_core_install,
    verify_core_install,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer-root", type=Path, default=Path.cwd())
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--release-dir", type=Path)
    parser.add_argument("--artifact-signature", type=Path)
    parser.add_argument("--manifest-signature", type=Path)
    parser.add_argument("--public-key-file", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--allow-unsigned-development", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--ensure-installed", action="store_true")
    parser.add_argument("--repository", default=None)
    args = parser.parse_args()
    try:
        root = find_repo_root(args.consumer_root)
        if args.remove:
            removed = remove_core_install(root, cache_root=args.cache_root)
            receipt = {"removed": str(removed)}
        elif args.ensure_installed:
            receipt = ensure_core_install(
                root,
                release_dir=args.release_dir,
                public_key_file=args.public_key_file,
                allow_unsigned=args.allow_unsigned_development,
                repository=args.repository,
            )
        elif args.verify_only:
            receipt = verify_core_install(root)
        else:
            lock = load_core_lock(root)
            version = lock["core"]["version"]
            artifact = args.artifact
            manifest = args.manifest
            if args.release_dir:
                artifact = artifact or args.release_dir / f"multiplai-core-{version}.tar.zst"
                manifest = manifest or args.release_dir / f"multiplai-core-{version}.manifest.json"
            if artifact is None or manifest is None:
                raise CoreInstallError("provide --release-dir or both --artifact and --manifest")
            public_key = None
            if args.public_key_file:
                public_key = args.public_key_file.read_text(encoding="utf-8").strip()
            receipt = install_core_bundle(
                root,
                artifact,
                manifest,
                artifact_signature=args.artifact_signature,
                manifest_signature=args.manifest_signature,
                public_key=public_key,
                allow_unsigned=args.allow_unsigned_development,
                cache_root=args.cache_root,
            )
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (ConsumerSopError, CoreInstallError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
