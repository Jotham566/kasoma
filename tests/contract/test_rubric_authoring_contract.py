"""Authored rubric contracts are distinct from enabled learner answer contracts."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.assessment_contracts import SubmitAnswer
from services.content_contracts import CreateDraft, DraftDocument
from services.rubric_contracts import RubricDraft
from services.whatsapp_format import supports


def criterion():
    return {
        "criterion_id": "R1",
        "maximum_points": 1,
        "criterion_text": "Name the synthetic label.",
        "acceptable_evidence": ["Alpha"],
        "common_errors": [],
        "prohibited_inferences": [],
    }


def test_absent_rubric_preserves_legacy_canonical_request():
    original = CreateDraft(subject_id=uuid4(), document=DraftDocument(), change_reason="Synthetic")
    payload = original.model_dump(mode="json")
    assert "rubric" not in payload["document"]
    explicit = payload | {"document": payload["document"] | {"rubric": None}}
    assert CreateDraft.model_validate(explicit).model_dump(mode="json") == payload


def test_duplicate_rubric_keys_are_rejected():
    with pytest.raises(ValidationError):
        RubricDraft(criteria=[criterion(), criterion()])


def test_review_only_short_text_is_not_a_learner_or_channel_response():
    document = DraftDocument(
        response_type="SHORT_TEXT",
        partial_credit="CRITERION_SUM",
        rubric={"criteria": [criterion()]},
    )
    assert not supports(document)
    with pytest.raises(ValidationError):
        SubmitAnswer.model_validate(
            {"session_item_id": uuid4(), "response": {"type": "SHORT_TEXT", "text": "Alpha"}}
        )
