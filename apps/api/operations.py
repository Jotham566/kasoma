from fastapi import APIRouter, Request

from apps.api.identity import bearer
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
