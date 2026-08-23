#!/usr/bin/env python3
"""Build-time validation for manifest version consistency.

This script ensures that the bundled manifest and release manifest are consistent
before building a release, preventing the version mismatch issue that caused
the Citrix "Ikke klar" problem.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from emolpat.manifest import load_manifest


def validate_manifest_consistency(release_version: str) -> bool:
    """Return whether the canonical manifest matches the release version."""
    errors = []

    # Load bundled manifest
    bundled_manifest_path = (
        PROJECT_ROOT
        / "src"
        / "emolpat"
        / "ui"
        / "resources"
        / "suite-manifest.json"
    )
    if not bundled_manifest_path.exists():
        errors.append(f"Bundled manifest not found: {bundled_manifest_path}")
        return False

    try:
        bundled_manifest = load_manifest(bundled_manifest_path)
    except (OSError, ValueError) as exc:
        errors.append(f"Error loading bundled manifest: {exc}")
        return False

    # Check bundled manifest version
    if bundled_manifest.suite_version != release_version:
        errors.append(
            f"Version mismatch: bundled manifest has '{bundled_manifest.suite_version}', "
            f"but expected '{release_version}'"
        )

    # Check for placeholder SHA256
    for file_digest in bundled_manifest.files:
        if file_digest.sha256 == "a" * 64:
            errors.append(
                f"Placeholder SHA256 detected for '{file_digest.path}': "
                f"{file_digest.sha256}"
            )

    # Check module versions are not test/placeholder values
    for module in bundled_manifest.modules:
        if "test" in module.version.lower():
            errors.append(
                f"Module '{module.id}' has test version: {module.version}"
            )

    if errors:
        print("=" * 60)
        print("MANIFEST VALIDATION FAILED")
        print("=" * 60)
        for error in errors:
            print(f"  FEIL: {error}")
        print("\nFix these issues before building the release.")
        print("=" * 60)
        return False
    
    print("Manifest validation passed")
    print(f"   Version: {bundled_manifest.suite_version}")
    print(f"   Modules: {[m.id for m in bundled_manifest.modules]}")
    return True


def main(argv: list[str] | None = None) -> int:
    """Validate one explicitly requested suite release version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    arguments = parser.parse_args(argv)
    print(f"Validating manifests for version: {arguments.version}")
    return 0 if validate_manifest_consistency(arguments.version) else 1


if __name__ == "__main__":
    raise SystemExit(main())
