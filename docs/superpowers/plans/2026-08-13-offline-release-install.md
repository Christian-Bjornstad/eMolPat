# Self-Contained Offline Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a downloadable `eMolPat-1.0.0-windows.zip` that installs eMolPat, all four analysis applications, and exact dependencies offline with `pip --user`, then reports real installation health in the portal.

**Architecture:** Preserve the existing deterministic builder and transactional installer as the only package-installation path. Add an environment observation boundary that feeds the existing pure health evaluator, a local-release locator shared by bootstrap and portal repair, deterministic ZIP/checksum generation, and a tag-only GitHub release workflow. The PyQt6 layer invokes installation through a background coordinator but never duplicates pip, manifest, or integrity logic.

**Tech Stack:** Python 3.12, PyQt6, pytest/pytest-qt, setuptools/wheel, PowerShell launchers, GitHub Actions on `windows-latest`.

## Global Constraints

- The supported workstation target is 64-bit Windows with Python FELLES 3.12.
- Installation uses `pip --user`, `--no-index`, local wheels, and `--require-hashes`; no workstation network access is permitted.
- A release contains exactly five application wheels: eMolPat, HemaFrag Diagnostics, IGH Merge, Archer/VPM-HTS, and MPN Tolkning.
- The portal never reports `Klar til bruk` without a verified install record, exact distribution versions, and resolvable imports.
- The supported download is the GitHub Release asset `eMolPat-1.0.0-windows.zip`, not `Code > Download ZIP`.
- Patient data, clinical inputs, credentials, and application settings remain outside eMolPat and its logs.
- No new runtime dependency is introduced.

---

### Task 1: Derive portal health from the installed environment

**Files:**
- Create: `src/emolpat/health_probe.py`
- Modify: `src/emolpat/domain.py`
- Modify: `src/emolpat/health.py`
- Modify: `src/emolpat/__main__.py`
- Modify: `src/emolpat/ui/translations.py`
- Test: `tests/test_health_probe.py`
- Test: `tests/test_health.py`
- Test: `tests/test_main_entrypoint.py`

**Interfaces:**
- Consumes: `SuiteManifest`, `UserPaths.install_record`, `read_install_record()`, and `evaluate_health()`.
- Produces: `probe_health(manifest: SuiteManifest, paths: UserPaths, version_reader: Callable[[str], str] = importlib.metadata.version, import_checker: Callable[[str], bool] = module_available) -> HealthReport` and `SuiteState.NOT_INSTALLED`.

- [ ] **Step 1: Write failing probe and entry-point tests**

Create `tests/test_health_probe.py` with injected readers so tests never depend on the developer machine:

```python
@pytest.fixture
def manifest():
    return load_manifest(Path("tests/fixtures/valid-manifest.json"))


def test_probe_is_not_installed_without_verified_record(tmp_path, manifest):
    paths = UserPaths(
        root=tmp_path,
        logs=tmp_path / "logs",
        install_record=tmp_path / "install-record.json",
        rollback=tmp_path / "rollback",
    )
    report = probe_health(
        manifest,
        paths,
        version_reader=lambda _name: pytest.fail("versions must not be read"),
        import_checker=lambda _name: pytest.fail("imports must not be checked"),
    )
    assert report.state is SuiteState.NOT_INSTALLED


def test_probe_requires_repair_when_registered_import_is_missing(tmp_path, manifest):
    paths = UserPaths(
        root=tmp_path,
        logs=tmp_path / "logs",
        install_record=tmp_path / "install-record.json",
        rollback=tmp_path / "rollback",
    )
    record = InstallRecord(
        suite_version=manifest.suite_version,
        manifest_sha256="a" * 64,
        verified_at="2026-08-13T12:00:00+00:00",
        modules=tuple(
            InstalledModule(module.distribution, module.version, module.import_name)
            for module in manifest.modules
        ),
    )
    replace_install_record(paths.install_record, record)
    expected_versions = {
        module.distribution: module.version for module in manifest.modules
    }
    report = probe_health(
        manifest,
        paths,
        version_reader=lambda name: expected_versions[name],
        import_checker=lambda name: name != "igh_merge",
    )
    assert report.state is SuiteState.REPAIR_REQUIRED
    assert report.issues == ("missing import: igh_merge",)
```

