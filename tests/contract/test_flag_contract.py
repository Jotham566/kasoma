"""FR-GRD-009/FR-CNT-006: bounded text, strict state and retention schedule."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from services.flag_contracts import FlagInput, FlagUpdate
from services.flags import retention_due


@pytest.mark.parametrize(
    "payload",
    [
        {"category": "UNKNOWN"},
        {"category": "OTHER", "comment": "x" * 1001},
        {"category": "OTHER", "reporter_id": "forged"},
        {"category": "OTHER", "status": "RESOLVED"},
    ],
)
def test_report_rejects_unknown_and_privileged_fields(payload):
    with pytest.raises(ValidationError):
        FlagInput.model_validate(payload)


@pytest.mark.parametrize(
    "change",
    [
        {"expected_revision": 0},
        {"status": "OPEN"},
        {"status": "RESOLVED", "resolution": " "},
        {"owner_id": "forged"},
        {"resolution": "x" * 1001},
        {"priority": "URGENT"},
    ],
)
def test_triage_bounds_and_terminal_resolution(change):
    with pytest.raises(ValidationError):
        FlagUpdate.model_validate(
            {"expected_revision": 1, "status": "IN_REVIEW", "priority": "NORMAL"} | change
        )


def test_trim_calendar_retention_and_safe_registered_events():
    assert FlagInput(category="OTHER", comment=" test ").comment == "test"
    assert retention_due(datetime(2024, 2, 29, tzinfo=UTC)) == datetime(2026, 2, 28, tzinfo=UTC)
    schema = json.loads(Path("packages/analytics-schema/content-event.schema.json").read_text())
    assert {"content.flag.created", "content.flag.updated"} <= set(
        schema["properties"]["type"]["enum"]
    )
    assert not {"comment", "reporter_id", "answer", "resolution"} & schema["properties"].keys()
