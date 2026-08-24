from __future__ import annotations

from pathlib import Path

from scripts.build_suite import assemble_release
from scripts.verify_suite import verify_suite
from tests.test_build_suite import create_inputs


def test_verifier_rejects_a_changed_wheel(tmp_path: Path) -> None:
    packages, dependencies = create_inputs(tmp_path)
    root = assemble_release("1.2.0", tmp_path / "dist", packages, dependencies)

    assert verify_suite(root) == 0
    next((root / "packages").glob("*.whl")).write_bytes(b"changed")
    assert verify_suite(root) == 1
