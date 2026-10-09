"""ADR-048 candidate owned job and attachment routes."""

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

import anyio
from fastapi import APIRouter, Depends, Header, Request

from apps.api.export_transfer import AsyncExportResponse
from apps.api.identity import bearer, service
from services.content_contracts import ErrorEnvelope
from services.export_downloads import AsyncExportStore, prepare_async
from services.export_job_contracts import ExportJobCommand, ExportJobView
from services.export_jobs import queue, status
from services.export_reader import PrivateExportReader

router = APIRouter(
    prefix="/api/v1",
    responses={code: {"model": ErrorEnvelope} for code in [401, 403, 404, 409, 410, 422, 429, 503]},
)


def reader_factory(request: Request) -> Callable[[], AsyncExportStore]:
    return lambda: PrivateExportReader(service(request).settings)


@router.post("/me/data-requests/{target}/export-job", response_model=ExportJobView, status_code=202)
def enqueue(
    target: UUID,
    body: ExportJobCommand,
    request: Request,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> ExportJobView:
    return queue(
        service(request), bearer(request), target, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/me/data-requests/{target}/export-job", response_model=ExportJobView)
def get_status(target: UUID, request: Request) -> ExportJobView:
    return status(service(request), bearer(request), target)


@router.get(
    "/me/data-requests/{target}/export-file",
    status_code=200,
    response_class=AsyncExportResponse,
    responses={
        200: {
            "description": "Private JSON attachment; exact length, no-store, 24-hour availability.",
            "content": {"application/json": {"schema": {"type": "string", "format": "binary"}}},
        }
    },
)
async def download(
    target: UUID,
    request: Request,
    storage: Annotated[Callable[[], AsyncExportStore], Depends(reader_factory)],
) -> AsyncExportResponse:
    with anyio.fail_after(8):
        result = await prepare_async(service(request), storage, bearer(request), target)
    return AsyncExportResponse(result, target)
