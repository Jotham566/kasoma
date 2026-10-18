from fastapi import APIRouter, Request

from apps.api.identity import bearer
from services.audit_activity import AuditActivity
from services.audit_activity import read as audit_activity
from services.content_contracts import ErrorEnvelope
from services.operations import read
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
