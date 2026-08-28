# Changelog

## [1.2.1] - 2026-08-28

- Updated LVMS Statistikk to 2.0.1 at immutable commit
  `72294225760b73d803edc66baaed8a3c3cb866f0`.
- Reduced the Windows archive to the two supported operator CMD launchers.
- Moved the verified offline payload under `suite` so local operator files next
  to the launchers no longer trigger a false preflight integrity failure.
- Removed the obsolete manual and diagnostic launchers from the release source.

## [1.2.0] - 2026-08-24

- Renamed the visible STAT navigation tab to Statistikk.
- Added MolKey 0.2.0 as the sixth standalone application under its own MolKey
  tab and pinned `molkey.__main__:main` to an immutable source commit.
- Expanded deterministic offline assembly to the portal plus six component
  wheels and added MolKey's compatible `platformdirs`, `portalocker`, and
  Windows `pywin32` dependencies to the Python 3.14 lock.
- Kept the MolKey registry, pseudonym mappings, secure-drive database, and
  settings entirely inside MolKey.
- Rebuilt the suite with Myolid Tolkning / Archer Prosess pinned to commit
  `2b0a29de99bc89c2c2a8417679746d634d670847`.

## [1.1.0] - 2026-08-23

- Added LVMS-STAT 2.0.0 as the fifth application under the STAT unit.
- Pinned the zero-argument `lvms_stat.portal:main` launcher to an immutable
  source commit.
- Expanded deterministic offline assembly to the portal plus five component
  wheels while preserving the existing separate-process lifecycle.
- Kept LVMS authentication, settings, report retrieval, and file storage inside
  LVMS-STAT.

## [1.0.7-test] - 2026-08-23

- Kept the eMolPat portal open and responsive while analysis applications run
  in separate Python FELLES processes.
- Added Hemato, Solide, and STAT unit navigation with an initial LVMS-STAT
  preview.
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

## Initial development

- Fixed Python FELLES prompt commands so installation and startup no longer close the interpreter.
- Added self-contained Windows release ZIPs with all five applications and exact offline dependencies.
- Replaced unconditional readiness with verified per-user package and import health.
- Added offline install and repair actions plus tag-based GitHub Release publication.
- Added the Norwegian eMolPat portal with canonical icons for all five applications.
- Added separate-process standalone application launch while the portal remains open.
- Added atomic offline per-user installation, verification, repair, and retained-version rollback.
- Added redacted rotating technical logs and safe startup-failure recovery.
- Added deterministic six-wheel release assembly and Python FELLES/Ivanti launchers.
