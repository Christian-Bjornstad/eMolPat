# Implementation Plan: eMolPat Suite

## Overview

Build a single offline-installable PyQt6 suite that packages and verifies HemaFrag Diagnostics, IGH Merge, VPM/HTS Tolkning, and MPN Tolkning, then launches one selected standalone tool while closing the portal. The detailed test-driven plan is in `docs/superpowers/plans/2026-08-13-emolpat-suite.md`.

## Architecture decisions

- One manifest-driven portal; four independently validated application packages.
- One exact offline dependency lock and atomic suite version.
- Per-user `pip --user` installation through Python FELLES/Ivanti.
- Same-process post-portal handoff, with no overlapping Qt application loops.
- Approved immutable releases on `K:`; GitHub is development source only.

## Phases

### Phase 1: Contracts and component readiness

- Task 1: Package and manifest contract
- Task 2: Release integrity verification
- Task 3: Installed-suite health
- Task 4: Upstream component entry points and HemaFrag packaging
- Checkpoint A: Build and import all pinned component wheels

### Phase 2: Working local suite

- Task 5: Application handoff coordinator
- Task 6: Approved PyQt6 portal
- Task 7: Redacted logging and startup recovery
- Task 8: Offline install, repair, and rollback
- Checkpoint B: Complete local test suite and synthetic handoff

### Phase 3: Release and work-computer integration

- Task 9: Reproducible atomic suite builder
- Task 10: Python FELLES/Ivanti launchers
- Task 11: End-to-end validation and operations documentation
- Checkpoint C: Clean-profile managed-workstation validation

## Risks

- Shared user-site dependency conflicts: mitigate with one exact tested lock.
- Qt lifecycle restrictions: validate same-process handoff early.
- HemaFrag package layout: isolate as packaging-only upstream work.
- Non-transactional pip updates: preflight, retain rollback artifacts, and verify before recording success.
- Sensitive log contents: prohibit analysis arguments and test path redaction.

