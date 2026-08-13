"""Cryptographic and structural verification of offline suite releases."""

from __future__ import annotations

import hashlib
from pathlib import Path

from emolpat.domain import (
    SuiteManifest,
    VerificationIssue,
    VerificationReport,
)

REQUIRED_DIRECTORIES = ("packages", "wheelhouse")
REQUIRED_FILES = ("requirements.lock",)


class IntegrityError(ValueError):
    """Raised when a manifest path cannot safely identify a release file."""


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _release_file(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute():
        raise IntegrityError(f"manifest path points outside release root: {relative_path}")
    root = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise IntegrityError(
            f"manifest path points outside release root: {relative_path}"
        ) from exc
    return candidate


def verify_release(root: Path, manifest: SuiteManifest) -> VerificationReport:
    """Verify required structure and every manifest-declared file."""
    release_root = root.resolve()
    issues: list[VerificationIssue] = []

    for relative_path in REQUIRED_DIRECTORIES:
        if not (release_root / relative_path).is_dir():
            issues.append(
                VerificationIssue(
                    code="missing_directory",
                    path=relative_path,
                    message=f"Required release directory is missing: {relative_path}",
                )
            )
    for relative_path in REQUIRED_FILES:
        if not (release_root / relative_path).is_file():
            issues.append(
                VerificationIssue(
                    code="missing_file",
                    path=relative_path,
                    message=f"Required release file is missing: {relative_path}",
                )
            )

    for declared in manifest.files:
        path = _release_file(release_root, declared.path)
        if not path.is_file():
            issues.append(
                VerificationIssue(
                    code="missing_file",
                    path=declared.path,
                    message=f"Declared release file is missing: {declared.path}",
                )
            )
            continue
        actual = sha256_file(path)
        if actual != declared.sha256:
            issues.append(
                VerificationIssue(
                    code="checksum_mismatch",
                    path=declared.path,
                    message=f"SHA-256 checksum does not match: {declared.path}",
                )
            )

    declared_paths = {file.path for file in manifest.files}
    actual_paths = {
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    for relative_path in sorted(actual_paths - declared_paths):
        issues.append(
            VerificationIssue(
                code="unexpected_file",
                path=relative_path,
                message=f"Unexpected release file: {relative_path}",
            )
        )

    ordered = tuple(sorted(set(issues), key=lambda issue: (issue.path, issue.code)))
    return VerificationReport(ok=not ordered, issues=ordered)
