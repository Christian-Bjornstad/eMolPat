# eMolPat Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one Python/PyQt6 eMolPat suite that installs all four approved analysis tools through Python FELLES, verifies them as one atomic release, and closes its portal after successfully opening the selected standalone tool.

**Architecture:** eMolPat is a manifest-driven PyQt6 portal plus offline installer, health verifier, launch coordinator, and suite builder. The four applications remain separate packages; eMolPat assembles approved revisions and invokes their official entry points only after its own Qt event loop and portal window have shut down. Exact dependencies and artifacts are locked, checksummed, installed with `pip --user`, and verified as one suite version.

**Tech Stack:** Python 3.12–3.14, PyQt6, setuptools, pytest, Ruff, standard-library JSON/hash/logging/subprocess modules, PowerShell/CMD launcher templates, offline wheelhouse.

## Global Constraints

- Support Windows with Python `>=3.12,<3.15`; validate the actual Python FELLES build before the first work-computer release.
- Installation uses `python -m pip install --user` and requires no administrator rights.
- Runtime installation uses only the approved suite folder and its offline wheelhouse; no PyPI lookup is permitted.
- Updates are atomic: portal plus HemaFrag, IGH Merge, VPM/HTS Tolkning, and MPN Tolkning always share one suite version.
- The portal and its logs never read or store patient identifiers, clinical inputs, reports, credentials, or evidence-provider secrets.
- Each application retains its analysis code, settings, output locations, tests, and validation history.
- User-facing copy is Norwegian; internal source identifiers are English.
- The portal closes only after the selected application has begun startup; startup failure returns to or retains the portal with an actionable error.
- The first release does not embed applications, run multiple modules concurrently, reopen after module exit, contact GitHub from workstations, or add a server/telemetry/accounts.

## Planned repository structure

```text
pyproject.toml                         Build metadata, dependencies, commands
src/emolpat/__init__.py                Suite package version
src/emolpat/__main__.py                Development and installed entry point
src/emolpat/domain.py                  Typed suite/module/state models
src/emolpat/manifest.py                Manifest loading and structural checks
src/emolpat/integrity.py               File hashes and bundle verification
src/emolpat/health.py                  Installed-suite state derivation
src/emolpat/install.py                 Offline per-user install/repair engine
src/emolpat/launch.py                  Post-portal entry-point handoff
src/emolpat/logging_config.py          Redacted per-user technical logging
src/emolpat/paths.py                   Approved and per-user path resolution
src/emolpat/ui/app.py                  QApplication lifecycle and handoff
src/emolpat/ui/main_window.py          Approved portal shell and navigation
src/emolpat/ui/widgets.py              Application cards and status widgets
src/emolpat/ui/resources/              eMolPat and bundled application icons
src/emolpat/ui/translations.py         Norwegian user-facing strings
scripts/build_suite.py                 Reproducible suite assembler
scripts/verify_suite.py                Standalone release verifier
packaging/install_emolpat.py           Python FELLES installer entry script
packaging/start_emolpat.py             Python FELLES startup entry script
packaging/Installer eMolPat.cmd         Ivanti installer launcher
packaging/Start eMolPat.cmd             Ivanti portal launcher
release/components.json                Approved source-revision declarations
release/requirements.lock              Exact compatible runtime packages
tests/                                  Unit/integration/UI tests
docs/operations/                        Assembly, installation, repair, release guides
```

## External repository integration contract

The suite builder consumes clean local checkouts of the approved repository revisions. Before the first integrated release, each repository must expose a buildable wheel and an official callable entry point:

| Module | Distribution | Import health check | Entry point |
|---|---|---|---|
| HemaFrag Diagnostics | `hemafrag-diagnostics` | `hemafrag_diagnostics` | `hemafrag_diagnostics.__main__:main` |
| IGH Merge | `igh-merge` | `igh_merge` | `igh_merge.__main__:main` |
| VPM/HTS Tolkning | `archer-prosess` | `archer_processor` | `archer_processor.__main__:main` |
| MPN Tolkning | `mpn-tolkning` | `mpn_tolkning` | `mpn_tolkning.__main__:main` |

IGH Merge, VPM/HTS Tolkning, and MPN Tolkning already satisfy this contract. HemaFrag requires a packaging-only upstream change that moves or maps its root modules under `hemafrag_diagnostics` while preserving its existing `qt_app.main()` behavior. That upstream change receives its own review, test run, and validation note before eMolPat pins the revision.

Shared typed contracts introduced across Tasks 1–8 are:

