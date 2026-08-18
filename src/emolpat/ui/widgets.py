"""Focused reusable widgets for the eMolPat portal with English text and modern design."""

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
        self.setMaximumWidth(240)

        symbol = QLabel("✓" if ready else "!")
        symbol.setObjectName("statusSymbol")
        symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol.setAccessibleName("Approved" if ready else "Action required")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statusTitle")
        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("statusDetail")
        self.detail_label.setWordWrap(True)
        self.detail_label.hide()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 14, 10)
        layout.setSpacing(10)
        layout.addWidget(symbol)
        layout.addWidget(self.title_label)

    def text(self) -> str:
        return self.title_label.text()

    def set_status(self, title: str, detail: str, ready: bool) -> None:
        self.title_label.setText(title)
        self.detail_label.setText(detail)
        self.setProperty("ready", ready)
        self.style().unpolish(self)
        self.style().polish(self)


class ApplicationCard(QFrame):
    """One analysis application and its single primary launch action."""

    def __init__(self, module: ModuleSpec, enabled: bool) -> None:
        super().__init__()
        self.module_id = module.id
        self.module_icon = module_icon(module.id)
        self.setObjectName("applicationCard")
        self.setAccessibleName(f"{module.name}, version {module.version}")
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
        icon_label.setAccessibleName(f"Icon for {module.name}")

        name = QLabel(module.name)
        name.setObjectName("moduleName")
        version = QLabel(f"Version {module.version}")
        version.setObjectName("moduleVersion")
        heading = QVBoxLayout()
        heading.setSpacing(2)
        heading.addWidget(name)
        heading.addWidget(version)

        top = QHBoxLayout()
        top.setSpacing(16)
        top.addWidget(icon_label)
        top.addLayout(heading, 1)

        description = QLabel(module.description_en)
        description.setObjectName("moduleDescription")
        description.setWordWrap(True)

        self.status_label = QLabel()
        self.status_label.setObjectName("moduleStatus")

        self.open_button = QPushButton("Open application")
        self.open_button.setObjectName("primaryButton")
        self.open_button.setMinimumHeight(44)
        self.open_button.setAccessibleName(f"Open {module.name}")
        self.module_name = module.name
        self.set_enabled(enabled)

        footer = QHBoxLayout()
        footer.addWidget(self.status_label)
        footer.addStretch(1)
        footer.addWidget(self.open_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        layout.addLayout(top)
        layout.addWidget(description)
        layout.addStretch(1)
        layout.addLayout(footer)

    def set_enabled(self, enabled: bool) -> None:
        self.status_label.setText("●  Verified" if enabled else "●  Not ready")
        self.status_label.setProperty("ready", enabled)
        self.open_button.setEnabled(enabled)
        self.open_button.setToolTip(
            f"Open {self.module_name}" if enabled else "eMolPat must be repaired first"
        )


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
    layout.setSpacing(16)
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