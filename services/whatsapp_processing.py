"""Transactional channel state machine; asynchronous fake-only delivery is separate."""

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from services.content import ContentError
from services.domain.identity import Identifier, User
from services.domain.messaging import (
    ChannelLink,
    ChannelSender,
    InboundMessage,
    LinkCode,
    OutboundMessage,
)
from services.identity import IdentityError, IdentityService
from services.observability import emit
from services.whatsapp_linking import channel_lock


def bound_link(db: Session, sender: str) -> ChannelLink | None:
    return db.scalar(
        select(ChannelLink).where(
            ChannelLink.sender_hash == sender, ChannelLink.status.in_(["ACTIVE", "STOPPED"])
        )
    )


def resolve_actor(db: Session, row: InboundMessage) -> UUID | None:
    if row.command == "LINK" and row.code_hash:
        code = db.scalar(select(LinkCode).where(LinkCode.code_hash == row.code_hash))
        return code.user_id if code else None
    if row.command == "STATUS":
        outgoing = db.scalar(
            select(OutboundMessage).where(
                OutboundMessage.provider_id == row.status_reference,
                OutboundMessage.recipient_hash == row.sender_hash,
            )
        )
        return outgoing.actor_id if outgoing else None
    link = bound_link(db, row.sender_hash)
    return link.user_id if link else None


def allowed(identity: IdentityService, db: Session, actor: UUID | None) -> bool:
    user = db.get(User, actor, populate_existing=True) if actor else None
    return bool(user and user.status == "ACTIVE" and identity.profile(db, user.id).learning_allowed)


def consume_link(identity: IdentityService, db: Session, row: InboundMessage) -> ChannelLink | None:
    now = identity.clock()
    if not identity.rate(
        db,
        "wa-link-attempt:" + row.sender_hash,
        identity.settings.whatsapp_link_attempts_per_minute,
        60,
    ):
        row.error_code = "RATE_LIMITED"
        return None
    code = (
        db.scalar(select(LinkCode).where(LinkCode.code_hash == row.code_hash))
        if row.code_hash
        else None
    )
    sender = db.get(ChannelSender, row.sender_hash)
    if (
        not code
        or code.expires_at <= now
        or code.consumed_at
        or code.revoked_at
        or not allowed(identity, db, code.user_id)
        or (sender and sender.barrier_at and code.created_at <= sender.barrier_at)
    ):
        row.error_code = "LINK_REJECTED"
        return None
    link = db.scalar(select(ChannelLink).where(ChannelLink.user_id == code.user_id))
    owner = bound_link(db, row.sender_hash)
    phone = identity.decrypt(row.sender_encrypted) if row.sender_encrypted else ""
    verified = db.scalar(
        select(Identifier).where(
            Identifier.lookup_hash == identity.digest("identifier", phone),
            Identifier.type == "PHONE",
        )
    )
    if (
        (owner and owner.user_id != code.user_id)
        or (link and link.status != "UNLINKED" and link.sender_hash != row.sender_hash)
        or (verified and verified.user_id != code.user_id)
    ):
        row.error_code = "LINK_REJECTED"
        return None
    if link is None:
        link = ChannelLink(id=uuid4(), user_id=code.user_id, revision=1)
        db.add(link)
    else:
        link.revision += 1
    link.sender_hash, link.external_identifier_encrypted = row.sender_hash, row.sender_encrypted
    link.status, link.linked_at, link.updated_at, link.opted_out_at = "ACTIVE", now, now, None
    code.code_hash, code.consumed_at = None, now
    row.actor_id = code.user_id
    identity.event(db, code.user_id, "channel.linked", str(row.request_id))
    db.flush()
    return link


def queue_reply(
    identity: IdentityService,
    db: Session,
    row: InboundMessage,
    link: ChannelLink | None,
    template: str,
) -> OutboundMessage:
    now = identity.clock()
    outgoing = OutboundMessage(
        id=uuid4(),
        inbound_id=row.id,
        link_id=link.id if link else None,
        actor_id=row.actor_id,
        recipient_hash=row.sender_hash,
        recipient_encrypted=row.sender_encrypted,
        template=template,
        status="PENDING",
        provider_id=None,
        attempts=0,
        error_code=None,
        created_at=now,
        available_at=now,
        sent_at=None,
        status_at=None,
    )
    db.add(outgoing)
    return outgoing


