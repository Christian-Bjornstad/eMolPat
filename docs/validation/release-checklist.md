# eMolPat release checklist

Release version: __________  Date: __________  Reviewer: __________

## Immutable inputs

- [ ] eMolPat commit recorded: ________________________________
- [ ] HemaFrag commit recorded: ______________________________
- [ ] IGH Merge commit recorded: ______________________________
- [ ] VPM/HTS commit recorded: ________________________________
- [ ] MPN commit recorded: ___________________________________
- [ ] `requirements.lock` SHA-256 recorded: ____________________
- [ ] Source trees were clean at the approved commits.

## Automated evidence

- [ ] eMolPat tests and Ruff pass.
- [ ] HemaFrag: _____ passed / _____ skipped.
- [ ] IGH Merge: _____ passed / _____ skipped.
- [ ] VPM/HTS: _____ passed / _____ skipped.
- [ ] MPN: _____ passed / _____ skipped.
- [ ] `scripts/verify_suite.py` passes the assembled folder.
- [ ] Missing wheel and corrupt-checksum tests fail safely.

## Clean managed workstation

- [ ] Installer runs through Ivanti/Python FELLES without admin rights.
- [ ] Installation is offline and uses the current user site.
- [ ] Portal renders at 1024×768 with Norwegian text and four correct icons.
- [ ] Ready, update, repair, and unavailable states are verified.
- [ ] Each real module opens and the portal closes.
- [ ] A failed import reopens the portal with a safe message.
- [ ] Logs contain no patient identifiers, clinical paths, credentials, or inputs.
- [ ] No patient files, reports, or application settings were changed.

Laboratory approval: __________________  Date: __________

Sykehuspartner/package approval: __________________  Date: __________
