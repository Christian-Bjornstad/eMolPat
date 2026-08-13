from __future__ import annotations

from pathlib import Path

import pytest

from emolpat.domain import HealthReport, SuiteManifest, SuiteState
from emolpat.manifest import load_manifest


@pytest.fixture
def manifest() -> SuiteManifest:
    return load_manifest(Path("tests/fixtures/valid-manifest.json"))


@pytest.fixture
def ready_report() -> HealthReport:
    return HealthReport(
        state=SuiteState.READY,
        suite_version="1.0.0",
        issues=(),
    )
