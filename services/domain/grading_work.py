"""Durable grading command and exact immutable transition evidence."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class GradingWorkRow(Base):
    __tablename__ = "assessment_grading_work"
    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("attempts.id"), primary_key=True)
    correlation_id: Mapped[UUID]
    revision: Mapped[int]
    status: Mapped[str]
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    claim_id: Mapped[UUID | None]
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str | None]


class GradingHistory(Base):
    __tablename__ = "assessment_grading_history"
    __table_args__ = (UniqueConstraint("attempt_id", "revision"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_grading_work.attempt_id"))
    revision: Mapped[int]
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
