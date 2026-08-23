# Changelog

## [1.0.7-test] - 2026-08-23

- Kept the eMolPat portal open and responsive while analysis applications run
  in separate Python FELLES processes.
- Added Hemato, Solide, and STAT unit navigation; LVMS-STAT is shown as a
  disabled preview and is not part of installation or health verification.
- Added explicit running, retry, and ready states for each application card.
- Replaced legacy status pages with a compact clinical-light status dialog.
- Blocked suite update and repair while an analysis application is running.
- Enforced one deterministic suite version across manifest, build, archive,
  checksum, and release metadata.

## [1.0.4-python314-test] - 2026-08-14

- Fixed updates that skipped same-version application wheels.
- Aligned the installed portal manifest with the suite release version.
- Added an explicit successful-update message and automatic portal shutdown so
  the restarted process loads only the new code.

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
- Added separate-process standalone application launch while the portal remains open.
- Added atomic offline per-user installation, verification, repair, and retained-version rollback.
- Added redacted rotating technical logs and safe startup-failure recovery.
- Added deterministic five-wheel release assembly and Python FELLES/Ivanti launchers.
