from __future__ import annotations

import hashlib
import json
from pathlib import Path

from emolpat.domain import SuiteState
from emolpat.health import evaluate_health, read_install_record
from emolpat.install import install_release
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths
from emolpat.ui.app import PortalOutcome, run_application_loop


class SyntheticWorkstation:
    def __init__(self) -> None:
        self.commands = []

    def __call__(self, command) -> int:
        self.commands.append(command)
        return 0

    def verify(self, _manifest) -> bool:
        return True


class SelectedPortal:
    def __init__(self, manifest, selected: str) -> None:
        self.manifest = manifest
        self.selected = selected
        self.shown = 0

    def __call__(self, _startup_error=None) -> PortalOutcome:
        self.shown += 1
        return PortalOutcome(self.selected)


def synthetic_release(root: Path) -> Path:
    root.mkdir()
    (root / "packages").mkdir()
    (root / "wheelhouse").mkdir()
    lock = b"packaging==25.0 --hash=sha256:" + b"a" * 64
    wheel = b"synthetic-wheel"
    (root / "requirements.lock").write_bytes(lock)
    (root / "packages" / "emolpat-1.0.0-py3-none-any.whl").write_bytes(wheel)
    document = json.loads(Path("tests/fixtures/valid-manifest.json").read_text())
    document["python_requires"] = ">=3.12,<3.15"
    document["files"] = [
        {
            "path": "requirements.lock",
            "sha256": hashlib.sha256(lock).hexdigest(),
        },
        {
            "path": "packages/emolpat-1.0.0-py3-none-any.whl",
            "sha256": hashlib.sha256(wheel).hexdigest(),
        },
    ]
    (root / "manifest.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def test_clean_install_health_selection_and_handoff(tmp_path: Path) -> None:
    release = synthetic_release(tmp_path / "release")
    user_root = tmp_path / "user"
    paths = UserPaths(
        root=user_root,
        logs=user_root / "logs",
        install_record=user_root / "install-record.json",
        rollback=user_root / "rollback",
    )
    workstation = SyntheticWorkstation()

    result = install_release(release, workstation, paths)

    assert result.ok
    manifest = load_manifest(release / "manifest.json")
    record = read_install_record(paths.install_record)
    assert record is not None
    distributions = {item.distribution: item.version for item in record.modules}
    imports = {item.import_name: True for item in record.modules}
    health = evaluate_health(manifest, record, distributions, imports)
    assert health.state is SuiteState.READY

    portal = SelectedPortal(manifest, "hemafrag")
    events = []
    exit_code = run_application_loop(
        portal,
        resolver=lambda value: lambda: events.append(value) or 0,
    )

    assert exit_code == 0
    assert portal.shown == 1
    assert events == ["hemafrag_diagnostics.__main__:main"]
