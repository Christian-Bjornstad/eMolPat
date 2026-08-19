from __future__ import annotations

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.ui.main_window import MainWindow
from emolpat.ui.translations import INSTALL_STAGE_TEXT


def test_every_install_stage_has_plain_english_progress_text() -> None:
    assert set(INSTALL_STAGE_TEXT) == {
        "preflight",
        "dependencies",
        "components",
        "verification",
        "record",
        "rollback",
    }
    assert INSTALL_STAGE_TEXT["dependencies"] == "Installing verified dependencies"


def test_portal_can_show_accessible_install_progress(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    window.show_install_stage("verification")

    assert window.install_progress.isVisibleTo(window)
    assert window.install_progress.text() == "Verifying the entire installation"
    assert window.install_progress.accessibleName() == "Installation status"
