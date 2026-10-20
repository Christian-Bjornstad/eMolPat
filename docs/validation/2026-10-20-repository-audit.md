# Portal component audit — 20 October 2026

Initial read-only GitHub API inspection through authenticated `gh`, with isolated shallow
source checkouts. Repository branches and checks were captured on 20 October
2026. This records source state and validation evidence; it does not certify
clinical interpretation results. Follow-up test fixes are identified below.

## Source of truth

The portal's seven requested applications are the repositories below. MolStat
replaces the previous LVMS-STAT component; Solide is added. Repository defaults
are used explicitly rather than assuming that every repository has `main`.

| Repository | Default branch | Immutable commit | Distribution / version |
| --- | --- | --- | --- |
| [MolStat](https://github.com/Christian-Bjornstad/MolStat) | `main` | `8bc513be5c07d5db4517cdbd3afb5e5e8297f9d1` | `molstat` / `0.1.0` |
| [HemaFrag-Diagnostics](https://github.com/Christian-Bjornstad/HemaFrag-Diagnostics) | `main` | `cd4ae389dc27d042a0169397061f6f8745a73e12` | `hemafrag-diagnostics` / `1.2.0` |
| [Archer-prosess](https://github.com/Christian-Bjornstad/Archer-prosess) | `main` | `249b82345761ff2facf78e35b3da1571f8af4195` | `archer-prosess` / `0.1.0` |
| [MolKey](https://github.com/Christian-Bjornstad/MolKey) | `main` | `2124e0874d651f7242a50e6e1fcf2055160a9dbb` | `molkey` / `0.2.0` |
| [solide](https://github.com/Christian-Bjornstad/solide) | `main` | `4ff2b04d387a21896ec3bbd05f40e641de645f2c` | `solide` / `0.8.1` |
| [IGH](https://github.com/Christian-Bjornstad/IGH) | `codex/igh-merge-gui` | `4af58a7bfb8317e91a00abc71b5d53022620941f` | `igh-merge` / `0.2.0` |
| [MPN-Tolkning](https://github.com/Christian-Bjornstad/MPN-Tolkning) | `main` | `5b79595716fc846a75e3a642c3849c6ac545dfde` | `mpn-tolkning` / `0.1.0` |

All seven have **zero open pull requests**. IGH has no `main` branch. MolStat,
MolKey, Solide, IGH and MPN-Tolkning have no branch with commits ahead of their
default branch.

HemaFrag has eight divergent branches; Archer has three. Commit ancestry alone
does not establish that their behavior is absent from the default branch:
changes may have been cherry-picked, squashed, or superseded. The audit does not
automatically merge these branches.

| Repository | Divergent branch | Ahead / behind default |
| --- | --- | --- |
| HemaFrag | `codex/deterministic-ci-tests` | 2 / 96 |
| HemaFrag | `codex-clonality-interp-v1-2026-06-28` | 2 / 267 |
| HemaFrag | `feat/ml-learning-tab-2026-07-12` | 31 / 236 |
| HemaFrag | `graphify-knowledge-graph` | 5 / 95 |
| HemaFrag | `improvement/clonality-annotation-panel-2026-07-11-v2` | 25 / 260 |
| HemaFrag | `improvement/clonality-annotation-panel-2026-07-11` | 1 / 236 |
| HemaFrag | `improvement/flt3-npm1-ref-zoom-baseline-2026-07-14` | 34 / 236 |
| HemaFrag | `ml-clonality-interpretation-2026-06-27` | 24 / 260 |
| Archer | `diagnostics/citrix-edge-connection` | 1 / 76 |
| Archer | `feat/historical-evidence-backup` | 4 / 4 |
| Archer | `feat/workstation-improvements-2026-10-07` | 5 / 4 |

## Previous portal pins

The starting portal contract on `origin/master` (`64c8a24`) contained six
applications, including LVMS-STAT. Every retained source pin was older than the
selected current default:

| Component | Previous pin | Default relative to previous pin |
| --- | --- | --- |
| HemaFrag | `f4eb9c32cd71b3f2996d2bf24a6ec43dcb4cfef0` | 96 commits ahead, 2 behind |
| IGH | `e54f598c0666ad3453df6dee06d55eb2e5f8fe1f` | 23 ahead |
| Archer | `2b0a29de99bc89c2c2a8417679746d634d670847` | 119 ahead |
| MPN | `a8c6e758f50d83eeb59e54917d64c61cf046229b` | 2 ahead |
| MolKey | `a01b5df13fc05bb0d2013d730405be85f25addf4` | 9 ahead |

The two HemaFrag-only commits change three tests: a simulated CPU count, Qt test
cleanup, and Windows file identity comparison. They are not application changes.
The updated source pin follows the current default; upstream test failures are
reported separately rather than silently modifying the component source.

## GitHub checks at the selected commits

| Repository | Evidence |
| --- | --- |
| HemaFrag | [CI run](https://github.com/Christian-Bjornstad/HemaFrag-Diagnostics/actions/runs/39386942686): Windows Python 3.12 and 3.14 pass; Rust checks pass; macOS Python 3.12 fails one GUI selection test. |
| IGH | [Tests](https://github.com/Christian-Bjornstad/IGH/actions/runs/39386746998) pass on Windows Python 3.11. |
| MPN | [Tests](https://github.com/Christian-Bjornstad/MPN-Tolkning/actions/runs/39396148293) pass on Windows Python 3.12; [Pages deployment](https://github.com/Christian-Bjornstad/MPN-Tolkning/actions/runs/39396148292) also passes. |
| MolStat, Archer, MolKey, Solide | No GitHub workflow or check results on their selected default commits. |

The HemaFrag macOS failure is
`tests/test_input_folder_selection.py::test_folder_dialog_selects_multiple_folders_with_shift`:
the selection contains the first directory rather than all three. The job
reports **1 failed, 1018 passed, 1 skipped**. This is a real upstream CI failure;
the successful Windows checks must not be described as a fully green matrix.

## Integration contracts and Python support

All declared console-entry modules exist in the selected source trees. No
`AGENTS.md` files were present in those seven checkouts.

| Application | Package Python requirement | Portal invocation |
| --- | --- | --- |
| MolStat | `>=3.11` | `molstat.cli:main` needs `gui --settings <path>`; use the existing `%LOCALAPPDATA%/MolStat/settings.json` convention from its launcher. |
| HemaFrag | `>=3.12,<3.15` | `hemafrag_diagnostics.__main__:main` |
| Archer | `>=3.11` | `archer_processor.__main__:main` |
| MolKey | `>=3.11,<3.15` | `molkey.__main__:main` |
| Solide | `>=3.11` | `solide.__main__:main`; parses command-line arguments, so the portal runner must remove its own module ID before invoking it. |
| IGH | `>=3.11` | `igh_merge.__main__:main` opens the GUI; the separate `igh_merge.cli:main` console interface is not the portal GUI contract. |
| MPN | `>=3.12` | `mpn_tolkning.__main__:main` |

HemaFrag also ships a Windows ABI3 native kernel wheel used by its CI. Source
installation alone does not install that separate wheel. Forward compatibility
requires resolving dependencies, native wheels and running tests for each new
Python minor. In particular HemaFrag and MolKey explicitly reject Python 3.15
in their package metadata. Their bounds must not be bypassed or advertised as
supported merely because the portal itself runs on a newer interpreter.

## Local component validation

Validation uses isolated `.tmp/portal-audit-2026-10-20/venv314`, CPython 3.14.0 on
Windows, with all seven selected distributions installed together and Qt in a
headless mode. Scratch JSON, GitHub responses, source clones and logs remain
under `.tmp/portal-audit-2026-10-20/`; they are not release payloads.

Use a short temporary directory outside every Git checkout when repeating
component tests on Windows, for example `--basetemp=C:/Temp/emolpat-tests`.
The first harness placed temporary output beneath this repository. That exceeded
Windows path limits in several tests and correctly triggered IGH's prohibition
on writing clinical output inside Git. Repeating the runs outside Git preserves
these checks and the upstream assertions.

MolStat's default commit had two failing recovery tests on Windows Python 3.14:
one mocked `Path.stat` while production uses `Path.lstat`; the other assumed
`Path.is_file` would call the overridable `stat` method. The fix explicitly
simulates the filesystem operations and race, preserving all error and privacy
assertions. Both test modules pass on Python 3.12 (58 tests), and the complete
Python 3.14 suite passes (908 tests).

[MolStat PR #7](https://github.com/Christian-Bjornstad/MolStat/pull/7) contains
only those test changes, based on the default commit above. The candidate pins
`6fb1219d82cf16a978cee9a86b45d51c4954db17` so its release test gate is reproducible
before that PR is merged. MolStat's runtime source and distribution version are
unchanged. No upstream default branches were merged or force-pushed.

### Completed local component gates

| Component | Passed | Skipped | Source |
|---|---:|---:|---|
| MolStat | 908 | 0 | `6fb1219` (test-only portability fix above) |
| HemaFrag Diagnostics | 1,014 | 6 | `cd4ae389` |
| Archer-prosess | 848 | 0 | `249b8234` |
| MolKey | 149 | 0 | `2124e087` |
| Solide | 862 | 1 | `4ff2b04d` |
| IGH | 229 | 0 | `4af58a7b` |
| MPN-Tolkning | 389 | 0 | `5b795957` |
| **Total** | **4,399** | **7** | Windows / CPython 3.14.0 |

No upstream tests or thresholds were skipped or weakened for this candidate.
Skipped tests are those already conditionally skipped by their component suites.
HemaFrag's remote macOS CI failure remains outside the verified Windows target.

The portal additionally passes **178 tests on each of Windows CPython 3.12,
3.14 and 3.15**. Its wheel and source distribution build successfully. Local
linting checks the tracked source directories; unrelated pre-existing local
build copies and scratch experiments are outside the source gate.

### Assembled offline candidate

The candidate builds from clean pinned source checkouts, including the MolStat
test-only commit. Its regenerated Windows CPython 3.14 lock contains 85 exact
wheels, including `python-docx`, `lxml` and the immutable HemaFrag ABI3 kernel.
All dependency versions already present in the prior input remain pinned; the
lock records the actual target-specific wheel hashes.

A new Python 3.14 virtual environment installed the hash-locked dependencies and
all eight application wheels without using an index. `pip check` passes. The
installed-suite smoke resolves eight distributions and seven entry points. Each
application also displayed its real `MainWindow` in a separate offscreen process
and exited successfully after a timer requested shutdown. Those startup probes
used disposable settings, an isolated home, and INI-based Qt settings; they did
not use the operator's live registry or clinical configuration.

Both the assembled payload and the deterministic archive pass integrity checks.
The candidate ZIP SHA-256 is recorded in [its release notes](../releases/1.3.0.md).
The Python 3.16 advisory is currently limited by an unavailable development build
in GitHub's Windows runner. Required stable-version jobs use disposable virtual
environments so unrelated runner tools cannot contaminate dependency checks.
