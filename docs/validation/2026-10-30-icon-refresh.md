# Component and icon refresh — 2026-10-30

Checked all 72 remote branch heads across the nine component repositories.
Each existing component pin is already the newest applicable active implementation
head. No application runtime source or component pin changed in this patch.
The prior ancestry review remains in [the component audit](2026-10-30-component-audit.md).

Three portal copies were stale: VPM / HTS Tolkning, MolKey and Solide.
MolStat and the other five portal icons already matched their current sources.
All nine assets were synchronized from the exact Git objects below.

| Application | Active branch | Exact source commit | Icon source |
|---|---|---|---|
| hemafrag | `codex/single-tracking-operator` | [`d31466154ab62655df839875b4289b908d402fec`](https://github.com/Christian-Bjornstad/HemaFrag-Diagnostics/commit/d31466154ab62655df839875b4289b908d402fec) | `assets/app_icon.png` |
| igh-merge | `codex/excel-workflow-saved-runs` | [`01315c0607c4d0556fe569fe7dd96db0bb935755`](https://github.com/Christian-Bjornstad/IGH/commit/01315c0607c4d0556fe569fe7dd96db0bb935755) | `src/igh_merge/assets/igh-merge-icon.png` |
| vpm-tolkning | `feat/app-ui-settings-cleanup` | [`c8092d194940e30062ef4d26059fd6233a508f3f`](https://github.com/Christian-Bjornstad/Archer-prosess/commit/c8092d194940e30062ef4d26059fd6233a508f3f) | `src/archer_processor/assets/vpm-tolkning-icon.png` |
| mpn-tolkning | `main` | [`5b79595716fc846a75e3a642c3849c6ac545dfde`](https://github.com/Christian-Bjornstad/MPN-Tolkning/commit/5b79595716fc846a75e3a642c3849c6ac545dfde) | `src/mpn_tolkning/assets/variant-lens.png` |
| molstat | `codex/portal-current-recovery-tests` | [`6f0398d2a14faa307132807766e3e1d5c7d5930d`](https://github.com/Christian-Bjornstad/MolStat/commit/6f0398d2a14faa307132807766e3e1d5c7d5930d) | `src/molstat/assets/molstat.png` |
| molkey | `codex/review-cleanup` | [`fd98d0263b04472db6a51ec09f18b859a4fabce8`](https://github.com/Christian-Bjornstad/MolKey/commit/fd98d0263b04472db6a51ec09f18b859a4fabce8) | `assets/molkey_icon_256.png` |
| dragen | `main` | [`0e243211c3d119595316ea13b472162352cac131`](https://github.com/Christian-Bjornstad/abl1-dragon/commit/0e243211c3d119595316ea13b472162352cac131) | `assets/brand/abl1-dragon.png` |
| solide | `codex/fix-workstation-searches` | [`429b1c3a5faed04807b92aec65d0ebd5f0d5cc8b`](https://github.com/Christian-Bjornstad/solide/commit/429b1c3a5faed04807b92aec65d0ebd5f0d5cc8b) | `src/solide/assets/solide.png` |
| qiaxcel | `main` | [`95c00a2713e5e0e8797aefdb9f8db93d299528b4`](https://github.com/Christian-Bjornstad/Qiaxcel-Fortynning/commit/95c00a2713e5e0e8797aefdb9f8db93d299528b4) | `src/qiaxcel/assets/qiaxcel.ico` |

## Release safeguards

`app-icons.json` records the source asset, exact component commit, bundled filename
and SHA-256 hash for each application. The portal reads the same catalog to choose
its icons. Root tests reject mismatched pins or bundled bytes. Before building,
the release builder also compares each hash against the asset in the pinned Git
object; after building, it checks every icon and the catalog inside the actual
portal wheel. It never rewrites sources or silently switches to a moving branch.

Refresh after changing pins with:

```powershell
py -3.12 scripts/sync_component_icons.py --component-root components --write
```

About now contains only `Utviklet av Christian Bjørnstad`. The navigation remains
available and the credit wraps at small window widths.

## Verification

- Full portal regression suite: 206 passed on Windows / Python 3.14.
- Static checks: Ruff passed.
- Catalog rendered at 1600×800 with all nine icons visible.
- About rendered at 760×520 and contains only the developer credit.
- Component application code and dependencies are unchanged from 1.4.0; their
  previous release validation remains applicable.
