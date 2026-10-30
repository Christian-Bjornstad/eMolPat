"""Copy and verify portal icons against the immutable component Git objects."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _catalog() -> tuple[dict, dict, Path]:
    resources = PROJECT_ROOT / "src/emolpat/ui/resources"
    components = {
        item["id"]: item
        for item in json.loads(
            (PROJECT_ROOT / "release/components.json").read_text(encoding="utf-8")
        )
    }
    icons = json.loads((resources / "app-icons.json").read_text(encoding="utf-8"))
    if set(icons) != set(components):
        raise RuntimeError("icon catalog must match the approved components")
    filenames = [icon["bundled_file"] for icon in icons.values()]
    if len(set(filenames)) != len(filenames) or any(
        Path(name).name != name or Path(name).suffix not in {".png", ".ico", ".svg"}
        for name in filenames
    ):
        raise RuntimeError("icon catalog requires unique resource filenames")
    return components, icons, resources


def validate_bundled_icons() -> None:
    """Check asset bytes and provenance without needing component checkouts."""
    components, icons, resources = _catalog()
    for module_id, icon in icons.items():
        if icon["commit"] != components[module_id]["commit"]:
            raise RuntimeError(f"icon pin is stale: {module_id}; sync component icons")
        path = resources / icon["bundled_file"]
        if not path.is_file() or digest(path.read_bytes()) != icon["sha256"]:
            raise RuntimeError(f"bundled icon is stale or missing: {module_id}")


def sync_component_icons(component_root: Path, *, write: bool = False) -> None:
    """Use committed bytes, never an uncommitted asset from a working tree."""
    components, icons, resources = _catalog()
    contents = {}
    for module_id, icon in icons.items():
        component = components[module_id]
        repository = component["repository"].rsplit("/", 1)[-1].removesuffix(".git")
        contents[module_id] = subprocess.check_output(
            [
                "git",
                "-C",
                str(component_root / repository),
                "show",
                f"{component['commit']}:{icon['source_file']}",
            ]
        )
    if write:
        for module_id, content in contents.items():
            icon = icons[module_id]
            (resources / icon["bundled_file"]).write_bytes(content)
            icon.update(commit=components[module_id]["commit"], sha256=digest(content))
        (resources / "app-icons.json").write_text(
            json.dumps(icons, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    validate_bundled_icons()
    for module_id, content in contents.items():
        if digest(content) != icons[module_id]["sha256"]:
            raise RuntimeError(f"icon differs from pinned Git source: {module_id}")


def validate_wheel_icons(wheel: Path) -> None:
    """Reject packaging omissions and stale setuptools build output."""
    validate_bundled_icons()
    _components, icons, resources = _catalog()
    with zipfile.ZipFile(wheel) as archive:
        for module_id, icon in icons.items():
            member = f"emolpat/ui/resources/{icon['bundled_file']}"
            if member not in archive.namelist() or (
                digest(archive.read(member)) != icon["sha256"]
            ):
                raise RuntimeError(f"wheel icon is stale or missing: {module_id}")
        member = "emolpat/ui/resources/app-icons.json"
        if member not in archive.namelist() or (
            archive.read(member) != (resources / "app-icons.json").read_bytes()
        ):
            raise RuntimeError("wheel icon catalog is stale or missing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-root", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write and args.component_root is None:
        parser.error("--write requires --component-root")
    if args.component_root is None:
        validate_bundled_icons()
    else:
        sync_component_icons(args.component_root, write=args.write)
    print("Component icons match their pinned source provenance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
