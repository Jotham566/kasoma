"""Shared nonpersonal warning versions; staff accountability stays in AuditLog."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class WarningConfigurationVersion(Base):
    __tablename__ = "operations_configuration_versions"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    revision: Mapped[int] = mapped_column(unique=True)
    values: Mapped[dict[str, int]] = mapped_column("thresholds", JSON)
    version_ref: Mapped[str]
    previous_ref: Mapped[str]
    command_hash: Mapped[str]
    changed_key: Mapped[str]
    reason: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("clock_timestamp()")
    )


class WarningConfigurationState(Base):
    __tablename__ = "operations_configuration_state"
    id: Mapped[int] = mapped_column(primary_key=True)
    nonce: Mapped[UUID] = mapped_column(server_default=text("gen_random_uuid()"))
    revision: Mapped[int]
    current_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("operations_configuration_versions.id")
    )
