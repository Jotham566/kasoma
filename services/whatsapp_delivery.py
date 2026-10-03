"""Fake-only outbox delivery with final consent, opt-out, ownership and rate checks."""

from datetime import timedelta
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.domain.messaging import ChannelLink, ChannelSender, OutboundMessage
from services.identity import IdentityService
from services.whatsapp_linking import channel_lock
from services.whatsapp_processing import allowed

TEMPLATES = {
    "LINKED": "Your Kasoma channel is linked. Send HELP for options or STOP to stop replies.",
    "STOPPED": "Kasoma replies are stopped. Manage your channel in your web account.",
    "HELP": "Manage linking in your Kasoma web account. Send LINK followed by its code, or STOP.",
    "LINK_REJECTED": "That link could not be completed. Get a new code in your Kasoma web account.",
    "UNSUPPORTED": "Local commands: LINK, HELP and STOP. Practice is not available yet.",
}


class Delivery(Protocol):
    def send(self, key: UUID, recipient: str, body: str) -> str: ...


class FakeChannelDelivery:
    """A stable synthetic provider ID per outbox key, including process restarts."""

    def send(self, key: UUID, recipient: str, body: str) -> str:
        return f"wamid.fake.{key}"


def deliver_one(identity: IdentityService, provider: Delivery) -> bool:
    with Session(identity.engine) as db, db.begin():
        row = db.scalar(
            select(OutboundMessage)
            .where(
                OutboundMessage.status == "PENDING",
                OutboundMessage.available_at <= identity.clock(),
            )
            .order_by(OutboundMessage.created_at, OutboundMessage.id)
            .limit(1)
        )
        if row is None:
            return False
        if row.actor_id:
            identity.lock(db, str(row.actor_id))
        channel_lock(identity, db)
        db.refresh(row)
        if row.status != "PENDING" or row.available_at > identity.clock():
            return True
        now = identity.clock()
        sender = db.get(ChannelSender, row.recipient_hash)
        link = db.get(ChannelLink, row.link_id) if row.link_id else None
        reason = None
        if not identity.settings.whatsapp_outbound_enabled:
            reason = "OUTBOUND_DISABLED"
        elif row.created_at + timedelta(hours=24) <= now:
            reason = "MESSAGE_EXPIRED"
        elif (
            sender
            and sender.barrier_at
            and (
                not link
                or link.linked_at <= sender.barrier_at
                or sender.barrier_at >= row.created_at
            )
        ):
            reason = "STOPPED"
        elif row.actor_id and not allowed(identity, db, row.actor_id):
            reason = "CONSENT_REQUIRED"
        elif row.link_id and (
            not link
            or link.status != "ACTIVE"
            or link.sender_hash != row.recipient_hash
            or link.user_id != row.actor_id
            or link.linked_at > row.created_at
        ):
            reason = "LINK_CHANGED"
        elif not identity.rate(
            db,
            "wa-outbound:" + row.recipient_hash,
            identity.settings.whatsapp_outbound_per_minute,
            60,
        ):
            reason = "RATE_LIMITED"
        if reason:
            row.status, row.error_code, row.recipient_encrypted = "CANCELLED", reason, None
            return True
        row.attempts += 1
        try:
            if not row.recipient_encrypted:
                raise ValueError("Missing recipient")
            result = provider.send(
                row.id, identity.decrypt(row.recipient_encrypted), TEMPLATES[row.template]
            )
            # This adapter accepts synthetic IDs only; no real transport can be enabled here.
            if result != f"wamid.fake.{row.id}":
                raise ValueError("Invalid fake receipt")
        except Exception:
            row.error_code = "DELIVERY_FAILED"
            if row.attempts >= 3:
                row.status, row.recipient_encrypted = "FAILED", None
            else:
                row.available_at = now + timedelta(seconds=60 * row.attempts)
        else:
            row.status, row.provider_id, row.sent_at = "SENT", result, now
            row.error_code, row.recipient_encrypted = None, None
        return True
