"""Browser diagnosis cannot disclose SQL/payloads or suppress the original failure."""

import json
from unittest.mock import MagicMock, Mock

import psycopg
import pytest
from sqlalchemy import column, insert, select, table, text

from scripts.e2e_failures import category, install, operation, record


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (psycopg.errors.QueryCanceled("synthetic-secret"), "QUERY_CANCELLED"),
        (psycopg.errors.LockNotAvailable("synthetic-secret"), "LOCK_UNAVAILABLE"),
        (psycopg.errors.DeadlockDetected("synthetic-secret"), "DEADLOCK"),
        (psycopg.errors.UniqueViolation("synthetic-secret"), "INTEGRITY_REJECTED"),
        (psycopg.OperationalError("synthetic-secret"), "CONNECTION"),
        (ValueError("synthetic-secret"), "OTHER"),
    ],
)
def test_fixed_categories_and_no_error_body(error, expected, capsys):
    assert category(error) == expected
    record(error, 7)
    captured = capsys.readouterr()
    assert captured.out == ""
    output = captured.err
    assert json.loads(output) == {
        "event": "e2e.database_failure",
        "category": expected,
        "elapsed_ms": 7,
        "operation": "OTHER",
    }
    assert "synthetic-secret" not in output


def test_arbitrary_exception_message_and_repr_are_never_inspected(capsys):
    class PrivateFailure(Exception):
        def __str__(self):
            raise AssertionError("Do not inspect")

        def __repr__(self):
            raise AssertionError("Do not inspect")

    record(PrivateFailure(), -1)
    assert json.loads(capsys.readouterr().err)["elapsed_ms"] == 0


def test_broken_output_cannot_mask_the_database_error(monkeypatch):
    monkeypatch.setattr("builtins.print", Mock(side_effect=OSError("private-output-error")))
    record(psycopg.errors.QueryCanceled("synthetic-secret"), 1)


@pytest.mark.parametrize(
    "changes",
    [
        {"model_provider": "local"},
        {"email_provider": "mailpit"},
        {"app_env": "production"},
        {"allow_external_api_calls": True},
    ],
)
def test_non_fake_profiles_refuse_before_connecting(settings, changes):
    engine = Mock()
    with pytest.raises(ValueError, match="isolated fake"):
        install(engine, settings.model_copy(update=changes), "e2e_" + "a" * 32)
    engine.connect.assert_not_called()


@pytest.mark.parametrize("namespace", ["public", "e2e_bad", "identity_test_" + "a" * 32])
def test_existing_review_or_other_namespaces_refuse_before_connecting(settings, namespace):
    engine = Mock()
    with pytest.raises(ValueError, match="isolated fake"):
        install(engine, settings, namespace)
    engine.connect.assert_not_called()


def test_observer_requires_actual_ownership_and_emits_at_most16_fixed_events(
    settings, monkeypatch, capsys
):
    engine = MagicMock()
    db = engine.connect.return_value.__enter__.return_value
    db.scalar.return_value = False
    listen = Mock()
    monkeypatch.setattr("scripts.e2e_failures.event.listen", listen)
    with pytest.raises(ValueError, match="owned browser"):
        install(engine, settings, "e2e_" + "a" * 32)
    listen.assert_not_called()
    db.scalar.return_value = True
    install(engine, settings, "e2e_" + "a" * 32)
    callback = listen.call_args.args[2]
    context = Mock(original_exception=psycopg.errors.QueryCanceled("synthetic-secret"))
    for _ in range(20):
        assert callback(context) is None
    lines = capsys.readouterr().err.splitlines()
    assert len(lines) == 16
    assert {json.loads(line)["category"] for line in lines} == {"QUERY_CANCELLED"}
    assert all("synthetic-secret" not in line for line in lines)


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        (select(column("private-column")), "READ"),
        (insert(table("attempts", column("private-column"))), "ATTEMPT_WRITE"),
        (insert(table("grades", column("private-column"))), "GRADE_WRITE"),
        (insert(table("data_subject_requests", column("private-column"))), "REQUEST_WRITE"),
        (insert(table("audit_log", column("private-column"))), "AUDIT_WRITE"),
        (insert(table("private-source", column("private-column"))), "WRITE"),
        (text("SELECT 'private-sql-value'"), "OTHER"),
    ],
)
def test_operation_uses_only_closed_labels_not_sql_names_or_parameters(statement, expected, capsys):
    context = Mock(statement="not-a-known-template")
    context.execution_context.compiled.statement = statement
    label = operation(context)
    assert label == expected
    record(ValueError("private-exception"), 1, label)
    output = capsys.readouterr().err
    assert not any(
        value in output
        for value in ["private-column", "private-source", "private-sql-value", "private-exception"]
    )


def test_identity_lock_tag_requires_exact_parameterized_template():
    context = Mock(statement="SELECT pg_advisory_xact_lock(%(key)s)")
    assert operation(context) == "IDENTITY_LOCK"
    context.statement = "SELECT pg_advisory_xact_lock(123456)"
    assert operation(context) == "OTHER"
