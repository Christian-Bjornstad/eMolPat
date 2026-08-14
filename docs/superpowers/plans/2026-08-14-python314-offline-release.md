# Python 3.14 Offline Test Release Implementation Plan

> Approved design: `docs/superpowers/specs/2026-08-14-python314-offline-release-design.md`

**Goal:** Publish an immutable eMolPat prerelease that installs the portal and all five bundled applications offline into the Python FELLES 3.14 user site and starts without Ivanti.

**Release:** `v1.0.3-python314-test`

## 1. Lock the Python 3.14 runtime contract

- Add failing tests proving the installer and starter accept Python 3.14 and reject unsupported minor versions.
- Change the bootstrap guards from Python 3.12 to Python 3.14.
- Change the bundled suite manifest and test fixture to `>=3.14,<3.15`.
- Keep the developer package metadata broad enough to run repository tests under both Python 3.12 and 3.14.
- Run the focused bootstrap and manifest tests.

## 2. Make the offline builder target explicit and deterministic

- Add a CPython target structure containing `python_version`, `abi`, `platform`, and `python_requires`.
- Pass the target into dependency download and manifest assembly instead of hard-coding `312` / `cp312`.
- Add an exact Python 3.14 dependency input derived from the already pinned dependency graph.
- Download with `--platform win_amd64 --python-version 314 --implementation cp --abi cp314 --only-binary=:all: --no-deps`.
- Continue generating the shipped `requirements.lock` from the actual wheel filenames and SHA-256 values.
- Add tests that assert the CPython 3.14 pip arguments, manifest range, and repeatable lock generation.
- Run the focused builder tests.

## 3. Include the Ivanti-free support launchers

- Copy the manual installer, manual starter, diagnostic starter, clean-import starter, and diagnostic Python helper into the release root.
- Keep the ordinary installer/starter files for managed deployment later.
- Add archive assembly tests proving every launcher and helper is present.
- Run the release-assembly tests.

## 4. Verify application compatibility under Python 3.14

- Create an isolated Python 3.14 virtual environment outside the repository.
- Install the eMolPat development dependencies and run the complete portal test suite.
- Install each bundled component from its pinned source checkout and run its own tests under Python 3.14.
- Resolve any genuine 3.14 incompatibility with a regression test before changing implementation code.

## 5. Build and test the complete offline package

- Build `eMolPat-1.0.3-python314-test` from the five pinned component revisions.
- Verify source hashes, wheel hashes, manifest hashes, dependency lock hashes, archive paths, and archive checksum.
- Set a temporary `PYTHONUSERBASE`, install only from the packaged wheels with Python 3.14, and import:
  - `emolpat`
  - `hemafrag`
  - `igh_merge`
  - `hts_tolkning`
  - `mpn_tolkning`
- Start the portal through the packaged diagnostic/manual path far enough to prove module discovery and bootstrap success without touching the real Windows user site.
- Run the complete Python 3.12 repository suite once more as a developer-regression check.

## 6. Document, review, and publish the prerelease

- Update release notes/readme with the Python FELLES 3.14 test instructions and clear prerelease status.
- Review the final diff for accidental credentials, local paths, mutable downloads, or missing artifacts.
- Commit and push the branch `codex/python-felles-diagnostics`.
- Create annotated tag `v1.0.3-python314-test` on the verified commit.
- Publish a GitHub **prerelease** containing:
  - `eMolPat-1.0.3-python314-test-windows.zip`
  - `eMolPat-1.0.3-python314-test-windows.zip.sha256`
- Download the published assets, verify the checksum, and inspect the archive contents.
- Do not create a pull request and do not merge to `main`.

## Work-computer acceptance test

1. Download the prerelease ZIP and extract it to a writable folder.
2. Open Python FELLES 3.14.
3. Run `Installer eMolPat - Manuell FELLES.cmd` once.
4. Run `Start eMolPat - Manuell FELLES.cmd`.
5. Confirm the portal opens and each application can be launched.
6. If startup fails, run `Start eMolPat - Diagnose.cmd` and return the displayed diagnostic text.
