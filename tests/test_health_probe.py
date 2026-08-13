from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from pathlib import Path

from emolpat.domain import InstalledModule, InstallRecord, SuiteState
from emolpat.health_probe import probe_health
from emolpat.install import replace_install_record
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths


def paths_at(root: Path) -> UserPaths:
    return UserPaths(
        root=root,
        logs=root / "logs",
        install_record=root / "install-record.json",
        rollback=root / "rollback",
    )


def manifest():
    return load_manifest(Path("tests/fixtures/valid-manifest.json"))


def write_exact_record(paths: UserPaths) -> None:
    expected = manifest()
    replace_install_record(
        paths.install_record,
        InstallRecord(
            suite_version=expected.suite_version,
            manifest_sha256="a" * 64,
            verified_at="2026-08-13T12:00:00+00:00",
            modules=tuple(
                InstalledModule(
                    module.distribution,
                    module.version,
                    module.import_name,
                )
                for module in expected.modules
            ),
        ),
    )


def test_probe_is_not_installed_without_verified_record(tmp_path: Path) -> None:
    report = probe_health(
        manifest(),
        paths_at(tmp_path),
        version_reader=lambda _name: (_ for _ in ()).throw(
            AssertionError("versions must not be read")
        ),
        import_checker=lambda _name: (_ for _ in ()).throw(
            AssertionError("imports must not be checked")
        ),
    )

    assert report.state is SuiteState.NOT_INSTALLED
    assert report.issues == ("suite is not installed for this Windows user",)


def test_probe_requires_repair_when_registered_import_is_missing(
    tmp_path: Path,
) -> None:
    paths = paths_at(tmp_path)
    expected = manifest()
    write_exact_record(paths)
    versions = {module.distribution: module.version for module in expected.modules}

    report = probe_health(
        expected,
        paths,
        version_reader=versions.__getitem__,
        import_checker=lambda name: name != "igh_merge",
    )

    assert report.state is SuiteState.REPAIR_REQUIRED
    assert report.issues == ("missing import: igh_merge",)


def test_probe_treats_missing_distribution_as_repair_required(tmp_path: Path) -> None:
    paths = paths_at(tmp_path)
    write_exact_record(paths)

    report = probe_health(
        manifest(),
        paths,
        version_reader=lambda _name: (_ for _ in ()).throw(
            PackageNotFoundError("missing")
        ),
        import_checker=lambda _name: True,
    )

    assert report.state is SuiteState.REPAIR_REQUIRED
    assert all("found missing" in issue for issue in report.issues)


def test_probe_treats_invalid_record_as_repair_required(tmp_path: Path) -> None:
    paths = paths_at(tmp_path)
    paths.install_record.write_text("not-json", encoding="utf-8")

    report = probe_health(manifest(), paths)

    assert report.state is SuiteState.REPAIR_REQUIRED
    assert report.issues == ("install record is invalid",)
