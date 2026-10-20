"""Hovedvindu for den norske, kliniske eMolPat-portalen."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
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
    ModuleUnit,
    SuiteManifest,
    SuiteState,
)
from emolpat.ui.status_dialog import SystemStatusDialog
from emolpat.ui.translations import (
    INSTALL_COMPLETE_TEXT,
    INSTALL_STAGE_TEXT,
    UNIT_NAVIGATION,
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
QWidget#cardsContainer, QScrollArea QWidget#qt_scrollarea_viewport { 
    background: #F5F6FA; 
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
        for index, (_unit, label, accessible_description) in enumerate(
            UNIT_NAVIGATION
        ):
            button = QPushButton(label)
            button.setObjectName("navigationButton")
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.setAccessibleName(label)
            button.setAccessibleDescription(accessible_description)
            button.clicked.connect(lambda _checked, page=index: self.pages.setCurrentIndex(page))
            group.addButton(button)
            layout.addWidget(button)
            self.navigation_buttons.append(button)
        self.navigation_buttons[0].setChecked(True)
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
        self.unit_pages: dict[ModuleUnit, QWidget] = {}
        for unit, label, _description in UNIT_NAVIGATION:
            page = self._build_applications_page(unit, label)
            self.unit_pages[unit] = page
            self.pages.addWidget(page)
        self.solide_page = self.unit_pages[ModuleUnit.SOLIDE]
        self.stat_page = self.unit_pages[ModuleUnit.STAT]
        self.molkey_page = self.unit_pages[ModuleUnit.MOLKEY]
        self.status_banner = self.status_controls[0]
        module_order = {
            module.id: index for index, module in enumerate(self.manifest.modules)
        }
        self.application_cards.sort(key=lambda card: module_order[card.module_id])
        self.about_page = self._build_about_page()
        self.pages.addWidget(self.about_page)

        layout.addWidget(self.pages)
        return container

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16

        )
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

    def _build_applications_page(
        self,
        unit: ModuleUnit,
        title_text: str,
    ) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        intro = QLabel("Velg analyseprogrammet du ønsker å åpne.")
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

        unit_modules = tuple(
            module for module in self.manifest.modules if module.unit is unit
        )
        unit_cards = []
        for module in unit_modules:
            card = ApplicationCard(module, enabled=ready)
            card.open_button.clicked.connect(
                lambda _checked, module_id=module.id: self._open_module(module_id)
            )
            unit_cards.append(card)
            self.application_cards.append(card)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(ApplicationGrid(unit_cards))
        layout.addWidget(scroll, 1)
        return page

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
