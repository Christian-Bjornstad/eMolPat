"""QApplication lifecycle for the persistent eMolPat portal."""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from importlib.resources import files

from PyQt6 import sip
from PyQt6.QtCore import QCoreApplication, QEvent, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

from emolpat.domain import HealthReport, InstallResult, SuiteManifest
from emolpat.launch import ApplicationProcessManager
from emolpat.paths import UserPaths
from emolpat.ui.install_coordinator import InstallCoordinator
from emolpat.ui.main_window import MainWindow


def run_portal(
    manifest: SuiteManifest,
    health: HealthReport,
    startup_error: str | None = None,
    release_root=None,
    paths: UserPaths | None = None,
    health_loader: Callable[[], HealthReport] | None = None,
    process_manager: ApplicationProcessManager | None = None,
) -> int:
    """Run one persistent portal session while child apps execute separately."""
    app = QApplication.instance()
    owns_application = app is None
    if owns_application:
        app = QApplication(sys.argv)
    app.setApplicationName("eMolPat")
    app.setOrganizationName("eMolPat")
    app.setWindowIcon(
        QIcon(str(files("emolpat.ui.resources").joinpath("emolpat.png")))
    )

    manager = process_manager or ApplicationProcessManager()
    window = MainWindow(manifest, health, release_available=release_root is not None)
    coordinator = None
    if release_root is not None and paths is not None and health_loader is not None:
        coordinator = InstallCoordinator(release_root, paths, health_loader)
        coordinator.stage_changed.connect(window.show_install_stage)
        coordinator.finished.connect(window.finish_install)
        window.install_requested.connect(coordinator.start)

        def log_install_failure(result: InstallResult, _health: HealthReport) -> None:
            if not result.ok:
                logging.getLogger("emolpat").error(
                    "install_failed stage=%s return_code=%s rolled_back=%s",
                    result.stage,
                    result.return_code,
                    str(result.rolled_back).lower(),
                )

        coordinator.finished.connect(log_install_failure)
    def start_module(module_id: str) -> None:
        module = manifest.module(module_id)
        result = manager.start(module)
        if result.started:
            window.set_module_running(module_id)
            return
        window.set_module_failed(module_id, result.error_code or "unknown")
        logging.getLogger("emolpat").error(
            "module_start_failed module_id=%s error_code=%s",
            module_id,
            result.error_code,
        )

    def poll_children() -> None:
        for process_exit in manager.poll():
            if process_exit.exit_code == 0:
                window.set_module_ready(process_exit.module_id)
            else:
                window.set_module_failed(process_exit.module_id, "process_exit_failed")

    window.module_selected.connect(start_module)
    process_timer = QTimer(window)
    window.process_timer = process_timer
    process_timer.setInterval(250)
    process_timer.timeout.connect(poll_children)
    process_timer.start()
    window.show()
    if startup_error:
        QMessageBox.warning(window, "Programmet kunne ikke åpnes", startup_error)
    app.exec()

    process_timer.stop()
    manager.stop_monitoring()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    if owns_application:
        sip.delete(app)
    return 0
