# Contributing to Core

Use a task branch and a reviewed PR. Preserve unfinished work. Never force-push,
auto-stage unrelated files, merge your own change without required review, or
edit a signed installation. Core owns shared procedures proven in two active
operating repositories and globally consistent platform contracts. Entity facts,
credentials, business outputs and exclusive workflows belong in consumer repos.

Edit procedural source in `sops/<id>/SKILL.md`; use references for conditional
background, naming when to read them. Update metadata/tests with the changed
contract. Generate adapters from that source; never hand-edit generated copies.

Use Python 3.12, Git, zstd and Minisign, then run:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,publishing]'
python tools/generate_catalog.py
python tools/check_core.py
```

The content gate checks tracked release inputs: stage an intended deletion/new
file after reviewing its diff so the gate sees the complete proposed inventory.
Stage only paths belonging to your change; do not use blanket staging commands.
Tests create synthetic temporary repositories and ephemeral signing keys. They
must not require production credentials or perform live integration writes.

For a skill change, record a normal, missing-input, wrong-route and untrusted-input
case with actual outputs, sources, tool actions and evaluation limits. Parsing a
manifest is not an agent-output evaluation. A passing phrase gate is not factual
verification. Keep third-party notices when adapting material; cite the source
and do not import large conflicting instruction bundles.

For review, pin the base SHA and independently check requirement coverage,
implementation quality, and output usefulness. Review only relevant code/prose:
remove unnecessary wrappers, swallowed errors, vague steps and unsupported
claims without rewriting unrelated files. Record tests and remaining limits in
the PR. Human maintainer review is separate from agent review and CI.

See [maintainer gates](docs/maintainer-guide.md), the [capability catalog](docs/capabilities.md),
and [security reporting](SECURITY.md). The source is distributed under the root MIT license. Preserve its copyright
notice and separately applicable third-party notices.
