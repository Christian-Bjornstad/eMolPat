# Python compatibility and offline releases

The portal's source compatibility and an offline suite's runtime compatibility
are separate contracts. Installing a newer Python does not make an existing
offline suite compatible with it.

| Contract | Versions | Evidence required |
|---|---|---|
| Portal source and development dependencies | CPython 3.12–3.15 on Windows x64 | Required CI matrix: dependency installation, `pip check`, lint, tests, wheel and source distribution build |
| Next interpreter | CPython 3.16 development builds | Advisory CI job; failures remain visible and do not approve support |
| Current offline suite | CPython 3.14 on Windows x64 | Exact component commits, target-specific wheels, hash lock, complete dependency validation, clean installation and component smoke tests |

The source range applies to **eMolPat**, not automatically to every application
it starts. Each application retains its own Python and dependency requirements.
Free-threaded interpreters, other CPU architectures and other operating systems
need separate validation.

## Detect changes before upgrading

The source matrix runs on pushes, pull requests, manual dispatch and every
Monday. The advisory development job also tries prerelease dependencies. It
deliberately bypasses Python metadata ceilings only in its disposable CI
environment, so a future interpreter can expose API removals or missing wheels.
A successful advisory run does not broaden the supported source range or change
any released offline package.

The explicit source upper bound is reviewed when a new interpreter passes the
required gates. Keep the Ruff target at the oldest supported source interpreter,
so newer development environments cannot silently introduce unsupported syntax.

## Add another offline runtime

1. Check every pinned application's `Requires-Python` and dependency constraints.
2. Add a separate `PythonTarget` and fully pinned dependency input for the new
   CPython ABI and Windows architecture. Resolve the complete transitive closure,
   including extras and target-specific dependencies.
3. Run the builder. It checks every application and dependency wheel's target
   tags and `Requires-Python`, evaluates markers for the target environment rather
   than the build host, and rejects missing or conflicting dependencies. The
   target represents the first patch release of that minor series. OS-version
   markers require an explicit target policy and are rejected until one exists.
4. Install the resulting hash-locked suite into a clean matching interpreter,
   run `pip check`, run each application's tests, and resolve every entry point
   with the installed-suite smoke test.
5. Verify installation, launch, repair and rollback on the managed workstation.
   Publish a new immutable release with its own manifest, wheels and checksums.

The current Python FELLES bootstraps intentionally accept only Python 3.14. Do
not remove that check or widen `manifest.python_requires` to reuse 3.14 binary
wheels on another minor version.

## References

- [Python 3.15.0 release](https://www.python.org/downloads/release/python-3150/)
- [Python version status](https://devguide.python.org/versions/)
- [PyPA Python metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#requires-python)
- [Packaging environment markers](https://packaging.pypa.io/en/stable/markers.html#packaging.markers.Marker.evaluate)
- [Packaging compatibility tags](https://packaging.pypa.io/en/stable/tags.html#packaging.tags.cpython_tags)
- [GitHub setup-python development versions](https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md#specifying-a-python-version)
