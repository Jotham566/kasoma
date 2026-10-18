"""Independent reviewer adapter; model output and learner identity stay hidden."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request

from apps.api.identity import bearer
from services.content_contracts import ErrorEnvelope
from services.grading_review_contracts import (
    AuditQueuePage,
    AuditReviewInput,
    AuditReviewReceipt,
    BlindedReviewTask,
)
from services.grading_reviews import GradingReviewService

router = APIRouter(
    prefix="/api/v1/admin/grading-audits",
    responses={code: {"model": ErrorEnvelope} for code in [401, 403, 404, 409, 422, 429]},
)
Key = Annotated[UUID, Header(alias="Idempotency-Key")]


@router.get("", response_model=AuditQueuePage)
def queue(
    request: Request,
    cursor: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> AuditQueuePage:
    return GradingReviewService(request.app.state.identity).list(
        bearer(request), cursor, limit, UUID(request.state.request_id)
    )


@router.get("/{audit_id}", response_model=BlindedReviewTask)
def task(audit_id: UUID, request: Request) -> BlindedReviewTask:
    return GradingReviewService(request.app.state.identity).get(
        bearer(request), audit_id, UUID(request.state.request_id)
    )


@router.post("/{audit_id}/review", response_model=AuditReviewReceipt, status_code=201)
def complete(
    audit_id: UUID, body: AuditReviewInput, request: Request, idempotency_key: Key
) -> AuditReviewReceipt:
    return GradingReviewService(request.app.state.identity).complete(
        bearer(request), audit_id, body, idempotency_key, UUID(request.state.request_id)
    )
