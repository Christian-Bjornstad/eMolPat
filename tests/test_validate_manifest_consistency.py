from scripts.validate_manifest_consistency import validate_manifest_consistency


def test_validator_accepts_exact_bundled_suite_version() -> None:
    assert validate_manifest_consistency("1.2.2")


def test_validator_rejects_release_name_mismatch(capsys) -> None:
    assert not validate_manifest_consistency("1.0.8-test")
    assert "Version mismatch" in capsys.readouterr().out
