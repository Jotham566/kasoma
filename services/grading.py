"""FR-GRD-001: exact grading from the pinned specification, never prompt prose."""

from uuid import UUID

from services.assessment_contracts import Feedback, GradeView
from services.content_contracts import DraftDocument

GRADER_VERSION = "single-choice-v1"


def grade_choice(
    attempt_id: UUID, version_id: UUID, document: DraftDocument, choice: str
) -> GradeView:
    if choice not in {option.id for option in document.choices}:
        raise ValueError("Unsupported choice")
    correct = choice == document.correct_choice_id
    return GradeView(
        attempt_id=attempt_id,
        item_version_id=version_id,
        score=1.0 if correct else 0.0,
        points_awarded=document.maximum_points if correct else 0,
        points_possible=document.maximum_points,
        grader_version=GRADER_VERSION,
        feedback=Feedback(
            correct_elements=["Your selected answer matches the approved answer."]
            if correct
            else [],
            missing_elements=[]
            if correct
            else ["Your selected answer does not match the approved answer."],
            next_action="Review the worked solution, then continue."
            if correct
            else document.remediation,
        ),
    )
