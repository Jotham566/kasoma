"""Best-effort local queue wake-up after durable intake; periodic drain recovers outages."""

from celery import Celery

from services.config import Settings
from services.observability import emit


def wake(settings: Settings, request_id: str) -> None:
    try:
        with Celery("kasoma-channel-wakeup", broker=settings.redis_url.get_secret_value()) as app:
            app.conf.update(
                broker_connection_timeout=0.2,
                broker_connection_max_retries=0,
                broker_pool_limit=0,
                task_publish_retry=False,
                broker_transport_options={
                    "socket_connect_timeout": 0.2,
                    "socket_timeout": 0.2,
                    "retry_on_timeout": False,
                    "retry_policy": {"max_retries": 0},
                },
            )
            app.send_task(
                "kasoma.channel_messages",
                queue="messaging",
                retry=False,
                headers={"kasoma_correlation_id": request_id},
            )
    except Exception:
        emit("channel.wakeup_failed", request_id, "WHATSAPP", 503)
