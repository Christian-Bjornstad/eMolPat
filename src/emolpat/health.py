"""Installed-suite record parsing and pure health-state derivation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from packaging.version import InvalidVersion, Version

from emolpat.domain import (
    HealthReport,
    InstalledModule,
    InstallRecord,
    SuiteManifest,
    SuiteState,
)


class InstallRecordError(ValueError):
    """Raised when a present install record cannot be trusted."""


def _required_string(data: Mapping[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise InstallRecordError(f"invalid install record field: {field}")
    return value


def read_install_record(path: Path) -> InstallRecord | None:
    """Read the last verified suite record, or return none when absent."""
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise TypeError("record must be an object")
        raw_modules = document.get("modules")
        if not isinstance(raw_modules, list):
            raise TypeError("modules must be an array")
        modules = tuple(
            InstalledModule(
                distribution=_required_string(module, "distribution"),
                version=_required_string(module, "version"),
                import_name=_required_string(module, "import_name"),
            )
            for module in raw_modules
            if isinstance(module, dict)
        )
        if len(modules) != len(raw_modules) or not modules:
            raise TypeError("modules contain an invalid item")
        return InstallRecord(
            suite_version=_required_string(document, "suite_version"),
            manifest_sha256=_required_string(document, "manifest_sha256"),
            verified_at=_required_string(document, "verified_at"),
            modules=modules,
        )
    except (OSError, json.JSONDecodeError, TypeError, InstallRecordError) as exc:
        raise InstallRecordError(f"invalid install record: {path}") from exc


def _is_newer(candidate: str, installed: str) -> bool:
    try:
        return Version(candidate) > Version(installed)
    except InvalidVersion:
        return candidate != installed


def evaluate_health(
    approved_manifest: SuiteManifest | None,
    record: InstallRecord | None,
    distributions: Mapping[str, str],
    imports: Mapping[str, bool],
) -> HealthReport:
    """Derive suite health from non-clinical package and import observations."""
    if record is None:
        return HealthReport(
            state=SuiteState.NOT_INSTALLED,
            suite_version=None,
            issues=("suite is not installed for this Windows user",),
        )

    issues: list[str] = []
    for module in record.modules:
        actual_version = distributions.get(module.distribution)
        if actual_version != module.version:
            found = actual_version if actual_version is not None else "missing"
            issues.append(
                "distribution version mismatch: "
                f"{module.distribution} expected {module.version}, found {found}"
            )
        if not imports.get(module.import_name, False):
            issues.append(f"missing import: {module.import_name}")

    if approved_manifest is not None and (
        approved_manifest.suite_version == record.suite_version
    ):
        approved_versions = {
            module.distribution: module.version for module in approved_manifest.modules
        }
        recorded_versions = {
            module.distribution: module.version for module in record.modules
        }
        if approved_versions != recorded_versions:
            issues.append("installed module set does not match approved suite manifest")

    if issues:
        return HealthReport(
            state=SuiteState.REPAIR_REQUIRED,
            suite_version=record.suite_version,
            issues=tuple(sorted(issues)),
        )

    if approved_manifest is not None and _is_newer(
        approved_manifest.suite_version, record.suite_version
    ):
        return HealthReport(
            state=SuiteState.UPDATE_AVAILABLE,
            suite_version=record.suite_version,
            issues=(),
        )

    return HealthReport(
        state=SuiteState.READY,
        suite_version=record.suite_version,
        issues=(),
    )
