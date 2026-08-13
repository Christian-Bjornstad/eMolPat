"""Main eMolPat portal window."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
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

from emolpat.domain import HealthReport, SuiteManifest, SuiteState
from emolpat.ui.translations import INSTALL_STAGE_TEXT, NAVIGATION, STATE_TEXT
from emolpat.ui.widgets import ApplicationCard, StatusBanner, placeholder_page

STYLESHEET = """
QMainWindow, QWidget#shell { background: #f4f7f8; color: #17393b; }
QFrame#sidebar { background: #073f43; border: 0; }
QLabel#brand { color: white; font-size: 25px; font-weight: 700; }
QLabel#brandSubtitle, QLabel#suiteVersion { color: #b7d4d4; font-size: 12px; }
QPushButton#navigationButton { color: #d9e9e9; background: transparent; border: 0;
  border-radius: 6px; padding: 11px 14px; text-align: left; font-weight: 600; }
QPushButton#navigationButton:hover { background: #125258; color: white; }
QPushButton#navigationButton:checked { background: #e4f2f0; color: #073f43; }
QPushButton#navigationButton:focus { border: 2px solid #8fd0ca; }
QLabel#pageTitle { color: #12383b; font-size: 25px; font-weight: 700; }
QLabel#pageIntro { color: #567174; font-size: 14px; }
QFrame#statusBanner { background: #fff7e6; border: 1px solid #e6c66a;
  border-radius: 8px; }
QFrame#statusBanner[ready="true"] { background: #e8f5ef; border-color: #9acdb5; }
QLabel#statusSymbol { background: #a16909; color: white; border-radius: 14px;
  min-width: 28px; min-height: 28px; font-weight: 700; }
QFrame#statusBanner[ready="true"] QLabel#statusSymbol { background: #247a56; }
QLabel#statusTitle { color: #17393b; font-weight: 700; }
QLabel#statusDetail { color: #4b686a; }
QFrame#applicationCard { background: white; border: 1px solid #d6e0e1;
  border-radius: 9px; }
QFrame#applicationCard:hover { border-color: #87aaa9; }
QLabel#installProgress { background: #e8f2f3; color: #17393b;
  border: 1px solid #9ebfc0; border-radius: 6px; padding: 10px 14px;
  font-weight: 600; }
QLabel#moduleName { color: #12383b; font-size: 17px; font-weight: 700; }
QLabel#moduleVersion { color: #6b8183; font-size: 12px; }
QLabel#moduleDescription { color: #4b6264; font-size: 13px; }
QLabel#moduleStatus { color: #9a6309; font-size: 12px; font-weight: 600; }
QLabel#moduleStatus[ready="true"] { color: #247a56; }
QPushButton#primaryButton { background: #0c6669; color: white; border: 0;
  border-radius: 6px; padding: 0 18px; font-weight: 700; }
QPushButton#primaryButton:hover { background: #084f52; }
QPushButton#primaryButton:focus { border: 2px solid #8fd0ca; }
QPushButton#primaryButton:disabled { background: #b7c3c4; color: #f5f7f7; }
QScrollArea { border: 0; background: transparent; }
QWidget#cardsContainer, QScrollArea QWidget#qt_scrollarea_viewport {
  background: #f4f7f8;
}
"""


class MainWindow(QMainWindow):
    """Suite dashboard that emits one selected module and then closes."""

    module_selected = pyqtSignal(str)

    def __init__(self, manifest: SuiteManifest, health: HealthReport) -> None:
        super().__init__()
        self.manifest = manifest
        self.health = health
        self.application_cards: list[ApplicationCard] = []
        self.navigation_buttons: list[QPushButton] = []
        self.setWindowTitle(f"eMolPat {manifest.suite_version}")
        self.setAccessibleName("eMolPat programportal")
        self.setMinimumSize(980, 700)
        self.resize(1180, 780)
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
        sidebar.setFixedWidth(224)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(8)

        brand = QLabel("eMolPat")
        brand.setObjectName("brand")
        subtitle = QLabel("Molekylærpatologi")
        subtitle.setObjectName("brandSubtitle")
        version = QLabel(f"Suite {self.manifest.suite_version}")
        version.setObjectName("suiteVersion")
        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addWidget(version)
        layout.addSpacing(26)

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
        privacy = QLabel("Kun teknisk status\nIngen pasientdata lagres")
        privacy.setObjectName("brandSubtitle")
        layout.addWidget(privacy)
        return sidebar

    def _build_content(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(12)
        self.install_progress = QLabel()
        self.install_progress.setObjectName("installProgress")
        self.install_progress.setAccessibleName("Installasjonsstatus")
        self.install_progress.hide()
        layout.addWidget(self.install_progress)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_applications_page())
        self.pages.addWidget(
            placeholder_page(
                "Systemstatus",
                "Her vises kontroll av Python FELLES og alle komponentene i pakken.",
            )
        )
        self.pages.addWidget(
            placeholder_page(
                "Oppdater eMolPat",
                "Oppdatering installerer alltid portal og alle fire programmer samlet.",
                "Se etter oppdatering",
            )
        )
        self.pages.addWidget(
            placeholder_page(
                "Hjelp og støtte",
                "Ved feil kan teknisk støtte bruke eMolPat-loggen. Ingen kliniske data logges.",
            )
        )
        layout.addWidget(self.pages)
        return container

    def _build_applications_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        title = QLabel("Programmer")
        title.setObjectName("pageTitle")
        intro = QLabel("Velg analyseprogrammet du vil åpne.")
        intro.setObjectName("pageIntro")
        layout.addWidget(title)
        layout.addWidget(intro)

        ready = self.health.state is SuiteState.READY
        status_title, status_detail = STATE_TEXT[self.health.state.value]
        self.status_banner = StatusBanner(status_title, status_detail, ready)
        layout.addWidget(self.status_banner)

        cards = QWidget()
        cards.setObjectName("cardsContainer")
        grid = QGridLayout(cards)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
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

    def _open_module(self, module_id: str) -> None:
        self.module_selected.emit(module_id)
        self.close()
