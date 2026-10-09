"""Content-owned persistence; publication never changes a historical payload."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class Item(Base):
    __tablename__ = "items"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ItemVersion(Base):
    __tablename__ = "item_versions"
    __table_args__ = (UniqueConstraint("item_id", "version"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id"), index=True)
    version: Mapped[int]
    review_round: Mapped[int]
    revision: Mapped[int]
    status: Mapped[str] = mapped_column(String(20), index=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    topic_id: Mapped[UUID | None] = mapped_column(ForeignKey("topics.id"))
    concept_id: Mapped[UUID | None] = mapped_column(ForeignKey("concepts.id"))
    document: Mapped[dict[str, Any]] = mapped_column(JSON)
    content_hash: Mapped[str] = mapped_column(String(64))
    requires_second_review: Mapped[bool]
    synthetic: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ItemMapping(Base):
    __tablename__ = "item_mappings"
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"), primary_key=True)
    competency_id: Mapped[UUID] = mapped_column(ForeignKey("competencies.id"), primary_key=True)
    weight: Mapped[float]


class ContentReview(Base):
    __tablename__ = "content_reviews"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"), index=True)
    reviewer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    content_hash: Mapped[str]
    review_round: Mapped[int]
    decision: Mapped[str]
    checklist: Mapped[list[str]] = mapped_column(JSON)
    reason: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    target_id: Mapped[UUID]
    action: Mapped[str]
    reason: Mapped[str]
    request_id: Mapped[UUID]
    before_hash: Mapped[str | None]
    after_hash: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ContentReceipt(Base):
    __tablename__ = "content_mutation_receipts"
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    key: Mapped[UUID] = mapped_column(primary_key=True)
    request_hash: Mapped[str]
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"))


class ContentEvent(Base):
    __tablename__ = "content_outbox_events"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"))
    type: Mapped[str]
    version: Mapped[int]
    request_id: Mapped[UUID]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ContentImport(Base):
    __tablename__ = "content_import_jobs"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    key: Mapped[UUID]
    request_hash: Mapped[str]
    request_id: Mapped[UUID]
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON(none_as_null=True))
    results: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    status: Mapped[str]
    attempts: Mapped[int]
    error_code: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Rubric(Base):
    __tablename__ = "rubrics"
    id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"), primary_key=True)
    maximum_points: Mapped[int]


class RubricCriterionRow(Base):
    __tablename__ = "rubric_criteria"
    rubric_id: Mapped[UUID] = mapped_column(ForeignKey("rubrics.id"), primary_key=True)
    criterion_id: Mapped[str] = mapped_column(primary_key=True)
    position: Mapped[int]
    maximum_points: Mapped[int]
    criterion_text: Mapped[str]
    acceptable_evidence: Mapped[list[str]] = mapped_column(JSON)
    common_errors: Mapped[list[str]] = mapped_column(JSON)
    prohibited_inferences: Mapped[list[str]] = mapped_column(JSON)
