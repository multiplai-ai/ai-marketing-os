#!/usr/bin/env python3
"""Install the generated, offline-safe consumer validator."""

from __future__ import annotations

import argparse
from pathlib import Path

from consumer_sops import find_repo_root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer-root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = find_repo_root(args.consumer_root)
    source = Path(__file__).resolve().parents[1] / "templates" / "consumer" / "validate_repo.py"
    content = source.read_text(encoding="utf-8")
    target = root / ".multiplai" / "tools" / "validate_repo.py"
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != content:
            print(f"generated consumer validator is stale: {target}")
            return 1
        print("generated consumer validator current")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"generated {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
