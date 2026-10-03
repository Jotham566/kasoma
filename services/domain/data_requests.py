"""Identity-owned minimized, append-only data-request intake evidence."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class DataRequest(Base):
    __tablename__ = "data_subject_requests"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str]
    authenticated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    export_digest: Mapped[str | None]
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


class DataExport(Base):
    __tablename__ = "data_exports"
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_subject_requests.id"), primary_key=True
    )
    encrypted_payload: Mapped[str]
    digest: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LegalHold(Base):
    __tablename__ = "legal_holds"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(ForeignKey("data_subject_requests.id"), index=True)
    record_type: Mapped[str]
    record_id: Mapped[UUID]
    decision_reference: Mapped[UUID]
    reason: Mapped[str]
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    released_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    release_reference: Mapped[UUID | None]


class LegalHoldReceipt(Base):
    __tablename__ = "legal_hold_receipts"
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    key: Mapped[UUID] = mapped_column(primary_key=True)
    request_hash: Mapped[str]
    hold_id: Mapped[UUID] = mapped_column(ForeignKey("legal_holds.id"))
