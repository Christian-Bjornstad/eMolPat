"""QApplication lifecycle for the portal side of an app handoff."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from importlib.resources import files
from typing import Protocol

from PyQt6 import sip
from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.launch import EntryPointResolver, resolve_entry_point, run_handoff
from emolpat.ui.main_window import MainWindow


@dataclass(frozen=True)
class PortalOutcome:
    """The user's portal selection, if the window was not simply closed."""

    selected_module_id: str | None = None


class PortalFactory(Protocol):
    """Callable portal session with the manifest used to resolve selections."""

    manifest: SuiteManifest

    def __call__(self, startup_error: str | None = None) -> PortalOutcome: ...


def run_portal(
    manifest: SuiteManifest,
    health: HealthReport,
    startup_error: str | None = None,
) -> PortalOutcome:
    """Run and fully release the portal before returning a selection."""
    app = QApplication.instance()
    owns_application = app is None
    if owns_application:
        app = QApplication(sys.argv)
    app.setApplicationName("eMolPat")
    app.setOrganizationName("eMolPat")
    app.setWindowIcon(
        QIcon(str(files("emolpat.ui.resources").joinpath("emolpat.svg")))
    )

    selected: list[str] = []
    window = MainWindow(manifest, health)
    window.module_selected.connect(selected.append)
    window.module_selected.connect(lambda _module_id: app.quit())
    window.show()
    if startup_error:
        QMessageBox.warning(window, "Programmet kunne ikke åpnes", startup_error)
    app.exec()

    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    if owns_application:
        sip.delete(app)
    return PortalOutcome(selected[0] if selected else None)


def run_application_loop(
    portal_factory: PortalFactory,
    resolver: EntryPointResolver = resolve_entry_point,
) -> int:
    """Reopen the portal after pre-start failure; otherwise hand off once."""
    startup_error: str | None = None
    had_failure = False
    while True:
        outcome = portal_factory(startup_error)
        if outcome.selected_module_id is None:
            return 1 if had_failure else 0

        module = portal_factory.manifest.module(outcome.selected_module_id)
        result = run_handoff(module, resolver=resolver)
        if result.started:
            return result.exit_code or 0

        had_failure = True
        logging.getLogger("emolpat").error(
            "module_start_failed module_id=%s error_code=%s",
            module.id,
            result.error_code,
        )
        startup_error = (
            f"{module.name} kunne ikke åpnes. "
            "Kontroller systemstatus, eller kontakt teknisk støtte."
        )
