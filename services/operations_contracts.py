"""Minimized operational views; no domain record identifiers or free text."""

from datetime import datetime
from typing import Literal

from pydantic import Field

from services.health import Health
from services.identity_contracts import Contract


class Count(Contract):
    value: int = Field(ge=0, le=10000)
    at_least: bool = False


class OperationCounts(Contract):
    queued_imports: Count
    oldest_import_seconds: int = Field(ge=0)
    failed_imports_24h: Count
    unresolved_flags: Count
    high_priority_flags: Count


AlertCode = Literal[
    "DATABASE_DOWN",
    "REDIS_DOWN",
    "WORKER_HEARTBEAT_MISSING",
    "IMPORT_FAILED",
    "IMPORT_STALLED",
    "FLAG_BACKLOG",
    "HIGH_PRIORITY_FLAGS",
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