```python
@dataclass(frozen=True)
class FileDigest:
    path: str
    sha256: str

@dataclass(frozen=True)
class VerificationIssue:
    code: str
    path: str
    message: str

@dataclass(frozen=True)
class VerificationReport:
    ok: bool
    issues: tuple[VerificationIssue, ...]

@dataclass(frozen=True)
class InstallRecord:
    suite_version: str
    manifest_sha256: str
    verified_at: str

class SuiteState(StrEnum):
    READY = "ready"
    UPDATE_AVAILABLE = "update_available"
    REPAIR_REQUIRED = "repair_required"
    UNAVAILABLE = "unavailable"

@dataclass(frozen=True)
class HealthReport:
    state: SuiteState
    suite_version: str | None
    issues: tuple[str, ...]

@dataclass(frozen=True)
class LaunchResult:
    started: bool
    error_code: str | None = None
    message: str | None = None

@dataclass(frozen=True)
class Command:
    stage: str
    argv: tuple[str, ...]

@dataclass(frozen=True)
class InstallResult:
    ok: bool
    completed_stage: str
    rolled_back: bool
    message: str

@dataclass(frozen=True)
class PortalOutcome:
    selected_module_id: str | None

@dataclass(frozen=True)
class UserPaths:
    root: Path
    logs: Path
    install_record: Path
    rollback: Path

@dataclass(frozen=True)
class ComponentSpec:
    id: str
    repository: str
    commit: str
    distribution: str
    import_name: str
    entry_point: str
    test_command: tuple[str, ...]
```

---

### Task 1: Establish the package and manifest contract

**Files:**
- Create: `pyproject.toml`
- Create: `src/emolpat/__init__.py`
- Create: `src/emolpat/domain.py`
- Create: `src/emolpat/manifest.py`
- Create: `tests/test_manifest.py`
- Create: `tests/fixtures/valid-manifest.json`

**Interfaces:**
- Produces: `ModuleSpec`, `SuiteManifest`, and `SuiteState` domain models.
- Produces: `load_manifest(path: Path) -> SuiteManifest` and `SuiteManifest.module(module_id: str) -> ModuleSpec`.
- Manifest module fields: `id`, `name`, `distribution`, `version`, `import_name`, `entry_point`, `icon`, `description_nb`.

- [ ] **Step 1: Write failing manifest tests**

```python
def test_load_manifest_returns_all_four_modules(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(VALID_MANIFEST, encoding="utf-8")
    manifest = load_manifest(path)
    assert manifest.suite_version == "1.0.0"
    assert [module.id for module in manifest.modules] == [
        "hemafrag", "igh-merge", "vpm-tolkning", "mpn-tolkning"
    ]

def test_load_manifest_rejects_duplicate_module_ids(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(DUPLICATE_ID_MANIFEST, encoding="utf-8")
    with pytest.raises(ManifestError, match="duplicate module id"):
        load_manifest(path)
```

- [ ] **Step 2: Run the focused test and confirm failure**

Run: `python -m pytest tests/test_manifest.py -q`  
Expected: collection fails because `emolpat.manifest` does not exist.

- [ ] **Step 3: Add build metadata and minimal typed parser**

```toml
[build-system]
requires = ["setuptools>=80", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "emolpat"
version = "0.1.0"
requires-python = ">=3.12,<3.15"
dependencies = ["packaging>=25,<26", "PyQt6>=6.7,<7"]

[project.optional-dependencies]
dev = ["build>=1.3,<2", "pytest>=8.4,<9", "pytest-qt>=4.5,<5", "ruff>=0.12,<1"]

[project.scripts]
emolpat = "emolpat.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]
```

```python
@dataclass(frozen=True)
class ModuleSpec:
    id: str
    name: str
    distribution: str
    version: str
    import_name: str
    entry_point: str
    icon: str
    description_nb: str

@dataclass(frozen=True)
class SuiteManifest:
    schema_version: int
    suite_version: str
    python_requires: str
    modules: tuple[ModuleSpec, ...]
    files: tuple[FileDigest, ...]
```

Use `json.loads`, reject unknown schema versions, require exactly the four approved module IDs, reject duplicate IDs, and validate entry points as `module.path:callable`.

- [ ] **Step 4: Run manifest tests and the initial quality gate**

Run: `python -m pytest tests/test_manifest.py -q`  
Expected: all manifest tests pass.  
Run: `python -m ruff check src/emolpat tests/test_manifest.py`  
Expected: exit code 0.

- [ ] **Step 5: Commit the contract**

```powershell
git add pyproject.toml src/emolpat tests/test_manifest.py tests/fixtures
git commit -m "feat: define the eMolPat suite manifest"
```

### Task 2: Verify release integrity before installation

**Files:**
- Create: `src/emolpat/integrity.py`
- Create: `tests/test_integrity.py`
- Modify: `src/emolpat/domain.py`
- Modify: `tests/fixtures/valid-manifest.json`

**Interfaces:**
- Consumes: `SuiteManifest.files: tuple[FileDigest, ...]`.
- Produces: `sha256_file(path: Path) -> str`.
- Produces: `verify_release(root: Path, manifest: SuiteManifest) -> VerificationReport`.
- `VerificationReport.ok` is true only when every declared file exists, matches its SHA-256 digest, and no required suite directory is absent.

- [ ] **Step 1: Write failing checksum, missing-file, and path-escape tests**

