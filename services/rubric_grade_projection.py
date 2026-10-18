"""Project a validated candidate without granting scoring or disclosure authority."""

from uuid import UUID

from services.rubric_grade_contracts import RubricGradeView
from services.short_text_validation import (
    ShortTextCandidate,
    SyntheticRubricContext,
    validate_candidate,
)


def project_candidate(
    *,
    attempt_id: UUID,
    candidate: ShortTextCandidate,
    context: SyntheticRubricContext,
    response: str,
    hint_count: int = 0,
    highest_hint_level: int = 0,
) -> RubricGradeView:
    """Internal result formatting only, after independent eligibility/dual-pass checks.

    Revalidate evidence and authored feedback even for an already-built candidate.
    The result contains answer excerpts: never log it or persist unencrypted copies.
    A high self-reported confidence grants no authorization to store or return a score.
    """
    context = SyntheticRubricContext.model_validate_json(context.model_dump_json())
    checked = validate_candidate(
        candidate.model_dump_json(), context=context, response=response, flagged=False
    )
    if checked.candidate is None:
        raise ValueError("Invalid rubric result")
    result = checked.candidate
    return RubricGradeView(
        attempt_id=attempt_id,
        item_version_id=context.item_version_id,
        rubric_version_id=context.rubric_version_id,
        score=result.total_points / context.maximum_points,
        points_awarded=result.total_points,
        points_possible=context.maximum_points,
        confidence=result.confidence,
        hint_count=hint_count,
        highest_hint_level=highest_hint_level,
        grader_version="rubric-dual-pass-v1",
        criterion_results=result.criterion_results,
        detected_misconception_ids=result.detected_misconception_ids,
        feedback=result.feedback,
    )
