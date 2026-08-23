from __future__ import annotations

from pathlib import Path

import pytest

from emolpat.domain import ModuleSpec, ModuleUnit, SuiteManifest
from emolpat.launch import (
    ApplicationProcessManager,
    ProcessExit,
    resolve_entry_point,
)
from emolpat.manifest import load_manifest

MODULE = ModuleSpec(
    id="hemafrag",
    name="HemaFrag Diagnostics",
    distribution="hemafrag-diagnostics",
    version="1.2.0",
    import_name="hemafrag_diagnostics",
    entry_point="hemafrag_diagnostics.__main__:main",
    icon="icons/hemafrag.svg",
    description_nb="Fragmentanalyse",
    unit=ModuleUnit.HEMATO,
)


@pytest.fixture
def manifest() -> SuiteManifest:
    return load_manifest(Path(__file__).parent / "fixtures" / "valid-manifest.json")


class FakeChild:
    def __init__(self, exit_code: int | None = None) -> None:
        self.exit_code = exit_code

    def poll(self) -> int | None:
        return self.exit_code


def test_resolve_entry_point_returns_a_callable() -> None:
    callback = resolve_entry_point("emolpat.launch:resolve_entry_point")

    assert callback is resolve_entry_point


@pytest.mark.parametrize(
    "value",
    ["missing_separator", ":main", "emolpat.launch:"],
)
def test_resolve_entry_point_rejects_invalid_paths(value: str) -> None:
    with pytest.raises(ValueError, match="entry point"):
        resolve_entry_point(value)


def test_resolve_entry_point_rejects_non_callable_attributes() -> None:
    with pytest.raises(TypeError, match="not callable"):
        resolve_entry_point("emolpat.domain:APPROVED_MODULE_IDS")


def test_manager_starts_trusted_child_command() -> None:
    commands: list[tuple[str, ...]] = []
    child = FakeChild()
    manager = ApplicationProcessManager(
        executable="python-felles.exe",
        spawn=lambda argv: commands.append(argv) or child,
    )

    result = manager.start(MODULE)

    assert result.started
    assert commands == [
        ("python-felles.exe", "-m", "emolpat.module_runner", MODULE.id)
    ]
    assert manager.running_module_ids == frozenset({MODULE.id})


def test_manager_rejects_duplicate_but_allows_different_module(
    manifest: SuiteManifest,
) -> None:
    children = iter((FakeChild(), FakeChild()))
    manager = ApplicationProcessManager(spawn=lambda _argv: next(children))

    assert manager.start(manifest.module("hemafrag")).started
    duplicate = manager.start(manifest.module("hemafrag"))
    assert not duplicate.started
    assert duplicate.error_code == "already_running"
    assert manager.start(manifest.module("igh-merge")).started


def test_poll_removes_finished_children(manifest: SuiteManifest) -> None:
    child = FakeChild()
    manager = ApplicationProcessManager(spawn=lambda _argv: child)
    manager.start(manifest.module("mpn-tolkning"))
    child.exit_code = 0

    assert manager.poll() == (ProcessExit("mpn-tolkning", 0),)
    assert not manager.is_running("mpn-tolkning")


def test_stop_monitoring_never_terminates_child(manifest: SuiteManifest) -> None:
    child = FakeChild()
    manager = ApplicationProcessManager(spawn=lambda _argv: child)
    manager.start(manifest.module("hemafrag"))

    manager.stop_monitoring()

    assert manager.running_module_ids == frozenset()


def test_manager_reports_process_start_failure() -> None:
    def fail_spawn(_argv: tuple[str, ...]) -> FakeChild:
        raise OSError("cannot create process")

    manager = ApplicationProcessManager(spawn=fail_spawn)

    result = manager.start(MODULE)

    assert not result.started
    assert result.error_code == "process_start_failed"
    assert not manager.is_running(MODULE.id)
