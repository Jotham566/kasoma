"""FR-GRD-003/004: independent points and strictly blinded task projections."""

import json
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.grading_review_contracts import AuditReviewInput, BlindedReviewTask


def task_payload():
    version = str(uuid4())
    return {
        "id": str(uuid4()),
        "item_version_id": version,
        "rubric_version_id": version,
        "prompt": "Synthetic label check",
        "response": "  Alpha\n",
        "criteria": [
            {
                "criterion_id": "R1",
                "maximum_points": 1,
                "criterion_text": "Write Alpha",
                "acceptable_evidence": ["Alpha"],
                "common_errors": [],
                "prohibited_inferences": ["Do not infer omitted text"],
            }
        ],
    }


@pytest.mark.parametrize(
    "hidden", ["learner_id", "model_score", "confidence", "ordinal", "band_id", "prior_reviews"]
)
def test_blinded_task_refuses_identity_model_and_sampling_fields(hidden):
    with pytest.raises(ValidationError):
        BlindedReviewTask.model_validate_json(json.dumps(task_payload() | {hidden: "CANARY"}))


def test_task_preserves_answer_without_printing_it():
    task = BlindedReviewTask.model_validate_json(json.dumps(task_payload()))
    assert task.response == "  Alpha\n" and "Alpha" not in repr(task)
    assert set(task.model_dump()) == {
        "id",
        "item_version_id",
        "rubric_version_id",
        "prompt",
        "response",
        "criteria",
    }


@pytest.mark.parametrize("value", [True, "1", -1, 0.5, 21])
def test_expert_points_require_bounded_integers(value):
    with pytest.raises(ValidationError):
        AuditReviewInput.model_validate_json(
            json.dumps(
                {
                    "criterion_points": [{"criterion_id": "R1", "points_awarded": value}],
                    "critical_error": "NONE",
                    "affirmative": True,
                }
            )
        )


def test_review_refuses_duplicate_criteria_and_self_declared_agreement():
    body = {
        "criterion_points": [{"criterion_id": "R1", "points_awarded": 1}],
        "critical_error": "NONE",
        "affirmative": True,
    }
    assert (
        AuditReviewInput.model_validate_json(json.dumps(body)).criterion_points[0].points_awarded
        == 1
    )
    for invalid in (
        body | {"criterion_points": body["criterion_points"] * 2},
        body | {"exact_agreement": True},
        body | {"critical_error": "APPROVED_BY_MODEL"},
    ):
        with pytest.raises(ValidationError):
            AuditReviewInput.model_validate_json(json.dumps(invalid))
