# Atomic Update Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace stale same-version wheels and finish updates by closing the old portal process.

**Architecture:** Keep the existing offline installer and Qt coordinator. Strengthen the component pip command, align wheel and suite versions, then make successful UI installation an explicit restart boundary.

**Tech Stack:** Python 3.14, pip offline wheelhouse, PyQt6, pytest.

## Global Constraints

- New immutable prerelease: `v1.0.4-python314-test`.
- Installation remains offline and uses `pip --user`.
- No existing release or tag is modified.

---

### Task 1: Replace stale application wheels

**Files:** `tests/test_install.py`, `src/emolpat/install.py`

- [ ] Add a failing assertion that the component command contains `--force-reinstall`.
- [ ] Run the focused test and confirm the missing argument failure.
- [ ] Add the argument to the component command only.
- [ ] Run installation tests and commit.

### Task 2: Align installed portal identity

**Files:** `pyproject.toml`, `src/emolpat/ui/resources/suite-manifest.json`, `tests/test_main_entrypoint.py`

- [ ] Add a failing test that `bundled_manifest().suite_version` is `1.0.4-python314-test`.
- [ ] Run it and confirm the old `1.0.0` value.
- [ ] Set the distribution to `0.1.1` and bundled suite to `1.0.4-python314-test`.
- [ ] Run focused tests and commit.

### Task 3: Make update completion a restart boundary

**Files:** `tests/ui/test_main_window.py`, `src/emolpat/ui/main_window.py`, `src/emolpat/ui/translations.py`

- [ ] Add a failing UI test requiring a success message and closed window.
- [ ] Run it and confirm the portal remains open.
- [ ] On successful installation, show completion copy, clear running state, refresh health, and close.
- [ ] Run UI tests and commit.

### Task 4: Verify and publish

**Files:** `CHANGELOG.md`, `docs/releases/1.0.4-python314-test.md`

- [ ] Run all tests and Ruff under Python 3.12 and all tests under Python 3.14.
- [ ] Build and verify `1.0.4-python314-test` from pinned component commits.
- [ ] Install into a blank temporary Python 3.14 user site and import all tools.
- [ ] Archive, checksum, review, commit documentation, and push the branch.
- [ ] Tag and publish `v1.0.4-python314-test` as a GitHub prerelease without PR or merge.
