from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from emolpat.integrity import verify_release
from emolpat.manifest import load_manifest
from scripts.build_suite import _validate_dependency_matrix, assemble_release


def create_inputs(root: Path) -> tuple[list[Path], list[Path]]:
    packages = root / "input-packages"
    dependencies = root / "input-dependencies"
    packages.mkdir(parents=True)
    dependencies.mkdir()
    package_paths = []
    for name in (
        "emolpat-1.0.0-py3-none-any.whl",
        "hemafrag_diagnostics-1.2.0-py3-none-any.whl",
        "igh_merge-0.2.0-py3-none-any.whl",
        "archer_prosess-0.1.0-py3-none-any.whl",
        "mpn_tolkning-0.1.0-py3-none-any.whl",
    ):
        path = packages / name
        path.write_bytes(name.encode())
        package_paths.append(path)
    dependency = dependencies / "packaging-25.0-py3-none-any.whl"
    dependency.write_bytes(b"dependency")
    return package_paths, [dependency]


def test_assembly_contains_atomic_verified_suite(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)

    root = assemble_release("1.0.0", tmp_path / "dist", packages, dependencies)

    assert (root / "manifest.json").is_file()
    assert len(list((root / "packages").glob("*.whl"))) == 5
    assert len(list((root / "wheelhouse").glob("*.whl"))) == 1
    manifest = load_manifest(root / "manifest.json")
    assert verify_release(root, manifest).ok
    assert [module.id for module in manifest.modules] == [
        "hemafrag",
        "igh-merge",
        "vpm-tolkning",
        "mpn-tolkning",
    ]


def test_two_assemblies_have_identical_manifests(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)

    first = assemble_release("1.0.0", tmp_path / "one", packages, dependencies)
    second = assemble_release("1.0.0", tmp_path / "two", packages, dependencies)

    assert (first / "manifest.json").read_bytes() == (
        second / "manifest.json"
    ).read_bytes()
    first_manifest = json.loads((first / "manifest.json").read_text())
    assert first_manifest["files"] == sorted(
        first_manifest["files"], key=lambda item: item["path"]
    )


def test_build_rejects_dependency_version_outside_component_contract(
    tmp_path: Path,
) -> None:
    package = tmp_path / "clinical_app-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr(
            "clinical_app-1.0.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: clinical-app\nVersion: 1.0.0\n"
            "Requires-Dist: pandas<3\n",
        )
    dependency = tmp_path / "pandas-3.0.1-py3-none-any.whl"
    with zipfile.ZipFile(dependency, "w") as archive:
        archive.writestr("pandas-3.0.1.dist-info/METADATA", "Metadata-Version: 2.1\n")

    with pytest.raises(RuntimeError, match="unsatisfied dependency"):
        _validate_dependency_matrix([package], [dependency])


def test_assembly_requires_exactly_the_five_approved_distributions(
    tmp_path: Path,
) -> None:
    packages, dependencies = create_inputs(tmp_path)
    packages[-1] = packages[-1].rename(
        packages[-1].with_name("wrong_app-0.1.0-py3-none-any.whl")
    )

    with pytest.raises(RuntimeError, match="exactly the five approved"):
        assemble_release("1.0.0", tmp_path / "dist", packages, dependencies)


def test_assembly_rejects_wrong_component_version(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)
    packages[1] = packages[1].rename(
        packages[1].with_name("hemafrag_diagnostics-9.9.9-py3-none-any.whl")
    )

    with pytest.raises(RuntimeError, match="component wheel version"):
        assemble_release("1.0.0", tmp_path / "dist", packages, dependencies)
