"""Checkout the exact component commits used by an eMolPat release."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for import_root in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from emolpat.components import load_components
from scripts.build_suite import COMPONENT_DIRECTORIES

REPOSITORY_PATTERN = re.compile(
    r"^https://github\.com/Christian-Bjornstad/[A-Za-z0-9._-]+\.git$"
)
Runner = Callable[..., subprocess.CompletedProcess[str]]


def checkout_components(
    component_file: Path,
    destination: Path,
    runner: Runner = subprocess.run,
) -> tuple[Path, ...]:
    """Clone and detach every approved repository at its immutable commit."""
    components = load_components(component_file)
    root = destination.resolve()
    root.mkdir(parents=True, exist_ok=True)
    results = []
    for component in components:
        if REPOSITORY_PATTERN.fullmatch(component.repository) is None:
            raise ValueError(f"repository is not allowlisted: {component.id}")
        target = root / COMPONENT_DIRECTORIES[component.id]
        runner(
            (
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                component.repository,
                str(target),
            ),
            check=True,
            capture_output=True,
            text=True,
        )
        runner(
            ("git", "-C", str(target), "fetch", "--depth=1", "origin", component.commit),
            check=True,
            capture_output=True,
            text=True,
        )
        runner(
            ("git", "-C", str(target), "checkout", "--detach", component.commit),
            check=True,
            capture_output=True,
            text=True,
        )
        completed = runner(
            ("git", "-C", str(target), "rev-parse", "HEAD"),
            check=True,
            capture_output=True,
            text=True,
        )
        if completed.stdout.strip() != component.commit:
            raise RuntimeError(f"component checkout mismatch: {component.id}")
        results.append(target)
    return tuple(results)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--components",
        type=Path,
        default=PROJECT_ROOT / "release/components.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    checkout_components(arguments.components, arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
