"""Hovedvindu for den norske, kliniske eMolPat-portalen."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from emolpat.domain import (
    HealthReport,
    InstallResult,
    SuiteManifest,
    SuiteState,
)
from emolpat.ui.status_dialog import SystemStatusDialog
from emolpat.ui.translations import (
    INSTALL_COMPLETE_TEXT,
    INSTALL_STAGE_TEXT,
)
from emolpat.ui.widgets import ApplicationCard, ApplicationGrid, StatusControl

STYLESHEET = """/* eMolPat klinisk lys portal */
 
/* Color Palette:
   Primary: #1A1F2E (deep midnight blue - trust, professionalism)
   Secondary: #2E86AB (calm teal accent - clinical, clean)
   Accent: #F18F01 (warm amber - highlights, CTA)
   Success: #4CAF50 (green - positive results)
   Warning: #FF9800 (orange - attention needed)
   Neutral: #F5F6FA (light surface - readability)
*/

QMainWindow, QDialog, QWidget#shell {
    background: #EDF4F6;
    color: #12383B;
}

/* Sidebar */
QFrame#sidebar { 
    background: #073F43; 
    border: 0; 
}

/* Brand */
QLabel#brand { 
    color: white; 
    font-size: 28px; 
    font-weight: 700; 
}

/* Subtle accents */
QLabel#brandSubtitle, QLabel#versionLabel { 
    color: #B7D4D4; 
    font-size: 12px; 
}

/* Navigation Buttons */
QPushButton#navigationButton { 
    color: #D9E9E9; 
    background: transparent; 
    border: 0; 
    border-radius: 6px; 
    padding: 11px 14px; 
    text-align: left; 
    font-weight: 600; 
}
QPushButton#navigationButton:hover { 
    background: #125258; 
    color: white; 
}
QPushButton#navigationButton:checked { 
    background: #E4F2F0; 
    color: #073F43; 
}
QPushButton#navigationButton:focus { 
    border: 2px solid #8FD0CA; 
    background: #E4F2F0; 
    color: #073F43;
}

/* Page Titles */
QLabel#pageTitle { 
    color: #12383B; 
    font-size: 25px; 
    font-weight: 700; 
}

/* Page Intro */
QLabel#pageIntro { 
    color: #567174; 
    font-size: 14px; 
}

QLineEdit#appSearch {
    background: white;
    color: #12383B;
    border: 1px solid #B7C9CC;
    border-radius: 7px;
    padding: 10px 14px;
    font-size: 14px;
}
QLineEdit#appSearch:focus {
    border: 2px solid #1D7A78;
    padding: 9px 13px;
}
QLabel#searchResults {
    color: #567174;
    font-size: 13px;
}

/* About Creator */
QLabel#aboutCreator { 
    color: #12383B; 
    font-size: 14px; 
    font-weight: 700; 
}

/* Status Banner */
QPushButton#statusControl {
    background: #F4F7F8;
    color: #17393B;
    border: 1px solid #B7C9CC;
    border-radius: 7px;
    padding: 9px 14px;
    font-weight: 700;
}
QPushButton#statusControl:hover,
QPushButton#statusControl:focus {
    border: 2px solid #1D7A78;
    background: #FFFFFF;
}
QPushButton#statusControl[state="ready"] {
    background: #E8F5EF;
    border-color: #75B596;
}
QPushButton#statusControl[state="update_available"] {
    background: #FFF7E6;
    border-color: #D6A638;
}
QPushButton#statusControl[state="repair_required"] {
    background: #FCEDEE;
    border-color: #C96A70;
}
QPushButton#statusControl[state="not_installed"],
QPushButton#statusControl[state="unavailable"] {
    background: #F3F0F0;
    border-color: #9B7779;
}
QFrame#statusBanner { 
    background: #FFF7E6; 
    border: 1px solid #E6C66A; 
    border-radius: 7px; 
    min-height: 32px; 
}
QFrame#statusBanner[ready="true"] { 
    background: #E8F5EF; 
    border-color: #9ACDB5; 
}
QLabel#statusSymbol { 
    background: #F18F01; 
    color: white; 
    border-radius: 11px; 
    min-width: 22px; max-width: 22px; 
    min-height: 22px; max-height: 22px; 
    font-weight: 700; 
}
QFrame#statusBanner[ready="true"] QLabel#statusSymbol { 
    background: #247A56; 
}

