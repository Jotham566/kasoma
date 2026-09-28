"""Content-owned report, metadata history and retry receipts."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class ContentFlag(Base):
    __tablename__ = "content_flags"
    __table_args__ = (UniqueConstraint("attempt_id", "category"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id"), index=True)
    item_version_id: Mapped[UUID] = mapped_column(ForeignKey("item_versions.id"))
    attempt_id: Mapped[UUID] = mapped_column(ForeignKey("attempts.id"))
    reporter_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str]
    comment_encrypted: Mapped[str]
    report_hash: Mapped[str]
    status: Mapped[str]
    priority: Mapped[str]
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    revision: Mapped[int]
    resolution_encrypted: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FlagHistory(Base):
    __tablename__ = "content_flag_history"
    __table_args__ = (UniqueConstraint("flag_id", "revision"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    flag_id: Mapped[UUID] = mapped_column(ForeignKey("content_flags.id"))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    revision: Mapped[int]
    status: Mapped[str]
    priority: Mapped[str]
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    resolution_hash: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FlagMutationReceipt(Base):
    __tablename__ = "content_flag_receipts"
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    key: Mapped[UUID] = mapped_column(primary_key=True)
    request_hash: Mapped[str]
    flag_id: Mapped[UUID] = mapped_column(ForeignKey("content_flags.id"))
