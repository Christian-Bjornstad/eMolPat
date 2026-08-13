from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("filename", "python_script"),
    [
        ("Installer eMolPat.cmd", "install_emolpat.py"),
        ("Start eMolPat.cmd", "start_emolpat.py"),
    ],
)
def test_cmd_uses_ivanti_and_copies_complete_python_command(
    filename: str,
    python_script: str,
) -> None:
    text = (Path("packaging") / filename).read_text(encoding="utf-8")

    assert "pwrgate.exe" in text
    assert "15694" in text
    assert "Set-Clipboard" in text
    assert python_script in text
    assert "runpy.run_path" in text
    assert "run_name=''emolpat_felles''" in text
    assert "[''main'']()" in text
    assert "exec(open(r" not in text
    assert "pause" in text.lower()


@pytest.mark.parametrize(
    ("filename", "clean_import"),
    [
        ("Start eMolPat - Diagnose.cmd", False),
        ("Start eMolPat - Clean import.cmd", True),
    ],
)
def test_diagnostic_cmd_keeps_felles_alive_and_selects_requested_mode(
    filename: str,
    clean_import: bool,
) -> None:
    text = (Path("packaging") / filename).read_text(encoding="utf-8")

    assert "pwrgate.exe" in text
    assert "15694" in text
    assert "diagnose_emolpat_start.py" in text
    assert "runpy.run_path" in text
    assert "run_name=''emolpat_felles''" in text
    assert "[''main'']()" in text
    assert ("EMOLPAT_DIAGNOSTIC_CLEAN_IMPORT" in text) is clean_import
    assert "exec(open(" not in text
    assert "pause" in text.lower()
