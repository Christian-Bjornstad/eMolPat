"""Locate a verified local release for installation or repair."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from emolpat.health import InstallRecordError, read_install_record
from emolpat.integrity import verify_release
from emolpat.manifest import ManifestError, load_manifest
from emolpat.paths import UserPaths


def _verified_release(candidate: Path) -> Path | None:
    try:
        root = candidate.resolve()
        if not all(
            (
                (root / "manifest.json").is_file(),
                (root / "requirements.lock").is_file(),
                (root / "packages").is_dir(),
                (root / "wheelhouse").is_dir(),
            )
        ):
            return None
        manifest = load_manifest(root / "manifest.json")
        return root if verify_release(root, manifest).ok else None
    except (OSError, ValueError, ManifestError):
        return None


def find_release_root(
    paths: UserPaths,
    environment: Mapping[str, str],
    script_root: Path | None = None,
) -> Path | None:
    """Return the first verified extracted or retained offline release."""
    configured = environment.get("EMOLPAT_RELEASE_ROOT")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    if script_root is not None:
        candidates.append(script_root)

    try:
        record = read_install_record(paths.install_record)
    except InstallRecordError:
        record = None
    if record is not None:
        candidates.append(paths.rollback / record.suite_version)

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        verified = _verified_release(resolved)
        if verified is not None:
            return verified
    return None
