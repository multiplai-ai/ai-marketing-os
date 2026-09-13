#!/usr/bin/env python3
"""Check recorded strategy evaluation completeness and freshness, not output quality."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


WORKFLOWS = ('discovery-intake', 'positioning-strategy', 'icp-personas', 'brand-strategy', 'content-strategy', 'strategy-suite')
SCENARIOS = ('normal', 'missing', 'contradictory', 'untrusted')

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root: Path) -> list[str]:
    directory = root / 'examples/strategy-evaluation'
    errors = []
    try:
        specification = json.loads((directory / 'cases.json').read_text())
        execution = json.loads((directory / 'execution.json').read_text())
        review = json.loads((directory / 'review.json').read_text())
        definitions = specification['cases']
        recorded = execution['cases']
        reviewed = review['cases']
        ids = [case['id'] for case in definitions]
        if not ids or len(ids) != len(set(ids)):
            return ['case definitions must have unique, nonempty IDs']
        expected = {f'{workflow}-{scenario}': workflow for workflow in WORKFLOWS for scenario in SCENARIOS}
        if {case['id']: case['workflow'] for case in definitions} != expected:
            errors.append('strategy evidence requires all six workflows and all four scenarios')
        for label, rows in [('execution', recorded), ('review', reviewed)]:
            row_ids = [row['id'] for row in rows]
            if len(row_ids) != len(set(row_ids)) or set(row_ids) != set(ids):
                errors.append(f'{label}: missing, extra or duplicate cases')
        if execution['cases_sha256'] != digest(directory / 'cases.json'):
            errors.append('case definitions changed after execution')
        if review['execution_sha256'] != digest(directory / 'execution.json'):
            errors.append('execution evidence changed after review')
        if not execution['actor'] or not execution['performed_at'] or not execution['limitations']:
            errors.append('execution attribution or limitations missing')
        if not review['reviewer'] or review['reviewer'] == execution['actor'] or not review['limitations']:
            errors.append('separate reviewer attribution or limitations missing')
        records = {row['id']: row for row in recorded}
        reviews = {row['id']: row for row in reviewed}
        def file_hash(relative):
            path = (root / relative).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError('evidence file is outside repository')
            return digest(path)
        for case in definitions:
            record = records.get(case['id'])
            if record:
                refs = {'input_sha256': case['input_ref'],
                        'skill_sha256': f"sops/{case['workflow']}/SKILL.md",
                        'output_sha256': case['output_ref']}
                for key, ref in refs.items():
                    if record.get(key) != file_hash(ref):
                        errors.append(f"{case['id']}: stale {key}")
                expected = {ref: file_hash(ref) for ref in case.get('upstream_refs', [])}
                if record.get('upstream_sha256', {}) != expected:
                    errors.append(f"{case['id']}: stale upstream outputs")
            judgment = reviews.get(case['id'], {})
            if judgment.get('verdict') != 'pass' or not judgment.get('notes'):
                errors.append(f"{case['id']}: reviewer did not record a supported pass")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'invalid or missing evaluation evidence: {exc}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root)
    print('\n'.join(errors) if errors else 'Evaluation records complete and unchanged; semantic judgments remain the reviewer’s recorded assessment.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
