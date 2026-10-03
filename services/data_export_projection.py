"""Read-only, allowlisted self-service export; never serialize ORM rows wholesale."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from services.assessment_contracts import GradeView
from services.content_contracts import DraftDocument
from services.data_request_contracts import DataExportBundle
from services.domain.assessment import (
    AssessmentSession,
    Attempt,
    Grade,
    HintUse,
    Reassessment,
    SessionItem,
)
from services.domain.content import ItemVersion
from services.domain.curriculum import Competency, Concept, Subject, Topic
from services.domain.data_requests import DataRequest
from services.domain.flags import ContentFlag
from services.domain.identity import Consent, Identifier, IdentityEvent, LearnerSubject, User
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.domain.messaging import ChannelLink, InboundMessage, OutboundMessage
from services.identity import IdentityError, IdentityService
from services.mastery_engine import Estimate, Evidence

MAX_RECORDS = 10_000
EXCLUSIONS = [
    "Authentication credentials, OTPs, lookup hashes and internal security records.",
    "Guardian contact/name/evidence and staff identities or internal notes.",
    "Answer keys, rubrics, worked solutions, future assignments and selection internals.",
    "Unfinished or abandoned diagnostic grades and calculations depending on sealed evidence.",
    "Content-owned feedback, operational audit internals and third-party records "
    "need separate review.",
]


def project(identity: IdentityService, db: Session, actor: UUID, target: UUID) -> DataExportBundle:
    remaining = MAX_RECORDS

    def rows(query: Select[Any]) -> list[Any]:
        nonlocal remaining
        result = list(db.scalars(query.limit(remaining + 1)))
        remaining -= len(result)
        if remaining < 0:
            raise IdentityError("EXPORT_LIMIT_REACHED", 409)
        return result

    def fields(row: Any, names: str) -> dict[str, Any]:
        result = {}
        for name in names.split():
            value = getattr(row, name)
            result[name] = (
                value.isoformat()
                if isinstance(value, (date, datetime))
                else (str(value) if isinstance(value, UUID) else value)
            )
        return result

    records: dict[str, list[dict[str, Any]]] = {}
    user = db.get(User, actor)
    if user is None:
        raise IdentityError("RESOURCE_NOT_FOUND", 404)
    records["profile"] = [
        fields(user, "id status birth_date created_at")
        | {"display_name": identity.decrypt(user.display_name) if user.display_name else None}
    ]
    records["identifiers"] = [
        fields(r, "type verified_at") | {"value": identity.decrypt(r.normalized_value_encrypted)}
        for r in rows(select(Identifier).where(Identifier.user_id == actor).order_by(Identifier.id))
    ]
    records["subjects"] = [
        fields(r, "id name")
        for r in rows(
            select(Subject)
            .join(LearnerSubject, LearnerSubject.subject_id == Subject.id)
            .where(LearnerSubject.user_id == actor)
            .order_by(Subject.id)
        )
    ]
    records["consents"] = [
        fields(r, "id consent_type basis policy_version granted_at revoked_at")
        for r in rows(select(Consent).where(Consent.user_id == actor).order_by(Consent.id))
    ]
    sessions = rows(
        select(AssessmentSession)
        .where(AssessmentSession.learner_id == actor)
        .order_by(AssessmentSession.id)
    )
    by_session = {r.id: r for r in sessions}
    records["sessions"] = [
        fields(
            r,
            "id subject_id topic_id kind status item_count reason plan_version "
            "started_at expires_at completed_at",
        )
        for r in sessions
    ]
    attempts = rows(select(Attempt).where(Attempt.learner_id == actor).order_by(Attempt.id))
    attempt_ids = {r.id for r in attempts}
    assignments = {
        r.id: r
        for r in rows(
            select(SessionItem)
            .where(SessionItem.id.in_([a.session_item_id for a in attempts]))
            .order_by(SessionItem.id)
        )
    }
    versions = {
        r.id: r
        for r in rows(
            select(ItemVersion)
            .where(ItemVersion.id.in_([a.item_version_id for a in attempts]))
            .order_by(ItemVersion.id)
        )
    }
    visible = {
        a.id
        for a in attempts
        if (
            by_session[assignments[a.session_item_id].session_id].kind != "DIAGNOSTIC"
            or by_session[assignments[a.session_item_id].session_id].status == "COMPLETED"
        )
    }
    records["answers"] = []
    for a in attempts:
        doc = DraftDocument.model_validate(versions[a.item_version_id].document)
        records["answers"].append(
            fields(a, "id item_version_id submitted_at hint_count highest_hint_level channel")
            | {
                "session_id": str(assignments[a.session_item_id].session_id),
                "response": a.response
                if a.response is not None
                else {"type": "SINGLE_CHOICE", "choice_id": a.choice_id},
                "question": {
                    "prompt": doc.prompt,
                    "choices": [c.model_dump() for c in doc.choices],
                },
                "grade_released": a.id in visible,
            }
        )
    records["grades"] = []
    for g in rows(select(Grade).where(Grade.attempt_id.in_(visible)).order_by(Grade.attempt_id)):
        result = GradeView.model_validate(g.result)
        records["grades"].append(
            fields(
                result,
                "attempt_id item_version_id status score points_awarded points_possible "
                "confidence method grader_version",
            )
        )
    records["hints"] = [
        fields(r, "session_item_id level phase created_at")
        for r in rows(select(HintUse).where(HintUse.learner_id == actor).order_by(HintUse.id))
    ]
    evidence = rows(
        select(MasteryEvidence)
        .where(MasteryEvidence.learner_id == actor, MasteryEvidence.attempt_id.in_(visible))
        .order_by(MasteryEvidence.id)
    )
    records["mastery_evidence"] = [
        Evidence.model_validate(r.snapshot).model_dump(mode="json") for r in evidence
    ]
    # Materialized histories may combine sealed and released evidence. Never leak that mixture.
    records["mastery_estimates"] = []
    records["mastery_history"] = []
    projections: list[tuple[str, Select[Any]]] = [
        ("mastery_estimates", select(MasteryEstimate).where(MasteryEstimate.learner_id == actor)),
        (
            "mastery_history",
            select(MasteryHistory).where(MasteryHistory.evidence_id.in_([e.id for e in evidence])),
        ),
    ]
    for section, query in projections:
        for row in rows(query):
            estimate = Estimate.model_validate(row.snapshot)
            if set(estimate.input_attempt_ids) <= visible:
                records[section].append(estimate.model_dump(mode="json"))
    records["reports"] = [
        fields(r, "id attempt_id item_version_id category created_at")
        | {"comment": identity.decrypt(r.comment_encrypted)}
        for r in rows(
            select(ContentFlag).where(ContentFlag.reporter_id == actor).order_by(ContentFlag.id)
        )
    ]
    records["reassessments"] = [
        fields(r, "original_attempt_id session_id basis elapsed_seconds")
        for r in rows(
            select(Reassessment)
            .where(Reassessment.original_attempt_id.in_(attempt_ids))
            .order_by(Reassessment.original_attempt_id)
        )
    ]
    records["data_requests"] = [
        fields(r, "id kind created_at completed_at retention_due_at")
        for r in rows(
            select(DataRequest).where(DataRequest.user_id == actor).order_by(DataRequest.id)
        )
    ]
    records["channel_links"] = [
        fields(r, "id status revision linked_at opted_out_at")
        | {
            "identifier": identity.decrypt(r.external_identifier_encrypted)
            if r.external_identifier_encrypted
            else None
        }
        for r in rows(
            select(ChannelLink).where(ChannelLink.user_id == actor).order_by(ChannelLink.id)
        )
    ]
    records["channel_inbound"] = [
        fields(r, "id command status received_at processed_at")
        for r in rows(
            select(InboundMessage)
            .where(InboundMessage.actor_id == actor)
            .order_by(InboundMessage.id)
        )
    ]
    records["channel_outbound"] = [
        fields(r, "id template status created_at sent_at")
        for r in rows(
            select(OutboundMessage)
            .where(OutboundMessage.actor_id == actor)
            .order_by(OutboundMessage.id)
        )
    ]
    records["account_events"] = [
        fields(r, "type created_at")
        for r in rows(
            select(IdentityEvent)
            .where(
                IdentityEvent.user_id == actor,
                IdentityEvent.type.not_in(["legal_hold.created", "legal_hold.released"]),
            )
            .order_by(IdentityEvent.id)
        )
    ]
    # Only taxonomy names referenced by this account, never content keys or future assignments.
    topic_ids = {r.topic_id for r in sessions if r.topic_id}
    concepts = rows(
        select(Concept).where(Concept.id.in_({e.concept_id for e in evidence})).order_by(Concept.id)
    )
    topic_ids.update(c.topic_id for c in concepts)
    records["concepts"] = [fields(r, "id topic_id name") for r in concepts]
    records["topics"] = [
        fields(r, "id subject_id name")
        for r in rows(select(Topic).where(Topic.id.in_(topic_ids)).order_by(Topic.id))
    ]
    records["competencies"] = [
        fields(r, "id name")
        for r in rows(
            select(Competency)
            .where(Competency.id.in_({e.competency_id for e in evidence}))
            .order_by(Competency.id)
        )
    ]
    return DataExportBundle(
        request_id=target, generated_at=identity.clock(), exclusions=EXCLUSIONS, records=records
    )
