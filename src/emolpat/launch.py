"""Resolve and hand control from the eMolPat portal to one analysis app."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module

from emolpat.domain import ModuleSpec

EntryPoint = Callable[[], int | None]
EntryPointResolver = Callable[[str], EntryPoint]


@dataclass(frozen=True)
class LaunchResult:
    """Structured outcome for the pre-start portion of an app handoff."""

    module_id: str
    started: bool
    exit_code: int | None = None
    error_code: str | None = None
    message: str | None = None


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
