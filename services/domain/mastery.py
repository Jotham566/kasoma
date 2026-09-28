"""Immutable skill evidence and rebuildable projections (FR-MST-001–003)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class MasteryEvidence(Base):
    __tablename__ = "mastery_evidence"
    __table_args__ = (UniqueConstraint("attempt_id", "concept_id", "competency_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    learner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("grades.attempt_id"))
    concept_id: Mapped[UUID] = mapped_column(ForeignKey("concepts.id"))
    competency_id: Mapped[UUID] = mapped_column(ForeignKey("competencies.id"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)


class MasteryEstimate(Base):
    __tablename__ = "mastery_estimates"
    learner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    concept_id: Mapped[UUID] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
    competency_id: Mapped[UUID] = mapped_column(ForeignKey("competencies.id"), primary_key=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)


class MasteryHistory(Base):
    __tablename__ = "mastery_estimate_history"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    evidence_id: Mapped[UUID] = mapped_column(ForeignKey("mastery_evidence.id"), unique=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