```python
def test_verify_release_rejects_changed_file(tmp_path: Path) -> None:
    artifact = tmp_path / "packages" / "portal.whl"
    artifact.parent.mkdir()
    artifact.write_bytes(b"changed")
    report = verify_release(tmp_path, manifest_for("packages/portal.whl", "0" * 64))
    assert not report.ok
    assert report.issues[0].code == "checksum_mismatch"

def test_verify_release_rejects_parent_path(tmp_path: Path) -> None:
    with pytest.raises(IntegrityError, match="outside release root"):
        verify_release(tmp_path, manifest_for("../outside.whl", "0" * 64))
```

- [ ] **Step 2: Confirm the tests fail**

Run: `python -m pytest tests/test_integrity.py -q`  
Expected: import failure for `emolpat.integrity`.

- [ ] **Step 3: Implement streaming hashes and deterministic reports**

```python
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
```

Resolve each manifest path beneath `root`, reject absolute paths and `..` escapes, verify `packages/`, `wheelhouse/`, and `requirements.lock`, and return issues sorted by relative path.

- [ ] **Step 4: Run focused and regression tests**

Run: `python -m pytest tests/test_integrity.py tests/test_manifest.py -q`  
Expected: all pass.

- [ ] **Step 5: Commit release verification**

```powershell
git add src/emolpat/domain.py src/emolpat/integrity.py tests
git commit -m "feat: verify approved suite artifacts"
```

### Task 3: Derive installed-suite health without touching clinical data

**Files:**
- Create: `src/emolpat/paths.py`
- Create: `src/emolpat/health.py`
- Create: `tests/test_health.py`
- Create: `tests/test_paths.py`

**Interfaces:**
- Produces: `UserPaths.from_environment(env: Mapping[str, str]) -> UserPaths`.
- Produces: `read_install_record(path: Path) -> InstallRecord | None`.
- Produces: `evaluate_health(manifest, record, distributions, imports) -> HealthReport`.
- Health states are exactly `READY`, `UPDATE_AVAILABLE`, `REPAIR_REQUIRED`, and `UNAVAILABLE`.

- [ ] **Step 1: Write health-state matrix tests**

```python
@pytest.mark.parametrize(
    ("record_version", "imports_ok", "shared_version", "expected"),
    [
        ("1.0.0", True, "1.0.0", SuiteState.READY),
        ("1.0.0", True, "1.1.0", SuiteState.UPDATE_AVAILABLE),
        ("1.0.0", False, "1.0.0", SuiteState.REPAIR_REQUIRED),
        (None, False, None, SuiteState.UNAVAILABLE),
    ],
)
def test_health_matrix(record_version, imports_ok, shared_version, expected):
    assert build_report(record_version, imports_ok, shared_version).state is expected
```

Also test that `UserPaths` uses `%LOCALAPPDATA%\eMolPat` for logs/state and never points into a module's patient-data directory.

- [ ] **Step 2: Confirm focused tests fail**

Run: `python -m pytest tests/test_health.py tests/test_paths.py -q`  
Expected: missing-module failures.

- [ ] **Step 3: Implement pure state derivation and per-user paths**

```python
class SuiteState(StrEnum):
    READY = "ready"
    UPDATE_AVAILABLE = "update_available"
    REPAIR_REQUIRED = "repair_required"
    UNAVAILABLE = "unavailable"
```

Use `importlib.metadata.version()` for installed distributions and `importlib.util.find_spec()` for import checks. Keep these effects behind injectable callables so tests never import clinical modules.

- [ ] **Step 4: Run health tests**

Run: `python -m pytest tests/test_health.py tests/test_paths.py -q`  
Expected: all pass.

- [ ] **Step 5: Commit health detection**

```powershell
git add src/emolpat/paths.py src/emolpat/health.py tests
git commit -m "feat: detect atomic suite health"
```

### Task 4: Establish installable upstream module entry points

**Files in external checkouts:**
- Modify: `HemaFrag-Diagnostics/pyproject.toml`
- Create: `HemaFrag-Diagnostics/hemafrag_diagnostics/__init__.py`
- Create: `HemaFrag-Diagnostics/hemafrag_diagnostics/__main__.py`
- Create: `HemaFrag-Diagnostics/assets/__init__.py`
- Create: `HemaFrag-Diagnostics/tests/test_package_entrypoint.py`
- Verify only: `IGH/src/igh_merge/__main__.py`
- Verify only: `Archer-prosess/src/archer_processor/__main__.py`
- Verify only: `MPN-Tolkning/src/mpn_tolkning/__main__.py`
- Create in eMolPat: `release/components.json`
- Create in eMolPat: `tests/test_component_contract.py`

**Interfaces:**
- Each module produces a buildable wheel with the distribution/import/entry-point names listed in the integration contract.
- `release/components.json` records repository URL, immutable commit SHA, distribution, import name, entry point, and test command.
- HemaFrag's new package entry point delegates to its existing Qt startup without changing analysis behavior.
- Produces: `load_components(path: Path) -> tuple[ComponentSpec, ...]`, where `ComponentSpec` contains `id`, `repository`, `commit`, `distribution`, `import_name`, `entry_point`, and `test_command`.

