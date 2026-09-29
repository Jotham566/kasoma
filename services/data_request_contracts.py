"""FR-ID-006: minimized request lifecycle and versioned personal export."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from services.identity_contracts import Contract

RequestKind = Literal["EXPORT", "DELETE"]


class DataRequestInput(Contract):
    kind: RequestKind
    affirmative: Literal[True]


class DataRequestView(Contract):
    id: UUID
    kind: RequestKind
    status: Literal["QUEUED", "IN_REVIEW", "COMPLETED"]
    created_at: datetime
    reviewed_at: datetime | None
    completed_at: datetime | None = None
    retention_due_at: datetime | None = None
    download_expires_at: datetime | None = None
    retention_policy: Literal["SIX_YEARS_AFTER_COMPLETION"] = "SIX_YEARS_AFTER_COMPLETION"


class DataRequestPage(Contract):
    data: list[DataRequestView]
    next_cursor: UUID | None


class DataRequestClaim(Contract):
    pass


class DataExportBundle(Contract):
    format_version: Literal["kasoma-personal-export-v1"] = "kasoma-personal-export-v1"
    request_id: UUID
    generated_at: datetime
    exclusions: list[str]
    records: dict[str, list[dict[str, Any]]]
