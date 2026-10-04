"""Durable, atomic intake and immediate STOP barriers, before webhook acknowledgement."""

from uuid import UUID, uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from services.domain.messaging import (
    ChannelLink,
    ChannelSender,
    ConversationState,
    InboundMessage,
    OutboundMessage,
)
from services.identity import IdentityService
from services.whatsapp_ingress import WebhookRejected, authenticate_and_decode
from services.whatsapp_linking import channel_lock
from services.whatsapp_payloads import normalize_payload


def ingest(identity: IdentityService, raw: bytes, signature: str | None, request_id: UUID) -> None:
    secret = identity.settings.whatsapp_app_secret
    payload = authenticate_and_decode(
        raw, signature, secret.get_secret_value().encode() if secret else b""
    )
    rows = normalize_payload(identity, payload)
    # WebhookRejected rolls back all rows, including conflicting duplicates within a batch.
    with Session(identity.engine) as db, db.begin():
        channel_lock(identity, db)
        now = identity.clock()
        for item in rows:
            old = db.scalar(
                select(InboundMessage).where(InboundMessage.message_hash == item.message_hash)
            )
            if old:
                if old.request_hash != item.request_hash:
                    raise WebhookRejected("WEBHOOK_ID_CONFLICT", 409)
                continue
            sender = db.get(ChannelSender, item.sender_hash)
            if sender is None:
                sender = ChannelSender(sender_hash=item.sender_hash, updated_at=now)
                db.add(sender)
                db.flush()
            if item.command != "STATUS":
                fresh = (
                    sender.last_provider_at is None or item.provider_at >= sender.last_provider_at
                )
                if item.command == "STOP":
                    sender.barrier_at = now
                    db.execute(
                        delete(ConversationState).where(
                            ConversationState.link_id.in_(
                                select(ChannelLink.id).where(
                                    ChannelLink.sender_hash == item.sender_hash
                                )
                            )
                        )
                    )
                    db.execute(
                        update(OutboundMessage)
                        .where(
                            OutboundMessage.recipient_hash == item.sender_hash,
                            OutboundMessage.status == "PENDING",
                        )
                        .values(status="CANCELLED", recipient_encrypted=None, error_code="STOPPED")
                    )
                if fresh:
                    sender.last_provider_at = item.provider_at
            sender.updated_at = now
            command, reply_reference, reply_encrypted = (
                item.command,
                item.reply_reference,
                item.reply_encrypted,
            )
            if command == "ANSWER":
                bound = db.scalar(
                    select(OutboundMessage.id)
                    .join(
                        ConversationState,
                        ConversationState.expected_outbound_id == OutboundMessage.id,
                    )
                    .join(ChannelLink, ChannelLink.id == ConversationState.link_id)
                    .where(
                        OutboundMessage.provider_id == reply_reference,
                        OutboundMessage.recipient_hash == item.sender_hash,
                        OutboundMessage.status.in_(["SENT", "DELIVERED", "READ"]),
                        OutboundMessage.template.in_(["PRACTICE_MENU", "PRACTICE_QUESTION"]),
                        OutboundMessage.link_revision == ChannelLink.revision,
                        ChannelLink.sender_hash == item.sender_hash,
                        ChannelLink.status == "ACTIVE",
                        ConversationState.expires_at > now,
                        ConversationState.link_revision == ChannelLink.revision,
                    )
                )
                if bound is None:
                    command, reply_reference, reply_encrypted = "UNSUPPORTED", None, None
            db.add(
                InboundMessage(
                    id=uuid4(),
                    message_hash=item.message_hash,
                    request_hash=item.request_hash,
                    request_id=request_id,
                    sender_hash=item.sender_hash,
                    sender_encrypted=item.sender_encrypted,
                    actor_id=None,
                    command=command,
                    code_hash=item.code_hash,
                    status_reference=item.status_reference,
                    delivery_status=item.delivery_status,
                    provider_at=item.provider_at,
                    reply_reference=reply_reference,
                    reply_encrypted=reply_encrypted,
                    received_at=now,
                    available_at=now,
                    processed_at=None,
                    status="QUEUED",
                    attempts=0,
                    error_code=None,
                )
            )
            db.flush()
