# First public release

The owner approved a clean public repository named `multiplai-ai/ai-marketing-os`,
confirmed source rights, selected MIT, and excluded unresolved GEO adaptations
on September 13, 2026. The public repository becomes the canonical home for
future shared source changes. Existing private history and release assets are
not imported; existing consumers keep their signed pins and trust root.

## Release boundary

The public snapshot contains 84 procedures, selected
source tools, schemas, tests, fictional examples, and member documentation.
The standalone GEO Audit and its local page-audit tool are included. Five
related GEO adaptations and their inherited reference corpus remain omitted.
Dependencies are installed separately. No historical branches, tags,
PRs, Actions logs, private operator guides, or old release assets are imported.

The prior history and ten old release sets were scanned. No credential patterns
were found, but old assets and hosting metadata contain private operating
identifiers. They remain private and are not cleared for redistribution.

## Consumer cutover status

AI Marketing OS is the only canonical source for future shared-workflow edits.
Existing private consumers still use their signed historical pins while the
public release is evaluated. Do not point a consumer lock, router, installer, or
default repository at the public channel until the owner accepts the results of
the [consumer cutover test plan](cutover-testing.md).

The public library contains `geo-audit`. Five separate GEO adaptations remain
outside this release. They need an ownership decision—move into an appropriate
private operating repository, retire them, or separately clear them for public
publication—before any consumer that uses them can move to the public channel.

## Required checks

Before public launch, run the local gate and hosted CI on the selected source,
scan the exported snapshot, and verify its allowlist. Build the signed release
from the public source commit and test the actual downloaded artifact. Configure
main protection and the release approval environment, then read settings back.
After publication, verify anonymous clone, signed setup, and a useful starter task.
A successful code test does not establish live integration behavior or human
voice calibration. The GitHub release and its Actions run identify the exact
source commit and hosted validation result.

## Evidence boundaries

The three starter workflows have offline output or structural setup evidence.
Six strategy workflows have 24 recorded offline cases, with evaluator/context
limitations documented in the test plan. Other workflows are opt-in and their
execution remains unverified. No subscriber communication or live publishing
integration is part of this launch. New members should test the starter path
first, then voice calibration, strategy inputs, and their chosen integrations.
