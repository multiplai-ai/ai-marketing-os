# Author, review, and release gates

## Author a procedure

Establish shared-library ownership before editing: use in two active consumers or a
platform contract. State trigger, necessary inputs, observable output, source
boundary, side effects, missing-input fallback, and neighboring workflow routes.
Keep conditional reference material behind explicit pointers; remove obsolete
account defaults and invented connector names. Keep one canonical procedure.

Use the human-writing standard for precise, meaning-preserving prose. Define
normal, missing-input, wrong-route and untrusted-input cases before claiming a
workflow is evaluated. Save actual outputs and actions, then have a separate
reviewer compare them with the source facts and case criteria. A fabricated claim
or unauthorized external action fails regardless of formatting. Do not claim a
blinded old/new experiment if only a new version was run.

## Review a contribution

Record the base commit and compare the proposed diff with requirements. Review
ownership/intent separately from implementation and actual output usefulness.
Check dependency setup, source references, the workflow library, negative paths,
side effects, installation compatibility and release impact. Simplify only changed
code and prose; do not add overlapping instruction bundles. Run the exact command
in CONTRIBUTING.md. When main advances, integrate it deliberately, regenerate the library,
and rerun affected checks. Preserve uncommitted work and surface ambiguous
conflicts rather than forcing or staging everything.

No CI success or agent review substitutes for the required human maintainer
review. Branches are review units, never authorization for direct main pushes,
auto-merge, release signing or public visibility changes.

## Server-side release controls

The intended main protection payload is `.github/main-protection.proposed.json`:
require the core check on an up-to-date branch, resolved conversations, and
administrator enforcement. Prohibit force pushes and deletion. The repository
currently has one GitHub collaborator, so a required independent GitHub review
would prevent every merge. Require explicit owner authorization before a solo
maintainer merges; restore required GitHub reviews when another maintainer is
available. Read back the actual GitHub settings after applying; a checked-in
file alone does not enforce these controls.

The `release` environment must require owner approval and main-only deployment.
Keep signing secrets in that environment. The workflow validates the source and
built archive before signing, tests a signed member installation, and publishes
a new preview version without overwriting old assets. Review a channel-version
change before each release. Keep production keys outside the repository.

A new public snapshot must use the distribution allowlist and clean history.
The existing private repository remains historical; do not synchronize future
SOP edits into two canonical repositories. Existing private consumers keep their
pins until an explicit reviewed migration.
