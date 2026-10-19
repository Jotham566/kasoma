"""ADR-057 fixtures/integrity checks confined to generated synthetic drill databases."""

import re
from datetime import timedelta
from uuid import uuid4

from pydantic import SecretStr
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from scripts.recovery_channel_receipts import ChannelHoldAuthority
from services.channel_preservation import ChannelPreservationService, dispose_bodies
from services.channel_preservation_contracts import PreservationCapture, PreservationSource
from services.channel_preservation_format import PreservationCipher, SnapshotBinding
from services.domain.assessment import AssessmentSession
from services.domain.channel_preservation import (
    ChannelSnapshot,
    ChannelSnapshotBody,
    ChannelSnapshotDisposal,
)
from services.domain.data_requests import DataRequest
from services.domain.messaging import ChannelLink, ChannelSender, ConversationState
from services.identity import IdentityService
from services.legal_hold_contracts import HoldInput, HoldRelease
from services.legal_holds import LegalHoldService
from services.whatsapp_linking import LinkingService, channel_lock


def _isolated(identity: IdentityService, stage: str) -> None:
    with Session(identity.engine) as db:
        name = db.scalar(text("SELECT current_database()"))
    if not re.fullmatch(rf"kasoma_drill_{stage}_[0-9a-f]{{32}}", name or ""):
        raise ValueError("Channel preservation requires an isolated synthetic drill")


def populate_preservation(
    identity: IdentityService, token: str, authority: ChannelHoldAuthority
) -> None:
    _isolated(identity, "src")
    now, link, sender = identity.clock(), uuid4(), uuid4().hex
    with Session(identity.engine) as db, db.begin():
        owner = identity.authenticate(db, token, recent=True).user_id
        session = db.scalar(
            select(AssessmentSession.id)
            .where(
                AssessmentSession.learner_id == owner,
                AssessmentSession.kind == "REVISION",
                AssessmentSession.item_count == 5,
            )
            .order_by(AssessmentSession.id)
            .limit(1)
        )
        if session is None:
            raise ValueError("Synthetic conversation requires its owned five-item session")
        channel_lock(identity, db)
        db.add(ChannelSender(sender_hash=sender, updated_at=now))
        db.flush()
        db.add(
            ChannelLink(
                id=link,
                user_id=owner,
                sender_hash=sender,
                external_identifier_encrypted=identity.encrypt("synthetic-recovery-contact"),
                revision=1,
                status="ACTIVE",
                linked_at=now,
                opted_out_at=None,
                updated_at=now,
            )
        )
        db.flush()
        db.add(
            ConversationState(
                link_id=link,
                actor_id=owner,
                link_revision=1,
                session_id=session,
                expected_outbound_id=None,
                updated_at=now,
                expires_at=now + timedelta(hours=24),
            )
        )
    # Reuse the exact current independent claimant in memory. Do not take over the
    # deduplicated DELETE request or bypass the OTP resend cooldown.
    holds = LegalHoldService(identity)
    target, admin = authority.request_id, authority.token.get_secret_value()
    original = identity.settings.channel_preservation_enabled
    identity.settings.channel_preservation_enabled = True
    try:
        service = ChannelPreservationService(identity)
        captured = []
        for kind in (
            "CHANNEL_LINK_SNAPSHOT",
            "CHANNEL_CONVERSATION_SNAPSHOT",
            "CHANNEL_LINK_SNAPSHOT",
        ):
            source = PreservationSource.model_validate(
                {
                    "source_kind": kind,
                    "source_link_id": link,
                    "link_revision": 1,
                }
            )
            version = service.inspect(admin, target, source, uuid4())
            captured.append(
                service.capture(
                    admin,
                    target,
                    PreservationCapture.model_validate(
                        source.model_dump()
                        | version.model_dump()
                        | {
                            "decision_reference": uuid4(),
                            "reason": "LEGAL_OBLIGATION",
                            "expires_at": now + timedelta(days=365),
                            "affirmative": True,
                        }
                    ),
                    uuid4(),
                    uuid4(),
                )
            )
        holds.create(
            admin,
            target,
            HoldInput.model_validate(
                {
                    "record_type": "CHANNEL_LINK_SNAPSHOT",
                    "record_id": captured[0].record_id,
                    "decision_reference": uuid4(),
                    "reason": "LEGAL_OBLIGATION",
                    "expires_at": now + timedelta(days=365),
                    "affirmative": True,
                }
            ),
            uuid4(),
            uuid4(),
        )
        holds.release(
            admin,
            target,
            captured[2].id,
            HoldRelease(decision_reference=uuid4(), affirmative=True),
            uuid4(),
            uuid4(),
        )
        with Session(identity.engine) as db, db.begin():
            channel_lock(identity, db)
            if dispose_bodies(db) != 1:
                raise ValueError("Synthetic released evidence did not dispose exactly once")
        LinkingService(identity).unlink(token, 1, uuid4(), uuid4(), link)
        # Controlled fixture source disposal proves snapshots have no operational FK.
        # This is not an account-erasure processor or a production data transform.
        with Session(identity.engine) as db, db.begin():
            channel_lock(identity, db)
            db.execute(delete(ChannelLink).where(ChannelLink.id == link))
            db.execute(delete(ChannelSender).where(ChannelSender.sender_hash == sender))
    finally:
        identity.settings.channel_preservation_enabled = original


