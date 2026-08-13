# eMolPat Suite Design

**Status:** Approved design awaiting written-spec review  
**Date:** 2026-08-13  
**Product:** eMolPat  
**Initial platform:** Managed Windows laboratory workstations

## Objective

eMolPat is one locally installed molecular-pathology application suite. It gives laboratory staff a single, polished portal for opening four existing analysis applications:

1. HemaFrag Diagnostics
2. IGH Merge
3. VPM/HTS Tolkning
4. MPN Tolkning

The suite must preserve each application's existing processing code, validation boundary, settings, and clinical safeguards. eMolPat packages, verifies, updates, and launches the applications; it does not rewrite their analytical workflows.

The first release succeeds when a laboratory user can install one approved eMolPat release through Python FELLES, open one portal, select any of the four modules, and see the selected standalone application open while the portal closes.

## Users and operating environment

The initial users are laboratory staff on Sykehuspartner-managed Windows computers.

The current environment has these constraints:

- Python is opened through Ivanti Workspace Control as **Python FELLES**.
- Installation cannot require administrator access.
- Python packages must be installed for the current Windows user with `pip --user`.
- Approved application releases are made available on the shared `K:` drive.
- A `.cmd` file opens Python FELLES and copies a Python command to the clipboard; the user pastes that command at the Python prompt.
- Workstations may not have direct or approved internet package access.
- Clinical data, patient identifiers, raw inputs, reports, and private validation data must remain outside Git and outside the eMolPat portal.

## Product boundary

### eMolPat owns

- One suite installer and one suite launcher.
- The portal user interface.
- The suite manifest and component version checks.
- The approved offline dependency lock and wheelhouse.
- Installation, update, repair, and health-check workflows.
- Application registration and launch handoff.
- Non-clinical technical logs for installation and launch failures.
- Release assembly of approved versions from the four source repositories.

### Individual applications own

- Analysis algorithms and workflow logic.
- Application-specific user interfaces.
- Input validation and clinical safeguards.
- Patient files, reports, evidence, screenshots, audit data, and settings.
- Application-specific tests and validation history.

## Chosen architecture

eMolPat will be a Python/PyQt6 desktop portal with a manifest-driven module registry. It will be distributed as one versioned suite containing the portal, approved builds of all four applications, exact dependencies, icons, and release metadata.

The applications remain separate Python packages within the suite. Their internals are not merged into the portal. A small, stable launch adapter may be added to an application repository when its official entry point cannot be invoked consistently.

```text
eMolPat Suite
├── Portal
├── HemaFrag Diagnostics package
├── IGH Merge package
├── VPM/HTS Tolkning package
├── MPN Tolkning package
├── Shared launch and health-check services
├── Exact compatible dependency lock
├── Offline wheelhouse
└── Suite manifest
```

Users experience this as one product. Repository and package boundaries remain separate so each clinical tool can continue to be developed and validated independently.

## Alternatives considered

### Command dashboard

A portal could copy the existing startup command and require the user to paste it into Python FELLES for every application launch. This closely matches the current process but does not provide the intended one-application experience. It remains a recovery route when managed-environment restrictions prevent automatic handoff.

### In-process plugin interface

The portal could import every application as a persistent plugin and embed its windows. This would create PyQt lifecycle and dependency coupling, require meaningful changes to validated applications, and weaken their independent boundaries. It is rejected for the initial suite.

### Web portal or GitHub Pages

A public web page cannot safely start local Python desktop applications and would be a poor fit for local clinical files. A public informational site may be added later, but it is not the operational eMolPat platform.

## Approved release model

The release path is:

```text
Separate GitHub repositories
        ↓
Approved, tested component revisions
        ↓
One assembled eMolPat suite release
        ↓
Reviewed release copied to K:
        ↓
Per-user installation through Python FELLES
```

All components are updated together. A user cannot independently update one application to a version that was not tested with the rest of the suite.

The suite follows semantic versioning. Its manifest records:

- Suite version
- Supported Python version range
- Exact portal and application versions
- Exact package filenames and checksums
- Exact dependency lock version
- Official application entry points
- Required-import health checks
- Application icons and user-facing descriptions

