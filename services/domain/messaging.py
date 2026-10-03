"""Channel linking and minimized durable transport receipts."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class LinkCode(Base):
    __tablename__ = "link_codes"
    __table_args__ = (UniqueConstraint("user_id", "key"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    key: Mapped[UUID]
    code_hash: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ChannelSender(Base):
    __tablename__ = "channel_senders"
    sender_hash: Mapped[str] = mapped_column(primary_key=True)
    barrier_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_provider_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChannelLink(Base):
    __tablename__ = "channel_links"
    __table_args__ = (UniqueConstraint("user_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    sender_hash: Mapped[str] = mapped_column(ForeignKey("channel_senders.sender_hash"))
    external_identifier_encrypted: Mapped[str | None]
    revision: Mapped[int]
    status: Mapped[str]
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    opted_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InboundMessage(Base):
    __tablename__ = "inbound_messages"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    message_hash: Mapped[str] = mapped_column(unique=True)
    request_hash: Mapped[str]
    request_id: Mapped[UUID]
    sender_hash: Mapped[str]
    sender_encrypted: Mapped[str | None]
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    command: Mapped[str]
    code_hash: Mapped[str | None]
    status_reference: Mapped[str | None]
    delivery_status: Mapped[str | None]
    provider_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str]
    attempts: Mapped[int]
    error_code: Mapped[str | None]


class OutboundMessage(Base):
    __tablename__ = "outbound_messages"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    inbound_id: Mapped[UUID] = mapped_column(ForeignKey("inbound_messages.id"), unique=True)
    link_id: Mapped[UUID | None] = mapped_column(ForeignKey("channel_links.id"))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    recipient_hash: Mapped[str]
    recipient_encrypted: Mapped[str | None]
    template: Mapped[str]
    status: Mapped[str]
    provider_id: Mapped[str | None] = mapped_column(unique=True)
    attempts: Mapped[int]
    error_code: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ChannelMutationReceipt(Base):
    __tablename__ = "channel_mutation_receipts"
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    key: Mapped[UUID] = mapped_column(primary_key=True)
    request_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
