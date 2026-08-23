"""Load and validate immutable eMolPat suite manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from emolpat.domain import (
    APPROVED_MODULE_IDS,
    FileDigest,
    ModuleSpec,
    ModuleUnit,
    SuiteManifest,
)

ENTRY_POINT_PATTERN = re.compile(
    r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*$"
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Raised when a suite manifest is structurally invalid."""


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{field} must be an object")
    return value


def _string(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field} must be a non-empty string")
    return value


def _module_unit(data: dict[str, Any]) -> ModuleUnit:
    value = _string(data, "unit")
    try:
        return ModuleUnit(value)
    except ValueError as exc:
        raise ManifestError(f"invalid module unit: {value}") from exc


def _module(data: Any, index: int) -> ModuleSpec:
    values = _mapping(data, f"modules[{index}]")
    entry_point = _string(values, "entry_point")
    if ENTRY_POINT_PATTERN.fullmatch(entry_point) is None:
        raise ManifestError(f"invalid entry point: {entry_point}")
    return ModuleSpec(
        id=_string(values, "id"),
        name=_string(values, "name"),
        distribution=_string(values, "distribution"),
        version=_string(values, "version"),
        import_name=_string(values, "import_name"),
        entry_point=entry_point,
        icon=_string(values, "icon"),
        description_nb=_string(values, "description_nb"),
        description_en=_string(values, "description_en"),
        unit=_module_unit(values),
    )


def _file_digest(data: Any, index: int) -> FileDigest:
    values = _mapping(data, f"files[{index}]")
    digest = _string(values, "sha256").lower()
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise ManifestError(f"invalid SHA-256 digest: {digest}")
    return FileDigest(path=_string(values, "path"), sha256=digest)


def load_manifest(path: Path) -> SuiteManifest:
    """Load a manifest and enforce the version-one suite contract."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"could not read manifest: {path}") from exc

    data = _mapping(document, "manifest")
    schema_version = data.get("schema_version")
    if schema_version != 1:
        raise ManifestError(f"unsupported schema version: {schema_version}")

    raw_modules = data.get("modules")
    if not isinstance(raw_modules, list):
        raise ManifestError("modules must be an array")
    modules = tuple(_module(value, index) for index, value in enumerate(raw_modules))
    module_ids = tuple(module.id for module in modules)
    duplicate = next(
        (module_id for module_id in module_ids if module_ids.count(module_id) > 1),
        None,
    )
    if duplicate is not None:
        raise ManifestError(f"duplicate module id: {duplicate}")
    if module_ids != APPROVED_MODULE_IDS:
        raise ManifestError(
            "modules must match the approved module set in its canonical order"
        )

    raw_files = data.get("files")
    if not isinstance(raw_files, list):
        raise ManifestError("files must be an array")
    files = tuple(_file_digest(value, index) for index, value in enumerate(raw_files))

    return SuiteManifest(
        schema_version=schema_version,
        suite_version=_string(data, "suite_version"),
        python_requires=_string(data, "python_requires"),
        modules=modules,
        files=files,
    )
