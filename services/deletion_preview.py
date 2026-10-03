"""FR-ID-006/BR-010: advisory relational inventory; never permission to erase."""

from typing import Any
from uuid import UUID

from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.orm import Session

from services.data_request_contracts import DeletionPreview, DeletionSource, RetentionCategory
from services.data_requests import DataRequestService
from services.domain.assessment import (
    AssessmentEvent,
    AssessmentReceipt,
    AssessmentSession,
    Attempt,
    Grade,
    HintUse,
    Reassessment,
    RecommendationSnapshot,
    SessionItem,
)
from services.domain.content import (
    AuditLog,
    ContentEvent,
    ContentImport,
    ContentReceipt,
    ContentReview,
    Item,
    ItemMapping,
    ItemVersion,
)
from services.domain.data_requests import (
    DataExport,
    DataRequest,
    DataRequestReceipt,
    DataRequestReview,
    LegalHold,
    LegalHoldReceipt,
)
from services.domain.flags import ContentFlag, FlagHistory, FlagMutationReceipt
from services.domain.identity import (
    AuthSession,
    Challenge,
    Consent,
    Identifier,
    IdentityEvent,
    LearnerProfile,
    LearnerSubject,
    User,
    UserRole,
)
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.identity import IdentityError, IdentityService
from services.legal_holds import active_count
from services.staff import authorize

COUNT_LIMIT = 10_000
LIMITATIONS = [
    "Advisory counts may change; this is not an execution plan or legal-hold clearance.",
    "Shared rate buckets, operational logs, backups and arbitrary embedded references "
    "need separate review.",
    "WhatsApp/channel links are not implemented; this does not establish channel erasure.",
    "Related staff records may also concern other people and are not account-owned data.",
]


def inventory(db: Session, user: UUID) -> list[DeletionSource]:
    sources: list[DeletionSource] = []

    def add(model: Any, condition: ColumnElement[bool], retention: RetentionCategory) -> None:
        limited = select(1).select_from(model).where(condition).limit(COUNT_LIMIT + 1).subquery()
        count = db.scalar(select(func.count()).select_from(limited)) or 0
        sources.append(
            DeletionSource(
                source=model.__tablename__,
                count=min(count, COUNT_LIMIT),
                at_least=count > COUNT_LIMIT,
                retention=retention,
            )
        )

    sessions = select(AssessmentSession.id).where(AssessmentSession.learner_id == user)
    attempts = select(Attempt.id).where(Attempt.learner_id == user)
    evidence = select(MasteryEvidence.id).where(MasteryEvidence.learner_id == user)
    requests = select(DataRequest.id).where(DataRequest.user_id == user)
    holds = select(LegalHold.id).where(LegalHold.request_id.in_(requests))
    flags = select(ContentFlag.id).where(ContentFlag.reporter_id == user)
    authored = select(Item.id).where(Item.author_id == user)
    versions = select(ItemVersion.id).where(
        or_(ItemVersion.author_id == user, ItemVersion.item_id.in_(authored))
    )
    identifiers = select(Identifier.lookup_hash).where(Identifier.user_id == user)
    for model, condition in [
        (User, User.id == user),
        (Identifier, Identifier.user_id == user),
        (AuthSession, AuthSession.user_id == user),
        (LearnerProfile, LearnerProfile.user_id == user),
        (LearnerSubject, LearnerSubject.user_id == user),
    ]:
        add(model, condition, "REMOVE_DIRECT_LINKAGE")
    add(
        Challenge,
        or_(
            Challenge.user_id == user,
            and_(Challenge.user_id.is_(None), Challenge.lookup_hash.in_(identifiers)),
        ),
        "TRANSIENT_EXPIRY",
    )
    add(Consent, Consent.user_id == user, "SIX_YEARS_AFTER_CLOSURE_OR_WITHDRAWAL")
    for model, condition in [
        (IdentityEvent, IdentityEvent.user_id == user),
        (AssessmentSession, AssessmentSession.learner_id == user),
        (SessionItem, SessionItem.session_id.in_(sessions)),
        (Attempt, Attempt.learner_id == user),
        (Grade, Grade.attempt_id.in_(attempts)),
        (AssessmentReceipt, AssessmentReceipt.learner_id == user),
        (AssessmentEvent, AssessmentEvent.session_id.in_(sessions)),
        (RecommendationSnapshot, RecommendationSnapshot.learner_id == user),
        (HintUse, HintUse.learner_id == user),
        (Reassessment, Reassessment.original_attempt_id.in_(attempts)),
        (MasteryEvidence, MasteryEvidence.learner_id == user),
        (MasteryEstimate, MasteryEstimate.learner_id == user),
        (MasteryHistory, MasteryHistory.evidence_id.in_(evidence)),
    ]:
        add(model, condition, "ANONYMIZATION_REVIEW")
    for model, condition in [
        (DataRequest, DataRequest.user_id == user),
        (
            DataRequestReview,
            or_(DataRequestReview.request_id.in_(requests), DataRequestReview.actor_id == user),
        ),
        (
            DataRequestReceipt,
            or_(DataRequestReceipt.request_id.in_(requests), DataRequestReceipt.actor_id == user),
        ),
    ]:
        add(model, condition, "SIX_YEARS_AFTER_COMPLETION")
    add(LegalHold, LegalHold.request_id.in_(requests), "SIX_YEARS_AFTER_COMPLETION")
    add(LegalHoldReceipt, LegalHoldReceipt.hold_id.in_(holds), "SIX_YEARS_AFTER_COMPLETION")
    add(DataExport, DataExport.request_id.in_(requests), "EXPIRES_AFTER_24_HOURS")
    add(ContentFlag, ContentFlag.reporter_id == user, "TWENTY_FOUR_MONTHS_AFTER_RESOLUTION")
    add(FlagHistory, FlagHistory.flag_id.in_(flags), "TWENTY_FOUR_MONTHS_AFTER_RESOLUTION")
    add(
        FlagMutationReceipt,
        FlagMutationReceipt.flag_id.in_(flags),
        "TWENTY_FOUR_MONTHS_AFTER_RESOLUTION",
    )
    # Staff provenance is deliberately separate from owned learning records.
    for model, condition in [
        (UserRole, UserRole.user_id == user),
        (ContentImport, ContentImport.actor_id == user),
        (DataRequestReview, DataRequestReview.actor_id == user),
        (LegalHold, or_(LegalHold.created_by == user, LegalHold.released_by == user)),
        (LegalHoldReceipt, LegalHoldReceipt.actor_id == user),
        (Item, Item.author_id == user),
        (ItemVersion, ItemVersion.id.in_(versions)),
        (ItemMapping, ItemMapping.item_version_id.in_(versions)),
        (
            ContentReview,
            or_(ContentReview.reviewer_id == user, ContentReview.item_version_id.in_(versions)),
        ),
        (
            ContentReceipt,
            or_(ContentReceipt.actor_id == user, ContentReceipt.item_version_id.in_(versions)),
        ),
        (ContentEvent, ContentEvent.item_version_id.in_(versions)),
    ]:
        add(model, condition, "STAFF_PROVENANCE_REVIEW")
    # Additional staff flag links can overlap the learner-owned inventory above.
    for model, condition in [
        (ContentFlag, ContentFlag.owner_id == user),
        (FlagHistory, or_(FlagHistory.actor_id == user, FlagHistory.owner_id == user)),
        (FlagMutationReceipt, FlagMutationReceipt.actor_id == user),
    ]:
        add(model, condition, "STAFF_PROVENANCE_REVIEW")
    add(
        AuditLog,
        or_(
            AuditLog.actor_id == user,
            AuditLog.target_id == user,
            AuditLog.target_id.in_(requests),
            AuditLog.target_id.in_(holds),
            AuditLog.target_id.in_(flags),
            AuditLog.target_id.in_(authored),
            AuditLog.target_id.in_(versions),
        ),
        "SIX_YEARS_AFTER_CLOSURE_OR_WITHDRAWAL",
    )
    return sources


