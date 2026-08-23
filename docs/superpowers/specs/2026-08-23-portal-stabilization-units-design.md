# eMolPat portal stabilization and unit navigation design

**Status:** Approved in conversation on 2026-08-23
**Target branch:** `codex/portal-stabilization` from `origin/master`
**Candidate release:** `1.0.7-test`

## Purpose

Stabilize eMolPat as the single local Windows portal for the existing molecular
pathology applications. The portal must remain responsive while separately
launched applications run, use unit-based navigation, and return to the
approved light clinical visual direction.

The working `1.0.4-python314-test` release is the behavioral reference for
offline installation, update, and Python FELLES compatibility. The new work is
based on the current `origin/master` history so useful later fixes can be kept
without making an old release tag the new development trunk.

## Scope

This stabilization includes:

- reliable child-process launching for the four installed applications;
- one running instance per application and multiple different applications at
  the same time;
- Norwegian unit navigation for Hemato, Solide, and STAT;
- the approved light clinical blue-green interface;
- a compact system-status and update surface outside the sidebar;
- consistent suite metadata and a passing baseline test suite;
- fresh offline installation and upgrade verification from release 1.0.4.

This stabilization does not include:

- functional LVMS-STAT integration;
- any application under Solide;
- changes to the internal behavior of HemaFrag, IGH Merge, HTS-tolkning, or
  MPN-tolkning;
- patient-data processing, storage, or logging in eMolPat;
- merging to `master` or publishing an ordinary release before workstation
  testing is approved.

## Repository audit and branch policy

The current `master` is tagged `v1.0.6`. It contains the Python FELLES and
installation lineage from 1.0.4/1.0.5, the English visual redesign, manifest
changes, and an incomplete keep-open launch change.

The baseline test suite fails because the manifest parser requires
`description_en`, while the bundled manifest does not provide it. The master
launch flow also emits a module selection without closing the portal, so
control never returns to the existing handoff loop. The later
`fix-portal-keep-open` tip invokes application entry points synchronously from
the Qt UI thread; its tests pass, but an open application can block the portal.

Implementation will therefore be reconstructive rather than a wholesale merge:

- keep the verified offline installer, forced wheel replacement, pip bootstrap,
  Python FELLES launchers, health probing, rollback, and safe diagnostics;
- use 1.0.4 behavior as the reference for installation and update recovery;
- replace the later portal launch implementation;
- replace the dark English UI with the approved Norwegian clinical-light UI;
- ignore copied build artifacts under the original checkout's `release/app`;
- preserve all untracked files in the original working directory.

## Application process architecture

### Process isolation

Every analysis application runs in its own child Python process. The process is
started with `sys.executable`, which guarantees the child uses the same approved
Python FELLES interpreter and user-site installation as eMolPat.

A small `emolpat.module_runner` entry point receives a trusted module identifier,
loads the bundled manifest, resolves the approved entry point, and calls it in
the child process. No shell command is constructed and no user-supplied command
text is executed.

### Process manager

A focused process manager owns only application launch state:

- map each module identifier to its `subprocess.Popen` object;
- reject a second launch while that module is still running;
- allow different modules to run concurrently;
- poll child completion from a Qt timer without blocking the UI thread;
- emit started, stopped, and failed state changes for the corresponding card;
- return a card to its ready state when the child exits;
- log only module identifier, controlled error code, and exit code.

Child stdout and stderr are not copied into the portal log because application
output could contain information outside the portal's technical logging scope.
The portal never records patient data.

`subprocess.Popen` is preferred over a parent-owned `QProcess` because closing
the portal must not terminate an analysis application that may contain ongoing
work. On portal shutdown, eMolPat stops monitoring and leaves existing child
processes untouched.

### UI behavior

Each installed application card has these states:

- **Ready:** enabled button labeled `Åpne app`;
- **Starting/running:** disabled button labeled `Kjører`;
- **Launch failed:** concise visible error and enabled `Prøv igjen` action;
- **Not installed/unhealthy:** disabled button with the existing health reason.

An update or repair cannot begin while a tracked analysis application is
running. The portal asks the user to close running applications first. A
successful suite update still closes eMolPat so the next start loads only the
new installation.

## Manifest and unit model

`ModuleSpec` gains a required, validated `unit` field. The supported initial
values are `hemato`, `solide`, and `stat`. All four installed modules are marked
`hemato`.

Norwegian `description_nb` remains the canonical card description. The partial
`description_en` requirement introduced by the unfinished redesign is removed
from the active schema. Localization can be designed separately when more than
one complete language is required.

