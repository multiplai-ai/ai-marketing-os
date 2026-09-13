#!/usr/bin/env python3
"""Validate local/core SOP ownership in an operating repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from consumer_sops import validate_consumer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer-root", type=Path, default=Path.cwd())
    parser.add_argument("--core-root", type=Path)
    args = parser.parse_args()
    errors = validate_consumer(args.consumer_root, args.core_root)
    if errors:
        print("\n".join(errors))
        return 1
    print("consumer SOP configuration valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
