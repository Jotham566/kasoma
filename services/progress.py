"""Owned progress and keyset history. Never materialize new learning evidence on reads."""

import base64
import hmac
import json
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from services.domain.assessment import AssessmentSession, Attempt, Grade, Reassessment, SessionItem
from services.domain.content import ItemMapping, ItemVersion
from services.domain.curriculum import Competency, Concept, Subject, Topic
from services.domain.mastery import MasteryEvidence
from services.identity import IdentityError
from services.mastery_engine import Evidence
from services.progress_contracts import (
    ProgressAction,
    ProgressView,
    SessionHistoryEntry,
    SessionHistoryPage,
)
from services.progress_engine import summarize

if TYPE_CHECKING:
    from services.assessment import AssessmentService


def progress(service: "AssessmentService", token: str, subject_id: UUID) -> ProgressView:
    with Session(service.identity.engine) as db, db.begin():
        actor = service.authorize(db, token, subject_id)
        if not service.identity.rate(db, "progress-read:" + str(actor), 60, 60):
            raise IdentityError("USAGE_LIMIT_REACHED", 429)
        subject = db.get(Subject, subject_id)
        if subject is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        at = service.identity.clock()
        topics = list(
            db.scalars(select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.name))
        )
        concepts = {
            c.id: c.topic_id
            for c in db.scalars(select(Concept).where(Concept.topic_id.in_([t.id for t in topics])))
        }
        rows = db.scalars(
            select(MasteryEvidence)
            .join(Attempt, Attempt.id == MasteryEvidence.attempt_id)
            .join(Grade, Grade.attempt_id == Attempt.id)
            .join(SessionItem, SessionItem.id == Attempt.session_item_id)
            .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
            .where(
                MasteryEvidence.learner_id == actor,
                AssessmentSession.learner_id == actor,
                AssessmentSession.subject_id == subject_id,
                MasteryEvidence.concept_id.in_(concepts),
                Grade.result["status"].as_string() == "GRADED",
                or_(
                    AssessmentSession.kind != "DIAGNOSTIC", AssessmentSession.status == "COMPLETED"
                ),
            )
        )
        evidence = [Evidence.model_validate(row.snapshot) for row in rows]
        skills = {
            (concept, competency)
            for concept, competency in db.execute(
                select(ItemVersion.concept_id, ItemMapping.competency_id)
                .join(ItemMapping, ItemMapping.item_version_id == ItemVersion.id)
                .where(
                    ItemVersion.concept_id.in_(concepts),
                    ItemVersion.status == "APPROVED",
                    ItemVersion.synthetic.is_(True),
                )
            )
            if concept is not None
        }
        skills.update((e.source.concept_id, e.source.competency_id) for e in evidence)
        summary = summarize(subject.id, subject.name, skills, evidence, at)
        active = db.scalar(
            select(AssessmentSession).where(
                AssessmentSession.learner_id == actor,
                AssessmentSession.subject_id == subject_id,
                AssessmentSession.kind == "DIAGNOSTIC",
                AssessmentSession.status == "ACTIVE",
                AssessmentSession.expires_at > at,
            )
        )
        action = (
            ProgressAction(
                kind="CONTINUE_DIAGNOSTIC", session_id=active.id, label="Continue your diagnostic"
            )
            if active
            else ProgressAction(
                kind="START_DIAGNOSTIC", label="Gather more evidence with a diagnostic"
            )
            if summary.confidence < 0.25
            else ProgressAction(kind="OPEN_RECOMMENDATIONS", label="View your recommended practice")
        )
        return ProgressView(
            subject=summary,
            topics=[
                summarize(t.id, t.name, {s for s in skills if concepts[s[0]] == t.id}, evidence, at)
                for t in topics
            ],
            competencies=[
                summarize(c.id, c.name, {s for s in skills if s[1] == c.id}, evidence, at)
                for c in db.scalars(
                    select(Competency)
                    .where(Competency.id.in_({s[1] for s in skills}))
                    .order_by(Competency.name)
                )
            ],
            calculated_at=at,
            next_action=action,
        )


def history(
    service: "AssessmentService",
    token: str,
    subject_id: UUID | None,
    cursor: str | None,
    limit: int,
) -> SessionHistoryPage:
    with Session(service.identity.engine) as db, db.begin():
        actor = service.authorize(db, token, subject_id)
        if not service.identity.rate(db, "history-read:" + str(actor), 60, 60):
            raise IdentityError("USAGE_LIMIT_REACHED", 429)
        subjects = service.identity.profile(db, actor).subject_ids
        query = (
            select(AssessmentSession, Subject.name, Topic.name)
            .join(Subject, Subject.id == AssessmentSession.subject_id)
            .outerjoin(Topic, Topic.id == AssessmentSession.topic_id)
            .where(
                AssessmentSession.learner_id == actor,
                AssessmentSession.subject_id.in_([subject_id] if subject_id else subjects),
            )
        )
        if cursor:
            try:
                payload, signature = cursor.split(".")
                expected = service.identity.digest(
                    "history-cursor", f"{actor}:{subject_id}:{payload}"
                )
                if not hmac.compare_digest(signature, expected):
                    raise ValueError("Invalid cursor")
                data = json.loads(base64.urlsafe_b64decode(payload))
                started, identifier = datetime.fromisoformat(data[0]), UUID(data[1])
                if started.tzinfo is None:
                    raise ValueError("Invalid cursor timestamp")
            except (ValueError, TypeError, IndexError, KeyError, UnicodeError):
                raise IdentityError("VALIDATION_FAILED", 422) from None
            query = query.where(
                or_(
                    AssessmentSession.started_at < started,
                    and_(
                        AssessmentSession.started_at == started, AssessmentSession.id < identifier
                    ),
                )
            )
        rows = list(
            db.execute(
                query.order_by(
                    AssessmentSession.started_at.desc(), AssessmentSession.id.desc()
                ).limit(limit + 1)
            )
        )
        sessions = [row[0].id for row in rows[:limit]]
        counts = {
            session_id: count
            for session_id, count in db.execute(
                select(SessionItem.session_id, func.count(Attempt.id))
                .join(Attempt, Attempt.session_item_id == SessionItem.id)
                .where(SessionItem.session_id.in_(sessions))
                .group_by(SessionItem.session_id)
            ).all()
        }
        parents = {
            session_id: parent
            for session_id, parent in db.execute(
                select(Reassessment.session_id, SessionItem.session_id)
                .join(Attempt, Attempt.id == Reassessment.original_attempt_id)
                .join(SessionItem, SessionItem.id == Attempt.session_item_id)
                .where(Reassessment.session_id.in_(sessions))
            ).all()
        }
        data_rows = [
            SessionHistoryEntry(
                id=s.id,
                subject_id=s.subject_id,
                subject=subject,
                topic=topic,
                kind=s.kind,
                status="EXPIRED"
                if s.status == "ACTIVE" and s.expires_at <= service.identity.clock()
                else s.status,
                started_at=s.started_at,
                completed_at=s.completed_at,
                item_count=s.item_count,
                answered_count=counts.get(s.id, 0),
                original_session_id=parents.get(s.id),
            )
            for s, subject, topic in rows[:limit]
        ]
        next_cursor = None
        if len(rows) > limit:
            last = rows[limit - 1][0]
            payload = base64.urlsafe_b64encode(
                json.dumps([last.started_at.isoformat(), str(last.id)]).encode()
            ).decode()
            signature = service.identity.digest("history-cursor", f"{actor}:{subject_id}:{payload}")
            next_cursor = payload + "." + signature
        return SessionHistoryPage(data=data_rows, next_cursor=next_cursor)