- [ ] **Step 1: Add a contract test that inspects four component declarations**

```python
def test_every_component_has_an_immutable_revision() -> None:
    components = load_components(Path("release/components.json"))
    assert len(components) == 4
    assert all(re.fullmatch(r"[0-9a-f]{40}", item.commit) for item in components)
    assert {item.import_name for item in components} == {
        "hemafrag_diagnostics", "igh_merge", "archer_processor", "mpn_tolkning"
    }
```

- [ ] **Step 2: In a clean HemaFrag branch, add a failing package-entry test**

```python
def test_packaged_entrypoint_delegates_to_existing_qt_main(monkeypatch):
    called = []
    monkeypatch.setattr("qt_app.main", lambda: called.append(True))
    from hemafrag_diagnostics.__main__ import main
    main()
    assert called == [True]
```

Run in HemaFrag: `python -m pytest tests/test_package_entrypoint.py -q`  
Expected: import failure for `hemafrag_diagnostics`.

- [ ] **Step 3: Add the packaging-only HemaFrag namespace and wheel metadata**

```python
# hemafrag_diagnostics/__main__.py
def main() -> None:
    from qt_app import main as run_app
    run_app()
```

Configure setuptools to include the namespace plus HemaFrag's existing root modules/packages and assets in the wheel. Do not rename analysis functions or change numerical/report behavior.

```toml
[project]
name = "hemafrag-diagnostics"
version = "1.2.0"
requires-python = ">=3.12,<3.15"

[project.scripts]
hemafrag-diagnostics = "hemafrag_diagnostics.__main__:main"

[tool.setuptools]
include-package-data = true
py-modules = ["app_meta", "app_resources", "config", "qt_app"]

[tool.setuptools.packages.find]
where = ["."]
include = ["assets*", "core*", "fraggler*", "gui_qt*", "hemafrag_diagnostics*"]
```

- [ ] **Step 4: Build and smoke-test all four exact wheels**

For each checkout run its repository test command, then:

```powershell
python -m build --wheel --outdir dist
python -m pip install --no-deps --target .wheel-smoke dist\*.whl
```

With `.wheel-smoke` first on `PYTHONPATH`, import the declared `import_name` and resolve the declared `entry_point` without invoking its GUI. Expected: four successful imports and callable resolution.

- [ ] **Step 5: Commit upstream HemaFrag packaging, then pin all four commit SHAs in eMolPat**

Commit HemaFrag separately with `feat: expose a packaged HemaFrag entry point`. Then commit `release/components.json` and its contract test in eMolPat with `build: pin approved suite components`.

### Checkpoint A: Contracts and component readiness

- [ ] Run: `python -m pytest tests/test_manifest.py tests/test_integrity.py tests/test_health.py tests/test_paths.py tests/test_component_contract.py -q`
- [ ] Build all four component wheels at pinned commits.
- [ ] Confirm no analysis-code diff exists in IGH, VPM, or MPN and HemaFrag changes are packaging-only.
- [ ] Have a human review the pinned component table before installer work.

### Task 5: Implement the safe application handoff coordinator

**Files:**
- Create: `src/emolpat/launch.py`
- Create: `tests/test_launch.py`

**Interfaces:**
- Consumes: `ModuleSpec.entry_point`.
- Produces: `resolve_entry_point(value: str) -> Callable[[], int | None]`.
- Produces: `run_handoff(module: ModuleSpec, resolver=resolve_entry_point) -> LaunchResult`.
- The portal calls the selected entry point only after its own `QApplication.exec()` has returned and the portal objects have been released.

- [ ] **Step 1: Write failing resolution and handoff tests**

```python
def test_handoff_calls_declared_entrypoint_after_portal_exit() -> None:
    events = []
    result = run_handoff(MODULE, resolver=lambda _: lambda: events.append("started"))
    assert events == ["started"]
    assert result.started

def test_handoff_reports_import_failure() -> None:
    result = run_handoff(MODULE, resolver=lambda _: (_ for _ in ()).throw(ImportError("x")))
    assert not result.started
    assert result.error_code == "entrypoint_import_failed"
```

- [ ] **Step 2: Confirm launch tests fail**

Run: `python -m pytest tests/test_launch.py -q`  
Expected: missing `emolpat.launch`.

- [ ] **Step 3: Implement callable resolution and structured launch errors**

```python
def resolve_entry_point(value: str) -> Callable[[], int | None]:
    module_name, attribute = value.split(":", 1)
    target = import_module(module_name)
    callback = getattr(target, attribute)
    if not callable(callback):
        raise TypeError(f"Entry point is not callable: {value}")
    return callback
```

Catch import/attribute errors before starting the module. Once the callable begins successfully, allow it to own the process until its application exits.

- [ ] **Step 4: Run launch tests**

Run: `python -m pytest tests/test_launch.py -q`  
Expected: all pass.

- [ ] **Step 5: Commit handoff logic**

