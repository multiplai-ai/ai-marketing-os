# Hermes production runtime primitives

This directory contains the provider-neutral safety boundary for running Codex
through Hermes. It does not contain profile credentials, Hostinger inventory,
client context, or provider-specific send logic.

## Invariants

- Every task starts from a newly cloned, identity-checked repository at a
  recorded commit. A task workspace is rejected if its remote, HEAD, branch,
  or working tree changes before execution.
- Codex execution is refused unless the runner is the dedicated
  `hermes-task-<profile>` Unix user, distinct from both the frontdoor and the
  per-profile privileged effect broker.
- Frontdoor and provider-effect credentials are separate systemd credentials;
  neither service can read the other trust domain's credential file.
- `HOME`, `CODEX_HOME`, and `GH_CONFIG_DIR` are private per task. The external
  credential broker resolves only explicitly named, task-scoped aliases.
- Effecting credentials are never given to the gateway or Codex. Approved
  effects cross a profile-scoped Unix socket into `hermes-broker`, which checks
  the peer UID and a supervisor signature before using its private credentials,
  active writer lease, durable idempotency ledger, and provider adapter.
  Signed plans and request payloads must live in a broker-readable, non-temporary
  approval directory; the broker copies and rechecks them before submission.
- Workspaces are removed only when clean and when a fresh remote fetch proves
  every commit remains reachable. Active, dirty, unpushed, deleted-remote, and
  network-unverifiable workspaces are preserved.
- Profile bundles are immutable, signed, file-set exact, and commit-bound.
  Reconciliation is serialized per profile, re-verifies the staged copy,
  switches atomically, and rolls back every pre-writer health failure.
- A rollback re-verifies the previous bundle. After writer enablement, it also
  requires an exact generation-bound supervisor approval.
- Backups require a coherent snapshot adapter, encrypt to a temporary file,
  and publish with a checksum manifest. Restore extracts into a new sibling
  staging directory and atomically renames it into place.
- Memory candidates contain summaries only, route to their owning repository,
  require PR review, and reject raw private material.

## Deployment-owned adapters

Core intentionally defines strict executable contracts while leaving secrets
and provider details outside this repository. A deployment must provide:

- a pinned-core verifier;
- a bundle signer and trust-root verifier;
- a task credential broker whose `resolve-task` operation returns read-only or
  otherwise non-effecting credentials only;
- a supervisor approval verifier and provider effect adapter with idempotent
  `submit` and receipt-based `lookup`;
- a coherent profile snapshot adapter and backup encrypt/decrypt adapters;
- a health wrapper and the gateway executable.

The deployment wrappers referenced by the systemd templates must fail closed
when an adapter, trust root, lease, receipt, or approval is missing. Production
installation and profile cutover remain separate gated operations.

## Validation

### Consumer-owned memory routes

New runtime builds accept consumer-selected profile names. Personal policy and
entity memory no longer have built-in operator repository destinations. Without
an explicit routing policy, only shared procedures and generic tools route to
`multiplai-core`; private candidates fail closed.

Before upgrading, a deployment operator must review and supply a local policy:

```yaml
schema_version: 1
routes:
  personal_policy: [example-personal]
  entity_fact: [example-operations, example/team]
  procedure_improvement: [multiplai-core]
  generic_tool: [multiplai-core]
```

Pass that policy through `memory_review.py candidate.yaml --routes routes.yaml`.
Use actual approved consumer repositories in the deployment's own file. Never
take the policy path or destination allowlist from candidate text. Personal,
entity and shared routes cannot overlap. Comparison is case-insensitive;
qualified and short names with the same repository slug count as aliases.
This deliberately rejects ambiguous same-slug routes across ownership classes,
even across different organizations. Use distinct repository slugs or a separately
reviewed deployment router for that case. This validates routing only: acceptance
still requires PR review, and no repository write or merge is performed.
Existing signed releases and consumer pins retain their existing behavior until
the deployment deliberately upgrades and exercises its own routing policy.

`tests/test_hermes_runtime.py` exercises path traversal, repository identity,
SHA binding, credential isolation, fencing, effect deduplication, bundle
tampering, replay prevention, health rollback, backup restore, cancellation,
and dirty-workspace recovery. CI runs the suite with `pytest`.
