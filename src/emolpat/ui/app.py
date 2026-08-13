"""QApplication lifecycle for the portal side of an app handoff."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from importlib.resources import files

from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.ui.main_window import MainWindow


@dataclass(frozen=True)
class PortalOutcome:
    """The user's portal selection, if the window was not simply closed."""

    selected_module_id: str | None = None


def run_portal(manifest: SuiteManifest, health: HealthReport) -> PortalOutcome:
    """Run and fully release the portal before returning a selection."""
    app = QApplication.instance()
    if app is None:
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
    app.exec()

    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    return PortalOutcome(selected[0] if selected else None)
