from __future__ import annotations

import logging

from PyQt6.QtCore import QTimer

from emolpat.domain import HealthReport, InstallResult, SuiteManifest, SuiteState
from emolpat.launch import LaunchResult, ProcessExit
from emolpat.paths import UserPaths
from emolpat.ui.app import run_portal
from emolpat.ui.main_window import MainWindow


class FakeProcessManager:
    def __init__(self, running: set[str] | None = None) -> None:
        self.started: list[str] = []
        self.exits: list[ProcessExit] = []
        self.failures: set[str] = set()
        self.monitoring_stopped = False
        self.poll_count = 0
        self.running = set(running or ())

    @property
    def running_module_ids(self) -> frozenset[str]:
        return frozenset(self.running)

    def start(self, module) -> LaunchResult:
        if module.id in self.failures:
            return LaunchResult(
                module.id,
                started=False,
                error_code="process_start_failed",
            )
        self.started.append(module.id)
        self.running.add(module.id)
        return LaunchResult(module.id, started=True)

    def poll(self) -> tuple[ProcessExit, ...]:
        self.poll_count += 1
        exits = tuple(self.exits)
        self.exits.clear()
        for process_exit in exits:
            self.running.discard(process_exit.module_id)
        return exits

    def stop_monitoring(self) -> None:
        self.monitoring_stopped = True


def visible_window(qapp) -> MainWindow:
    return next(
        widget for widget in qapp.topLevelWidgets() if isinstance(widget, MainWindow)
    )


def run_portal_with_scheduled_click_and_close(
    qapp,
    manifest: SuiteManifest,
    health: HealthReport,
    *,
    process_manager: FakeProcessManager,
    module_id: str,
) -> int:
    def click_and_close() -> None:
        window = visible_window(qapp)
        window.card(module_id).open_button.click()
        window.close()

    QTimer.singleShot(0, click_and_close)
    return run_portal(
        manifest,
        health,
        process_manager=process_manager,
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


def test_install_is_blocked_while_analysis_app_runs(
    monkeypatch,
    qapp,
    manifest: SuiteManifest,
    ready_report: HealthReport,
    tmp_path,
) -> None:
    manager = FakeProcessManager(running={"hemafrag"})
    starts: list[bool] = []
    warnings: list[str] = []

    class CoordinatorStub:
        def __init__(self, *_args, **_kwargs) -> None:
            self.stage_changed = SignalStub()
            self.finished = SignalStub()

        def start(self) -> bool:
            starts.append(True)
            return True

    monkeypatch.setattr("emolpat.ui.app.InstallCoordinator", CoordinatorStub)
    monkeypatch.setattr(
        "emolpat.ui.main_window.QMessageBox.warning",
        lambda _parent, _title, message: warnings.append(message),
    )

    def request_then_close() -> None:
        window = visible_window(qapp)
        window.install_requested.emit()
        window.close()

    QTimer.singleShot(0, request_then_close)

    run_portal(
        manifest,
        ready_report,
        release_root=tmp_path,
        paths=UserPaths(
            tmp_path,
            tmp_path / "logs",
            tmp_path / "install-record.json",
            tmp_path / "rollback",
        ),
        health_loader=lambda: ready_report,
        process_manager=manager,
    )

    assert starts == []
    assert warnings == [
        (
            "Lukk kjørende analyseapper før eMolPat oppdateres eller repareres.\n"
            "Kjører: HemaFrag Diagnostics"
        )
    ]
    assert manager.running_module_ids == frozenset({"hemafrag"})


def test_process_failure_log_contains_only_controlled_fields(
    caplog,
    qapp,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    manager = FakeProcessManager()
    manager.failures.add("hemafrag")

    with caplog.at_level(logging.INFO, logger="emolpat"):
        run_portal_with_scheduled_click_and_close(
            qapp,
            manifest,
            ready_report,
            process_manager=manager,
            module_id="hemafrag",
        )

    record = next(
        item
        for item in caplog.records
        if item.msg == "module_process_failed module_id=%s error_code=%s"
    )
    assert record.args == ("hemafrag", "process_start_failed")
    assert "patient" not in record.getMessage().lower()
