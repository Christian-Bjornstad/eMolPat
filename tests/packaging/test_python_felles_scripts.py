from __future__ import annotations

import runpy
import site
import sys
from pathlib import Path

import pytest

PACKAGING = Path("packaging")


@pytest.mark.parametrize("name", ["install_emolpat.py", "start_emolpat.py"])
def test_activate_user_site_places_current_user_first(
    monkeypatch,
    tmp_path: Path,
    name: str,
) -> None:
    namespace = runpy.run_path(str(PACKAGING / name), run_name="launcher_test")
    user_site = tmp_path / "user-site"
    monkeypatch.setattr(site, "getusersitepackages", lambda: str(user_site))
    monkeypatch.setattr(sys, "path", ["existing", str(user_site)])

    result = namespace["activate_user_site"]()

    assert result == user_site
    assert user_site.is_dir()
    assert sys.path[0] == str(user_site)
    assert sys.path.count(str(user_site)) == 1


def test_installer_bootstraps_emolpat_from_local_release_only() -> None:
    text = (PACKAGING / "install_emolpat.py").read_text(encoding="utf-8")

    assert "EMOLPAT_RELEASE_ROOT" in text
    assert "wheelhouse" in text
    assert "packages" in text
    assert "install_release" in text
    assert "http://" not in text and "https://" not in text


def test_start_script_invokes_installed_suite_entrypoint() -> None:
    text = (PACKAGING / "start_emolpat.py").read_text(encoding="utf-8")

    assert "from emolpat.__main__ import main" in text
    assert "raise SystemExit(main())" in text
