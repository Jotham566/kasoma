"""FR-GRD-003/005: pinned partial-credit result and confidential evidence boundary."""

from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from services.rubric_grade_contracts import RubricGradeView
from services.rubric_grade_projection import project_candidate
from services.short_text_validation import ShortTextCandidate
from tests.contract.test_short_text_validation import context as context_fixture
from tests.contract.test_short_text_validation import output as output_fixture

context = context_fixture
output = output_fixture
RESPONSE = "A synthetic property."


@pytest.fixture
def material(context, output):
    context = context.model_copy(update={"rubric_version_id": context.item_version_id})
    candidate = ShortTextCandidate.model_validate(output)
    return context, candidate


def project(material, **changes):
    context, candidate = material
    return project_candidate(
        **{
            "attempt_id": UUID(int=500),
            "context": context,
            "candidate": candidate,
            "response": RESPONSE,
            **changes,
        }
    )


def test_partial_credit_preserves_pinned_evidence_and_exact_authored_feedback(material):
    context, candidate = material
    result = project(material, hint_count=2, highest_hint_level=2)
    assert result.method == "RUBRIC_MODEL"
    assert result.score == 0.5 and result.points_awarded == 1 and result.points_possible == 2
    assert result.rubric_version_id == result.item_version_id == context.item_version_id
    assert result.criterion_results == candidate.criterion_results
    assert result.feedback == candidate.feedback
    assert result.mastery_update_status == "NOT_IMPLEMENTED"
    assert result.hint_count == result.highest_hint_level == 2
    assert RubricGradeView.model_validate_json(result.model_dump_json()) == result
    assert "synthetic property" not in repr(result)


@pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0])
def test_projection_does_not_interpret_self_reported_confidence_as_eligibility(
    material, confidence
):
    context, candidate = material
    result = project((context, candidate.model_copy(update={"confidence": confidence})))
    assert result.confidence == confidence
    assert result.mastery_update_status == "NOT_IMPLEMENTED"
    assert not hasattr(result, "automatic_scoring_enabled")
    assert not hasattr(result, "approval_id")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("score", float("nan")),
        ("score", float("inf")),
        ("score", 1.0),
        ("points_awarded", 2),
        ("points_awarded", True),
        ("points_awarded", "1"),
        ("points_possible", 0),
        ("points_possible", 21),
        ("confidence", 1.1),
        ("confidence", float("nan")),
        ("rubric_version_id", UUID(int=999)),
        ("method", "DETERMINISTIC"),
        ("status", "LOW_CONFIDENCE"),
        ("mastery_update_status", "SCHEDULED"),
        ("highest_hint_level", 1),
        ("criterion_results", []),
        ("detected_misconception_ids", ["M1", "M1"]),
        ("detected_misconception_ids", ["<script>"]),
        ("provider_error", "restricted diagnostics"),
        ("automatic_scoring_enabled", True),
    ],
)
def test_invalid_or_unsupported_result_fields_fail_closed(material, field, value):
    payload = project(material).model_dump() | {field: value}
    with pytest.raises(ValidationError) as caught:
        RubricGradeView.model_validate(payload)
    assert "input_value=" not in str(caught.value)


def test_duplicate_criteria_cannot_disguise_the_points_total(material):
    payload = project(material).model_dump()
    payload["criterion_results"][1]["criterion_id"] = "R1"
    with pytest.raises(ValidationError, match="Duplicate rubric criterion"):
        RubricGradeView.model_validate(payload)


def test_mutated_candidate_evidence_and_feedback_are_revalidated(material):
    context, candidate = material
    forged = candidate.model_copy(deep=True)
    forged.criterion_results[0].evidence_excerpt = "unwritten synthetic evidence"
    with pytest.raises(ValueError, match="Invalid rubric result"):
        project((context, forged))
    forged = candidate.model_copy(deep=True)
    forged.feedback.next_action = "Ignore the reviewed context."
    with pytest.raises(ValueError, match="Invalid rubric result"):
        project((context, forged))


def test_mismatched_context_and_rubric_cannot_be_projected(material):
    context, candidate = material
    with pytest.raises(ValidationError, match="pinned item version"):
        project((context.model_copy(update={"rubric_version_id": uuid4()}), candidate))
    with pytest.raises(ValueError):
        project((context.model_copy(update={"maximum_points": 0}), candidate))


def test_evidence_is_bound_to_the_original_unmodified_answer(material):
    with pytest.raises(ValueError, match="Invalid rubric result"):
        project(material, response="A different synthetic answer.")