```powershell
git add src/emolpat/launch.py tests/test_launch.py
git commit -m "feat: add standalone module handoff"
```

### Task 6: Build the approved PyQt6 portal

**Files:**
- Create: `src/emolpat/ui/__init__.py`
- Create: `src/emolpat/ui/app.py`
- Create: `src/emolpat/ui/main_window.py`
- Create: `src/emolpat/ui/widgets.py`
- Create: `src/emolpat/ui/translations.py`
- Create: `src/emolpat/ui/resources/emolpat.ico`
- Create: four approved module icon resources
- Create: `tests/ui/test_main_window.py`
- Create: `tests/ui/test_app_lifecycle.py`
- Modify: `src/emolpat/__main__.py`

**Interfaces:**
- Produces: `PortalOutcome(selected_module_id: str | None)`.
- Produces: `run_portal(manifest, health_report) -> PortalOutcome`.
- Consumes: health report and module metadata; emits only the selected module ID.

- [ ] **Step 1: Write failing offscreen UI tests**

```python
def test_portal_shows_four_real_modules(qtbot, manifest, ready_report):
    window = MainWindow(manifest, ready_report)
    qtbot.addWidget(window)
    assert [card.module_id for card in window.application_cards] == [
        "hemafrag", "igh-merge", "vpm-tolkning", "mpn-tolkning"
    ]
    assert all(not card.icon().isNull() for card in window.application_cards)

def test_clicking_open_emits_selection_and_closes_portal(qtbot, window):
    with qtbot.waitSignal(window.module_selected) as signal:
        qtbot.mouseClick(window.card("hemafrag").open_button, Qt.MouseButton.LeftButton)
    assert signal.args == ["hemafrag"]
    assert not window.isVisible()
```

- [ ] **Step 2: Confirm UI tests fail in offscreen mode**

Run: `$env:QT_QPA_PLATFORM='offscreen'; python -m pytest tests/ui -q`  
Expected: missing UI modules.

- [ ] **Step 3: Implement the approved portal design**

Build the deep-teal sidebar, Applications/System status/Suite update/Help pages, four cards with canonical icons, suite status banner, Norwegian labels, keyboard focus, accessible names, and one primary **Åpne program** action per card. Keep installation/update controls disabled until their services exist.

```python
def run_portal(manifest: SuiteManifest, health: HealthReport) -> PortalOutcome:
    app = QApplication(sys.argv)
    window = MainWindow(manifest, health)
    selected: list[str] = []
    window.module_selected.connect(selected.append)
    window.show()
    app.exec()
    window.deleteLater()
    app.processEvents()
    return PortalOutcome(selected[0] if selected else None)
```

- [ ] **Step 4: Run UI and accessibility checks**

Run: `$env:QT_QPA_PLATFORM='offscreen'; python -m pytest tests/ui -q`  
Expected: all pass.  
Manual: run `python -m emolpat` and compare spacing, colors, icons, and states to the approved mockup at 1280×800 and 1024×768.

- [ ] **Step 5: Commit the portal**

```powershell
git add src/emolpat/ui src/emolpat/__main__.py tests/ui
git commit -m "feat: add the eMolPat application portal"
```

### Task 7: Add redacted logging and startup failure recovery

**Files:**
- Create: `src/emolpat/logging_config.py`
- Create: `tests/test_logging_config.py`
- Modify: `src/emolpat/ui/app.py`
- Modify: `src/emolpat/launch.py`
- Modify: `tests/ui/test_app_lifecycle.py`

**Interfaces:**
- Produces: `configure_logging(paths: UserPaths) -> logging.Logger`.
- Produces: `redact_message(message: str) -> str`.
- Produces: `run_application_loop(portal_factory, resolver=resolve_entry_point) -> int`.
- Portal lifecycle returns to the portal with a Norwegian error dialog when entry-point resolution fails; after the entry point begins, the module owns the process.

- [ ] **Step 1: Write failing redaction and recovery tests**

```python
def test_log_redacts_windows_user_and_network_paths():
    message = redact_message(r"C:\Users\alice\patient-123 K:\Clinical\case.xlsx")
    assert "alice" not in message
    assert "patient-123" not in message

def test_failed_entrypoint_reopens_portal(fake_portal, failing_resolver):
    code = run_application_loop(fake_portal, resolver=failing_resolver)
    assert fake_portal.show_count == 2
    assert code == 1
```

- [ ] **Step 2: Confirm tests fail**

Run: `python -m pytest tests/test_logging_config.py tests/ui/test_app_lifecycle.py -q`.

- [ ] **Step 3: Implement bounded rotating logs and safe messages**

Use `RotatingFileHandler(maxBytes=2_000_000, backupCount=3)`. Log suite/module IDs, versions, stage names, exception classes, and return codes. Replace user-profile paths, shared-path tails, and values matching configured patient-ID patterns with `[redacted]`; never log input arguments from analysis modules.

