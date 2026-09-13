#!/usr/bin/env python3
"""Generate the capability inventory from canonical manifests and the starter set."""
from pathlib import Path
import argparse
import yaml
from check_evaluation_evidence import check as check_evidence
from scaffold_member import DEFAULT_SOPS


def render(root: Path) -> str:
    strategy_ids = {'discovery-intake', 'positioning-strategy', 'icp-personas', 'brand-strategy', 'content-strategy', 'strategy-suite'}
    strategy_evaluated = not check_evidence(root)
    text = '''# Capability catalog

The default member set is intentionally three workflows. The two editorial
workflows have eight recorded offline agent-output cases in total; writing setup
has deterministic configuration and preservation tests. These are different kinds
of evidence. See [the readiness report](readiness-report.md).

| Default workflow | Inputs / prerequisites | Output | Actions and fallback | Evidence / maturity | First prompt |
| --- | --- | --- | --- | --- | --- |
| content-brief | Business packet, reader, keyword, desired action; agent with file access | Local brief with source limits and handoff | No publishing; supplied excerpts support an offline brief | Evaluated offline preview; live research unverified | Create an offline brief using context/business-context.md. |
| human-writing-standard | Draft and source packet; voice guide when available | Revised prose, claim findings, deterministic gate report | Local edits only; absent evidence stays unverified | Evaluated offline preview; gate is not a fact checker | Review this draft against our business packet. |
| writing-setup | Consumer directory and author preferences; Python 3.12 base dependencies | Consumer-owned profile, templates, catalog | Creates local configuration; preserves existing files | Mechanically tested setup; human calibration still required | Configure writing; leave exemplars unapproved until I review them. |

All other workflows below are available for inspection and explicit opt-in.
Where a recorded offline evaluation exists, it is identified below; otherwise
task execution remains unverified. Live integration status is unverified. Historical metadata `released`
is not a new readiness endorsement. Read each canonical contract for exact inputs,
outputs, approval classes and tools. Do not enable scheduled agents or external
publishing merely because a procedure exists. Optional integrations may require
paid accounts, credentials and tools that are not installed in your agent.

| Workflow | Canonical title | Historical metadata | Member status | Declared tools |
| --- | --- | --- | --- | --- |
'''
    for path in sorted((root / 'sops').glob('*/sop.yaml')):
        data = yaml.safe_load(path.read_text())
        sid = data['id']
        status = ('Default; evidence above' if sid in DEFAULT_SOPS else
                  'Opt-in; offline cases reviewed; see [test plan](workflow-testing.md)' if strategy_evaluated and sid in strategy_ids else
                  'Opt-in; execution unverified')
        title = data['title'].replace('|', '\\|')
        declared = ', '.join(data['tools']).replace('|', '\\|') or 'None declared'
        text += f'| [{sid}](../sops/{sid}/SKILL.md) | {title} | {data["maturity"]} | {status} | {declared} |\n'
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = args.root / 'docs/capabilities.md'
    expected = render(args.root)
    if args.check:
        if not target.is_file() or target.read_text() != expected:
            parser.exit(1, 'capability catalog stale: run python tools/generate_catalog.py\n')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected)
    print('capability catalog current')

if __name__ == '__main__':
    main()
