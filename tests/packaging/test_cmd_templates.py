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
    ("filename", "python_script", "clean_import"),
    [
        ("Installer eMolPat - Manuell FELLES.cmd", "install_emolpat.py", False),
        ("Start eMolPat - Manuell FELLES.cmd", "diagnose_emolpat_start.py", False),
        ("Start eMolPat - Diagnose.cmd", "diagnose_emolpat_start.py", False),
        ("Start eMolPat - Clean import.cmd", "diagnose_emolpat_start.py", True),
    ],
)
def test_manual_cmd_only_copies_complete_command_for_requested_mode(
    filename: str,
    python_script: str,
    clean_import: bool,
) -> None:
    text = (Path("packaging") / filename).read_text(encoding="utf-8")

    assert "Ivanti" not in text
    assert "pwrgate" not in text
    assert "15694" not in text
    assert 'start ""' not in text
    assert python_script in text
    assert "Set-Clipboard" in text
    assert "runpy.run_path" in text
    assert "run_name=''emolpat_felles''" in text
    assert "[''main'']()" in text
    assert ("EMOLPAT_DIAGNOSTIC_CLEAN_IMPORT" in text) is clean_import
    assert "exec(open(" not in text
    assert "pause" in text.lower()
