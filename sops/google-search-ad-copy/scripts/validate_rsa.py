#!/usr/bin/env python3
"""Check static RSA copy. Exit 0: format pass; 1: errors; 2: manual review.

Usage: python3 validate_rsa.py ads.json
Input: {"ads": [{"name": "A", "headlines": [...], "descriptions": [...],
                 "paths": [...]}]}
This checks format only, never claims, destination alignment, or ad approval.
"""

import json
from pathlib import Path
import sys
import unicodedata


def ad_length(text):
    """ASCII exact; Unicode W/F width approximates Google's double-width rule."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1
               for c in text)


def validate(payload):
    errors, review, counts = [], [], []
    ads = payload.get("ads") if isinstance(payload, dict) else None
    if not isinstance(ads, list) or not ads:
        return {"status": "fail", "errors": ["ads must be a nonempty list"],
                "manual_review": [], "counts": []}
    for number, ad in enumerate(ads, 1):
        label = f"ad {number}"
        if not isinstance(ad, dict):
            errors.append(f"{label}: must be an object")
            continue
        for field, minimum, maximum, limit in (
            ("headlines", 3, 15, 30), ("descriptions", 2, 4, 90),
            ("paths", 0, 2, 15),
        ):
            values = ad.get(field, [])
            if not isinstance(values, list):
                errors.append(f"{label}.{field}: must be a list")
                continue
            if not minimum <= len(values) <= maximum:
                errors.append(f"{label}.{field}: needs {minimum}–{maximum} assets; got {len(values)}")
            seen = set()
            for index, value in enumerate(values, 1):
                key = f"{label}.{field}[{index}]"
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{key}: must be a nonempty string")
                    continue
                length = ad_length(value)
                counts.append({"asset": key, "text": value, "count": length, "limit": limit})
                if length > limit:
                    errors.append(f"{key}: {length} characters exceeds {limit}")
                if value != value.strip():
                    errors.append(f"{key}: leading or trailing whitespace")
                if any(unicodedata.category(c).startswith("C") or c in "\u2028\u2029" for c in value):
                    errors.append(f"{key}: control, hidden, or line-break characters")
                normalized = " ".join(unicodedata.normalize("NFKC", value).casefold().split())
                if normalized in seen and field != "paths":
                    errors.append(f"{key}: duplicate asset")
                seen.add(normalized)
                if any(ord(c) > 127 for c in value):
                    review.append(f"{key}: verify Unicode count/rendering in Google Ads")
                if "{" in value or "}" in value:
                    review.append(f"{key}: dynamic syntax or placeholder needs expansion review")
                if field == "headlines" and "!" in value:
                    review.append(f"{key}: headline exclamation mark; inspect editorial policy")
    return {"status": "fail" if errors else "manual_review" if review else "format_pass",
            "errors": errors, "manual_review": review, "counts": counts}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_rsa.py ads.json", file=sys.stderr)
        return 1
    try:
        result = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "errors": [str(exc)]}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"format_pass": 0, "fail": 1, "manual_review": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