```python
def configure_logging(paths: UserPaths) -> logging.Logger:
    paths.logs.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        paths.logs / "emolpat.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    logger = logging.getLogger("emolpat")
    logger.handlers[:] = [handler]
    logger.setLevel(logging.INFO)
    return logger
```

- [ ] **Step 4: Run recovery tests**

Run: `python -m pytest tests/test_logging_config.py tests/test_launch.py tests/ui/test_app_lifecycle.py -q`  
Expected: all pass.

- [ ] **Step 5: Commit recovery and logging**

```powershell
git add src/emolpat/logging_config.py src/emolpat/launch.py src/emolpat/ui/app.py tests
git commit -m "feat: recover safely from module startup failures"
```

### Task 8: Implement offline per-user installation, repair, and rollback

**Files:**
- Create: `src/emolpat/install.py`
- Create: `tests/test_install.py`
- Modify: `src/emolpat/domain.py`
- Modify: `src/emolpat/ui/main_window.py`
- Create: `tests/ui/test_install_progress.py`

**Interfaces:**
- Produces: `build_pip_commands(release_root, user_site) -> tuple[Command, ...]`.
- Produces: `install_release(release_root, runner, paths) -> InstallResult`.
- Pip arguments include `--user --no-index --find-links wheelhouse --require-hashes -r requirements.lock`.
- Writes `install-record.json` atomically only after complete import/version verification.

- [ ] **Step 1: Write failing command and transaction tests**

```python
def test_dependency_command_is_offline_and_per_user(release_root):
    command = build_pip_commands(release_root)[0].argv
    assert "--user" in command
    assert "--no-index" in command
    assert "--require-hashes" in command
    assert "--find-links" in command

def test_failed_update_does_not_write_new_install_record(tmp_path, failing_runner):
    result = install_release(RELEASE, failing_runner, paths_at(tmp_path))
    assert not result.ok
    assert read_install_record(paths_at(tmp_path).install_record).suite_version == "1.0.0"
```

- [ ] **Step 2: Confirm installer tests fail**

Run: `python -m pytest tests/test_install.py tests/ui/test_install_progress.py -q`.

- [ ] **Step 3: Implement staged installation**

Stages are `preflight`, `dependencies`, `components`, `verification`, `record`, and, on failure, `rollback`. Run pip in a subprocess first; when Python FELLES denies subprocess creation, call `pip._internal.cli.main` in-process with the identical argument list. Capture return codes without placing credentials or clinical paths in logs.

Write the new record to `install-record.json.tmp`, flush it, then replace `install-record.json`. For an update from version 1.0.0, retain the prior release's manifest, lock, and required wheels under `%LOCALAPPDATA%\eMolPat\rollback\1.0.0` until the new version verifies.

```python
def dependency_command(release_root: Path) -> Command:
    return Command(
        stage="dependencies",
        argv=(
            sys.executable, "-m", "pip", "install", "--user",
            "--no-index", "--find-links", str(release_root / "wheelhouse"),
            "--require-hashes", "-r", str(release_root / "requirements.lock"),
        ),
    )

def replace_install_record(path: Path, record: InstallRecord) -> None:
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(asdict(record), sort_keys=True), encoding="utf-8")
    temporary.replace(path)
```

- [ ] **Step 4: Run install and UI progress tests**

Run: `python -m pytest tests/test_install.py tests/ui/test_install_progress.py -q`  
Expected: clean install, repair, subprocess fallback, failed-update, and rollback tests pass.

- [ ] **Step 5: Commit atomic installation**

```powershell
git add src/emolpat/install.py src/emolpat/domain.py src/emolpat/ui/main_window.py tests
git commit -m "feat: install and repair the suite offline"
```

### Checkpoint B: Working local suite

- [ ] Run: `$env:QT_QPA_PLATFORM='offscreen'; python -m pytest -q`
- [ ] Run: `python -m ruff check .`
- [ ] Manually open each harmless fixture entry point and confirm the portal closes after startup.
- [ ] Force an import failure and confirm the portal remains available with a Norwegian message and redacted log.

### Task 9: Build reproducible atomic suite artifacts

**Files:**
- Create: `scripts/build_suite.py`
- Create: `scripts/verify_suite.py`
- Create: `release/requirements.in`
- Create: `release/requirements.lock`
- Create: `tests/test_build_suite.py`
- Create: `tests/test_verify_suite_script.py`
- Create: `docs/operations/build-release.md`

**Interfaces:**
- `python scripts/build_suite.py --version 1.0.0 --output dist --component-root C:\Users\molpa\Documents\ChatGPT\eMolPat-components` builds five wheels, collects exact Windows wheels, writes hashes, and emits `dist/eMolPat-1.0.0/`.
- Produces: `build_suite(version: str, output: Path, component_root: Path) -> Path`.
- `python scripts/verify_suite.py dist/eMolPat-1.0.0` exits 0 only for a complete valid bundle.

- [ ] **Step 1: Write failing artifact-layout and reproducibility tests**

