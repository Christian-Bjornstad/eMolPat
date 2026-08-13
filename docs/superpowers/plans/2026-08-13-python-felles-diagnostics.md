# Python FELLES Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a branch-only, Ivanti-free replacement ZIP for complete offline installation, normal startup, startup diagnosis, and a safe clean-import retry.

**Architecture:** A shared Python diagnostic helper owns environment reporting, redacted traceback output, file logging, stale-module cleanup, and portal invocation. Four CMD files only copy explicit Python commands; the user opens Python FELLES through the workstation's normal method. A standard-library archive script produces one small deterministic test ZIP, while the existing v1.0.2 release continues to supply every application and dependency offline.

**Tech Stack:** Python 3.12, Windows CMD, PowerShell clipboard integration, pytest, standard-library `traceback`, `zipfile`, and `importlib`.

## Global Constraints

- Work only on `codex/python-felles-diagnostics`.
- Do not create a pull request, merge, tag, or public release.
- Do not reference, check, or start Ivanti from any test launcher.
- Do not fetch code or dependencies from GitHub at installation or startup time.
- Do not print environment variables, usernames, patient data, or arbitrary filesystem paths.
- Keep Python FELLES open by running helpers under `run_name='emolpat_felles'` and calling `main()` explicitly.

---

### Task 1: Shared safe startup diagnostic

**Files:**
- Create: `packaging/diagnose_emolpat_start.py`
- Create: `tests/packaging/test_start_diagnostics.py`

**Interfaces:**
- Produces: `redact(text: str) -> str`, `clear_emolpat_modules() -> tuple[str, ...]`, `diagnostic_lines(error: BaseException | None = None) -> tuple[str, ...]`, and `main() -> int`.
- Writes: `%LOCALAPPDATA%\eMolPat\logs\startup-diagnostic.log`.

- [ ] Write failing tests proving diagnostics include Python version, executable name, user-site, eMolPat location/status, exception type/message and traceback while redacting user paths.
- [ ] Run `py -3.12 -m pytest tests/packaging/test_start_diagnostics.py -q` and verify failure because the helper does not exist.
- [ ] Implement the smallest helper that reports those values, logs the same redacted text, optionally removes `emolpat` and `emolpat.*` from `sys.modules`, invalidates import caches, and invokes `emolpat.__main__.main`.
- [ ] Run the focused test and verify it passes.
- [ ] Commit as `feat: add safe Python FELLES startup diagnostics`.

### Task 2: Four manual Python FELLES launchers

**Files:**
- Create: `packaging/Installer eMolPat - Manuell FELLES.cmd`
- Create: `packaging/Start eMolPat - Manuell FELLES.cmd`
- Create: `packaging/Start eMolPat - Diagnose.cmd`
- Create: `packaging/Start eMolPat - Clean import.cmd`
- Modify: `tests/packaging/test_cmd_templates.py`

**Interfaces:**
- The installer and starter consume the existing `install_emolpat.py` and `start_emolpat.py` through clipboard commands.
- Both diagnostic launchers consume `packaging/diagnose_emolpat_start.py` through a clipboard command.
- The clean launcher sets `EMOLPAT_DIAGNOSTIC_CLEAN_IMPORT=1` only in the pasted Python command.

- [ ] Add failing parametrized tests requiring zero `Ivanti`, `pwrgate`, `15694`, or `start` references; `runpy.run_path`; `run_name='emolpat_felles'`; explicit `main()` invocation; the correct Python helper; and the clean-import flag only in the clean launcher.
- [ ] Run the focused CMD tests and verify failure because the two manual launchers do not exist and the diagnostic launchers still reference Ivanti.
- [ ] Create the installer and normal starter, and simplify both diagnostic CMD files so each only copies its command and prints manual open/paste instructions.
- [ ] Run packaging tests and verify they pass.
- [ ] Commit as `fix: remove Ivanti from Python FELLES launchers`.

### Task 3: Branch-only replacement ZIP

**Files:**
- Create: `scripts/build_diagnostic_patch.py`
- Create: `tests/test_build_diagnostic_patch.py`
- Modify: `README.md`

**Interfaces:**
- Produces: `dist/eMolPat-1.0.2-startup-diagnostics.zip` containing exactly the shared helper and four CMD launchers under one `eMolPat-1.0.2-startup-diagnostics/` directory.

- [ ] Update the archive test to require deterministic names, exactly five payload files, no Ivanti text, and no install wheels or clinical data.
- [ ] Run the focused archive test and verify failure because the builder still emits three files.
- [ ] Update the standard-library deterministic ZIP builder and branch-testing instructions.
- [ ] Run the focused test, build the ZIP, inspect its entry names, and verify it passes.
- [ ] Commit as `build: package Python FELLES diagnostic launchers`.

### Task 4: Final verification and branch publication

**Files:**
- Verify all changed files and generated ignored archive.

- [ ] Run `py -3.12 -m pytest -q` and require zero failures.
- [ ] Run `py -3.12 -m ruff check .` and require zero findings.
- [ ] Run `git diff --check` and require no whitespace errors.
- [ ] Inspect the generated ZIP and all four pasted commands directly.
- [ ] Push `codex/python-felles-diagnostics` only; do not create a PR.
- [ ] Give the user exact download/copy/run instructions and ask for the displayed traceback from the Diagnose launcher before selecting a production fix.
