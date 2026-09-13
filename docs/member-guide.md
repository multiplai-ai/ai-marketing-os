# Codex workspace setup

Start with the signed public preview and a fictional business, then adapt your
own workspace. See [README](../README.md) for the copy-and-paste clone and setup
commands. Python 3.12, Git, zstd, and Minisign are required. Code access does not
include AI/API usage or optional services.

## What you will make

The fictional Riverton Workshop packet feeds a proposed positioning statement,
an offline content brief, and a prose review. Inspect the actual
[business packet](../examples/member-demo/business-context.md),
[brief](../examples/member-demo/example-brief.md), and
[reviewed prose](../examples/member-demo/example-prose.md). The brief labels its
research limits and avoids inventing customer results. These files demonstrate
context reuse; they do not constitute a separately evaluated positioning skill.

## Install and open your workspace

After cloning the public repository and activating its Python environment, run:

```bash
python tools/start_member.py --workspace ../my-marketing
```

The recommended version and public repository come from `releases/channel.json`.
The public key is pinned in the source checkout. Setup downloads without a GitHub
login, verifies signatures and digest, and creates a new consumer repository
outside the source checkout. It installs three adapters and scaffolds writing
configuration. It refuses to overwrite a nonempty directory. If setup reports
partial files, inspect them and retry with a new empty destination after fixing
the cause. Do not delete unrelated work.

Activate the source checkout's Python environment in the terminal used by your
agent. The adapters use `python3`, which must resolve to that Python 3.12
installation with the declared dependencies. In the desktop app, if its terminal
has a different Python, give the agent the full path to the source checkout's
`.venv/bin/python` and ask it to use that interpreter for the resolver and tools.

## First useful result

Open the new consumer directory in your agent. Codex discovers the three `.agents/skills` adapters in this workspace. The explicit resolver path works without relying on
automatic discovery:

```bash
cd /path/to/riverton-workshop
python .multiplai/tools/resolve_sop.py --consumer-root . \
  --sop-id content-brief --require-installed
```

Ask the agent:

> Read SKILL.md in the returned source_ref directory and use
> context/business-context.md. Create an offline content brief for bicycle repair
> scheduling. Save the brief in content/briefs/. Label live SERP research as not
> checked, cite packet source IDs, and use the walkthrough CTA. Do not publish.

The resolver returns `source_ref`, bindings, and tool roots. The agent must read
the returned canonical procedure completely. Replace the fictional packet with
your own source-backed facts in the consumer directory for real work. Do not
change the immutable installation. No supplied example is an approved customer
claim or an approved voice exemplar.

To review a draft, resolve `human-writing-standard`, provide the same source
packet, and request claim findings plus a local deterministic gate. To configure
voice, resolve `writing-setup` and review candidate examples before approving
them. The setup tool's successful validation is structural; it does not approve
taste or prove authentic voice.

## Customize, update, and uninstall

Keep facts and paths in `context/`, `config/writing/`, and `config/sop-bindings/`.
Store outputs in `content/`. Preserve one canonical SOP authority. If a procedure
needs different ownership, propose an explicit fork/migration; never maintain a
second manually synchronized copy. Inspect the [catalog](capabilities.md) before
opting into another workflow.

Updates are reviewed consumer changes: obtain the new approved signed assets,
change the lock's version/commit/digest and desired SOP IDs, then use the approved
checkout's `install_core_bundle.py` to install and verify. Regenerate consumer
adapters after lock/binding changes; inspect that diff and retain your old lock in
Git for rollback to an approved signed version. Do not run first-time scaffolding
against your existing workspace. No automatic update or background job is enabled.

```bash
python /path/to/approved-core/tools/install_core_bundle.py \
  --consumer-root /path/to/riverton-workshop --release-dir /path/to/new-assets \
  --public-key-file /path/to/riverton-workshop/.multiplai/trust/minisign.pub
python /path/to/approved-core/tools/generate_consumer_adapters.py \
  --consumer-root /path/to/riverton-workshop
python /path/to/approved-core/tools/install_core_bundle.py \
  --consumer-root /path/to/riverton-workshop --verify-only
```

To remove the active installation, run the same installer with `--remove`.
This removes the managed installation and receipt, preserving your configuration,
content, lock and adapters. Adapters can reinstall the pinned release if invoked;
to stop using them, remove only the three generated starter skill directories
after reviewing their paths. Never delete the business workspace as an uninstall
step. Installation, failed-signature handling and removal have automated tests;
signed update/rollback preservation has additional regression coverage. Claude
plugin discovery is verified with the Claude loader. An interactive signed-update
session remains unverified.

## Troubleshooting and support scope

- Missing module: activate Python 3.12 and install the documented extra. A base
  installation covers configuration/resolution; `publishing` adds Markdown
  preview dependencies. Help works before optional publisher setup.
- Signature mismatch: stop. Confirm the independently pinned key and exact
  approved asset set; do not bypass verification.
- Receipt/binding drift: inspect the changed lock/binding and reinstall deliberately
  after review. Do not edit receipt hashes or chmod the installation to write.
- Missing connector: use local source documents and explicit research limits when
  the procedure permits it. Substack uses an unofficial API and may require manual
  editor entry. Live Ghost/Substack and other external writes were not tested.
- Supported test environment: Python 3.12 on macOS arm64 locally, plus Ubuntu CI
  as recorded in the readiness report. Windows, other Python versions, Cursor
  discovery, and native Windows setup are unverified. Public downloads
  do not require GitHub entitlement.
