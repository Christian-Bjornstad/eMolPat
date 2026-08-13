"""Typed domain models shared by the eMolPat suite services."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

APPROVED_MODULE_IDS = (
    "hemafrag",
    "igh-merge",
    "vpm-tolkning",
    "mpn-tolkning",
)


class SuiteState(StrEnum):
    """User-facing health states for the complete installed suite."""

    READY = "ready"
    UPDATE_AVAILABLE = "update_available"
    REPAIR_REQUIRED = "repair_required"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class FileDigest:
    """Expected SHA-256 digest for one release-relative file."""

    path: str
    sha256: str


@dataclass(frozen=True)
class ModuleSpec:
    """One approved analysis module declared by a suite release."""

    id: str
    name: str
    distribution: str
    version: str
    import_name: str
    entry_point: str
    icon: str
    description_nb: str


@dataclass(frozen=True)
class SuiteManifest:
    """Immutable release contract for the portal and its four modules."""

    schema_version: int
    suite_version: str
    python_requires: str
    modules: tuple[ModuleSpec, ...]
    files: tuple[FileDigest, ...]

    def module(self, module_id: str) -> ModuleSpec:
        """Return a declared module or raise a useful lookup error."""
        for module in self.modules:
            if module.id == module_id:
                return module
        raise KeyError(f"unknown module id: {module_id}")

