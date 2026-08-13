from __future__ import annotations

import json
from pathlib import Path

from emolpat.integrity import verify_release
from emolpat.manifest import load_manifest
from scripts.build_suite import assemble_release


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
