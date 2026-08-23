# eMolPat Portal Stabilization and Unit Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a branch-only eMolPat 1.0.7-test candidate that stays responsive while separately launched analysis applications run and presents the approved Norwegian Hemato/Solide/STAT interface.

**Architecture:** Keep the verified offline installer and health model, but replace in-process handoff with a trusted child runner plus a non-blocking `subprocess.Popen` manager polled by Qt. Build the UI from manifest unit metadata, keep LVMS-STAT outside the install contract as a disabled STAT placeholder, and expose install/repair through a compact status dialog.

**Tech Stack:** Python 3.12–3.14, PyQt6, `subprocess`, pytest, pytest-qt, Ruff, setuptools wheels, existing offline suite builder.

**Spec:** `docs/superpowers/specs/2026-08-23-portal-stabilization-units-design.md`

## Global Constraints

- Work only in the isolated `codex/portal-stabilization` worktree based on `origin/master`.
- Preserve the original checkout's `.hermes`, `fix_manifest.py`, `release/app`, and all unrelated branch state.
- Use the exact suite identity `1.0.7-test`; keep the Python distribution version independent at `0.1.2`.
- Keep `requires-python = ">=3.12,<3.15"` and the Python FELLES 3.14 offline target.
- All four installed modules belong to `hemato`; Solide has no modules; STAT contains only a presentation placeholder.
- Keep portal text Norwegian and implement the approved A — Klinisk lys visual direction.
- Launch only trusted manifest entries through `sys.executable`; never construct a shell command.
- Never terminate a child analysis application when eMolPat closes.
- Never copy child stdout, child stderr, patient data, or local application configuration into eMolPat logs.
- Do not merge to `master` or publish an ordinary release before workstation approval.

---

## File responsibility map

- `src/emolpat/domain.py` — immutable suite, unit, health, and launch result types.
- `src/emolpat/manifest.py` — strict validation of the approved manifest contract.
- `src/emolpat/module_runner.py` — child-process CLI that resolves one trusted module identifier.
- `src/emolpat/launch.py` — entry-point resolution and non-blocking child-process tracking.
- `src/emolpat/ui/app.py` — Qt application wiring, polling timer, install guard, and window lifetime.
- `src/emolpat/ui/main_window.py` — unit pages, navigation, card orchestration, and About content.
- `src/emolpat/ui/widgets.py` — reusable status control, application cards, and placeholder cards.
- `src/emolpat/ui/status_dialog.py` — compact health, update, repair, and technical-detail dialog.
- `src/emolpat/ui/translations.py` — all Norwegian portal labels and controlled error copy.
- `src/emolpat/ui/resources/suite-manifest.json` — canonical suite identity and approved module metadata.
- `scripts/validate_manifest_consistency.py` — validates a caller-supplied suite version against the canonical manifest.
- `scripts/build_suite.py` — assembles the exact offline suite after version validation.

---

### Task 1: Restore the canonical Norwegian module contract

**Files:**
- Modify: `src/emolpat/domain.py:16-48`
- Modify: `src/emolpat/manifest.py:9-56`
- Modify: `src/emolpat/ui/resources/suite-manifest.json`
- Modify: `src/emolpat/ui/widgets.py:72-138`
- Modify: `tests/fixtures/valid-manifest.json`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_main_entrypoint.py`
- Modify: `tests/test_launch.py`
- Modify: `pyproject.toml:8`

**Interfaces:**
- Consumes: existing `APPROVED_MODULE_IDS`, `SuiteManifest`, and manifest JSON schema version 1.
- Produces: `ModuleUnit`, `ModuleSpec.unit: ModuleUnit`, canonical `description_nb`, suite version `1.0.7-test`, and portal distribution version `0.1.2`.

- [ ] **Step 1: Write failing manifest contract tests**

Add imports and assertions to `tests/test_manifest.py`:

```python
from emolpat.domain import ModuleUnit


def test_load_manifest_assigns_every_approved_module_to_hemato() -> None:
    manifest = load_manifest(FIXTURE)

    assert {module.unit for module in manifest.modules} == {ModuleUnit.HEMATO}
    assert all(module.description_nb for module in manifest.modules)


def test_load_manifest_rejects_unknown_unit(tmp_path: Path) -> None:
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    document["modules"][0]["unit"] = "laboratorium"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ManifestError, match="invalid module unit"):
        load_manifest(path)
```

Change `tests/test_main_entrypoint.py` to expect `1.0.7-test`. Update every direct
`ModuleSpec(...)` construction to pass `unit=ModuleUnit.HEMATO` and remove
`description_en`.

- [ ] **Step 2: Run the contract tests and confirm the red state**

Run:

```powershell
py -3.12 -m pytest tests/test_manifest.py tests/test_main_entrypoint.py tests/test_launch.py -q
```

Expected: FAIL because `ModuleUnit` and `ModuleSpec.unit` do not exist and the
bundled manifest still identifies 1.0.5.

- [ ] **Step 3: Implement the unit-aware Norwegian contract**

In `src/emolpat/domain.py`, add:

```python
class ModuleUnit(StrEnum):
    """Laboratory unit that owns an application card."""

    HEMATO = "hemato"
    SOLIDE = "solide"
    STAT = "stat"
```

Change `ModuleSpec` to end with:

```python
    icon: str
    description_nb: str
    unit: ModuleUnit
```

In `src/emolpat/manifest.py`, import `ModuleUnit` and construct it with a
controlled error:

```python
def _module_unit(data: dict[str, Any]) -> ModuleUnit:
    value = _string(data, "unit")
    try:
        return ModuleUnit(value)
    except ValueError as exc:
        raise ManifestError(f"invalid module unit: {value}") from exc