Add `tests/test_main_entrypoint.py` asserting `main()` passes the result of `probe_health()` into `InstalledPortal` instead of constructing `HealthReport(SuiteState.READY, ...)`.

- [ ] **Step 2: Run the new tests and verify red**

Run: `py -3.12 -m pytest tests/test_health_probe.py tests/test_health.py tests/test_main_entrypoint.py -q`

Expected: FAIL because `health_probe`, `NOT_INSTALLED`, and real startup probing do not exist.

- [ ] **Step 3: Implement the minimal health observation boundary**

Add `SuiteState.NOT_INSTALLED = "not_installed"`. Change the no-record branch of `evaluate_health()` to return that state. Implement `module_available(name)` with `importlib.util.find_spec(name) is not None`; catch `PackageNotFoundError`, `ImportError`, `ValueError`, and invalid install records and return deterministic non-clinical issues. Build observed distribution/import mappings only from the verified record's module list.

Replace the unconditional health construction in `emolpat.__main__.main()` with:

```python
paths = UserPaths.from_environment(os.environ)
configure_logging(paths)
manifest = bundled_manifest()
health = probe_health(manifest, paths)
return run_application_loop(InstalledPortal(manifest, health))
```

Add concise Norwegian `not_installed` copy to `STATE_TEXT`.

- [ ] **Step 4: Run the focused and existing UI tests**

Run: `$env:QT_QPA_PLATFORM='offscreen'; py -3.12 -m pytest tests/test_health_probe.py tests/test_health.py tests/test_main_entrypoint.py tests/ui -q`

Expected: PASS; existing repair and ready behavior remains intact.

- [ ] **Step 5: Commit real health evaluation**

```powershell
git add src/emolpat tests/test_health_probe.py tests/test_health.py tests/test_main_entrypoint.py
git commit -m "fix: derive portal health from installed applications"
```

### Task 2: Make the extracted release the authoritative offline source

**Files:**
- Create: `src/emolpat/release_source.py`
- Modify: `packaging/install_emolpat.py`
- Modify: `packaging/start_emolpat.py`
- Modify: `src/emolpat/ui/resources/suite-manifest.json`
- Modify: `tests/fixtures/valid-manifest.json`
- Test: `tests/test_release_source.py`
- Test: `tests/packaging/test_python_felles_scripts.py`
- Test: `tests/test_manifest.py`

**Interfaces:**
- Consumes: `UserPaths.rollback`, `InstallRecord.suite_version`, and `EMOLPAT_RELEASE_ROOT`.
- Produces: `find_release_root(paths: UserPaths, environment: Mapping[str, str], script_root: Path | None = None) -> Path | None` and bootstrap scripts that set `EMOLPAT_RELEASE_ROOT` to their own extracted directory.

- [ ] **Step 1: Write failing release-source tests**

Cover this exact priority:

```python
@pytest.fixture
def paths(tmp_path: Path) -> UserPaths:
    root = tmp_path / "user"
    return UserPaths(
        root=root,
        logs=root / "logs",
        install_record=root / "install-record.json",
        rollback=root / "rollback",
    )


def create_verified_release(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / "packages").mkdir()
    (root / "wheelhouse").mkdir()
    lock = b"packaging==25.0 --hash=sha256:" + b"a" * 64
    (root / "requirements.lock").write_bytes(lock)
    document = json.loads(Path("tests/fixtures/valid-manifest.json").read_text())
    document["files"] = [{
        "path": "requirements.lock",
        "sha256": hashlib.sha256(lock).hexdigest(),
    }]
    (root / "manifest.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def test_explicit_extracted_release_wins(tmp_path, paths):
    extracted = create_verified_release(tmp_path / "extracted")
    create_verified_release(paths.rollback / "1.0.0")
    result = find_release_root(
        paths,
        {"EMOLPAT_RELEASE_ROOT": str(extracted)},
        script_root=None,
    )
    assert result == extracted.resolve()


def test_retained_verified_release_is_repair_fallback(tmp_path, paths):
    replace_install_record(
        paths.install_record,
        InstallRecord(
            suite_version="1.0.0",
            manifest_sha256="b" * 64,
            verified_at="2026-08-13T12:00:00+00:00",
            modules=(InstalledModule("example", "1.0.0", "example"),),
        ),
    )
    retained = create_verified_release(paths.rollback / "1.0.0")
    assert find_release_root(paths, {}, None) == retained.resolve()
```

