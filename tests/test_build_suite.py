from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path

import pytest

import scripts.build_suite as builder
from emolpat.integrity import verify_release
from emolpat.manifest import load_manifest
from scripts.build_suite import (
    PYTHON_314,
    _download_dependencies,
    _validate_dependency_matrix,
    assemble_release,
)


def create_inputs(root: Path) -> tuple[list[Path], list[Path]]:
    packages = root / "input-packages"
    dependencies = root / "input-dependencies"
    packages.mkdir(parents=True)
    dependencies.mkdir()
    package_paths = []
    for name in (
        "emolpat-1.0.0-py3-none-any.whl",
        "hemafrag_diagnostics-1.2.1-py3-none-any.whl",
        "igh_merge-0.2.0-py3-none-any.whl",
        "archer_prosess-0.1.0-py3-none-any.whl",
        "mpn_tolkning-0.1.0-py3-none-any.whl",
        "molstat-0.1.0-py3-none-any.whl",
        "molkey-0.2.0-py3-none-any.whl",
        "abl1_dragon-0.6.2-py3-none-any.whl",
        "solide-0.8.11-py3-none-any.whl",
        "qiaxcel_fortynning-0.2.0-py3-none-any.whl",
    ):
        path = packages / name
        path.write_bytes(name.encode())
        package_paths.append(path)
    dependency = dependencies / "packaging-25.0-py3-none-any.whl"
    dependency.write_bytes(b"dependency")
    return package_paths, [dependency]


def test_assembly_contains_atomic_verified_suite(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)

    root = assemble_release("1.4.0", tmp_path / "dist", packages, dependencies)

    assert (root / "manifest.json").is_file()
    assert len(list((root / "packages").glob("*.whl"))) == 10
    assert len(list((root / "wheelhouse").glob("*.whl"))) == 1
    manifest = load_manifest(root / "manifest.json")
    assert verify_release(root, manifest).ok
    assert manifest.python_requires == ">=3.14,<3.15"
    assert [module.id for module in manifest.modules] == [
        "hemafrag",
        "igh-merge",
        "vpm-tolkning",
        "mpn-tolkning",
        "molstat",
        "molkey",
        "dragen",
        "solide",
        "qiaxcel",
    ]


def test_assembly_contains_only_verified_python_bootstraps(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)

    root = assemble_release("1.4.0", tmp_path / "dist", packages, dependencies)

    expected = {"install_emolpat.py", "start_emolpat.py"}
    assert not list(root.glob("*.cmd"))
    assert not (root / "diagnose_emolpat_start.py").exists()
    manifest = load_manifest(root / "manifest.json")
    assert expected <= {item.path for item in manifest.files}


def test_two_assemblies_have_identical_manifests(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)

    first = assemble_release("1.4.0", tmp_path / "one", packages, dependencies)
    second = assemble_release("1.4.0", tmp_path / "two", packages, dependencies)

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


def test_assembly_requires_exactly_the_ten_approved_distributions(
    tmp_path: Path,
) -> None:
    packages, dependencies = create_inputs(tmp_path)
    packages[-1] = packages[-1].rename(
        packages[-1].with_name("wrong_app-0.1.0-py3-none-any.whl")
    )

    with pytest.raises(RuntimeError, match="exactly the ten approved"):
        assemble_release("1.4.0", tmp_path / "dist", packages, dependencies)


def test_assembly_rejects_wrong_component_version(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)
    packages[1] = packages[1].rename(
        packages[1].with_name("hemafrag_diagnostics-9.9.9-py3-none-any.whl")
    )

    with pytest.raises(RuntimeError, match="component wheel version"):
        assemble_release("1.4.0", tmp_path / "dist", packages, dependencies)


def test_dependency_download_targets_cpython_314_windows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, ...]] = []

    def record(command: tuple[str, ...], *, check: bool) -> subprocess.CompletedProcess:
        assert check
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", record)

    _download_dependencies(tmp_path, PYTHON_314)

    command = calls[0]
    assert command[command.index("--python-version") + 1] == "314"
    assert command[command.index("--abi") + 1] == "cp314"
    assert command[command.index("--platform") + 1] == "win_amd64"
    assert "--no-deps" in command
    requirement_file = Path(command[command.index("-r") + 1])
    assert requirement_file.name == "requirements-py314.in"


