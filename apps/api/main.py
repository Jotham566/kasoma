from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from services.config import Settings
from services.health import Health, dependency_health
from services.observability import correlation_id, emit, tracer


class Live(BaseModel):
    status: str = "ok"


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = settings or Settings()
        yield

    app = FastAPI(title="Kasoma API", version="0.1.0", lifespan=lifespan)
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
            emit("api.request", request_id, "WEB", response.status_code)
            return response

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


def error(request: Request, status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request.state.request_id,
                "field_errors": [],
            }
        },
    )


app = create_app()
