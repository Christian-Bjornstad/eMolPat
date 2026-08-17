"""Installed eMolPat suite entry point."""

from __future__ import annotations

import logging
import os
import sys
from importlib.resources import as_file, files

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.health_probe import probe_health
from emolpat.logging_config import configure_logging
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths
from emolpat.release_source import find_release_root
from emolpat.ui.app import PortalOutcome, run_application_loop, run_portal


def bundled_manifest() -> SuiteManifest:
    """Load the manifest shipped with this exact portal build."""
    resource = files("emolpat.ui.resources").joinpath("suite-manifest.json")
    with as_file(resource) as manifest_path:
        return load_manifest(manifest_path)


class InstalledPortal:
    """Portal session factory bound to one immutable installed manifest."""

    def __init__(
        self,
        manifest: SuiteManifest,
        health: HealthReport,
        paths: UserPaths | None = None,
        release_root=None,
    ) -> None:
        self.manifest = manifest
        self.health = health
        self.paths = paths
        self.release_root = release_root

    def load_health(self) -> HealthReport:
        if self.paths is not None:
            self.health = probe_health(self.manifest, self.paths)
        return self.health

    def __call__(self, startup_error: str | None = None) -> PortalOutcome:
        return run_portal(
            self.manifest,
            self.load_health(),
            startup_error,
            release_root=self.release_root,
            paths=self.paths,
            health_loader=self.load_health,
        )


def main() -> int:
    """Show the portal and hand control to the selected standalone app."""
    paths = UserPaths.from_environment(os.environ)
    configure_logging(paths)
    manifest = bundled_manifest()
    health = probe_health(manifest, paths)
    release_root = find_release_root(paths, os.environ)
    
    # Diagnostic logging for health state
    logging.info("=" * 60)
    logging.info("eMolPat Portal Health Check")
    logging.info("=" * 60)
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Python executable: {sys.executable}")
    logging.info(f"Bundled manifest version: {manifest.suite_version}")
    logging.info(f"Install record version: {health.suite_version}")
    logging.info(f"Health state: {health.state}")
    
    if health.issues:
        logging.warning(f"Health issues detected:")
        for issue in health.issues:
            logging.warning(f"  - {issue}")
    else:
        logging.info("No health issues detected")
    
    # Log module status
    logging.info("Module status:")
    for module in manifest.modules:
        logging.info(f"  {module.id}: {module.distribution}=={module.version}")
    
    logging.info("=" * 60)
    
    return run_application_loop(InstalledPortal(manifest, health, paths, release_root))


if __name__ == "__main__":
    raise SystemExit(main())
