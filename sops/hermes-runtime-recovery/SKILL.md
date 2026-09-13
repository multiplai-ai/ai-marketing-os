---
name: hermes-runtime-recovery
description: Diagnose and recover the current live Hermes profile runtime and its Slack front door without exposing credentials or confusing v3 compatibility paths with the approved v4 target. Use when a Hermes profile is running but unresponsive, rejects an authorized Slack operator, reports account_inactive, loses its Slack app installation, or needs a sanitized runtime recovery receipt.
---

# Hermes Runtime Recovery

Treat this as a controlled production operation. Diagnosis is read-only by
default. SSH access, configuration changes, token replacement, service restarts,
Slack app changes, and smoke-test messages each require the applicable explicit
approval.

A general request for a "read-only diagnosis" does not by itself authorize SSH
or access to a production host. Require explicit authority for the named system
and access class, such as the approved G0b Hostinger inventory gate.

## Procedure

1. Identify the affected Hermes profile, front door, symptom, last known good
   time, and approved access level.
2. Read `config/hermes-profiles.yaml`,
   `docs/runbooks/hermes/vps-agent-update.md`, and the applicable gate in
   `docs/projects/brand-os-v4-execution-plan.md`. Confirm the live profile name,
   expected paths, and access authority; do not infer target v4 paths are
   deployed.
3. For Slack authorization or app-installation failures, read
   [references/v3-slack-front-door.md](references/v3-slack-front-door.md) and run
   only the diagnostic steps allowed by the current gate.
4. Capture sanitized evidence: profile name, command class, timestamp, service
   state, error category, expected identity/channel, and whether configured
   aliases are present. Never capture token values, raw message bodies, or broad
   environment dumps.
5. Stop for approval before any mutation. State the exact file, Slack app,
   service, or credential alias that would change and the rollback step.
6. After an approved repair, verify authentication, Socket Mode, channel
   discovery, expected allowlist behavior, and one explicitly approved smoke
   test. Confirm that no other profile or gateway changed.
7. Produce a sanitized receipt with expected versus actual behavior, approved
   actions, verification results, remaining risks, and rollback status.

## Safety Rules

- Never print, diff, paste, or commit `.env` values, OAuth tokens, app tokens,
  session databases, or credential files.
- Do not regenerate a token merely because another diagnostic path is
  inconvenient. Establish which token class or installation is invalid first.
- Do not restart every Hermes service. Scope actions to the approved profile.
- Do not treat a running systemd unit as client that Slack authentication or
  delivery works.
- Do not treat dated recovery notes as current production evidence. Re-verify
  under the applicable gate.
- Do not replace Codex, Hermes, Slack, or another requested platform with a
  local substitute and describe it as recovery.
- Do not use this transitional v3 package to design or emulate the v4 runtime.

## Canon

Keep the reusable recovery procedure here. Keep version-specific commands in
the reference file and deterministic checks in tools when they are introduced.
Legacy runbooks may link here for compatibility but must not copy these steps.
