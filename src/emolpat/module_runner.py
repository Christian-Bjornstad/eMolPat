"""Start one trusted analysis module in a dedicated child process."""

from __future__ import annotations

from collections.abc import Sequence

from emolpat.__main__ import bundled_manifest
from emolpat.launch import EntryPointResolver, resolve_entry_point


def run_module(
    module_id: str,
    resolver: EntryPointResolver = resolve_entry_point,
) -> int:
    """Resolve a manifest-approved module identifier and invoke its entry point."""
    try:
        module = bundled_manifest().module(module_id)
        callback = resolver(module.entry_point)
    except (KeyError, ImportError, AttributeError, TypeError, ValueError):
        return 2
    result = callback()
    return int(result or 0)


def main(argv: Sequence[str] | None = None) -> int:
    """Require exactly one trusted module identifier from the command line."""
    import sys

    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        return 2
    return run_module(arguments[0])


if __name__ == "__main__":
    raise SystemExit(main())
