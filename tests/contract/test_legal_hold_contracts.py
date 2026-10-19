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


@pytest.mark.parametrize("kind", ["GRADE", "MASTERY_EVIDENCE", "MASTERY_HISTORY"])
def test_learning_record_hold_uses_exact_uuid(kind):
    record = uuid4()
    body = HoldInput(
        record_type=kind,
        record_id=record,
        decision_reference=uuid4(),
        reason="LEGAL_OBLIGATION",
        expires_at="2027-01-01T12:00:00Z",
        affirmative=True,
    )
    assert body.record_type == kind and body.record_id == record


@pytest.mark.parametrize("kind", ["CHANNEL_INBOUND_RECEIPT", "CHANNEL_OUTBOUND_RECEIPT"])
def test_channel_receipt_kind_is_explicitly_opted_in(kind):
    from services.config import Settings
    from services.legal_hold_contracts import supported_record_types

    assert kind not in supported_record_types(False)
    assert kind in supported_record_types(True)
    assert Settings.model_fields["channel_receipt_holds_enabled"].default is False


@pytest.mark.parametrize("kind", ["DATA_REQUEST_RECEIPT", "EXPORT_JOB_RECEIPT"])
def test_export_evidence_is_separately_gated(kind):
    from services.config import Settings
    from services.legal_hold_contracts import supported_record_types

    assert kind not in supported_record_types(True, True)
    assert kind in supported_record_types(False, False, True)
    assert Settings.model_fields["export_evidence_holds_enabled"].default is False
