from __future__ import annotations

import importlib.metadata
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from scripts.build_suite import COMPONENT_DIRECTORIES
from scripts.smoke_installed_suite import smoke_installed_suite
from scripts.test_components import editable_spec
from scripts.test_components import test_components as run_component_tests


def test_component_gate_installs_declared_development_extra(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="demo"\nversion="1"\n'
        '[project.optional-dependencies]\ndev=["pypdf"]\n',
        encoding="utf-8",
    )

    assert editable_spec(tmp_path) == f"{tmp_path}[dev]"


def test_component_gate_runs_declared_commands_with_active_python(tmp_path: Path) -> None:
    calls = []
    for directory in COMPONENT_DIRECTORIES.values():
        source = tmp_path / directory
        source.mkdir()
        (source / "pyproject.toml").write_text(
            '[project]\nname="demo"\nversion="1"\n',
            encoding="utf-8",
        )

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return CompletedProcess(command, 0)

    run_component_tests(
        Path("release/components.json"),
        tmp_path,
        runner=runner,
        python_executable="C:/Python314/python.exe",
    )

    assert len(calls) == 18
    for index in range(0, len(calls), 2):
        install, install_options = calls[index]
        command, test_options = calls[index + 1]
        assert install[:4] == (
            "C:/Python314/python.exe",
            "-m",
            "pip",
            "install",
        )
        assert install_options["check"] is True
        assert command == (
            "C:/Python314/python.exe",
            "-m",
            "pytest",
            "-q",
        )
        assert test_options["check"] is True


def test_installed_suite_gate_resolves_all_zero_argument_entry_points(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    versions = {
        "emolpat": "0.2.0",
        "hemafrag-diagnostics": "1.2.1",
        "igh-merge": "0.2.0",
        "archer-prosess": "0.1.0",
        "mpn-tolkning": "0.1.0",
        "molstat": "0.1.0",
        "molkey": "0.2.0",
        "solide": "0.8.11",
        "abl1-dragon": "0.6.2",
        "qiaxcel-fortynning": "0.2.0",
    }
    imported = []

    monkeypatch.setattr(importlib.metadata, "version", versions.__getitem__)

    class Module:
        @staticmethod
        def main() -> int:
            return 0

        launch_molstat = main

    def importer(name: str):
        imported.append(name)
        return Module()

    result = smoke_installed_suite(
        Path("src/emolpat/ui/resources/suite-manifest.json"),
        importer=importer,
    )

    assert result == 0
    assert imported == [
        "emolpat",
        "hemafrag_diagnostics",
        "hemafrag_diagnostics.__main__",
        "igh_merge",
        "igh_merge.__main__",
        "archer_processor",
        "archer_processor.__main__",
        "mpn_tolkning",
        "mpn_tolkning.__main__",
        "molstat",
        "emolpat.entrypoints",
        "molkey",
        "molkey.__main__",
        "abl1_workstation",
        "abl1_workstation.__main__",
        "solide",
        "solide.__main__",
        "qiaxcel",
        "qiaxcel.__main__",
    ]
    assert "10 distributions, 9 entry points" in capsys.readouterr().out


def test_component_gate_installs_declared_test_file_and_native_wheel(tmp_path):
    calls = []
    for directory in COMPONENT_DIRECTORIES.values():
        source = tmp_path / directory
        source.mkdir()
        (source / "pyproject.toml").write_text('[project]\nname="demo"\nversion="1"\n')
    source = tmp_path / "HemaFrag-Diagnostics"
    requirements = source / "requirements-dev.txt"
    requirements.write_text("PyInstaller>=6.20\n")
    native = source / "wheels" / "fraggler_kernels-0.1.3-cp310-abi3-win_amd64.whl"
    native.parent.mkdir()
    native.write_bytes(b"test wheel")

    def runner(command, **kwargs):
        calls.append(tuple(command))
        return CompletedProcess(command, 0)

    run_component_tests(Path("release/components.json"), tmp_path, runner=runner,
                        python_executable="python314")
    assert ("python314", "-m", "pip", "install", "-r", str(requirements)) in calls
    assert ("python314", "-m", "pip", "install", "--no-deps", str(native)) in calls
    assert calls.index(("python314", "-m", "pip", "install", "--no-deps", str(native))) < calls.index(("python314", "-m", "pytest", "-q"))
