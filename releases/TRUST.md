# Public release trust

The public channel is `multiplai-ai/ai-marketing-os`; the recommended preview
version is pinned in `releases/channel.json`. Obtain the source checkout from
that repository. Its `releases/trust/minisign.pub` is the public channel's trust
anchor. Do not replace it with a key supplied beside an untrusted archive.

Both the bundle and manifest are signed. Setup verifies signatures, the full
source commit, exact version, and SHA-256 digest before use. A consumer pins these
values plus the release repository in `.multiplai/core.lock.yaml`; its pinned key
lives in `.multiplai/trust/minisign.pub`. Cached installations are reverified.

The public channel has a separate signing key from historical private releases.
Existing private consumers are not silently migrated. The new private key is
stored outside the repository in an owner-only local file and in the public
repository's protected `release` environment as `MINISIGN_SECRET_KEY`.
It is never included in source or artifacts. The owner must maintain a secure
recovery backup; this release does not claim an encrypted recovery copy exists.

The release workflow requires validation and environment approval before signing.
It publishes each version once; tags and assets must not be replaced. The release
tag, manifest, and release target must identify the same reviewed main commit.
Key rotation requires reviewed consumer trust changes. If compromise is suspected,
suspend signing and revoke the key through an explicit consumer update.

Source and setup use the legacy artifact prefix `multiplai-core` for compatibility.
Public downloads require no GitHub login. Legacy locks without a repository keep
the private channel and authenticated download behavior.
