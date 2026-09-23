"""HTTP transport only; identity policy is owned by IdentityService."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request, Response

from services.identity import IdentityService
from services.identity_contracts import (
    ConsentInput,
    Credentials,
    OTPAccepted,
    OTPRequest,
    OTPVerify,
    ProfilePatch,
    ProfileView,
    Refresh,
    SubjectView,
)

router = APIRouter(prefix="/api/v1")


def service(request: Request) -> IdentityService:
    result: IdentityService = request.app.state.identity
    return result


def bearer(request: Request) -> str:
    header = request.headers.get("authorization", "")
    return header[7:] if header.startswith("Bearer ") and len(header) <= 160 else ""


@router.post("/auth/otp/request", status_code=202, response_model=OTPAccepted)
def request_otp(body: OTPRequest, request: Request) -> OTPAccepted:
    return service(request).request_otp(
        body, request.client.host if request.client else "unknown", bearer(request)
    )


@router.post("/auth/otp/verify", response_model=Credentials)
def verify(body: OTPVerify, request: Request) -> Credentials:
    return service(request).verify(body, bearer(request), request.state.request_id)


@router.post("/auth/refresh", response_model=Credentials)
def refresh(body: Refresh, request: Request) -> Credentials:
    return service(request).refresh(body.refresh_token)


@router.post("/auth/logout", status_code=204)
def logout(request: Request) -> Response:
    service(request).logout(bearer(request), False, request.state.request_id)
    return Response(status_code=204)


@router.post("/auth/logout-all", status_code=204)
def logout_all(request: Request) -> Response:
    service(request).logout(bearer(request), True, request.state.request_id)
    return Response(status_code=204)


@router.get("/me", response_model=ProfileView)
def me(request: Request) -> ProfileView:
    return service(request).me(bearer(request))


@router.patch("/me", response_model=ProfileView)
def patch_me(body: ProfilePatch, request: Request) -> ProfileView:
    return service(request).update_profile(bearer(request), body, request.state.request_id)


@router.post("/me/consents", response_model=ProfileView)
def consent(
    body: ConsentInput, request: Request, idempotency_key: Annotated[UUID, Header()]
) -> ProfileView:
    return service(request).consent(
        bearer(request), body, idempotency_key, request.state.request_id
    )


@router.get("/curriculum/subjects", response_model=list[SubjectView])
def subjects(request: Request) -> list[SubjectView]:
    return service(request).subjects()
