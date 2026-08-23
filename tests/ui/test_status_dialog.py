from __future__ import annotations

from emolpat.domain import HealthReport, SuiteState
from emolpat.ui.status_dialog import SystemStatusDialog


def test_ready_dialog_has_no_install_action(qtbot, ready_report) -> None:
    dialog = SystemStatusDialog(ready_report, release_available=True)
    qtbot.addWidget(dialog)

    assert "Klar til bruk" in dialog.summary_label.text()
    assert dialog.version_label.text() == "Installert versjon: 1.0.0"
    assert dialog.action_button.isHidden()


def test_update_dialog_exposes_one_update_action(qtbot) -> None:
    health = HealthReport(SuiteState.UPDATE_AVAILABLE, "1.0.6", ())
    dialog = SystemStatusDialog(health, release_available=True)
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog.action_button.text() == "Oppdater eMolPat"
    assert dialog.action_button.isVisibleTo(dialog)


def test_repair_dialog_shows_controlled_issues_without_raw_details(qtbot) -> None:
    health = HealthReport(
        SuiteState.REPAIR_REQUIRED,
        "1.0.6",
        ("missing_distribution:igh-merge",),
    )
    dialog = SystemStatusDialog(health, release_available=True)
    qtbot.addWidget(dialog)

    assert "IGH Merge" in dialog.details_label.text()
    assert "missing_distribution" not in dialog.details_label.text()
