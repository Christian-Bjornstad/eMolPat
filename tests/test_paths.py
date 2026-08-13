from __future__ import annotations

from pathlib import Path

import pytest

from emolpat.paths import UserPaths


def test_user_paths_use_local_app_data() -> None:
    paths = UserPaths.from_environment(
        {
            "LOCALAPPDATA": r"C:\Users\operator\AppData\Local",
            "USERPROFILE": r"C:\Users\operator",
        }
    )

    assert paths.root == Path(r"C:\Users\operator\AppData\Local") / "eMolPat"
    assert paths.logs == paths.root / "logs"
    assert paths.install_record == paths.root / "install-record.json"
    assert paths.rollback == paths.root / "rollback"


def test_user_paths_fall_back_to_user_profile() -> None:
    paths = UserPaths.from_environment({"USERPROFILE": r"C:\Users\operator"})

    assert paths.root == Path(r"C:\Users\operator\AppData\Local\eMolPat")


def test_user_paths_require_a_windows_user_location() -> None:
    with pytest.raises(RuntimeError, match="Windows user data location"):
        UserPaths.from_environment({})
