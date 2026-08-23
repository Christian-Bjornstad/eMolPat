"""Install and run the declared tests for every immutable suite component."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for import_root in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from emolpat.components import load_components
from scripts.build_suite import COMPONENT_DIRECTORIES

Runner = Callable[..., subprocess.CompletedProcess[str]]


def editable_spec(source: Path) -> str:
    """Include a component's declared test dependencies when available."""
    document = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))
    optional = document.get("project", {}).get("optional-dependencies", {})
    suffix = "[dev]" if "dev" in optional else ""
    return f"{source}{suffix}"


def test_components(
    component_file: Path,
    component_root: Path,
    *,
    runner: Runner = subprocess.run,
    python_executable: str = sys.executable,
) -> None:
    """Install each pinned source and execute its exact declared test command."""
    for component in load_components(component_file):
        source = component_root / COMPONENT_DIRECTORIES[component.id]
        runner(
            (
                python_executable,
                "-m",
                "pip",
                "install",
                "-e",
                editable_spec(source),
            ),
            check=True,
        )
        command = component.test_command
        if command[0].casefold() == "python":
            command = (python_executable, *command[1:])
        runner(command, cwd=source, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--components",
        type=Path,
        default=PROJECT_ROOT / "release/components.json",
    )
    parser.add_argument("--component-root", type=Path, required=True)
    arguments = parser.parse_args()
    test_components(arguments.components, arguments.component_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