The approved `K:` release is immutable after publication. A corrected release receives a new suite version.

## Distribution layout

An assembled release has this conceptual structure:

```text
eMolPat-1.0.0/
├── manifest.json
├── install_emolpat.py
├── start_emolpat.py
├── packages/
│   ├── emolpat_portal
│   ├── hemafrag_diagnostics
│   ├── igh_merge
│   ├── vpm_tolkning
│   └── mpn_tolkning
├── wheelhouse/
├── requirements.lock
└── release-notes.txt
```

The implementation plan will define the precise build artifact format, but the distributed artifact must remain self-contained and install without downloading runtime packages from the internet.

## Installation and update behavior

Two `.cmd` launchers preserve the proven work-computer workflow:

- **Installer eMolPat.cmd** opens Python FELLES through Ivanti and copies the eMolPat installation command.
- **Start eMolPat.cmd** opens Python FELLES through Ivanti and copies the eMolPat startup command.

The suite installer performs these stages:

1. Verify the active Python FELLES version.
2. Verify access to the selected approved `K:` release.
3. Validate the manifest, checksums, package set, lock file, and wheelhouse.
4. Verify that the user-site location and per-user eMolPat data directory are writable.
5. Install the exact locked dependencies with `pip --user` and offline package lookup.
6. Install the portal and all four application packages for the current user.
7. Import every required module and verify every exact component version.
8. Record the installed suite version only after all checks pass.

An update runs the same complete workflow for a newer approved suite. It never silently downloads a dependency or installs only one application.

Python user-site installation is not inherently transactional. The installer therefore preflights the whole bundle before changing packages, records every stage, and keeps the previous suite's manifest and lock information. If an update fails, it attempts to reinstall the previous exact lock from its retained offline artifacts. The suite is marked **Repair required** unless the previous or new version passes complete verification.

## Portal interface

The approved portal uses a restrained clinical desktop design:

- eMolPat branding and suite version in a persistent sidebar.
- Navigation for Applications, System status, Suite update, and Help & support.
- Four application cards using the real icon from each application repository.
- Each card shows its description, component version, health state, and **Open application** action.
- A suite-level status clearly states whether all four applications are verified.
- Update and repair actions are suite-level, not per-application.

The initial user-facing language should be Norwegian. Internal identifiers and source code remain English unless an existing repository convention requires otherwise.

## Application handoff

The normal launch flow is:

```text
Open eMolPat
    → choose an application
    → verify the complete installed suite
    → begin the selected application's official startup
    → confirm startup succeeded
    → close eMolPat completely
```

The selected tool opens as its existing standalone desktop application. It is not embedded in the portal.

The launch coordinator first tries the supported direct handoff for Python FELLES. The technical implementation may dispatch to the selected official entry point after the portal window exits, allowing the portal and analysis application to use one managed Python process. The implementation must not keep two conflicting Qt application loops alive.

If the application cannot begin startup, eMolPat remains open or reopens its portal window and presents the failure. It closes only after the selected application's startup has been confirmed. A clipboard-and-paste command remains available as a documented recovery route if the managed environment blocks direct handoff.

After the selected application exits, eMolPat does not reopen automatically in version one.

## Health states

The portal presents one suite state derived from component checks:

- **Ready:** Installed version matches a complete verified suite.
- **Update available:** A newer approved complete suite is present on `K:`.
- **Repair required:** A package, version, import, checksum, or installation record is inconsistent.
- **Unavailable:** A required environment resource such as Python FELLES or the approved release path cannot be accessed.

The portal must never display **Ready** based only on a recorded version. It must confirm the manifest and required imports for all five packages.

## Error handling and recovery

User messages explain the failed stage in plain Norwegian and provide an actionable next step. Detailed exceptions, commands, package names, and return codes are written to a per-user technical log.

The portal and installer must:

- Never delete patient data, application settings, or generated reports.
- Never log patient identifiers, clinical input contents, credentials, or evidence-provider secrets.
- Never claim an install, update, repair, or launch succeeded until its verification passes.
- Preserve diagnostic evidence when a step fails.
- Distinguish an unavailable `K:` drive from a corrupt release or missing user package.
- Direct the user to support with the log location when automatic recovery is not safe.

