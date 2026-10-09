"""Subject diagnostic planning; all scoring remains in the shared assessment service."""

from datetime import timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from services.assessment_contracts import (
    DiagnosticAnswerReference,
    DiagnosticResult,
    DiagnosticView,
    InitialRecommendation,
    SkillSummary,
    StartDiagnostic,
)
from services.content_contracts import DraftDocument
from services.domain.assessment import (
    AssessmentReceipt,
    AssessmentSession,
    Attempt,
    Grade,
    SessionItem,
)
from services.domain.content import ItemVersion
from services.domain.curriculum import Competency, Topic
from services.identity import IdentityError
from services.mastery import project_skill, reconcile
from services.mastery_engine import BASELINE, fingerprint

if TYPE_CHECKING:
    from services.assessment import AssessmentService


class Diagnostics:
    def __init__(self, assessment: "AssessmentService"):
        self.assessment = assessment
        self.identity = assessment.identity

    def candidates(
        self,
        db: Session,
        actor: UUID,
        subject: UUID,
        *,
        channel: str = "WEB",
        topic_id: UUID | None = None,
        per_topic_limit: int = 1000,
    ) -> list[ItemVersion]:
        if not 1 <= per_topic_limit <= 1000:
            raise ValueError("Candidate limit is outside the supported range")
        excluded = set(
            db.scalars(
                select(ItemVersion.item_id)
                .join(SessionItem, SessionItem.item_version_id == ItemVersion.id)
                .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
                .where(
                    AssessmentSession.learner_id == actor,
                    or_(
                        SessionItem.served_at
                        >= self.identity.clock()
                        - timedelta(days=self.identity.settings.assessment_repetition_days),
                        and_(
                            AssessmentSession.status == "ACTIVE",
                            AssessmentSession.expires_at > self.identity.clock(),
                        ),
                    ),
                )
            )
        )
        result = []
        topics = select(Topic).where(Topic.subject_id == subject)
        if topic_id is not None:
            topics = topics.where(Topic.id == topic_id)
        for topic in db.scalars(topics.order_by(Topic.id)):
            result.extend(
                self.assessment.content.assessment_candidates(
                    db, subject, topic.id, excluded, per_topic_limit, lock=False, channel=channel
                )
            )
        return result

    def view(self, db: Session, session: AssessmentSession) -> DiagnosticView:
        answers = [
            DiagnosticAnswerReference(attempt_id=attempt, position=position)
            for attempt, position in db.execute(
                select(Attempt.id, SessionItem.position)
                .join(SessionItem)
                .where(SessionItem.session_id == session.id)
                .order_by(SessionItem.position)
            )
        ]
        return DiagnosticView(
            id=session.id,
            subject_id=session.subject_id,
            status=session.status,
            item_count=session.item_count,
            answered_count=len(answers),
            answered_attempts=answers,
            plan_version=session.plan_version,
            expires_at=session.expires_at,
            result=DiagnosticResult.model_validate(session.diagnostic_result)
            if session.diagnostic_result
            else None,
        )

    def start(self, token: str, body: StartDiagnostic, key: UUID, request: UUID) -> DiagnosticView:
        service = self.assessment
        with Session(self.identity.engine) as db, db.begin():
            actor = service.authorize(db, token, body.subject_id)
            fingerprint = self.identity.digest("assessment", "diagnostic:" + body.model_dump_json())
            receipt = service.replay(db, actor, key, fingerprint)
            if receipt:
                return self.view(db, service.owned(db, actor, receipt.session_id))
            active = db.scalar(
                select(AssessmentSession).where(
                    AssessmentSession.learner_id == actor,
                    AssessmentSession.subject_id == body.subject_id,
                    AssessmentSession.kind == "DIAGNOSTIC",
                    AssessmentSession.status == "ACTIVE",
                )
            )
            if active and active.expires_at <= self.identity.clock():
                active.status = "EXPIRED"
                db.flush()
                active = None
            reconcile(db, actor, self.identity.clock())
            if active is None:
                if not self.identity.rate(db, "assessment-start:" + str(actor), 30, 3600):
                    raise IdentityError("USAGE_LIMIT_REACHED", 429)
                candidates = self.candidates(db, actor, body.subject_id)
                docs = [DraftDocument.model_validate(v.document) for v in candidates]
                topics = {d.topic_id for d in docs}
                if len(candidates) < 15 or any(
                    not any(d.topic_id == topic and d.difficulty == "STANDARD" for d in docs)
                    for topic in topics
                ):
                    raise IdentityError("INSUFFICIENT_CONTENT", 409)
                active = AssessmentSession(
                    id=uuid4(),
                    learner_id=actor,
                    subject_id=body.subject_id,
                    topic_id=None,
                    kind="DIAGNOSTIC",
                    status="ACTIVE",
                    item_count=15,
                    reason="Gather initial evidence across the available subject topics.",
                    plan_version="diagnostic-15-v1",
                    started_at=self.identity.clock(),
                    expires_at=self.identity.clock()
                    + timedelta(days=self.identity.settings.assessment_session_days),
                )
                db.add(active)
                db.flush()
                service.event(db, active.id, "diagnostic.started", request)
            db.add(
                AssessmentReceipt(
                    learner_id=actor, key=key, request_hash=fingerprint, session_id=active.id
                )
            )
            db.flush()
            return self.view(db, active)

    def assign(self, db: Session, session: AssessmentSession) -> SessionItem:
        candidates = self.candidates(db, session.learner_id, session.subject_id)
        assigned = list(db.scalars(select(SessionItem).where(SessionItem.session_id == session.id)))
        used = {a.item_version_id for a in assigned}
        candidates = [v for v in candidates if v.id not in used]
        if not candidates:
            raise IdentityError("INSUFFICIENT_CONTENT", 409)
        covered_topics: set[UUID | None] = set()
        covered_competencies: set[UUID] = set()
        latest: dict[tuple[UUID, UUID], float] = {}
        for _item, version, grade in db.execute(
            select(SessionItem, ItemVersion, Grade)
            .join(ItemVersion, ItemVersion.id == SessionItem.item_version_id)
            .join(Attempt, Attempt.session_item_id == SessionItem.id)
            .join(Grade, Grade.attempt_id == Attempt.id)
            .where(SessionItem.session_id == session.id)
            .order_by(SessionItem.position)
        ):
            doc = DraftDocument.model_validate(version.document)
            covered_topics.add(doc.topic_id)
            for mapping in doc.competency_mappings:
                covered_competencies.add(mapping.competency_id)
                if doc.concept_id:
                    latest[(doc.concept_id, mapping.competency_id)] = grade.result["score"]
        documents = {v.id: DraftDocument.model_validate(v.document) for v in candidates}
        uncovered = sorted(
            {d.topic_id for d in documents.values() if d.topic_id not in covered_topics}, key=str
        )
        reason = "Gather more evidence for an under-covered skill."
        if uncovered:
            candidates = [
                v
                for v in candidates
                if documents[v.id].topic_id == uncovered[0]
                and documents[v.id].difficulty == "STANDARD"
            ]
            reason = "Sample this topic with a core question."
            if not candidates:
                raise IdentityError("INSUFFICIENT_CONTENT", 409)
        elif len(covered_competencies) < 2:
            diverse = [
                v
                for v in candidates
                if any(
                    m.competency_id not in covered_competencies
                    for m in documents[v.id].competency_mappings
                )
            ]
            if diverse:
                candidates = diverse
                reason = "Gather evidence in another competency."
        cache: dict[tuple[UUID, UUID], float] = {}

        def priority(v: ItemVersion) -> tuple[float, int, str]:
            doc = documents[v.id]
            scores = []
            for mapping in doc.competency_mappings:
                if doc.concept_id is None:
                    continue
                skill = (doc.concept_id, mapping.competency_id)
                if skill not in cache:
                    cache[skill] = project_skill(
                        db, session.learner_id, *skill, self.identity.clock()
                    ).confidence
                previous = latest.get(skill)
                desired = (
                    "STANDARD"
                    if previous is None
                    else ("CHALLENGING" if previous >= 0.75 else "FOUNDATIONAL")
                )
                scores.append((cache[skill], int(doc.difficulty != desired)))
            confidence, mismatch = min(scores, default=(0.0, 0))
            return confidence, mismatch, str(v.item_id)

        chosen = min(candidates, key=priority)
        item = SessionItem(
            id=uuid4(),
            session_id=session.id,
            item_version_id=chosen.id,
            position=len(assigned) + 1,
            reason=reason,
        )
        db.add(item)
        db.flush()
        return item

    def complete(self, db: Session, session: AssessmentSession) -> None:
        skills: dict[tuple[UUID, UUID], UUID] = {}
        for version in db.scalars(
            select(ItemVersion).join(SessionItem).where(SessionItem.session_id == session.id)
        ):
            doc = DraftDocument.model_validate(version.document)
            if doc.concept_id and doc.topic_id:
                for mapping in doc.competency_mappings:
                    skills[(doc.concept_id, mapping.competency_id)] = doc.topic_id
        summaries = []
        for (concept, competency), topic_id in sorted(
            skills.items(), key=lambda entry: str(entry[0])
        ):
            projection = project_skill(
                db, session.learner_id, concept, competency, self.identity.clock()
            )
            topic, comp = db.get(Topic, topic_id), db.get(Competency, competency)
            if topic is None or comp is None:
                raise IdentityError("CONTENT_NOT_APPROVED", 409)
            summaries.append(
                SkillSummary(
                    topic_id=topic_id,
                    topic=topic.name,
                    concept_id=concept,
                    competency_id=competency,
                    competency=comp.name,
                    mastery=projection.mastery,
                    confidence=projection.confidence,
                    display_state=projection.display_state,
                    evidence_count=projection.evidence_count,
                )
            )
        available: dict[UUID | None, int] = {}
        pool = self.candidates(db, session.learner_id, session.subject_id)
        for version in pool:
            candidate_topic = DraftDocument.model_validate(version.document).topic_id
            available[candidate_topic] = available.get(candidate_topic, 0) + 1
        eligible = [s for s in summaries if available.get(s.topic_id, 0) >= 5]
        recommendation = InitialRecommendation(
            topic_id=None,
            reason_code="CONTENT_UNAVAILABLE",
            learner_text="More reviewed content is needed before recommending a next activity.",
        )
        if eligible:
            target = min(
                eligible,
                key=lambda s: (
                    s.confidence >= 0.5,
                    s.confidence if s.confidence < 0.5 else s.mastery,
                    str(s.concept_id),
                    str(s.competency_id),
                ),
            )
            sparse = target.confidence < 0.5
            recommendation = InitialRecommendation(
                topic_id=target.topic_id,
                reason_code="GATHER_MORE_EVIDENCE" if sparse else "PRACTISE_SUPPORTED_GAP",
                learner_text=(
                    f"Practise {target.topic} to gather more evidence. "
                    "This is a developing estimate."
                )
                if sparse
                else (f"Continue practice in {target.topic} based on the current evidence."),
            )
        result = DiagnosticResult(
            skills=summaries,
            recommendation=recommendation,
            calculated_at=self.identity.clock(),
            algorithm_version=BASELINE.algorithm_version,
            configuration_version=BASELINE.configuration_version,
            input_hash=fingerprint(
                {
                    "skills": [s.model_dump(mode="json") for s in summaries],
                    "eligible_content_versions": sorted(str(v.id) for v in pool),
                    "configuration": BASELINE.model_dump(),
                    "plan_version": session.plan_version,
                    "calculated_at": self.identity.clock().isoformat(),
                }
            ),
        )
        session.diagnostic_result = result.model_dump(mode="json")
