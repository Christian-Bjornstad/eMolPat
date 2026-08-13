# Build an approved eMolPat release

Build only from the eMolPat release branch and the four clean component checkouts pinned in `release/components.json`.

```powershell
py -3.12 -m pytest -q
py -3.12 -m ruff check .
py -3.12 scripts/build_suite.py --version 1.0.0 --output dist --component-root C:\Users\molpa\Documents\ChatGPT\eMolPat-components
py -3.12 scripts/verify_suite.py dist\eMolPat-1.0.0
```

The result contains five application wheels, Windows dependency wheels, a hash-locked requirements file, and a manifest covering every install artifact. Never edit a published release in place; build a new suite version.