/* Status text */
QLabel#statusTitle { 
    color: #17393B; 
    font-weight: 700; 
}
QLabel#statusDetail { 
    color: #4B686A; 
}

/* Application Cards */
QFrame#applicationCard { 
    background: white; 
    border: 1px solid #D6E0E1; 
    border-radius: 12px; 
    margin: 8px 0; 
}
QFrame#applicationCard:hover { 
    border-color: #87AAA9; 
    background: #F8FCFC; 
}

/* Install Progress */
QLabel#installProgress { 
    background: #E8F2F3; 
    color: #17393B; 
    border: 1px solid #9EbfC0; 
    border-radius: 6px; 
    padding: 10px 14px; 
    font-weight: 600; 
}

/* Module Name/Version */
QLabel#moduleName { 
    color: #12383B; 
    font-size: 17px; 
    font-weight: 700; 
}
QLabel#moduleVersion { 
    color: #526D70;
    font-size: 12px; 
}
QLabel#moduleDescription { 
    color: #4B6264; 
    font-size: 13px; 
}

/* Module Status */
QLabel#moduleStatus { 
    color: #9A6309; 
    font-size: 12px; 
    font-weight: 600; 
}
QLabel#moduleStatus[ready="true"] { 
    color: #247A56; 
}

/* Primary Buttons */
QPushButton#primaryButton { 
    background: #0C6669; 
    color: white; 
    border: 0; 
    border-radius: 6px; 
    padding: 0 18px; 
    font-weight: 700; 
}
QPushButton#primaryButton:hover { 
    background: #084F52; 
}
QPushButton#primaryButton:focus { 
    border: 2px solid #8FD0CA; 
}
QPushButton#primaryButton:disabled { 
    background: #B7C3C4; 
    color: #F5F7F7; 
}

/* Scroll Area */
QScrollArea { 
    border: 0; 
    background: transparent; 
}
QWidget#cardsContainer, QWidget#searchResults, QWidget#emptyResults,
QScrollArea QWidget#qt_scrollarea_viewport {
    background: #EDF4F6;
}

