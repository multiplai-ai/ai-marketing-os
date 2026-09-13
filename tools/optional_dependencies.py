"""Load integration packages only when a caller uses that integration."""
from __future__ import annotations

from importlib import import_module
import sys
from typing import Callable


class MissingOptionalDependency(ImportError):
    """An integration cannot start with the current Python environment."""


def require_dependency(module: str, extra: str):
    """Import a dependency and report its maintained installation group."""
    try:
        return import_module(module)
    except ImportError as exc:
        raise MissingOptionalDependency(
            f"Cannot load {module}: {exc}. From the Core checkout, run "
            f"python -m pip install '.[{extra}]' using this Python environment."
        ) from exc


def run_cli(main: Callable[[], int | None]) -> int | None:
    """Give setup failures a concise CLI error without swallowing runtime errors."""
    try:
        return main()
    except MissingOptionalDependency as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 2


def launch_chromium(browser_type, **kwargs):
    """Keep Playwright's missing-browser remedy visible without a traceback."""
    try:
        return browser_type.launch(**kwargs)
    except Exception as exc:
        if "Executable doesn't exist" not in str(exc):
            raise
        raise MissingOptionalDependency(
            "Playwright Chromium is not installed. Run "
            "python -m playwright install chromium using this Python environment."
        ) from exc
