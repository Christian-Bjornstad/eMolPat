from __future__ import annotations

from pathlib import Path


def test_release_workflow_is_tag_scoped_and_publishes_only_verified_assets() -> None:
    text = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
    job_environment = text.split("    env:\n", 1)[1].split("    steps:\n", 1)[0]

    assert 'tags: ["v*.*.*"]' in text
    assert "workflow_dispatch:" in text
    assert "version:" in text
    assert "windows-latest" in text
    assert 'python-version: "3.14"' in text
    assert "contents: write" in text
    assert "python -m pytest -q" in text
    assert "python -m ruff check ." in text
    assert "scripts/checkout_components.py" in text
    assert "scripts/test_components.py" in text
    assert "scripts/build_suite.py" in text
    assert "scripts/verify_suite.py" in text
    assert "scripts/smoke_installed_suite.py" in text
    assert "release-smoke" in text
    assert "scripts/archive_release.py" in text
    assert 'GH_TOKEN: ${{ github.token }}' in text
    assert "QT_QPA_PLATFORM: minimal" in job_environment
    assert 'PYTEST_ADDOPTS: "-x -vv"' in job_environment
    assert 'dist/eMolPat-$version-windows.zip"' in text
    assert 'dist/eMolPat-$version-windows.zip.sha256"' in text
    assert "gh release create" in text
    assert "dist/*.whl" not in text
