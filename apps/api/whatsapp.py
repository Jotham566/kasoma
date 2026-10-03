"""Owner channel endpoints; provider ingress never uses a learner bearer token."""

import hmac
import re
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request, Response
from starlette.concurrency import run_in_threadpool

from apps.api.identity import bearer, service
from services.content_contracts import ErrorEnvelope
from services.whatsapp_contracts import ChannelLinkView, LinkCodeView, UnlinkInput, WebhookAccepted
from services.whatsapp_ingress import MAX_WEBHOOK_BYTES, WebhookRejected
from services.whatsapp_intake import ingest
from services.whatsapp_linking import LinkingService

router = APIRouter(
    prefix="/api/v1/channels/whatsapp",
    responses={s: {"model": ErrorEnvelope} for s in [401, 403, 409, 410, 422, 429, 503]},
)


@router.post("/link-code", response_model=LinkCodeView, status_code=201)
def issue(
    request: Request, idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")]
) -> LinkCodeView:
    return LinkingService(service(request)).issue(
        bearer(request), idempotency_key, UUID(request.state.request_id)
    )


@router.get("/link", response_model=ChannelLinkView)
def status(request: Request) -> ChannelLinkView:
    return LinkingService(service(request)).status(bearer(request))


@router.delete("/link", response_model=ChannelLinkView)
def unlink(
    body: UnlinkInput,
    request: Request,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> ChannelLinkView:
    return LinkingService(service(request)).unlink(
        bearer(request),
        body.expected_revision,
        idempotency_key,
        UUID(request.state.request_id),
        body.expected_link_id,
    )


webhook_router = APIRouter(
    prefix="/api/v1/webhooks/whatsapp",
    responses={s: {"model": ErrorEnvelope} for s in [400, 401, 409, 413, 503]},
)


@webhook_router.get("", response_class=Response)
def verify(request: Request) -> Response:
    token = service(request).settings.whatsapp_verify_token
    supplied = request.query_params.get("hub.verify_token", "")
    challenge = request.query_params.get("hub.challenge", "")
    if token is None or len(token.get_secret_value()) < 32:
        raise WebhookRejected("WEBHOOK_UNAVAILABLE", 503)
    if (
        request.query_params.get("hub.mode") != "subscribe"
        or not hmac.compare_digest(supplied.encode(), token.get_secret_value().encode())
        or re.fullmatch(r"[0-9]{1,64}", challenge) is None
    ):
        raise WebhookRejected("WEBHOOK_VERIFICATION_INVALID", 401)
    return Response(challenge, media_type="text/plain")


@webhook_router.post("", response_model=WebhookAccepted)
async def receive(request: Request) -> WebhookAccepted:
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_WEBHOOK_BYTES:
            raise WebhookRejected("WEBHOOK_SIZE_INVALID", 413)
        raw.extend(chunk)
    await run_in_threadpool(
        ingest,
        service(request),
        bytes(raw),
        request.headers.get("x-hub-signature-256"),
        UUID(request.state.request_id),
    )
    return WebhookAccepted()
