from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from emolpat.domain import InstalledModule, InstallRecord
from emolpat.health import read_install_record
from emolpat.install import (
    build_pip_commands,
    install_release,
    replace_install_record,
    run_command,
)
from emolpat.paths import UserPaths


def paths_at(root: Path) -> UserPaths:
    return UserPaths(
        root=root,
        logs=root / "logs",
        install_record=root / "install-record.json",
        rollback=root / "rollback",
    )


def create_release(root: Path, version: str = "1.1.0") -> Path:
    root.mkdir(parents=True)
    (root / "packages").mkdir()
    (root / "wheelhouse").mkdir()
    lock = b"emolpat==1.1.0 --hash=sha256:" + b"a" * 64
    (root / "requirements.lock").write_bytes(lock)
    portal = root / "packages" / "emolpat-1.1.0-py3-none-any.whl"
    portal.write_bytes(b"wheel")
    # Add pip wheel for ensure-pip stage
    (root / "wheelhouse" / "pip-26.1.2-py3-none-any.whl").write_bytes(b"wheel")
    document = json.loads(Path("tests/fixtures/valid-manifest.json").read_text())
    document["suite_version"] = version
    # Use current Python version for tests to pass preflight
    import sys
    document["python_requires"] = f">={sys.version_info.major}.{sys.version_info.minor},<{sys.version_info.major}.{sys.version_info.minor + 1}"
    document["files"] = [
        {
            "path": "requirements.lock",
            "sha256": hashlib.sha256(lock).hexdigest(),
        },
        {
            "path": "packages/emolpat-1.1.0-py3-none-any.whl",
            "sha256": hashlib.sha256(b"wheel").hexdigest(),
        },
        {
            "path": "wheelhouse/pip-26.1.2-py3-none-any.whl",
            "sha256": hashlib.sha256(b"wheel").hexdigest(),
        },
    ]
    (root / "manifest.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def old_record() -> InstallRecord:
    return InstallRecord(
        suite_version="1.0.0",
        manifest_sha256="b" * 64,
        verified_at="2026-08-12T10:00:00+00:00",
        modules=(InstalledModule("old-suite", "1.0.0", "old_suite"),),
    )


class RecordingRunner:
    def __init__(self, codes: list[int] | None = None, verified: bool = True) -> None:
        # Default: ensurepip-bootstrap, ensure-pip, dependencies, components, verification
        self.codes = iter(codes or [0, 0, 0, 0, 0])
        self.commands = []
        self.verified = verified

    def __call__(self, command) -> int:
        self.commands.append(command)
        return next(self.codes)

    def verify(self, _manifest) -> bool:
        return self.verified


def test_dependency_command_is_offline_and_per_user(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")
    # Add a pip wheel to the test release
    (release / "wheelhouse" / "pip-26.1.2-py3-none-any.whl").write_bytes(b"wheel")

    commands = build_pip_commands(release)
    # First command is now ensurepip-bootstrap
    ensurepip_bootstrap_cmd = commands[0].argv
    assert ensurepip_bootstrap_cmd == (sys.executable, "-m", "ensurepip", "--user", "--upgrade")
    
    # Second command is ensure-pip
    ensure_pip_cmd = commands[1].argv
    assert "pip-26.1.2-py3-none-any.whl" in " ".join(ensure_pip_cmd)
    assert "--no-deps" in ensure_pip_cmd
    assert "--force-reinstall" in ensure_pip_cmd

    # Third command is dependencies
    command = commands[2].argv

    assert "--user" in command
    assert "--no-index" in command
    assert "--require-hashes" in command
    assert "--find-links" in command
    assert str(release / "wheelhouse") in command


def test_component_command_installs_only_approved_local_wheels(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")

    command = build_pip_commands(release)[3]

    assert command.stage == "components"
    assert "--no-index" in command.argv
    assert "--force-reinstall" in command.argv
    assert str(release / "packages" / "emolpat-1.1.0-py3-none-any.whl") in command.argv


def test_successful_install_writes_verified_record_atomically(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")
    paths = paths_at(tmp_path / "user")
    runner = RecordingRunner()

    result = install_release(release, runner, paths)

    assert result.ok
    assert result.stage == "record"
    record = read_install_record(paths.install_record)
    assert record is not None
    assert record.suite_version == "1.1.0"
    assert len(record.modules) == 5
    assert not paths.install_record.with_suffix(".json.tmp").exists()
    assert (paths.rollback / "1.1.0" / "manifest.json").is_file()


def test_successful_install_reports_stages_in_order(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")
    # Add a pip wheel to the test release
    (release / "wheelhouse" / "pip-26.1.2-py3-none-any.whl").write_bytes(b"wheel")
    stages = []

    result = install_release(
        release,
        RecordingRunner(),
        paths_at(tmp_path / "user"),
        progress=stages.append,
    )

    assert result.ok
    assert stages == [
        "preflight",
        "ensurepip-bootstrap",
        "ensure-pip",
        "dependencies",
        "components",
        "verification",
        "record",
    ]


def test_failed_update_does_not_write_new_install_record(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")
    paths = paths_at(tmp_path / "user")
    replace_install_record(paths.install_record, old_record())
    # Fails at dependencies stage (index 2)
    runner = RecordingRunner(codes=[0, 0, 9])

    result = install_release(release, runner, paths)

    assert not result.ok
    assert result.stage == "dependencies"
    assert read_install_record(paths.install_record) == old_record()


def test_failed_verification_keeps_previous_record(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")
    paths = paths_at(tmp_path / "user")
    replace_install_record(paths.install_record, old_record())
    # Fails at verification stage (index 4) - verification returns False
    runner = RecordingRunner(codes=[0, 0, 0, 0, 0], verified=False)

    result = install_release(release, runner, paths)

    assert not result.ok
    assert result.stage == "verification"
    assert read_install_record(paths.install_record) == old_record()


def test_failed_update_restores_retained_previous_release(tmp_path: Path) -> None:
    release = create_release(tmp_path / "release")
    # Add a pip wheel to the test release
    (release / "wheelhouse" / "pip-26.1.2-py3-none-any.whl").write_bytes(b"wheel")
    paths = paths_at(tmp_path / "user")
    replace_install_record(paths.install_record, old_record())
    create_release(paths.rollback / "1.0.0", version="1.0.0")
    # Rollback also needs pip wheel
    (paths.rollback / "1.0.0" / "wheelhouse" / "pip-26.1.2-py3-none-any.whl").write_bytes(b"wheel")
    runner = RecordingRunner(codes=[0, 0, 0, 9, 0, 0, 0, 0])

    result = install_release(release, runner, paths)

    assert not result.ok
    assert result.rolled_back
    assert [command.stage for command in runner.commands] == [
            "ensurepip-bootstrap",
            "ensure-pip",
            "dependencies",
            "components",
            "ensurepip-bootstrap",
            "ensure-pip",
            "dependencies",
            "components",
        ]
    assert read_install_record(paths.install_record) == old_record()


def test_subprocess_denial_falls_back_to_in_process_pip(monkeypatch) -> None:
    calls = []

    def denied(*_args, **_kwargs):
        raise PermissionError("blocked by Ivanti")

    monkeypatch.setattr("emolpat.install.subprocess.run", denied)
    monkeypatch.setattr(
        "emolpat.install.run_pip_in_process",
        lambda arguments: calls.append(arguments) or 0,
    )
    command = type("CommandLike", (), {"argv": ("python", "-m", "pip", "install", "x")})()

    assert run_command(command) == 0
    assert calls == [("install", "x")]


def test_ensurepip_bootstrap_is_skipped_when_pip_is_already_available(
    monkeypatch,
) -> None:
    calls = []
    monkeypatch.setattr("emolpat.install.find_spec", lambda _name: object(), raising=False)
    monkeypatch.setattr(
        "emolpat.install.subprocess.run",
        lambda *_args, **_kwargs: calls.append(True),
    )
    command = type(
        "CommandLike",
        (),
        {
            "stage": "ensurepip-bootstrap",
            "argv": (sys.executable, "-m", "ensurepip", "--user", "--upgrade"),
        },
    )()

    assert run_command(command) == 0
    assert calls == []