Add packaging assertions that `install_emolpat.py` defaults to `Path(__file__).resolve().parent`, and that both bootstrap scripts set `EMOLPAT_RELEASE_ROOT` before importing installed eMolPat code.

Add a parametrized bootstrap test proving Python 3.11 and 3.13 are rejected while 3.12 is accepted. Require both bundled and test manifests to declare `python_requires` as `>=3.12,<3.13`.

- [ ] **Step 2: Run focused tests and verify red**

Run: `py -3.12 -m pytest tests/test_release_source.py tests/packaging/test_python_felles_scripts.py tests/test_manifest.py -q`

Expected: FAIL because the local release locator does not exist and the installer still defaults to a hard-coded shared path.

- [ ] **Step 3: Implement safe local release discovery**

Resolve candidates without shell expansion. Accept a candidate only when `manifest.json`, `requirements.lock`, `packages/`, and `wheelhouse/` exist and `verify_release()` succeeds. `install_emolpat.release_root()` defaults to the script directory; `start_emolpat.py` stores its script directory in `EMOLPAT_RELEASE_ROOT` before activating the installed entry point.

Tighten both bootstrap `activate_user_site()` guards to `sys.version_info[:2] == (3, 12)` so a cp312 Windows dependency set is never installed into another interpreter.

- [ ] **Step 4: Verify bootstrap behavior**

Run: `py -3.12 -m pytest tests/test_release_source.py tests/packaging/test_python_felles_scripts.py tests/packaging/test_cmd_templates.py tests/test_manifest.py -q`

Expected: PASS and no `http://` or `https://` appears in workstation bootstrap scripts.

- [ ] **Step 5: Commit local release discovery**

```powershell
git add src/emolpat/release_source.py src/emolpat/ui/resources/suite-manifest.json packaging tests/test_release_source.py tests/fixtures/valid-manifest.json tests/test_manifest.py tests/packaging
git commit -m "fix: install from the extracted offline release"
```

### Task 3: Enforce an exact complete release and safe archive

**Files:**
- Modify: `src/emolpat/integrity.py`
- Modify: `scripts/build_suite.py`
- Create: `scripts/archive_release.py`
- Test: `tests/test_integrity.py`
- Test: `tests/test_build_suite.py`
- Test: `tests/test_archive_release.py`

**Interfaces:**
- Consumes: a verified root returned by `assemble_release()`.
- Produces: `create_release_archive(release_root: Path, destination: Path) -> tuple[Path, Path]`, returning the ZIP and `<zip>.sha256` paths.

- [ ] **Step 1: Write failing integrity and archive tests**

Add a test proving an undeclared wheel is rejected with `unexpected_file`, and a test proving the packages directory contains exactly the five expected normalized distributions. Add archive assertions:

```python
archive, checksum = create_release_archive(release, tmp_path / "out")
with ZipFile(archive) as zipped:
    assert all(name.startswith("eMolPat-1.0.0/") for name in zipped.namelist())
    assert "eMolPat-1.0.0/manifest.json" in zipped.namelist()
    assert not any(".." in PurePosixPath(name).parts for name in zipped.namelist())
assert checksum.read_text().split()[0] == sha256_file(archive)
```

Build the same fixture twice and assert byte-identical ZIPs and checksums.

- [ ] **Step 2: Run archive/integrity tests and verify red**

Run: `py -3.12 -m pytest tests/test_integrity.py tests/test_build_suite.py tests/test_archive_release.py -q`

Expected: FAIL because unexpected files are currently ignored and no archive function exists.

- [ ] **Step 3: Implement exact file-set and deterministic ZIP validation**

In `verify_release()`, compare all files beneath the release root (excluding `manifest.json`) with `manifest.files`; report sorted `unexpected_file` issues. In `assemble_release()`, parse wheel filenames and require the normalized set:

