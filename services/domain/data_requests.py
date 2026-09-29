"""Identity-owned minimized, append-only data-request intake evidence."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class DataRequest(Base):
    __tablename__ = "data_subject_requests"
    __table_args__ = (UniqueConstraint("user_id", "kind"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str]
    authenticated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verification_method: Mapped[str]
    retention_policy: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DataRequestReview(Base):
    __tablename__ = "data_request_reviews"
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_subject_requests.id"), primary_key=True
    )
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DataRequestReceipt(Base):
    __tablename__ = "data_request_receipts"
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    key: Mapped[UUID] = mapped_column(primary_key=True)
    request_hash: Mapped[str]
    request_id: Mapped[UUID] = mapped_column(ForeignKey("data_subject_requests.id"))
