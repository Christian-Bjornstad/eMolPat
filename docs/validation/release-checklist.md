# eMolPat release checklist

Release version: __________  Date: __________  Reviewer: __________

## Immutable inputs

- [ ] eMolPat commit recorded: ________________________________
- [ ] HemaFrag commit recorded: ______________________________
- [ ] IGH Merge commit recorded: ______________________________
- [ ] VPM/HTS commit recorded: ________________________________
- [ ] MPN commit recorded: ___________________________________
- [ ] LVMS-STAT commit recorded: ______________________________
- [ ] MolKey commit recorded: _________________________________
- [ ] `requirements.lock` SHA-256 recorded: ____________________
- [ ] Source trees were clean at the approved commits.

## Automated evidence

- [ ] eMolPat tests and Ruff pass.
- [ ] HemaFrag: _____ passed / _____ skipped.
- [ ] IGH Merge: _____ passed / _____ skipped.
- [ ] VPM/HTS: _____ passed / _____ skipped.
- [ ] MPN: _____ passed / _____ skipped.
- [ ] LVMS-STAT: _____ passed / _____ subtests.
- [ ] MolKey: _____ passed / _____ skipped.
- [ ] `scripts/verify_suite.py` passes the assembled folder.
- [ ] Missing wheel and corrupt-checksum tests fail safely.
- [ ] Release ZIP contains one safe top-level directory, exactly two CMD
      launchers, and the verified payload under `suite`.
- [ ] Downloaded ZIP matches the published SHA-256 sidecar.
- [ ] GitHub Release contains only the Windows ZIP and checksum assets.

## Clean managed workstation

- [ ] Installer runs through Ivanti/Python FELLES without admin rights.
- [ ] Installation is offline and uses the current user site.
- [ ] Portal renders at 1024×768 with Norwegian text and six correct icons.
- [ ] Ready, update, repair, and unavailable states are verified.
- [ ] Each real module opens in a separate process and the portal remains open.
- [ ] HemaFrag Diagnostics opens from eMolPat.
- [ ] IGH Merge opens from eMolPat.
- [ ] VPM / HTS Tolkning opens from eMolPat.
- [ ] MPN Tolkning opens from eMolPat.
- [ ] LVMS Statistikk opens from Statistikk without arguments.
- [ ] LVMS Statistikk uses its existing Local AppData setup and K-disk paths.
- [ ] MolKey opens from its own MolKey tab without arguments.
- [ ] MolKey uses its configured secure-drive registry and existing settings.
- [ ] A failed import reopens the portal with a safe message.
- [ ] Logs contain no patient identifiers, clinical paths, credentials, or inputs.
- [ ] No patient files, reports, or application settings were changed.

Laboratory approval: __________________  Date: __________

Sykehuspartner/package approval: __________________  Date: __________
