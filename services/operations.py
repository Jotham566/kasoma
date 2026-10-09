"""Read-only bounded operational sampling and local allowlisted alerts."""

import json
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from redis import Redis
from sqlalchemy import Select, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from services.domain.content import ContentImport
from services.domain.export_jobs import ExportJob
from services.domain.flags import ContentFlag
from services.health import Health, dependency_health
from services.identity import IdentityError, IdentityService
from services.observability import logger
from services.operations_contracts import (
    Count,
    ExportCounts,
    OperationAlert,
    OperationCounts,
    OperationsView,
    OperationThresholds,
    RequestTiming,
)
from services.request_metrics_collector import metric_cache, metric_scope
from services.request_metrics_store import RequestMetricStore
from services.staff import authorize


def thresholds(identity: IdentityService) -> OperationThresholds:
    settings = identity.settings
    return OperationThresholds(
        request_p95_ms=settings.ops_request_p95_ms,
        request_min_samples=settings.ops_request_min_samples,
        failed_imports=settings.ops_failed_import_threshold,
        import_age_seconds=settings.ops_import_age_seconds,
        unresolved_flags=settings.ops_flag_backlog_threshold,
        channel_failures=settings.ops_channel_failure_threshold,
        channel_queue_age_seconds=settings.ops_channel_queue_age_seconds,
        channel_dispatch_p95_ms=settings.ops_channel_dispatch_p95_ms,
        channel_dispatch_min_samples=settings.ops_channel_dispatch_min_samples,
        export_failures=settings.ops_export_failure_threshold,
        export_age_seconds=settings.ops_export_age_seconds,
    )


def bounded_count(db: Session, query: Select[tuple[int]]) -> Count:
    value = db.scalar(select(func.count()).select_from(query.limit(10001).subquery())) or 0
    return Count(value=min(value, 10000), at_least=value > 10000)


def counts(db: Session, now: datetime) -> OperationCounts:
    from services.channel_operations import channel_counts

    pending = select(1).select_from(ContentImport).where(ContentImport.status == "QUEUED")
    flags = select(1).select_from(ContentFlag).where(ContentFlag.status.in_(["OPEN", "IN_REVIEW"]))
    oldest = db.scalar(
        select(func.min(ContentImport.created_at)).where(ContentImport.status == "QUEUED")
    )
    return OperationCounts(
        queued_imports=bounded_count(db, pending),
        oldest_import_seconds=max(0, int((now - oldest).total_seconds())) if oldest else 0,
        failed_imports_24h=bounded_count(
            db,
            select(1)
            .select_from(ContentImport)
            .where(
                ContentImport.status == "FAILED",
                ContentImport.finished_at >= now - timedelta(hours=24),
                ContentImport.finished_at <= now,
            ),
        ),
        unresolved_flags=bounded_count(db, flags),
        high_priority_flags=bounded_count(db, flags.where(ContentFlag.priority == "HIGH")),
        channel=channel_counts(db, now),
        exports=export_counts(db, now),
    )


def export_counts(db: Session, now: datetime) -> ExportCounts:
    jobs = select(1).select_from(ExportJob)
    oldest = db.scalar(
        select(func.min(ExportJob.queued_at)).where(ExportJob.status.in_(["QUEUED", "RUNNING"]))
    )
    return ExportCounts(
        queued=bounded_count(db, jobs.where(ExportJob.status == "QUEUED")),
        running=bounded_count(db, jobs.where(ExportJob.status == "RUNNING")),
        failed_finished_24h=bounded_count(
            db,
            jobs.where(
                ExportJob.status == "FAILED",
                ExportJob.finished_at >= now - timedelta(hours=24),
                ExportJob.finished_at <= now,
            ),
        ),
        oldest_pending_seconds=max(0, int((now - oldest).total_seconds())) if oldest else 0,
    )


