"""Focused reusable widgets for the eMolPat portal."""

from __future__ import annotations

from importlib.resources import files

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from emolpat.domain import ModuleSpec

ICON_FILES = {
    "hemafrag": "hemafrag.png",
    "igh-merge": "igh-merge.png",
    "vpm-tolkning": "vpm-tolkning.png",
    "mpn-tolkning": "mpn-tolkning.png",
}


def module_icon(module_id: str) -> QIcon:
    """Load the canonical icon bundled from an approved component package."""
    path = files("emolpat.ui.resources").joinpath(ICON_FILES[module_id])
    return QIcon(str(path))


class StatusBanner(QFrame):
    """Compact portal health status with text and iconography."""

    def __init__(self, title: str, detail: str, ready: bool) -> None:
        super().__init__()
        self.setObjectName("statusBanner")
        self.setProperty("ready", ready)
        self.setMaximumWidth(220)

        symbol = QLabel("✓" if ready else "!")
        symbol.setObjectName("statusSymbol")
        symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol.setAccessibleName("Godkjent" if ready else "Krever handling")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statusTitle")
        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("statusDetail")
        self.detail_label.setWordWrap(True)
        self.detail_label.hide()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 12, 8)
        layout.setSpacing(8)
        layout.addWidget(symbol)
        layout.addWidget(self.title_label)

    def text(self) -> str:
        return self.title_label.text()


class ApplicationCard(QFrame):
    """One analysis application and its single primary launch action."""

    def __init__(self, module: ModuleSpec, enabled: bool) -> None:
        super().__init__()
        self.module_id = module.id
        self.module_icon = module_icon(module.id)
        self.setObjectName("applicationCard")
        self.setAccessibleName(f"{module.name}, versjon {module.version}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(280, 218)

        icon_label = QLabel()
        icon_label.setObjectName("moduleIcon")
        icon_label.setFixedSize(64, 64)
        icon_label.setPixmap(
            self.module_icon.pixmap(
                QSize(58, 58),
                QIcon.Mode.Normal,
                QIcon.State.Off,
            )
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setAccessibleName(f"Ikon for {module.name}")

        name = QLabel(module.name)
        name.setObjectName("moduleName")
        version = QLabel(f"Versjon {module.version}")
        version.setObjectName("moduleVersion")
        heading = QVBoxLayout()
        heading.setSpacing(2)
        heading.addWidget(name)
        heading.addWidget(version)

        top = QHBoxLayout()
        top.setSpacing(14)
        top.addWidget(icon_label)
        top.addLayout(heading, 1)

        description = QLabel(module.description_nb)
        description.setObjectName("moduleDescription")
        description.setWordWrap(True)

        status = QLabel("●  Kontrollert" if enabled else "●  Ikke klar")
        status.setObjectName("moduleStatus")
        status.setProperty("ready", enabled)

        self.open_button = QPushButton("Åpne program")
        self.open_button.setObjectName("primaryButton")
        self.open_button.setMinimumHeight(44)
        self.open_button.setEnabled(enabled)
        self.open_button.setAccessibleName(f"Åpne {module.name}")
        self.open_button.setToolTip(
            f"Åpne {module.name}" if enabled else "eMolPat må repareres først"
        )

        footer = QHBoxLayout()
        footer.addWidget(status)
        footer.addStretch(1)
        footer.addWidget(self.open_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        layout.addLayout(top)
        layout.addWidget(description)
        layout.addStretch(1)
        layout.addLayout(footer)


def placeholder_page(title: str, body: str, action: str | None = None) -> QFrame:
    """Create a meaningful non-empty secondary portal page."""
    page = QFrame()
    page.setObjectName("contentPage")
    heading = QLabel(title)
    heading.setObjectName("pageTitle")
    detail = QLabel(body)
    detail.setObjectName("pageIntro")
    detail.setWordWrap(True)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(12)
    layout.addWidget(heading)
    layout.addWidget(detail)
    if action:
        button = QPushButton(action)
        button.setMinimumHeight(44)
        button.setEnabled(False)
        button.setAccessibleName(action)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
    layout.addStretch(1)
    return page