def verify_preservation(
    identity: IdentityService, *, expected_source_database: str | None = None
) -> None:
    if expected_source_database is None:
        _isolated(identity, "dst")
    else:
        # ADR-065 restores the same database name on a separate exclusively owned
        # server, preserving the private export scope. This verifier is read-only.
        if re.fullmatch(r"kasoma_drill_src_[0-9a-f]{32}", expected_source_database) is None:
            raise ValueError("Exact generated recovery source name required")
        with Session(identity.engine) as db:
            if db.scalar(text("SELECT current_database()")) != expected_source_database:
                raise ValueError("Restored recovery database identity mismatch")
    cipher = PreservationCipher(identity.settings.identity_encryption_key)
    with Session(identity.engine) as db:
        rows = list(db.scalars(select(ChannelSnapshot)))
        if len(rows) != 3:
            raise ValueError("Synthetic preservation fixture count mismatch")
        bodies, disposed, largest_version = 0, 0, 0
        for meta in rows:
            request = db.get(DataRequest, meta.request_id)
            if request is None or request.completed_at or request.retention_due_at:
                raise ValueError("Synthetic accountability retention changed")
            if db.get(ChannelLink, meta.source_link_id) is not None:
                raise ValueError("Synthetic operational source was not disposed")
            body = db.get(ChannelSnapshotBody, meta.id)
            receipt = db.get(ChannelSnapshotDisposal, meta.id)
            if body is None:
                if receipt is None:
                    raise ValueError("Synthetic evidence disposal receipt missing")
                disposed += 1
                continue
            if receipt is not None:
                raise ValueError("Disposed synthetic evidence was resurrected")
            binding = SnapshotBinding.model_validate(
                {
                    "snapshot_id": meta.id,
                    "request_id": meta.request_id,
                    "owner_id": request.user_id,
                    "source_kind": meta.source_kind,
                    "source_link_id": meta.source_link_id,
                    "link_revision": meta.link_revision,
                    "source_version": meta.source_version,
                }
            )
            evidence = cipher.open(binding, SecretStr(body.encrypted_payload))
            if (
                evidence.binding != binding
                or evidence.evidence.source_link_id != meta.source_link_id
            ):
                raise ValueError("Synthetic channel binding changed during recovery")
            largest_version = max(largest_version, meta.source_state_version or 0)
            bodies += 1
        last, called = db.execute(
            text("SELECT last_value,is_called FROM channel_conversation_versions")
        ).one()
        if (
            bodies != 2
            or disposed != 1
            or not called
            or last < largest_version
            or largest_version < 1
        ):
            raise ValueError("Synthetic preservation lifecycle or sequence recovery mismatch")
