"""ADR-048 work in progress: minimized background export state and disposable generations."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class ExportJob(Base):
    __tablename__ = "personal_export_jobs"
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_subject_requests.id"), primary_key=True
    )
    status: Mapped[str]
    correlation_id: Mapped[UUID]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int]
    failure: Mapped[str | None]
    grant_family: Mapped[UUID | None]
    grant_authenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    generation_id: Mapped[UUID | None]


class ExportGeneration(Base):
    __tablename__ = "personal_export_generations"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("personal_export_jobs.request_id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    lease_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    encrypted_manifest: Mapped[str | None]
    digest: Mapped[str | None]
    size: Mapped[int | None]
