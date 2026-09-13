#!/usr/bin/env python3
"""Generate pointer-only Codex skill adapters in an operating repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from consumer_sops import (
    ConsumerSopError,
    find_repo_root,
    generate_adapters,
    validate_consumer_bootstrap,
    write_adapters,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer-root", type=Path, default=Path.cwd())
    parser.add_argument("--core-root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        root = find_repo_root(args.consumer_root)
        expected = generate_adapters(root, args.core_root)
        if args.check:
            stale = validate_consumer_bootstrap(root)
            adapter_root = root / ".agents" / "skills"
            actual_ids = {p.name for p in adapter_root.iterdir() if p.is_dir()} if adapter_root.is_dir() else set()
            if actual_ids != set(expected):
                stale.append("adapter set")
            stale.extend(
                str(adapter_root / sop_id / "SKILL.md")
                for sop_id, content in expected.items()
                if not (adapter_root / sop_id / "SKILL.md").is_file()
                or (adapter_root / sop_id / "SKILL.md").read_text(encoding="utf-8") != content
            )
            if stale:
                print("stale generated consumer routing: " + ", ".join(stale))
                return 1
            print(f"generated adapters current: {len(expected)}")
            return 0
        write_adapters(root, expected)
        print(f"generated {len(expected)} consumer adapters")
        return 0
    except ConsumerSopError as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
