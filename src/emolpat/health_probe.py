"""Observe installed packages and derive trustworthy portal health."""

from __future__ import annotations

import importlib.metadata
import importlib.util
from collections.abc import Callable

from emolpat.domain import HealthReport, SuiteManifest, SuiteState
from emolpat.health import InstallRecordError, evaluate_health, read_install_record
from emolpat.paths import UserPaths

VersionReader = Callable[[str], str]
ImportChecker = Callable[[str], bool]


def module_available(name: str) -> bool:
    """Return whether Python can resolve an installed top-level package."""
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def probe_health(
    manifest: SuiteManifest,
    paths: UserPaths,
    version_reader: VersionReader = importlib.metadata.version,
    import_checker: ImportChecker = module_available,
) -> HealthReport:
    """Observe only recorded components and feed the pure health evaluator."""
    try:
        record = read_install_record(paths.install_record)
    except InstallRecordError:
        return HealthReport(
            state=SuiteState.REPAIR_REQUIRED,
            suite_version=None,
            issues=("install record is invalid",),
        )

    if record is None:
        return evaluate_health(manifest, None, {}, {})

    distributions: dict[str, str] = {}
    imports: dict[str, bool] = {}
    for module in record.modules:
        try:
            distributions[module.distribution] = version_reader(module.distribution)
        except (importlib.metadata.PackageNotFoundError, ImportError, ValueError):
            pass
        imports[module.import_name] = import_checker(module.import_name)

    return evaluate_health(manifest, record, distributions, imports)
