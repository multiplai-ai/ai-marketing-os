#!/usr/bin/env python3
"""Check every executable tool in fresh, credential-free subprocesses."""
from __future__ import annotations
import argparse
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile

# These wrappers invoke this smoke check (directly or through check_core).
# Excluding them prevents recursion; their orchestration is exercised by CI.
EXCLUDED = {"check_core", "check_offline_cli"}


def discover_tools(root: Path) -> tuple[str, ...]:
    """Include each Python tool with a top-level __main__ entry point."""
    names = []
    for path in sorted((root / "tools").glob("*.py")):
        if path.stem in EXCLUDED:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if any(isinstance(node, ast.If) and
               any(isinstance(value, ast.Compare) and
                   any(isinstance(term, ast.Name) and term.id == "__name__" for term in ast.walk(value)) and
                   any(isinstance(term, ast.Constant) and term.value == "__main__" for term in ast.walk(value))
                   for value in ast.walk(node.test))
               for node in tree.body):
            names.append(path.stem)
    return tuple(names)


GUARD = '''import socket
import builtins
import io
import os

def deny(*args, **kwargs):
    raise RuntimeError("Network access forbidden in offline smoke check")
socket.create_connection = deny
socket.getaddrinfo = deny
socket.socket.connect = deny
socket.socket.connect_ex = deny

# Integration startup must not discover or read private dotenv files.
def guarded_open(original):
    def checked(path, *args, **kwargs):
        if isinstance(path, (str, bytes, os.PathLike)):
            name = os.path.basename(os.fsdecode(path))
            if name == ".env" or name.startswith(".env."):
                raise RuntimeError("Implicit dotenv reads forbidden in offline smoke check")
        return original(path, *args, **kwargs)
    return checked
builtins.open = guarded_open(builtins.open)
io.open = guarded_open(io.open)
'''


def check(root: Path) -> list[str]:
    failures = []
    with tempfile.TemporaryDirectory() as directory:
        isolated = Path(directory)
        (isolated / 'sitecustomize.py').write_text(GUARD)
        env = {key: os.environ[key] for key in ('PATH', 'SYSTEMROOT') if key in os.environ}
        env.update(HOME=directory, PYTHONPATH=os.pathsep.join((directory, str(root), str(root / 'tools'))), PYTHONDONTWRITEBYTECODE='1')
        for name in discover_tools(root):
            path = root / 'tools' / f'{name}.py'
            commands = ([sys.executable, str(path), '--help'],
                        [sys.executable, '-c', 'import runpy,sys; runpy.run_path(sys.argv[1], run_name="offline_import")', str(path)])
            for mode, command in zip(('help', 'import'), commands):
                try:
                    result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True, timeout=30)
                except subprocess.TimeoutExpired:
                    failures.append(f'{name} {mode}: exceeded 30-second offline timeout')
                    continue
                if result.returncode:
                    failures.append(f'{name} {mode}: {result.stderr.strip() or result.stdout.strip()}')
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    failures = check(args.root.resolve())
    print('\n'.join(failures) if failures else f'offline CLI/import checks: {len(discover_tools(args.root.resolve()))} tools passed (Python sockets blocked)')
    return bool(failures)

if __name__ == '__main__':
    raise SystemExit(main())
