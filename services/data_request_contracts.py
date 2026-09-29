"""FR-ID-006: minimized request intake, never a claim of fulfillment."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from services.identity_contracts import Contract

RequestKind = Literal["EXPORT", "DELETE"]


class DataRequestInput(Contract):
    kind: RequestKind
    affirmative: Literal[True]


class DataRequestView(Contract):
    id: UUID
    kind: RequestKind
    status: Literal["QUEUED", "IN_REVIEW"]
    created_at: datetime
    reviewed_at: datetime | None
    retention_policy: Literal["SIX_YEARS_AFTER_COMPLETION"] = "SIX_YEARS_AFTER_COMPLETION"


class DataRequestPage(Contract):
    data: list[DataRequestView]
    next_cursor: UUID | None


class DataRequestClaim(Contract):
    pass
