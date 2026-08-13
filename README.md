# eMolPat

eMolPat is one local Windows application suite for molecular pathology. Its Norwegian PyQt6 portal opens four independently validated desktop tools without rewriting their analytical workflows:

- HemaFrag Diagnostics
- IGH Merge
- VPM / HTS Tolkning
- MPN Tolkning

The portal closes before the selected standalone app starts. Installation and updates are atomic: one approved offline release contains all five application wheels, exact Windows dependencies, hashes, launchers, and recovery metadata. Workstation installation uses `pip --user` through Ivanti/Python FELLES and requires no administrator access.

## Clinical boundary

eMolPat stores only suite status and redacted technical logs. It does not read, move, centralize, log, or upload patient files, reports, clinical inputs, credentials, or application settings. Each analysis application retains ownership of its own validated workflow and data.

## Development

```powershell
py -3.12 -m pip install -e ".[dev]"
$env:QT_QPA_PLATFORM="offscreen"
py -3.12 -m pytest -q
py -3.12 -m ruff check .
```

Build and verify a release using [the build guide](docs/operations/build-release.md). Workstation setup is described in [Python FELLES](docs/operations/python-felles.md), with a separate [repair procedure](docs/operations/repair.md) and [release checklist](docs/validation/release-checklist.md).

Architecture and safety decisions are documented in [the approved suite design](docs/superpowers/specs/2026-08-13-emolpat-suite-design.md).
