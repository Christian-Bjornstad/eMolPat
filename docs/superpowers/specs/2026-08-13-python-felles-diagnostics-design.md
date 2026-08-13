# Python FELLES startup diagnostics

## Goal

Provide a small test-only package that reveals why eMolPat cannot start in the
managed Python FELLES environment and offers one safe stale-import workaround.
The work stays on `codex/python-felles-diagnostics` until it is confirmed on the
work computer.

## Test launchers

The package contains two replacement launchers for an extracted eMolPat 1.0.2
folder:

1. `Start eMolPat - Diagnose.cmd` opens Python FELLES and copies a command that
   prints the Python executable and version, user-site directory, eMolPat module
   location, full exception traceback, and diagnostic-log location.
2. `Start eMolPat - Clean import.cmd` does the same after removing already-loaded
   `emolpat` modules and invalidating Python's import caches.

Both commands run without `SystemExit`, keep Python FELLES open, and avoid
printing environment variables or patient data. Diagnostics are also written to
`%LOCALAPPDATA%\eMolPat\logs\startup-diagnostic.log`.

## Packaging and test flow

The branch will include a ZIP containing only the two CMD files and their Python
helpers. The files are copied into the already-extracted v1.0.2 folder; they do
not reinstall or modify any installed package. Automated tests cover clipboard
command construction, safe diagnostic content, traceback visibility, and stale
module cleanup.

No pull request, merge, tag, or public release is created until the work-computer
result identifies and confirms the real fix.
