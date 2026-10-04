"""Bounded transient channel expiry; this does not execute account erasure or legal holds."""

from datetime import timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from services.domain.messaging import (
    ChannelLink,
    ChannelMutationReceipt,
    ChannelSender,
    ConversationState,
    InboundMessage,
    LinkCode,
    OutboundMessage,
)
from services.identity import IdentityService
from services.whatsapp_linking import channel_lock


def expire(identity: IdentityService) -> int:
    with Session(identity.engine) as db, db.begin():
        channel_lock(identity, db)
        now = identity.clock()
        expired = (
            select(ConversationState.link_id).where(ConversationState.expires_at <= now).limit(100)
        )
        db.execute(delete(ConversationState).where(ConversationState.link_id.in_(expired)))
        # Bounded batches avoid monopolizing the mutation lock as histories grow.
        codes = (
            select(LinkCode.id)
            .where(LinkCode.expires_at <= now, LinkCode.code_hash.is_not(None))
            .limit(100)
        )
        db.execute(update(LinkCode).where(LinkCode.id.in_(codes)).values(code_hash=None))
        ids = select(LinkCode.id).where(LinkCode.created_at <= now - timedelta(hours=24)).limit(100)
        db.execute(delete(LinkCode).where(LinkCode.id.in_(ids)))
        receipts = list(
            db.scalars(
                select(ChannelMutationReceipt)
                .where(ChannelMutationReceipt.created_at <= now - timedelta(hours=24))
                .limit(100)
            )
        )
        for receipt in receipts:
            db.delete(receipt)
        pending = (
            select(OutboundMessage.id)
            .where(
                OutboundMessage.status == "PENDING",
                OutboundMessage.created_at <= now - timedelta(hours=24),
            )
            .limit(100)
        )
        db.execute(
            update(OutboundMessage)
            .where(OutboundMessage.id.in_(pending))
            .values(status="CANCELLED", error_code="MESSAGE_EXPIRED", recipient_encrypted=None)
        )
        queued = (
            select(InboundMessage.id)
            .where(
                InboundMessage.status == "QUEUED",
                InboundMessage.received_at <= now - timedelta(hours=24),
            )
            .limit(100)
        )
        db.execute(
            update(InboundMessage)
            .where(InboundMessage.id.in_(queued))
            .values(
                status="REJECTED",
                error_code="MESSAGE_EXPIRED",
                processed_at=now,
                sender_encrypted=None,
                code_hash=None,
                reply_encrypted=None,
            )
        )
        horizon = now - timedelta(days=30)
        outgoing = (
            select(OutboundMessage.id)
            .where(OutboundMessage.status != "PENDING", OutboundMessage.created_at <= horizon)
            .limit(100)
        )
        db.execute(delete(OutboundMessage).where(OutboundMessage.id.in_(outgoing)))
        incoming = (
            select(InboundMessage.id)
            .where(
                InboundMessage.status != "QUEUED",
                InboundMessage.received_at <= horizon,
                ~select(OutboundMessage.id)
                .where(OutboundMessage.inbound_id == InboundMessage.id)
                .exists(),
            )
            .limit(100)
        )
        db.execute(delete(InboundMessage).where(InboundMessage.id.in_(incoming)))
        links = (
            select(ChannelLink.id)
            .where(
                ChannelLink.status == "UNLINKED",
                ChannelLink.updated_at <= horizon,
                ~select(OutboundMessage.id)
                .where(OutboundMessage.link_id == ChannelLink.id)
                .exists(),
            )
            .limit(100)
        )
        db.execute(delete(ChannelLink).where(ChannelLink.id.in_(links)))
        senders = (
            select(ChannelSender.sender_hash)
            .where(
                ChannelSender.updated_at <= horizon,
                ~select(ChannelLink.id)
                .where(ChannelLink.sender_hash == ChannelSender.sender_hash)
                .exists(),
                ~select(InboundMessage.id)
                .where(InboundMessage.sender_hash == ChannelSender.sender_hash)
                .exists(),
                ~select(OutboundMessage.id)
                .where(OutboundMessage.recipient_hash == ChannelSender.sender_hash)
                .exists(),
            )
            .limit(100)
        )
        db.execute(delete(ChannelSender).where(ChannelSender.sender_hash.in_(senders)))
        return len(receipts)
