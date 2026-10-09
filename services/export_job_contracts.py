"""ADR-048 owner job status contracts."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from services.identity_contracts import Contract

ExportFailure = Literal["AUTH_REQUIRED", "LIMIT_REACHED", "PROCESSING_FAILED", "REQUEST_COMPLETED"]


class ExportJobCommand(Contract):
    pass


class ExportJobView(Contract):
    request_id: UUID
    status: Literal["QUEUED", "RUNNING", "FAILED", "READY", "EXPIRED"]
    queued_at: datetime
    finished_at: datetime | None
    attempts: int = Field(ge=0, le=3)
    failure: ExportFailure | None
    expires_at: datetime | None
    size_bytes: int | None = Field(ge=1, le=16 * 1024 * 1024)
