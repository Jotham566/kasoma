"""ADR-057 bounded source/decision metadata, not narratives or resumable material."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.channel_preservation_contracts import PreservationCapture, PreservationSource
from services.config import Settings
from services.legal_hold_contracts import supported_record_types


def source():
    return {
        "source_kind": "CHANNEL_CONVERSATION_SNAPSHOT",
        "source_link_id": str(uuid4()),
        "link_revision": 1,
    }


def decision():
    return source() | {
        "source_version": "a" * 64,
        "decision_reference": str(uuid4()),
        "reason": "LEGAL_OBLIGATION",
        "expires_at": "2027-10-19T00:00:00Z",
        "affirmative": True,
    }


@pytest.mark.parametrize("revision", [0, -1, True, "1", 1.5, 2_147_483_648])
def test_revision_is_an_exact_positive_database_integer(revision):
    with pytest.raises(ValidationError):
        PreservationSource.model_validate(source() | {"link_revision": revision})


@pytest.mark.parametrize(
    "change",
    [
        {"source_kind": "CHANNEL_INBOUND_RECEIPT"},
        {"source_link_id": "*"},
        {"conversation_id": str(uuid4())},
        {"source_version": "a" * 63},
        {"source_version": "a" * 65},
        {"source_version": "A" * 64},
        {"source_version": "a" * 64 + "\n"},
        {"source_version": "💥" * 64},
        {"expires_at": "infinity"},
        {"expires_at": "2027-10-19T00:00:00"},
        {"affirmative": False},
        {"decision_reference": "Personal narrative"},
        {"reason": "OTHER"},
        {"contact": "synthetic-restricted"},
        {"message": "synthetic-restricted"},
        {"token": "synthetic-restricted"},
    ],
)
def test_capture_rejects_unbounded_ambiguous_or_confidential_input(change):
    with pytest.raises(ValidationError):
        PreservationCapture.model_validate(decision() | change)


def test_default_disabled_creation_is_independent_of_receipt_holds():
    assert Settings.model_fields["channel_preservation_enabled"].default is False
    for receipt_flag in (True, False):
        assert "CHANNEL_LINK_SNAPSHOT" not in supported_record_types(receipt_flag)
        assert "CHANNEL_CONVERSATION_SNAPSHOT" in supported_record_types(receipt_flag, True)
