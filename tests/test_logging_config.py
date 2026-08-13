from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from emolpat.logging_config import configure_logging, redact_message
from emolpat.paths import UserPaths


def paths_at(root) -> UserPaths:
    return UserPaths(
        root=root,
        logs=root / "logs",
        install_record=root / "install-record.json",
        rollback=root / "rollback",
    )


def test_redaction_removes_user_shared_and_case_paths() -> None:
    message = redact_message(
        r"C:\Users\alice\patient-123 K:\Clinical\case.xlsx "
        r"\\lab-server\cases\sample-991.txt"
    )

    assert "alice" not in message
    assert "patient-123" not in message
    assert "Clinical" not in message
    assert "lab-server" not in message
    assert message.count("[redacted]") == 3


def test_redaction_removes_patient_like_tokens_outside_paths() -> None:
    message = redact_message("Failed for patient-123 and prøve_9988")

    assert message == "Failed for [redacted] and [redacted]"


def test_configure_logging_uses_bounded_redacting_file_handler(tmp_path) -> None:
    logger = configure_logging(paths_at(tmp_path))

    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, RotatingFileHandler)
    assert handler.maxBytes == 2_000_000
    assert handler.backupCount == 3
    assert logger.level == logging.INFO

    logger.info(r"launch failed at C:\Users\alice\patient-123.txt")
    handler.flush()
    contents = (tmp_path / "logs" / "emolpat.log").read_text(encoding="utf-8")

    assert "alice" not in contents
    assert "patient-123" not in contents
    assert "[redacted]" in contents
