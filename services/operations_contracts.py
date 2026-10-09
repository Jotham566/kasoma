"""Minimized operational views; no domain record identifiers or free text."""

from datetime import datetime
from typing import Literal

from pydantic import Field

from services.health import Health
from services.identity_contracts import Contract


class Count(Contract):
    value: int = Field(ge=0, le=10000)
    at_least: bool = False


class DispatchTiming(Contract):
    sample_size: int = Field(ge=0, le=1000)
    sample_capped: bool
    p95_ms: int | None = Field(ge=0)
    measure: Literal["LOCAL_FAKE_ACCEPTANCE"] = "LOCAL_FAKE_ACCEPTANCE"


class ChannelCounts(Contract):
    queued_inbound: Count
    queued_outbound: Count
    oldest_pending_seconds: int = Field(ge=0)
    failed_inbound_received_24h: Count
    rejected_inbound_received_24h: Count
    failed_outbound_created_24h: Count
    cancelled_outbound_created_24h: Count
    accepted_outbound_created_24h: Count
    feedback_dispatch: DispatchTiming


class ExportCounts(Contract):
    queued: Count
    running: Count
    failed_finished_24h: Count
    oldest_pending_seconds: int = Field(ge=0)


class OperationCounts(Contract):
    queued_imports: Count
    oldest_import_seconds: int = Field(ge=0)
    failed_imports_24h: Count
    unresolved_flags: Count
    high_priority_flags: Count
    channel: ChannelCounts | None = None
    exports: ExportCounts | None = None


AlertCode = Literal[
    "DATABASE_DOWN",
    "REDIS_DOWN",
    "WORKER_HEARTBEAT_MISSING",
    "IMPORT_FAILED",
    "IMPORT_STALLED",
    "FLAG_BACKLOG",
    "HIGH_PRIORITY_FLAGS",
    "CHANNEL_INBOUND_FAILED",
    "CHANNEL_OUTBOUND_FAILED",
    "CHANNEL_STALLED",
    "CHANNEL_DISPATCH_SLOW",
    "EXPORT_FAILED",
    "EXPORT_STALLED",
]


class OperationAlert(Contract):
    code: AlertCode
    severity: Literal["WARNING", "CRITICAL"]
    observed: int = Field(ge=0)
    threshold: int = Field(ge=0)


class OperationThresholds(Contract):
    failed_imports: int = Field(ge=1, le=10000)
    import_age_seconds: int = Field(ge=60, le=86400)
    unresolved_flags: int = Field(ge=1, le=10000)
    channel_failures: int = Field(default=1, ge=1, le=10000)
    channel_queue_age_seconds: int = Field(default=60, ge=1, le=86400)
    channel_dispatch_p95_ms: int = Field(default=1500, ge=1, le=60000)
    channel_dispatch_min_samples: int = Field(default=20, ge=1, le=1000)
    export_failures: int = Field(default=1, ge=1, le=10000)
    export_age_seconds: int = Field(default=300, ge=60, le=86400)


class OperationsView(Contract):
    schema_version: Literal[1] = 1
    generated_at: datetime
    health: Health
    worker: Literal["up", "unavailable"]
    counts: OperationCounts | None
    thresholds: OperationThresholds
    alerts: list[OperationAlert]
    unavailable_metrics: list[
        Literal[
            "AI_USAGE",
            "MESSAGING_USAGE",
            "GRADING_FAILURE_RATE",
            "REQUEST_LATENCY",
            "MASTERY_LAG",
            "WEBHOOK_FAILURES",
        ]
    ] = [
        "AI_USAGE",
        "MESSAGING_USAGE",
        "GRADING_FAILURE_RATE",
        "REQUEST_LATENCY",
        "MASTERY_LAG",
        "WEBHOOK_FAILURES",
    ]
