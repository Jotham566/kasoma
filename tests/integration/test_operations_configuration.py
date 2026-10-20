"""FR-OPS-002/003: actual SQL authority, atomic versioning and safe retries."""

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.content import AuditLog
from services.domain.operations_configuration import WarningConfigurationVersion
from services.identity import IdentityError
from services.operations_configuration import ACTION, change, current, defaults
from services.operations_configuration_contracts import ConfigurationPatch, WarningValues
from services.staff import provision

pytestmark = pytest.mark.integration
PATH = "/api/v1/admin/configuration"


def get(client, actors):
    response = client.get(PATH, headers=actors["admin"])
    assert response.status_code == 200, response.text
    return response.json()


def patch(client, actors, view, *, key="failed_imports", value=2, command=None, **extra):
    return client.patch(
        PATH + "/" + key,
        headers=actors["admin"] | {"Idempotency-Key": str(command or uuid4())},
        json={"version": view["version"], "value": value, "reason": "REDUCE_NOISE"} | extra,
    )


@pytest.mark.parametrize("identity", ["0042"], indirect=True)
def test_configuration_additive_upgrade_preserves_existing_staff_and_content(content):
    service, client, actors, body = content
    created = client.post(
        "/api/v1/admin/items",
        headers=actors["author"] | {"Idempotency-Key": str(uuid4())},
        json=body,
    )
    assert created.status_code == 201, created.text
    before = {}
    with service.engine.connect() as connection:
        for table in ["users", "user_roles", "auth_sessions", "item_versions", "audit_log"]:
            before[table] = list(
                connection.scalars(text(f"SELECT to_jsonb(t)::text FROM {table} t ORDER BY 1"))
            )
    unavailable = client.get(PATH, headers=actors["admin"])
    assert unavailable.status_code == 503
    subprocess.run(
        ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
        env=os.environ | {"DATABASE_URL": service.settings.database_url.get_secret_value()},
        check=True,
        capture_output=True,
    )
    with service.engine.connect() as connection:
        for table, rows in before.items():
            actual = [
                json.loads(row)
                for row in connection.scalars(
                    text(f"SELECT to_jsonb(t)::text FROM {table} t ORDER BY 1")
                )
            ]
            expected = [json.loads(row) for row in rows]
            if table == "users":
                assert all("closed_at" not in row for row in expected)
                # 0045 adds only a nullable clock; every prior field/row must survive.
                expected = [row | {"closed_at": None} for row in expected]
            assert actual == expected
    view = get(client, actors)
    assert view["revision"] == 0
    assert patch(client, actors, view).status_code == 200


def test_configuration_authorization_recent_login_and_strict_request(content, identity):
    service, client, actors, _ = content
    assert client.get(PATH).status_code == 401
    view = get(client, actors)
    assert view["revision"] == 0 and view["source"] == "ENVIRONMENT_DEFAULTS"
    assert view["updated_at"] is None and view["values"] == defaults(service.settings).model_dump()
    body = {"version": view["version"], "value": 2, "reason": "REDUCE_NOISE"}
    for role in ["learner", "author", "reviewer", "support"]:
        assert client.get(PATH, headers=actors[role]).status_code == 403
        assert (
            client.patch(
                PATH + "/failed_imports",
                headers=actors[role] | {"Idempotency-Key": str(uuid4())},
                json=body,
            ).status_code
            == 403
        )
    for invalid in [True, "2", 0, 10001]:
        assert patch(client, actors, view, value=invalid).status_code == 422
    assert patch(client, actors, view, reason="input-canary").status_code == 422
    assert patch(client, actors, view, unexpected="input-canary").status_code == 422
    assert patch(client, actors, view, key="model_provider").status_code == 422
    assert (
        client.patch(PATH + "/failed_imports", headers=actors["admin"], json=body).status_code
        == 422
    )
    identity[3][0] += timedelta(minutes=10)
    refused = patch(client, actors, view)
    assert refused.status_code == 401 and refused.json()["error"]["code"] == "REAUTH_REQUIRED"
    assert get(client, actors)["revision"] == 0
    provision(service, "admin@example.invalid", "ADMIN", revoke=True)
    assert client.get(PATH, headers=actors["admin"]).status_code == 403


