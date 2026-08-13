"""Run the existing offline installer without blocking the Qt interface."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from emolpat.domain import HealthReport, InstallResult, SuiteState
from emolpat.install import CommandRunner, install_release, run_command
from emolpat.paths import UserPaths


class Installer(Protocol):
    def __call__(
        self,
        release_root: Path,
        runner: CommandRunner,
        paths: UserPaths,
        progress: Callable[[str], None],
    ) -> InstallResult: ...


class _InstallThread(QThread):
    stage_changed = pyqtSignal(str)

    def __init__(
        self,
        release_root: Path,
        paths: UserPaths,
        health_loader: Callable[[], HealthReport],
        installer: Installer,
        runner: CommandRunner,
        parent: QObject,
    ) -> None:
        super().__init__(parent)
        self.release_root = release_root
        self.paths = paths
        self.health_loader = health_loader
        self.installer = installer
        self.runner = runner
        self.result: InstallResult | None = None
        self.health: HealthReport | None = None

    def run(self) -> None:
        stage = "preflight"

        def report_progress(current_stage: str) -> None:
            nonlocal stage
            stage = current_stage
            self.stage_changed.emit(current_stage)

        try:
            self.result = self.installer(
                self.release_root,
                self.runner,
                self.paths,
                report_progress,
            )
        except Exception:
            logging.getLogger("emolpat").exception(
                "unexpected_install_failure stage=%s",
                stage,
            )
            self.result = InstallResult(ok=False, stage=stage)

        try:
            self.health = self.health_loader()
        except Exception:
            logging.getLogger("emolpat").exception("health_refresh_failed")
            self.health = HealthReport(
                SuiteState.REPAIR_REQUIRED,
                None,
                ("internal_install_error",),
            )


class InstallCoordinator(QObject):
    """Own one installer thread and expose stable UI-facing signals."""

    stage_changed = pyqtSignal(str)
    finished = pyqtSignal(object, object)

    def __init__(
        self,
        release_root: Path,
        paths: UserPaths,
        health_loader: Callable[[], HealthReport],
        installer: Installer = install_release,
        runner: CommandRunner = run_command,
    ) -> None:
        super().__init__()
        self.release_root = release_root
        self.paths = paths
        self.health_loader = health_loader
        self.installer = installer
        self.runner = runner
        self._thread: _InstallThread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None

    def start(self) -> bool:
        if self.running:
            return False
        thread = _InstallThread(
            self.release_root,
            self.paths,
            self.health_loader,
            self.installer,
            self.runner,
            self,
        )
        thread.stage_changed.connect(self.stage_changed)
        thread.finished.connect(self._thread_finished)
        self._thread = thread
        thread.start()
        return True

    @pyqtSlot()
    def _thread_finished(self) -> None:
        thread = self._thread
        if thread is None:
            return
        result = thread.result
        health = thread.health
        thread.deleteLater()
        self._thread = None
        if result is not None and health is not None:
            self.finished.emit(result, health)
