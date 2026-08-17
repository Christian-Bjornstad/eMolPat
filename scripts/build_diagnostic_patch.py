"""Build the branch-only Python FELLES diagnostic replacement archive."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_NAME = "eMolPat-1.0.2-startup-diagnostics.zip"
TOP_LEVEL = "eMolPat-1.0.2-startup-diagnostics"
PAYLOAD = (
    "Installer eMolPat - Manuell FELLES.cmd",
    "Start eMolPat - Clean import.cmd",
    "Start eMolPat - Diagnose.cmd",
    "Start eMolPat - Manuell FELLES.cmd",
    "diagnose_emolpat_start.py",
)


def build_diagnostic_patch(output: Path) -> Path:
    """Create a deterministic archive containing only diagnostic launch files."""
    output.mkdir(parents=True, exist_ok=True)
    destination = output / ARCHIVE_NAME
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for filename in PAYLOAD:
            info = zipfile.ZipInfo(f"{TOP_LEVEL}/{filename}")
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, (PROJECT_ROOT / "packaging" / filename).read_bytes())
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "dist")
    arguments = parser.parse_args()
    print(build_diagnostic_patch(arguments.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
