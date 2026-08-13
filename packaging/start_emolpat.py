"""Start the installed eMolPat portal from a Python FELLES prompt."""

from __future__ import annotations

import os
import site
import sys
from pathlib import Path


def activate_user_site() -> Path:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(
            f"Python FELLES-versjon støttes ikke: {sys.version.split()[0]}"
        )
    user_site = Path(site.getusersitepackages())
    user_site.mkdir(parents=True, exist_ok=True)
    value = str(user_site)
    while value in sys.path:
        sys.path.remove(value)
    sys.path.insert(0, value)
    return user_site


def _record_startup_failure(error: BaseException) -> None:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    logs = base / "eMolPat" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    with (logs / "bootstrap.log").open("a", encoding="utf-8") as stream:
        stream.write(f"portal_start_failed {type(error).__name__}\n")


def main() -> int:
    try:
        os.environ["EMOLPAT_RELEASE_ROOT"] = str(Path(__file__).resolve().parent)
        activate_user_site()
        from emolpat.__main__ import main

        return main()
    except Exception as error:  # noqa: BLE001 - final Python FELLES safety boundary
        _record_startup_failure(error)
        print("eMolPat kunne ikke startes. Kontakt teknisk støtte.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
