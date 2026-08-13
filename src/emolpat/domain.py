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


@dataclass(frozen=True)
class VerificationIssue:
    """One deterministic integrity failure in an approved release."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class VerificationReport:
    """Complete release verification result."""

    ok: bool
    issues: tuple[VerificationIssue, ...]


@dataclass(frozen=True)
class InstalledModule:
    """Exact module identity recorded after successful installation."""

    distribution: str
    version: str
    import_name: str


@dataclass(frozen=True)
class InstallRecord:
    """Last suite version that passed complete per-user verification."""

    suite_version: str
    manifest_sha256: str
    verified_at: str
    modules: tuple[InstalledModule, ...]


@dataclass(frozen=True)
class HealthReport:
    """Derived health state for the complete installed suite."""

    state: SuiteState
    suite_version: str | None
    issues: tuple[str, ...]


@dataclass(frozen=True)
class ComponentSpec:
    """Immutable source contract for one bundled application repository."""

    id: str
    repository: str
    commit: str
    distribution: str
    import_name: str
    entry_point: str
    test_command: tuple[str, ...]