def test_python_314_dependency_input_is_fully_pinned() -> None:
    lines = [
        line.strip()
        for line in PYTHON_314.requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    assert len(lines) == len(set(lines))
    assert all("==" in line and " --hash=" not in line for line in lines)
    assert "platformdirs==4.11.3" in lines
    assert "portalocker==3.2.0" in lines
    assert "pywin32==312" in lines
    assert "python-docx==1.2.0" in lines
    assert "lxml==6.1.3" in lines


def test_build_copies_native_wheel_from_approved_component_checkout(
    tmp_path: Path,
) -> None:
    component_root = tmp_path / "components"
    source = component_root / "HemaFrag-Diagnostics"
    vendor = source / "wheels" / "fraggler_kernels-0.1.3-cp310-abi3-win_amd64.whl"
    vendor.parent.mkdir(parents=True)
    vendor.write_bytes(b"approved native dependency")
    for arguments in (
        ("init",),
        ("add", "wheels"),
        (
            "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-m", "Record approved vendored wheel",
        ),
    ):
        subprocess.run(("git", *arguments), cwd=source, check=True, capture_output=True)
    destination = tmp_path / "dependencies"
    destination.mkdir()

    builder._copy_vendored_wheels(component_root, destination)

    assert (destination / vendor.name).read_bytes() == vendor.read_bytes()


def test_build_rejects_missing_native_wheel(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="missing approved vendored wheel"):
        builder._copy_vendored_wheels(tmp_path, tmp_path / "dependencies")


def test_build_rejects_untracked_native_wheel(tmp_path: Path) -> None:
    source = tmp_path / "components" / "HemaFrag-Diagnostics"
    vendor = source / "wheels" / "fraggler_kernels-0.1.3-cp310-abi3-win_amd64.whl"
    vendor.parent.mkdir(parents=True)
    vendor.write_bytes(b"unapproved native dependency")
    subprocess.run(("git", "init"), cwd=source, check=True, capture_output=True)
    destination = tmp_path / "dependencies"
    destination.mkdir()

    with pytest.raises(RuntimeError, match="vendored wheel is not tracked"):
        builder._copy_vendored_wheels(tmp_path / "components", destination)


def test_build_suite_passes_target_to_download_and_assembly(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    names = iter(
        (
            "emolpat-0.1.0-py3-none-any.whl",
            "hemafrag_diagnostics-1.2.1-py3-none-any.whl",
            "igh_merge-0.2.0-py3-none-any.whl",
            "archer_prosess-0.1.0-py3-none-any.whl",
            "mpn_tolkning-0.1.0-py3-none-any.whl",
            "molstat-0.1.0-py3-none-any.whl",
            "molkey-0.2.0-py3-none-any.whl",
            "abl1_dragon-0.6.2-py3-none-any.whl",
        "solide-0.8.11-py3-none-any.whl",
        "qiaxcel_fortynning-0.2.0-py3-none-any.whl",
        )
    )
    seen: list[tuple[str, object]] = []
    monkeypatch.setattr(
        builder,
        "validate_manifest_consistency",
        lambda _version: True,
        raising=False,
    )
    monkeypatch.setattr(
        builder,
        "assert_clean_pinned_checkouts",
        lambda _root: [Path(str(index)) for index in range(9)],
    )

    def build_wheel(_source: Path, destination: Path) -> None:
        (destination / next(names)).write_bytes(b"wheel")

    def download(destination: Path, target: builder.PythonTarget) -> None:
        seen.append(("download", target))
        (destination / "packaging-25.0-py3-none-any.whl").write_bytes(b"dependency")

    def assemble(
        _version: str,
        output: Path,
        _packages: list[Path],
        _dependencies: list[Path],
        target: builder.PythonTarget,
    ) -> Path:
        seen.append(("assemble", target))
        return output / "release"

    monkeypatch.setattr(builder, "_build_wheel", build_wheel)
    monkeypatch.setattr(builder, "_download_dependencies", download)
    monkeypatch.setattr(builder, "_copy_vendored_wheels", lambda _r, _d: None)
    monkeypatch.setattr(builder, "_validate_dependency_matrix", lambda _p, _d, _t: None)
    monkeypatch.setattr(builder, "_normalize_wheel", lambda _wheel: None)
    monkeypatch.setattr(builder, "assemble_release", assemble)

    result = builder.build_suite("test", tmp_path / "dist", tmp_path / "components")

    assert result == tmp_path / "dist" / "release"
    assert seen == [("download", PYTHON_314), ("assemble", PYTHON_314)]


def test_build_suite_rejects_version_before_building_components(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        builder,
        "validate_manifest_consistency",
        lambda _version: False,
        raising=False,
    )
    monkeypatch.setattr(
        builder,
        "assert_clean_pinned_checkouts",
        lambda _root: pytest.fail("component checkout must not be inspected"),
    )

    with pytest.raises(ValueError, match="does not match the bundled manifest"):
        builder.build_suite(
            "1.0.8-test",
            tmp_path / "dist",
            tmp_path / "components",
        )
