from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.checkout_components import checkout_components


def test_checkout_script_runs_directly_outside_repository(tmp_path: Path) -> None:
    script = Path("scripts/checkout_components.py").resolve()

    completed = subprocess.run(
        (sys.executable, str(script), "--help"),
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr


def test_checkout_uses_exact_pinned_commits_without_a_shell(tmp_path: Path) -> None:
    commands = []

    def runner(argv, **kwargs):
        commands.append((tuple(argv), kwargs))
        if "rev-parse" in argv:
            commit = next(
                command[0][-1]
                for command in reversed(commands)
                if "fetch" in command[0]
            )
            return subprocess.CompletedProcess(argv, 0, stdout=f"{commit}\n")
        return subprocess.CompletedProcess(argv, 0, stdout="")

    roots = checkout_components(
        Path("release/components.json"),
        tmp_path / "components",
        runner=runner,
    )

    assert len(roots) == 4
    assert all(path.parent == (tmp_path / "components").resolve() for path in roots)
    clone_commands = [command for command, _kwargs in commands if "clone" in command]
    assert len(clone_commands) == 4
    assert all(command[0] == "git" for command in clone_commands)
    assert all("--no-checkout" in command for command in clone_commands)
    assert all(
        command[-2].startswith("https://github.com/Christian-Bjornstad/")
        for command in clone_commands
    )
    fetch_commands = [command for command, _kwargs in commands if "fetch" in command]
    assert all(len(command[-1]) == 40 for command in fetch_commands)
    assert all(kwargs.get("shell") is not True for _command, kwargs in commands)
