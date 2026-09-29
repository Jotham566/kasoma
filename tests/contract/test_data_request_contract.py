"""FR-ID-006: minimal, explicit request intent and safe status projection."""

import json
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.data_request_contracts import DataRequestClaim, DataRequestInput, DataRequestView


@pytest.mark.parametrize(
    "body",
    [
        {"kind": "EXPORT", "affirmative": False},
        {"kind": "DELETE"},
        {"kind": "UNKNOWN", "affirmative": True},
        {"kind": "DELETE", "affirmative": True, "user_id": str(uuid4())},
        {"kind": "EXPORT", "affirmative": True, "comment": "Unnecessary personal information"},
    ],
)
def test_rejects_unconfirmed_or_privileged_inputs(body):
    with pytest.raises(ValidationError):
        DataRequestInput.model_validate(body)


def test_minimized_status_and_no_manual_completion():
    assert set(DataRequestView.model_fields) == {
        "id",
        "kind",
        "status",
        "created_at",
        "reviewed_at",
        "retention_policy",
        "completed_at",
        "retention_due_at",
        "download_expires_at",
    }
    with pytest.raises(ValidationError):
        DataRequestClaim(status="COMPLETED")
    schema = json.loads(Path("packages/analytics-schema/identity-event.schema.json").read_text())
    assert "data_request.created" in schema["properties"]["type"]["enum"]
    assert set(schema["properties"]["payload"]["properties"]) == {"request_id"}
