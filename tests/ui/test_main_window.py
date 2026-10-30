from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QScrollArea

from emolpat.domain import (
    HealthReport,
    InstallResult,
    SuiteManifest,
    SuiteState,
)
from emolpat.ui.main_window import MainWindow
from emolpat.ui.widgets import ApplicationCard, ApplicationGrid, StatusControl


def test_portal_shows_nine_real_modules(
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
        "molstat",
        "molkey",
        "dragen",
        "solide",
        "qiaxcel",
    ]
    assert all(not card.module_icon.isNull() for card in window.application_cards)
    assert all(card.open_button.isEnabled() for card in window.application_cards)


def test_sidebar_contains_only_apps_and_about(qtbot, manifest, ready_report):
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    assert [button.text() for button in window.navigation_buttons] == [
        "Apper", "Om eMolPat"
    ]
    assert window.pages.count() == 2
    assert window.pages.currentWidget() is window.applications_page


def test_all_apps_share_the_default_page(qtbot, manifest, ready_report):
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    cards = window.applications_page.findChildren(ApplicationCard)
    assert {card.module_id for card in cards} == {
        module.id for module in manifest.modules
    }
    assert all(card.isVisibleTo(window) for card in cards)
    assert window.results_label.text() == "9 apper"


def test_app_cards_show_launch_information_without_descriptions(
    qtbot, manifest, ready_report
):
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    for card in window.application_cards:
        module = manifest.module(card.module_id)
        labels = card.findChildren(QLabel)
        assert not any(
            label.objectName() == "moduleDescription" and label.isVisibleTo(window)
            for label in labels
        )
        assert module.description_nb not in [label.text() for label in labels]
        assert card.findChild(QLabel, "moduleName").text() == module.name
        assert card.findChild(QLabel, "moduleVersion").text() == (
            f"Versjon {module.version}"
        )
        assert not card.findChild(QLabel, "moduleIcon").pixmap().isNull()
        assert card.status_label.isVisibleTo(window)
        assert card.open_button.isVisibleTo(window)


def test_compact_cards_fit_three_rows_in_a_wide_window(qtbot, manifest, ready_report):
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.resize(1600, 800)
    window.show()

    qtbot.waitUntil(lambda: window.application_grid.columns == 3)

    qtbot.waitUntil(lambda: window.app_scroll.verticalScrollBar().maximum() == 0)
    assert all(card.isVisibleTo(window) for card in window.application_cards)


