# Changelog

## [1.0.3-python314-test] - 2026-08-14

- Added a complete offline Windows bundle targeting CPython 3.14 on `win_amd64`.
- Included HemaFrag Diagnostics, IGH Merge, VPM/HTS Tolkning, MPN Tolkning,
  eMolPat, and all 79 exact dependency wheels in one archive.
- Added Ivanti-free manual installation, startup, clean-import, and diagnostic
  launchers to the verified release manifest.
- Fixed the Python FELLES bootstrap to activate the Python 3.14 per-user site.

## Unreleased

- Fixed Python FELLES prompt commands so installation and startup no longer close the interpreter.
- Added self-contained Windows release ZIPs with all four applications and exact offline dependencies.
- Replaced unconditional readiness with verified per-user package and import health.
- Added offline install and repair actions plus tag-based GitHub Release publication.
- Added the Norwegian eMolPat portal with canonical icons for all four applications.
- Added same-process standalone application handoff after the portal fully closes.
- Added atomic offline per-user installation, verification, repair, and retained-version rollback.
- Added redacted rotating technical logs and safe startup-failure recovery.
- Added deterministic five-wheel release assembly and Python FELLES/Ivanti launchers.
