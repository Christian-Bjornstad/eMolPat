# Portal UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish eMolPat's visible identity with the canonical blue HemaFrag icon, compact health status, and a dedicated About page crediting Christian Bjørnstad.

**Architecture:** Keep the existing PyQt6 `MainWindow`, stacked-page navigation, and `ApplicationCard` boundaries. Extend the navigation with one bottom-aligned button, make `StatusBanner` support a compact presentation without changing health derivation, and replace only the bundled HemaFrag resource.

**Tech Stack:** Python 3.12, PyQt6, pytest-qt, Ruff, Pillow for asset verification only.

## Global Constraints

- Visible portal identity uses `Versjon`, not `Suite`; internal release models remain unchanged.
- Ready health is shown as `✓ Klar til bruk` at the upper-right and is not conveyed by color alone.
- The About page uses the exact approved Norwegian copy and creator credit `Utviklet av Christian Bjørnstad`.
- Launch behavior remains unchanged: eMolPat closes before the selected standalone application starts.
- No new runtime dependency is added.

---

### Task 1: Specify the polished portal behavior

**Files:**
- Modify: `tests/ui/test_main_window.py`
- Test: `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: `MainWindow(manifest: SuiteManifest, health: HealthReport)` and existing Qt object names.
- Produces: behavioral expectations for `version_label`, `about_button`, `about_page`, and compact `status_banner`.

- [ ] **Step 1: Write failing UI tests**

Add assertions that the version label is `Versjon 1.0.0`, the removed privacy phrases are absent, a bottom navigation button named `Om eMolPat` opens a page containing the approved paragraph and creator credit, and ready status exposes only `Klar til bruk` without the old detail sentence.

- [ ] **Step 2: Run tests to verify they fail**

Run: `$env:QT_QPA_PLATFORM='offscreen'; py -3.12 -m pytest tests/ui/test_main_window.py -q`

Expected: FAIL because the current window still says `Suite`, has no About tab/page, retains the privacy footer, and displays the wide status detail.

- [ ] **Step 3: Commit the red tests**

```powershell
git add tests/ui/test_main_window.py
git commit -m "test: specify polished portal navigation"
```

### Task 2: Implement compact status and About navigation

**Files:**
- Modify: `src/emolpat/ui/main_window.py`
- Modify: `src/emolpat/ui/widgets.py`
- Modify: `src/emolpat/ui/translations.py` only if accessible navigation copy requires it
- Test: `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: `StatusBanner(title: str, detail: str, ready: bool)` and the existing `QStackedWidget`.
- Produces: `MainWindow.version_label`, `MainWindow.about_button`, `MainWindow.about_page`, and a compact `StatusBanner` with state text and symbol.

- [ ] **Step 1: Add the minimal implementation**

Create the version label with `Versjon {manifest.suite_version}`; add `Om eMolPat` after the sidebar stretch so it remains at the bottom; append the About page after operational pages; connect the button to that page index; remove the privacy footer. Build the Programs heading as a horizontal row with title copy on the left and the compact `StatusBanner` on the right. Hide the detail label in compact mode while preserving it in `text()` for non-ready diagnostics only when visible.

- [ ] **Step 2: Run focused tests to verify green**

Run: `$env:QT_QPA_PLATFORM='offscreen'; py -3.12 -m pytest tests/ui/test_main_window.py tests/ui/test_install_progress.py -q`

Expected: PASS.

- [ ] **Step 3: Run Ruff on changed Python files**

Run: `py -3.12 -m ruff check src/emolpat/ui tests/ui`

Expected: `All checks passed!`

- [ ] **Step 4: Commit the implementation**

```powershell
git add src/emolpat/ui tests/ui/test_main_window.py
git commit -m "feat: polish portal status and About page"
```

### Task 3: Replace the HemaFrag resource and refresh documentation

**Files:**
- Modify: `src/emolpat/ui/resources/hemafrag.png`
- Modify: `docs/assets/portal-overview.png`
- Modify: `README.md` only if its visible copy or screenshot description is no longer accurate

**Interfaces:**
- Consumes: canonical HemaFrag asset `C:/Users/molpa/Documents/ChatGPT/eMolPat-components/HemaFrag-Diagnostics/assets/app_icon.png`.
- Produces: packaged resource `emolpat.ui.resources/hemafrag.png` and an updated real-window screenshot.

- [ ] **Step 1: Verify the source icon contract**

Use Pillow to assert the canonical source is a 640×640 RGBA image with transparent corners and differs from the currently bundled full-canvas transparent variant.

- [ ] **Step 2: Replace the resource without altering artwork**

Copy the canonical source bytes to `src/emolpat/ui/resources/hemafrag.png`; do not recolor, crop, or regenerate it.

- [ ] **Step 3: Render and inspect the actual portal**

Run the existing offscreen screenshot helper or instantiate `MainWindow` at 1180×780, capture `docs/assets/portal-overview.png`, and inspect it visually. Confirm the blue HemaFrag tile, compact top-right status, About tab placement, and absence of old footer copy.

- [ ] **Step 4: Verify package resources and full quality gate**

Run:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
py -3.12 -m pytest -q
py -3.12 -m ruff check .
py -3.12 -m pip wheel --no-deps . --wheel-dir dist
```

Inspect the wheel and assert it contains `emolpat/ui/resources/hemafrag.png` and `emolpat/ui/resources/emolpat.png`.

- [ ] **Step 5: Commit the identity assets**

```powershell
git add src/emolpat/ui/resources/hemafrag.png docs/assets/portal-overview.png README.md
git commit -m "docs: refresh the polished portal preview"
```

### Task 4: Review, publish, and merge

**Files:**
- Review all branch changes against `origin/master`.

**Interfaces:**
- Consumes: a clean, verified feature branch.
- Produces: a merged GitHub pull request whose `master` CI passes.

- [ ] **Step 1: Review correctness, readability, architecture, security, and performance**

Confirm no launch logic, health derivation, release contract, or clinical-data boundary changed; confirm all new visible text is Norwegian and accessible.

- [ ] **Step 2: Push and create a pull request**

Push `codex/portal-ui-polish`, create a PR targeting `master`, and wait for Windows CI.

- [ ] **Step 3: Merge after green CI**

Merge the PR with a merge commit, fetch `origin/master`, and verify the feature commit is an ancestor of the merge commit.

- [ ] **Step 4: Verify merged-master CI**

Wait for the Windows validation triggered by the merge commit and require a successful conclusion before reporting completion.
