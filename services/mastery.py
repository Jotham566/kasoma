"""Mastery-owned writes inside the assessment transaction; replayable evidence."""

import json
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment_contracts import GradeView
from services.content_contracts import DraftDocument
from services.domain.assessment import Attempt, Grade
from services.domain.content import ItemVersion
from services.domain.mastery import MasteryEstimate, MasteryEvidence, MasteryHistory
from services.mastery_engine import Estimate, Evidence, GradeInput, estimate, normalize
from services.rubric_grade_protection import StoredRubricGrade


def project_skill(
    db: Session, learner: UUID, concept: UUID, competency: UUID, at: datetime
) -> Estimate:
    rows = db.scalars(
        select(MasteryEvidence).where(
            MasteryEvidence.learner_id == learner,
            MasteryEvidence.concept_id == concept,
            MasteryEvidence.competency_id == competency,
        )
    )
    return estimate(concept, competency, [Evidence.model_validate(r.snapshot) for r in rows], at)


def record(db: Session, attempt: Attempt, grade: Grade, at: datetime) -> None:
    """Caller holds the authenticated learner lock; never edits grades or old evidence."""
    result = (
        StoredRubricGrade.model_validate_json(json.dumps(grade.result))
        if grade.result.get("method") == "RUBRIC_MODEL"
        else GradeView.model_validate(grade.result)
    )
    version = db.get(ItemVersion, attempt.item_version_id)
    if version is None:
        raise ValueError("Missing pinned content")
    document = DraftDocument.model_validate(version.document)
    if document.concept_id is None:
        raise ValueError("Missing approved skill mapping")
    for mapping in document.competency_mappings:
        existing = db.scalar(
            select(MasteryEvidence.id).where(
                MasteryEvidence.attempt_id == attempt.id,
                MasteryEvidence.concept_id == document.concept_id,
                MasteryEvidence.competency_id == mapping.competency_id,
            )
        )
        if existing is not None:
            continue
        normalized = normalize(
            GradeInput(
                attempt_id=attempt.id,
                item_id=version.item_id,
                item_version_id=version.id,
                concept_id=document.concept_id,
                competency_id=mapping.competency_id,
                occurred_at=attempt.submitted_at,
                response_type=document.response_type,
                content_difficulty=document.difficulty,
                points_awarded=result.points_awarded,
                points_possible=result.points_possible,
                hint_count=attempt.hint_count,
                highest_hint_level=attempt.highest_hint_level,
                grade_confidence=result.confidence,
                method=result.method,
                status=result.status,
                mapping_weight=mapping.weight,
            ),
            calculated_at=at,
        )
        if normalized is None:
            continue
        row = MasteryEvidence(
            id=uuid4(),
            learner_id=attempt.learner_id,
            attempt_id=attempt.id,
            concept_id=document.concept_id,
            competency_id=mapping.competency_id,
            occurred_at=attempt.submitted_at,
            snapshot=normalized.model_dump(mode="json"),
        )
        db.add(row)
        db.flush()
        projection = project_skill(
            db, attempt.learner_id, row.concept_id, row.competency_id, at
        ).model_dump(mode="json")
        key = (attempt.learner_id, row.concept_id, row.competency_id)
        current = db.get(MasteryEstimate, key)
        if current is None:
            db.add(
                MasteryEstimate(
                    learner_id=key[0], concept_id=key[1], competency_id=key[2], snapshot=projection
                )
            )
        else:
            current.snapshot = projection
        db.add(MasteryHistory(id=uuid4(), evidence_id=row.id, snapshot=projection))
        db.flush()


def reconcile(db: Session, learner: UUID, at: datetime) -> None:
    """After current consent authorization, incorporate legacy grades once, in order."""
    rows = db.execute(
        select(Attempt, Grade)
        .join(Grade, Grade.attempt_id == Attempt.id)
        .where(
            Attempt.learner_id == learner,
            ~select(MasteryEvidence.id).where(MasteryEvidence.attempt_id == Attempt.id).exists(),
        )
        .order_by(Attempt.submitted_at, Attempt.id)
    )
    for attempt, grade in rows:
        record(db, attempt, grade, at)