```

Pass `unit=_module_unit(values)` to `ModuleSpec`, keep
`description_nb=_string(values, "description_nb")`, and remove the
`description_en` read. Ensure `_module` consistently passes `values`, not the
unvalidated input object, to `_string`.

Set every bundled and fixture module to `"unit": "hemato"`; remove
`description_en`; set the bundled `suite_version` to `1.0.7-test`. Change the
application card description to `module.description_nb` and its Norwegian
labels to `Versjon`, `Åpne app`, `Verifisert`, and `Ikke klar`. Set the
`pyproject.toml` project version to `0.1.2`.

- [ ] **Step 4: Run focused contract and assembly tests**

Run:

```powershell
py -3.12 -m pytest tests/test_manifest.py tests/test_main_entrypoint.py tests/test_launch.py tests/test_archive_release.py tests/test_build_suite.py tests/test_verify_suite_script.py -q
```

Expected: PASS. This also proves release assembly can load the canonical
manifest again.

- [ ] **Step 5: Commit the contract repair**

```powershell
git add pyproject.toml src/emolpat/domain.py src/emolpat/manifest.py src/emolpat/ui/widgets.py src/emolpat/ui/resources/suite-manifest.json tests/fixtures/valid-manifest.json tests/test_manifest.py tests/test_main_entrypoint.py tests/test_launch.py
git commit -m "fix: restore canonical Norwegian module contract"
```

---

### Task 2: Add the trusted child module runner

**Files:**
- Create: `src/emolpat/module_runner.py`
- Create: `tests/test_module_runner.py`
- Modify: `src/emolpat/__main__.py:19-23`

**Interfaces:**
- Consumes: `bundled_manifest() -> SuiteManifest`, `resolve_entry_point(value: str) -> Callable[[], int | None]`, and a trusted module identifier.
- Produces: `run_module(module_id: str, resolver: EntryPointResolver = resolve_entry_point) -> int` and `main(argv: Sequence[str] | None = None) -> int`.

- [ ] **Step 1: Write failing child-runner tests**

Create `tests/test_module_runner.py`:

```python
from emolpat import module_runner


def test_run_module_calls_only_the_manifest_entry_point(monkeypatch, manifest) -> None:
    called: list[str] = []
    monkeypatch.setattr(module_runner, "bundled_manifest", lambda: manifest)

    code = module_runner.run_module(
        "igh-merge",
        resolver=lambda value: lambda: called.append(value) or 7,
    )

    assert code == 7
    assert called == ["igh_merge.__main__:main"]


def test_run_module_rejects_unknown_module_without_resolving(monkeypatch, manifest) -> None:
    monkeypatch.setattr(module_runner, "bundled_manifest", lambda: manifest)
    resolved: list[str] = []

    code = module_runner.run_module(
        "unknown",
        resolver=lambda value: resolved.append(value),
    )

    assert code == 2
    assert resolved == []


def test_main_requires_exactly_one_module_id() -> None:
    assert module_runner.main([]) == 2
    assert module_runner.main(["hemafrag", "extra"]) == 2
```

- [ ] **Step 2: Run the child-runner tests and confirm the red state**

Run:

```powershell
py -3.12 -m pytest tests/test_module_runner.py -q
```

Expected: FAIL because `emolpat.module_runner` does not exist.

- [ ] **Step 3: Implement the child runner without shell execution**

Create `src/emolpat/module_runner.py` with this public flow:

```python
from __future__ import annotations

from collections.abc import Sequence

from emolpat.__main__ import bundled_manifest
from emolpat.launch import EntryPointResolver, resolve_entry_point


def run_module(
    module_id: str,
    resolver: EntryPointResolver = resolve_entry_point,
) -> int:
    try:
        module = bundled_manifest().module(module_id)
        callback = resolver(module.entry_point)
    except (KeyError, ImportError, AttributeError, TypeError, ValueError):
        return 2
    result = callback()
    return int(result or 0)


def main(argv: Sequence[str] | None = None) -> int:
    import sys

    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        return 2
    return run_module(arguments[0])


if __name__ == "__main__":
    raise SystemExit(main())
```

Keep `bundled_manifest` side-effect free; importing `emolpat.__main__` must not
create a QApplication or probe workstation state.

- [ ] **Step 4: Run child-runner and entry-point tests**

```powershell
py -3.12 -m pytest tests/test_module_runner.py tests/test_launch.py tests/test_main_entrypoint.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the child runner**

```powershell
git add src/emolpat/module_runner.py src/emolpat/__main__.py tests/test_module_runner.py
git commit -m "feat: add trusted child module runner"
```

---

### Task 3: Replace handoff with non-blocking process tracking

**Files:**
- Modify: `src/emolpat/launch.py`
- Replace tests: `tests/test_launch.py`

**Interfaces:**
- Consumes: `ModuleSpec`, `sys.executable`, and injected `SpawnChild`.
- Produces: `ProcessExit`, `spawn_child(argv: tuple[str, ...]) -> ChildProcess`, and `ApplicationProcessManager` methods `start`, `poll`, `is_running`, `running_module_ids`, and `stop_monitoring`.

- [ ] **Step 1: Write failing process-manager tests**

Retain the resolver tests in `tests/test_launch.py`, remove the old in-process
`run_handoff` tests, and add a fake child:

