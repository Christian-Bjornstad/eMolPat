from __future__ import annotations

from PyQt6.QtCore import QTimer

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.ui.app import PortalOutcome, run_portal
from emolpat.ui.main_window import MainWindow


def test_portal_outcome_defaults_to_no_selection() -> None:
    assert PortalOutcome().selected_module_id is None


def test_run_portal_returns_selected_module_after_window_closes(
    qapp,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    def select_module() -> None:
        windows = [
            widget
            for widget in qapp.topLevelWidgets()
            if isinstance(widget, MainWindow)
        ]
        assert len(windows) == 1
        windows[0].card("mpn-tolkning").open_button.click()

    QTimer.singleShot(0, select_module)

    outcome = run_portal(manifest, ready_report)

    assert outcome == PortalOutcome(selected_module_id="mpn-tolkning")
