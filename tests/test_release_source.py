from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from emolpat.domain import InstalledModule, InstallRecord
from emolpat.install import replace_install_record
from emolpat.paths import UserPaths
from emolpat.release_source import find_release_root


@pytest.fixture
def paths(tmp_path: Path) -> UserPaths:
    root = tmp_path / "user"
    return UserPaths(
        root=root,
        logs=root / "logs",
        install_record=root / "install-record.json",
        rollback=root / "rollback",
    )


def create_verified_release(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / "packages").mkdir()
    (root / "wheelhouse").mkdir()
    lock = b"packaging==25.0 --hash=sha256:" + b"a" * 64
    (root / "requirements.lock").write_bytes(lock)
    document = json.loads(
        Path("tests/fixtures/valid-manifest.json").read_text(encoding="utf-8")
    )
    document["files"] = [
        {
            "path": "requirements.lock",
            "sha256": hashlib.sha256(lock).hexdigest(),
        }
    ]
    (root / "manifest.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def install_record(version: str = "1.0.0") -> InstallRecord:
    return InstallRecord(
        suite_version=version,
        manifest_sha256="b" * 64,
        verified_at="2026-08-13T12:00:00+00:00",
        modules=(InstalledModule("example", "1.0.0", "example"),),
    )


def test_explicit_extracted_release_wins(tmp_path: Path, paths: UserPaths) -> None:
    extracted = create_verified_release(tmp_path / "extracted")
    create_verified_release(paths.rollback / "1.0.0")
    replace_install_record(paths.install_record, install_record())

    result = find_release_root(
        paths,
        {"EMOLPAT_RELEASE_ROOT": str(extracted)},
        script_root=None,
    )

    assert result == extracted.resolve()


def test_script_release_is_used_without_an_install_record(
    tmp_path: Path,
    paths: UserPaths,
) -> None:
    extracted = create_verified_release(tmp_path / "extracted")

    assert find_release_root(paths, {}, extracted) == extracted.resolve()


def test_retained_verified_release_is_repair_fallback(
    paths: UserPaths,
) -> None:
    replace_install_record(paths.install_record, install_record())
    retained = create_verified_release(paths.rollback / "1.0.0")

    assert find_release_root(paths, {}, None) == retained.resolve()


def test_invalid_explicit_release_falls_back_to_retained(
    tmp_path: Path,
    paths: UserPaths,
) -> None:
    invalid = tmp_path / "invalid"
    invalid.mkdir()
    replace_install_record(paths.install_record, install_record())
    retained = create_verified_release(paths.rollback / "1.0.0")

    result = find_release_root(
        paths,
        {"EMOLPAT_RELEASE_ROOT": str(invalid)},
        script_root=None,
    )

    assert result == retained.resolve()


def test_no_verified_candidate_returns_none(tmp_path: Path, paths: UserPaths) -> None:
    assert find_release_root(paths, {}, tmp_path / "missing") is None
