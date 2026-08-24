# Build an approved eMolPat release

Build only from the eMolPat release branch and the six clean component checkouts pinned in `release/components.json`.

```powershell
py -3.12 -m pytest -q
py -3.12 -m ruff check .
py -3.12 scripts/build_suite.py --version 1.2.0 --output dist --component-root C:\Users\molpa\Documents\ChatGPT\eMolPat-components
py -3.12 scripts/verify_suite.py dist\eMolPat-1.2.0
py -3.12 scripts/archive_release.py dist\eMolPat-1.2.0 --output dist
```

The result contains seven package wheels, Windows dependency wheels, a hash-locked requirements file, a complete manifest, `eMolPat-1.2.0-windows.zip`, and its SHA-256 sidecar. Verify the download asset before publication:

```powershell
$expected = (Get-Content dist\eMolPat-1.2.0-windows.zip.sha256).Split()[0]
$actual = (Get-FileHash dist\eMolPat-1.2.0-windows.zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "Release checksum mismatch" }
```

Publishing is tag-driven. After reviewed changes are merged and `master` CI is green, push an unused annotated semantic version tag such as `v1.0.0`. Never edit or replace a published release in place; build a new version.
