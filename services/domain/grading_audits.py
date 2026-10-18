"""Learner-owned publication/audit bindings and non-personal aggregate counters."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class GradingPublicationCounter(Base):
    __tablename__ = "grading_publication_counters"
    band_id: Mapped[UUID] = mapped_column(ForeignKey("grading_bands.id"), primary_key=True)
    returned_grades: Mapped[int] = mapped_column(BigInteger)
    assigned_audits: Mapped[int] = mapped_column(BigInteger)


class GradingPublication(Base):
    __tablename__ = "grading_publications"
    __table_args__ = (UniqueConstraint("band_id", "ordinal"),)
    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("grades.attempt_id"), primary_key=True)
    band_id: Mapped[UUID] = mapped_column(ForeignKey("grading_bands.id"))
    ordinal: Mapped[int] = mapped_column(BigInteger)
    audit_required: Mapped[bool]
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sampling_policy: Mapped[str] = mapped_column(default="global-publication-v1")
    session_ordinal: Mapped[int | None]


class GradingAuditAssignment(Base):
    __tablename__ = "grading_audit_assignments"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey("grading_publications.attempt_id"), unique=True
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class GradingReviewCounter(Base):
    __tablename__ = "grading_review_counters"
    band_id: Mapped[UUID] = mapped_column(ForeignKey("grading_bands.id"), primary_key=True)
    completed_audits: Mapped[int] = mapped_column(BigInteger)


class GradingAuditReview(Base):
    __tablename__ = "grading_audit_reviews"
    __table_args__ = (
        UniqueConstraint("band_id", "completion_ordinal"),
        UniqueConstraint("reviewer_id", "request_key"),
    )
    id: Mapped[UUID] = mapped_column(ForeignKey("grading_audit_assignments.id"), primary_key=True)
    band_id: Mapped[UUID] = mapped_column(ForeignKey("grading_bands.id"))
    reviewer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    criterion_points: Mapped[dict[str, int]] = mapped_column(JSON)
    critical_error: Mapped[str]
    exact_agreement: Mapped[bool]
    completion_ordinal: Mapped[int] = mapped_column(BigInteger)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    request_key: Mapped[UUID]
    request_hash: Mapped[str] = mapped_column(String(64))
    correlation_id: Mapped[UUID]