```python
{
    "emolpat",
    "hemafrag-diagnostics",
    "igh-merge",
    "archer-prosess",
    "mpn-tolkning",
}
```

For the four analysis wheels, also require the parsed wheel version to equal the corresponding `ModuleSpec.version` in the manifest template. Reject a renamed, missing, duplicate, or wrong-version application wheel before writing `manifest.json`.

Create ZIP members in sorted order, use `/` paths, fixed DOS timestamp `(1980, 1, 1, 0, 0, 0)`, and preserve one top-level release directory. Write `<64 lowercase hex>  <asset-name>\n` to the checksum file.

- [ ] **Step 4: Verify release assembly and archive determinism**

Run: `py -3.12 -m pytest tests/test_integrity.py tests/test_build_suite.py tests/test_archive_release.py tests/test_verify_suite_script.py -q`

Expected: PASS.

- [ ] **Step 5: Commit exact release packaging**

```powershell
git add src/emolpat/integrity.py scripts/build_suite.py scripts/archive_release.py tests
git commit -m "feat: create verified offline release archives"
```

### Task 4: Expose install and repair through the portal

**Files:**
- Create: `src/emolpat/ui/install_coordinator.py`
- Modify: `src/emolpat/install.py`
- Modify: `src/emolpat/ui/main_window.py`
- Modify: `src/emolpat/ui/app.py`
- Modify: `src/emolpat/__main__.py`
- Modify: `src/emolpat/ui/translations.py`
- Modify: `src/emolpat/logging_config.py`
- Test: `tests/test_install.py`
- Test: `tests/test_logging_config.py`
- Test: `tests/ui/test_install_coordinator.py`
- Test: `tests/ui/test_main_window.py`
- Test: `tests/ui/test_app_lifecycle.py`

**Interfaces:**
- Consumes: `install_release(release_root, runner, paths, progress)`, `find_release_root()`, and `probe_health()`.
- Produces: `InstallCoordinator(release_root: Path, paths: UserPaths, health_loader: Callable[[], HealthReport])`, emitting `stage_changed(str)` and `finished(InstallResult, HealthReport)`; `MainWindow.install_requested` signal and `set_health(report: HealthReport)`.

- [ ] **Step 1: Write failing installer progress and portal-action tests**

Extend `install_release()` tests with a recording callback and require stages `preflight`, `dependencies`, `components`, `verification`, and `record` in order. Add UI tests proving:

- `NOT_INSTALLED` disables all four launch buttons and shows `Installer programmer` when a verified release root exists;
- `REPAIR_REQUIRED` shows `Reparer installasjon`;
- `READY` hides the install action and enables all cards;
- install action is disabled while work runs;
- successful completion calls `set_health(READY)` and enables all cards;
- failed completion preserves disabled cards and shows concise Norwegian stage guidance.
- failed completion logs only the stage, return code, rollback result, and application-level error code; it never logs pip arguments or release path tails.

- [ ] **Step 2: Run focused tests and verify red**

Run: `$env:QT_QPA_PLATFORM='offscreen'; py -3.12 -m pytest tests/test_install.py tests/ui/test_install_coordinator.py tests/ui/test_main_window.py tests/ui/test_app_lifecycle.py -q`

Expected: FAIL because install progress callbacks, coordinator, and portal actions do not exist.

- [ ] **Step 3: Add progress reporting without duplicating installer logic**

Add an optional `progress: Callable[[str], None] = lambda _stage: None` parameter to `install_release()`. Emit before each stage and before rollback. Keep command construction, verification, record writes, and rollback in `emolpat.install`.

- [ ] **Step 4: Implement the background Qt coordinator and UI state refresh**

Run `install_release()` in a `QThread`-owned worker. Connect queued signals to the main thread, prevent a second operation, and keep the worker/thread references until `finished`. On success, call the injected `health_loader`; enable cards only if the refreshed report is `READY`. Closing the portal requests interruption but does not terminate pip unsafely.

Replace the current static System Status page with a status page that owns the action button and current issue summary. `run_portal()` receives optional `release_root`, `paths`, and `health_loader` dependencies; `__main__.py` supplies them from `find_release_root()` and `probe_health()`.

