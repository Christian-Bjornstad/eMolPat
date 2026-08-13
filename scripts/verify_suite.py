"""Command-line cryptographic verifier for assembled eMolPat releases."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from emolpat.integrity import verify_release
from emolpat.manifest import ManifestError, load_manifest


def verify_suite(root: Path) -> int:
    try:
        manifest = load_manifest(root / "manifest.json")
        report = verify_release(root, manifest)
    except (OSError, ValueError, ManifestError) as exc:
        print(f"Ugyldig eMolPat-pakke: {type(exc).__name__}")
        return 1
    if not report.ok:
        for issue in report.issues:
            print(f"{issue.code}: {issue.path}")
        return 1
    print(f"eMolPat {manifest.suite_version}: kontrollert")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    return verify_suite(parser.parse_args().release.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
