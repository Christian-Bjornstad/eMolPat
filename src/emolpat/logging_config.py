"""Bounded technical logging that excludes clinical and user-identifying paths."""

from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler

from emolpat.paths import UserPaths

WINDOWS_PATH = re.compile(
    r"(?:[A-Za-z]:\\|\\\\)[^\s,;]+",
    flags=re.IGNORECASE,
)
PATIENT_LIKE_TOKEN = re.compile(
    r"\b(?:patient|pasient|sample|prøve|prove)[-_ ]?\d+[A-Za-z0-9_-]*\b",
    flags=re.IGNORECASE,
)


def redact_message(message: str) -> str:
    """Remove paths and conservative patient/sample-like identifiers."""
    without_paths = WINDOWS_PATH.sub("[redacted]", message)
    return PATIENT_LIKE_TOKEN.sub("[redacted]", without_paths)


class RedactingFormatter(logging.Formatter):
    """Redact only after logging has safely rendered a complete message."""

    def format(self, record: logging.LogRecord) -> str:
        return redact_message(super().format(record))


def configure_logging(paths: UserPaths) -> logging.Logger:
    """Create the suite's sole bounded, per-user technical log."""
    paths.logs.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        paths.logs / "emolpat.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        RedactingFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger = logging.getLogger("emolpat")
    for existing in logger.handlers:
        existing.close()
    logger.handlers[:] = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
