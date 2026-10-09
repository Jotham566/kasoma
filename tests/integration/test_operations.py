"""FR-OPS-002: operator authorization, real queue truth and heartbeat expiry."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr
from redis import Redis
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from apps.worker.main import make_worker
from services.content_imports import process_one
from services.health import Health
from services.operations import bounded_count, export_counts, heartbeat, heartbeat_key, snapshot
from services.staff import provision
from tests.integration.test_content_imports import enqueue
from tests.integration.test_flags import assessment as assessment_fixture
from tests.integration.test_flags import report, saved, triage

assessment = assessment_fixture

pytestmark = pytest.mark.integration


def test_export_operations_follow_durable_queue_failure_and_age_without_identifiers(
    content, monkeypatch
):
    from uuid import UUID, uuid4

    from services.export_jobs import claim_next, fail_claim, queue
    from tests.integration.test_data_requests import create

    service, client, actors, _ = content
    now = [service.clock()]
    service.clock = lambda: now[0]
    monkeypatch.setattr(
        "services.operations.dependency_health",
        lambda _: Health(status="ok", database="up", redis="up"),
    )
    target = UUID(create(client, actors["learner"]).json()["id"])
    queue(service, actors["learner"]["Authorization"][7:], target, uuid4(), uuid4())

    def current():
        response = client.get("/api/v1/admin/operations", headers=actors["admin"])
        assert response.status_code == 200
        result = response.json()
        for forbidden in [str(target), "grant_family", "encrypted_manifest", "generation_id", "@"]:
            assert forbidden not in response.text
        return result["counts"]["exports"], {
            a["code"] for a in result["alerts"] if a["code"].startswith("EXPORT_")
        }

    first, alerts = current()
    assert first == {
        "queued": {"value": 1, "at_least": False},
        "running": {"value": 0, "at_least": False},
        "failed_finished_24h": {"value": 0, "at_least": False},
        "oldest_pending_seconds": 0,
    }
    assert not alerts
    now[0] += timedelta(seconds=300)
    assert current()[1] == {"EXPORT_STALLED"}
    claim = claim_next(service)
    running, alerts = current()
    assert running["queued"]["value"] == 0 and running["running"]["value"] == 1
    assert alerts == {"EXPORT_STALLED"}
    fail_claim(service, claim, "LIMIT_REACHED")
    failed, alerts = current()
    assert failed["oldest_pending_seconds"] == 0
    assert failed["running"]["value"] == 0 and failed["failed_finished_24h"]["value"] == 1
    assert alerts == {"EXPORT_FAILED"}
    with Session(service.engine) as db:
        assert export_counts(db, now[0] + timedelta(hours=24)).failed_finished_24h.value == 1
        assert (
            export_counts(db, now[0] + timedelta(hours=24, seconds=1)).failed_finished_24h.value
            == 0
        )
        assert export_counts(db, now[0] - timedelta(seconds=1)).failed_finished_24h.value == 0

    queue(service, actors["learner"]["Authorization"][7:], target, uuid4(), uuid4())
    retried, alerts = current()
    assert retried["queued"]["value"] == 1 and retried["failed_finished_24h"]["value"] == 0
    assert retried["oldest_pending_seconds"] == 0 and not alerts


def test_operations_authorization_and_failed_stalled_queue(content, identity, monkeypatch):
    service, client, actors, body = content
    monkeypatch.setattr(
        "services.operations.dependency_health",
        lambda _: Health(status="ok", database="up", redis="up"),
    )
    path = "/api/v1/admin/operations"
    assert client.get(path).status_code == 401
    for role in ["author", "reviewer", "learner", "support"]:
        assert client.get(path, headers=actors[role]).status_code == 403
    enqueue(client, actors, body)
    provision(service, "author@example.invalid", "CONTENT_AUTHOR", revoke=True)
    assert process_one(service)
    provision(service, "author@example.invalid", "CONTENT_AUTHOR")
    enqueue(client, actors, body)
    identity[3][0] += timedelta(seconds=300)
    response = client.get(path, headers=actors["admin"])
    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store" and response.headers["request_id"]
    view = response.json()
    assert view["counts"]["failed_imports_24h"]["value"] == 1
    assert view["counts"]["queued_imports"]["value"] == 1
    assert view["counts"]["oldest_import_seconds"] == 300
    assert {a["code"] for a in view["alerts"]} == {
        "IMPORT_FAILED",
        "IMPORT_STALLED",
        "WORKER_HEARTBEAT_MISSING",
    }
    for forbidden in [
        "@",
        "Synthetic selector fixture",
        "actor_id",
        "version_id",
        "source_locator",
    ]:
        assert forbidden not in response.text
    assert process_one(service)
    assert "IMPORT_STALLED" not in {a.code for a in snapshot(service).alerts}
    provision(service, "admin@example.invalid", "ADMIN", revoke=True)
    assert client.get(path, headers=actors["admin"]).status_code == 403


def test_operations_rate_and_query_failure_are_safe(content, monkeypatch):
    service, client, actors, _ = content
    monkeypatch.setattr(
        "services.operations.dependency_health",
        lambda _: Health(status="ok", database="up", redis="up"),
    )

    def broken(*args):
        raise RuntimeError("secret database diagnostic")

    monkeypatch.setattr("services.operations.counts", broken)
    for _ in range(20):
        result = client.get("/api/v1/admin/operations", headers=actors["admin"])
        assert result.status_code == 200
        assert result.json()["counts"] is None
        assert result.json()["health"]["database"] == "down"
        assert "secret" not in result.text
    assert client.get("/api/v1/admin/operations", headers=actors["admin"]).status_code == 429


def test_operations_heartbeat_expiry_and_real_worker_task(identity):
    service, _, _, now = identity
    assert heartbeat(service) == "unavailable"
    original_settings = service.settings
    key = heartbeat_key(service)
    alias = make_url(service.settings.database_url.get_secret_value()).set(
        host="postgres", port=5432
    )
    service.settings = service.settings.model_copy(
        update={"database_url": SecretStr(alias.render_as_string(hide_password=False))}
    )
    assert heartbeat_key(service) == key
    service.settings = original_settings
    assert heartbeat(service, write=True) == "up"
    assert heartbeat(service) == "up"
    with Redis.from_url(service.settings.redis_url.get_secret_value()) as cache:
        assert 0 < cache.ttl(heartbeat_key(service)) <= 180
    now[0] += timedelta(seconds=180)
    assert heartbeat(service) == "unavailable"
    with Redis.from_url(service.settings.redis_url.get_secret_value()) as cache:
        cache.set(heartbeat_key(service), "malformed", ex=180)
    assert heartbeat(service) == "unavailable"
    service.clock = lambda: datetime.now(UTC)
    worker = make_worker(service.settings)
    assert worker.tasks["kasoma.monitor_operations"].run() == 0
    assert heartbeat(service) == "up"
    with Session(service.engine) as db:
        small = bounded_count(db, select(1).select_from(func.generate_series(1, 2)))
        large = bounded_count(db, select(1).select_from(func.generate_series(1, 10001)))
        assert small.value == 2 and not small.at_least
        assert large.value == 10000 and large.at_least


def test_operations_flag_counts_exclude_resolved_without_disclosing_reports(
    assessment, monkeypatch
):
    service, client, actors, *_ = assessment
    monkeypatch.setattr(
        "services.operations.dependency_health",
        lambda _: Health(status="ok", database="up", redis="up"),
    )
    grade = saved(assessment)
    response = report(
        client,
        actors["learner"],
        grade["attempt_id"],
        {"category": "UNSAFE_CONTENT", "comment": "Synthetic confidential report"},
    )
    assert response.status_code == 201, response.text
    view = snapshot(service)
    assert view.counts.unresolved_flags.value == 1
    assert view.counts.high_priority_flags.value == 1
    assert "HIGH_PRIORITY_FLAGS" in {a.code for a in view.alerts}
    assert "confidential" not in view.model_dump_json()
    flag = client.get(
        "/api/v1/admin/content-flags/" + response.json()["id"], headers=actors["reviewer"]
    ).json()
    resolved = triage(
        client,
        actors["reviewer"],
        flag,
        status="RESOLVED",
        resolution="Synthetic report independently checked",
    )
    assert resolved.status_code == 200, resolved.text
    view = snapshot(service)
    assert view.counts.unresolved_flags.value == 0 and view.counts.high_priority_flags.value == 0
