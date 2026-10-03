"""Staff-only HTTP adapter; every service call rechecks identity and role."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request

from apps.api.identity import bearer
from services.content import ContentService
from services.content_contracts import (
    ContentContext,
    CreateDraft,
    EditDraft,
    ErrorEnvelope,
    ReviewInput,
    ReviewView,
    Transition,
    VersionPage,
    VersionView,
)
from services.content_imports import ImportService
from services.import_contracts import ImportInput, ImportPage, ImportView

router = APIRouter(
    prefix="/api/v1/admin",
    responses={status: {"model": ErrorEnvelope} for status in [400, 401, 403, 404, 409, 422, 429]},
)
Key = Annotated[UUID, Header(alias="Idempotency-Key")]


def service(request: Request) -> ContentService:
    return ContentService(request.app.state.identity)


@router.get("/content-context", response_model=ContentContext)
def context(request: Request) -> ContentContext:
    return service(request).context(bearer(request))


@router.get("/items", response_model=VersionPage)
def items(
    request: Request, cursor: UUID | None = None, limit: Annotated[int, Query(ge=1, le=50)] = 20
) -> VersionPage:
    return service(request).list_versions(bearer(request), cursor, limit)


@router.post("/items", status_code=201, response_model=VersionView)
def create(body: CreateDraft, request: Request, idempotency_key: Key) -> VersionView:
    return service(request).create(
        bearer(request), body, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/item-versions/{version_id}", response_model=VersionView)
def get_version(version_id: UUID, request: Request) -> VersionView:
    return service(request).get(bearer(request), version_id)


@router.get("/item-versions/{version_id}/reviews", response_model=list[ReviewView])
def reviews(version_id: UUID, request: Request) -> list[ReviewView]:
    return service(request).reviews(bearer(request), version_id)


@router.patch("/item-versions/{version_id}", response_model=VersionView)
def edit(version_id: UUID, body: EditDraft, request: Request, idempotency_key: Key) -> VersionView:
    return service(request).mutate(
        bearer(request), version_id, "edit", body, idempotency_key, UUID(request.state.request_id)
    )


@router.post("/item-versions/{version_id}/submit", response_model=VersionView)
def submit(
    version_id: UUID, body: Transition, request: Request, idempotency_key: Key
) -> VersionView:
    return service(request).mutate(
        bearer(request), version_id, "submit", body, idempotency_key, UUID(request.state.request_id)
    )


@router.post("/item-versions/{version_id}/review", response_model=VersionView)
def review(
    version_id: UUID, body: ReviewInput, request: Request, idempotency_key: Key
) -> VersionView:
    return service(request).mutate(
        bearer(request), version_id, "review", body, idempotency_key, UUID(request.state.request_id)
    )


@router.post("/item-versions/{version_id}/retire", response_model=VersionView)
def retire(
    version_id: UUID, body: Transition, request: Request, idempotency_key: Key
) -> VersionView:
    return service(request).mutate(
        bearer(request), version_id, "retire", body, idempotency_key, UUID(request.state.request_id)
    )


@router.post(
    "/content-imports",
    status_code=202,
    response_model=ImportView,
    responses={413: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def import_drafts(body: ImportInput, request: Request, idempotency_key: Key) -> ImportView:
    return ImportService(request.app.state.identity).enqueue(
        bearer(request), body, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/content-imports", response_model=ImportPage)
def imports(
    request: Request, cursor: UUID | None = None, limit: Annotated[int, Query(ge=1, le=50)] = 20
) -> ImportPage:
    return ImportService(request.app.state.identity).listing(bearer(request), None, cursor, limit)


@router.get("/content-imports/{target}", response_model=ImportView)
def import_status(target: UUID, request: Request) -> ImportView:
    return ImportService(request.app.state.identity).listing(bearer(request), target).data[0]
