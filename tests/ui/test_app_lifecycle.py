from __future__ import annotations

from PyQt6.QtCore import QTimer

from emolpat.domain import HealthReport, InstallResult, SuiteManifest, SuiteState
from emolpat.launch import LaunchResult, ProcessExit
from emolpat.paths import UserPaths
from emolpat.ui.app import run_portal
from emolpat.ui.main_window import MainWindow


class FakeProcessManager:
    def __init__(self) -> None:
        self.started: list[str] = []
        self.exits: list[ProcessExit] = []
        self.failures: set[str] = set()
        self.monitoring_stopped = False
        self.poll_count = 0

    def start(self, module) -> LaunchResult:
        if module.id in self.failures:
            return LaunchResult(
                module.id,
                started=False,
                error_code="process_start_failed",
            )
        self.started.append(module.id)
        return LaunchResult(module.id, started=True)

    def poll(self) -> tuple[ProcessExit, ...]:
        self.poll_count += 1
        exits = tuple(self.exits)
        self.exits.clear()
        return exits

    def stop_monitoring(self) -> None:
        self.monitoring_stopped = True


def visible_window(qapp) -> MainWindow:
    return next(
        widget for widget in qapp.topLevelWidgets() if isinstance(widget, MainWindow)
    )


def test_click_starts_child_and_keeps_portal_visible(
    qapp, manifest: SuiteManifest, ready_report: HealthReport
) -> None:
    manager = FakeProcessManager()

    def click_then_assert_then_close() -> None:
        window = visible_window(qapp)
        window.card("hemafrag").open_button.click()
        assert window.isVisible()
        assert manager.started == ["hemafrag"]
        window.close()

    QTimer.singleShot(0, click_then_assert_then_close)

    assert run_portal(manifest, ready_report, process_manager=manager) == 0
    assert manager.monitoring_stopped


def test_two_different_cards_start_two_children(
    qapp, manifest: SuiteManifest, ready_report: HealthReport
) -> None:
    manager = FakeProcessManager()

    def start_both_then_close() -> None:
        window = visible_window(qapp)
        window.card("hemafrag").open_button.click()
        window.card("igh-merge").open_button.click()
        window.close()

    QTimer.singleShot(0, start_both_then_close)

    run_portal(manifest, ready_report, process_manager=manager)

    assert manager.started == ["hemafrag", "igh-merge"]


def test_timer_consumes_finished_child(
    qapp, manifest: SuiteManifest, ready_report: HealthReport
) -> None:
    manager = FakeProcessManager()

    def start_child() -> None:
        window = visible_window(qapp)
        window.card("mpn-tolkning").open_button.click()
        manager.exits.append(ProcessExit("mpn-tolkning", 0))
        window.process_timer.timeout.emit()
        try:
            assert manager.poll_count > 0
            assert window.card("mpn-tolkning").open_button.isEnabled()
        finally:
            window.close()

    QTimer.singleShot(0, start_child)

    run_portal(manifest, ready_report, process_manager=manager)


def test_process_start_failure_leaves_portal_visible(
    qapp, manifest: SuiteManifest, ready_report: HealthReport
) -> None:
    manager = FakeProcessManager()
    manager.failures.add("igh-merge")

    def fail_then_assert_then_close() -> None:
        window = visible_window(qapp)
        window.card("igh-merge").open_button.click()
        assert window.isVisible()
        assert window.card("igh-merge").open_button.isEnabled()
        window.close()

    QTimer.singleShot(0, fail_then_assert_then_close)

    assert run_portal(manifest, ready_report, process_manager=manager) == 0


class SignalStub:
    def __init__(self) -> None:
        self.callbacks = []

    def connect(self, callback) -> None:
        self.callbacks.append(callback)


def test_run_portal_wires_install_action_to_coordinator(
    monkeypatch,
    qapp,
    tmp_path,
    manifest: SuiteManifest,
) -> None:
    started = []

    class FakeCoordinator:
        def __init__(self, *_args, **_kwargs) -> None:
            self.stage_changed = SignalStub()
            self.finished = SignalStub()

        def start(self) -> bool:
            started.append(True)
            for callback in self.finished.callbacks:
                callback(
                    InstallResult(ok=True, stage="record"),
                    HealthReport(SuiteState.READY, "1.0.0", ()),
                )
            return True

    monkeypatch.setattr("emolpat.ui.app.InstallCoordinator", FakeCoordinator)
    paths = UserPaths(
        tmp_path,
        tmp_path / "logs",
        tmp_path / "record.json",
        tmp_path / "rollback",
    )

    def install_then_close() -> None:
        window = visible_window(qapp)
        window.install_button.click()
        window.close()

    QTimer.singleShot(0, install_then_close)
    outcome = run_portal(
        manifest,
        HealthReport(SuiteState.NOT_INSTALLED, None, ()),
        release_root=tmp_path,
        paths=paths,
        health_loader=lambda: HealthReport(SuiteState.READY, "1.0.0", ()),
    )

    assert outcome == 0
    assert started == [True]
