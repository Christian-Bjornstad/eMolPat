from __future__ import annotations

from pathlib import Path

from emolpat import __main__ as entrypoint
from emolpat.domain import HealthReport, SuiteState


def test_bundled_manifest_identifies_current_prerelease() -> None:
    assert entrypoint.bundled_manifest().suite_version == "1.0.7"


def test_main_uses_observed_installation_health(monkeypatch, tmp_path: Path) -> None:
    observed = HealthReport(
        state=SuiteState.REPAIR_REQUIRED,
        suite_version="1.0.0",
        issues=("missing import: igh_merge",),
    )
    captured = {}
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(entrypoint, "configure_logging", lambda _paths: None)
    monkeypatch.setattr(
        entrypoint,
        "probe_health",
        lambda manifest, paths: observed,
        raising=False,
    )

    def run_loop(portal):
        captured["portal"] = portal
        return 17

    monkeypatch.setattr(entrypoint, "run_application_loop", run_loop)

    result = entrypoint.main()

    assert result == 17
    assert captured["portal"].health is observed