At the UI/service boundary, log a structured event such as `install_failed stage=components return_code=1 rolled_back=false`; pass values through the existing redaction filter and never include `Command.argv`, environment values, or clinical paths.

- [ ] **Step 5: Run UI and lifecycle verification**

Run: `$env:QT_QPA_PLATFORM='offscreen'; py -3.12 -m pytest tests/test_install.py tests/test_logging_config.py tests/ui -q`

Expected: PASS, including the rule that eMolPat closes before a standalone application starts.

- [ ] **Step 6: Commit portal install/repair behavior**

```powershell
git add src/emolpat tests/test_install.py tests/ui
git commit -m "feat: install and repair bundled applications from eMolPat"
```

### Task 5: Automate pinned component checkout and GitHub Release publication

**Files:**
- Create: `scripts/checkout_components.py`
- Create: `.github/workflows/release.yml`
- Modify: `scripts/build_suite.py`
- Test: `tests/test_checkout_components.py`
- Test: `tests/test_release_workflow.py`

**Interfaces:**
- Consumes: `release/components.json`, the explicit tag `v1.0.0`, `build_suite()`, `verify_suite()`, and `create_release_archive()`.
- Produces: `checkout_components(component_file: Path, destination: Path, runner: Callable[..., CompletedProcess]) -> tuple[Path, ...]` and a tag-only workflow publishing ZIP/checksum assets.

- [ ] **Step 1: Write failing checkout and workflow contract tests**

Use a fake command runner to assert each component is cloned from the declared HTTPS GitHub URL, checked out detached at the exact 40-character commit, and validated with `rev-parse HEAD`. Parse `.github/workflows/release.yml` as text and assert:

- trigger is `push.tags: ["v*.*.*"]` plus `workflow_dispatch` with a version input;
- job runs on `windows-latest` with Python `3.12`;
- permissions are limited to `contents: write`;
- tests and Ruff run before build;
- `build_suite.py`, `verify_suite.py`, and `archive_release.py` run;
- `gh release create` receives only the ZIP and checksum files.
- `GH_TOKEN` is supplied from `${{ github.token }}` rather than a repository secret.

- [ ] **Step 2: Run workflow tests and verify red**

Run: `py -3.12 -m pytest tests/test_checkout_components.py tests/test_release_workflow.py -q`

Expected: FAIL because the checkout helper and release workflow do not exist.

- [ ] **Step 3: Implement constrained component checkout**

Accept only `https://github.com/Christian-Bjornstad/<repo>.git` URLs already parsed by `load_components()`. Create each known `COMPONENT_DIRECTORIES` path, clone without selecting a moving branch, fetch the declared commit, check it out detached, and verify exact HEAD. Never pass component data through `shell=True`.

- [ ] **Step 4: Implement the tag-only Windows release workflow**

Derive version by removing the leading `v`; reject anything not matching `^[0-9]+\.[0-9]+\.[0-9]+$`. Build in `dist/`, verify the release root, create `eMolPat-<version>-windows.zip` and checksum, then run:

```powershell
gh release create "v$version" `
  "dist/eMolPat-$version-windows.zip" `
  "dist/eMolPat-$version-windows.zip.sha256" `
  --title "eMolPat $version" `
  --generate-notes
```

For an existing tag invoked through `workflow_dispatch`, use `gh release view` to fail closed rather than overwrite published assets.

- [ ] **Step 5: Verify workflow contracts and existing CI**

Run: `py -3.12 -m pytest tests/test_checkout_components.py tests/test_release_workflow.py -q; py -3.12 -m ruff check scripts tests`

Expected: PASS.

- [ ] **Step 6: Commit release automation**

```powershell
git add scripts/checkout_components.py scripts/build_suite.py .github/workflows/release.yml tests
git commit -m "ci: publish self-contained Windows releases"
```

