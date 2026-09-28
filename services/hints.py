"""Reviewed hint disclosure; authoritative usage shares the answer/consent transaction."""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment_contracts import HintRequest, HintState, RevealedHint
from services.content_contracts import DraftDocument
from services.domain.assessment import AssessmentReceipt, Attempt, HintUse, SessionItem
from services.identity import IdentityError

if TYPE_CHECKING:
    from services.assessment import AssessmentService


def uses(db: Session, item: UUID) -> list[HintUse]:
    return list(
        db.scalars(select(HintUse).where(HintUse.session_item_id == item).order_by(HintUse.level))
    )


def counts(db: Session, item: UUID) -> tuple[int, int]:
    before = [h for h in uses(db, item) if h.phase == "BEFORE_ANSWER"]
    return len(before), max((h.level for h in before), default=0)


def state(db: Session, item: UUID, doc: DraftDocument, through: int = 3) -> HintState:
    disclosed = [h for h in uses(db, item) if h.level <= through]
    return HintState(
        session_item_id=item,
        hints=[
            RevealedHint(level=h.level, text=doc.hints[h.level - 1], phase=h.phase)
            for h in disclosed
        ],
        has_more_hints=len(disclosed) < len(doc.hints),
    )


def access(
    assessment: "AssessmentService",
    token: str,
    *,
    session_id: UUID | None = None,
    item_id: UUID | None = None,
    attempt_id: UUID | None = None,
    body: HintRequest | None = None,
    key: UUID | None = None,
    request: UUID | None = None,
) -> HintState:
    identity = assessment.identity
    with Session(identity.engine) as db, db.begin():
        actor = assessment.authorize(db, token)
        if attempt_id is not None:
            attempt = db.scalar(
                select(Attempt).where(Attempt.id == attempt_id, Attempt.learner_id == actor)
            )
            if attempt is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            item = db.get(SessionItem, attempt.session_item_id)
            session_id = item.session_id if item else None
        else:
            item = db.scalar(
                select(SessionItem).where(
                    SessionItem.id == item_id, SessionItem.session_id == session_id
                )
            )
        if item is None or session_id is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        session = assessment.owned(db, actor, session_id)
        assessment.authorize(db, token, session.subject_id)
        if session.kind != "REVISION":
            raise IdentityError("HINTS_DISABLED", 403)
        version = assessment.content.assessment_version(
            db, item.item_version_id, session.subject_id
        )
        document = DraftDocument.model_validate(version.document)
        if item.served_at is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if body is None:
            return state(db, item.id, document)
        if key is None or request is None:
            raise ValueError("Hint mutations require idempotency and request IDs")
        phase = "AFTER_ANSWER" if attempt_id else "BEFORE_ANSWER"
        fingerprint = identity.digest(
            "assessment", f"hint:{item.id}:{phase}:" + body.model_dump_json()
        )
        receipt = assessment.replay(db, actor, key, fingerprint)
        if receipt and receipt.hint_use_id:
            use = db.get(HintUse, receipt.hint_use_id)
            if use is None:
                raise ValueError("Missing committed hint receipt")
            return state(db, item.id, document, use.level)
        if attempt_id is None:
            if session.status != "ACTIVE":
                raise IdentityError("SESSION_NOT_ACTIVE", 409)
            pending = assessment.pending(db, session.id)
            if pending is None or pending.id != item.id:
                raise IdentityError("ITEM_ALREADY_ANSWERED", 409)
        current = uses(db, item.id)
        if body.expected_hint_level != len(current):
            raise IdentityError("VERSION_CONFLICT", 409)
        if len(current) >= len(document.hints):
            raise IdentityError("HINT_UNAVAILABLE", 409)
        use = HintUse(
            id=uuid4(),
            learner_id=actor,
            session_item_id=item.id,
            level=len(current) + 1,
            phase=phase,
            created_at=identity.clock(),
        )
        db.add(use)
        db.flush()
        db.add(
            AssessmentReceipt(
                learner_id=actor,
                key=key,
                request_hash=fingerprint,
                session_id=session.id,
                hint_use_id=use.id,
            )
        )
        assessment.event(
            db,
            session.id,
            "hint.used",
            request,
            attempt_id,
            hint_count=len(current) + 1,
            highest_hint_level=use.level,
        )
        db.flush()
        return state(db, item.id, document)
