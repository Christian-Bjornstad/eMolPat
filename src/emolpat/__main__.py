"""Installed eMolPat suite entry point."""

from __future__ import annotations

import os
from importlib.resources import as_file, files

from emolpat.domain import HealthReport, SuiteManifest, SuiteState
from emolpat.logging_config import configure_logging
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths
from emolpat.ui.app import PortalOutcome, run_application_loop, run_portal


def bundled_manifest() -> SuiteManifest:
    """Load the manifest shipped with this exact portal build."""
    resource = files("emolpat.ui.resources").joinpath("suite-manifest.json")
    with as_file(resource) as manifest_path:
        return load_manifest(manifest_path)


class InstalledPortal:
    """Portal session factory bound to one immutable installed manifest."""

    def __init__(self, manifest: SuiteManifest, health: HealthReport) -> None:
        self.manifest = manifest
        self.health = health

    def __call__(self, startup_error: str | None = None) -> PortalOutcome:
        return run_portal(self.manifest, self.health, startup_error)


def main() -> int:
    """Show the portal and hand control to the selected standalone app."""
    configure_logging(UserPaths.from_environment(os.environ))
    manifest = bundled_manifest()
    health = HealthReport(
        state=SuiteState.READY,
        suite_version=manifest.suite_version,
        issues=(),
    )
    return run_application_loop(InstalledPortal(manifest, health))


if __name__ == "__main__":
    raise SystemExit(main())
