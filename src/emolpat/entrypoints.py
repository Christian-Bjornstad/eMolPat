"""GUI adapters for applications whose public entry point is a command-line tool."""

from __future__ import annotations

import os
from pathlib import Path


def launch_molstat() -> int:
    """Use MolStat's GUI command and its standalone per-user settings location."""
    from molstat.cli import main

    local = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    settings = local / "MolStat" / "settings.json"
    return int(main(["gui", "--settings", str(settings)]) or 0)
