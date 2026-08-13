from __future__ import annotations

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.ui.main_window import MainWindow
from emolpat.ui.translations import INSTALL_STAGE_TEXT


def test_every_install_stage_has_plain_norwegian_progress_text() -> None:
    assert set(INSTALL_STAGE_TEXT) == {
        "preflight",
        "dependencies",
        "components",
        "verification",
        "record",
        "rollback",
    }
    assert INSTALL_STAGE_TEXT["dependencies"] == "Installerer godkjente avhengigheter"


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
    assert window.install_progress.text() == "Kontrollerer hele installasjonen"
    assert window.install_progress.accessibleName() == "Installasjonsstatus"
