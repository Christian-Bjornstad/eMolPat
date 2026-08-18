"""Main eMolPat portal window with English UI and modern design."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from emolpat.domain import HealthReport, InstallResult, SuiteManifest, SuiteState
from emolpat.ui.translations import INSTALL_COMPLETE_TEXT, INSTALL_STAGE_TEXT, NAVIGATION, STATE_TEXT
from emolpat.ui.widgets import ApplicationCard, StatusBanner, placeholder_page

STYLESHEET = """/* eMolPat Portal - Modern English Frontend Design */
 
/* Color Palette:
   Primary: #1A1F2E (deep midnight blue - trust, professionalism)
   Secondary: #2E86AB (calm teal accent - clinical, clean)
   Accent: #F18F01 (warm amber - highlights, CTA)
   Success: #4CAF50 (green - positive results)
   Warning: #FF9800 (orange - attention needed)
   Neutral: #F5F6FA (light surface - readability)
*/

QMainWindow, QWidget#shell { 
    background: #1A1F2E; 
    color: #F5F6FA; 
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
QFrame#applicationCard:focus-within { 
    border-color: #2E86AB; 
    outline: 2px solid #2E86AB; 
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
    color: #6B8183; 
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

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
    QPushButton#navigationButton:hover,
    QFrame#applicationCard:hover,
    QPushButton#primaryButton:hover {
        transition: none !important;
    }
}
"""



class MainWindow(QMainWindow):
    """Suite dashboard that emits one selected module and then closes."""

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
        self.application_cards: list[ApplicationCard] = []
        self.navigation_buttons: list[QPushButton] = []
        self.setWindowTitle(f"eMolPat {manifest.suite_version}")
        self.setAccessibleName("eMolPat program portal")
        self.setMinimumSize(980, 700)
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def card(self, module_id: str) -> ApplicationCard:
        for card in self.application_cards:
            if card.module_id == module_id:
                return card
        raise KeyError(f"unknown module card: {module_id}")

    def show_install_stage(self, stage: str) -> None:
        """Expose plain-language progress for a suite-level install operation."""
        self.install_progress.setText(INSTALL_STAGE_TEXT[stage])
        self.install_progress.show()

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
        subtitle = QLabel("Molecular Pathology Portal")
        subtitle.setObjectName("brandSubtitle")
        self.version_label = QLabel(f"Version {self.manifest.suite_version}")
        self.version_label.setObjectName("versionLabel")
        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addWidget(self.version_label)
        layout.addSpacing(28)

        group = QButtonGroup(self)
        group.setExclusive(True)
        for index, (label, accessible_description) in enumerate(NAVIGATION):
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

        self.about_button = QPushButton("About eMolPat")
        self.about_button.setObjectName("navigationButton")
        self.about_button.setCheckable(True)
        self.about_button.setMinimumHeight(44)
        self.about_button.setAccessibleName("About eMolPat")
        self.about_button.setAccessibleDescription(
            "About eMolPat, the analysis tools, and the developer"
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
        layout.setSpacing(16
        )
        self.install_progress = QLabel()
        self.install_progress.setObjectName("installProgress")
        self.install_progress.setAccessibleName("Installation status")
        self.install_progress.hide()
        layout.addWidget(self.install_progress)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_applications_page())
        self.system_status_page = self._build_system_status_page()
        self.pages.addWidget(self.system_status_page)
        self.pages.addWidget(
            placeholder_page(
                "Update eMolPat",
                "The update always installs the portal and all four applications together.",
                "Check for update",
            )
        )
        self.pages.addWidget(
            placeholder_page(
                "Help & Support",
                "Technical support can use the eMolPat log. No clinical data is logged.",
            )
        )
        self.about_page = self._build_about_page()
        self.pages.addWidget(self.about_page)
        layout.addWidget(self.pages)
        return container

    def _build_system_status_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        title = QLabel("System Status")
        title.setObjectName("pageTitle")
        self.system_summary = QLabel()
        self.system_summary.setObjectName("pageIntro")
        self.system_summary.setWordWrap(True)
        self.system_issues = QLabel()
        self.system_issues.setObjectName("systemIssues")
        self.system_issues.setWordWrap(True)
        self.install_button = QPushButton()
        self.install_button.setObjectName("primaryButton")
        self.install_button.setMinimumHeight(44)
        self.install_button.setAccessibleName("Install or repair eMolPat")
        self.install_button.clicked.connect(self._request_install)
        layout.addWidget(title)
        layout.addWidget(self.system_summary)
        layout.addWidget(self.system_issues)
        layout.addWidget(
            self.install_button,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        layout.addStretch(1)
        self._update_system_status()
        return page

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16

        )
        title = QLabel("About eMolPat")
        title.setObjectName("pageTitle")
        description = QLabel(
            "eMolPat is a unified portal for molecular pathology applications. "
            "The portal provides simple access to HemaFrag Diagnostics, IGH Merge, "
            "VPM / HTS Tolkning and MPN Tolkning, while each program continues "
            "to run as an independent tool."
        )
        description.setObjectName("pageIntro")
        description.setWordWrap(True)
        creator = QLabel("Developed by Christian Bjørnstad")
        creator.setObjectName("aboutCreator")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(creator)
        layout.addStretch(1)
        return page

    def _build_applications_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20
        )
        title = QLabel("Applications")
        title.setObjectName("pageTitle")
        intro = QLabel("Select the analysis application you want to open.")
        intro.setObjectName("pageIntro")

        ready = self.health.state is SuiteState.READY
        status_title, status_detail = STATE_TEXT[self.health.state.value]
        self.status_banner = StatusBanner(status_title, status_detail, ready)

        heading_copy = QVBoxLayout()
        heading_copy.setSpacing(8)
        heading_copy.addWidget(title)
        heading_copy.addWidget(intro)

        heading = QHBoxLayout()
        heading.setSpacing(24)
        heading.addLayout(heading_copy, 1)
        heading.addWidget(
            self.status_banner,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        layout.addLayout(heading)

        cards = QWidget()
        cards.setObjectName("cardsContainer")
        grid = QGridLayout(cards)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)

        for index, module in enumerate(self.manifest.modules):
            card = ApplicationCard(module, enabled=ready)
            card.open_button.clicked.connect(
                lambda _checked, module_id=module.id: self._open_module(module_id)
            )
            grid.addWidget(card, index // 2, index % 2)
            self.application_cards.append(card)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(cards)
        layout.addWidget(scroll, 1)
        return page

    def _request_install(self) -> None:
        self.set_install_running(True)
        self.install_requested.emit()

    def _update_system_status(self) -> None:
        title, detail = STATE_TEXT[self.health.state.value]
        self.system_summary.setText(f"{title}. {detail}")
        self.system_issues.setText("\n".join(self.health.issues))
        action_text = {
            SuiteState.NOT_INSTALLED: "Install applications",
            SuiteState.REPAIR_REQUIRED: "Repair installation",
            SuiteState.UPDATE_AVAILABLE: "Update eMolPat",
        }.get(self.health.state)
        self.install_button.setText(action_text or "")
        self.install_button.setVisible(bool(action_text and self.release_available))

    def set_install_running(self, running: bool) -> None:
        self._install_running = running
        self.install_button.setEnabled(not running)
        if running:
            self.pages.setCurrentWidget(self.system_status_page)

    def set_health(self, health: HealthReport) -> None:
        self.health = health
        ready = health.state is SuiteState.READY
        title, detail = STATE_TEXT[health.state.value]
        self.status_banner.set_status(title, detail, ready)
        for card in self.application_cards:
            card.set_enabled(ready)
        self._update_system_status()

    def finish_install(self, result: InstallResult, health: HealthReport) -> None:
        self.set_install_running(False)
        self.set_health(health)
        if result.ok:
            self.install_progress.setText(INSTALL_COMPLETE_TEXT)
            self.install_progress.show()
            self.close()
            return
        self.install_progress.setText(
            f"Installation stopped at: {INSTALL_STAGE_TEXT[result.stage]}"
        )
        self.install_progress.show()

    def _open_module(self, module_id: str) -> None:
            self.module_selected.emit(module_id)
            # Do NOT close the portal – keep it running so the user can
            # close the app or press a portal button to return later.

    def closeEvent(self, event: QCloseEvent) -> None:
        """Keep the portal alive until the atomic installation has finished."""
        if self._install_running:
            event.ignore()
            return
        super().closeEvent(event)