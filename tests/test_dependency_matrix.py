from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts.build_suite import _validate_dependency_matrix


def wheel(
    root: Path,
    name: str,
    *,
    requirements: tuple[str, ...] = (),
    python_requires: str = ">=3.12",
    tag: str = "py3-none-any",
) -> Path:
    path = root / f"{name}-1.0.0-{tag}.whl"
    metadata = [
        "Metadata-Version: 2.1",
        f"Name: {name}",
        "Version: 1.0.0",
        f"Requires-Python: {python_requires}",
        *(f"Requires-Dist: {value}" for value in requirements),
    ]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            f"{name}-1.0.0.dist-info/METADATA", "\n".join(metadata) + "\n"
        )
    return path


def test_rejects_missing_transitive_dependency(tmp_path: Path) -> None:
    app = wheel(tmp_path, "app", requirements=("dependency",))
    dependency = wheel(tmp_path, "dependency", requirements=("missing>=2",))

    with pytest.raises(RuntimeError, match="unsatisfied dependency.*missing"):
        _validate_dependency_matrix([app], [dependency])


def test_rejects_incompatible_transitive_dependency(tmp_path: Path) -> None:
    app = wheel(tmp_path, "app", requirements=("dependency",))
    dependency = wheel(tmp_path, "dependency", requirements=("transitive>=2",))
    transitive = wheel(tmp_path, "transitive")

    with pytest.raises(RuntimeError, match="unsatisfied dependency.*transitive"):
        _validate_dependency_matrix([app], [dependency, transitive])


def test_checks_markers_for_target_python_instead_of_build_host(tmp_path: Path) -> None:
    app = wheel(
        tmp_path, "app", requirements=('missing; python_version >= "3.14"',)
    )

    with pytest.raises(RuntimeError, match="unsatisfied dependency.*missing"):
        _validate_dependency_matrix([app], [])


def test_ignores_markers_for_older_python(tmp_path: Path) -> None:
    app = wheel(
        tmp_path, "app", requirements=('old_dependency; python_version < "3.14"',)
    )

    _validate_dependency_matrix([app], [])


def test_checks_markers_for_windows_even_on_another_build_os(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import packaging.markers

    original = packaging.markers.default_environment
    monkeypatch.setattr(
        packaging.markers,
        "default_environment",
        lambda: {**original(), "sys_platform": "linux", "os_name": "posix"},
    )
    app = wheel(tmp_path, "app", requirements=('missing; sys_platform == "win32"',))

    with pytest.raises(RuntimeError, match="unsatisfied dependency.*missing"):
        _validate_dependency_matrix([app], [])


@pytest.mark.parametrize("as_dependency", [False, True])
def test_rejects_requires_python_excluding_release_target(
    tmp_path: Path, as_dependency: bool
) -> None:
    incompatible = wheel(tmp_path, "incompatible", python_requires="<3.14")
    packages, dependencies = ([], [incompatible]) if as_dependency else ([incompatible], [])

    with pytest.raises(RuntimeError, match="Requires-Python.*incompatible"):
        _validate_dependency_matrix(packages, dependencies)


@pytest.mark.parametrize("tag", ["cp312-cp312-win_amd64", "cp314-cp314-manylinux_2_17_x86_64"])
def test_rejects_wheels_for_another_runtime(tmp_path: Path, tag: str) -> None:
    incompatible = wheel(tmp_path, "incompatible", tag=tag)

    with pytest.raises(RuntimeError, match="incompatible wheel.*incompatible"):
        _validate_dependency_matrix([], [incompatible])


def test_accepts_cpython_stable_abi_wheel(tmp_path: Path) -> None:
    dependency = wheel(tmp_path, "dependency", tag="cp312-abi3-win_amd64")

    _validate_dependency_matrix([], [dependency])


def test_propagates_requested_extras_through_transitive_dependencies(tmp_path: Path) -> None:
    app = wheel(tmp_path, "app", requirements=("dependency[gui]",))
    dependency = wheel(
        tmp_path, "dependency", requirements=('missing; extra == "gui"',)
    )

    with pytest.raises(RuntimeError, match="unsatisfied dependency.*missing"):
        _validate_dependency_matrix([app], [dependency])


def test_revisits_dependency_when_an_extra_is_discovered_later(tmp_path: Path) -> None:
    app = wheel(tmp_path, "app", requirements=("middle",))
    dependency = wheel(
        tmp_path, "dependency", requirements=('missing; extra == "gui"',)
    )
    middle = wheel(tmp_path, "middle", requirements=("dependency[gui]",))

    with pytest.raises(RuntimeError, match="unsatisfied dependency.*missing"):
        _validate_dependency_matrix([app], [dependency, middle])


def test_leaves_unrequested_extras_optional(tmp_path: Path) -> None:
    app = wheel(tmp_path, "app", requirements=("dependency",))
    dependency = wheel(
        tmp_path, "dependency", requirements=('optional; extra == "gui"',)
    )

    _validate_dependency_matrix([app], [dependency])


def test_rejects_os_version_markers_without_an_explicit_target(tmp_path: Path) -> None:
    app = wheel(tmp_path, "app", requirements=('missing; platform_release == "99"',))

    with pytest.raises(RuntimeError, match="OS-version marker"):
        _validate_dependency_matrix([app], [])
