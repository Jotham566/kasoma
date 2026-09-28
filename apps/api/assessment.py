"""Thin web API over shared consent-aware assessment services."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request

from apps.api.identity import bearer
from services.assessment import AssessmentService
from services.assessment_contracts import (
    DiagnosticReceipt,
    DiagnosticView,
    GradeView,
    LearnerItem,
    SessionView,
    SolutionView,
    StartDiagnostic,
    StartRevision,
    SubmitAnswer,
    TopicView,
)
from services.content_contracts import ErrorEnvelope

router = APIRouter(
    prefix="/api/v1",
    responses={s: {"model": ErrorEnvelope} for s in [400, 401, 403, 404, 409, 422, 429]},
)
Key = Annotated[UUID, Header(alias="Idempotency-Key")]


def service(request: Request) -> AssessmentService:
    return AssessmentService(request.app.state.identity)


@router.get("/curriculum/subjects/{subject_id}/topics", response_model=list[TopicView])
def topics(subject_id: UUID, request: Request) -> list[TopicView]:
    return service(request).topics(bearer(request), subject_id)


@router.post("/revision-sessions", response_model=SessionView, status_code=201)
def start(body: StartRevision, request: Request, idempotency_key: Key) -> SessionView:
    return service(request).start(
        bearer(request), body, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/sessions/active", response_model=list[SessionView])
def active(request: Request) -> list[SessionView]:
    return service(request).active(bearer(request))


@router.get("/sessions/{session_id}", response_model=SessionView | DiagnosticView)
def get(session_id: UUID, request: Request) -> SessionView | DiagnosticView:
    return service(request).get(bearer(request), session_id)


@router.get("/sessions/{session_id}/next-item", response_model=LearnerItem)
def next_item(session_id: UUID, request: Request) -> LearnerItem:
    return service(request).next_item(bearer(request), session_id, UUID(request.state.request_id))


@router.post("/sessions/{session_id}/attempts", response_model=GradeView | DiagnosticReceipt)
def submit(
    session_id: UUID, body: SubmitAnswer, request: Request, idempotency_key: Key
) -> GradeView | DiagnosticReceipt:
    return service(request).submit(
        bearer(request), session_id, body, idempotency_key, UUID(request.state.request_id)
    )


@router.post("/sessions/{session_id}/abandon", response_model=SessionView | DiagnosticView)
def abandon(session_id: UUID, request: Request) -> SessionView | DiagnosticView:
    return service(request).abandon(bearer(request), session_id, UUID(request.state.request_id))


@router.get("/attempts/{attempt_id}/grade", response_model=GradeView)
def grade(attempt_id: UUID, request: Request) -> GradeView | SolutionView:
    return service(request).result(bearer(request), attempt_id)


@router.get("/attempts/{attempt_id}/solution", response_model=SolutionView)
def solution(attempt_id: UUID, request: Request) -> GradeView | SolutionView:
    return service(request).result(bearer(request), attempt_id, solution=True)


@router.post("/diagnostics", response_model=DiagnosticView, status_code=201)
def diagnostic_start(
    body: StartDiagnostic, request: Request, idempotency_key: Key
) -> DiagnosticView:
    return service(request).diagnostics.start(
        bearer(request), body, idempotency_key, UUID(request.state.request_id)
    )


@router.get("/diagnostics/{session_id}", response_model=DiagnosticView)
def diagnostic_get(session_id: UUID, request: Request) -> DiagnosticView:
    from services.identity import IdentityError

    result = service(request).get(bearer(request), session_id)
    if not isinstance(result, DiagnosticView):
        raise IdentityError("RESOURCE_NOT_FOUND", 404)
    return result
