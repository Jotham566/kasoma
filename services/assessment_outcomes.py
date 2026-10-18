"""Internal owned-attempt result decoding; callers authorize disclosure first."""

import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment_contracts import AttemptGrade, GradeView
from services.domain.assessment import Attempt, Grade, SessionItem
from services.domain.grading_work import GradingWorkRow
from services.grading_work_store import apply, snapshot
from services.identity import IdentityError, IdentityService
from services.rubric_grade_contracts import RubricGradeView
from services.rubric_grade_protection import (
    GradeProtectionError,
    ResultBinding,
    StoredRubricGrade,
    reveal_result,
)
from services.short_text_answers import AnswerBinding, reveal_answer
from services.short_text_contracts import (
    LowConfidenceShortTextGrade,
    PendingShortTextGrade,
    RequestReviewFallback,
)
from services.short_text_workflow import expire_work


def answer_binding(attempt: Attempt) -> AnswerBinding:
    return AnswerBinding(
        learner_id=attempt.learner_id,
        attempt_id=attempt.id,
        session_item_id=attempt.session_item_id,
        item_version_id=attempt.item_version_id,
        rubric_version_id=attempt.item_version_id,
    )


def result_binding(db: Session, attempt: Attempt) -> ResultBinding:
    item = db.get(SessionItem, attempt.session_item_id)
    if item is None or item.grading_band_id is None:
        raise ValueError("Missing pinned grading band")
    return ResultBinding(answer=answer_binding(attempt), band_id=item.grading_band_id)


def response_projection(identity: IdentityService, attempt: Attempt) -> dict[str, object]:
    if attempt.response is not None and attempt.response.get("type") == "SHORT_TEXT":
        response = reveal_answer(attempt.response["ciphertext"], answer_binding(attempt), identity)
        return response.model_dump(mode="json")
    return (
        attempt.response
        if attempt.response is not None
        else {"type": "SINGLE_CHOICE", "choice_id": attempt.choice_id}
    )


def grade_projection(
    identity: IdentityService,
    db: Session,
    attempt: Attempt,
    grade: Grade,
    *,
    pinned_binding: ResultBinding | None = None,
) -> GradeView | RubricGradeView:
    if grade.result.get("method") == "RUBRIC_MODEL":
        stored = StoredRubricGrade.model_validate_json(json.dumps(grade.result))
        return reveal_result(stored, pinned_binding or result_binding(db, attempt), identity)
    return GradeView.model_validate(grade.result)


def outcome(identity: IdentityService, db: Session, attempt_id: UUID) -> AttemptGrade:
    attempt = db.get(Attempt, attempt_id)
    if attempt is None:
        raise IdentityError("RESOURCE_NOT_FOUND", 404)
    grade = db.get(Grade, attempt_id)
    if grade is not None:
        try:
            return grade_projection(identity, db, attempt, grade)
        except GradeProtectionError:
            raise IdentityError("GRADE_UNAVAILABLE", 409) from None
    row = db.scalar(
        select(GradingWorkRow).where(GradingWorkRow.attempt_id == attempt_id).with_for_update()
    )
    if row is None:
        raise IdentityError("RESOURCE_NOT_FOUND", 404)
    work = expire_work(snapshot(row), identity.clock())
    apply(db, row, work)
    if work.status == "LOW_CONFIDENCE":
        return LowConfidenceShortTextGrade(
            attempt_id=attempt.id,
            item_version_id=attempt.item_version_id,
            fallback=RequestReviewFallback(kind="REQUEST_REVIEW"),
        )
    if work.status == "GRADED":
        raise IdentityError("GRADE_UNAVAILABLE", 409)
    return PendingShortTextGrade(attempt_id=attempt.id, item_version_id=attempt.item_version_id)
