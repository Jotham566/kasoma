"""Thin web API over shared consent-aware assessment services."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request

from apps.api.identity import bearer
from services.assessment import AssessmentService
from services.assessment_contracts import (
    DiagnosticReceipt,
    DiagnosticView,
    GradeView,
    HintRequest,
    HintState,
    LearnerItem,
    RecommendationView,
    SessionView,
    SolutionView,
    StartDiagnostic,
    StartRevision,
    SubmitAnswer,
    TopicView,
)
from services.content_contracts import ErrorEnvelope
from services.progress_contracts import ProgressView, SessionHistoryPage

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


@router.get("/me/recommendations/next", response_model=RecommendationView)
def recommendation(subject_id: UUID, request: Request) -> RecommendationView:
    return service(request).recommendation(bearer(request), subject_id)


@router.post("/sessions/{session_id}/items/{item_id}/hint", response_model=HintState)
def revision_hint(
    session_id: UUID, item_id: UUID, body: HintRequest, request: Request, idempotency_key: Key
) -> HintState:
    from services.hints import access

    return access(
        service(request),
        bearer(request),
        session_id=session_id,
        item_id=item_id,
        body=body,
        key=idempotency_key,
        request=UUID(request.state.request_id),
    )


@router.post("/attempts/{attempt_id}/hint", response_model=HintState)
def attempt_hint(
    attempt_id: UUID, body: HintRequest, request: Request, idempotency_key: Key
) -> HintState:
    from services.hints import access

    return access(
        service(request),
        bearer(request),
        attempt_id=attempt_id,
        body=body,
        key=idempotency_key,
        request=UUID(request.state.request_id),
    )


@router.get("/attempts/{attempt_id}/hints", response_model=HintState)
def attempt_hints(attempt_id: UUID, request: Request) -> HintState:
    from services.hints import access

    return access(service(request), bearer(request), attempt_id=attempt_id)


@router.post("/attempts/{attempt_id}/reassessment", response_model=SessionView)
def reassessment_start(attempt_id: UUID, request: Request, idempotency_key: Key) -> SessionView:
    from services.reassessments import access

    return access(
        service(request),
        bearer(request),
        attempt_id,
        idempotency_key,
        UUID(request.state.request_id),
    )


@router.get("/attempts/{attempt_id}/reassessment", response_model=SessionView)
def reassessment_get(attempt_id: UUID, request: Request) -> SessionView:
    from services.reassessments import access

    return access(service(request), bearer(request), attempt_id)


@router.get("/me/progress", response_model=ProgressView)
def learner_progress(subject_id: UUID, request: Request) -> ProgressView:
    from services.progress import progress

    return progress(service(request), bearer(request), subject_id)


@router.get("/me/session-history", response_model=SessionHistoryPage)
def learner_history(
    request: Request,
    subject_id: UUID | None = None,
    cursor: Annotated[str | None, Query(max_length=512)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> SessionHistoryPage:
    from services.progress import history

    return history(service(request), bearer(request), subject_id, cursor, limit)