### Task 6: Document the correct download and validate the complete path

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/operations/build-release.md`
- Modify: `docs/operations/python-felles.md`
- Modify: `docs/validation/release-checklist.md`
- Test: `tests/test_documentation_links.py`

**Interfaces:**
- Consumes: the published asset contract `eMolPat-1.0.0-windows.zip` and checksum.
- Produces: a prominent Releases download path and exact offline install/start instructions.

- [ ] **Step 1: Write a failing documentation contract test**

Assert README contains `https://github.com/Christian-Bjornstad/eMolPat/releases`, `eMolPat-<version>-windows.zip`, `Installer eMolPat.cmd`, `pip --user`, and a warning that `Code > Download ZIP` is source-only. Resolve every repository-relative Markdown/HTML asset link and require the target to exist.

- [ ] **Step 2: Run the documentation test and verify red**

Run: `py -3.12 -m pytest tests/test_documentation_links.py -q`

Expected: FAIL because README does not yet distinguish the source ZIP or link to Release assets.

- [ ] **Step 3: Update operator and user documentation**

Put a `Download eMolPat` link near the README title. Document extract → run installer → paste in Python FELLES → wait for verified success → run starter. Add checksum verification and tag publication commands to the build guide. Add a clean-machine checklist item requiring all four apps to open from eMolPat.

- [ ] **Step 4: Run the complete local gate**

Run:

```powershell
$env:QT_QPA_PLATFORM="offscreen"
py -3.12 -m pytest -q
py -3.12 -m ruff check .
git diff --check
```

Expected: all tests pass, Ruff reports no issues, and the diff has no whitespace errors.

- [ ] **Step 5: Build the real local release and inspect it**

From clean component checkouts at `release/components.json` commits, run:

```powershell
py -3.12 scripts\build_suite.py --version 1.0.0 --output dist --component-root C:\Users\molpa\Documents\ChatGPT\eMolPat-components
py -3.12 scripts\verify_suite.py dist\eMolPat-1.0.0
py -3.12 scripts\archive_release.py dist\eMolPat-1.0.0 --output dist
```

Inspect the ZIP and require five package wheels, all manifest-declared dependencies, four launchers, one safe top-level directory, and a matching checksum.

- [ ] **Step 6: Commit documentation and validation changes**

```powershell
git add README.md CHANGELOG.md docs tests/test_documentation_links.py
git commit -m "docs: explain the complete offline installation"
```

### Task 7: Review, merge, and publish version 1.0.0

**Files:**
- Review all changes against `origin/master`.
- Publish Git tag: `v1.0.0` only after merge and green `master` CI.

**Interfaces:**
- Consumes: verified implementation commits and GitHub release workflow.
- Produces: merged source plus downloadable `eMolPat-1.0.0-windows.zip` and checksum.

- [ ] **Step 1: Run the pre-merge review gate**

Review correctness, readability, architecture, security, and performance. Confirm no runtime URL fetch, arbitrary shell input, clinical logging, machine-wide install, or unconditional ready state exists. Re-run the full pytest, Ruff, clean release build, verifier, archive, and checksum checks on the exact branch head.

- [ ] **Step 2: Push a PR and wait for Windows CI**

Push `codex/offline-release-install`, create a PR targeting `master`, and require all Windows checks to succeed before merging.

- [ ] **Step 3: Merge and verify master**

Merge with a merge commit, fetch `origin/master`, verify the reviewed feature head is an ancestor and the merge tree matches, then wait for the `master` Windows validation.

- [ ] **Step 4: Publish the explicit release tag**

After green master CI, create and push annotated tag:

```powershell
$existing = git ls-remote --tags origin refs/tags/v1.0.0
if ($existing) { throw "Refusing to replace existing release tag v1.0.0" }
git tag -a v1.0.0 origin/master -m "Release eMolPat 1.0.0"
git push origin v1.0.0
```

Wait for the release workflow. Verify the GitHub Release contains exactly `eMolPat-1.0.0-windows.zip` and `eMolPat-1.0.0-windows.zip.sha256`; download both, verify the checksum locally, inspect the archive, and run `verify_suite.py` against the extracted directory.

- [ ] **Step 5: Record the remaining workstation gate honestly**

If a clean Python FELLES/Sykehuspartner workstation is not available during implementation, do not claim operational publication is complete. Report the automated release as published and explicitly retain the hands-on checklist: install with `Installer eMolPat.cmd`, start with `Start eMolPat.cmd`, and open HemaFrag, IGH Merge, VPM/HTS Tolkning, and MPN Tolkning once each.
