"""Consent-authorized synthetic ranking and immutable session snapshots."""

from datetime import timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.content_contracts import DraftDocument
from services.domain.assessment import AssessmentSession, RecommendationSnapshot, SessionItem
from services.domain.content import ItemVersion
from services.domain.curriculum import Topic
from services.mastery import project_skill, reconcile
from services.mastery_engine import fingerprint
from services.recommendation_engine import Candidate, RankedPlan, RankingInput, Target, rank

if TYPE_CHECKING:
    from services.assessment import AssessmentService


def plan(
    assessment: "AssessmentService", db: Session, learner: UUID, subject: UUID, count: int
) -> RankedPlan:
    at = assessment.identity.clock()
    reconcile(db, learner, at)
    eligible = {v.id for v in assessment.diagnostics.candidates(db, learner, subject)}
    occupied = set(
        db.scalars(
            select(AssessmentSession.topic_id).where(
                AssessmentSession.learner_id == learner,
                AssessmentSession.subject_id == subject,
                AssessmentSession.kind == "REVISION",
                AssessmentSession.status == "ACTIVE",
                AssessmentSession.expires_at > at,
            )
        )
    )
    topics = list(db.scalars(select(Topic).where(Topic.subject_id == subject).order_by(Topic.id)))
    versions = [
        v
        for topic in topics
        for v in assessment.content.assessment_candidates(
            db, subject, topic.id, set(), 1000, lock=False
        )
    ]
    topic_names = {t.id: t.name for t in topics}
    exposures: dict[UUID, int] = {}
    recent: dict[tuple[UUID, UUID], int] = {}
    for version, served in db.execute(
        select(ItemVersion, SessionItem.served_at)
        .join(SessionItem, SessionItem.item_version_id == ItemVersion.id)
        .join(AssessmentSession, AssessmentSession.id == SessionItem.session_id)
        .where(
            AssessmentSession.learner_id == learner,
            SessionItem.served_at.is_not(None),
            AssessmentSession.subject_id == subject,
        )
    ):
        exposures[version.item_id] = exposures.get(version.item_id, 0) + 1
        doc = DraftDocument.model_validate(version.document)
        if served >= at - timedelta(days=assessment.identity.settings.assessment_repetition_days):
            if doc.concept_id:
                for mapping in doc.competency_mappings:
                    key = (doc.concept_id, mapping.competency_id)
                    recent[key] = recent.get(key, 0) + 1
    prerequisites: dict[UUID, set[UUID]] = {}
    metadata: dict[tuple[UUID, UUID], UUID] = {}
    candidates = []
    for version in versions:
        doc = DraftDocument.model_validate(version.document)
        if doc.concept_id is None or doc.topic_id is None:
            continue
        prerequisites.setdefault(doc.concept_id, set()).update(doc.prerequisite_concept_ids)
        for mapping in doc.competency_mappings:
            metadata[(doc.concept_id, mapping.competency_id)] = doc.topic_id
            if version.id in eligible and doc.topic_id not in occupied:
                candidates.append(
                    Candidate(
                        item_id=version.item_id,
                        version_id=version.id,
                        concept_id=doc.concept_id,
                        competency_id=mapping.competency_id,
                        mapping_weight=mapping.weight,
                        difficulty=doc.difficulty,
                        response_type=doc.response_type,
                        scenario_hash=fingerprint(doc.prompt),
                        historical_exposures=exposures.get(version.item_id, 0),
                        expected_seconds=doc.expected_seconds,
                    )
                )
    # Include existing prerequisite evidence even when its content was withdrawn.
    from services.domain.curriculum import Concept
    from services.domain.mastery import MasteryEvidence

    for concept, competency, topic in db.execute(
        select(MasteryEvidence.concept_id, MasteryEvidence.competency_id, Concept.topic_id)
        .join(Concept, Concept.id == MasteryEvidence.concept_id)
        .join(Topic, Topic.id == Concept.topic_id)
        .where(MasteryEvidence.learner_id == learner, Topic.subject_id == subject)
        .distinct()
    ):
        metadata[(concept, competency)] = topic
    targets = tuple(
        Target(
            estimate=project_skill(db, learner, concept, competency, at),
            topic_id=topic,
            topic=topic_names[topic],
            prerequisite_concepts=tuple(sorted(prerequisites.get(concept, set()), key=str)),
            recent_exposures=recent.get((concept, competency), 0),
        )
        for (concept, competency), topic in sorted(metadata.items(), key=lambda pair: str(pair[0]))
    )
    result = rank(
        RankingInput(
            calculated_at=at,
            targets=targets,
            curriculum_version_ids=tuple(sorted((v.id for v in versions), key=str)),
            candidates=tuple(candidates),
            desired_item_count=count,
        )
    )

    existing = db.scalar(
        select(RecommendationSnapshot).where(
            RecommendationSnapshot.learner_id == learner,
            RecommendationSnapshot.input_hash == result.input_hash,
        )
    )
    if existing is None:
        db.add(
            RecommendationSnapshot(
                id=uuid4(),
                learner_id=learner,
                subject_id=subject,
                input_hash=result.input_hash,
                snapshot=result.model_dump(mode="json"),
            )
        )
        db.flush()
    return result
