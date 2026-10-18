"""FR-GRD-008: owned one-item transfer assessment with immutable selection provenance."""

from datetime import timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment_contracts import SessionView
from services.content_contracts import DraftDocument
from services.domain.assessment import (
    AssessmentReceipt,
    AssessmentSession,
    Attempt,
    Grade,
    Reassessment,
    SessionItem,
)
from services.domain.content import ContentReview, ItemVersion
from services.identity import IdentityError
from services.mastery_engine import fingerprint
from services.reassessment_engine import CONFIG, near_duplicate, same_skill, select_candidate

if TYPE_CHECKING:
    from services.assessment import AssessmentService


def access(
    service: "AssessmentService",
    token: str,
    original_id: UUID,
    key: UUID | None = None,
    request: UUID | None = None,
) -> SessionView:
    identity = service.identity
    with Session(identity.engine) as db, db.begin():
        actor = service.authorize(db, token)
        original = db.scalar(
            select(Attempt).where(Attempt.id == original_id, Attempt.learner_id == actor)
        )
        if original is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        assignment = db.get(SessionItem, original.session_item_id)
        if assignment is None:
            raise ValueError("Missing original assignment")
        parent = service.owned(db, actor, assignment.session_id)
        service.authorize(db, token, parent.subject_id)
        if parent.kind != "REVISION":
            raise IdentityError("REASSESSMENT_NOT_ALLOWED", 403)
        if db.get(Grade, original.id) is None:
            raise IdentityError("REASSESSMENT_NOT_ALLOWED", 409)
        digest = identity.digest("assessment", "reassessment:" + str(original_id))
        if key:
            service.replay(db, actor, key, digest)
        binding = db.get(Reassessment, original_id)
        if binding is None:
            if key is None:
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            if not identity.rate(db, "assessment-start:" + str(actor), 30, 3600):
                raise IdentityError("USAGE_LIMIT_REACHED", 429)
            source = service.content.eligible_version(
                db, original.item_version_id, parent.subject_id, synthetic=True
            )
            source_doc = DraftDocument.model_validate(source.document)
            seen = list(
                db.scalars(
                    select(ItemVersion)
                    .join(SessionItem, SessionItem.item_version_id == ItemVersion.id)
                    .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
                    .where(
                        AssessmentSession.learner_id == actor, SessionItem.served_at.is_not(None)
                    )
                )
            )
            seen_ids = {v.item_id for v in seen}
            seen_prompts = [DraftDocument.model_validate(v.document).prompt for v in seen]
            candidates = []
            for version in service.diagnostics.candidates(db, actor, parent.subject_id):
                document = DraftDocument.model_validate(version.document)
                if (
                    version.item_id in seen_ids
                    or not same_skill(source_doc, document)
                    or any(near_duplicate(document.prompt, prompt) for prompt in seen_prompts)
                ):
                    continue
                relation = None
                for claim_version, doc, target_id in [
                    (source, source_doc, version.id),
                    (version, document, source.id),
                ]:
                    claim = next((c for c in doc.equivalents if c.version_id == target_id), None)
                    if claim:
                        approvals = list(
                            db.scalars(
                                select(ContentReview).where(
                                    ContentReview.item_version_id == claim_version.id,
                                    ContentReview.content_hash == claim_version.content_hash,
                                    ContentReview.review_round == claim_version.review_round,
                                    ContentReview.decision == "APPROVE",
                                )
                            )
                        )
                        if approvals:
                            relation = {
                                "claim_version_id": str(claim_version.id),
                                "confidence": claim.confidence,
                                "review_ids": sorted(str(r.id) for r in approvals),
                            }
                            break
                candidates.append(
                    {
                        "version_id": str(version.id),
                        "content_hash": version.content_hash,
                        "basis": "EQUIVALENT" if relation else "SAME_SKILL_DIFFICULTY",
                        "relationship": relation,
                    }
                )
            if not candidates:
                raise IdentityError("REASSESSMENT_UNAVAILABLE", 409)
            snapshot = {
                "configuration": CONFIG,
                "original_version_id": str(source.id),
                "original_content_hash": source.content_hash,
                "candidates": sorted(candidates, key=lambda c: str(c["version_id"])),
            }
            selected = select_candidate(snapshot)
            target = db.get(ItemVersion, UUID(selected["version_id"]))
            if target is None:
                raise ValueError("Missing selected item")
            # Stable lock order avoids reciprocal learner selections deadlocking.
            for version_id in sorted([source.id, target.id], key=str):
                service.content.assessment_version(
                    db,
                    version_id,
                    parent.subject_id,
                    assigned_band_id=assignment.grading_band_id
                    if version_id == source.id
                    else None,
                )
            now = identity.clock()
            session = AssessmentSession(
                id=uuid4(),
                learner_id=actor,
                subject_id=parent.subject_id,
                topic_id=target.topic_id,
                kind="REASSESSMENT",
                status="ACTIVE",
                item_count=1,
                reason="Try a new question on the same skill after reviewing your feedback.",
                plan_version=str(CONFIG["version"]),
                started_at=now,
                expires_at=now + timedelta(days=identity.settings.assessment_session_days),
            )
            db.add(session)
            db.flush()
            db.add(
                SessionItem(
                    id=uuid4(),
                    session_id=session.id,
                    item_version_id=target.id,
                    position=1,
                    reason=session.reason,
                    grading_band_id=service.assignment_band(db, target),
                )
            )
            db.flush()
            binding = Reassessment(
                original_attempt_id=original_id,
                session_id=session.id,
                item_version_id=target.id,
                basis=selected["basis"],
                elapsed_seconds=(now - original.submitted_at).total_seconds(),
                snapshot=snapshot,
                input_hash=fingerprint(snapshot),
            )
            db.add(binding)
            if request is None:
                raise ValueError("Request ID required")
            service.event(db, session.id, "reassessment.started", request, original_id)
            db.flush()
        if key and db.get(AssessmentReceipt, (actor, key)) is None:
            db.add(
                AssessmentReceipt(
                    learner_id=actor, key=key, request_hash=digest, session_id=binding.session_id
                )
            )
            db.flush()
        return service.view(db, service.owned(db, actor, binding.session_id))
