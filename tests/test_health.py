from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from emolpat.domain import InstalledModule, InstallRecord, SuiteState
from emolpat.health import InstallRecordError, evaluate_health, read_install_record
from emolpat.manifest import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "valid-manifest.json"


def manifest(version: str = "1.0.0"):
    return replace(load_manifest(FIXTURE), suite_version=version)


def installed_record(version: str = "1.0.0") -> InstallRecord:
    modules = tuple(
        InstalledModule(
            distribution=module.distribution,
            version=module.version,
            import_name=module.import_name,
        )
        for module in manifest().modules
    )
    return InstallRecord(
        suite_version=version,
        manifest_sha256="a" * 64,
        verified_at="2026-08-13T12:00:00+00:00",
        modules=modules,
    )


def installed_distributions(record: InstallRecord) -> dict[str, str]:
    return {module.distribution: module.version for module in record.modules}


def available_imports(record: InstallRecord) -> dict[str, bool]:
    return {module.import_name: True for module in record.modules}


def test_health_is_ready_when_installed_suite_is_exact() -> None:
    record = installed_record()

    report = evaluate_health(
        manifest(), record, installed_distributions(record), available_imports(record)
    )

    assert report.state is SuiteState.READY
    assert report.suite_version == "1.0.0"
    assert report.issues == ()


def test_health_reports_atomic_update_for_newer_approved_suite() -> None:
    record = installed_record()

    report = evaluate_health(
        manifest("1.1.0"),
        record,
        installed_distributions(record),
        available_imports(record),
    )

    assert report.state is SuiteState.UPDATE_AVAILABLE


def test_health_requires_repair_when_one_import_is_missing() -> None:
    record = installed_record()
    imports = available_imports(record)
    imports["igh_merge"] = False

    report = evaluate_health(
        manifest(), record, installed_distributions(record), imports
    )

    assert report.state is SuiteState.REPAIR_REQUIRED
    assert report.issues == ("missing import: igh_merge",)


def test_health_requires_repair_when_distribution_version_differs() -> None:
    record = installed_record()
    distributions = installed_distributions(record)
    distributions["mpn-tolkning"] = "9.9.9"

    report = evaluate_health(
        manifest(), record, distributions, available_imports(record)
    )

    assert report.state is SuiteState.REPAIR_REQUIRED
    assert report.issues == (
        "distribution version mismatch: mpn-tolkning expected 0.1.0, found 9.9.9",
    )


def test_valid_installed_suite_remains_ready_when_shared_release_is_unavailable() -> None:
    record = installed_record()

    report = evaluate_health(
        None, record, installed_distributions(record), available_imports(record)
    )

    assert report.state is SuiteState.READY


def test_health_is_not_installed_without_an_install_record() -> None:
    report = evaluate_health(manifest(), None, {}, {})

    assert report.state is SuiteState.NOT_INSTALLED
    assert report.issues == ("suite is not installed for this Windows user",)


def test_read_install_record_returns_none_when_file_is_missing(tmp_path: Path) -> None:
    assert read_install_record(tmp_path / "missing.json") is None


def test_read_install_record_parses_verified_components(tmp_path: Path) -> None:
    expected = installed_record()
    path = tmp_path / "install-record.json"
    path.write_text(
        json.dumps(
            {
                "suite_version": expected.suite_version,
                "manifest_sha256": expected.manifest_sha256,
                "verified_at": expected.verified_at,
                "modules": [
                    {
                        "distribution": module.distribution,
                        "version": module.version,
                        "import_name": module.import_name,
                    }
                    for module in expected.modules
                ],
            }
        ),
        encoding="utf-8",
    )

    assert read_install_record(path) == expected


def test_read_install_record_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "install-record.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(InstallRecordError, match="invalid install record"):
        read_install_record(path)
