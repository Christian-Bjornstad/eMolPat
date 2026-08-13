"""Resolve non-clinical per-user locations for eMolPat itself."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UserPaths:
    """Per-user eMolPat state paths, separate from analysis module data."""

    root: Path
    logs: Path
    install_record: Path
    rollback: Path

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> UserPaths:
        """Resolve paths from Windows environment values without using clinical paths."""
        local_app_data = environment.get("LOCALAPPDATA")
        if local_app_data:
            root = Path(local_app_data) / "eMolPat"
        else:
            user_profile = environment.get("USERPROFILE")
            if not user_profile:
                raise RuntimeError("Windows user data location is unavailable")
            root = Path(user_profile) / "AppData" / "Local" / "eMolPat"
        return cls(
            root=root,
            logs=root / "logs",
            install_record=root / "install-record.json",
            rollback=root / "rollback",
        )