def preview(
    identity: IdentityService, token: str, target: UUID, request_id: UUID
) -> DeletionPreview:
    with identity.transaction() as db:
        actor = authorize(identity, db, token, {"ADMIN"}, recent=True)[0]
        if not identity.rate(db, f"deletion-preview:{actor}", 10, 60):
            raise IdentityError("RATE_LIMITED", 429)
        request = db.get(DataRequest, target)
        if request is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        if request.user_id == actor:
            raise IdentityError("SELF_REVIEW_FORBIDDEN", 403)
        if request.kind != "DELETE":
            raise IdentityError("DELETE_REQUIRED", 409)
        review = db.get(DataRequestReview, target)
        if review is None or review.actor_id != actor:
            raise IdentityError("REVIEW_OWNERSHIP_REQUIRED", 403)
        if request.completed_at is not None:
            raise IdentityError("REQUEST_COMPLETED", 409)
        sources = inventory(db, request.user_id)
        held_count, held_at_least = active_count(db, request.user_id, identity.clock())
        result = DeletionPreview(
            active_legal_holds=held_count,
            active_holds_at_least=held_at_least,
            request_id=target,
            observed_at=identity.clock(),
            sources=sources,
            blockers=[
                "LEGAL_HOLD_COVERAGE_INCOMPLETE",
                "ERASURE_PROCESSOR_UNAVAILABLE",
                "ANONYMIZATION_REVIEW_REQUIRED",
            ],
            limitations=LIMITATIONS,
        )
        if held_count:
            result.blockers.append("ACTIVE_RECORD_HOLDS")
        if any(s.count and s.retention == "STAFF_PROVENANCE_REVIEW" for s in sources):
            result.blockers.append("STAFF_RECORDS_REQUIRE_REVIEW")
        DataRequestService(identity).audit(
            db, actor, target, "data_request.deletion_previewed", request_id
        )
        return result
