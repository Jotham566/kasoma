"""Allowlisted operational events. Never pass arbitrary payloads to the logger."""

import json
import logging
from uuid import UUID, uuid4

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("kasoma.foundation", "1")
logger = logging.getLogger("kasoma")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def correlation_id(value: str | None) -> str:
    try:
        return str(UUID(value)) if value else str(uuid4())
    except (ValueError, AttributeError):
        return str(uuid4())


def emit(
    event: str, request_id: str, channel: str, status: int, *, response_start_ms: int | None = None
) -> None:
    logger.info(
        json.dumps(
            {
                "event": event,
                "correlation_id": correlation_id(request_id),
                "channel": channel,
                "status": status,
                "schema_version": 1,
                **(
                    {"response_start_ms": response_start_ms}
                    if response_start_ms is not None
                    else {}
                ),
            },
            sort_keys=True,
        )
    )
