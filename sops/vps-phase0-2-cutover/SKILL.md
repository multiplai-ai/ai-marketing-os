---
name: vps-phase0-2-cutover
description: Consult legacy VPS inventory and cutover reference material; do not use this runbook to execute a current runtime cutover.
---

# Legacy VPS Inventory and Cutover Reference

This procedure retains reusable inventory and rollback considerations from a
retired runtime migration. It does not authorize a cutover, describe a running
installation or replace a consumer's current deployment plan. Profile names,
repository URLs, host paths, branches and services must come from that plan.

For current Core runtime contracts, consult `runtime/hermes/` and
`docs/maintainer-guide.md`, together with the consumer-owned deployment policy.
Do not restore historical direct-to-main push procedures or copy old account
routing into a new installation.

## Read-only inventory

Resolve the target host and profile list first. If the installed Hermes version
supports these commands, they can establish current state:

```bash
hermes profile list
hermes -p <profile> config path
hermes -p <profile> cron list
hermes -p <profile> mcp list
hermes -p <profile> gateway status
```

Replace `<profile>` with the verified consumer profile; inspect CLI help if the
syntax differs. Record connection names, paths and service status privately.
Never print credential/token contents. Inspect repository status and the actual
operating branch without switching branches or resetting unfinished work.

For each profile, determine:

- workspace ownership and repository root;
- relevant scheduled jobs and delivery destinations;
- gateway, webhook and service dependencies;
- credential scopes and accessible resources;
- persistent memory, local changes and unique state requiring preservation.

A gateway being up does not prove end-to-end functionality. Record what was
actually checked and distinguish untested connections from failures.

## Preconditions for an owner-approved migration plan

These are planning requirements, not execution instructions:

1. Define source and destination state, affected profiles, authorized writes,
   success checks and a stopping condition in the consumer's current plan.
2. Preserve unfinished repository work. Use reviewed task branches and PRs for
   source/configuration changes; do not push migration edits directly to `main`.
3. Keep profile backups outside Git in protected consumer storage because they
   may contain credentials, session state and personal context. Verify the
   backup is readable and specify who can restore it.
4. Identify each service and scheduler that references a profile before planning
   its retirement. Preserve unique memory and configuration with access controls.
5. Use the host's supported workspace manager for isolation. In Codex, use
   app-managed worktrees; a manual worktree requires explicit owner authorization.
6. Document rollback triggers and restoration steps before changing production.
   Do not delete old profiles, remote branches or backups as an inventory step.

## Verification and close-out

A current migration plan should verify each affected profile's repository root,
required context, gateway, schedule and authorized connections. Also check the
negative boundary: another consumer's credentials or data must not appear in its
workspace. Live external-message tests require the user's permission and must
respect their communication policy; use read-only or local checks otherwise.

Report failed and unverified checks, preserved work and privately recorded backup
locations. Do not declare a migration complete based on metadata parsing or a
successful service restart alone. Keep this legacy reference out of the current
execution path; consumer deployment changes belong in the owning repository.
