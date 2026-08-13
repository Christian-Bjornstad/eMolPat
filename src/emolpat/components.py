"""Load immutable source declarations for bundled applications."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from emolpat.domain import APPROVED_MODULE_IDS, ComponentSpec
from emolpat.manifest import ENTRY_POINT_PATTERN

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ComponentContractError(ValueError):
    """Raised when component source metadata is not reproducible."""


def _string(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise ComponentContractError(f"{field} must be a non-empty string")
    return value


def _component(value: Any, index: int) -> ComponentSpec:
    if not isinstance(value, dict):
        raise ComponentContractError(f"component {index} must be an object")
    commit = _string(value, "commit")
    if COMMIT_PATTERN.fullmatch(commit) is None:
        raise ComponentContractError(
            f"component {index} requires an immutable 40-character commit"
        )
    entry_point = _string(value, "entry_point")
    if ENTRY_POINT_PATTERN.fullmatch(entry_point) is None:
        raise ComponentContractError(f"invalid entry point: {entry_point}")
    command = value.get("test_command")
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(item, str) and item for item in command)
    ):
        raise ComponentContractError("test_command must be a non-empty string array")
    return ComponentSpec(
        id=_string(value, "id"),
        repository=_string(value, "repository"),
        commit=commit,
        distribution=_string(value, "distribution"),
        import_name=_string(value, "import_name"),
        entry_point=entry_point,
        test_command=tuple(command),
    )


def load_components(path: Path) -> tuple[ComponentSpec, ...]:
    """Load the four immutable repositories used to assemble one suite."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComponentContractError(f"could not read component contract: {path}") from exc
    if not isinstance(document, list):
        raise ComponentContractError("component contract must be an array")
    components = tuple(_component(value, index) for index, value in enumerate(document))
    if tuple(component.id for component in components) != APPROVED_MODULE_IDS:
        raise ComponentContractError(
            "components must match the approved module set in canonical order"
        )
    return components
