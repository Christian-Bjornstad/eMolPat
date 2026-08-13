"""Installed eMolPat suite entry point."""

from __future__ import annotations

from importlib.resources import as_file, files

from emolpat.domain import HealthReport, SuiteManifest, SuiteState
from emolpat.launch import run_handoff
from emolpat.manifest import load_manifest
from emolpat.ui.app import run_portal


def bundled_manifest() -> SuiteManifest:
    """Load the manifest shipped with this exact portal build."""
    resource = files("emolpat.ui.resources").joinpath("suite-manifest.json")
    with as_file(resource) as manifest_path:
        return load_manifest(manifest_path)


def main() -> int:
    """Show the portal and hand control to the selected standalone app."""
    manifest = bundled_manifest()
    health = HealthReport(
        state=SuiteState.READY,
        suite_version=manifest.suite_version,
        issues=(),
    )
    outcome = run_portal(manifest, health)
    if outcome.selected_module_id is None:
        return 0

    result = run_handoff(manifest.module(outcome.selected_module_id))
    if not result.started:
        return 1
    return result.exit_code or 0


if __name__ == "__main__":
    raise SystemExit(main())
