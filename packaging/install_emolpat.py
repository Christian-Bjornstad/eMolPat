"""Bootstrap an approved eMolPat release from a Python FELLES prompt."""

from __future__ import annotations

import os
import site
import sys
from pathlib import Path


def activate_user_site() -> Path:
    if sys.version_info[:2] != (3, 14):
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


def release_root() -> Path:
    configured = os.environ.get("EMOLPAT_RELEASE_ROOT")
    root = Path(configured) if configured else Path(__file__).resolve().parent
    root = root.resolve()
    os.environ["EMOLPAT_RELEASE_ROOT"] = str(root)
    return root


def _activate_bootstrap_wheels(root: Path) -> None:
    portal_wheels = sorted((root / "packages").glob("emolpat-*.whl"))
    packaging_wheels = sorted((root / "wheelhouse").glob("packaging-*.whl"))
    if len(portal_wheels) != 1 or len(packaging_wheels) != 1:
        raise RuntimeError("eMolPat-pakken er ufullstendig")
    sys.path[:0] = [str(portal_wheels[0]), str(packaging_wheels[0])]


def _record_startup_failure(error: BaseException) -> None:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    logs = base / "eMolPat" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    with (logs / "bootstrap.log").open("a", encoding="utf-8") as stream:
        stream.write(f"installer_start_failed {type(error).__name__}\n")


def main() -> int:
    try:
        activate_user_site()
        root = release_root().resolve()
        _activate_bootstrap_wheels(root)
        from emolpat.install import install_release
        from emolpat.paths import UserPaths

        result = install_release(
            root,
            paths=UserPaths.from_environment(os.environ),
        )
        if not result.ok:
            print(f"eMolPat kunne ikke installeres (steg: {result.stage}).")
            return 1
        print("eMolPat er installert og kontrollert for denne brukeren.")
        return 0
    except Exception as error:  # noqa: BLE001 - final Python FELLES safety boundary
        _record_startup_failure(error)
        print("eMolPat-installasjonen kunne ikke starte. Kontakt teknisk støtte.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
