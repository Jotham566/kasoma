"""FR-ID-006: minimized request lifecycle and versioned personal export."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

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


RetentionCategory = Literal[
    "REMOVE_DIRECT_LINKAGE",
    "ANONYMIZATION_REVIEW",
    "SIX_YEARS_AFTER_CLOSURE_OR_WITHDRAWAL",
    "SIX_YEARS_AFTER_COMPLETION",
    "TWENTY_FOUR_MONTHS_AFTER_RESOLUTION",
    "EXPIRES_AFTER_24_HOURS",
    "STAFF_PROVENANCE_REVIEW",
    "TRANSIENT_EXPIRY",
    "ACTIVE_EXACT_PRESERVATION_ONLY",
]


class DeletionSource(Contract):
    source: str
    count: int = Field(ge=0, le=10_000)
    at_least: bool
    retention: RetentionCategory


class DeletionPreview(Contract):
    request_id: UUID
    observed_at: datetime
    execution_enabled: Literal[False] = False
    active_legal_holds: int = Field(default=0, ge=0, le=10_000)
    active_holds_at_least: bool = False
    sources: list[DeletionSource]
    blockers: list[
        Literal[
            "LEGAL_HOLD_CHECK_UNAVAILABLE",
            "LEGAL_HOLD_COVERAGE_INCOMPLETE",
            "ACTIVE_RECORD_HOLDS",
            "ERASURE_PROCESSOR_UNAVAILABLE",
            "ANONYMIZATION_REVIEW_REQUIRED",
            "STAFF_RECORDS_REQUIRE_REVIEW",
        ]
    ]
    limitations: list[str]
