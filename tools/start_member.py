#!/usr/bin/env python3
"""Create your first workspace from the public, signed starter release."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from consumer_sops import ConsumerSopError
from core_install import CoreInstallError, download_public_release
from scaffold_member import MemberSetupError, _destination, scaffold_member

ROOT = Path(__file__).resolve().parents[1]


def start_member(workspace: Path) -> dict:
    _destination(workspace)
    for name in ("git", "zstd", "minisign"):
        if shutil.which(name) is None:
            raise MemberSetupError(f"Install {name} before setup; see docs/member-guide.md.")
    channel = json.loads((ROOT / "releases/channel.json").read_text())
    with tempfile.TemporaryDirectory(prefix="marketing-release-") as temporary:
        directory = Path(temporary)
        download_public_release(channel["repository"], channel["version"], directory)
        return scaffold_member(workspace, directory, channel["version"],
                               ROOT / "releases/trust/minisign.pub", repository=channel["repository"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path, help="New directory outside this source checkout")
    args = parser.parse_args()
    try:
        print(json.dumps(start_member(args.workspace), indent=2))
        return 0
    except (CoreInstallError, ConsumerSopError, MemberSetupError, OSError, ValueError) as exc:
        parser.exit(1, f"member setup: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