LVMS-STAT is not placed in the suite manifest for this release. Adding it there
would make health checks and the offline installer expect a wheel that is not
yet approved as part of eMolPat. Its STAT card is a presentation-only placeholder
labeled `Kommer senere`.

The bundled suite manifest is the canonical suite-version source. Release
assembly receives an expected version and must fail if it differs from the
manifest. The same version is written to the installation record and release
directory. Portal package distribution versions remain independent Python
package versions.

## Navigation and page structure

The sidebar contains only unit navigation and About:

1. **Hemato** — shows HemaFrag, IGH Merge, HTS-tolkning, and MPN-tolkning;
2. **Solide** — shows `Ingen verktøy tilgjengelig ennå`;
3. **STAT** — shows an LVMS-STAT card with a disabled `Kommer senere` button;
4. **Om eMolPat** — anchored at the bottom of the sidebar.

The former Programmer, Systemstatus, Oppdater, and Hjelp sidebar entries are
removed. Their essential behavior is reorganized rather than deleted.

The About page briefly explains eMolPat and each available tool, contains
`Utviklet av Christian Bjørnstad`, and links the user to diagnostic and
technical-help guidance.

## Status, update, and recovery surface

A compact status control appears at the upper-right of each unit page:

- green `Klar til bruk` when the installed suite is healthy;
- amber `Oppdatering tilgjengelig` with an update action;
- red `Reparasjon kreves` with repair and technical-detail actions;
- neutral unavailable state when the approved package cannot be located.

Activating the status control opens a compact system panel. The panel shows the
suite version, component health, controlled issue descriptions, and only the
actions valid for the current state. It reuses the existing install coordinator,
health probe, rollback, and release-source behavior.

## Visual system

The approved direction is **A — Klinisk lys**:

- very light blue-gray main background;
- deep petrol sidebar;
- white application cards with subtle neutral borders;
- blue and green application-icon accents;
- restrained teal primary actions;
- green, amber, and red reserved for semantic system state;
- existing application icons used for the four real tools;
- clear keyboard focus, readable contrast, and Norwegian labels throughout.

The layout remains usable at the current minimum desktop size and reflows card
columns when horizontal space is constrained. Empty and placeholder pages use
plain explanatory copy rather than invented functionality.

## Error handling and logging

Expected launch failures produce stable error codes for missing distribution,
invalid entry point, process creation failure, and early non-zero exit. The user
sees a concise Norwegian message and can retry without restarting the portal.

Logs remain under the existing local eMolPat log directory. Portal logs contain
technical lifecycle facts only and use existing diagnostic redaction rules.
Raw child output, configuration contents, report identifiers, paths selected
inside analysis tools, and patient information are excluded.

## Verification strategy

Implementation follows test-driven increments. Required verification is:

1. restore a green master-derived baseline by repairing schema/manifest and
   tests coherently;
2. unit-test module runner resolution and controlled failures;
3. unit-test process manager launch, duplicate rejection, concurrent different
   apps, polling, completion, failure, and portal-close survival behavior;
4. UI-test every card state and every Hemato/Solide/STAT/About page;
5. integration-test a harmless dummy child application while proving the portal
   event loop remains responsive;
6. test that update and repair are blocked while applications run;
7. run the full suite on Python 3.12 and Python FELLES-compatible Python 3.14;
8. lint and validate manifest/release consistency;
9. build and verify the complete offline `1.0.7-test` suite;
10. install into a clean temporary user profile;
11. update an isolated 1.0.4 user profile to 1.0.7-test and verify imports,
    health state, and all four application launch commands;
12. inspect the packaged portal visually before workstation handoff.

## Delivery gates

The first deliverable is a branch-only `1.0.7-test` candidate. It must include
the offline Windows ZIP, checksum, exact installation instructions, and a short
change summary. It is not merged to `master`, tagged as an ordinary release, or
presented for routine laboratory use until the user confirms the workstation
test.

## Acceptance criteria

- eMolPat stays visible and responsive while any installed app runs.
- Different applications can run together; the same application cannot be
  launched twice.
- Closing eMolPat does not close a running analysis application.
- Hemato contains all four existing tools; Solide is empty; STAT shows
  LVMS-STAT as `Kommer senere`.
- The sidebar and all portal copy follow the approved Norwegian clinical-light
  design.
- Status, update, repair, diagnostics, and About remain reachable without the
  removed legacy sidebar tabs.
- Manifest, build version, install record, and release directory are consistent.
- Fresh install and 1.0.4 upgrade paths pass the full verification strategy.
- Original untracked files and unrelated branches remain unchanged.
