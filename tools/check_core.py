#!/usr/bin/env python3
"""Run the same offline contribution gate locally and in CI."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    commands = (
        ['tools/check_release_content.py', '.'],
        ['tools/validate_sop_canon.py'],
        ['tools/generate_adapters.py', '.', '--check'],
        ['tools/generate_catalog.py', '--check'],
        ['tools/check_client_scrub.py', '.'],
        ['tools/check_offline_cli.py'],
        ['tools/check_evaluation_evidence.py'],
        ['-m', 'pytest', '-q'],
    )
    for command in commands:
        result = subprocess.run([sys.executable, *command], cwd=root)
        if result.returncode:
            return result.returncode
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
