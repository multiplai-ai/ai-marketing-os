---
name: vps-agent-update
description: Review a consumer's legacy VPS agent update procedure; use the current signed runtime workflow for bundle-based installations.
---

# Legacy VPS Agent Update

This reference covers the distinction between repository content and installed
agent instructions in older persistent deployments. It is not evidence that any
particular host or profile is running that architecture. First inspect the
consumer's current deployment plan. For signed bundle installations, follow the
current `runtime/hermes/` contracts and `docs/maintainer-guide.md`; do not mutate
an installed signed release or replace it with a Git pull.

## Resolve the deployment

From the consumer registry, identify the host, target profile, repository or
bundle, intended reviewed revision, generated instruction source, installed path,
update helper and gateway/service manager. Confirm authorization for deployment
and restart; a merged source change alone is not deployment approval.

Inventory each affected profile separately. Keep credentials, session state and
private account mappings in consumer storage. Do not update every profile simply
because several live on one machine.

## Update sequence for an applicable legacy deployment

1. Inspect the target checkout's branch and worktree status. Preserve unfinished
   work; stop on conflicting changes rather than resetting them.
2. Verify the approved source revision and update through the consumer's supported
   deployment command. A fast-forward pull is suitable only when that workflow
   explicitly deploys a tracked branch and the checkout is clean. Record the
   resulting revision rather than assuming every merged change is now live.
3. Determine whether the change affects repository-read content or installed
   instruction files. A repository update does not prove the gateway loaded new
   installed instructions.
4. If the consumer uses an instruction-sync helper, inspect its existence and
   supported CLI. Run its dry-run mode, review the source/destination diff and
   ensure rollback material is preserved before applying an authorized update.
   Do not assume a helper path or backup behavior from another deployment.
5. Restart only affected services when required. Verify installed content and
   gateway status; inspect logs without exposing credential material.
6. Run the planned functional check. Read-only or local tests are preferred when
   external-message delivery is not authorized. If a live message test is allowed,
   use only the configured destination and report the actual result.

## Rollback

Before changing installed instructions, verify a protected backup or previous
immutable bundle is available and that the consumer's restoration command is
known. Use the approved rollback on failed acceptance checks, then verify the
restored version and service state.

Repository changes should be reverted through a reviewed source change when
needed, not by silently editing installed instructions or resetting unrelated
work. Do not claim an instruction rollback also reverted repository content;
report the versions of both layers.

## Boundaries and close-out

Canonical source remains in its owning repository. Generated and installed
instructions are derived artifacts; do not hand-edit them as a permanent fix.
Account access, new integrations and credential-scope changes require their own
consumer configuration workflow.

For gateway/front-door diagnosis, consult
`sops/hermes-runtime-recovery/SKILL.md` and apply its current scope and approval
requirements. Do not treat any historical account or token repair as current
connection evidence.

Report target profiles, source and installed revisions, checks performed, failed
or unverified integrations and rollback status. A service restart alone does not
establish end-to-end readiness.
