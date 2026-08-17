# Atomic update recovery design

## Problem

The work computer can install and open eMolPat, but the installed portal reports
an update immediately. All releases currently ship `emolpat==0.1.0`, so pip
skips a newer same-version wheel. The wheel also contains suite manifest
`1.0.0`, while the external release record is newer. Finally, successful UI
installation leaves the last progress text visible and keeps the old Python
process alive.

## Approved correction

- Publish a new immutable prerelease `v1.0.4-python314-test`.
- Set the eMolPat distribution version to `0.1.1` and its bundled manifest to
  `1.0.4-python314-test`.
- Add `--force-reinstall` to the local five-wheel component installation so
  same-version application builds are replaced atomically.
- On successful portal update, show a completion message and close eMolPat.
  The user restarts it so Python loads only the newly installed code.
- Retain the existing offline, per-user, hash-verified installation model.

## Verification

Regression tests must prove forced component replacement, matching bundled
suite identity, and successful UI shutdown. The complete Python 3.12 and 3.14
test gates, offline build verification, and a clean temporary user-site install
must pass before publishing the new prerelease.
