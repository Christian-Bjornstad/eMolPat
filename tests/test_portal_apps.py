import sys
from pathlib import Path
from types import SimpleNamespace


def test_molstat_adapter_opens_gui_with_existing_settings_path(monkeypatch, tmp_path):
    from emolpat.entrypoints import launch_molstat

    app_data = tmp_path / "Local App Data"
    monkeypatch.setenv("LOCALAPPDATA", str(app_data))
    calls = []
    monkeypatch.setitem(
        sys.modules, "molstat.cli",
        SimpleNamespace(main=lambda argv: calls.append(argv) or 7),
    )

    assert launch_molstat() == 7
    assert calls == [
        ["gui", "--settings", str(app_data / "MolStat" / "settings.json")]
    ]
    assert not app_data.exists()


def test_molstat_adapter_uses_standalone_launcher_fallback(monkeypatch, tmp_path):
    from emolpat.entrypoints import launch_molstat

    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    calls = []
    monkeypatch.setitem(
        sys.modules, "molstat.cli",
        SimpleNamespace(main=lambda argv: calls.append(argv)),
    )

    assert launch_molstat() == 0
    assert calls[0][-1] == str(
        tmp_path / "AppData" / "Local" / "MolStat" / "settings.json"
    )
