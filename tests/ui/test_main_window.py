from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

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


def test_portal_uses_plain_version_copy_and_removes_privacy_footer(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    visible_copy = " ".join(label.text() for label in window.findChildren(QLabel))

    assert window.version_label.text() == "Versjon 1.0.0"
    assert "Suite 1.0.0" not in visible_copy
    assert "Kun teknisk status" not in visible_copy
    assert "Ingen pasientdata lagres" not in visible_copy


def test_about_tab_opens_creator_and_portal_information(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    qtbot.mouseClick(window.about_button, Qt.MouseButton.LeftButton)

    about_copy = " ".join(
        label.text() for label in window.about_page.findChildren(QLabel)
    )
    assert window.pages.currentWidget() is window.about_page
    assert "Om eMolPat" in about_copy
    assert "samlet portal for molekylærpatologiske analyseverktøy" in about_copy
    assert "HemaFrag Diagnostics" in about_copy
    assert "IGH Merge" in about_copy
    assert "VPM / HTS Tolkning" in about_copy
    assert "MPN Tolkning" in about_copy
    assert "Utviklet av Christian Bjørnstad" in about_copy
    assert window.about_button.accessibleName() == "Om eMolPat"


def test_ready_state_is_a_compact_top_status_box(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    assert window.status_banner.text() == "Klar til bruk"
    assert window.status_banner.maximumWidth() <= 220
    assert window.status_banner.detail_label.isHidden()
