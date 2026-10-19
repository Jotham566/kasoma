"""Payload-free database diagnosis for the exclusively created synthetic browser API."""

import json
import re
import sys
from threading import Lock
from time import perf_counter
from typing import Literal

import psycopg
from sqlalchemy import Engine, event, text
from sqlalchemy.engine import ExceptionContext
from sqlalchemy.sql import Select
from sqlalchemy.sql.dml import Delete, Insert, Update
from sqlalchemy.sql.selectable import TableClause

from services.config import Settings

FailureCategory = Literal[
    "QUERY_CANCELLED", "LOCK_UNAVAILABLE", "DEADLOCK", "INTEGRITY_REJECTED", "CONNECTION", "OTHER"
]
MAX_FAILURE_EVENTS = 16
Operation = Literal[
    "IDENTITY_LOCK",
    "READ",
    "ATTEMPT_WRITE",
    "GRADE_WRITE",
    "REQUEST_WRITE",
    "AUDIT_WRITE",
    "WRITE",
    "OTHER",
]


def operation(context: ExceptionContext) -> Operation:
    # Match one fixed parameterized program template; never inspect its parameter value.
    if context.statement == "SELECT pg_advisory_xact_lock(%(key)s)":
        return "IDENTITY_LOCK"
    execution = context.execution_context
    compiled = execution.compiled if execution is not None else None
    statement = compiled.statement if compiled is not None else None
    if isinstance(statement, Select):
        return "READ"
    if isinstance(statement, (Insert, Update, Delete)):
        labels: dict[str, Operation] = {
            "attempts": "ATTEMPT_WRITE",
            "grades": "GRADE_WRITE",
            "data_subject_requests": "REQUEST_WRITE",
            "audit_log": "AUDIT_WRITE",
        }
        target = statement.table
        return labels.get(target.name, "WRITE") if isinstance(target, TableClause) else "WRITE"
    return "OTHER"


def category(error: BaseException) -> FailureCategory:
    if isinstance(error, psycopg.errors.QueryCanceled):
        return "QUERY_CANCELLED"
    if isinstance(error, psycopg.errors.LockNotAvailable):
        return "LOCK_UNAVAILABLE"
    if isinstance(error, psycopg.errors.DeadlockDetected):
        return "DEADLOCK"
    if isinstance(error, psycopg.IntegrityError):
        return "INTEGRITY_REJECTED"
    if isinstance(error, psycopg.OperationalError):
        return "CONNECTION"
    return "OTHER"


def record(error: BaseException, elapsed_ms: int, command: Operation = "OTHER") -> None:
    """Never inspect messages, SQL, parameters, diagnostics or exception repr/str."""
    try:
        print(
            json.dumps(
                {
                    "event": "e2e.database_failure",
                    "category": category(error),
                    "elapsed_ms": max(0, elapsed_ms),
                    "operation": command,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
    except Exception:
        return  # Optional diagnosis cannot replace the original database exception.


def install(engine: Engine, settings: Settings, namespace: str) -> None:
    if (
        settings.app_env not in {"development", "test"}
        or settings.model_provider != "fake"
        or settings.email_provider != "fake"
        or settings.sms_provider != "fake"
        or settings.whatsapp_provider != "fake"
        or settings.allow_external_api_calls
        or not re.fullmatch(r"e2e_[0-9a-f]{32}", namespace)
    ):
        raise ValueError("Database diagnosis requires the isolated fake browser profile")
    with engine.connect() as db:
        owned = db.scalar(
            text("""SELECT n.nspname=current_schema()
              AND pg_has_role(current_user,n.nspowner,'USAGE')
              FROM pg_catalog.pg_namespace n WHERE n.nspname=:namespace"""),
            {"namespace": namespace},
        )
        if owned is not True:
            raise ValueError("Database diagnosis requires the owned browser namespace")
    started = perf_counter()
    lock = Lock()
    remaining = MAX_FAILURE_EVENTS

    def observe(context: ExceptionContext) -> None:
        nonlocal remaining
        with lock:
            if remaining <= 0:
                return
            remaining -= 1
        record(
            context.original_exception, int((perf_counter() - started) * 1000), operation(context)
        )

    event.listen(engine, "handle_error", observe)
