"""Installed eMolPat suite entry point."""

from __future__ import annotations

import logging
import os
import sys
from importlib.resources import as_file, files

from emolpat.domain import SuiteManifest
from emolpat.health_probe import probe_health
from emolpat.logging_config import configure_logging
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths
from emolpat.release_source import find_release_root
from emolpat.ui.app import run_portal


def bundled_manifest() -> SuiteManifest:
    """Load the manifest shipped with this exact portal build."""
    resource = files("emolpat.ui.resources").joinpath("suite-manifest.json")
    with as_file(resource) as manifest_path:
        return load_manifest(manifest_path)


def main() -> int:
    """Show the portal while standalone analysis applications run separately."""
    paths = UserPaths.from_environment(os.environ)
    configure_logging(paths)
    manifest = bundled_manifest()
    health = probe_health(manifest, paths)
    release_root = find_release_root(paths, os.environ)
    logger = logging.getLogger("emolpat")

    # Diagnostic logging for health state
    logger.info("=" * 60)
    logger.info("eMolPat Portal Health Check")
    logger.info("=" * 60)
    logger.info("Python version: %s", sys.version)
    logger.info("Python executable: %s", sys.executable)
    logger.info("Bundled manifest version: %s", manifest.suite_version)
    logger.info("Install record version: %s", health.suite_version)
    logger.info("Health state: %s", health.state)

    if health.issues:
        logger.warning("Health issues detected:")
        for issue in health.issues:
            logger.warning("  - %s", issue)
    else:
        logger.info("No health issues detected")

    # Log module status
    logger.info("Module status:")
    for module in manifest.modules:
        logger.info("  %s: %s==%s", module.id, module.distribution, module.version)

    logger.info("=" * 60)

    return run_portal(
        manifest,
        health,
        release_root=release_root,
        paths=paths,
        health_loader=lambda: probe_health(manifest, paths),
    )


if __name__ == "__main__":
    raise SystemExit(main())
