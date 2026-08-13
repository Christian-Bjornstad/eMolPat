"""Create a deterministic Windows release ZIP and SHA-256 sidecar."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from emolpat.integrity import sha256_file, verify_release
from emolpat.manifest import load_manifest

FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def create_release_archive(
    release_root: Path,
    destination: Path,
) -> tuple[Path, Path]:
    """Archive one verified release under a single stable top-level path."""
    root = release_root.resolve()
    manifest = load_manifest(root / "manifest.json")
    report = verify_release(root, manifest)
    if not report.ok:
        raise ValueError("release must pass verification before archiving")

    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"eMolPat-{manifest.suite_version}-windows.zip"
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    top_level = f"eMolPat-{manifest.suite_version}"

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zipped:
        for path in sorted(
            (item for item in root.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(root).as_posix(),
        ):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{top_level}/{relative}", FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0o100644 << 16
            zipped.writestr(info, path.read_bytes())

    checksum.write_text(
        f"{sha256_file(archive)}  {archive.name}\n",
        encoding="ascii",
        newline="\n",
    )
    return archive, checksum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    archive, checksum = create_release_archive(arguments.release, arguments.output)
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
