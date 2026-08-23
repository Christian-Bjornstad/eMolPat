"""Resolve and hand control from the eMolPat portal to one analysis app."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from typing import Protocol

from emolpat.domain import ModuleSpec

EntryPoint = Callable[[], int | None]
EntryPointResolver = Callable[[str], EntryPoint]


class ChildProcess(Protocol):
    """Small process interface needed for non-blocking lifecycle checks."""

    def poll(self) -> int | None:
        """Return the exit code when finished, otherwise ``None``."""
        raise NotImplementedError


SpawnChild = Callable[[tuple[str, ...]], ChildProcess]


@dataclass(frozen=True)
class LaunchResult:
    """Structured outcome for the pre-start portion of an app handoff."""

    module_id: str
    started: bool
    exit_code: int | None = None
    error_code: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class ProcessExit:
    """Observed completion of one separately launched analysis app."""

    module_id: str
    exit_code: int


def spawn_child(argv: tuple[str, ...]) -> ChildProcess:
    """Create a detached-I/O child without invoking a command shell."""
    return subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
    )


class ApplicationProcessManager:
    """Start and observe trusted analysis apps without blocking the portal."""

    def __init__(
        self,
        executable: str = sys.executable,
        spawn: SpawnChild = spawn_child,
    ) -> None:
        self.executable = executable
        self._spawn = spawn
        self._children: dict[str, ChildProcess] = {}

    @property
    def running_module_ids(self) -> frozenset[str]:
        return frozenset(self._children)

    def is_running(self, module_id: str) -> bool:
        return module_id in self._children

    def start(self, module: ModuleSpec) -> LaunchResult:
        if self.is_running(module.id):
            return LaunchResult(
                module_id=module.id,
                started=False,
                error_code="already_running",
            )

        argv = (
            self.executable,
            "-m",
            "emolpat.module_runner",
            module.id,
        )
        try:
            child = self._spawn(argv)
        except OSError as exc:
            return LaunchResult(
                module_id=module.id,
                started=False,
                error_code="process_start_failed",
                message=str(exc),
            )

        self._children[module.id] = child
        return LaunchResult(module_id=module.id, started=True)

    def poll(self) -> tuple[ProcessExit, ...]:
        finished: list[ProcessExit] = []
        for module_id, child in tuple(self._children.items()):
            exit_code = child.poll()
            if exit_code is None:
                continue
            del self._children[module_id]
            finished.append(ProcessExit(module_id, exit_code))
        return tuple(finished)

    def stop_monitoring(self) -> None:
        """Forget children while allowing every launched app to keep running."""
        self._children.clear()


def resolve_entry_point(value: str) -> EntryPoint:
    """Resolve a ``module:attribute`` value and require a callable target."""
    if value.count(":") != 1:
        raise ValueError(f"invalid entry point: {value!r}")

    module_name, attribute = value.split(":", 1)
    if not module_name or not attribute:
        raise ValueError(f"invalid entry point: {value!r}")

    callback = getattr(import_module(module_name), attribute)
    if not callable(callback):
        raise TypeError(f"entry point is not callable: {value}")
    return callback


def run_handoff(
    module: ModuleSpec,
    resolver: EntryPointResolver = resolve_entry_point,
) -> LaunchResult:
    """Start an app after resolution succeeds; do not hide runtime failures."""
    try:
        callback = resolver(module.entry_point)
    except ImportError as exc:
        return LaunchResult(
            module_id=module.id,
            started=False,
            error_code="entrypoint_import_failed",
            message=str(exc),
        )
    except (AttributeError, TypeError, ValueError) as exc:
        return LaunchResult(
            module_id=module.id,
            started=False,
            error_code="entrypoint_invalid",
            message=str(exc),
        )

    exit_code = callback()
    return LaunchResult(module_id=module.id, started=True, exit_code=exit_code)
