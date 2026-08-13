from __future__ import annotations

from pathlib import Path

from emolpat.domain import HealthReport, InstallResult, SuiteState
from emolpat.paths import UserPaths
from emolpat.ui.install_coordinator import InstallCoordinator


def paths_at(root: Path) -> UserPaths:
    return UserPaths(root, root / "logs", root / "record.json", root / "rollback")


def test_coordinator_emits_progress_and_refreshed_health(qtbot, tmp_path: Path) -> None:
    ready = HealthReport(SuiteState.READY, "1.0.0", ())

    def installer(_root, _runner, _paths, progress):
        progress("preflight")
        progress("verification")
        return InstallResult(ok=True, stage="record")

    coordinator = InstallCoordinator(
        tmp_path,
        paths_at(tmp_path / "user"),
        health_loader=lambda: ready,
        installer=installer,
    )
    stages = []
    coordinator.stage_changed.connect(stages.append)

    with qtbot.waitSignal(coordinator.finished, timeout=3000) as signal:
        assert coordinator.start()

    assert stages == ["preflight", "verification"]
    assert signal.args == [InstallResult(ok=True, stage="record"), ready]
    assert not coordinator.running


def test_coordinator_refuses_concurrent_install(qtbot, tmp_path: Path) -> None:
    def installer(_root, _runner, _paths, progress):
        progress("preflight")
        return InstallResult(ok=True, stage="record")

    coordinator = InstallCoordinator(
        tmp_path,
        paths_at(tmp_path / "user"),
        health_loader=lambda: HealthReport(SuiteState.READY, "1.0.0", ()),
        installer=installer,
    )

    with qtbot.waitSignal(coordinator.finished, timeout=3000):
        assert coordinator.start()
        assert not coordinator.start()


def test_coordinator_reports_unexpected_installer_failure(qtbot, tmp_path: Path) -> None:
    repair = HealthReport(
        SuiteState.REPAIR_REQUIRED,
        None,
        ("internal_install_error",),
    )

    def installer(_root, _runner, _paths, progress):
        progress("components")
        raise RuntimeError("simulated failure")

    coordinator = InstallCoordinator(
        tmp_path,
        paths_at(tmp_path / "user"),
        health_loader=lambda: repair,
        installer=installer,
    )

    with qtbot.waitSignal(coordinator.finished, timeout=3000) as signal:
        assert coordinator.start()

    assert signal.args == [InstallResult(ok=False, stage="components"), repair]
    assert not coordinator.running


def test_coordinator_reports_failed_health_refresh(qtbot, tmp_path: Path) -> None:
    def broken_health_loader() -> HealthReport:
        raise RuntimeError("simulated health failure")

    coordinator = InstallCoordinator(
        tmp_path,
        paths_at(tmp_path / "user"),
        health_loader=broken_health_loader,
        installer=lambda _root, _runner, _paths, _progress: InstallResult(
            ok=True,
            stage="record",
        ),
    )

    with qtbot.waitSignal(coordinator.finished, timeout=3000) as signal:
        assert coordinator.start()

    result, health = signal.args
    assert result == InstallResult(ok=True, stage="record")
    assert health.state is SuiteState.REPAIR_REQUIRED
    assert health.issues == ("internal_install_error",)
