from __future__ import annotations

import json
from pathlib import Path

import pytest

from emolpat.domain import APPROVED_MODULE_IDS
from emolpat.manifest import ManifestError, load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "valid-manifest.json"


def manifest_data() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def write_manifest(tmp_path: Path, data: dict[str, object]) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_manifest_returns_the_four_approved_modules() -> None:
    manifest = load_manifest(FIXTURE)

    assert manifest.schema_version == 1
    assert manifest.suite_version == "1.0.0"
    assert manifest.python_requires == ">=3.14,<3.15"
    assert tuple(module.id for module in manifest.modules) == APPROVED_MODULE_IDS
    assert manifest.module("hemafrag").entry_point == (
        "hemafrag_diagnostics.__main__:main"
    )


def test_load_manifest_rejects_duplicate_module_ids(tmp_path: Path) -> None:
    data = manifest_data()
    modules = data["modules"]
    assert isinstance(modules, list)
    modules[1]["id"] = "hemafrag"

    with pytest.raises(ManifestError, match="duplicate module id: hemafrag"):
        load_manifest(write_manifest(tmp_path, data))


def test_load_manifest_requires_exactly_the_approved_modules(tmp_path: Path) -> None:
    data = manifest_data()
    modules = data["modules"]
    assert isinstance(modules, list)
    modules.pop()

    with pytest.raises(ManifestError, match="approved module set"):
        load_manifest(write_manifest(tmp_path, data))


def test_load_manifest_rejects_unknown_schema_version(tmp_path: Path) -> None:
    data = manifest_data()
    data["schema_version"] = 2

    with pytest.raises(ManifestError, match="unsupported schema version: 2"):
        load_manifest(write_manifest(tmp_path, data))


@pytest.mark.parametrize(
    "entry_point",
    ["missing_colon", "module:", ":main", "module.path:main.extra", "bad-name:main"],
)
def test_load_manifest_rejects_invalid_entry_points(
    tmp_path: Path, entry_point: str
) -> None:
    data = manifest_data()
    modules = data["modules"]
    assert isinstance(modules, list)
    modules[0]["entry_point"] = entry_point

    with pytest.raises(ManifestError, match="invalid entry point"):
        load_manifest(write_manifest(tmp_path, data))


def test_manifest_module_rejects_unknown_id() -> None:
    manifest = load_manifest(FIXTURE)

    with pytest.raises(KeyError, match="unknown module id: missing"):
        manifest.module("missing")