```python
class FakeChild:
    def __init__(self, exit_code: int | None = None) -> None:
        self.exit_code = exit_code

    def poll(self) -> int | None:
        return self.exit_code


def test_manager_starts_trusted_child_command(module) -> None:
    commands: list[tuple[str, ...]] = []
    child = FakeChild()
    manager = ApplicationProcessManager(
        executable="python-felles.exe",
        spawn=lambda argv: commands.append(argv) or child,
    )

    result = manager.start(module)

    assert result.started
    assert commands == [
        ("python-felles.exe", "-m", "emolpat.module_runner", module.id)
    ]
    assert manager.running_module_ids == frozenset({module.id})


def test_manager_rejects_duplicate_but_allows_different_module(manifest) -> None:
    children = iter((FakeChild(), FakeChild()))
    manager = ApplicationProcessManager(spawn=lambda _argv: next(children))

    assert manager.start(manifest.module("hemafrag")).started
    duplicate = manager.start(manifest.module("hemafrag"))
    assert not duplicate.started
    assert duplicate.error_code == "already_running"
    assert manager.start(manifest.module("igh-merge")).started


def test_poll_removes_finished_children(manifest) -> None:
    child = FakeChild()
    manager = ApplicationProcessManager(spawn=lambda _argv: child)
    manager.start(manifest.module("mpn-tolkning"))
    child.exit_code = 0

    assert manager.poll() == (ProcessExit("mpn-tolkning", 0),)
    assert not manager.is_running("mpn-tolkning")


def test_stop_monitoring_never_terminates_child(manifest) -> None:
    child = FakeChild()
    manager = ApplicationProcessManager(spawn=lambda _argv: child)
    manager.start(manifest.module("hemafrag"))

    manager.stop_monitoring()

    assert manager.running_module_ids == frozenset()
```

Add a spawn-failure test that injects a function raising `OSError` and asserts
`error_code == "process_start_failed"`.

- [ ] **Step 2: Run process-manager tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/test_launch.py -q
```

Expected: FAIL because `ApplicationProcessManager` and `ProcessExit` do not
exist.

- [ ] **Step 3: Implement process tracking in `launch.py`**

Define protocols and immutable results:

```python
class ChildProcess(Protocol):
    def poll(self) -> int | None:
        raise NotImplementedError


SpawnChild = Callable[[tuple[str, ...]], ChildProcess]


@dataclass(frozen=True)
class ProcessExit:
    module_id: str
    exit_code: int
```

Implement the default child creation without shell use:

```python
def spawn_child(argv: tuple[str, ...]) -> ChildProcess:
    return subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
    )
```

Implement `ApplicationProcessManager` with a private
`dict[str, ChildProcess]`. `start` builds exactly
`(self.executable, "-m", "emolpat.module_runner", module.id)`, catches
`OSError`, and returns the existing structured `LaunchResult`. `poll` removes
every child whose `poll()` result is not `None` and returns ordered
`ProcessExit` values. `stop_monitoring` clears the dictionary and never calls
`terminate`, `kill`, or `wait`.

- [ ] **Step 4: Run process tests and lint the module**

```powershell
py -3.12 -m pytest tests/test_launch.py -q
py -3.12 -m ruff check src/emolpat/launch.py tests/test_launch.py
```

Expected: both commands PASS.

- [ ] **Step 5: Commit the process manager**

```powershell
git add src/emolpat/launch.py tests/test_launch.py
git commit -m "feat: track analysis apps in separate processes"
```

---

### Task 4: Wire child processes into the Qt portal lifetime

**Files:**
- Modify: `src/emolpat/ui/app.py`
- Modify: `src/emolpat/__main__.py`
- Replace: `tests/ui/test_app_lifecycle.py`
- Modify: `tests/e2e/test_suite_workflow.py`

**Interfaces:**
- Consumes: `ApplicationProcessManager.start/poll/stop_monitoring`, `MainWindow.module_selected`, and existing `InstallCoordinator`.
- Produces: `run_portal(manifest: SuiteManifest, health: HealthReport, startup_error: str | None = None, release_root: Path | None = None, paths: UserPaths | None = None, health_loader: Callable[[], HealthReport] | None = None, process_manager: ApplicationProcessManager | None = None) -> int` and a single-pass `main() -> int` with no handoff loop.

- [ ] **Step 1: Write failing responsive-lifecycle tests**

Replace the old `PortalOutcome` and `run_application_loop` tests with a fake
manager that records starts and controllable exits:

```python
def test_click_starts_child_and_keeps_portal_visible(
    qapp, manifest, ready_report
) -> None:
    manager = FakeProcessManager()

    def click_then_assert_then_close() -> None:
        window = next(
            widget for widget in qapp.topLevelWidgets()
            if isinstance(widget, MainWindow)
        )
        window.card("hemafrag").open_button.click()
        assert window.isVisible()
        assert manager.started == ["hemafrag"]
        window.close()

    QTimer.singleShot(0, click_then_assert_then_close)

    assert run_portal(manifest, ready_report, process_manager=manager) == 0
    assert manager.monitoring_stopped
```

Add tests proving the Qt timer consumes `ProcessExit`, two different card
clicks start two different modules, and process-start failure leaves the portal
visible.

- [ ] **Step 2: Run lifecycle tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/ui/test_app_lifecycle.py tests/e2e/test_suite_workflow.py -q
```

Expected: FAIL because `run_portal` still returns `PortalOutcome` and uses the
blocking handoff loop.

- [ ] **Step 3: Simplify the portal to one Qt event loop**

In `src/emolpat/ui/app.py`:

- delete `PortalOutcome`, `PortalFactory`, and `run_application_loop`;
- accept an optional process manager and create the real manager when absent;
- connect `window.module_selected` to a handler that resolves the `ModuleSpec`,
  calls `manager.start`, and updates the window through the Task 5 methods;
- create a parented `QTimer(window)` with a 250 ms interval;
- on each timeout, call `manager.poll()` and pass exits to the window;
- after `app.exec()`, stop the timer and call `manager.stop_monitoring()`;
- preserve deferred Qt deletion and return integer exit code 0.

Add these minimal `MainWindow` adapters so the lifecycle boundary is complete
before Task 5 centralizes presentation inside `ApplicationCard`:

```python
def set_module_running(self, module_id: str) -> None:
    self.card(module_id).open_button.setEnabled(False)


def set_module_ready(self, module_id: str) -> None:
    self.card(module_id).set_enabled(self.health.state is SuiteState.READY)


def set_module_failed(self, module_id: str, _error_code: str) -> None:
    self.card(module_id).set_enabled(self.health.state is SuiteState.READY)
```

