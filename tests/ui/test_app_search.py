from dataclasses import replace

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit

from emolpat.domain import HealthReport, SuiteState
from emolpat.ui.main_window import MainWindow


@pytest.fixture
def window(qtbot, manifest, ready_report):
    portal = MainWindow(manifest, ready_report)
    qtbot.addWidget(portal)
    portal.show()
    return portal


def visible_ids(window):
    return [card.module_id for card in window.application_cards if not card.isHidden()]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("  mOlKeY  ", ["molkey"]),
        ("  DrAgEn  ", ["dragen"]),
        ("qIaXcEl", ["qiaxcel"]),
        ("fragment", ["hemafrag"]),
        ("SOLIDE svulster", ["solide"]),
        ("variant review", ["vpm-tolkning", "dragen", "solide"]),
        ("   ", ["hemafrag", "igh-merge", "vpm-tolkning", "mpn-tolkning",
                 "molstat", "molkey", "dragen", "solide", "qiaxcel"]),
        ("<no app>", []),
    ],
)
def test_search_filters_names_and_descriptions_without_case_sensitivity(
    window, query, expected
):
    search = window.findChild(QLineEdit, "appSearch")
    assert search is not None

    search.setText(query)

    assert visible_ids(window) == expected


def test_typing_filters_and_clearing_restores_the_catalog(qtbot, window):
    search = window.findChild(QLineEdit, "appSearch")
    assert search is not None
    search.setFocus()
    qtbot.keyClicks(search, "molkey")
    assert visible_ids(window) == ["molkey"]
    assert window.results_label.text() == "1 av 9 apper"

    search.clear()

    assert len(visible_ids(window)) == 9
    assert window.results_label.text() == "9 apper"
    assert search.isClearButtonEnabled()
    assert search.accessibleName() == "Søk etter apper"


def test_no_results_is_explained_and_can_be_cleared(qtbot, window):
    search = window.findChild(QLineEdit, "appSearch")
    assert search is not None
    search.setText("<unknown>")

    assert window.empty_results.isVisibleTo(window)
    assert window.results_label.text() == "0 av 9 apper"
    assert window.application_grid.grid.count() == 0
    qtbot.mouseClick(window.clear_search_button, Qt.MouseButton.LeftButton)
    assert search.text() == ""
    assert len(visible_ids(window)) == 9
    assert not window.empty_results.isVisible()
    assert search.hasFocus()


def test_filter_reflows_results_without_gaps_and_keeps_running_state(window):
    search = window.findChild(QLineEdit, "appSearch")
    assert search is not None
    running_card = window.card("solide")
    window.set_module_running("solide")
    search.setText("solide")

    assert window.application_grid.grid.itemAtPosition(0, 0).widget() is running_card
    assert window.application_grid.grid.count() == 1
    assert not running_card.open_button.isEnabled()
    search.setText("molkey")
    window.set_module_ready("solide")
    search.clear()
    assert window.card("solide") is running_card
    assert running_card.open_button.isEnabled()


def test_search_survives_about_navigation_and_filtered_app_still_launches(qtbot, window):
    search = window.findChild(QLineEdit, "appSearch")
    assert search is not None
    search.setText("molkey")
    qtbot.mouseClick(window.about_button, Qt.MouseButton.LeftButton)
    assert window.pages.currentWidget() is window.about_page
    qtbot.mouseClick(window.navigation_buttons[0], Qt.MouseButton.LeftButton)

    assert window.pages.currentWidget() is window.applications_page
    assert search.text() == "molkey"
    with qtbot.waitSignal(window.module_selected) as signal:
        qtbot.mouseClick(window.card("molkey").open_button, Qt.MouseButton.LeftButton)
    assert signal.args == ["molkey"]
    assert window.isVisible()


def test_search_cannot_enable_unhealthy_or_installing_apps(window):
    search = window.findChild(QLineEdit, "appSearch")
    assert search is not None
    window.set_health(HealthReport(SuiteState.REPAIR_REQUIRED, "1.3.0", ("missing",)))
    search.setText("molkey")
    search.clear()
    assert not any(card.open_button.isEnabled() for card in window.application_cards)
    window.set_health(HealthReport(SuiteState.READY, "1.3.0", ()))
    window.set_install_running(True)
    search.setText("solide")
    assert not window.card("solide").open_button.isEnabled()
    window.set_install_running(False)


def test_ctrl_f_opens_catalog_and_focuses_search_from_about(qtbot, window):
    qtbot.mouseClick(window.about_button, Qt.MouseButton.LeftButton)
    window.activateWindow()
    qtbot.keyClick(window, Qt.Key.Key_F, Qt.KeyboardModifier.ControlModifier)

    qtbot.waitUntil(lambda: window.pages.currentWidget() is window.applications_page)
    assert window.findChild(QLineEdit, "appSearch").hasFocus()
    assert window.navigation_buttons[0].isChecked()


def test_catalog_and_count_follow_the_manifest(qtbot, manifest, ready_report):
    smaller = replace(manifest, modules=(manifest.module("molkey"),))
    window = MainWindow(smaller, ready_report)
    qtbot.addWidget(window)
    window.show()

    assert visible_ids(window) == ["molkey"]
    assert window.results_label.text() == "1 app"


def test_wide_catalog_uses_three_columns_and_search_reflows_them(qtbot, window):
    window.resize(1600, 1000)
    grid = window.application_grid
    qtbot.waitUntil(lambda: grid.columns == 3)
    assert grid.grid.itemAtPosition(0, 2).widget() is window.card("vpm-tolkning")

    window.app_search.setText("mol")

    assert grid.grid.itemAtPosition(0, 0).widget() is window.card("molstat")
    assert grid.grid.itemAtPosition(0, 1).widget() is window.card("molkey")
    assert grid.grid.count() == 2


def test_filter_from_bottom_returns_results_to_top(qtbot, window):
    window.resize(760, 520)
    scrollbar = window.app_scroll.verticalScrollBar()
    qtbot.waitUntil(lambda: scrollbar.maximum() > 0)
    scrollbar.setValue(scrollbar.maximum())

    window.app_search.setText("hemafrag")

    assert scrollbar.value() == 0
    qtbot.waitUntil(lambda: window.card("hemafrag").isVisibleTo(window))


def test_filter_does_not_reset_a_hidden_app_failure(window):
    failed = window.card("igh-merge")
    window.set_module_failed("igh-merge", "process_start_failed")
    window.app_search.setText("molstat")
    window.app_search.clear()

    assert window.card("igh-merge") is failed
    assert failed.open_button.text() == "Prøv igjen"


def test_no_match_and_filtered_results_fit_compact_window(qtbot, window):
    window.resize(760, 520)
    window.app_search.setText("unknown")
    qtbot.waitUntil(lambda: window.empty_results.isVisibleTo(window))
    assert window.app_scroll.horizontalScrollBar().maximum() == 0

    window.app_search.setText("mpn")
    qtbot.waitUntil(lambda: window.card("mpn-tolkning").isVisibleTo(window))
    assert window.app_scroll.horizontalScrollBar().maximum() == 0