def test_configuration_frozen_snapshot_and_exact_historical_retry(content):
    service, client, actors, _ = content
    initial = get(client, actors)
    command = uuid4()
    first = patch(client, actors, initial, command=command)
    assert first.status_code == 200, first.text
    recorded = first.json()["recorded"]
    assert recorded["revision"] == 1 and not first.json()["replayed"]
    assert recorded["source"] == "VERSIONED" and recorded["updated_at"] is not None
    assert recorded["values"] == initial["values"] | {"failed_imports": 2}
    second = patch(client, actors, recorded, key="unresolved_flags", value=3)
    assert second.status_code == 200, second.text
    retry = patch(client, actors, initial, command=command)
    assert retry.status_code == 200 and retry.json() == {"recorded": recorded, "replayed": True}
    assert get(client, actors)["revision"] == 2
    assert patch(client, actors, initial).status_code == 409
    for changes in [{"value": 3}, {"key": "unresolved_flags"}, {"reason": "REVIEWED_BASELINE"}]:
        assert patch(client, actors, initial, command=command, **changes).status_code == 409
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(WarningConfigurationVersion)) == 2
        receipts = list(db.scalars(select(AuditLog).where(AuditLog.action == ACTION)))
        assert len(receipts) == 2
        assert str(command) not in repr(
            [(a.id, a.reason, a.before_hash, a.after_hash) for a in receipts]
        )
        alternate = service.settings.model_copy(update={"ops_failed_import_threshold": 777})
        assert current(db, alternate).values.failed_imports == 2
    operations = client.get("/api/v1/admin/operations", headers=actors["admin"]).json()
    assert operations["configuration_state"] == "VERSIONED"
    assert operations["thresholds"]["failed_imports"] == 2
    assert operations["thresholds"]["unresolved_flags"] == 3


def test_configuration_environment_change_invalidates_only_unstored_reference(content):
    service, client, actors, _ = content
    initial = get(client, actors)
    service.settings = service.settings.model_copy(update={"ops_failed_import_threshold": 8})
    assert patch(client, actors, initial).status_code == 409
    fresh = get(client, actors)
    assert fresh["revision"] == 0 and fresh["version"] != initial["version"]
    assert fresh["values"]["failed_imports"] == 8
    assert patch(client, actors, fresh).status_code == 200


def test_configuration_failed_audit_rolls_back_version_and_pointer(content):
    service, client, actors, _ = content
    view = get(client, actors)
    with service.engine.begin() as connection:
        connection.execute(
            text("""
          CREATE FUNCTION reject_configuration_audit() RETURNS trigger LANGUAGE plpgsql AS $$
          BEGIN
            IF NEW.action='operations.configuration.changed' THEN
              RAISE EXCEPTION 'diagnostic-canary' USING ERRCODE='42501';
            END IF;
            RETURN NEW;
          END $$;
          CREATE TRIGGER reject_configuration_audit BEFORE INSERT ON audit_log
          FOR EACH ROW EXECUTE FUNCTION reject_configuration_audit();
        """)
        )
    response = patch(client, actors, view)
    assert response.status_code == 503 and "diagnostic-canary" not in response.text
    assert get(client, actors) == view
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(WarningConfigurationVersion)) == 0


def test_configuration_worker_uses_saved_warning_values_with_different_startup_defaults(
    content, monkeypatch
):
    import services.operations as operations
    from apps.worker.main import make_worker

    service, client, actors, _ = content
    assert patch(client, actors, get(client, actors), value=2).status_code == 200
    evaluate, observed = operations.evaluate, []

    def observe(health, worker, counts, limits, *observations):
        observed.append(limits.failed_imports)
        return evaluate(health, worker, counts, limits, *observations)

    monkeypatch.setattr(operations, "evaluate", observe)
    alternate = service.settings.model_copy(update={"ops_failed_import_threshold": 888})
    worker = make_worker(alternate)
    try:
        worker.tasks["kasoma.monitor_operations"].run()
    finally:
        worker.close()
    assert observed == [2]


def test_configuration_concurrent_identical_retry_and_stale_distinct_commands(content):
    service, client, actors, _ = content
    initial = get(client, actors)
    token = actors["admin"]["Authorization"][7:]
    body = ConfigurationPatch(version=initial["version"], value=2, reason="REDUCE_NOISE")
    command = uuid4()

    def execute(key):
        try:
            return change(service, token, "failed_imports", body, key, uuid4())
        except IdentityError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(execute, [command, command]))
    assert sorted(result.replayed for result in results) == [False, True]
    fresh = get(client, actors)
    body = ConfigurationPatch(version=fresh["version"], value=3, reason="REDUCE_NOISE")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(execute, [uuid4(), uuid4()]))
    assert sum(isinstance(result, IdentityError) for result in results) == 1
    assert [result.code for result in results if isinstance(result, IdentityError)] == [
        "VERSION_CONFLICT"
    ]
    assert get(client, actors)["revision"] == 2


