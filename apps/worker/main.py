from typing import Any
from uuid import UUID, uuid4

from celery import Celery

from services.assessment import AssessmentService
from services.config import Settings
from services.content_imports import process_imports
from services.data_exports import expire
from services.database import engine_for
from services.identity import IdentityService
from services.identity_expiry import expire_identity
from services.observability import correlation_id, emit, tracer
from services.operations import monitor
from services.providers import FakeMessagingProvider
from services.short_text_processor import ShortTextProcessor
from services.whatsapp_jobs import process_messages


def make_worker(settings: Settings) -> Celery:
    app = Celery("kasoma", broker=settings.redis_url.get_secret_value())
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_ignore_result=True,
        task_soft_time_limit=15,
        task_time_limit=20,
        worker_hijack_root_logger=False,
        task_default_queue="operations",
        broker_connection_retry_on_startup=True,
        task_publish_retry=False,
        task_queues={"operations": {}, "grading": {}, "imports": {}, "messaging": {}},
        task_routes={"kasoma.grade_short_text": {"queue": "grading"}},
        beat_schedule={
            "short-text-grading": {
                "task": "kasoma.grade_short_text",
                "schedule": 5.0,
                "options": {"queue": "grading"},
            },
            "channel-messages": {
                "task": "kasoma.channel_messages",
                "schedule": 10.0,
                "options": {"queue": "messaging"},
            },
            "monitor-operations": {"task": "kasoma.monitor_operations", "schedule": 60.0},
            "expire-identity": {"task": "kasoma.expire_identity", "schedule": 60.0},
            "expire-exports": {"task": "kasoma.expire_exports", "schedule": 300.0},
            "content-imports": {
                "task": "kasoma.content_imports",
                "schedule": 30.0,
                "options": {"queue": "imports"},
            },
        },
    )

    @app.task(shared=False, name="kasoma.smoke", bind=True)  # type: ignore[untyped-decorator]
    def smoke(task: Any) -> dict[str, str]:
        request_id = correlation_id((task.request.headers or {}).get("kasoma_correlation_id"))
        with tracer.start_as_current_span("worker.smoke") as span:
            span.set_attribute("correlation_id", request_id)
            emit("worker.smoke", request_id, "WORKER", 200)
        return {"correlation_id": request_id, "status": "ok"}

    @app.task(shared=False, name="kasoma.grade_short_text", acks_late=True)  # type: ignore[untyped-decorator]
    def grade_short_text() -> bool:
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            identity = IdentityService(engine, settings, fake, fake)
            return ShortTextProcessor(AssessmentService(identity)).process_one()
        finally:
            engine.dispose()

    @app.task(shared=False, name="kasoma.expire_exports", bind=True)  # type: ignore[untyped-decorator]
    def expire_exports(task: Any) -> int:
        request_id = correlation_id((task.request.headers or {}).get("kasoma_correlation_id"))
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            return expire(IdentityService(engine, settings, fake, fake), UUID(request_id))
        finally:
            engine.dispose()

    @app.task(shared=False, name="kasoma.expire_identity", bind=True)  # type: ignore[untyped-decorator]
    def identity_expiry(task: Any) -> dict[str, int]:
        request_id = correlation_id((task.request.headers or {}).get("kasoma_correlation_id"))
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            return expire_identity(IdentityService(engine, settings, fake, fake), UUID(request_id))
        finally:
            engine.dispose()

    @app.task(shared=False, name="kasoma.content_imports", acks_late=True)  # type: ignore[untyped-decorator]
    def content_imports() -> int:
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            return process_imports(IdentityService(engine, settings, fake, fake))
        finally:
            engine.dispose()

    @app.task(shared=False, name="kasoma.monitor_operations")  # type: ignore[untyped-decorator]
    def monitor_operations() -> int:
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            return monitor(
                IdentityService(engine, settings, fake, fake), uuid4(), worker_sample=True
            )
        finally:
            engine.dispose()

    @app.task(shared=False, name="kasoma.channel_messages", acks_late=True)  # type: ignore[untyped-decorator]
    def channel_messages() -> int:
        engine = engine_for(settings)
        try:
            fake = FakeMessagingProvider()
            return process_messages(IdentityService(engine, settings, fake, fake))
        finally:
            engine.dispose()

    from apps.worker.exports import register

    register(app, settings)
    return app


def worker_app() -> Celery:
    return make_worker(Settings())
