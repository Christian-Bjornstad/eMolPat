from __future__ import annotations

from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from emolpat.integrity import sha256_file
from scripts.archive_release import create_release_archive
from scripts.build_suite import assemble_release
from tests.test_build_suite import create_inputs


def build_release(tmp_path: Path, name: str) -> Path:
    packages, dependencies = create_inputs(tmp_path / name)
    return assemble_release("1.0.7", tmp_path / f"dist-{name}", packages, dependencies)


def test_archive_has_one_safe_top_level_directory_and_checksum(
    tmp_path: Path,
) -> None:
    release = build_release(tmp_path, "first")

    archive, checksum = create_release_archive(release, tmp_path / "out")

    assert archive.name == "eMolPat-1.0.7-windows.zip"
    assert checksum.name == "eMolPat-1.0.7-windows.zip.sha256"
    with ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert names
        assert all(name.startswith("eMolPat-1.0.7/") for name in names)
        assert "eMolPat-1.0.7/manifest.json" in names
        assert not any(".." in PurePosixPath(name).parts for name in names)
    assert checksum.read_text(encoding="ascii").split()[0] == sha256_file(archive)


def test_two_archives_are_byte_identical(tmp_path: Path) -> None:
    first = build_release(tmp_path, "first")
    second = build_release(tmp_path, "second")

    first_archive, first_checksum = create_release_archive(first, tmp_path / "one")
    second_archive, second_checksum = create_release_archive(second, tmp_path / "two")

    assert first_archive.read_bytes() == second_archive.read_bytes()
    assert first_checksum.read_bytes() == second_checksum.read_bytes()
