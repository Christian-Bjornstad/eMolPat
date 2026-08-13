from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.build_diagnostic_patch import build_diagnostic_patch


def test_patch_archive_contains_only_three_safe_startup_files(tmp_path: Path) -> None:
    archive = build_diagnostic_patch(tmp_path)

    assert archive.name == "eMolPat-1.0.2-startup-diagnostics.zip"
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.namelist() == [
            "eMolPat-1.0.2-startup-diagnostics/Start eMolPat - Clean import.cmd",
            "eMolPat-1.0.2-startup-diagnostics/Start eMolPat - Diagnose.cmd",
            "eMolPat-1.0.2-startup-diagnostics/diagnose_emolpat_start.py",
        ]
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in bundle.infolist())
        assert not any(name.endswith(".whl") for name in bundle.namelist())
