#!/usr/bin/env python3
"""Validate consumer-owned writing profile and asset catalog."""

import argparse
from pathlib import Path

from writing_config import load_yaml, safe_consumer_ref, validate_catalog, validate_profile


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-root", required=True, type=Path)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--catalog", required=True)
    args = parser.parse_args(argv)
    try:
        profile_path = safe_consumer_ref(args.consumer_root, args.profile)
        catalog_path = safe_consumer_ref(args.consumer_root, args.catalog)
        profile = load_yaml(profile_path)
        catalog = load_yaml(catalog_path)
        errors = validate_profile(args.consumer_root, profile)
        errors.extend(validate_catalog(args.consumer_root, catalog))
    except ValueError as exc:
        errors = [str(exc)]
    if errors:
        print("FAIL: writing configuration is invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: writing configuration is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
