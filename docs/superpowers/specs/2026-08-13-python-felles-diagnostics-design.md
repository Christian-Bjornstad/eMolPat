# Python FELLES startup diagnostics

## Goal

Provide a small test-only package that reveals why eMolPat cannot start in the
managed Python FELLES environment and offers one safe stale-import workaround.
The work stays on `codex/python-felles-diagnostics` until it is confirmed on the
work computer.

## Manual Python FELLES launchers

The package contains four replacement launchers for an extracted eMolPat 1.0.2
folder. None checks for, starts, or depends on Ivanti:

1. `Installer eMolPat - Manuell FELLES.cmd` copies the existing complete offline
   installation command.
2. `Start eMolPat - Manuell FELLES.cmd` copies the normal portal command.
3. `Start eMolPat - Diagnose.cmd` copies a command that prints the Python
   executable and version, user-site directory, eMolPat module location, full
   exception traceback, and diagnostic-log location.
4. `Start eMolPat - Clean import.cmd` copies the diagnostic command after
   selecting stale-module cleanup and import-cache invalidation.

Each CMD file only copies its command and then tells the user to open Python
FELLES through the workstation's normal approved method, paste with `Ctrl+V`,
and press Enter. The commands run without prompt-level `SystemExit`; diagnostic
output avoids environment variables and patient data and is also written to
`%LOCALAPPDATA%\eMolPat\logs\startup-diagnostic.log`.

## Offline application bundle

The complete eMolPat release already contains eMolPat, HemaFrag, IGH Merge,
VPM/HTS Tolkning, MPN Tolkning, and their Windows dependencies. The manual
launcher fix does not fetch application code from GitHub and does not require
network access. `Installer eMolPat - Manuell FELLES.cmd` continues to install
the complete release with `pip --user` from the extracted local folder.

## Packaging and test flow

The branch will include a ZIP containing only the four CMD files and diagnostic
Python helper. The files are copied into the already-extracted v1.0.2 folder.
The installer launcher deliberately invokes the existing bundled installer;
the other files do not modify installed packages. Automated tests cover
clipboard command construction, absence of Ivanti references, safe diagnostic
content, traceback visibility, and stale-module cleanup.

No pull request, merge, tag, or public release is created until the work-computer
result identifies and confirms the real fix.
