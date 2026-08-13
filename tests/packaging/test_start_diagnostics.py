from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import ModuleType

NAMESPACE = runpy.run_path(
    "packaging/diagnose_emolpat_start.py",
    run_name="diagnostic_test",
)
clear_emolpat_modules = NAMESPACE["clear_emolpat_modules"]
diagnostic_lines = NAMESPACE["diagnostic_lines"]
main = NAMESPACE["main"]
redact = NAMESPACE["redact"]


def test_redact_hides_user_identity_but_keeps_useful_location_tokens(
    monkeypatch,
    tmp_path: Path,
) -> None:
    profile = tmp_path / "Users" / "Christian"
    local = profile / "AppData" / "Local"
    monkeypatch.setenv("USERPROFILE", str(profile))
    monkeypatch.setenv("LOCALAPPDATA", str(local))

    text = redact(
        f"module={profile / 'module.py'} log={local / 'eMolPat' / 'log.txt'} "
        r"external=C:\Restricted\Python\python.exe"
    )

    assert "Christian" not in text
    assert "%USERPROFILE%" in text
    assert "%LOCALAPPDATA%" in text
    assert r"C:\Restricted" not in text
    assert "python.exe" in text


def test_diagnostic_lines_show_runtime_and_full_redacted_exception(
    monkeypatch,
    tmp_path: Path,
) -> None:
    user_site = tmp_path / "Users" / "Christian" / "site-packages"
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "Users" / "Christian"))
    monkeypatch.setattr(NAMESPACE["site"], "getusersitepackages", lambda: str(user_site))

    try:
        raise ImportError(r"DLL failed at C:\Users\Christian\secret\Qt6Core.dll")
    except ImportError as error:
        lines = diagnostic_lines(error)

    output = "\n".join(lines)
    assert f"Python: {sys.version.split()[0]}" in output
    assert f"Executable: {Path(sys.executable).name}" in output
    assert "User-site: %USERPROFILE%" in output
    assert "eMolPat module:" in output
    assert "Traceback (most recent call last)" in output
    assert "ImportError" in output
    assert "Qt6Core.dll" in output
    assert "Christian" not in output


def test_clear_emolpat_modules_removes_only_emolpat(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "emolpat", ModuleType("emolpat"))
    monkeypatch.setitem(sys.modules, "emolpat.ui", ModuleType("emolpat.ui"))
    unrelated = ModuleType("unrelated")
    monkeypatch.setitem(sys.modules, "unrelated", unrelated)

    removed = clear_emolpat_modules()

    assert removed == ("emolpat", "emolpat.ui")
    assert "emolpat" not in sys.modules
    assert "emolpat.ui" not in sys.modules
    assert sys.modules["unrelated"] is unrelated


def test_main_prints_and_logs_startup_failure(monkeypatch, tmp_path, capsys) -> None:
    local = tmp_path / "local"
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    fake_package = ModuleType("emolpat")
    fake_main = ModuleType("emolpat.__main__")

    def fail() -> int:
        raise RuntimeError("Qt plugin unavailable")

    fake_main.main = fail
    monkeypatch.setitem(sys.modules, "emolpat", fake_package)
    monkeypatch.setitem(sys.modules, "emolpat.__main__", fake_main)

    assert main() == 1

    output = capsys.readouterr().out
    log = local / "eMolPat" / "logs" / "startup-diagnostic.log"
    assert "RuntimeError: Qt plugin unavailable" in output
    assert "RuntimeError: Qt plugin unavailable" in log.read_text(encoding="utf-8")
