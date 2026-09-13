# Agent contract

This repository owns only procedures proven shared by two or more active
operating repositories and platform-level contracts that must remain globally
consistent. Entity-exclusive procedures belong in that entity's repository
under `sops/<id>/`.

Edit shared workflow source only in `sops/<id>/SKILL.md`, regenerate the workflow
library, run validation, and use a reviewed PR. Never add client-specific values. Do not
keep synchronized core and local copies: promotion into core or a fork out of
core is an explicit ownership migration.
