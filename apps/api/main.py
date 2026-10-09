from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from math import ceil
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from apps.api.assessment import router as assessment_router
from apps.api.content import router as content_router
from apps.api.data_requests import router as data_requests_router
from apps.api.export_jobs import router as export_jobs_router
from apps.api.flags import router as flags_router
from apps.api.identity import router
from apps.api.import_limit import ImportBodyLimit
from apps.api.operations import router as operations_router
from apps.api.whatsapp import router as whatsapp_router
from apps.api.whatsapp import webhook_router
from services.config import Settings
from services.content import ContentError
from services.database import engine_for
from services.health import Health, dependency_health
from services.identity import IdentityError, IdentityService
from services.observability import correlation_id, emit, tracer
from services.providers import FakeMessagingProvider, MailpitEmailProvider
from services.whatsapp_ingress import WebhookRejected


class Live(BaseModel):
    status: str = "ok"


def create_app(
    settings: Settings | None = None,
    identity: IdentityService | None = None,
    channel_wakeup: Callable[[Settings, str], None] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        from services.whatsapp_wakeup import wake

        app.state.channel_wakeup = channel_wakeup or wake
        app.state.settings = settings or Settings()
        config = app.state.settings
        engine = engine_for(config)
        email = (
            FakeMessagingProvider()
            if config.email_provider == "fake"
            else MailpitEmailProvider(config)
        )
        app.state.identity = identity or IdentityService(
            engine, config, email, FakeMessagingProvider()
        )
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Kasoma API", version="0.1.0", lifespan=lifespan)
    app.include_router(router)
    app.include_router(content_router)
    app.include_router(assessment_router)
    app.include_router(flags_router)
    app.include_router(data_requests_router)
    app.include_router(export_jobs_router)
    app.include_router(operations_router)
    app.include_router(whatsapp_router)
    app.include_router(webhook_router)
    app.add_middleware(ImportBodyLimit)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.app_public_url] if settings else [],
        allow_methods=["GET"],
        allow_headers=["request_id"],
        expose_headers=["request_id"],
    )

    @app.middleware("http")
    async def correlate(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = perf_counter()
        request_id = correlation_id(request.headers.get("request_id"))
        request.state.request_id = request_id
        with tracer.start_as_current_span("api.request") as span:
            span.set_attribute("correlation_id", request_id)
            try:
                response = await call_next(request)
            except Exception:
                response = error(request, 500, "INTERNAL_ERROR", "The service is unavailable.")
            response.headers["request_id"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Cache-Control"] = "no-store"
            channel = "WHATSAPP" if request.url.path == "/api/v1/webhooks/whatsapp" else "WEB"
            response_start_ms = max(0, ceil((perf_counter() - started) * 1000))
            span.set_attribute("http.response.status_code", response.status_code)
            span.set_attribute("response_start_ms", response_start_ms)
            emit(
                "api.request",
                request_id,
                channel,
                response.status_code,
                response_start_ms=response_start_ms,
            )
            return response

    @app.exception_handler(WebhookRejected)
    async def webhook_error(request: Request, exc: WebhookRejected) -> JSONResponse:
        return error(request, exc.status, exc.code, "Webhook could not be accepted.")

    @app.exception_handler(IdentityError)
    async def identity_error(request: Request, exc: IdentityError) -> JSONResponse:
        return error(
            request,
            exc.status,
            exc.code,
            "This action could not be completed.",
            exc.fields if isinstance(exc, ContentError) else [],
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return error(request, exc.status_code, "RESOURCE_NOT_FOUND", "Resource unavailable.")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error(request, 422, "VALIDATION_FAILED", "Invalid request.")

    @app.get("/api/v1/live", response_model=Live, operation_id="get_liveness")
    def live() -> Live:
        return Live()

    @app.get(
        "/api/v1/health",
        response_model=Health,
        operation_id="get_health",
        responses={503: {"model": Health, "description": "Dependency unavailable"}},
    )
    def health(request: Request, response: Response) -> Health:
        result = dependency_health(request.app.state.settings)
        response.status_code = 200 if result.status == "ok" else 503
        return result

    return app


def error(
    request: Request, status: int, code: str, message: str, fields: list[str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request.state.request_id,
                "field_errors": [
                    {"field": field, "message": "Review this field."} for field in (fields or [])
                ],
            }
        },
    )


app = create_app()
