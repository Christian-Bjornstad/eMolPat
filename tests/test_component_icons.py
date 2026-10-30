from __future__ import annotations

import json
import subprocess
import zipfile

import pytest

from scripts import sync_component_icons as icons


def test_all_bundled_icons_match_their_pinned_source_provenance() -> None:
    icons.validate_bundled_icons()


@pytest.fixture
def icon_project(tmp_path, monkeypatch):
    """One small real Git source, so checks exercise committed asset bytes."""
    root = tmp_path / "portal"
    resources = root / "src/emolpat/ui/resources"
    resources.mkdir(parents=True)
    (root / "release").mkdir()
    component_root = tmp_path / "components"
    source = component_root / "App"
    source.mkdir(parents=True)
    subprocess.run(["git", "init", str(source)], check=True, capture_output=True)
    (source / "icon.png").write_bytes(b"current source icon")
    subprocess.run(["git", "-C", str(source), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(source),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.test",
            "commit",
            "-m",
            "Icon",
        ],
        check=True,
        capture_output=True,
    )
    commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    component = {
        "id": "app",
        "repository": "https://example.test/App.git",
        "commit": commit,
    }
    (root / "release/components.json").write_text(json.dumps([component]))
    metadata = {
        "app": {
            "source_file": "icon.png",
            "bundled_file": "app.png",
            "commit": "0" * 40,
            "sha256": "0" * 64,
        }
    }
    (resources / "app-icons.json").write_text(json.dumps(metadata))
    (resources / "app.png").write_bytes(b"old icon")
    monkeypatch.setattr(icons, "PROJECT_ROOT", root)
    return component_root, source, resources


def test_refresh_copies_the_exact_pinned_commit_even_with_local_changes(icon_project):
    component_root, source, resources = icon_project
    (source / "icon.png").write_bytes(b"uncommitted icon")

    icons.sync_component_icons(component_root, write=True)

    assert (resources / "app.png").read_bytes() == b"current source icon"
    icons.validate_bundled_icons()
    icons.sync_component_icons(component_root)


@pytest.mark.parametrize("change", ["asset", "pin", "source"])
def test_stale_icons_block_the_build(icon_project, change):
    component_root, _source, resources = icon_project
    icons.sync_component_icons(component_root, write=True)
    metadata_path = resources / "app-icons.json"
    metadata = json.loads(metadata_path.read_text())
    if change == "asset":
        (resources / "app.png").write_bytes(b"stale icon")
    elif change == "pin":
        metadata["app"]["commit"] = "0" * 40
    else:
        # Self-consistent copied bytes still have to match the Git source.
        (resources / "app.png").write_bytes(b"wrong source")
        metadata["app"]["sha256"] = icons.digest(b"wrong source")
    metadata_path.write_text(json.dumps(metadata))

    with pytest.raises(RuntimeError, match="app"):
        icons.sync_component_icons(component_root)


@pytest.mark.parametrize("content", [None, b"stale icon", b"current source icon"])
def test_built_wheel_must_include_the_current_icons(icon_project, content):
    component_root, _source, resources = icon_project
    icons.sync_component_icons(component_root, write=True)
    wheel = component_root / "portal.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "emolpat/ui/resources/app-icons.json",
            (resources / "app-icons.json").read_bytes(),
        )
        if content is not None:
            archive.writestr("emolpat/ui/resources/app.png", content)
    if content == b"current source icon":
        icons.validate_wheel_icons(wheel)
    else:
        with pytest.raises(RuntimeError, match="app"):
            icons.validate_wheel_icons(wheel)