def evaluate(
    health: Health,
    worker: Literal["up", "unavailable"],
    values: OperationCounts | None,
    limits: OperationThresholds,
    request_metric: RequestTiming | None = None,
) -> list[OperationAlert]:
    alerts: list[OperationAlert] = []
    if request_metric is not None and request_metric.sample_size >= limits.request_min_samples:
        lower = request_metric.p95_lower_exclusive_ms
        # Integer-ms measurements make lower + 1 a proven inclusive lower bound.
        # An overlapping upper bound alone never establishes a threshold breach.
        observed = lower + 1 if lower is not None else 0
        if observed >= limits.request_p95_ms:
            alerts.append(
                OperationAlert(
                    code="REQUEST_RESPONSE_START_SLOW",
                    severity="WARNING",
                    observed=observed,
                    threshold=limits.request_p95_ms,
                )
            )
    if health.database == "down":
        alerts.append(
            OperationAlert(code="DATABASE_DOWN", severity="CRITICAL", observed=1, threshold=1)
        )
    if health.redis == "down":
        alerts.append(
            OperationAlert(code="REDIS_DOWN", severity="CRITICAL", observed=1, threshold=1)
        )
    if worker == "unavailable":
        alerts.append(
            OperationAlert(
                code="WORKER_HEARTBEAT_MISSING", severity="WARNING", observed=1, threshold=1
            )
        )
    if values:
        for code, severity, observed, threshold in [
            ("IMPORT_FAILED", "WARNING", values.failed_imports_24h.value, limits.failed_imports),
            ("IMPORT_STALLED", "WARNING", values.oldest_import_seconds, limits.import_age_seconds),
            ("FLAG_BACKLOG", "WARNING", values.unresolved_flags.value, limits.unresolved_flags),
            ("HIGH_PRIORITY_FLAGS", "CRITICAL", values.high_priority_flags.value, 1),
        ]:
            if observed >= threshold:
                alerts.append(
                    OperationAlert.model_validate(
                        {
                            "code": code,
                            "severity": severity,
                            "observed": observed,
                            "threshold": threshold,
                        }
                    )
                )
    if values and values.channel:
        channel = values.channel
        observations = [
            (
                "CHANNEL_INBOUND_FAILED",
                channel.failed_inbound_received_24h.value,
                limits.channel_failures,
            ),
            (
                "CHANNEL_OUTBOUND_FAILED",
                channel.failed_outbound_created_24h.value,
                limits.channel_failures,
            ),
            ("CHANNEL_STALLED", channel.oldest_pending_seconds, limits.channel_queue_age_seconds),
        ]
        timing = channel.feedback_dispatch
        if timing.p95_ms is not None and timing.sample_size >= limits.channel_dispatch_min_samples:
            observations.append(
                ("CHANNEL_DISPATCH_SLOW", timing.p95_ms, limits.channel_dispatch_p95_ms)
            )
        for code, observed, threshold in observations:
            if observed >= threshold:
                alerts.append(
                    OperationAlert.model_validate(
                        {
                            "code": code,
                            "severity": "WARNING",
                            "observed": observed,
                            "threshold": threshold,
                        }
                    )
                )
    if values and values.exports:
        for code, observed, threshold in [
            ("EXPORT_FAILED", values.exports.failed_finished_24h.value, limits.export_failures),
            ("EXPORT_STALLED", values.exports.oldest_pending_seconds, limits.export_age_seconds),
        ]:
            if observed >= threshold:
                alerts.append(
                    OperationAlert.model_validate(
                        {
                            "code": code,
                            "severity": "WARNING",
                            "observed": observed,
                            "threshold": threshold,
                        }
                    )
                )
    return alerts


def heartbeat_key(identity: IdentityService) -> str:
    url = make_url(identity.settings.database_url.get_secret_value())
    # Host aliases differ between native and Compose processes for the same database.
    scope = json.dumps(
        {"database": url.database, "options": url.query.get("options", "")}, sort_keys=True
    )
    return "kasoma:ops:heartbeat:" + identity.digest("operations-heartbeat", scope)


def heartbeat(identity: IdentityService, *, write: bool = False) -> Literal["up", "unavailable"]:
    try:
        with Redis.from_url(
            identity.settings.redis_url.get_secret_value(),
            socket_connect_timeout=2,
            socket_timeout=2,
        ) as cache:
            now = identity.clock()
            if write:
                cache.set(heartbeat_key(identity), now.isoformat(), ex=180)
                return "up"
            raw = cache.get(heartbeat_key(identity))
            if not isinstance(raw, bytes):
                return "unavailable"
            at = datetime.fromisoformat(raw.decode())
            age = (now - at).total_seconds()
            return "up" if 0 <= age < 180 else "unavailable"
    except Exception:
        return "unavailable"


def snapshot(identity: IdentityService, *, worker_sample: bool = False) -> OperationsView:
    health = dependency_health(identity.settings)
    values = None
    if health.database == "up":
        try:
            with Session(identity.engine) as db:
                values = counts(db, identity.clock())
        except Exception:
            health = health.model_copy(update={"database": "down", "status": "degraded"})
    worker = heartbeat(identity, write=worker_sample)
    limits = thresholds(identity)
    timing = request_timing(identity)
    view = OperationsView(
        generated_at=identity.clock(),
        health=health,
        worker=worker,
        counts=values,
        thresholds=limits,
        alerts=evaluate(health, worker, values, limits, timing),
        request_timing=timing,
    )
    if timing is not None:
        view.unavailable_metrics = [m for m in view.unavailable_metrics if m != "REQUEST_LATENCY"]
    return view


def request_timing(identity: IdentityService) -> RequestTiming | None:
    try:
        with metric_cache(identity.settings) as cache:
            value = RequestMetricStore(cache, metric_scope(identity.settings)).read()
        if value is None:
            return None
        return RequestTiming(
            sample_size=value.estimate.sample_size,
            p95_lower_exclusive_ms=value.estimate.p95_lower_exclusive_ms,
            p95_upper_inclusive_ms=value.estimate.p95_upper_inclusive_ms,
            interval_count=value.interval_count,
            capped=value.capped,
        )
    except Exception:
        return None


def read(identity: IdentityService, token: str) -> OperationsView:
    with identity.transaction() as db:
        actor = authorize(identity, db, token, {"ADMIN"})[0]
        if not identity.rate(db, f"operations-read:{actor}", 20, 60):
            raise IdentityError("RATE_LIMITED", 429)
    return snapshot(identity)


def emit_alerts(view: OperationsView, request_id: UUID) -> int:
    for alert in view.alerts:
        logger.warning(
            json.dumps(
                {
                    "event": "operations.alert",
                    "schema_version": 1,
                    "correlation_id": str(request_id),
                    "channel": "WORKER",
                    **alert.model_dump(),
                },
                sort_keys=True,
            )
        )
    return len(view.alerts)


def monitor(identity: IdentityService, request_id: UUID, *, worker_sample: bool = False) -> int:
    return emit_alerts(snapshot(identity, worker_sample=worker_sample), request_id)
