from typing import Any

from celery import Celery

from services.config import Settings
from services.observability import correlation_id, emit, tracer


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
    )

    @app.task(name="kasoma.smoke", bind=True)  # type: ignore[untyped-decorator]
    def smoke(task: Any) -> dict[str, str]:
        request_id = correlation_id((task.request.headers or {}).get("kasoma_correlation_id"))
        with tracer.start_as_current_span("worker.smoke") as span:
            span.set_attribute("correlation_id", request_id)
            emit("worker.smoke", request_id, "WORKER", 200)
        return {"correlation_id": request_id, "status": "ok"}

    return app


def worker_app() -> Celery:
    return make_worker(Settings())
