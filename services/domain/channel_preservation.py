"""ADR-057 capture accountability separate from disposable encrypted evidence.

No FK points into operational channel state. STOP/unlink and source expiry must
remain possible independently of every preservation decision.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class ChannelSnapshot(Base):
    __tablename__ = "channel_preservation_snapshots"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(ForeignKey("data_subject_requests.id"))
    source_kind: Mapped[str]
    source_link_id: Mapped[UUID]
    link_revision: Mapped[int]
    source_state_version: Mapped[int | None] = mapped_column(BigInteger)
    source_version: Mapped[str]
    captured_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChannelSnapshotBody(Base):
    __tablename__ = "channel_preservation_bodies"
    snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("channel_preservation_snapshots.id"), primary_key=True
    )
    encrypted_payload: Mapped[str]


class ChannelSnapshotDisposal(Base):
    __tablename__ = "channel_preservation_disposals"
    snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("channel_preservation_snapshots.id"), primary_key=True
    )
    disposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
