"""Strict metadata only; no free-text legal details or personal record bodies."""

from datetime import datetime
from typing import Literal, get_args
from uuid import UUID

from pydantic import AwareDatetime, Field

from services.identity_contracts import Contract

RecordType = Literal[
    "CONSENT",
    "ATTEMPT",
    "CONTENT_FLAG",
    "DATA_REQUEST",
    "GRADE",
    "MASTERY_EVIDENCE",
    "MASTERY_HISTORY",
    "FLAG_HISTORY",
    "DATA_REQUEST_REVIEW",
    "GRADING_HISTORY",
    "GRADING_PUBLICATION",
    "GRADING_AUDIT",
    "GRADING_REVIEW",
    "CHANNEL_INBOUND_RECEIPT",
    "CHANNEL_OUTBOUND_RECEIPT",
    "CHANNEL_LINK_SNAPSHOT",
    "CHANNEL_CONVERSATION_SNAPSHOT",
]
CHANNEL_RECEIPT_TYPES = frozenset({"CHANNEL_INBOUND_RECEIPT", "CHANNEL_OUTBOUND_RECEIPT"})
CHANNEL_SNAPSHOT_TYPES = frozenset({"CHANNEL_LINK_SNAPSHOT", "CHANNEL_CONVERSATION_SNAPSHOT"})


def supported_record_types(
    channel_receipts: bool, channel_snapshots: bool = False
) -> list[RecordType]:
    return [
        kind
        for kind in get_args(RecordType)
        if (channel_receipts or kind not in CHANNEL_RECEIPT_TYPES)
        and (channel_snapshots or kind not in CHANNEL_SNAPSHOT_TYPES)
    ]


HoldReason = Literal["LEGAL_OBLIGATION", "SECURITY_INVESTIGATION"]


class HoldInput(Contract):
    record_type: RecordType
    record_id: UUID
    decision_reference: UUID
    reason: HoldReason
    expires_at: AwareDatetime
    affirmative: Literal[True]


class HoldRelease(Contract):
    decision_reference: UUID
    affirmative: Literal[True]


class HoldView(Contract):
    id: UUID
    request_id: UUID
    record_type: RecordType
    record_id: UUID
    decision_reference: UUID
    reason: HoldReason
    status: Literal["ACTIVE", "EXPIRED", "RELEASED"]
    created_at: datetime
    expires_at: datetime
    released_at: datetime | None
    release_reference: UUID | None
    retention_policy: Literal["SIX_YEARS_AFTER_REQUEST_COMPLETION"] = (
        "SIX_YEARS_AFTER_REQUEST_COMPLETION"
    )


class HoldPage(Contract):
    data: list[HoldView]
    next_cursor: UUID | None
    supported_record_types: list[RecordType] = Field(default_factory=list)