def apply_status(db: Session, row: InboundMessage) -> None:
    outgoing = db.scalar(
        select(OutboundMessage).where(
            OutboundMessage.provider_id == row.status_reference,
            OutboundMessage.recipient_hash == row.sender_hash,
        )
    )
    ranks = {"SENT": 1, "DELIVERED": 2, "READ": 3}
    if not outgoing or outgoing.status not in ranks or not row.delivery_status:
        return
    if outgoing.status_at and row.provider_at < outgoing.status_at:
        return
    if row.delivery_status == "FAILED":
        # A late failed callback cannot undo confirmed delivery/read evidence.
        if outgoing.status != "SENT":
            return
        outgoing.status, outgoing.error_code = "FAILED", "PROVIDER_FAILED"
    elif ranks.get(row.delivery_status, 0) > ranks[outgoing.status]:
        outgoing.status = row.delivery_status
    outgoing.status_at = row.provider_at


def process_one(identity: IdentityService) -> bool:
    with Session(identity.engine) as db, db.begin():
        row = db.scalar(
            select(InboundMessage)
            .where(
                InboundMessage.status == "QUEUED", InboundMessage.available_at <= identity.clock()
            )
            .order_by(InboundMessage.received_at, InboundMessage.id)
            .limit(1)
        )
        if row is None:
            return False
        actor = resolve_actor(db, row)
        if actor:
            identity.lock_user(db, actor)
        channel_lock(identity, db)
        db.refresh(row)
        if (
            row.status != "QUEUED"
            or row.available_at > identity.clock()
            or resolve_actor(db, row) != actor
        ):
            return True  # Association changed; retry with correct actor-before-channel order.
        now = identity.clock()
        try:
            with db.begin_nested():
                apply_command(identity, db, row, actor)
                db.flush()
        except Exception:
            row.attempts += 1
            row.error_code = "PROCESSING_FAILED"
            if row.attempts < 3:
                row.available_at = now + timedelta(seconds=60 * row.attempts)
            else:
                row.status = "FAILED"
        else:
            row.attempts += 1
            row.status = "REJECTED" if row.error_code else "PROCESSED"
        if row.status != "QUEUED":
            row.processed_at, row.sender_encrypted, row.code_hash = now, None, None
            row.reply_encrypted = None
        db.flush()
        event, correlation = "channel.inbound." + row.status.lower(), str(row.request_id)
        status = 200 if row.status == "PROCESSED" else 503
    emit(event, correlation, "WHATSAPP", status)
    return True


def apply_command(
    identity: IdentityService, db: Session, row: InboundMessage, actor: UUID | None
) -> None:
    now = identity.clock()
    link = bound_link(db, row.sender_hash)
    row.actor_id = actor
    row.error_code = None
    if row.received_at + timedelta(hours=24) <= now:
        row.error_code = "MESSAGE_EXPIRED"
    elif row.command == "STATUS":
        apply_status(db, row)
    elif row.command == "LINK":
        linked = consume_link(identity, db, row)
        queue_reply(identity, db, row, linked, "LINKED" if linked else "LINK_REJECTED")
    elif row.command == "STOP":
        sender = db.get(ChannelSender, row.sender_hash)
        if link and sender and sender.barrier_at and sender.barrier_at >= link.linked_at:
            link.status, link.opted_out_at, link.updated_at = "STOPPED", now, now
            link.revision += 1
            identity.event(db, link.user_id, "channel.stopped", str(row.request_id))
            db.execute(
                update(OutboundMessage)
                .where(OutboundMessage.link_id == link.id, OutboundMessage.status == "PENDING")
                .values(status="CANCELLED", recipient_encrypted=None, error_code="STOPPED")
            )
    elif row.command in {"START", "CONTINUE", "PROGRESS", "ANSWER", "HELP"} and link:
        sender = db.get(ChannelSender, row.sender_hash)
        if (
            link.status != "ACTIVE"
            or row.received_at < link.linked_at
            or (sender and sender.barrier_at and sender.barrier_at >= link.linked_at)
            or not allowed(identity, db, actor)
        ):
            row.error_code = "CHANNEL_NOT_ACTIVE"
            return
        from services.whatsapp_practice import process, queue

        try:
            with db.begin_nested():
                process(identity, db, row, link)
                db.flush()
        except (IdentityError, ContentError, ValueError):
            row.error_code = "PRACTICE_UNAVAILABLE"
            queue(identity, db, row, link, "PRACTICE_NOTICE")
    else:
        queue_reply(identity, db, row, link, "HELP" if row.command == "HELP" else "UNSUPPORTED")
