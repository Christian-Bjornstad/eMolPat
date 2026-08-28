"""Build one self-contained, immutable eMolPat release directory."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass, replace
from email.parser import Parser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename

from emolpat.components import load_components
from emolpat.domain import FileDigest
from emolpat.integrity import sha256_file
from emolpat.manifest import load_manifest
from scripts.validate_manifest_consistency import validate_manifest_consistency

COMPONENT_DIRECTORIES = {
    "hemafrag": "HemaFrag-Diagnostics",
    "igh-merge": "IGH",
    "vpm-tolkning": "Archer-prosess",
    "mpn-tolkning": "MPN-Tolkning",
    "lvms-stat": "LVMS-STAT",
    "molkey": "MolKey",
}
APPROVED_DISTRIBUTIONS = {
    "emolpat",
    "hemafrag-diagnostics",
    "igh-merge",
    "archer-prosess",
    "mpn-tolkning",
    "lvms-stat",
    "molkey",
}


@dataclass(frozen=True)
class PythonTarget:
    python_version: str
    abi: str
    platform: str
    python_requires: str
    requirements_file: Path


PYTHON_314 = PythonTarget(
    python_version="314",
    abi="cp314",
    platform="win_amd64",
    python_requires=">=3.14,<3.15",
    requirements_file=PROJECT_ROOT / "release" / "requirements-py314.in",
)


def _normalize_wheel(path: Path) -> None:
    """Rewrite ZIP metadata in stable member order with a fixed safe timestamp."""
    temporary = path.with_suffix(".normalized.whl")
    with zipfile.ZipFile(path, "r") as source, zipfile.ZipFile(
        temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as target:
        for name in sorted(source.namelist()):
            original = source.getinfo(name)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = original.external_attr
            info.create_system = original.create_system
            target.writestr(info, source.read(name))
    temporary.replace(path)


def _copy_files(paths: list[Path], destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=False)
    copied = []
    for source in sorted(paths, key=lambda item: item.name.casefold()):
        target = destination / source.name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def _locked_requirement(path: Path) -> str:
    stem = path.name.removesuffix(".whl")
    distribution, version, *_tags = stem.split("-")
    normalized = distribution.replace("_", "-")
    return f"{normalized}=={version} --hash=sha256:{sha256_file(path)}"


def assemble_release(
    version: str,
    output: Path,
    package_wheels: list[Path],
    dependency_wheels: list[Path],
    target: PythonTarget = PYTHON_314,
) -> Path:
    """Assemble already-built inputs into a deterministic verified layout."""
    package_versions = {}
    for wheel in package_wheels:
        name, wheel_version, _build, _tags = parse_wheel_filename(wheel.name)
        normalized = canonicalize_name(name)
        if normalized in package_versions:
            raise RuntimeError(f"duplicate package wheel: {normalized}")
        package_versions[normalized] = str(wheel_version)
    if set(package_versions) != APPROVED_DISTRIBUTIONS:
        raise RuntimeError("release must contain exactly the seven approved distributions")

    template = load_manifest(
        PROJECT_ROOT / "src" / "emolpat" / "ui" / "resources" / "suite-manifest.json"
    )
    
    # Validate manifest version matches release version
    if template.suite_version != version:
        raise RuntimeError(
            f"bundled manifest version '{template.suite_version}' does not match "
            f"release version '{version}'. Update src/emolpat/ui/resources/suite-manifest.json"
        )
    
    # Validate no placeholder SHA256 hashes
    for file_digest in template.files:
        if file_digest.sha256 == "a" * 64:
            raise RuntimeError(
                f"placeholder SHA256 detected in manifest for '{file_digest.path}'. "
                f"Update with actual hash before building."
            )
    
    for module in template.modules:
        if package_versions[module.distribution] != module.version:
            raise RuntimeError(
                f"component wheel version does not match manifest: {module.distribution}"
            )

    root = output.resolve() / f"eMolPat-{version}"
    if root.exists():
        raise FileExistsError(f"release already exists: {root}")
    root.mkdir(parents=True)
    packages = _copy_files(package_wheels, root / "packages")
    dependencies = _copy_files(dependency_wheels, root / "wheelhouse")

    bootstraps = []
    packaging_root = PROJECT_ROOT / "packaging"
    if packaging_root.is_dir():
        for filename in (
            "install_emolpat.py",
            "start_emolpat.py",
        ):
            source = packaging_root / filename
            if source.is_file():
                bootstrap_target = root / filename
                shutil.copy2(source, bootstrap_target)
                bootstraps.append(bootstrap_target)

    lock_lines = sorted(_locked_requirement(path) for path in dependencies)
    lock = root / "requirements.lock"
    lock.write_text("\n".join(lock_lines) + "\n", encoding="utf-8", newline="\n")

    declared_paths = [lock, *packages, *dependencies, *bootstraps]
    digests = tuple(
        FileDigest(
            path=path.relative_to(root).as_posix(),
            sha256=sha256_file(path),
        )
        for path in sorted(declared_paths, key=lambda item: item.relative_to(root).as_posix())
    )
    manifest = replace(
        template,
        suite_version=version,
        python_requires=target.python_requires,
        files=digests,
    )
    document = asdict(manifest)
    (root / "manifest.json").write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return root


def _git_text(source: Path, *arguments: str) -> str:
    result = subprocess.run(
        ("git", *arguments),
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def assert_clean_pinned_checkouts(component_root: Path) -> list[Path]:
    """Require exact component commits and no tracked source modifications."""
    components = load_components(PROJECT_ROOT / "release" / "components.json")
    roots = []
    for component in components:
        source = component_root / COMPONENT_DIRECTORIES[component.id]
        if _git_text(source, "rev-parse", "HEAD") != component.commit:
            raise RuntimeError(f"component is not at approved commit: {component.id}")
        if _git_text(source, "status", "--porcelain", "--untracked-files=no"):
            raise RuntimeError(f"component has tracked changes: {component.id}")
        roots.append(source)
    return roots


def _build_wheel(source: Path, destination: Path) -> None:
    subprocess.run(
        (
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            str(source),
            "--wheel-dir",
            str(destination),
        ),
        check=True,
    )


def _download_dependencies(destination: Path, target: PythonTarget) -> None:
    subprocess.run(
        (
            sys.executable,
            "-m",
            "pip",
            "download",
            "--dest",
            str(destination),
            "--only-binary=:all:",
            "--platform",
            target.platform,
            "--implementation",
            "cp",
            "--python-version",
            target.python_version,
            "--abi",
            target.abi,
            "--no-deps",
            "-r",
            str(target.requirements_file),
        ),
        check=True,
    )


def _validate_dependency_matrix(
    package_wheels: list[Path],
    dependency_wheels: list[Path],
) -> None:
    """Prove every active wheel requirement is present at an allowed version."""
    versions = {}
    for wheel in (*package_wheels, *dependency_wheels):
        name, version, _build, _tags = parse_wheel_filename(wheel.name)
        normalized = canonicalize_name(name)
        previous = versions.get(normalized)
        if previous is not None and previous != version:
            raise RuntimeError(f"conflicting wheel versions for {normalized}")
        versions[normalized] = version

    for wheel in package_wheels:
        with zipfile.ZipFile(wheel) as archive:
            metadata_name = next(
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            )
            metadata = Parser().parsestr(
                archive.read(metadata_name).decode("utf-8", errors="strict")
            )
        for value in metadata.get_all("Requires-Dist", []):
            requirement = Requirement(value)
            if requirement.marker and not requirement.marker.evaluate({"extra": ""}):
                continue
            actual = versions.get(canonicalize_name(requirement.name))
            if actual is None or actual not in requirement.specifier:
                raise RuntimeError(
                    f"unsatisfied dependency for {wheel.name}: {requirement}"
                )


def build_suite(
    version: str,
    output: Path,
    component_root: Path,
    target: PythonTarget = PYTHON_314,
) -> Path:
    """Build seven package wheels, collect Windows dependencies, and assemble."""
    if not validate_manifest_consistency(version):
        raise ValueError(
            f"suite version {version!r} does not match the bundled manifest"
        )
    component_sources = assert_clean_pinned_checkouts(component_root.resolve())
    with tempfile.TemporaryDirectory(prefix="emolpat-build-") as temporary:
        staging = Path(temporary)
        package_dir = staging / "packages"
        dependency_dir = staging / "dependencies"
        package_dir.mkdir()
        dependency_dir.mkdir()
        _build_wheel(PROJECT_ROOT, package_dir)
        for source in component_sources:
            _build_wheel(source, package_dir)
        if len(list(package_dir.glob("*.whl"))) != 7:
            raise RuntimeError("suite build must produce exactly seven package wheels")
        _download_dependencies(dependency_dir, target)
        _validate_dependency_matrix(
            list(package_dir.glob("*.whl")),
            list(dependency_dir.glob("*.whl")),
        )
        for wheel in package_dir.glob("*.whl"):
            _normalize_wheel(wheel)
        return assemble_release(
            version,
            output,
            list(package_dir.glob("*.whl")),
            list(dependency_dir.glob("*.whl")),
            target,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--component-root", type=Path, required=True)
    arguments = parser.parse_args()
    root = build_suite(arguments.version, arguments.output, arguments.component_root)
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