## Settings and data locations

eMolPat stores only non-clinical per-user state, including:

- Installed suite version and verification result
- Portal preferences
- Technical logs
- Retained manifest and lock metadata needed for repair

The portal does not centralize or relocate the four applications' existing data directories. Each module continues to own its settings and outputs.

## Security and privacy boundaries

### Always

- Install only a complete approved suite from the configured shared release path.
- Verify checksums and exact component versions.
- Use offline dependencies from the approved wheelhouse.
- Keep clinical data outside eMolPat and Git.
- Run the full verification gates before publishing a suite.

### Require explicit approval

- Change the supported Python FELLES version.
- Add, remove, or replace an analysis module.
- Change an application's official launch entry point.
- Change the shared release path or update trust model.
- Add internet access, telemetry, central accounts, or a server component.

### Never

- Install unpinned dependencies from the internet during a work-computer installation.
- Mix application versions from different suite releases.
- Upload patient data or identifiers from the portal.
- Modify clinical algorithms as part of portal integration without that application's separate validation process.
- Store passwords or provider credentials in the suite manifest or logs.

## Testing strategy

### Unit tests

Unit tests cover manifest parsing, checksum validation, version comparison, health-state derivation, command construction, application registration, and translation of technical failures into safe user messages.

### Integration tests

Integration tests cover clean installation, complete update, repair, missing shared drive, missing wheel, corrupt checksum, incompatible dependency, incomplete user-site installation, and launch handoff through harmless test entry points.

### Component tests

Every suite build runs the existing automated tests from HemaFrag Diagnostics, IGH Merge, VPM/HTS Tolkning, and MPN Tolkning against the exact revisions selected for the release.

### Manual managed-workstation validation

Before publication to the approved `K:` path, the release is tested with a clean Windows user profile for:

- Ivanti/Python FELLES installer flow
- `pip --user` installation without administrator rights
- Offline wheelhouse installation
- Portal rendering and real application icons
- Health, update, and repair states
- Successful handoff to each real application
- Portal closure after successful application startup
- Useful recovery when startup fails
- Continued isolation of patient files and module settings

## Proposed development commands

The implementation will provide these stable commands from the repository root:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m emolpat
python scripts/build_suite.py --version 1.0.0 --output dist
```

Work-computer installation uses the approved `install_emolpat.py` script through Python FELLES rather than the development commands.

## Proposed project structure

```text
src/emolpat/          Portal, manifest, health, install, and launch code
tests/                Unit and integration tests
scripts/              Suite assembly and icon/build utilities
packaging/            Python FELLES and Windows launcher templates
docs/                 Design, operations, validation, and release documentation
```

Modules should have one clear responsibility and communicate through typed data structures. User-facing text is separated from state and installation logic so it can be tested and translated without changing behavior.

## Release gates

An eMolPat suite release is publishable only when:

1. Portal tests and static checks pass.
2. All four application test suites pass at the selected revisions.
3. Exact dependency resolution and all required-import smoke tests pass.
4. The assembled artifact passes manifest and checksum verification.
5. Installation, update, repair, and launch flows pass on a clean managed-workstation profile.
6. Laboratory review is documented.
7. The immutable approved release is copied to the controlled `K:` location.

## Success criteria

- One approved artifact contains the portal and all four applications.
- One per-user installation workflow installs the complete suite through Python FELLES.
- No administrator access or runtime internet download is required.
- The portal accurately reports the health of the complete suite.
- Each application can be opened from its card using its real icon and official entry point.
- The portal closes after successful startup and remains available when startup fails.
- Updates replace all components with one tested suite version.
- Failure states produce actionable Norwegian guidance and non-clinical technical logs.
- Existing application code, data ownership, and validation boundaries remain intact.
- The suite layout can later serve as the input to a Sykehuspartner-managed Windows package.

## Out of scope for version one

- Rewriting or visually embedding the four applications.
- Running multiple analysis applications from one portal session.
- Automatically reopening eMolPat when an application exits.
- Central user accounts, a server, telemetry, or cloud analysis.
- Direct GitHub updates on laboratory workstations.
- Additional modules beyond the initial four.
- A public operational GitHub Pages application.
