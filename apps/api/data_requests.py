"""FR-ID-006 HTTP transport; policy belongs to identity's request service."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request, Response

from apps.api.identity import bearer, service
from services.content_contracts import ErrorEnvelope
from services.data_request_contracts import (
    DataExportBundle,
    DataRequestClaim,
    DataRequestInput,
    DataRequestPage,
    DataRequestView,
    DeletionPreview,
)
from services.data_requests import DataRequestService

router = APIRouter(
    prefix="/api/v1",
    responses={s: {"model": ErrorEnvelope} for s in [401, 403, 404, 409, 410, 422, 429]},
)


@router.post("/me/data-requests", response_model=DataRequestView, status_code=201)
def create(
    body: DataRequestInput,
    request: Request,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> DataRequestView:
    return DataRequestService(service(request)).create(
        bearer(request), body, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/me/data-requests", response_model=DataRequestPage)
def listing(
    request: Request, cursor: UUID | None = None, limit: Annotated[int, Query(ge=1, le=50)] = 20
) -> DataRequestPage:
    return DataRequestService(service(request)).listing(
        bearer(request), cursor, limit, UUID(request.state.request_id)
    )


@router.get("/me/data-requests/{target}", response_model=DataRequestView)
def get(target: UUID, request: Request) -> DataRequestView:
    return DataRequestService(service(request)).get(bearer(request), target)


@router.get("/admin/data-requests", response_model=DataRequestPage)
def queue(
    request: Request, cursor: UUID | None = None, limit: Annotated[int, Query(ge=1, le=50)] = 20
) -> DataRequestPage:
    return DataRequestService(service(request)).listing(
        bearer(request), cursor, limit, UUID(request.state.request_id), staff=True
    )


@router.post("/admin/data-requests/{target}/claim", response_model=DataRequestView)
def claim(
    target: UUID,
    body: DataRequestClaim,
    request: Request,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> DataRequestView:
    return DataRequestService(service(request)).claim(
        bearer(request), target, idempotency_key, UUID(request.state.request_id)
    )


@router.post("/me/data-requests/{target}/export", response_model=DataExportBundle)
def export(
    target: UUID,
    body: DataRequestClaim,
    request: Request,
    response: Response,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> DataExportBundle:
    from services.data_exports import download

    result = download(
        service(request), bearer(request), target, idempotency_key, UUID(request.state.request_id)
    )
    response.headers["Content-Disposition"] = f'attachment; filename="kasoma-export-{target}.json"'
    return result


@router.get("/admin/data-requests/{target}/deletion-preview", response_model=DeletionPreview)
def deletion_preview(target: UUID, request: Request) -> DeletionPreview:
    from services.deletion_preview import preview

    return preview(service(request), bearer(request), target, UUID(request.state.request_id))
