from __future__ import annotations

from PyQt6.QtCore import QTimer

from emolpat.domain import HealthReport, SuiteManifest
from emolpat.ui.app import PortalOutcome, run_application_loop, run_portal
from emolpat.ui.main_window import MainWindow


def test_portal_outcome_defaults_to_no_selection() -> None:
    assert PortalOutcome().selected_module_id is None


def test_run_portal_returns_selected_module_after_window_closes(
    qapp,
    manifest: SuiteManifest,
    ready_report: HealthReport,
) -> None:
    def select_module() -> None:
        windows = [
            widget
            for widget in qapp.topLevelWidgets()
            if isinstance(widget, MainWindow)
        ]
        assert len(windows) == 1
        windows[0].card("mpn-tolkning").open_button.click()

    QTimer.singleShot(0, select_module)

    outcome = run_portal(manifest, ready_report)

    assert outcome == PortalOutcome(selected_module_id="mpn-tolkning")
    assert not qapp.windowIcon().isNull()


class FakePortal:
    def __init__(
        self,
        manifest: SuiteManifest,
        outcomes: list[PortalOutcome],
    ) -> None:
        self.manifest = manifest
        self.outcomes = iter(outcomes)
        self.errors: list[str | None] = []

    @property
    def show_count(self) -> int:
        return len(self.errors)

    def __call__(self, startup_error: str | None = None) -> PortalOutcome:
        self.errors.append(startup_error)
        return next(self.outcomes)


def test_failed_entrypoint_reopens_portal_with_safe_norwegian_error(
    manifest: SuiteManifest,
) -> None:
    portal = FakePortal(
        manifest,
        [PortalOutcome("hemafrag"), PortalOutcome()],
    )

    def failing_resolver(_value: str):
        raise ImportError(r"C:\Users\alice\patient-123 could not import")

    code = run_application_loop(portal, resolver=failing_resolver)

    assert portal.show_count == 2
    assert code == 1
    assert portal.errors[0] is None
    assert portal.errors[1] is not None
    assert "kunne ikke åpnes" in portal.errors[1].lower()
    assert "alice" not in portal.errors[1]
    assert "patient-123" not in portal.errors[1]


def test_successful_entrypoint_owns_process_until_it_returns(
    manifest: SuiteManifest,
) -> None:
    portal = FakePortal(manifest, [PortalOutcome("igh-merge")])
    events: list[str] = []

    code = run_application_loop(
        portal,
        resolver=lambda _value: lambda: events.append("ran") or 7,
    )

    assert portal.show_count == 1
    assert events == ["ran"]
    assert code == 7
