"""FR-GRD-004/005: unresolved results cannot carry an unsupported judgment."""

import json
from uuid import UUID

import pytest
from pydantic import TypeAdapter, ValidationError

from services.short_text_contracts import (
    LowConfidenceShortTextGrade,
    PendingShortTextGrade,
    ShortTextResponse,
    UnresolvedShortTextGrade,
)

ATTEMPT = UUID(int=301)
ITEM = UUID(int=302)


@pytest.mark.parametrize("text", ["  synthetic answer  ", "x" * 2000, "Δv = 2\n m/s"])
def test_response_preserves_exact_evidence_without_repr_disclosure(text):
    response = ShortTextResponse(type="SHORT_TEXT", text=text)
    assert response.text == text
    assert text not in repr(response)
    assert ShortTextResponse.model_validate_json(response.model_dump_json()).text == text


@pytest.mark.parametrize("text", ["", " \n\t", "x" * 2001, 10, False, None])
def test_invalid_response_is_rejected_without_error_text_disclosure(text):
    with pytest.raises(ValidationError) as error:
        ShortTextResponse.model_validate({"type": "SHORT_TEXT", "text": text})
    assert "input_value=" not in str(error.value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("score", 0),
        ("points_awarded", 0),
        ("points_possible", 2),
        ("confidence", 1.0),
        ("feedback", {"missing_elements": ["Unsupported judgment"]}),
        ("candidate", {"total_points": 1}),
        ("rubric", {"criterion": "hidden"}),
        ("raw_output", "untrusted"),
        ("response", "synthetic answer"),
        ("provider_error", "private provider data"),
    ],
)
@pytest.mark.parametrize("status", ["PENDING", "LOW_CONFIDENCE"])
def test_unresolved_union_rejects_scores_hidden_content_and_provider_data(field, value, status):
    payload = {"attempt_id": str(ATTEMPT), "item_version_id": str(ITEM), "status": status}
    if status == "LOW_CONFIDENCE":
        payload["fallback"] = {"kind": "REQUEST_REVIEW"}
    payload[field] = value
    with pytest.raises(ValidationError):
        TypeAdapter(UnresolvedShortTextGrade).validate_json(json.dumps(payload))


def test_pending_poll_target_is_derived_from_attempt_not_untrusted_input():
    pending = PendingShortTextGrade(attempt_id=ATTEMPT, item_version_id=ITEM)
    assert pending.model_dump()["poll_url"] == f"/api/v1/attempts/{ATTEMPT}/grade"
    assert TypeAdapter(UnresolvedShortTextGrade).validate_json(pending.model_dump_json()) == pending
    with pytest.raises(ValidationError):
        PendingShortTextGrade.model_validate(
            {"attempt_id": ATTEMPT, "item_version_id": ITEM, "poll_url": "https://example.test"}
        )


@pytest.mark.parametrize("model", [PendingShortTextGrade, LowConfidenceShortTextGrade])
def test_unresolved_result_cannot_claim_mastery_updated(model):
    payload = {"attempt_id": ATTEMPT, "item_version_id": ITEM, "mastery_update_status": "COMPLETED"}
    if model is LowConfidenceShortTextGrade:
        payload["fallback"] = {"kind": "REQUEST_REVIEW"}
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_low_confidence_requires_a_typed_fallback_and_does_not_claim_review_completed():
    for fallback in [None, {}, {"kind": "MODEL_RETRY"}, {"kind": "OBJECTIVE_EQUIVALENT"}]:
        with pytest.raises(ValidationError):
            LowConfidenceShortTextGrade.model_validate(
                {"attempt_id": ATTEMPT, "item_version_id": ITEM, "fallback": fallback}
            )
    result = LowConfidenceShortTextGrade(
        attempt_id=ATTEMPT, item_version_id=ITEM, fallback={"kind": "REQUEST_REVIEW"}
    )
    assert result.model_dump()["fallback"] == {"kind": "REQUEST_REVIEW"}
    equivalent = LowConfidenceShortTextGrade.model_validate_json(
        json.dumps(
            {
                "attempt_id": str(ATTEMPT),
                "item_version_id": str(ITEM),
                "fallback": {"kind": "OBJECTIVE_EQUIVALENT", "session_id": str(UUID(int=303))},
            }
        )
    )
    assert equivalent.fallback.kind == "OBJECTIVE_EQUIVALENT"
