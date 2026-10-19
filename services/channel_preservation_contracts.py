"""ADR-057 exact synthetic source selection; never a payload-reading contract."""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field

from services.identity_contracts import Contract
from services.legal_hold_contracts import HoldReason

SnapshotKind = Literal["CHANNEL_LINK_SNAPSHOT", "CHANNEL_CONVERSATION_SNAPSHOT"]


class PreservationSource(Contract):
    source_kind: SnapshotKind
    source_link_id: UUID
    link_revision: int = Field(strict=True, ge=1, le=2_147_483_647)


class PreservationVersion(Contract):
    source_version: str = Field(pattern=r"^[a-f0-9]{64}$", min_length=64, max_length=64)


class PreservationCapture(PreservationSource, PreservationVersion):
    decision_reference: UUID
    reason: HoldReason
    expires_at: AwareDatetime
    affirmative: Literal[True]
