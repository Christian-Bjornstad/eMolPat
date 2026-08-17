# Python 3.14 offline test release

## Goal

Build a complete eMolPat test release for the managed Python FELLES runtime,
which the workstation diagnostic identified as CPython 3.14.6. The release must
install eMolPat and all four analysis applications offline into the current
user's Python 3.14 user-site directory.

Work remains on `codex/python-felles-diagnostics`. No pull request or merge is
created until the package has been tested successfully on the work computer.

## Runtime and package contract

- The suite manifest accepts `Python >=3.14,<3.15` and rejects other minor
  versions.
- Both bootstrap scripts accept Python 3.14 and activate
  `%APPDATA%\Python\Python314\site-packages` before imports.
- The release wheelhouse contains the complete resolved dependency graph for
  CPython 3.14 on 64-bit Windows. Every dependency is pinned with its exact
  version and SHA-256 hash.
- The five application wheels remain the pinned eMolPat, HemaFrag Diagnostics,
  IGH Merge, VPM/HTS Tolkning, and MPN Tolkning source revisions already
  approved in `release/components.json`.
- Installation uses only files in the extracted release with `pip --user`,
  `--no-index`, `--require-hashes`, and no GitHub or PyPI access.

## Build and verification

The release builder takes an explicit Python target instead of hard-coding
CPython 3.12. For this test release it downloads only `win_amd64` wheels
compatible with CPython 3.14 and generates the lock file from the exact wheels
that are bundled.

Verification includes:

1. Existing eMolPat tests under Python 3.12 to protect current development
   compatibility.
2. The complete eMolPat test suite under the available local CPython 3.14
   runtime.
3. All four pinned component test suites under CPython 3.14.
4. A clean temporary Python 3.14 user-base installation from the assembled
   offline directory, followed by imports of all five installed distributions.
5. Archive integrity, checksum, one top-level directory, five application
   wheels, and only CPython 3.14-compatible platform wheels.

## Workstation launch flow

The archive includes the Ivanti-free manual installer and starter. Each CMD file
only copies its local Python command. The user opens Python FELLES through the
workstation's normal approved method, pastes with `Ctrl+V`, and presses Enter.
Startup failures remain visible and are written to the redacted diagnostic log.

## Distribution

The verified archive is published from the test branch as a GitHub prerelease
tagged `v1.0.3-python314-test`. It contains only:

- `eMolPat-1.0.3-python314-test-windows.zip`
- `eMolPat-1.0.3-python314-test-windows.zip.sha256`

The prerelease is explicitly non-production and is not created through a pull
request. The prerelease tag remains immutable after publication. If workstation
testing finds another issue, a new test version is created rather than replacing
the existing asset.

## Success criteria

On the work computer, the manual installer reports successful installation and
verification under Python 3.14.6. The manual starter then opens the eMolPat
portal, and each of the four application cards can launch its bundled program.