In `src/emolpat/__main__.py`, delete `InstalledPortal` and call `run_portal`
once with the probed manifest, health, release root, paths, and health loader.
Keep diagnostic logging, but replace f-strings with parameterized logging.

Update `tests/e2e/test_suite_workflow.py` to assert clean installation, ready
health, and the exact child command produced by `ApplicationProcessManager`
instead of executing an in-process callback.

- [ ] **Step 4: Run lifecycle, installation, and entry-point tests**

```powershell
py -3.12 -m pytest tests/ui/test_app_lifecycle.py tests/e2e/test_suite_workflow.py tests/test_main_entrypoint.py tests/test_install.py -q
```

Expected: PASS with the portal still visible after a module click.

- [ ] **Step 5: Commit the Qt lifecycle replacement**

```powershell
git add src/emolpat/ui/app.py src/emolpat/__main__.py tests/ui/test_app_lifecycle.py tests/e2e/test_suite_workflow.py
git commit -m "fix: keep portal responsive during app launch"
```

---

### Task 5: Add explicit application-card runtime states

**Files:**
- Modify: `src/emolpat/ui/widgets.py:72-146`
- Modify: `src/emolpat/ui/main_window.py:227-516`
- Modify: `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: module start and exit callbacks from Task 4 plus suite health state.
- Produces: `ApplicationCard.show_ready`, `show_unhealthy`, `show_running`, `show_failure`; `MainWindow.set_module_running`, `set_module_ready`, `set_module_failed`.

- [ ] **Step 1: Write failing card-state tests**

Add to `tests/ui/test_main_window.py`:

```python
def test_running_card_blocks_duplicate_launch(qtbot, manifest, ready_report) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    window.set_module_running("hemafrag")

    card = window.card("hemafrag")
    assert card.open_button.text() == "Kjører"
    assert not card.open_button.isEnabled()
    assert window.card("igh-merge").open_button.isEnabled()


def test_finished_card_returns_to_ready(qtbot, manifest, ready_report) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    window.set_module_running("mpn-tolkning")

    window.set_module_ready("mpn-tolkning")

    card = window.card("mpn-tolkning")
    assert card.open_button.text() == "Åpne app"
    assert card.open_button.isEnabled()