```python
def test_build_contains_atomic_suite(tmp_path, fake_components):
    root = build_suite("1.0.0", tmp_path, fake_components)
    assert (root / "manifest.json").is_file()
    assert len(list((root / "packages").glob("*.whl"))) == 5
    assert (root / "wheelhouse").is_dir()
    assert verify_release(root, load_manifest(root / "manifest.json")).ok
```

- [ ] **Step 2: Confirm build tests fail**

Run: `python -m pytest tests/test_build_suite.py tests/test_verify_suite_script.py -q`.

- [ ] **Step 3: Implement deterministic assembly**

Require clean source trees at the exact commit SHAs in `release/components.json`. Build wheels with `python -m build --wheel`, download locked `win_amd64` wheels for the configured CPython versions with `pip download --only-binary=:all: --no-deps`, copy canonical icons, sort manifest entries, and set ZIP timestamps consistently when a transport archive is emitted.

Generate `requirements.lock` with exact `==` versions and `--hash=sha256:...` entries. Fail the build if dependency resolution produces a source distribution or if the same distribution has conflicting versions.

```python
def build_suite(version: str, output: Path, component_root: Path) -> Path:
    components = load_components(Path("release/components.json"))
    assert_clean_pinned_checkouts(component_root, components)
    release_root = output / f"eMolPat-{version}"
    build_component_wheels(component_root, release_root / "packages", components)
    collect_locked_wheels(Path("release/requirements.lock"), release_root / "wheelhouse")
    write_hashed_manifest(release_root, version, components)
    return release_root
```

- [ ] **Step 4: Run reproducibility and verifier tests**

Run: `python -m pytest tests/test_build_suite.py tests/test_verify_suite_script.py -q`  
Expected: two builds from identical inputs produce identical manifest/file hashes.

- [ ] **Step 5: Commit suite assembly**

```powershell
git add scripts release tests docs/operations/build-release.md
git commit -m "build: assemble reproducible eMolPat releases"
```

### Task 10: Add Python FELLES and Ivanti launchers

**Files:**
- Create: `packaging/install_emolpat.py`
- Create: `packaging/start_emolpat.py`
- Create: `packaging/Installer eMolPat.cmd`
- Create: `packaging/Start eMolPat.cmd`
- Create: `tests/packaging/test_python_felles_scripts.py`
- Create: `tests/packaging/test_cmd_templates.py`
- Create: `docs/operations/python-felles.md`

**Interfaces:**
- Installer command: `exec(open(r"K:\Felles\KDI\Delte\PAT\Molekylaerpatologi\Molpat OCCI\Administrasjon\Timeliste\Hemato\Christian\Apper\eMolPat\releases\1.0.0\install_emolpat.py", encoding="utf-8").read())`.
- Start command: `exec(open(r"K:\Felles\KDI\Delte\PAT\Molekylaerpatologi\Molpat OCCI\Administrasjon\Timeliste\Hemato\Christian\Apper\eMolPat\releases\1.0.0\start_emolpat.py", encoding="utf-8").read())`.
- Ivanti executable: `C:\Program Files (x86)\Ivanti\Workspace Control\pwrgate.exe` with application ID `15694`.

- [ ] **Step 1: Write launcher-content tests**

```python
def test_cmd_uses_ivanti_and_copies_complete_python_command():
    text = Path("packaging/Start eMolPat.cmd").read_text(encoding="utf-8")
    assert "pwrgate.exe" in text
    assert "15694" in text
    assert "Set-Clipboard" in text
    assert "start_emolpat.py" in text
```

- [ ] **Step 2: Confirm launcher tests fail**

Run: `python -m pytest tests/packaging -q`.

- [ ] **Step 3: Implement the four launchers from the proven MPN pattern**

Installer/start Python scripts activate `site.getusersitepackages()` before importing eMolPat, validate Python `>=3.12,<3.15`, write startup errors to `%LOCALAPPDATA%\eMolPat\logs`, and call `emolpat.install.install_release()` or `emolpat.ui.app.main()` respectively. CMD files keep the console open, verify Ivanti exists, copy only the non-secret command, open application ID `15694`, and print Norwegian paste instructions.

```python
def activate_user_site() -> Path:
    if not ((3, 12) <= sys.version_info[:2] < (3, 15)):
        raise RuntimeError(f"Python FELLES-versjon støttes ikke: {sys.version.split()[0]}")
    user_site = Path(site.getusersitepackages())
    user_site.mkdir(parents=True, exist_ok=True)
    value = str(user_site)
    if value in sys.path:
        sys.path.remove(value)
    sys.path.insert(0, value)
    return user_site
```

- [ ] **Step 4: Run packaging tests and a local dry run**

Run: `python -m pytest tests/packaging -q`  
Expected: all pass.  
Manual on a non-clinical workstation: point the scripts to a synthetic release path, confirm clipboard contents, and stop before launching Ivanti if it is unavailable.

- [ ] **Step 5: Commit managed-workstation launchers**

```powershell
git add packaging tests/packaging docs/operations/python-felles.md
git commit -m "feat: add Python FELLES suite launchers"
```

### Task 11: Complete end-to-end validation and operational documentation

