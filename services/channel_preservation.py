"""ADR-057 default-disabled exact synthetic capture, never operational capability."""

import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, load_only

from services.channel_preservation_contracts import (
    PreservationCapture,
    PreservationSource,
    PreservationVersion,
)
from services.channel_preservation_format import (
    ConversationEvidence,
    LinkEvidence,
    PreservationCipher,
    PreservationFormatError,
    SnapshotBinding,
)
from services.domain.channel_preservation import ChannelSnapshot, ChannelSnapshotBody
from services.domain.data_requests import DataRequest, DataRequestReview, LegalHold
from services.domain.messaging import ChannelLink, ChannelSender, ConversationState, OutboundMessage
from services.identity import IdentityError, IdentityService
from services.legal_hold_contracts import HoldView
from services.legal_holds import LegalHoldService, database_now
from services.whatsapp_linking import channel_lock


@dataclass(frozen=True, repr=False)
class Material:
    evidence: LinkEvidence | ConversationEvidence
    state_version: int | None
    version: str


class ChannelPreservationService:
    def __init__(self, identity: IdentityService):
        self.identity = identity
        self.holds = LegalHoldService(identity)

    def enabled(self) -> None:
        if not self.identity.settings.channel_preservation_enabled:
            raise IdentityError("HOLD_TARGET_UNAVAILABLE", 409)

    def material(
        self, db: Session, request: DataRequest, source: PreservationSource, now: datetime
    ) -> Material:
        link = db.scalar(
            select(ChannelLink)
            .options(
                load_only(
                    ChannelLink.id,
                    ChannelLink.user_id,
                    ChannelLink.sender_hash,
                    ChannelLink.revision,
                    ChannelLink.status,
                    ChannelLink.linked_at,
                    ChannelLink.opted_out_at,
                    ChannelLink.updated_at,
                )
            )
            .where(
                ChannelLink.id == source.source_link_id,
                ChannelLink.user_id == request.user_id,
                ChannelLink.revision == source.link_revision,
                ChannelLink.status == "ACTIVE",
            )
            .with_for_update()
        )
        if link is None:
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        sender = db.scalar(
            select(ChannelSender)
            .options(load_only(ChannelSender.sender_hash, ChannelSender.barrier_at))
            .where(ChannelSender.sender_hash == link.sender_hash)
            .with_for_update()
        )
        if sender is None or (sender.barrier_at and sender.barrier_at >= link.linked_at):
            raise IdentityError("RESOURCE_NOT_FOUND", 404)
        state_version = None
        evidence: LinkEvidence | ConversationEvidence
        if source.source_kind == "CHANNEL_LINK_SNAPSHOT":
            evidence = LinkEvidence(
                source_link_id=link.id,
                revision=link.revision,
                status="ACTIVE",
                linked_at=link.linked_at,
                opted_out_at=link.opted_out_at,
                updated_at=link.updated_at,
            )
        else:
            state = db.scalar(
                select(ConversationState)
                .where(
                    ConversationState.link_id == link.id,
                    ConversationState.actor_id == request.user_id,
                    ConversationState.link_revision == link.revision,
                    ConversationState.expires_at > now,
                )
                .with_for_update()
            )
            if state is None or (state.session_id is None and state.expected_outbound_id is None):
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            if (
                state.expected_outbound_id is not None
                and db.scalar(
                    select(OutboundMessage.id)
                    .where(
                        OutboundMessage.id == state.expected_outbound_id,
                        OutboundMessage.actor_id == request.user_id,
                        OutboundMessage.link_id == link.id,
                        OutboundMessage.link_revision == link.revision,
                    )
                    .with_for_update()
                )
                is None
            ):
                raise IdentityError("RESOURCE_NOT_FOUND", 404)
            state_version = state.state_version
            evidence = ConversationEvidence(
                source_link_id=link.id,
                link_revision=state.link_revision,
                session_id=state.session_id,
                expected_outbound_id=state.expected_outbound_id,
                updated_at=state.updated_at,
                expires_at=state.expires_at,
            )
        version = self.identity.digest(
            "channel-preservation-source-version-v1",
            json.dumps(
                {
                    "request_id": str(request.id),
                    "owner_id": str(request.user_id),
                    "source_kind": source.source_kind,
                    "state_version": state_version,
                    "evidence": evidence.model_dump(mode="json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ),
        )
        return Material(evidence, state_version, version)

    def inspect(
        self, token: str, target: UUID, source: PreservationSource, request_id: UUID
    ) -> PreservationVersion:
        with self.identity.transaction() as db:
            actor, request = self.holds.access(db, token, target)
            self.enabled()
            if not self.identity.rate(db, f"legal-hold-read:{actor}", 60, 60):
                raise IdentityError("RATE_LIMITED", 429)
            channel_lock(self.identity, db)
            now = database_now(db)
            review = db.get(DataRequestReview, target)
            if review is None or review.created_at > now:
                raise IdentityError("HOLD_TARGET_UNAVAILABLE", 503)
            material = self.material(db, request, source, now)
            self.holds.requests.audit(db, actor, target, "legal_hold.source_checked", request_id)
            return PreservationVersion(source_version=material.version)

    def capture(
        self, token: str, target: UUID, body: PreservationCapture, key: UUID, request_id: UUID
    ) -> HoldView:
        body = body.model_copy(update={"expires_at": body.expires_at.astimezone(UTC)})
        digest = self.identity.digest(
            "channel-preservation-capture", f"{target}:{body.model_dump_json()}"
        )
        try:
            with self.identity.transaction() as db:
                actor, request = self.holds.access(db, token, target)
                self.enabled()
                channel_lock(self.identity, db)
                old = self.holds.replay(db, actor, key, digest)
                if old:
                    return self.holds.view(old, database_now(db))
                now = database_now(db)
                review = db.get(DataRequestReview, target)
                if review is None or review.created_at > now:
                    raise IdentityError("HOLD_TARGET_UNAVAILABLE", 503)
                if body.expires_at <= now:
                    raise IdentityError("HOLD_END_REQUIRED", 422)
                material = self.material(db, request, body, now)
                if not hmac.compare_digest(body.source_version, material.version):
                    raise IdentityError("SOURCE_VERSION_CONFLICT", 409)
                # IdentityError commits outer rate accounting. Every capture write
                # must roll back together, even when a late failure is IdentityError.
                with db.begin_nested():
                    snapshot = uuid4()
                    binding = SnapshotBinding(
                        snapshot_id=snapshot,
                        request_id=target,
                        owner_id=request.user_id,
                        source_kind=body.source_kind,
                        source_link_id=body.source_link_id,
                        link_revision=body.link_revision,
                        source_version=material.version,
                    )
                    encrypted = PreservationCipher(
                        self.identity.settings.identity_encryption_key
                    ).seal(binding, material.evidence)
                    db.add(
                        ChannelSnapshot(
                            id=snapshot,
                            request_id=target,
                            source_kind=body.source_kind,
                            source_link_id=body.source_link_id,
                            link_revision=body.link_revision,
                            source_state_version=material.state_version,
                            source_version=material.version,
                            captured_by=actor,
                            captured_at=now,
                        )
                    )
                    db.flush()
                    db.add(
                        ChannelSnapshotBody(
                            snapshot_id=snapshot, encrypted_payload=encrypted.get_secret_value()
                        )
                    )
                    db.flush()
                    row = LegalHold(
                        id=uuid4(),
                        request_id=target,
                        record_type=body.source_kind,
                        record_id=snapshot,
                        decision_reference=body.decision_reference,
                        reason=body.reason,
                        created_by=actor,
                        created_at=now,
                        expires_at=body.expires_at,
                        released_at=None,
                        released_by=None,
                        release_reference=None,
                    )
                    db.add(row)
                    db.flush()
                    self.holds.evidence(
                        db,
                        actor,
                        row,
                        key,
                        digest,
                        "legal_hold.created",
                        request.user_id,
                        request_id,
                    )
                    db.flush()
                    result = self.holds.view(row, database_now(db))
                return result
        except (DBAPIError, PreservationFormatError):
            raise IdentityError("HOLD_TARGET_UNAVAILABLE", 409) from None


def dispose_bodies(db: Session) -> int:
    """Caller holds channel lock. Active exact decisions are excluded before LIMIT."""
    rows = list(
        db.scalars(
            select(ChannelSnapshotBody)
            .join(ChannelSnapshot, ChannelSnapshot.id == ChannelSnapshotBody.snapshot_id)
            .where(
                ~func.record_is_held(
                    ChannelSnapshot.source_kind, ChannelSnapshot.id, func.clock_timestamp()
                )
            )
            .order_by(ChannelSnapshotBody.snapshot_id)
            .limit(100)
            .with_for_update(of=ChannelSnapshotBody, skip_locked=True)
        )
    )
    for row in rows:
        db.delete(row)
    db.flush()
    return len(rows)