def test_failed_card_offers_retry_without_exposing_details(
    qtbot, manifest, ready_report
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    window.set_module_failed("igh-merge", "process_start_failed")

    card = window.card("igh-merge")
    assert card.open_button.text() == "Prøv igjen"
    assert card.open_button.isEnabled()
    assert "kunne ikke åpnes" in card.status_label.text().lower()
    assert "process_start_failed" not in card.status_label.text()
```

- [ ] **Step 2: Run the card-state tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/ui/test_main_window.py -k "running_card or finished_card or failed_card" -q
```

Expected: FAIL because the runtime-state methods do not exist.

- [ ] **Step 3: Implement explicit card-state methods**

In `ApplicationCard`, centralize button, status, tooltip, and accessibility copy:

```python
def show_running(self) -> None:
    self.status_label.setText("●  Kjører")
    self.open_button.setText("Kjører")
    self.open_button.setEnabled(False)


def show_failure(self) -> None:
    self.status_label.setText("Appen kunne ikke åpnes")
    self.open_button.setText("Prøv igjen")
    self.open_button.setEnabled(True)
```

`show_ready` restores `●  Verifisert` and `Åpne app`; `show_unhealthy` restores
`●  Ikke klar` and disables the button. Update dynamic Qt properties and
repolish each state so semantic colors refresh.

Add the four `MainWindow` adapter methods and look up cards through `card()`.
On a non-zero `ProcessExit`, call `set_module_failed`; on zero call
`set_module_ready`.

- [ ] **Step 4: Run all card and lifecycle tests**

```powershell
py -3.12 -m pytest tests/ui/test_main_window.py tests/ui/test_app_lifecycle.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit runtime card states**

```powershell
git add src/emolpat/ui/widgets.py src/emolpat/ui/main_window.py tests/ui/test_main_window.py
git commit -m "feat: show analysis app runtime states"
```

---

### Task 6: Build Hemato, Solide, and STAT navigation

**Files:**
- Modify: `src/emolpat/ui/translations.py`
- Modify: `src/emolpat/ui/main_window.py:274-463`
- Modify: `src/emolpat/ui/widgets.py:147-170`
- Modify: `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: `ModuleSpec.unit`, the four real application cards, and the existing stacked-page navigation.
- Produces: `UNIT_NAVIGATION`, `MainWindow.unit_pages: dict[ModuleUnit, QWidget]`, an empty Solide page, and a disabled LVMS-STAT placeholder card.

- [ ] **Step 1: Write failing unit-navigation tests**

Replace legacy navigation assertions with:

```python
def test_sidebar_contains_only_units_and_about(qtbot, manifest, ready_report) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    labels = [button.text() for button in window.navigation_buttons]
    assert labels == ["Hemato", "Solide", "STAT", "Om eMolPat"]
    assert "Systemstatus" not in labels
    assert "Oppdater" not in labels


def test_hemato_contains_all_four_real_apps(qtbot, manifest, ready_report) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    assert [card.module_id for card in window.application_cards] == [
        "hemafrag", "igh-merge", "vpm-tolkning", "mpn-tolkning"
    ]


def test_solide_is_empty_and_stat_is_coming_later(
    qtbot, manifest, ready_report
) -> None:
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)

    solide_copy = " ".join(
        label.text() for label in window.solide_page.findChildren(QLabel)
    )
    stat_copy = " ".join(
        label.text() for label in window.stat_page.findChildren(QLabel)
    )
    stat_buttons = window.stat_page.findChildren(QPushButton)

    assert "Ingen verktøy tilgjengelig ennå" in solide_copy
    assert "LVMS-STAT" in stat_copy
    assert len(stat_buttons) == 1
    assert stat_buttons[0].text() == "Kommer senere"
    assert not stat_buttons[0].isEnabled()
```

Import `QLabel` and `QPushButton` in the test and inspect the actual child
widgets; do not add test-only production methods.

- [ ] **Step 2: Run navigation tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/ui/test_main_window.py -k "sidebar or hemato or solide or stat" -q
```

Expected: FAIL because the current pages are Programmer, System Status,
Update, and Help & Support.

- [ ] **Step 3: Implement unit pages and the STAT placeholder**

Define in `translations.py`:

```python
UNIT_NAVIGATION = (
    (ModuleUnit.HEMATO, "Hemato", "Åpne hematologiske analyseverktøy"),
    (ModuleUnit.SOLIDE, "Solide", "Verktøy for solide svulster"),
    (ModuleUnit.STAT, "STAT", "Statistikkverktøy"),
)
```

Build one stacked page per unit. Populate Hemato by filtering
`module.unit is ModuleUnit.HEMATO`. Render Solide with the exact empty text.
Render STAT with a dedicated placeholder widget containing `LVMS-STAT`, a short
description, and a disabled `Kommer senere` button. Do not create a
`ModuleSpec`, install record, health requirement, or launch signal for the
placeholder.

Anchor `Om eMolPat` after `layout.addStretch(1)` in the sidebar. Delete the old
Programmer/System Status/Update/Help page construction.

- [ ] **Step 4: Run unit-navigation and manifest tests**

```powershell
py -3.12 -m pytest tests/ui/test_main_window.py tests/test_manifest.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit unit navigation**

```powershell
git add src/emolpat/ui/translations.py src/emolpat/ui/main_window.py src/emolpat/ui/widgets.py tests/ui/test_main_window.py
git commit -m "feat: organize portal by laboratory unit"
```

---

### Task 7: Apply the clinical-light UI and compact system dialog

**Files:**
- Create: `src/emolpat/ui/status_dialog.py`
- Create: `tests/ui/test_status_dialog.py`
- Modify: `src/emolpat/ui/widgets.py:34-70`
- Modify: `src/emolpat/ui/main_window.py`
- Modify: `src/emolpat/ui/translations.py`
- Modify: `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: `HealthReport`, `SuiteState`, release availability, install-running state, and `MainWindow.install_requested`.
- Produces: clickable `StatusControl`, `SystemStatusDialog.action_requested`, Norwegian About page, and the approved clinical-light stylesheet.

- [ ] **Step 1: Write failing system-dialog and visual-contract tests**

Create `tests/ui/test_status_dialog.py`:

```python
def test_ready_dialog_has_no_install_action(qtbot, ready_report) -> None:
    dialog = SystemStatusDialog(ready_report, release_available=True)
    qtbot.addWidget(dialog)

    assert "Klar til bruk" in dialog.summary_label.text()
    assert dialog.version_label.text() == "Installert versjon: 1.0.0"
    assert dialog.action_button.isHidden()


def test_update_dialog_exposes_one_update_action(qtbot) -> None:
    health = HealthReport(SuiteState.UPDATE_AVAILABLE, "1.0.6", ())
    dialog = SystemStatusDialog(health, release_available=True)
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog.action_button.text() == "Oppdater eMolPat"
    assert dialog.action_button.isVisibleTo(dialog)


def test_repair_dialog_shows_controlled_issues_without_raw_details(qtbot) -> None:
    health = HealthReport(
        SuiteState.REPAIR_REQUIRED,
        "1.0.6",
        ("missing_distribution:igh-merge",),
    )
    dialog = SystemStatusDialog(health, release_available=True)
    qtbot.addWidget(dialog)

    assert "IGH Merge" in dialog.details_label.text()
    assert "missing_distribution" not in dialog.details_label.text()
```

Add main-window tests asserting the compact status width, status click opening
the dialog, Norwegian About text, creator credit, and stylesheet markers for
light main background, petrol sidebar, visible focus border, and semantic
ready/update/repair properties.

- [ ] **Step 2: Run dialog and visual-contract tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/ui/test_status_dialog.py tests/ui/test_main_window.py -q
```

Expected: FAIL because `SystemStatusDialog` and the target page structure do not
exist.

- [ ] **Step 3: Implement status control, dialog, About, and stylesheet**

Make `StatusControl` a keyboard-accessible `QPushButton` with compact title text
and a `state` dynamic property. Keep its maximum width at 220 px. Map states to
the exact labels `Klar til bruk`, `Oppdatering tilgjengelig`,
`Reparasjon kreves`, and `System utilgjengelig`.

Create `SystemStatusDialog(QDialog)` with this concrete widget structure:

```python
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
    action_requested = pyqtSignal()

    def __init__(
        self,
        health: HealthReport,
        release_available: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.summary_label = QLabel()
        self.version_label = QLabel()
        self.details_label = QLabel()
        self.action_button = QPushButton()
        self.action_button.clicked.connect(self.action_requested.emit)
        layout = QVBoxLayout(self)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.version_label)
        layout.addWidget(self.details_label)
        layout.addWidget(self.action_button)
        self.release_available = release_available
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
```

Use a centralized mapping from controlled issue prefixes and module IDs to
Norwegian user copy. Unknown issues become `En komponent kunne ikke
verifiseres`; raw issue strings are never displayed.

Move install/repair action ownership from the deleted status page into this
dialog. Connect `action_requested` to the existing `MainWindow._request_install`
flow. Keep install stage progress visible in the dialog and preserve the
successful-update close behavior.

Rewrite `STYLESHEET` to the approved palette: light blue-gray main shell, deep
petrol sidebar, white cards, teal primary buttons, and semantic state colors.
Use existing icon files and explicit focus borders. Restore Norwegian title,
subtitle, card, status, tooltip, and About copy including
`Utviklet av Christian Bjørnstad`. The About tests also require visible
`Diagnostikk` and `Teknisk hjelp` guidance without embedding a workstation path.

- [ ] **Step 4: Run the complete UI suite**

```powershell
py -3.12 -m pytest tests/ui -q
```

Expected: PASS with no test requiring the portal to close when an app opens.

- [ ] **Step 5: Commit the polished status and UI system**

```powershell
git add src/emolpat/ui/status_dialog.py src/emolpat/ui/widgets.py src/emolpat/ui/main_window.py src/emolpat/ui/translations.py tests/ui/test_status_dialog.py tests/ui/test_main_window.py
git commit -m "feat: restore clinical-light portal interface"
```

---

### Task 8: Enforce update guards and privacy-safe lifecycle logging

**Files:**
- Modify: `src/emolpat/ui/app.py`
- Modify: `src/emolpat/ui/main_window.py`
- Modify: `tests/ui/test_app_lifecycle.py`

**Interfaces:**
- Consumes: `ApplicationProcessManager.running_module_ids`, status-dialog action signal, and existing configured logger.
- Produces: blocked update/repair while children run, controlled warning copy, and parameterized lifecycle log events.

- [ ] **Step 1: Write failing install-guard and logging tests**

Add a lifecycle test:

```python
def test_install_is_blocked_while_analysis_app_runs(
    monkeypatch, qapp, manifest, ready_report, tmp_path
) -> None:
    manager = FakeProcessManager(running={"hemafrag"})
    starts: list[bool] = []
    warnings: list[str] = []

    class CoordinatorStub:
        def __init__(self, *_args, **_kwargs) -> None:
            self.stage_changed = SignalStub()
            self.finished = SignalStub()

        def start(self) -> bool:
            starts.append(True)
            return True

    monkeypatch.setattr("emolpat.ui.app.InstallCoordinator", CoordinatorStub)
    monkeypatch.setattr(
        "emolpat.ui.main_window.QMessageBox.warning",
        lambda _parent, _title, message: warnings.append(message),
    )

    def request_then_close() -> None:
        window = next(
            widget for widget in qapp.topLevelWidgets()
            if isinstance(widget, MainWindow)
        )
        window.install_requested.emit()
        window.close()

    QTimer.singleShot(0, request_then_close)

    run_portal(
        manifest,
        ready_report,
        release_root=tmp_path,
        paths=UserPaths(
            tmp_path,
            tmp_path / "logs",
            tmp_path / "install-record.json",
            tmp_path / "rollback",
        ),
        health_loader=lambda: ready_report,
        process_manager=manager,
    )

    assert starts == []
    assert warnings == [
        "Lukk kjørende analyseapper før eMolPat oppdateres eller repareres.\n"
        "Kjører: HemaFrag Diagnostics"
    ]
    assert manager.running_module_ids == frozenset({"hemafrag"})
```

Add a lifecycle test that configures the fake manager to return
`LaunchResult(module_id="hemafrag", started=False,
error_code="process_start_failed")`, clicks HemaFrag, and captures the
`emolpat` logger:

```python
with caplog.at_level(logging.INFO, logger="emolpat"):
    run_portal_with_scheduled_click_and_close(
        qapp,
        manifest,
        ready_report,
        process_manager=manager,
        module_id="hemafrag",
    )

record = next(
    item for item in caplog.records
    if item.msg == "module_process_failed module_id=%s error_code=%s"
)
assert record.msg == "module_process_failed module_id=%s error_code=%s"
assert record.args == ("hemafrag", "process_start_failed")
assert "patient" not in record.getMessage().lower()
```

Define `run_portal_with_scheduled_click_and_close` once at the top of
`tests/ui/test_app_lifecycle.py`; it schedules a `QTimer.singleShot`, clicks the
requested card, closes the visible `MainWindow`, and calls `run_portal` with the
passed manager. All Task 8 lifecycle tests use this same helper:

```python
def run_portal_with_scheduled_click_and_close(
    qapp,
    manifest: SuiteManifest,
    health: HealthReport,
    *,
    process_manager: FakeProcessManager,
    module_id: str,
) -> int:
    def click_and_close() -> None:
        window = next(
            widget for widget in qapp.topLevelWidgets()
            if isinstance(widget, MainWindow)
        )
        window.card(module_id).open_button.click()
        window.close()

    QTimer.singleShot(0, click_and_close)
    return run_portal(
        manifest,
        health,
        process_manager=process_manager,
    )
```

- [ ] **Step 2: Run guard and logging tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/ui/test_app_lifecycle.py tests/test_logging_config.py -q
```

Expected: FAIL until the status-dialog action is routed through the running-app
guard and lifecycle logs are normalized.

- [ ] **Step 3: Implement the guard and controlled logs**

Route every install/repair request through one handler in `ui/app.py`:

```python
def request_install() -> None:
    if manager.running_module_ids:
        window.show_running_apps_warning(manager.running_module_ids)
        return
    coordinator.start()
```

The warning says `Lukk kjørende analyseapper før eMolPat oppdateres eller
repareres` and lists display names resolved from the trusted manifest. Do not
show command lines, executable paths, or process IDs.

Use parameterized log messages in `ui/app.py` for `module_process_started`,
`module_process_stopped`, `module_process_failed`, and `install_blocked`.
Fields are restricted to module ID, controlled error code, integer exit code,
and count of running apps.

- [ ] **Step 4: Run lifecycle, logging, and complete portal tests**

```powershell
py -3.12 -m pytest tests/ui/test_app_lifecycle.py tests/test_logging_config.py tests/e2e/test_suite_workflow.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit guards and logging**

```powershell
git add src/emolpat/ui/app.py src/emolpat/ui/main_window.py tests/ui/test_app_lifecycle.py
git commit -m "fix: guard updates while analysis apps run"
```

---

### Task 9: Make suite identity and release validation deterministic

**Files:**
- Modify: `scripts/validate_manifest_consistency.py`
- Modify: `scripts/build_suite.py:291-332`
- Create: `tests/test_validate_manifest_consistency.py`
- Modify: `tests/test_build_suite.py`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Create: `docs/releases/1.0.7-test.md`

**Interfaces:**
- Consumes: canonical bundled manifest version `1.0.7-test` and build CLI `--version`.
- Produces: `validate_manifest_consistency(release_version: str) -> bool`, build fail-fast behavior, and candidate release notes.

- [ ] **Step 1: Write failing deterministic-version tests**

Create `tests/test_validate_manifest_consistency.py`:

```python
def test_validator_accepts_exact_bundled_suite_version() -> None:
    assert validate_manifest_consistency("1.0.7-test")


def test_validator_rejects_release_name_mismatch(capsys) -> None:
    assert not validate_manifest_consistency("1.0.8-test")
    assert "Version mismatch" in capsys.readouterr().out
```

Add a builder test that monkeypatches the validator to return false and asserts
`build_suite` raises `ValueError` before component wheels or dependencies are
built.

- [ ] **Step 2: Run version tests and confirm the red state**

```powershell
py -3.12 -m pytest tests/test_validate_manifest_consistency.py tests/test_build_suite.py -q
```

Expected: FAIL because the validator CLI reads the unrelated Python package
version and `build_suite` does not invoke it.

- [ ] **Step 3: Make the manifest the suite-version source**

Change the validator CLI to require `--version` and pass it directly to
`validate_manifest_consistency`. Remove pyproject version parsing. Call the
validator at the beginning of `build_suite`; raise:

```python
raise ValueError(
    f"suite version {version!r} does not match the bundled manifest"
)
```

Keep the existing assembly check as a second boundary. The release manifest,
install record, archive top-level directory, ZIP name, and checksum name remain
derived from the validated suite manifest.

Add a human-facing changelog entry for `1.0.7-test`, update README test
instructions, and create release notes covering unit navigation, separate app
processes, known STAT placeholder scope, install steps, and rollback to 1.0.4.

- [ ] **Step 4: Run version, build, archive, and documentation checks**

```powershell
py -3.12 -m pytest tests/test_validate_manifest_consistency.py tests/test_build_suite.py tests/test_archive_release.py tests/test_verify_suite_script.py -q
py -3.12 scripts/validate_manifest_consistency.py --version 1.0.7-test
```

Expected: both commands PASS.

- [ ] **Step 5: Commit deterministic release identity**

```powershell
git add scripts/validate_manifest_consistency.py scripts/build_suite.py tests/test_validate_manifest_consistency.py tests/test_build_suite.py CHANGELOG.md README.md docs/releases/1.0.7-test.md
git commit -m "build: enforce deterministic 1.0.7 test identity"
```

---

### Task 10: Verify the complete portal and offline upgrade candidate

**Files:**
- Create from the build scripts: ignored `dist/eMolPat-1.0.7-test/` and its ZIP/checksum artifacts.
- Update: `docs/releases/1.0.7-test.md` with final verified counts and checksum.

**Interfaces:**
- Consumes: all prior tasks, component checkouts under the configured component root, Python 3.12, and Python 3.14.
- Produces: verified branch-only offline ZIP and checksum suitable for user workstation testing.

- [ ] **Step 1: Run the complete Python 3.12 quality gate**

```powershell
py -3.12 -m pytest -q
py -3.12 -m ruff check .
git diff --check origin/master...HEAD
```

Expected: full suite PASS, Ruff reports `All checks passed!`, and diff check has
no output.

- [ ] **Step 2: Run the complete isolated Python 3.14 quality gate**

Create a temporary Python 3.14 virtual environment outside the repository,
install the project with its dev dependencies, and run:

```powershell
$python314Base = py -V:Astral/CPython3.14.0 -c "import sys; print(sys.executable)"
$qualityRoot = Join-Path $env:TEMP ("emolpat-314-quality-" + [guid]::NewGuid().ToString("N"))
& $python314Base -m venv $qualityRoot
$python314 = Join-Path $qualityRoot "Scripts\python.exe"
& $python314 -m pip install -e ".[dev]"
& $python314 -m pytest -q
& $python314 -m ruff check .
```

Expected: the same test count passes under Python 3.14 and Ruff is clean. Record
the interpreter path and exact counts in the release notes without recording a
user name or workstation share path.

- [ ] **Step 3: Build the exact offline suite**

From the isolated worktree, run with the actual component checkout root:

```powershell
py -3.12 scripts/build_suite.py `
  --version 1.0.7-test `
  --output dist `
  --component-root C:\Users\molpa\Documents\ChatGPT\eMolPat-components
py -3.12 scripts/verify_suite.py dist\eMolPat-1.0.7-test
py -3.12 scripts/archive_release.py dist\eMolPat-1.0.7-test --output dist
```

Expected: five approved package wheels, the complete CPython 3.14 wheelhouse,
manual Python FELLES launchers, a passing suite verifier, one Windows ZIP, and
one SHA-256 file.

- [ ] **Step 4: Verify fresh install in an isolated user profile**

Set temporary `PYTHONUSERBASE` and `LOCALAPPDATA` directories, run the packaged
`install_emolpat.py` with the Python 3.14 interpreter, and then run a probe that
asserts:

```powershell
$installRoot = Join-Path $env:TEMP ("emolpat-fresh-" + [guid]::NewGuid().ToString("N"))
$env:PYTHONUSERBASE = Join-Path $installRoot "userbase"
$env:LOCALAPPDATA = Join-Path $installRoot "localappdata"
$env:PIP_BREAK_SYSTEM_PACKAGES = "1"
& $python314Base "dist\eMolPat-1.0.7-test\install_emolpat.py"
```

```python
import os
from importlib import import_module
from importlib.metadata import distribution

from emolpat.__main__ import bundled_manifest
from emolpat.domain import SuiteState
from emolpat.health_probe import probe_health
from emolpat.paths import UserPaths

manifest = bundled_manifest()
paths = UserPaths.from_environment(os.environ)
assert distribution("emolpat").version == "0.1.2"
assert manifest.suite_version == "1.0.7-test"
assert probe_health(manifest, paths).state is SuiteState.READY
assert len(manifest.modules) == 4
for module in manifest.modules:
    import_module(module.import_name)
```

Import each module package and invoke the module runner with injected harmless
callbacks; do not open the real clinical application UIs in automated testing.

- [ ] **Step 5: Verify upgrade from an isolated 1.0.4 profile**

Download the published `1.0.4-python314-test` asset into a new temporary
directory, install it into a second temporary user profile, verify its ready
record, then run the 1.0.7-test installer over it:

```powershell
$upgradeRoot = Join-Path $env:TEMP ("emolpat-upgrade-" + [guid]::NewGuid().ToString("N"))
$oldAsset = Join-Path $upgradeRoot "old"
New-Item -ItemType Directory -Path $oldAsset -Force | Out-Null
gh release download v1.0.4-python314-test --dir $oldAsset --pattern "*.zip"
Expand-Archive (Join-Path $oldAsset "eMolPat-1.0.4-python314-test-windows.zip") (Join-Path $upgradeRoot "old-expanded")
$env:PYTHONUSERBASE = Join-Path $upgradeRoot "userbase"
$env:LOCALAPPDATA = Join-Path $upgradeRoot "localappdata"
$env:PIP_BREAK_SYSTEM_PACKAGES = "1"
& $python314Base (Join-Path $upgradeRoot "old-expanded\eMolPat-1.0.4-python314-test\install_emolpat.py")
& $python314Base "dist\eMolPat-1.0.7-test\install_emolpat.py"
```

Assert the resulting distribution version, install-record suite version,
manifest identity, four imports, and health state match Step 4. Confirm the
forced component reinstall command still contains `--force-reinstall`.

- [ ] **Step 6: Verify archive contents and checksum**

Use `zipfile` and `hashlib` to assert:

```python
assert package_wheel_count == 5
assert dependency_wheel_count == 79
assert checksum_from_file == hashlib.sha256(archive.read_bytes()).hexdigest()
assert all(name.startswith("eMolPat-1.0.7-test/") for name in archive_names)
```

Also assert all three manual FELLES launchers are present at the release root.

- [ ] **Step 7: Perform visual and behavior inspection**

Launch the portal against a synthetic ready health record and inspect:

- clinical-light colors and readable focus states;
- Hemato with four correct icons and cards;
- empty Solide copy;
- LVMS-STAT `Kommer senere` card;
- About copy and creator credit;
- status dialog in ready, update, and repair states;
- portal responsiveness while a harmless dummy child process runs;
- `Kjører`, completion, failure, and retry card transitions.

Capture no clinical data and use only synthetic module/process fixtures.

- [ ] **Step 8: Record final evidence and commit release-note verification**

Update `docs/releases/1.0.7-test.md` with exact test counts, wheel counts, archive
name, SHA-256, fresh-install result, and 1.0.4-upgrade result.

```powershell
git add docs/releases/1.0.7-test.md
git commit -m "docs: record 1.0.7 test verification"
```

- [ ] **Step 9: Push only the test branch for user handoff**

```powershell
git status --short
git push -u origin codex/portal-stabilization
```

Expected: clean tracked worktree, pushed branch, no pull request, and no merge.

- [ ] **Step 10: Publish and independently verify the GitHub prerelease**

Create an annotated test tag on the branch commit and a prerelease, never an
ordinary release:

```powershell
git tag -a v1.0.7-test -m "eMolPat 1.0.7 portal stabilization test"
git push origin v1.0.7-test
gh release create v1.0.7-test `
  dist\eMolPat-1.0.7-test-windows.zip `
  dist\eMolPat-1.0.7-test-windows.zip.sha256 `
  --verify-tag `
  --prerelease `
  --title "eMolPat 1.0.7 portal stabilization test" `
  --notes-file docs\releases\1.0.7-test.md
```

Download both published assets to a new temporary directory, recompute SHA-256,
open the downloaded ZIP with `zipfile`, and repeat the Step 6 structure checks.
Expected: the published checksum and archive contents exactly match the local
verified candidate. Confirm `gh pr list --head codex/portal-stabilization
--state open` returns no pull requests.

---

## Checkpoints

### Checkpoint A — after Tasks 1–3

- Manifest loads with Norwegian descriptions and required unit metadata.
- Trusted module runner accepts only one approved module identifier.
- Process manager starts exact argument vectors, rejects duplicates, permits
  different apps, and never terminates children.
- Focused tests and Ruff pass.

### Checkpoint B — after Tasks 4–6

- Portal uses one responsive Qt event loop.
- Card runtime states follow child lifetime.
- Sidebar contains only Hemato, Solide, STAT, and Om eMolPat.
- UI and lifecycle tests pass.

### Checkpoint C — after Tasks 7–9

- Clinical-light UI and compact system dialog match the approved design.
- Updates are blocked while apps run.
- Logs contain controlled technical lifecycle fields only.
- Suite identity validation and release documentation pass.
- Full Python 3.12 test suite and Ruff pass before release assembly.

### Checkpoint D — after Task 10

- Full Python 3.12 and 3.14 gates pass.
- Fresh offline install and 1.0.4 upgrade both reach `READY`.
- Archive structure and SHA-256 are verified.
- Branch-only 1.0.7-test candidate is ready for workstation approval.
