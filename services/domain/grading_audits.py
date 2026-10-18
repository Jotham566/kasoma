"""Learner-owned publication/audit bindings and non-personal aggregate counters."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint
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


class GradingAuditAssignment(Base):
    __tablename__ = "grading_audit_assignments"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey("grading_publications.attempt_id"), unique=True
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
