"""ADR-061 private lifecycle metadata; no execution authority or payload-bearing rows.

FR-ID-006/BR-010/FR-OPS-003: SQL owns clocks, roles, transitions and activation.
These mappings do not create an executor, perform erasure or complete a request.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class ErasureState(Base):
    __tablename__ = "account_erasure_state"
    singleton: Mapped[int] = mapped_column(primary_key=True)
    original_scope_eligible: Mapped[bool]
    database_oid: Mapped[int] = mapped_column(BigInteger)
    namespace_oid: Mapped[int] = mapped_column(BigInteger)
    owner_oid: Mapped[int | None] = mapped_column(BigInteger)
    executor_oid: Mapped[int | None] = mapped_column(BigInteger)
    scope_nonce: Mapped[UUID]
    creation_enabled: Mapped[bool]
    execution_enabled: Mapped[bool]
    policy: Mapped[str] = mapped_column(String(64))
    manifest: Mapped[str] = mapped_column(String(64))
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ErasurePlanRow(Base):
    __tablename__ = "account_erasure_plans"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(ForeignKey("data_subject_requests.id"), index=True)
    scope_nonce: Mapped[UUID]
    policy: Mapped[str] = mapped_column(String(64))
    manifest: Mapped[str] = mapped_column(String(64))
    inventory_hash: Mapped[str] = mapped_column(String(64))
    version: Mapped[str | None] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ErasureJob(Base):
    __tablename__ = "account_erasure_jobs"
    __table_args__ = (UniqueConstraint("authorized_by", "command_key"),)
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_subject_requests.id"), primary_key=True
    )
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    authorized_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    decision_reference: Mapped[UUID]
    authorized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    authenticated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    policy: Mapped[str] = mapped_column(String(64))
    manifest: Mapped[str] = mapped_column(String(64))
    # Deliberately no plan FK: finite plan expiry must not be blocked by a durable job.
    plan_id: Mapped[UUID]
    plan_version: Mapped[str] = mapped_column(String(64))
    command_key: Mapped[UUID]
    command_hash: Mapped[str] = mapped_column(String(64))
    phase: Mapped[str] = mapped_column(String(32))
    blocker: Mapped[str | None] = mapped_column(String(64))
    failure: Mapped[str | None] = mapped_column(String(64))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    examined: Mapped[int] = mapped_column(BigInteger)
    removed: Mapped[int] = mapped_column(BigInteger)
    batches: Mapped[int] = mapped_column(BigInteger)
    private_cursor: Mapped[dict[str, object] | None] = mapped_column(JSON)
    correlation_id: Mapped[UUID]
