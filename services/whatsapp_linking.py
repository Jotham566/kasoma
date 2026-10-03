"""Identity-owned channel mutations; no provider can create an account or bypass consent."""

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from services.domain.messaging import (
    ChannelLink,
    ChannelMutationReceipt,
    ChannelSender,
    LinkCode,
    OutboundMessage,
)
from services.identity import IdentityError, IdentityService
from services.whatsapp_contracts import ChannelLinkView, LinkCodeView


def channel_lock(identity: IdentityService, db: Session) -> None:
    """Acquire only after any required identity actor lock; never call a remote provider here."""
    identity.lock(db, "whatsapp-channel-mutations")


def link_code(identity: IdentityService, row: LinkCode) -> str:
    return identity.digest("whatsapp-code-value", f"{row.user_id}:{row.id}")[:12].upper()


def code_hash(identity: IdentityService, code: str) -> str:
    return identity.digest("whatsapp-code-lookup", code)


def owned_view(identity: IdentityService, db: Session, actor: UUID) -> ChannelLinkView:
    link = db.scalar(select(ChannelLink).where(ChannelLink.user_id == actor))
    status = link.status if link else "NOT_LINKED"
    opted_out_at = link.opted_out_at if link else None
    if link and link.status == "ACTIVE":
        sender = db.get(ChannelSender, link.sender_hash)
        if sender and sender.barrier_at and sender.barrier_at >= link.linked_at:
            status = "STOPPED"
            opted_out_at = sender.barrier_at
    return ChannelLinkView.model_validate(
        {
            "status": status,
            "link_id": link.id if link else None,
            "revision": link.revision if link else 0,
            "linked_at": link.linked_at if link else None,
            "opted_out_at": opted_out_at,
            "outbound_enabled": identity.settings.whatsapp_outbound_enabled,
        }
    )


class LinkingService:
    def __init__(self, identity: IdentityService):
        self.identity = identity

    def issue(self, token: str, key: UUID, request_id: UUID) -> LinkCodeView:
        secret = self.identity.settings.whatsapp_app_secret
        if secret is None or len(secret.get_secret_value()) < 32:
            raise IdentityError("CHANNEL_UNAVAILABLE", 503)
        with self.identity.transaction() as db:
            actor = self.identity.authenticate(db, token, recent=True).user_id
            if not self.identity.profile(db, actor).learning_allowed:
                raise IdentityError("CONSENT_REQUIRED", 403)
            channel_lock(self.identity, db)
            old = db.scalar(select(LinkCode).where(LinkCode.user_id == actor, LinkCode.key == key))
            now = self.identity.clock()
            if old:
                if (
                    old.expires_at <= now
                    or old.code_hash is None
                    or old.consumed_at
                    or old.revoked_at
                ):
                    raise IdentityError("LINK_CODE_EXPIRED", 410)
                return LinkCodeView(
                    id=old.id, code=link_code(self.identity, old), expires_at=old.expires_at
                )
            if not self.identity.rate(db, f"wa-code-issue:{actor}", 5, 3600):
                raise IdentityError("RATE_LIMITED", 429)
            db.execute(
                update(LinkCode)
                .where(LinkCode.user_id == actor, LinkCode.code_hash.is_not(None))
                .values(code_hash=None, revoked_at=now)
            )
            row = LinkCode(
                id=uuid4(),
                user_id=actor,
                key=key,
                created_at=now,
                expires_at=now + timedelta(minutes=5),
                consumed_at=None,
                revoked_at=None,
            )
            code = link_code(self.identity, row)
            row.code_hash = code_hash(self.identity, code)
            db.add(row)
            db.flush()
            self.identity.event(db, actor, "channel.link_code.issued", str(request_id))
            return LinkCodeView(id=row.id, code=code, expires_at=row.expires_at)

    def status(self, token: str) -> ChannelLinkView:
        with self.identity.transaction() as db:
            actor = self.identity.authenticate(db, token).user_id
            if not self.identity.rate(db, f"wa-status:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            return owned_view(self.identity, db, actor)

    def unlink(
        self,
        token: str,
        expected_revision: int,
        key: UUID,
        request_id: UUID,
        expected_link_id: UUID | None,
    ) -> ChannelLinkView:
        with self.identity.transaction() as db:
            actor = self.identity.authenticate(db, token, recent=True).user_id
            channel_lock(self.identity, db)
            fingerprint = self.identity.digest(
                "wa-unlink", f"{expected_link_id}:{expected_revision}"
            )
            receipt = db.get(ChannelMutationReceipt, (actor, key))
            if receipt:
                if receipt.request_hash != fingerprint:
                    raise IdentityError("IDEMPOTENCY_CONFLICT", 409)
                return owned_view(self.identity, db, actor)
            if not self.identity.rate(db, f"wa-unlink:{actor}", 10, 60):
                raise IdentityError("RATE_LIMITED", 429)
            link = db.scalar(select(ChannelLink).where(ChannelLink.user_id == actor))
            if expected_revision != (link.revision if link else 0) or expected_link_id != (
                link.id if link else None
            ):
                raise IdentityError("VERSION_CONFLICT", 409)
            now = self.identity.clock()
            db.execute(
                update(LinkCode)
                .where(LinkCode.user_id == actor, LinkCode.code_hash.is_not(None))
                .values(code_hash=None, revoked_at=now)
            )
            if link and link.status != "UNLINKED":
                sender = db.get(ChannelSender, link.sender_hash)
                if sender:
                    sender.barrier_at, sender.updated_at = now, now
                link.status, link.opted_out_at, link.updated_at = "UNLINKED", now, now
                link.external_identifier_encrypted = None
                link.revision += 1
                db.execute(
                    update(OutboundMessage)
                    .where(OutboundMessage.link_id == link.id, OutboundMessage.status == "PENDING")
                    .values(status="CANCELLED", recipient_encrypted=None, error_code="UNLINKED")
                )
            db.add(
                ChannelMutationReceipt(
                    actor_id=actor, key=key, request_hash=fingerprint, created_at=now
                )
            )
            self.identity.event(db, actor, "channel.unlinked", str(request_id))
            db.flush()
            return owned_view(self.identity, db, actor)
