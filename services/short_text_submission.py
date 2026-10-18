"""Owned encrypted submission/receipt/work transaction; no model call here."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from services.assessment_contracts import DiagnosticReceipt
from services.assessment_outcomes import answer_binding
from services.domain.assessment import AssessmentReceipt, AssessmentSession, Attempt, SessionItem
from services.domain.content import ItemVersion
from services.grading_work_store import enqueue
from services.hints import counts
from services.identity import IdentityError
from services.short_text_answers import protect_answer
from services.short_text_contracts import PendingShortTextGrade, ShortTextResponse

if TYPE_CHECKING:
    from services.assessment import AssessmentService


def submit_encrypted(
    service: "AssessmentService",
    db: Session,
    actor: UUID,
    session: AssessmentSession,
    item: SessionItem,
    version: ItemVersion,
    response: ShortTextResponse,
    attempt_id: UUID,
    key: UUID,
    request: UUID,
    fingerprint: str,
) -> PendingShortTextGrade | DiagnosticReceipt:
    if item.grading_band_id is None:
        raise IdentityError("CONTENT_NOT_APPROVED", 409)
    hint_count, highest = counts(db, item.id)
    attempt = Attempt(
        id=attempt_id,
        learner_id=actor,
        session_item_id=item.id,
        item_version_id=version.id,
        choice_id=None,
        response=None,
        submitted_at=service.identity.clock(),
        hint_count=hint_count,
        highest_hint_level=highest,
        channel="WEB",
    )
    ciphertext = protect_answer(response, answer_binding(attempt), service.identity)
    attempt.response = {
        "type": "SHORT_TEXT",
        "ciphertext": ciphertext,
        "rubric_version_id": str(version.id),
    }
    db.add(attempt)
    db.flush()
    enqueue(db, attempt.id, request, service.identity.clock())
    db.add(
        AssessmentReceipt(
            learner_id=actor,
            key=key,
            request_hash=fingerprint,
            session_id=session.id,
            attempt_id=attempt.id,
        )
    )
    service.event(db, session.id, "attempt.saved", request, attempt.id)
    db.flush()
    if session.kind != "DIAGNOSTIC" and service.pending(db, session.id) is None:
        session.status, session.completed_at = "COMPLETED", service.identity.clock()
        service.event(db, session.id, "session.completed", request)
    return (
        DiagnosticReceipt(attempt_id=attempt.id)
        if session.kind == "DIAGNOSTIC"
        else (PendingShortTextGrade(attempt_id=attempt.id, item_version_id=version.id))
    )
