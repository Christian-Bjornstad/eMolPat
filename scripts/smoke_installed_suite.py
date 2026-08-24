"""Smoke-test an installed suite without invoking any application GUI."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import inspect
import json
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

Importer = Callable[[str], ModuleType]


def smoke_installed_suite(
    manifest_path: Path,
    *,
    importer: Importer = importlib.import_module,
) -> int:
    """Verify all seven distributions and resolve every zero-argument launcher."""
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        importer("emolpat")
        importlib.metadata.version("emolpat")
        for module in document["modules"]:
            installed = importlib.metadata.version(module["distribution"])
            if installed != module["version"]:
                raise RuntimeError(
                    f"version mismatch for {module['distribution']}: {installed}"
                )
            module_name, attribute = module["entry_point"].split(":", 1)
            callback = getattr(importer(module_name), attribute)
            if not callable(callback):
                raise TypeError(f"entry point is not callable: {module['entry_point']}")
            inspect.signature(callback).bind()
    except (ImportError, LookupError, OSError, TypeError, ValueError, RuntimeError) as exc:
        print(f"Installed suite smoke test failed: {type(exc).__name__}: {exc}")
        return 1
    print("Installed suite smoke test passed: 6 distributions, 5 entry points")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    return smoke_installed_suite(parser.parse_args().manifest.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
