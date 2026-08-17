"""Expose safe startup evidence from a managed Python FELLES prompt."""

from __future__ import annotations

import importlib
import importlib.util
import ntpath
import os
import re
import site
import sys
import traceback
from pathlib import Path

WINDOWS_PATH = re.compile(r"(?i)(?:[a-z]:\\|\\\\)[^\s\"']+")
PATIENT_LIKE_TOKEN = re.compile(
    r"\b(?:patient|pasient|sample|prøve|prove)[-_ ]?\d+[A-Za-z0-9_-]*\b",
    flags=re.IGNORECASE,
)


def redact(text: str) -> str:
    """Hide user-specific roots and collapse all other absolute Windows paths."""
    safe = text
    roots = (
        (os.environ.get("LOCALAPPDATA"), "%LOCALAPPDATA%"),
        (os.environ.get("APPDATA"), "%APPDATA%"),
        (os.environ.get("USERPROFILE"), "%USERPROFILE%"),
        (str(Path.home()), "%USERPROFILE%"),
        (os.environ.get("USERNAME"), "[user]"),
    )
    for value, token in sorted(roots, key=lambda item: len(item[0] or ""), reverse=True):
        if value:
            safe = re.sub(re.escape(value), token, safe, flags=re.IGNORECASE)

    def hide_unknown_path(match: re.Match[str]) -> str:
        filename = ntpath.basename(match.group(0).rstrip("\\/"))
        return rf"[path]\{filename}" if filename else "[path]"

    without_paths = WINDOWS_PATH.sub(hide_unknown_path, safe)
    return PATIENT_LIKE_TOKEN.sub("[redacted]", without_paths)


def _module_location() -> str:
    try:
        spec = importlib.util.find_spec("emolpat")
    except (ImportError, ValueError):
        spec = None
    if spec is None or spec.origin is None:
        return "ikke funnet"
    return redact(spec.origin)


def diagnostic_lines(error: BaseException | None = None) -> tuple[str, ...]:
    """Return useful runtime facts plus a complete redacted traceback."""
    lines = [
        "=== eMolPat oppstartsdiagnose ===",
        f"Python: {sys.version.split()[0]}",
        f"Executable: {Path(sys.executable).name}",
        f"User-site: {redact(site.getusersitepackages())}",
        f"eMolPat module: {_module_location()}",
    ]
    if error is not None:
        lines.extend(
            redact(part.rstrip("\n"))
            for part in traceback.format_exception(error)
        )
    return tuple(lines)


def clear_emolpat_modules() -> tuple[str, ...]:
    """Remove only cached eMolPat imports before a clean retry."""
    names = tuple(
        sorted(
            name
            for name in sys.modules
            if name == "emolpat" or name.startswith("emolpat.")
        )
    )
    for name in names:
        sys.modules.pop(name, None)
    importlib.invalidate_caches()
    return names


def activate_user_site() -> Path:
    """Expose the same per-user installation boundary as the normal starter."""
    user_site = Path(site.getusersitepackages())
    user_site.mkdir(parents=True, exist_ok=True)
    value = str(user_site)
    while value in sys.path:
        sys.path.remove(value)
    sys.path.insert(0, value)
    return user_site


def _diagnostic_log() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / "eMolPat" / "logs" / "startup-diagnostic.log"


def _write_diagnostic(lines: tuple[str, ...]) -> Path:
    path = _diagnostic_log()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    """Start eMolPat and keep Python FELLES alive if startup fails."""
    os.environ["EMOLPAT_RELEASE_ROOT"] = str(Path(__file__).resolve().parent)
    activate_user_site()
    if os.environ.pop("EMOLPAT_DIAGNOSTIC_CLEAN_IMPORT", "") == "1":
        clear_emolpat_modules()
    try:
        from emolpat.__main__ import main as portal_main

        return portal_main()
    except BaseException as error:  # noqa: BLE001 - FELLES must survive SystemExit.
        lines = diagnostic_lines(error)
        log = _write_diagnostic(lines)
        print("\n".join(lines))
        print(f"Diagnoseloggen er lagret i: {redact(str(log))}")
        print("Python FELLES holdes åpen. Kopier teksten over tilbake til Codex.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
