"""Hold forms accept scoped metadata, never narratives or account wildcards."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.legal_hold_contracts import HoldInput, HoldRelease


@pytest.mark.parametrize(
    "change",
    [
        {"record_type": "USER"},
        {"record_id": "*"},
        {"expires_at": None},
        {"expires_at": "2027-01-01T12:00:00"},
        {"expires_at": "infinity"},
        {"affirmative": False},
        {"notes": "Personal narrative"},
        {"decision_reference": "Name"},
    ],
)
def test_hold_rejects_unbounded_or_personal_input(change):
    body = dict(
        record_type="DATA_REQUEST",
        record_id=uuid4(),
        decision_reference=uuid4(),
        reason="LEGAL_OBLIGATION",
        expires_at="2027-01-01T12:00:00Z",
        affirmative=True,
    )
    with pytest.raises(ValidationError):
        HoldInput.model_validate(body | change)


def test_release_requires_affirmative_decision_reference():
    with pytest.raises(ValidationError):
        HoldRelease.model_validate({"affirmative": True})
    with pytest.raises(ValidationError):
        HoldRelease.model_validate({"affirmative": False, "decision_reference": uuid4()})
