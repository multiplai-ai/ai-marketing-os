---
name: routing-and-notifications
description: Route assistant work to configured owners and apply the consumer notification policy for delegated tasks.
---

# Routing and Notifications

## Resolve ownership

Read the consumer's agent registry and ownership/delegation policy. Resolve the
requesting agent, relevant domain, owning specialist, permitted workspace and
available handoff mechanism. No personal agent name or repository is a shared
default. If no owner is configured, explain the missing route and keep the task
pending with the user; do not grant yourself broader access.

Use the least disruptive authorized path:

1. Continue in the current workspace when the request belongs to its owner.
2. Identify the appropriate specialist when the user should contact them.
3. Dispatch a bounded task through an available supported delegation mechanism
   when delegation is authorized, giving only the context that owner may access.
4. For recurring work, use the consumer-designated scheduling owner and explicit
   target profile only when a schedule is requested or already authorized.

State the handoff clearly. Do not imply a role change inside the current session
grants another specialist's tools, credentials or write scope. A request arriving
in the wrong channel still follows the ownership boundary. Cross-domain work
requires an explicit configured route; do not collect client context merely
because one assistant can technically read it.

## Notifications and task state

Apply the configured communication policy. If the user sends their own external
messages, prepare the exact draft instead of posting a handoff or notification.
An internal task handoff does not authorize an external Slack message.

Preserve existing authorized schedule cadence and destinations. Use the supported
scheduler to inspect matching jobs before creating replacements; do not enable
new recurring runs as an implied side effect of routing. The registry determines
who owns scheduling; a coordinating agent is not universally required.

Keep durable task status in the consumer's configured task store. Notifications
can link to it but should not become a second task database. Report completed,
failed and unverified handoffs accurately; dispatch alone is not completion.
