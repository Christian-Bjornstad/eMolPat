from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from emolpat.domain import FileDigest, SuiteManifest
from emolpat.integrity import IntegrityError, sha256_file, verify_release


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_for(*files: FileDigest) -> SuiteManifest:
    return SuiteManifest(
        schema_version=1,
        suite_version="1.0.0",
        python_requires=">=3.12,<3.15",
        modules=(),
        files=files,
    )


def create_release_root(tmp_path: Path) -> None:
    (tmp_path / "packages").mkdir()
    (tmp_path / "wheelhouse").mkdir()
    (tmp_path / "requirements.lock").write_text("locked", encoding="utf-8")


def test_sha256_file_hashes_large_files_in_binary_mode(tmp_path: Path) -> None:
    content = b"eMolPat\r\n" * 200_000
    path = tmp_path / "artifact.whl"
    path.write_bytes(content)

    assert sha256_file(path) == digest(content)


def test_verify_release_accepts_complete_matching_release(tmp_path: Path) -> None:
    create_release_root(tmp_path)
    artifact = tmp_path / "packages" / "portal.whl"
    artifact.write_bytes(b"portal")
    manifest = manifest_for(
        FileDigest("requirements.lock", digest(b"locked")),
        FileDigest("packages/portal.whl", digest(b"portal")),
    )

    report = verify_release(tmp_path, manifest)

    assert report.ok
    assert report.issues == ()


def test_verify_release_reports_changed_and_missing_files_in_path_order(
    tmp_path: Path,
) -> None:
    create_release_root(tmp_path)
    changed = tmp_path / "packages" / "changed.whl"
    changed.write_bytes(b"changed")
    manifest = manifest_for(
        FileDigest("packages/missing.whl", digest(b"missing")),
        FileDigest("packages/changed.whl", digest(b"original")),
    )

    report = verify_release(tmp_path, manifest)

    assert not report.ok
    assert [(issue.path, issue.code) for issue in report.issues] == [
        ("packages/changed.whl", "checksum_mismatch"),
        ("packages/missing.whl", "missing_file"),
    ]


@pytest.mark.parametrize("relative_path", ["../outside.whl", "/absolute.whl"])
def test_verify_release_rejects_paths_outside_release_root(
    tmp_path: Path, relative_path: str
) -> None:
    create_release_root(tmp_path)

    with pytest.raises(IntegrityError, match="outside release root"):
        verify_release(
            tmp_path,
            manifest_for(FileDigest(relative_path, "0" * 64)),
        )


@pytest.mark.parametrize("directory", ["packages", "wheelhouse"])
def test_verify_release_requires_suite_directories(
    tmp_path: Path, directory: str
) -> None:
    create_release_root(tmp_path)
    (tmp_path / directory).rmdir()

    report = verify_release(tmp_path, manifest_for())

    assert not report.ok
    assert (directory, "missing_directory") in {
        (issue.path, issue.code) for issue in report.issues
    }
