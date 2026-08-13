# eMolPat Self-Contained Offline Release Design

## Goal

Publish one versioned eMolPat ZIP that installs the portal, all four analysis applications, and their exact Windows dependencies for the current user. After installation, every verified application is immediately available from the portal without downloading anything else.

## User experience

The supported download is a GitHub **Release asset** named `eMolPat-<version>-windows.zip`, not GitHub's source-code ZIP.

1. The user downloads and extracts the release asset.
2. The user runs `Installer eMolPat.cmd`.
3. The launcher opens the approved Python FELLES environment and starts the bundled installer.
4. The installer validates the complete release, installs dependencies and all five application wheels with `pip --user --no-index`, and verifies exact versions and imports.
5. The installer reports success only after all four analysis applications and eMolPat pass verification.
6. The user runs `Start eMolPat.cmd`. Every verified application can be opened immediately; no internet connection is required during installation or use.

The README and GitHub release notes link directly to the release asset and clearly distinguish it from `Code > Download ZIP`.

## Release contents

```text
eMolPat-<version>-windows/
├── manifest.json
├── requirements.lock
├── packages/
│   ├── emolpat-<version>-py3-none-any.whl
│   ├── hemafrag_diagnostics-*.whl
│   ├── igh_merge-*.whl
│   ├── archer_prosess-*.whl
│   └── mpn_tolkning-*.whl
├── wheelhouse/                 Exact Windows dependency wheels
├── install_emolpat.py
├── start_emolpat.py
├── Installer eMolPat.cmd
└── Start eMolPat.cmd
```

The archive is self-contained. Installation uses only these files, never a package index or a component repository. Every file is covered by the release manifest and a SHA-256 digest.

## Build and publication

The existing deterministic suite builder remains the single assembly path. A release workflow runs only for an explicit version tag such as `v1.0.0` and performs these steps:

1. Check out eMolPat and the four public component repositories at the exact commits in `release/components.json`.
2. Build the five application wheels.
3. collect the exact supported Windows/Python FELLES dependency wheels from the authoritative hash lock;
4. validate the dependency matrix and release manifest;
5. run all eMolPat automated tests and the release verifier;
6. create `eMolPat-<version>-windows.zip` with a single top-level release directory;
7. publish the ZIP and its SHA-256 checksum as GitHub Release assets.

The build workflow is allowed to access GitHub and the Python package index. The downloaded release and the laboratory workstation installer do not.

The first supported workstation target is 64-bit Windows with Python FELLES 3.12. Support for another Python minor version requires a separately validated dependency wheel set and release asset; the installer must reject unsupported interpreters before changing the user environment.

## Installation contract

`install_emolpat.py` bootstraps eMolPat from the bundled portal and packaging wheels, then calls the existing transactional installer. The installer:

- rejects missing, unexpected, or hash-mismatched release files;
- executes pip through the active Python FELLES interpreter;
- installs with `--user`, `--no-index`, and the local `wheelhouse`;
- installs dependency versions from `requirements.lock` with `--require-hashes`;
- installs all five application wheels with `--no-deps`;
- verifies each declared distribution version and import name;
- writes the per-user install record only after complete verification;
- retains the verified release inputs for repair and rollback;
- leaves the previous verified install record intact if an update fails.

An installation is atomic at the suite-record level: partial installation is never presented as ready.

## Portal health and repair behavior

The current unconditional `READY` state is removed. Portal startup reads the per-user install record and observes installed distribution versions and imports, then calls the existing pure `evaluate_health` function.

- **Ready:** the recorded component set, exact versions, and imports all pass. Application launch buttons are enabled.
- **Repair required:** a record exists but one or more packages, versions, or imports do not match. Launch buttons are disabled and the portal offers `Reparer installasjon` when a retained or adjacent verified release is available.
- **Not installed:** no verified record exists. Launch buttons are disabled and the portal offers `Installer programmer` when started from an extracted release directory.
- **Unavailable:** required installation inputs or the Python environment cannot be accessed. The portal gives concise Norwegian guidance and a redacted technical log location.

The portal never displays `Klar til bruk` based only on its bundled manifest. A failed launch returns to the portal, but installation state is corrected at startup rather than discovered only after clicking an application.

## Installer access from the portal

The primary supported installation remains `Installer eMolPat.cmd`, because a portal wheel cannot install missing applications before the portal itself exists. When eMolPat is started from an extracted release directory or a retained verified release is available, the System Status page runs the same installation service through an `Installer programmer` or `Reparer installasjon` action.

The UI displays installation stages, keeps the window responsive, prevents concurrent install or launch actions, and requires a successful post-install health evaluation before enabling application cards. The implementation must not duplicate pip or integrity logic in the UI.

## Failure handling and diagnostics

Failures are reported by stage: release validation, dependency installation, application installation, verification, record creation, or rollback. User-facing messages remain concise and Norwegian. Logs contain only application identifiers, error codes, stages, and redacted paths; pip command lines, patient data, credentials, and clinical files are not logged.

The generic `kunne ikke åpne` message remains a last-resort handoff boundary. Normal missing-package cases are prevented by accurate health evaluation and disabled launch buttons.

## Trust boundaries

- GitHub tags and `release/components.json` select source commits at build time.
- The release manifest and published checksum protect the transfer and installation boundary.
- The installer trusts only files inside the extracted, verified release root.
- Archive creation rejects unsafe or ambiguous paths; extraction instructions require a normal local directory.
- No arbitrary repository URL, package name, or shell command is accepted from the portal UI.
- Installation remains per-user and requires no administrator privileges.

## Validation

Automated coverage must prove:

- a complete release includes exactly five application wheels, launchers, dependency wheels, lock, and manifest;
- the ZIP contains one safe top-level directory and matches the published checksum;
- offline pip commands use `--user`, `--no-index`, `--require-hashes`, and only verified local paths;
- a missing install record produces a non-ready portal;
- missing, wrong-version, or unimportable applications disable all launch actions;
- complete exact installation produces `Ready` and enables all four applications;
- install, repair, rollback, and stage-specific failure behavior remain deterministic;
- portal lifecycle still closes eMolPat before starting a standalone application;
- the release workflow builds only from explicit version tags and uploads the verified ZIP/checksum;
- Windows CI passes on the supported Python FELLES version.

Before publication, the final asset must also be installed on a clean managed workstation and all four applications must be opened from eMolPat through Python FELLES.

## Out of scope

- Downloading applications or Python dependencies from the portal at runtime.
- Installing directly from Git repositories on laboratory workstations.
- Administrator-wide or machine-wide installation.
- Rewriting or embedding the four applications into the portal process.
- Supporting unvalidated Python, Windows, or processor combinations in the same asset.
