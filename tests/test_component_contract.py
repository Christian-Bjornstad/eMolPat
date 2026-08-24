from __future__ import annotations

import re
from pathlib import Path

import pytest

from emolpat.components import ComponentContractError, load_components

COMPONENTS = Path("release/components.json")


def test_every_component_has_an_immutable_revision() -> None:
    components = load_components(COMPONENTS)

    assert [component.id for component in components] == [
        "hemafrag",
        "igh-merge",
        "vpm-tolkning",
        "mpn-tolkning",
        "lvms-stat",
        "molkey",
    ]
    assert all(re.fullmatch(r"[0-9a-f]{40}", item.commit) for item in components)
    assert {item.import_name for item in components} == {
        "hemafrag_diagnostics",
        "igh_merge",
        "archer_processor",
        "mpn_tolkning",
        "lvms_stat",
        "molkey",
    }
    assert components[2].commit == "2b0a29de99bc89c2c2a8417679746d634d670847"
    assert components[-1].commit == "a01b5df13fc05bb0d2013d730405be85f25addf4"


def test_component_entrypoints_are_callable_paths() -> None:
    components = load_components(COMPONENTS)

    assert {item.entry_point for item in components} == {
        "hemafrag_diagnostics.__main__:main",
        "igh_merge.__main__:main",
        "archer_processor.__main__:main",
        "mpn_tolkning.__main__:main",
        "lvms_stat.portal:main",
        "molkey.__main__:main",
    }


def test_load_components_rejects_a_moving_branch_reference(tmp_path: Path) -> None:
    path = tmp_path / "components.json"
    path.write_text(
        """[{"id":"hemafrag","repository":"https://example.test/repo.git",\
"commit":"main","distribution":"hemafrag-diagnostics",\
"import_name":"hemafrag_diagnostics",\
"entry_point":"hemafrag_diagnostics.__main__:main",\
"test_command":["python","-m","pytest","-q"]}]""",
        encoding="utf-8",
    )

    with pytest.raises(ComponentContractError, match="immutable 40-character commit"):
        load_components(path)
