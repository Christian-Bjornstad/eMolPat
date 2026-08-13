from __future__ import annotations

from PyQt6.QtCore import Qt

from emolpat.domain import HealthReport, SuiteManifest, SuiteState
from emolpat.ui.main_window import MainWindow


def test_portal_shows_four_real_modules(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    assert [card.module_id for card in window.application_cards] == [
        "hemafrag",
        "igh-merge",
        "vpm-tolkning",
        "mpn-tolkning",
    ]
    assert all(not card.module_icon.isNull() for card in window.application_cards)
    assert all(card.open_button.isEnabled() for card in window.application_cards)


def test_clicking_open_emits_selection_and_closes_portal(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    with qtbot.waitSignal(window.module_selected) as signal:
        qtbot.mouseClick(
            window.card("hemafrag").open_button,
            Qt.MouseButton.LeftButton,
        )

    assert signal.args == ["hemafrag"]
    assert not window.isVisible()


def test_repair_state_disables_launch_and_explains_status(
    qtbot,
    manifest: SuiteManifest,
) -> None:
    health = HealthReport(
        state=SuiteState.REPAIR_REQUIRED,
        suite_version="1.0.0",
        issues=("missing_distribution:igh-merge",),
    )
    window = MainWindow(manifest, health)
    qtbot.addWidget(window)

    assert not any(card.open_button.isEnabled() for card in window.application_cards)
    assert "Reparasjon" in window.status_banner.text()


def test_navigation_and_actions_are_accessibly_named(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    assert window.accessibleName() == "eMolPat programportal"
    assert all(button.accessibleName() for button in window.navigation_buttons)
    assert all(
        card.open_button.accessibleName() for card in window.application_cards
    )
    assert all(card.open_button.minimumHeight() >= 44 for card in window.application_cards)
