# Component branch audit — 2026-10-30

All 69 remote branches in the seven existing component repositories were enumerated through the authenticated GitHub API. Each branch was compared against its repository default branch using `compare/default...branch`; every nonmerged branch’s commit subjects and changed-file scope were inspected. The table records the remote state observed on 2026-10-30 before any audit fixes. Exact source commits are pinned independently from mutable branch names.

The latest active implementation was selected for each component. No clinical implementation branches were merged and no branches were deleted. Three missing draft integration PRs were created and attached to the eMolPat chat. Existing PRs were retained. Older divergent research branches are explicitly listed below for separate review.

## Selected component sources

| Repository | Selected branch | Exact commit | Version | Ahead / behind default | Review |
| --- | --- | --- | --- | --- | --- |
| HemaFrag-Diagnostics | `codex/single-tracking-operator` | `d31466154ab62655df839875b4289b908d402fec` | 1.2.1 | +1 / −0 | [PR #10](https://github.com/Christian-Bjornstad/HemaFrag-Diagnostics/pull/10) |
| IGH | `codex/excel-workflow-saved-runs` | `01315c0607c4d0556fe569fe7dd96db0bb935755` | 0.2.0 | +3 / −1 | [PR #2](https://github.com/Christian-Bjornstad/IGH/pull/2) |
| Archer-prosess | `feat/app-ui-settings-cleanup` | `c8092d194940e30062ef4d26059fd6233a508f3f` | 0.1.0 | +8 / −1 | [PR #13](https://github.com/Christian-Bjornstad/Archer-prosess/pull/13) |
| MPN-Tolkning | `main` | `5b79595716fc846a75e3a642c3849c6ac545dfde` | 0.1.0 | +0 / −0 | Default branch |
| MolStat | `codex/solide-tidsforlop` | `196ae74c2a83ea548e45420e5aa3a90cc6950848` | 0.1.0 | +16 / −3 | [PR #8](https://github.com/Christian-Bjornstad/MolStat/pull/8) |
| MolKey | `codex/review-cleanup` | `fd98d0263b04472db6a51ec09f18b859a4fabce8` | 0.2.0 | +5 / −0 | [PR #3](https://github.com/Christian-Bjornstad/MolKey/pull/3) |
| solide | `codex/fix-workstation-searches` | `429b1c3a5faed04807b92aec65d0ebd5f0d5cc8b` | 0.8.11 | +21 / −0 | [PR #2](https://github.com/Christian-Bjornstad/solide/pull/2) |

### Integration decisions

- **IGH:** the saved-run branch contains the current report branch plus the saved-run workflow. The only default-only commit is PR #1’s merge wrapper (`4af58a7b`), so the latest source retains the substantive default implementation. Draft PR #2 includes all three subsequent commits.
- **Archer:** eight source fixes followed the already merged PR #12 on its existing head branch. The only default-only commit is PR #12’s merge wrapper (`249b8234`). Draft PR #13 exposes those later changes, including provider recovery, COSMIC identity verification, credential error sanitization, report order, updated product assets and GPLv3 distribution cleanup.
- **MolStat:** the latest timeline/performance branch includes all eight substantive commits from `codex/app-redesign-unit-isolation` plus eight later commits. The three default-only commits are merge wrappers for PRs #4–6 (`d1a9fc7c`, `cf1f3acc`, `8bc513be`). Draft PR #8 retains all sixteen. Test-only PR #7 (`6fb1219d`) is a separate Python 3.14 filesystem simulation portability fix; its relationship to the current suite is tracked below.
- **HemaFrag, MolKey and Solide:** latest branches are direct descendants of default and already have open PRs (#10, #3 and #2 respectively). HemaFrag’s PR #10 has successful upstream Windows/Python 3.12, Python 3.14 and Rust checks at its exact selected head.
- **MPN:** only `main` exists; no missing integration PR is applicable.

## Isolated source validation

Tests use the existing isolated CPython 3.14 virtual environment, the exact selected checkout on `PYTHONPATH`, offscreen Qt, and unique short `C:/Temp/na…` directories for APPDATA, LOCALAPPDATA and pytest temporary files. They use repository synthetic fixtures; no live workstation service or patient data was used. The environment initially contained fraggler-kernels 0.1.2, whereas the current HemaFrag CI requires 0.1.3; dependency correction and any reruns are recorded explicitly.

| Component | Full pytest result |
| --- | --- |
| HemaFrag-Diagnostics | 1066 passed, 6 skipped; native 0.1.3 and PyInstaller installed |
| IGH | 252 passed in 20.08s |
| Archer-prosess | 916 passed, 2 warnings in 79.77s (0:01:19) |
| MPN-Tolkning | 389 passed, 2 warnings in 37.54s |
| MolStat | 1064 passed on current branch plus test portability fix |
| MolKey | 172 passed in 23.35s |
| solide | 1162 passed, 7 skipped in 76.46s (0:01:16) |

## Complete branch inventory

Ahead/behind numbers are Git ancestry, not a judgment that old clinical changes can safely be replayed. A branch with zero ahead commits is fully reachable from default. Historical divergent branches remain preserved for later domain-specific review.

### HemaFrag-Diagnostics

Default: `main`. Selected: `codex/single-tracking-operator`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `clonality-ml-phase-5-real-data-2026-07-11` | 0 | 226 | `8efa96d7a2df` | Default or fully merged ancestor |
| `code-cleanup` | 0 | 293 | `19c23ea0f11b` | Default or fully merged ancestor |
| `codex/clonality-ml-cleanup-plan-2026-07-26` | 0 | 197 | `9dde48c516a3` | Default or fully merged ancestor |
| `codex/deterministic-ci-tests` | 2 | 102 | `f4eb9c32cd71` | Historical test-only branch, +2 / −102; current upstream CI green, do not replay blindly |
| `codex/emolpat-packaging` | 0 | 102 | `1bbce920b584` | Default or fully merged ancestor |
| `codex/input-folder-browser-sort` | 0 | 7 | `f7c26673ecbe` | Default or fully merged ancestor |
| `codex/ladder-fitting-historical-research` | 0 | 122 | `0ad278362aa9` | Default or fully merged ancestor |
| `codex/ladder-fitting-performance-safety` | 0 | 178 | `443a97628d7e` | Default or fully merged ancestor |
| `codex/ladder-missing-source` | 0 | 11 | `a0a8c7d6dbbb` | Default or fully merged ancestor |
| `codex/ladder-review-completion-guide` | 0 | 8 | `4dacb5e0d4a9` | Default or fully merged ancestor |
| `codex/liz-early-anchor-qc` | 0 | 10 | `1515a0f47713` | Default or fully merged ancestor |
| `codex/npm1-manual-review` | 0 | 12 | `884741ff159a` | Default or fully merged ancestor |
| `codex/plan-13-quality-speed-precision` | 0 | 187 | `231f7164d963` | Default or fully merged ancestor |
| `codex/plan-14-channel-level-clonality` | 0 | 186 | `2ff44ce2b755` | Default or fully merged ancestor |
| `codex/single-tracking-operator` | 1 | 0 | `d31466154ab6` | Selected latest source |
| `codex/ui-polish` | 0 | 185 | `d5fb54fa54a9` | Default or fully merged ancestor |
| `codex/usability-archive-tracking` | 0 | 185 | `385793e5e322` | Default or fully merged ancestor |
| `codex-clonality-interp-v1-2026-06-28` | 2 | 273 | `a69295a4eb28` | Historical clinical/research divergence; requires separate clinical review |
| `codex-clonality-ladder-finalize-2026-05-14` | 0 | 329 | `3345195b7ace` | Default or fully merged ancestor |
| `feat/ml-learning-tab-2026-07-12` | 31 | 242 | `5996b1bfaf6b` | Historical clinical/research divergence; requires separate clinical review |
| `feature/ighv-clonality-round` | 0 | 94 | `ea9258de0fa3` | Default or fully merged ancestor |
| `feature/ladder-review-workflow` | 0 | 14 | `0f5bd9a9b56f` | Default or fully merged ancestor |
| `fix/html-report-savepeaks-combo-qc` | 0 | 255 | `2d950675fe3d` | Default or fully merged ancestor |
| `fix/ladder-dialog-unbound-names` | 0 | 259 | `cf3e123f3587` | Default or fully merged ancestor |
| `graphify-knowledge-graph` | 5 | 101 | `15b49bcd10b1` | Historical graph/docs experiment; preserved separately |
| `improvement/clonality-annotation-panel-2026-07-11-v2` | 25 | 266 | `a053e8c368fe` | Historical clinical/research divergence; requires separate clinical review |
| `improvement/clonality-annotation-panel-2026-07-11` | 1 | 242 | `56b7da92eb18` | Historical clinical/research divergence; requires separate clinical review |
| `improvement/flt3-npm1-ref-zoom-baseline-2026-07-14` | 34 | 242 | `c6bc98428d11` | Historical clinical/research divergence; requires separate clinical review |
| `main` | 0 | 0 | `35c33d1b2b77` | Default or fully merged ancestor |
| `ml-clonality-interpretation-2026-06-27` | 24 | 266 | `5003a6313fba` | Historical clinical/research divergence; requires separate clinical review |
| `py314-migration-plan` | 0 | 260 | `b6a289c8fc3a` | Default or fully merged ancestor |
| `review/codebase-optimization` | 0 | 87 | `7e7bb2f2c0fa` | Default or fully merged ancestor |
| `ux/design-pass-1` | 0 | 244 | `8575d4051c66` | Default or fully merged ancestor |

### IGH

Default: `codex/igh-merge-gui`. Selected: `codex/excel-workflow-saved-runs`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `codex/excel-workflow-saved-runs` | 3 | 1 | `01315c0607c4` | Selected latest source |
| `codex/igh-merge-gui` | 0 | 0 | `4af58a7bfb83` | Default or fully merged ancestor |
| `codex/ighv-analysis-reports` | 2 | 1 | `3b8be8442734` | Included in selected saved-run branch |
| `feature/ighv-modern-ui-english` | 0 | 14 | `c29eb3426f8c` | Default or fully merged ancestor |

### Archer-prosess

Default: `main`. Selected: `feat/app-ui-settings-cleanup`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `diagnostics/citrix-edge-connection` | 1 | 76 | `699eba649522` | Historical Citrix diagnostics; +1 / −76, preserved separately |
| `docs/vpm-brukerguide` | 0 | 26 | `fcedeb8bbdfb` | Default or fully merged ancestor |
| `feat/app-ui-settings-cleanup` | 8 | 1 | `c8092d194940` | Selected latest source |
| `feat/edge-cdp-dynamic-port` | 0 | 69 | `d2642d0a5373` | Default or fully merged ancestor |
| `feat/historical-evidence-backup` | 4 | 4 | `c9ab58776429` | Historical implementation ancestry already integrated; no competing PR |
| `feat/myolid-tolkning-redesign` | 0 | 129 | `8f35ed2d5745` | Default or fully merged ancestor |
| `feat/rerun-failed-and-evidence` | 0 | 116 | `05f61a5a3f90` | Default or fully merged ancestor |
| `feat/vpm-app-improvements-implementation` | 0 | 90 | `102f994c5b72` | Default or fully merged ancestor |
| `feat/vpm-report-polish` | 0 | 58 | `dd01110bbada` | Default or fully merged ancestor |
| `feat/workstation-improvements-2026-10-07` | 5 | 4 | `50b643e0d751` | Historical implementation ancestry already integrated; no competing PR |
| `fix/archer-priority-franklin-capture` | 0 | 122 | `2b6d3f00d15e` | Default or fully merged ancestor |
| `fix/germline-only-highlighting` | 0 | 121 | `d5ed776198a8` | Default or fully merged ancestor |
| `fix/run-diagnostics-recovery` | 0 | 37 | `100c623a9c12` | Default or fully merged ancestor |
| `fix/vpm-ui-report-capture` | 0 | 77 | `372d702013e1` | Default or fully merged ancestor |
| `main` | 0 | 0 | `249b82345761` | Default or fully merged ancestor |
| `redesign/status-workspace` | 0 | 132 | `a6ff94b09588` | Default or fully merged ancestor |

### MPN-Tolkning

Default: `main`. Selected: `main`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `main` | 0 | 0 | `5b79595716fc` | Selected latest source |

### MolStat

Default: `main`. Selected: `codex/solide-tidsforlop`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `codex/app-redesign-unit-isolation` | 8 | 3 | `9f6097b8faf8` | Included in selected timeline branch |
| `codex/fix-sharepoint-publishing` | 0 | 102 | `6b76c92110cd` | Default or fully merged ancestor |
| `codex/molstat-implementation` | 0 | 106 | `c2fc602247a6` | Default or fully merged ancestor |
| `codex/python314-portable-recovery-tests` | 1 | 0 | `6fb1219d82cf` | Separate portability test fix; open PR #7 |
| `codex/review-fixes-2026-09-26` | 0 | 22 | `d19f012338e7` | Default or fully merged ancestor |
| `codex/robust-app-config` | 0 | 28 | `db1417ce764f` | Default or fully merged ancestor |
| `codex/solide-tidsforlop` | 16 | 3 | `196ae74c2a83` | Selected latest source |
| `docs/powerbi-restanse-mal` | 0 | 47 | `d9a39a78e4a1` | Default or fully merged ancestor |
| `main` | 0 | 0 | `8bc513be5c07` | Default or fully merged ancestor |

### MolKey

Default: `main`. Selected: `codex/review-cleanup`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `codex/review-cleanup` | 5 | 0 | `fd98d0263b04` | Selected latest source |
| `feat/uppercase-ids-and-concurrency` | 0 | 2 | `99342948f54a` | Default or fully merged ancestor |
| `main` | 0 | 0 | `2124e0874d65` | Default or fully merged ancestor |

### solide

Default: `main`. Selected: `codex/fix-workstation-searches`.

| Branch | Ahead | Behind | Head commit | Disposition |
| --- | ---: | ---: | --- | --- |
| `codex/excel-review` | 0 | 1 | `20acaa9504c3` | Default or fully merged ancestor |
| `codex/fix-workstation-searches` | 21 | 0 | `429b1c3a5fae` | Selected latest source |
| `main` | 0 | 0 | `4ff2b04d387a` | Default or fully merged ancestor |

## Outstanding historical divergence

HemaFrag’s July clonality/ML/annotation/FLT3 experiments have 1–34 unique commits and are 242–273 commits behind current default. They include overlapping ladder workflow, QDA training, manual annotation and FLT3 integration work. They are not treated as current releases solely because Git reports unique commits. Their exact head hashes remain in the inventory and their commit subjects/files are retained in `.tmp/nine-apps/audit/HemaFrag-Diagnostics.comparisons.json` for focused future clinical review. The August graph experiment and old deterministic-test branch likewise remain unmodified.

Archer’s September Citrix probe (`699eba649522`) is an isolated diagnostic experiment 76 commits behind default. Historical backup/workstation heads are preserved; the selected current branch already contains their substantive ancestry.

No outstanding historical branch was silently dropped, automatically merged, force-pushed, or deleted. The audit creates review opportunities without claiming clinical validation of those unselected experiments.

## Final nine-application candidate

The current MolStat production branch is retained, with the earlier test-only
Python 3.14 portability fix applied in child branch
`codex/portal-current-recovery-tests`, commit
`6f0398d2a14faa307132807766e3e1d5c7d5930d`.
[PR #9](https://github.com/Christian-Bjornstad/MolStat/pull/9) targets the current
branch, while PR #8 exposes that branch for default integration. The suite pins
the child commit. No runtime implementation was altered by these test fixes.

Two additional repositories were inspected across their full branch lists:

| Application | Repository | Branch | Commit | Version | Tests |
|---|---|---|---|---|---|
| DRAGEN | abl1-dragon | main (only branch) | 0e243211c3d119595316ea13b472162352cac131 | 0.6.2 | 286 passed, 2 platform skips |
| Qiaxcel | Qiaxcel-Fortynning | main (only branch) | 95c00a2713e5e0e8797aefdb9f8db93d299528b4 | 0.2.0 | 59 passed |

Neither new repository has a missing integration PR because neither has work
outside its default branch. DRAGEN resources are copied into the distribution
by its existing setup.py; Qiaxcel declares its assets as package data. Installed
wheels for both launch their GUI with zero arguments. No adapters were needed.

Across all nine app suites: **5366 tests passed, 15 existing conditional skips**.
The initial HemaFrag failures were resolved by installing its required native
0.1.3 wheel and PyInstaller, without changing source or skipping tests. MolStat's
two reproduced pathlib mocking failures were fixed with the existing test-only
change. Exact logs and synthetic test receipts are under `.tmp/nine-apps/audit`.
The portal release gate now installs declared requirements-dev.txt and the native
wheel so CI uses the required test tools.

The complete Windows CPython 3.14 payload contains ten application wheels and
91 dependency wheels. Complete dependency closure, markers, target ABI and
Requires-Python validation pass. A new environment installs the hash-locked
payload without an index: all 101 distributions satisfy their dependencies, and
the installed-suite smoke resolves all nine launchers. Runtime GUI smoke results
are recorded separately after the final installed-package run.

## Offline installed GUI validation

The assembled `dist/nine-apps/eMolPat-1.4.0` release was installed into a new, isolated CPython 3.14.0 environment at `.tmp/nine-apps/offline314`. The installation used only the release's local wheelhouse and package directory: 91 dependencies were installed with `--no-index --require-hashes`, followed by the 10 application wheels with `--no-index --no-deps`. `uv pip check` checked all 101 installed packages and reported that every package was compatible. The installed-suite smoke check verified all 10 distributions and all 9 zero-argument launch callbacks.

All nine applications then opened successfully through the installed `emolpat.module_runner.run_module` path, rendered a visible native Qt window, and exited with code 0. The portal itself also opened, rendered and exited with code 0. The captured window titles were:

| Module | Installed window title | Result |
| --- | --- | --- |
| HemaFrag | HemaFrag Diagnostics v1.2.1 | Passed |
| IGH Merge | IGHV | Passed |
| VPM / HTS Tolkning | VPM Tolkning | Passed |
| MPN Tolkning | MPN Tolkning | Passed |
| MolStat | MolStat | Passed |
| MolKey | MolKey | Passed |
| DRAGEN | DRAGEN | Passed |
| Solide | Solide 0.8.11 \| Variant review | Passed |
| Qiaxcel | QIAxcel | Passed |

The installed native `fraggler-kernels==0.1.3` extension also reported `fraggler_native.is_available() == True`. This check confirms native loading; it does not claim analysis of a real FSA file.

The GUI harness used a separate disposable home, local/roaming app-data folder and Qt settings folder for each application. Qt settings used INI files rather than the user's registry settings; MolKey used a new local test registry. No patient files or existing user settings were opened. Each application ran its real entry point and Qt event loop; the harness scheduled screenshots and a clean event-loop exit. Windows fonts were loaded explicitly for offscreen rendering. All nine screenshots were inspected together in the contact sheet.

Receipts are retained locally in `.tmp/nine-apps/audit/offline314-summary.json`, `offline314-<module>.json`, `offline314-<module>-0.png` and `offline314-<module>.log`; the contact sheet is `offline314-nine-guis.jpg`. Dependency, package, compatibility and import logs are `offline314-dependencies.log`, `offline314-packages.log`, `offline314-check.log` and `offline314-imports.log`; the native-loading receipt is `offline314-native.log`.

The direct wheel installation deliberately did not create an eMolPat installation record. Consequently the portal displayed its expected **not installed** health state and disabled launch buttons in this disposable environment. That state is a record/gating result, not an application runtime failure: all nine module-runner launches passed independently. This test does not replace a real Python FELLES deployment or clinical workflow validation.
