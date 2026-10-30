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
    monkeypatch.setattr(sys, "version_info", (3, 14))
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


def test_bootstrap_scripts_use_their_extracted_release_directory() -> None:
    installer = (PACKAGING / "install_emolpat.py").read_text(encoding="utf-8")
    starter = (PACKAGING / "start_emolpat.py").read_text(encoding="utf-8")

    assert "Path(__file__).resolve().parent" in installer
    assert "DEFAULT_RELEASE_ROOT" not in installer
    assert 'os.environ["EMOLPAT_RELEASE_ROOT"]' in installer
    assert 'os.environ["EMOLPAT_RELEASE_ROOT"]' in starter


@pytest.mark.parametrize("name", ["install_emolpat.py", "start_emolpat.py"])
@pytest.mark.parametrize("version", [(3, 12), (3, 13), (3, 15)])
def test_bootstrap_rejects_non_314_python(
    monkeypatch,
    name: str,
    version: tuple[int, int],
) -> None:
    namespace = runpy.run_path(str(PACKAGING / name), run_name="launcher_test")
    monkeypatch.setattr(sys, "version_info", version)

    with pytest.raises(RuntimeError, match="støttes ikke"):
        namespace["activate_user_site"]()


@pytest.mark.parametrize("name", ["install_emolpat.py", "start_emolpat.py"])
def test_bootstrap_accepts_python_314(
    monkeypatch,
    tmp_path: Path,
    name: str,
) -> None:
    namespace = runpy.run_path(str(PACKAGING / name), run_name="launcher_test")
    monkeypatch.setattr(sys, "version_info", (3, 14))
    monkeypatch.setattr(site, "getusersitepackages", lambda: str(tmp_path / "site"))

    assert namespace["activate_user_site"]() == tmp_path / "site"


def test_start_script_invokes_installed_suite_entrypoint() -> None:
    text = (PACKAGING / "start_emolpat.py").read_text(encoding="utf-8")

    assert "from emolpat.__main__ import bundled_manifest, main" in text
    assert "raise SystemExit(main())" in text


def test_installer_ignores_previous_release_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("EMOLPAT_RELEASE_ROOT", str(tmp_path / "old-release"))
    namespace = runpy.run_path(str(PACKAGING / "install_emolpat.py"))
    assert namespace["release_root"]() == PACKAGING.resolve()


@pytest.mark.parametrize("name", ["install_emolpat.py", "start_emolpat.py"])
def test_launchers_discard_cached_portal_modules(monkeypatch, tmp_path, name):
    import types

    namespace = runpy.run_path(str(PACKAGING / name))
    stale = types.ModuleType("emolpat")
    monkeypatch.setitem(sys.modules, "emolpat", stale)
    monkeypatch.setitem(sys.modules, "emolpat.__main__", stale)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    def inspect_then_stop():
        assert "emolpat" not in sys.modules
        assert "emolpat.__main__" not in sys.modules
        raise RuntimeError("controlled bootstrap stop")

    monkeypatch.setitem(
        namespace["main"].__globals__, "activate_user_site", inspect_then_stop
    )
    cached = {
        key: value
        for key, value in sys.modules.items()
        if key == "emolpat" or key.startswith("emolpat.")
    }
    try:
        assert namespace["main"]() == 1
    finally:
        sys.modules.update(cached)


def test_start_refuses_an_older_installed_portal():
    text = (PACKAGING / "start_emolpat.py").read_text(encoding="utf-8")
    assert "bundled_manifest().suite_version != expected" in text
