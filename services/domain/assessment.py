"""Assessment evidence and durable delivery state."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    learner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"))
    topic_id: Mapped[UUID] = mapped_column(ForeignKey("topics.id"))
    status: Mapped[str]
    item_count: Mapped[int]
    reason: Mapped[str]
    plan_version: Mapped[str]
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SessionItem(Base):
    __tablename__ = "session_items"
    __table_args__ = (
        UniqueConstraint("session_id", "position"),
        UniqueConstraint("session_id", "item_version_id"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_sessions.id"), index=True)
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"))
    position: Mapped[int]
    reason: Mapped[str]
    served_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Attempt(Base):
    __tablename__ = "attempts"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    learner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    session_item_id: Mapped[UUID] = mapped_column(ForeignKey("session_items.id"), unique=True)
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"))
    choice_id: Mapped[str]
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    hint_count: Mapped[int]
    channel: Mapped[str]


class Grade(Base):
    __tablename__ = "grades"
    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("attempts.id"), primary_key=True)
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"))
    answer_specification_hash: Mapped[str]
    result: Mapped[dict[str, Any]] = mapped_column(JSON)


class AssessmentReceipt(Base):
    __tablename__ = "assessment_receipts"
    learner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    key: Mapped[UUID] = mapped_column(primary_key=True)
    request_hash: Mapped[str]
    session_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_sessions.id"))
    attempt_id: Mapped[UUID | None] = mapped_column(ForeignKey("attempts.id"))


class AssessmentEvent(Base):
    __tablename__ = "assessment_outbox_events"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_sessions.id"), index=True)
    attempt_id: Mapped[UUID | None] = mapped_column(ForeignKey("attempts.id"))
    type: Mapped[str]
    version: Mapped[int]
    request_id: Mapped[UUID]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