"""



class MainWindow(QMainWindow):
    """Suite dashboard that remains available while analysis apps run."""

    module_selected = pyqtSignal(str)
    install_requested = pyqtSignal()

    def __init__(
        self,
        manifest: SuiteManifest,
        health: HealthReport,
        release_available: bool = False,
    ) -> None:
        super().__init__()
        self.manifest = manifest
        self.health = health
        self.release_available = release_available
        self._install_running = False
        self._running_modules: set[str] = set()
        self.application_cards: list[ApplicationCard] = []
        self.navigation_buttons: list[QPushButton] = []
        self.status_controls: list[StatusControl] = []
        self.setWindowTitle(f"eMolPat {manifest.suite_version}")
        self.setAccessibleName("eMolPat programportal")
        self.setMinimumSize(760, 520)
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self._focus_search)

    def card(self, module_id: str) -> ApplicationCard:
        for card in self.application_cards:
            if card.module_id == module_id:
                return card
        raise KeyError(f"unknown module card: {module_id}")

    def set_module_running(self, module_id: str) -> None:
        self._running_modules.add(module_id)
        self.card(module_id).show_running()

    def set_module_ready(self, module_id: str) -> None:
        self._running_modules.discard(module_id)
        self._refresh_card(self.card(module_id))

    def set_module_failed(self, module_id: str, _error_code: str) -> None:
        self._running_modules.discard(module_id)
        card = self.card(module_id)
        if self.health.state is SuiteState.READY and not self._install_running:
            card.show_failure()
        else:
            self._refresh_card(card)

    def _refresh_card(self, card: ApplicationCard) -> None:
        if card.module_id in self._running_modules:
            card.show_running()
        elif self._install_running:
            card.show_installing()
        else:
            card.set_enabled(self.health.state is SuiteState.READY)

    def show_running_apps_warning(self, module_ids: frozenset[str]) -> None:
        names = [
            module.name for module in self.manifest.modules if module.id in module_ids
        ]
        message = (
            "Lukk kjørende analyseapper før eMolPat oppdateres eller repareres.\n"
            f"Kjører: {', '.join(names)}"
        )
        QMessageBox.warning(self, "Analyseapper kjører", message)

    def show_install_stage(self, stage: str) -> None:
        """Expose plain-language progress for a suite-level install operation."""
        self.status_dialog.show_install_stage(stage)
        self.status_dialog.show()

    def _build_ui(self) -> None:
        shell = QWidget()
        shell.setObjectName("shell")
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_sidebar())
        layout.addWidget(self._build_content(), 1)
        self.setCentralWidget(shell)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(12)

        brand = QLabel("eMolPat")
        brand.setObjectName("brand")
        subtitle = QLabel("Molekylærpatologisk programportal")
        subtitle.setObjectName("brandSubtitle")
        subtitle.setWordWrap(True)
        self.version_label = QLabel(f"Versjon {self.manifest.suite_version}")
        self.version_label.setObjectName("versionLabel")
        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addWidget(self.version_label)
        layout.addSpacing(28)

        group = QButtonGroup(self)
        group.setExclusive(True)
        apps_button = QPushButton("Apper")
        apps_button.setObjectName("navigationButton")
        apps_button.setCheckable(True)
        apps_button.setChecked(True)
        apps_button.setMinimumHeight(44)
        apps_button.setAccessibleName("Apper")
        apps_button.setAccessibleDescription("Finn og åpne alle tilgjengelige apper")
        apps_button.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.applications_page)
        )
        group.addButton(apps_button)
        layout.addWidget(apps_button)
        self.navigation_buttons.append(apps_button)
        layout.addStretch(1)

        self.about_button = QPushButton("Om eMolPat")
        self.about_button.setObjectName("navigationButton")
        self.about_button.setCheckable(True)
        self.about_button.setMinimumHeight(44)
        self.about_button.setAccessibleName("Om eMolPat")
        self.about_button.setAccessibleDescription(
            "Om eMolPat, analyseverktøyene og utvikleren"
        )
        self.about_button.clicked.connect(
            lambda _checked: self.pages.setCurrentWidget(self.about_page)
        )
        group.addButton(self.about_button)
        layout.addWidget(self.about_button)
        self.navigation_buttons.append(self.about_button)
        return sidebar

    def _build_content(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(16)
        self.status_dialog = SystemStatusDialog(
            self.health,
            self.release_available,
            self,
        )
        self.status_dialog.action_requested.connect(self._request_install)
        self.install_button = self.status_dialog.action_button
        self.install_progress = self.status_dialog.progress_label
        self.install_progress.setAccessibleName("Installasjonsstatus")

        self.pages = QStackedWidget()
        self.applications_page = self._build_applications_page()
        self.pages.addWidget(self.applications_page)
        self.status_banner = self.status_controls[0]
        self.about_page = self._build_about_page()
        self.pages.addWidget(self.about_page)

        layout.addWidget(self.pages)
        return container

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        title = QLabel("Om eMolPat")
        title.setObjectName("pageTitle")
        names = [module.name for module in self.manifest.modules]
        applications = ", ".join(names[:-1]) + " og " + names[-1]
        description = QLabel(
            "eMolPat er en samlet portal for molekylærpatologiske analyseverktøy. "
            f"Portalen gir enkel tilgang til {applications}, samtidig "
            "som hvert program fortsetter å kjøre som et selvstendig verktøy."
        )
        description.setObjectName("pageIntro")
        description.setWordWrap(True)
        creator = QLabel("Utviklet av Christian Bjørnstad")
        creator.setObjectName("aboutCreator")
        guidance = QLabel(
            "Diagnostikk viser teknisk systemstatus uten å vise analysedata. "
            "Ved behov kan Teknisk hjelp bruke eMolPat-loggen til feilsøking."
        )
        guidance.setObjectName("pageIntro")
        guidance.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(creator)
        layout.addWidget(guidance)
        layout.addStretch(1)
        return page

    def _build_applications_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        title = QLabel("Apper")
        title.setObjectName("pageTitle")
        intro = QLabel("Alle verktøyene dine på ett sted. Finn appen du vil åpne.")
        intro.setObjectName("pageIntro")
        intro.setWordWrap(True)

        ready = self.health.state is SuiteState.READY
        heading_copy = QVBoxLayout()
        heading_copy.setSpacing(8)
        heading_copy.addWidget(title)
        heading_copy.addWidget(intro)

        heading = QHBoxLayout()
        heading.setSpacing(24)
        heading.addLayout(heading_copy, 1)
        status = StatusControl(self.health)
        status.clicked.connect(self.status_dialog.show)
        self.status_controls.append(status)
        heading.addWidget(
            status,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        layout.addLayout(heading)

        self.app_search = QLineEdit()
        self.app_search.setObjectName("appSearch")
        self.app_search.setPlaceholderText("Søk etter appnavn eller beskrivelse …")
        self.app_search.setAccessibleName("Søk etter apper")
        self.app_search.setAccessibleDescription(
            "Filtrer apper etter navn eller beskrivelse. Ctrl+F åpner søket."
        )
        self.app_search.setClearButtonEnabled(True)
        self.app_search.setMinimumHeight(44)
        layout.addWidget(self.app_search)

        self.results_label = QLabel()
        self.results_label.setObjectName("searchResults")
        layout.addWidget(self.results_label)

        for module in self.manifest.modules:
            card = ApplicationCard(module, enabled=ready)
            card.open_button.clicked.connect(
                lambda _checked, module_id=module.id: self._open_module(module_id)
            )
            self.application_cards.append(card)

        self.application_grid = ApplicationGrid(self.application_cards)
        self.empty_results = QWidget()
        self.empty_results.setObjectName("emptyResults")
        empty_layout = QVBoxLayout(self.empty_results)
        empty_layout.setContentsMargins(24, 32, 24, 32)
        empty_title = QLabel("Ingen apper funnet")
        empty_title.setObjectName("moduleName")
        empty_title.setWordWrap(True)
        empty_detail = QLabel("Prøv et annet søkeord, eller tøm søket for å se alle appene.")
        empty_detail.setObjectName("pageIntro")
        empty_detail.setWordWrap(True)
        self.clear_search_button = QPushButton("Vis alle apper")
        self.clear_search_button.setObjectName("primaryButton")
        self.clear_search_button.setMinimumHeight(44)
        self.clear_search_button.setAccessibleName("Tøm søket og vis alle apper")
        self.clear_search_button.clicked.connect(self._clear_search)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_detail)
        empty_layout.addWidget(self.clear_search_button, alignment=Qt.AlignmentFlag.AlignLeft)
        empty_layout.addStretch(1)

        self.search_results = QStackedWidget()
        self.search_results.setObjectName("searchResults")
        self.search_results.addWidget(self.application_grid)
        self.search_results.addWidget(self.empty_results)
        self.app_scroll = QScrollArea()
        self.app_scroll.setWidgetResizable(True)
        self.app_scroll.setWidget(self.search_results)
        layout.addWidget(self.app_scroll, 1)
        self.app_search.textChanged.connect(self._filter_applications)
        self._filter_applications("")
        return page

    def _filter_applications(self, query: str) -> None:
        count = self.application_grid.filter_cards(query)
        total = len(self.application_cards)
        self.results_label.setText(
            f"{count} av {total} apper" if query.strip()
            else f"{total} {'app' if total == 1 else 'apper'}"
        )
        self.search_results.setCurrentWidget(
            self.application_grid if count else self.empty_results
        )
        self.app_scroll.verticalScrollBar().setValue(0)

    def _clear_search(self) -> None:
        self.app_search.clear()
        self.app_search.setFocus()

    def _focus_search(self) -> None:
        self.pages.setCurrentWidget(self.applications_page)
        self.navigation_buttons[0].setChecked(True)
        self.app_search.setFocus()
        self.app_search.selectAll()

    def _request_install(self) -> None:
        if not self._install_running:
            self.install_requested.emit()

    def set_install_running(self, running: bool) -> None:
        self._install_running = running
        self.status_dialog.set_install_running(running)
        for card in self.application_cards:
            self._refresh_card(card)
        if running:
            self.status_dialog.show()

    def set_health(self, health: HealthReport) -> None:
        self.health = health
        for status in self.status_controls:
            status.set_health(health)
        self.status_dialog.set_health(health)
        for card in self.application_cards:
            self._refresh_card(card)

    def finish_install(self, result: InstallResult, health: HealthReport) -> None:
        self.set_install_running(False)
        self.set_health(health)
        if result.ok:
            self.install_progress.setText(INSTALL_COMPLETE_TEXT)
            self.install_progress.show()
            self.close()
            return
        self.install_progress.setText(
            f"Installasjonen stoppet ved: {INSTALL_STAGE_TEXT[result.stage]}"
        )
        self.install_progress.show()

    def _open_module(self, module_id: str) -> None:
        self.module_selected.emit(module_id)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Keep the portal alive until the atomic installation has finished."""
        if self._install_running:
            event.ignore()
            return
        self.status_dialog.close()
        super().closeEvent(event)