**Files:**
- Create: `tests/e2e/test_suite_workflow.py`
- Create: `docs/operations/repair.md`
- Create: `docs/validation/release-checklist.md`
- Create: `README.md`
- Create: `CHANGELOG.md`
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- E2E tests use synthetic packages and entry points only.
- CI runs portal tests offscreen and never accesses live evidence providers or clinical fixtures.
- Release checklist records component SHAs, lock hash, clean-profile result, module test results, and laboratory reviewer sign-off.

- [ ] **Step 1: Write the failing synthetic end-to-end workflow**

```python
def test_clean_install_portal_selection_and_handoff(synthetic_release, clean_user):
    install = install_release(synthetic_release, clean_user.runner, clean_user.paths)
    assert install.ok
    assert evaluate_health(
        synthetic_release.manifest,
        clean_user.install_record,
        clean_user.distributions,
        clean_user.imports,
    ).state is SuiteState.READY
    outcome = run_portal_with_selection("hemafrag")
    assert outcome.selected_module_id == "hemafrag"
    assert run_handoff(synthetic_release.manifest.module("hemafrag")).started
```

- [ ] **Step 2: Confirm the E2E test fails before fixtures/docs are complete**

Run: `$env:QT_QPA_PLATFORM='offscreen'; python -m pytest tests/e2e/test_suite_workflow.py -q`.

- [ ] **Step 3: Add synthetic fixtures, CI, README, repair guide, and release checklist**

CI commands are:

```powershell
python -m pip install -e ".[dev]"
python -m ruff check .
$env:QT_QPA_PLATFORM='offscreen'
python -m pytest -q
```

README documents development setup, architecture, no-clinical-data boundary, and links to the approved design and operations guides. CHANGELOG begins with an unreleased entry describing the portal, atomic offline installation, and four-module handoff.

- [ ] **Step 4: Run the complete automated release gate**

Run: `python -m ruff check .`  
Run: `$env:QT_QPA_PLATFORM='offscreen'; python -m pytest -q`  
Run: `python scripts/build_suite.py --version 1.0.0 --output dist --component-root C:\Users\molpa\Documents\ChatGPT\eMolPat-components`  
Run: `python scripts/verify_suite.py dist/eMolPat-1.0.0`  
Expected: every command exits 0; the build uses only pinned clean component revisions.

- [ ] **Step 5: Commit the complete validation workflow**

```powershell
git add tests/e2e docs README.md CHANGELOG.md .github/workflows/ci.yml
git commit -m "test: validate the complete eMolPat suite workflow"
```

### Checkpoint C: Managed-workstation release candidate

- [ ] Run every existing test suite at the four pinned component commits.
- [ ] Install the built suite with a clean Windows user through Python FELLES and `--user`.
- [ ] Verify the portal icons, Norwegian text, and all four health states.
- [ ] Open each real module; confirm its window appears and the portal closes.
- [ ] Simulate one missing wheel, one corrupt checksum, one missing import, and one unavailable `K:` path; confirm safe Norwegian errors and redacted logs.
- [ ] Confirm no patient files, application settings, or reports are read, copied, changed, or deleted.
- [ ] Record laboratory review and Sykehuspartner packaging observations in the release checklist.

## Dependency order

```text
Manifest contract → Integrity → Health → Component packaging
        ↓                         ↓
   Portal UI ← Launch handoff ← upstream entry points
        ↓
Logging/recovery → Offline install/rollback
        ↓
Suite builder → Python FELLES launchers → E2E/release validation
```

## Primary risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Shared user-site dependency conflict | High | Resolve one exact suite lock, reject mixed versions, test all component suites against it before publication. |
| Qt application lifecycle prevents same-process handoff | High | Portal event loop returns and releases its QApplication before resolving the module entry point; validate all four on Python FELLES early at Checkpoint B. |
| HemaFrag is not currently a standard package | High | Make a separate packaging-only upstream change, run its full suite, and pin the reviewed commit. |
| `pip --user` update is not transactional | High | Full preflight, immutable offline releases, atomic install record, retained prior lock/artifacts, verified rollback, and explicit Repair required state. |
| Ivanti blocks subprocess creation | Medium | Use the proven in-process pip fallback and same-process module handoff. |
| `K:` drive is unavailable | Medium | Distinguish unavailable from corrupt, retain installed suite usability, and avoid claiming an update is required when the share cannot be checked. |
| Logs expose sensitive paths | High | Log only suite stages and IDs, redact user/share tails, prohibit analysis arguments and clinical content, and test redaction. |

## Definition of done

- All eleven tasks and three checkpoints pass.
- The exact pinned components and dependency lock are documented and reproducible.
- One offline eMolPat artifact installs all five packages with `--user`.
- The approved portal accurately reports complete-suite health.
- Clicking any module opens that standalone app and closes the portal after successful startup.
- Failed startup preserves or restores the portal and yields actionable Norwegian guidance.
- Clean-profile Python FELLES validation and laboratory review are recorded.
