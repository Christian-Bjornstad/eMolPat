from __future__ import annotations

import pytest

from emolpat.domain import ModuleSpec
from emolpat.launch import resolve_entry_point, run_handoff

MODULE = ModuleSpec(
    id="hemafrag",
    name="HemaFrag Diagnostics",
    distribution="hemafrag-diagnostics",
    version="1.2.0",
    import_name="hemafrag_diagnostics",
    entry_point="hemafrag_diagnostics.__main__:main",
    icon="icons/hemafrag.svg",
    description_nb="Fragmentanalyse",
)


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


def test_handoff_calls_declared_entrypoint_after_portal_exit() -> None:
    events: list[str] = []

    result = run_handoff(
        MODULE,
        resolver=lambda value: lambda: events.append(f"started:{value}"),
    )

    assert events == [f"started:{MODULE.entry_point}"]
    assert result.started
    assert result.error_code is None


def test_handoff_reports_import_failure_without_starting() -> None:
    def fail_resolution(_value: str):
        raise ImportError("dependency unavailable")

    result = run_handoff(MODULE, resolver=fail_resolution)

    assert not result.started
    assert result.error_code == "entrypoint_import_failed"
    assert result.module_id == MODULE.id
    assert "dependency unavailable" in (result.message or "")


def test_handoff_reports_invalid_entrypoint_without_starting() -> None:
    def fail_resolution(_value: str):
        raise TypeError("not callable")

    result = run_handoff(MODULE, resolver=fail_resolution)

    assert not result.started
    assert result.error_code == "entrypoint_invalid"


def test_handoff_does_not_hide_errors_after_application_start() -> None:
    def fail_after_start() -> None:
        raise RuntimeError("application crashed")

    with pytest.raises(RuntimeError, match="application crashed"):
        run_handoff(MODULE, resolver=lambda _value: fail_after_start)