def test_molkey_launches_and_keeps_portal_open(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    with qtbot.waitSignal(window.module_selected) as signal:
        qtbot.mouseClick(
            window.card("molkey").open_button,
            Qt.MouseButton.LeftButton,
        )

    assert signal.args == ["molkey"]
    assert window.isVisible()


def test_molstat_launches_from_catalog_and_blocks_duplicate_clicks(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    with qtbot.waitSignal(window.module_selected) as signal:
        qtbot.mouseClick(
            window.card("molstat").open_button,
            Qt.MouseButton.LeftButton,
        )

    assert signal.args == ["molstat"]
    window.set_module_running("molstat")
    assert window.card("molstat").open_button.text() == "Kjører"
    assert not window.card("molstat").open_button.isEnabled()
    assert window.isVisible()


def test_clicking_open_emits_selection_and_keeps_portal_open(
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
    assert window.isVisible()


def test_running_card_blocks_duplicate_launch(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    window.set_module_running("hemafrag")

    card = window.card("hemafrag")
    assert card.open_button.text() == "Kjører"
    assert not card.open_button.isEnabled()
    assert window.card("igh-merge").open_button.isEnabled()


def test_finished_card_returns_to_ready(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.set_module_running("mpn-tolkning")

    window.set_module_ready("mpn-tolkning")

    card = window.card("mpn-tolkning")
    assert card.open_button.text() == "Åpne app"
    assert card.open_button.isEnabled()


def test_failed_card_offers_retry_without_exposing_details(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    window.set_module_failed("igh-merge", "process_start_failed")

    card = window.card("igh-merge")
    assert card.open_button.text() == "Prøv igjen"
    assert card.open_button.isEnabled()
    assert "kunne ikke åpnes" in card.status_label.text().lower()
    assert "process_start_failed" not in card.status_label.text()


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
    assert "HemaFrag" in about_copy
    assert "IGH Merge" in about_copy
    assert "VPM / HTS Tolkning" in about_copy
    assert "MPN Tolkning" in about_copy
    assert all(module.name in about_copy for module in manifest.modules)
    assert "LVMS" not in about_copy
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


def test_status_control_opens_compact_system_dialog(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    qtbot.mouseClick(window.status_banner, Qt.MouseButton.LeftButton)

    assert window.status_dialog.isVisibleTo(window)
    assert window.status_banner.maximumWidth() <= 220


def test_clinical_light_stylesheet_has_focus_and_semantic_states(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    stylesheet = window.styleSheet()
    assert "#EDF4F6" in stylesheet
    assert "#073F43" in stylesheet
    assert ":focus" in stylesheet
    assert '[state="ready"]' in stylesheet
    assert '[state="update_available"]' in stylesheet
    assert '[state="repair_required"]' in stylesheet


def test_not_installed_shows_install_action_and_disables_launch(
    qtbot,
    manifest: SuiteManifest,
) -> None:
    health = HealthReport(SuiteState.NOT_INSTALLED, None, ("not installed",))
    window = MainWindow(manifest, health, release_available=True)
    qtbot.addWidget(window)

    assert not any(card.open_button.isEnabled() for card in window.application_cards)
    assert window.install_button.text() == "Installer programmer"
    assert not window.install_button.isHidden()


def test_repair_state_shows_repair_action(qtbot, manifest: SuiteManifest) -> None:
    health = HealthReport(SuiteState.REPAIR_REQUIRED, "1.0.0", ("missing",))
    window = MainWindow(manifest, health, release_available=True)
    qtbot.addWidget(window)

    assert window.install_button.text() == "Reparer installasjon"


def test_successful_install_refresh_enables_all_apps(
    qtbot,
    manifest: SuiteManifest,
) -> None:
    window = MainWindow(
        manifest,
        HealthReport(SuiteState.NOT_INSTALLED, None, ()),
        release_available=True,
    )
    qtbot.addWidget(window)
    window.show()
    window.set_install_running(True)
    window.show_install_stage("record")

    window.finish_install(
        InstallResult(ok=True, stage="record"),
        HealthReport(SuiteState.READY, "1.0.0", ()),
    )

    assert all(card.open_button.isEnabled() for card in window.application_cards)
    assert window.install_button.isHidden()
    assert window.install_progress.text() == (
        "Oppdateringen er fullført. Start eMolPat på nytt."
    )
    assert not window.isVisible()


def test_portal_stays_open_while_installation_is_running(
    qtbot,
    manifest: SuiteManifest,
) -> None:
    window = MainWindow(
        manifest,
        HealthReport(SuiteState.NOT_INSTALLED, None, ()),
        release_available=True,
    )
    qtbot.addWidget(window)
    window.show()
    window.set_install_running(True)

    window.close()

    assert window.isVisible()
    window.set_install_running(False)
    window.close()


def test_closing_portal_closes_open_system_status(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()
    window.status_dialog.show()

    window.close()

    assert not window.isVisible()
    assert not window.status_dialog.isVisible()


def test_health_refresh_preserves_running_app_state(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.set_module_running("hemafrag")

    window.set_health(ready_report)

    assert window.card("hemafrag").open_button.text() == "Kjører"
    assert not window.card("hemafrag").open_button.isEnabled()
    assert window.card("igh-merge").open_button.isEnabled()


def test_installation_disables_launch_until_finished(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    window.set_install_running(True)
    window.set_health(ready_report)

    assert not any(card.open_button.isEnabled() for card in window.application_cards)
    assert "Installasjon pågår" in window.card("hemafrag").status_label.text()
    window.set_install_running(False)
    assert all(card.open_button.isEnabled() for card in window.application_cards)


def test_catalog_can_open_system_status(qtbot, manifest, ready_report):
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.show()

    status = window.applications_page.findChild(StatusControl)
    qtbot.mouseClick(status, Qt.MouseButton.LeftButton)
    assert window.status_dialog.isVisible()


def test_compact_window_reflows_cards_without_horizontal_scrolling(
    qtbot,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.resize(760, 520)
    window.show()
    grid = window.applications_page.findChild(ApplicationGrid)
    scroll = window.applications_page.findChild(QScrollArea)

    qtbot.waitUntil(lambda: grid.columns == 1)

    assert scroll.horizontalScrollBar().maximum() == 0
    assert grid.cards[1].geometry().top() > grid.cards[0].geometry().top()

    window.resize(1200, 800)
    qtbot.waitUntil(
        lambda: grid.columns == 2
        and grid.cards[1].geometry().top() == grid.cards[0].geometry().top()
    )