def test_configuration_sql_history_and_pointer_guards_and_atomic_audit(content):
    service, client, actors, _ = content
    first = patch(client, actors, get(client, actors))
    assert first.status_code == 200, first.text
    for statement in [
        "UPDATE operations_configuration_versions SET reason='REVIEWED_BASELINE'",
        "DELETE FROM operations_configuration_versions",
        "TRUNCATE operations_configuration_versions CASCADE",
        "DELETE FROM operations_configuration_state",
        "TRUNCATE operations_configuration_state",
        "UPDATE operations_configuration_state SET revision=0,current_id=NULL",
        "UPDATE operations_configuration_state SET nonce=gen_random_uuid()",
    ]:
        with pytest.raises(DBAPIError), service.engine.begin() as connection:
            connection.execute(text(statement))
    # A valid-shaped append without the atomic active-ADMIN audit cannot commit.
    with pytest.raises(DBAPIError), service.engine.begin() as connection:
        target = uuid4()
        connection.execute(
            text("""
            INSERT INTO operations_configuration_versions
              (id,revision,thresholds,version_ref,previous_ref,command_hash,changed_key,reason)
            SELECT :target,2,thresholds,:ref,version_ref,:hash,changed_key,reason
            FROM operations_configuration_versions WHERE revision=1
        """),
            {"target": target, "ref": "a" * 64, "hash": "b" * 64},
        )
        connection.execute(
            text("UPDATE operations_configuration_state SET revision=2,current_id=:id"),
            {"id": target},
        )
    assert get(client, actors)["revision"] == 1
    # Raw JSON values are independently constrained, including unknown extra keys.
    for invalid in ['{"failed_imports":true}', '{"failed_imports":10001}', '{"unknown":1}']:
        with pytest.raises(DBAPIError), service.engine.begin() as connection:
            connection.execute(
                text("""
                INSERT INTO operations_configuration_versions
                  (id,revision,thresholds,version_ref,previous_ref,command_hash,changed_key,reason)
                SELECT :target,2,thresholds || CAST(:invalid AS jsonb),:ref,version_ref,:hash,
                  changed_key,reason
                FROM operations_configuration_versions WHERE revision=1
                """),
                {"target": uuid4(), "ref": "a" * 64, "hash": "b" * 64, "invalid": invalid},
            )


def test_configuration_sql_every_range_and_single_key_prior_reference(content):
    service, client, actors, _ = content
    assert patch(client, actors, get(client, actors)).status_code == 200
    statement = text("""
      INSERT INTO operations_configuration_versions
        (id,revision,thresholds,version_ref,previous_ref,command_hash,changed_key,reason)
      SELECT :id,2,thresholds || CAST(:override AS jsonb),:ref,
        COALESCE(:previous,version_ref),:hash,:key,reason
      FROM operations_configuration_versions WHERE revision=1
    """)
    for key, field in WarningValues.model_fields.items():
        lower = next(item.ge for item in field.metadata if hasattr(item, "ge"))
        upper = next(item.le for item in field.metadata if hasattr(item, "le"))
        for value in [lower - 1, lower, upper, upper + 1]:
            params = {
                "id": uuid4(),
                "override": json.dumps({key: value}),
                "key": key,
                "ref": "a" * 64,
                "hash": "b" * 64,
                "previous": None,
            }
            with service.engine.connect() as connection:
                try:
                    if value in [lower, upper]:
                        # Valid shape reaches the pending atomic-audit boundary. It is
                        # deliberately rolled back, never committed without its audit.
                        connection.execute(statement, params)
                    else:
                        with pytest.raises(DBAPIError):
                            connection.execute(statement, params)
                finally:
                    connection.rollback()
    for override, previous in [
        ({"failed_imports": 3, "unresolved_flags": 4}, None),
        ({"failed_imports": 3}, "0" * 64),
    ]:
        with service.engine.connect() as connection:
            try:
                with pytest.raises(DBAPIError):
                    connection.execute(
                        statement,
                        {
                            "id": uuid4(),
                            "override": json.dumps(override),
                            "key": "failed_imports",
                            "ref": "a" * 64,
                            "hash": "b" * 64,
                            "previous": previous,
                        },
                    )
            finally:
                connection.rollback()


def test_configuration_unavailable_is_explicit_and_payload_is_bounded(content, monkeypatch):
    service, client, actors, _ = content
    import services.operations as operations

    def broken(*args):
        raise ValueError("secret diagnostic canary")

    monkeypatch.setattr(operations, "current_configuration", broken)
    response = client.get("/api/v1/admin/operations", headers=actors["admin"])
    assert response.status_code == 200
    assert response.json()["configuration_state"] == "UNAVAILABLE_DEFAULTS_APPLIED"
    assert "OPERATIONS_CONFIGURATION_UNAVAILABLE" in {a["code"] for a in response.json()["alerts"]}
    assert "secret diagnostic" not in response.text
    # Streaming chunks cannot bypass the limit or persist a partial command.
    oversized = client.patch(
        PATH + "/failed_imports",
        headers=actors["admin"] | {"Idempotency-Key": str(uuid4())},
        content=iter([b"x" * 600, b"canary" * 100]),
    )
    assert oversized.status_code == 413 and "canary" not in oversized.text
    assert get(client, actors)["revision"] == 0
