"""Offline, per-user installation of one atomic eMolPat suite release."""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.util import find_spec
from pathlib import Path
from typing import Protocol

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from emolpat.domain import (
    Command,
    InstalledModule,
    InstallRecord,
    InstallResult,
    SuiteManifest,
)
from emolpat.health import InstallRecordError, read_install_record
from emolpat.integrity import sha256_file, verify_release
from emolpat.manifest import load_historical_manifest, load_manifest
from emolpat.paths import UserPaths


class CommandRunner(Protocol):
    def __call__(self, command: Command) -> int: ...


def build_pip_commands(
    release_root: Path,
    user_site: Path | None = None,
) -> tuple[Command, ...]:
    """Build exact offline pip commands; ``user_site`` documents the boundary."""
    del user_site
    root = release_root.resolve()
    common = (
        sys.executable,
        "-m",
        "pip",
        "install",
        "--user",
        "--no-index",
    )
    # First command: bootstrap pip via ensurepip (critical for Microsoft Store Python)
    # ensurepip is a stdlib module that installs pip without needing pip already present
    ensurepip_bootstrap = Command(
        stage="ensurepip-bootstrap",
        argv=(sys.executable, "-m", "ensurepip", "--user", "--upgrade"),
    )
    # Second command: ensure pip itself is available from local wheelhouse
    pip_wheel = sorted((root / "wheelhouse").glob("pip-*.whl"))
    if not pip_wheel:
        raise RuntimeError("pip wheel not found in wheelhouse")
    ensure_pip = Command(
        stage="ensure-pip",
        argv=(*common, "--no-deps", "--force-reinstall", str(pip_wheel[0])),
    )
    dependencies = Command(
        stage="dependencies",
        argv=(
            *common,
            "--find-links",
            str(root / "wheelhouse"),
            "--require-hashes",
            "-r",
            str(root / "requirements.lock"),
        ),
    )
    wheels = tuple(str(path) for path in sorted((root / "packages").glob("*.whl")))
    components = Command(
        stage="components",
        argv=(*common, "--no-deps", "--force-reinstall", *wheels),
    )
    return ensurepip_bootstrap, ensure_pip, dependencies, components


def run_pip_in_process(arguments: tuple[str, ...]) -> int:
    """Invoke pip without a child process for restricted Python FELLES hosts."""
    if find_spec("pip") is None:
        try:
            subprocess.run(
                (sys.executable, "-m", "ensurepip", "--user", "--upgrade"),
                check=False,
                stdin=subprocess.DEVNULL,
            )
        except (OSError, subprocess.SubprocessError):
            # The later import reports the controlled installation failure.
            pass

    from pip._internal.cli.main import main as pip_main

    return pip_main(list(arguments))


def run_command(command: Command) -> int:
    """Prefer an isolated child process and fall back only when creation is denied."""
    if (
        getattr(command, "stage", None) == "ensurepip-bootstrap"
        and find_spec("pip") is not None
    ):
        return 0
    try:
        completed = subprocess.run(
            command.argv,
            check=False,
            stdin=subprocess.DEVNULL,
        )
        return completed.returncode
    except OSError:
        try:
            pip_index = command.argv.index("pip")
        except ValueError:
            return 1
        return run_pip_in_process(command.argv[pip_index + 1 :])


def replace_install_record(path: Path, record: InstallRecord) -> None:
    """Durably replace the verified install record in one atomic rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(asdict(record), stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def _verify_installed(manifest: SuiteManifest) -> bool:
    for module in manifest.modules:
        try:
            if importlib.metadata.version(module.distribution) != module.version:
                return False
            importlib.import_module(module.import_name)
        except (ImportError, importlib.metadata.PackageNotFoundError):
            return False
    return True


def _runner_verifies(runner: CommandRunner, manifest: SuiteManifest) -> bool:
    verifier = getattr(runner, "verify", None)
    if callable(verifier):
        return bool(verifier(manifest))
    return _verify_installed(manifest)


def _retain_release(release_root: Path, paths: UserPaths, version: str) -> None:
    """Retain immutable offline inputs so this version can be restored later."""
    destination = paths.rollback / version
    if destination.exists():
        return
    temporary = paths.rollback / f".{version}.tmp"
    temporary.mkdir(parents=True, exist_ok=False)
    for filename in ("manifest.json", "requirements.lock"):
        shutil.copy2(release_root / filename, temporary / filename)
    for directory in ("packages", "wheelhouse"):
        shutil.copytree(release_root / directory, temporary / directory)
    temporary.rename(destination)


def _attempt_rollback(
    previous: InstallRecord | None,
    runner: CommandRunner,
    paths: UserPaths,
) -> bool:
    if previous is None:
        return False
    retained = paths.rollback / previous.suite_version
    manifest_path = retained / "manifest.json"
    if not manifest_path.is_file():
        return False
    try:
        if sha256_file(manifest_path) != previous.manifest_sha256:
            return False
        manifest = load_historical_manifest(manifest_path, previous)
        if not verify_release(retained, manifest).ok:
            return False
        for command in build_pip_commands(retained):
            if runner(command) != 0:
                return False
        return _runner_verifies(runner, manifest)
    except (OSError, RuntimeError, ValueError):
        return False


def install_release(
    release_root: Path,
    runner: CommandRunner = run_command,
    paths: UserPaths | None = None,
    progress: Callable[[str], None] | None = None,
) -> InstallResult:
    """Install all suite components and record success only after verification."""
    report_progress = progress or (lambda _stage: None)
    report_progress("preflight")
    if paths is None:
        raise ValueError("per-user eMolPat paths are required")
    root = release_root.resolve()
    try:
        manifest = load_manifest(root / "manifest.json")
        integrity = verify_release(root, manifest)
        supported_python = Version(
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ) in SpecifierSet(manifest.python_requires)
    except (OSError, ValueError, InvalidSpecifier):
        return InstallResult(ok=False, stage="preflight")
    if not integrity.ok or not supported_python:
        return InstallResult(ok=False, stage="preflight")

    try:
        previous = read_install_record(paths.install_record)
    except InstallRecordError:
        return InstallResult(ok=False, stage="preflight")
    for command in build_pip_commands(root):
        report_progress(command.stage)
        code = runner(command)
        if code != 0:
            rolled_back = _attempt_rollback(previous, runner, paths)
            return InstallResult(
                ok=False,
                stage=command.stage,
                return_code=code,
                rolled_back=rolled_back,
            )

    report_progress("verification")
    if not _runner_verifies(runner, manifest):
        rolled_back = _attempt_rollback(previous, runner, paths)
        return InstallResult(
            ok=False,
            stage="verification",
            rolled_back=rolled_back,
        )

    report_progress("record")
    record = InstallRecord(
        suite_version=manifest.suite_version,
        manifest_sha256=sha256_file(root / "manifest.json"),
        verified_at=datetime.now(UTC).isoformat(),
        modules=tuple(
            InstalledModule(
                distribution=module.distribution,
                version=module.version,
                import_name=module.import_name,
            )
            for module in manifest.modules
        ),
    )
    try:
        _retain_release(root, paths, manifest.suite_version)
        replace_install_record(paths.install_record, record)
    except OSError:
        rolled_back = _attempt_rollback(previous, runner, paths)
        return InstallResult(ok=False, stage="record", rolled_back=rolled_back)
    return InstallResult(ok=True, stage="record")
