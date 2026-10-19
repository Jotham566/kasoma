"""ADMIN-only aggregate sampling; no executor credential or source references."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from services.config import Settings
from services.export_retirement_config import isolated_scope
from services.export_retirement_observations import read, timestamp
from services.operations_contracts import Count, RetirementCounts


def retirement_counts(db: Session, settings: Settings) -> RetirementCounts | None:
    try:
        database, namespace, enabled, age, observed = db.execute(
            text("""
          SELECT current_database(),current_schema(),enabled,
            greatest(0,floor(extract(epoch FROM clock_timestamp()-updated_at)))::bigint
           ,clock_timestamp() FROM export_retirement_state WHERE singleton
        """)
        ).one()
        due = (
            db.scalar(
                text("""
          SELECT count(*) FROM (SELECT 1 FROM data_subject_requests r
            WHERE r.kind='EXPORT' AND r.completed_at IS NOT NULL
              AND isfinite(r.completed_at) AND isfinite(r.retention_due_at)
              AND r.retention_due_at<=:observed
              AND r.retention_due_at=((r.completed_at AT TIME ZONE 'UTC')+interval '6 years')
                AT TIME ZONE 'UTC' LIMIT 10001) bounded
        """),
                {"observed": observed},
            )
            or 0
        )
        observation = read(settings.redis_url.get_secret_value(), (database, namespace))
        last, failures = observation if observation is not None else (None, 0)
        return RetirementCounts(
            scheduled=settings.export_retirement_enabled,
            database_enabled=enabled,
            scope_allowed=isolated_scope(database, namespace),
            due_requests=Count(value=min(due, 10000), at_least=due > 10000),
            last_db_progress_seconds=age,
            last_attempt_status=last.status if last else None,
            last_attempt_at=timestamp(last) if last else None,
            last_removed=last.removed if last else None,
            last_examined=last.examined if last else None,
            failures_current_interval=Count(value=min(failures, 10000), at_least=failures > 10000),
            observation_available=observation is not None,
        )
    except Exception:
        return None
