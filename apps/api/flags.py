"""Learner and staff adapters; server owns report linkage and authorization."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request

from apps.api.identity import bearer
from services.content_contracts import ErrorEnvelope
from services.flag_contracts import FlagDetail, FlagInput, FlagPage, FlagReceipt, FlagUpdate, Status
from services.flags import FlagService

router = APIRouter(
    prefix="/api/v1",
    responses={s: {"model": ErrorEnvelope} for s in [401, 403, 404, 409, 422, 429]},
)
Key = Annotated[UUID, Header(alias="Idempotency-Key")]


def service(request: Request) -> FlagService:
    return FlagService(request.app.state.identity)


@router.post("/attempts/{attempt_id}/flag", response_model=FlagReceipt, status_code=201)
def report(
    attempt_id: UUID, body: FlagInput, request: Request, idempotency_key: Key
) -> FlagReceipt:
    return service(request).create(
        bearer(request), attempt_id, body, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/attempts/{attempt_id}/flag", response_model=list[FlagReceipt])
def owned_reports(attempt_id: UUID, request: Request) -> list[FlagReceipt]:
    return service(request).owned_reports(bearer(request), attempt_id)


@router.get("/admin/content-flags", response_model=FlagPage)
def queue(
    request: Request,
    cursor: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    status: Status | None = None,
) -> FlagPage:
    return service(request).list(
        bearer(request), cursor, limit, status, UUID(request.state.request_id)
    )


@router.get("/admin/content-flags/{flag_id}", response_model=FlagDetail)
def detail(flag_id: UUID, request: Request) -> FlagDetail:
    return service(request).get(bearer(request), flag_id, UUID(request.state.request_id))


@router.patch("/admin/content-flags/{flag_id}", response_model=FlagDetail)
def triage(flag_id: UUID, body: FlagUpdate, request: Request, idempotency_key: Key) -> FlagDetail:
    return service(request).update(
        bearer(request), flag_id, body, idempotency_key, UUID(request.state.request_id)
    )
