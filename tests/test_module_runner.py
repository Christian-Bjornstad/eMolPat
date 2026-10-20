import sys
from pathlib import Path

import pytest

from emolpat import module_runner
from emolpat.domain import SuiteManifest
from emolpat.manifest import load_manifest


@pytest.fixture
def manifest() -> SuiteManifest:
    return load_manifest(Path(__file__).parent / "fixtures" / "valid-manifest.json")


def test_run_module_calls_only_the_manifest_entry_point(
    monkeypatch, manifest: SuiteManifest
) -> None:
    called: list[str] = []
    monkeypatch.setattr(module_runner, "bundled_manifest", lambda: manifest)

    code = module_runner.run_module(
        "igh-merge",
        resolver=lambda value: lambda: called.append(value) or 7,
    )

    assert code == 7
    assert called == ["igh_merge.__main__:main"]


def test_run_module_rejects_unknown_module_without_resolving(
    monkeypatch, manifest: SuiteManifest
) -> None:
    monkeypatch.setattr(module_runner, "bundled_manifest", lambda: manifest)
    resolved: list[str] = []

    code = module_runner.run_module(
        "unknown",
        resolver=lambda value: resolved.append(value),
    )

    assert code == 2
    assert resolved == []


def test_main_requires_exactly_one_module_id() -> None:
    assert module_runner.main([]) == 2
    assert module_runner.main(["hemafrag", "extra"]) == 2


def test_child_entrypoint_receives_no_portal_arguments(monkeypatch, manifest) -> None:
    monkeypatch.setattr(module_runner, "bundled_manifest", lambda: manifest)
    arguments = ["module_runner.py", "igh-merge"]
    monkeypatch.setattr(sys, "argv", arguments)
    seen = []

    def resolve(value):
        seen.append(tuple(sys.argv))
        return lambda: seen.append(tuple(sys.argv)) or 0

    assert module_runner.run_module("igh-merge", resolver=resolve) == 0
    assert seen == [("igh_merge.__main__:main",)] * 2
    assert sys.argv is arguments


def test_child_arguments_restored_when_callback_exits(monkeypatch, manifest) -> None:
    monkeypatch.setattr(module_runner, "bundled_manifest", lambda: manifest)
    arguments = ["module_runner.py", "igh-merge"]
    monkeypatch.setattr(sys, "argv", arguments)

    def callback():
        raise SystemExit(4)

    with pytest.raises(SystemExit) as error:
        module_runner.run_module("igh-merge", resolver=lambda _value: callback)

    assert error.value.code == 4
    assert sys.argv is arguments
