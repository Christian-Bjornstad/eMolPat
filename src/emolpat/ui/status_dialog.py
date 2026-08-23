"""Compact, privacy-safe system status for the eMolPat portal."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from emolpat.domain import HealthReport, SuiteState
from emolpat.ui.translations import INSTALL_STAGE_TEXT, STATE_TEXT

INSTALL_ACTION_TEXT = {
    SuiteState.NOT_INSTALLED: "Installer programmer",
    SuiteState.UPDATE_AVAILABLE: "Oppdater eMolPat",
    SuiteState.REPAIR_REQUIRED: "Reparer installasjon",
}

MODULE_NAMES = {
    "hemafrag": "HemaFrag",
    "igh-merge": "IGH Merge",
    "vpm-tolkning": "HTS-tolkning",
    "mpn-tolkning": "MPN-tolkning",
}


def friendly_issue_copy(issues: tuple[str, ...], default: str) -> str:
    """Translate controlled issue identifiers without exposing raw details."""
    if not issues:
        return default
    copy: list[str] = []
    for issue in issues:
        _prefix, separator, module_id = issue.partition(":")
        if separator and module_id in MODULE_NAMES:
            copy.append(f"{MODULE_NAMES[module_id]} må repareres.")
        else:
            copy.append("En komponent kunne ikke verifiseres.")
    return " ".join(copy)


class SystemStatusDialog(QDialog):
    """Show suite health and the one permitted install or repair action."""

    action_requested = pyqtSignal()

    def __init__(
        self,
        health: HealthReport,
        release_available: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.release_available = release_available
        self.setWindowTitle("Systemstatus")
        self.setModal(False)
        self.setMinimumWidth(420)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("dialogSummary")
        self.version_label = QLabel()
        self.version_label.setObjectName("dialogVersion")
        self.details_label = QLabel()
        self.details_label.setObjectName("dialogDetails")
        self.details_label.setWordWrap(True)
        self.progress_label = QLabel()
        self.progress_label.setObjectName("installProgress")
        self.progress_label.setWordWrap(True)
        self.progress_label.hide()
        self.action_button = QPushButton()
        self.action_button.setObjectName("primaryButton")
        self.action_button.setMinimumHeight(44)
        self.action_button.clicked.connect(self.action_requested.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.version_label)
        layout.addWidget(self.details_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.action_button)
        self.set_health(health)

    def set_health(self, health: HealthReport) -> None:
        title, detail = STATE_TEXT[health.state.value]
        self.summary_label.setText(title)
        installed = health.suite_version or "ikke installert"
        self.version_label.setText(f"Installert versjon: {installed}")
        self.details_label.setText(friendly_issue_copy(health.issues, detail))
        action = INSTALL_ACTION_TEXT.get(health.state)
        self.action_button.setText(action or "")
        self.action_button.setVisible(bool(action and self.release_available))

    def set_install_running(self, running: bool) -> None:
        self.action_button.setEnabled(not running)

    def show_install_stage(self, stage: str) -> None:
        self.progress_label.setText(INSTALL_STAGE_TEXT[stage])
        self.progress_label.show()
