from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request

from apps.api.identity import bearer
from services.audit_activity import AuditActivity
from services.audit_activity import read as audit_activity
from services.content_contracts import ErrorEnvelope
from services.operations import read
from services.operations_configuration import change as change_configuration
from services.operations_configuration import read as read_configuration
from services.operations_configuration_contracts import (
    ConfigurationChange,
    ConfigurationKey,
    ConfigurationPatch,
    ConfigurationView,
)
from services.operations_contracts import OperationsView

router = APIRouter(
    prefix="/api/v1/admin",
    responses={status: {"model": ErrorEnvelope} for status in [401, 403, 429]},
)


@router.get("/operations", response_model=OperationsView)
def operations(request: Request) -> OperationsView:
    return read(request.app.state.identity, bearer(request))


@router.get("/audit", response_model=AuditActivity)
def audit(request: Request) -> AuditActivity:
    return audit_activity(request.app.state.identity, bearer(request))


@router.get(
    "/configuration", response_model=ConfigurationView, responses={503: {"model": ErrorEnvelope}}
)
def configuration(request: Request) -> ConfigurationView:
    return read_configuration(request.app.state.identity, bearer(request))


@router.patch(
    "/configuration/{key}",
    response_model=ConfigurationChange,
    responses={status: {"model": ErrorEnvelope} for status in [409, 413, 422, 503]},
)
def configure(
    key: ConfigurationKey,
    body: ConfigurationPatch,
    request: Request,
    command: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> ConfigurationChange:
    return change_configuration(
        request.app.state.identity,
        bearer(request),
        key,
        body,
        command,
        UUID(request.state.request_id),
    )
