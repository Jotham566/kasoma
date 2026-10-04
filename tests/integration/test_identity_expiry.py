"""Ephemeral expiry is bounded, atomic, concurrent-safe and payload-free."""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from uuid import uuid4

import pytest
from sqlalchemy import event as sqlalchemy_event
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.worker.main import make_worker
from services.domain.identity import AuthSession, Challenge, Consent, RateBucket, User
from services.identity_expiry import expire_identity
from tests.integration.test_identity import consent, login, profile

pytestmark = pytest.mark.integration
CANARY = "expiry-canary@example.invalid"


def seed_expired(service, count):
    at = service.clock()
    challenge_ids, bucket_keys = [], []
    with Session(service.engine) as db, db.begin():
        for _ in range(count):
            identifier = uuid4()
            key = service.digest("rate", str(identifier))
            challenge_ids.append(identifier)
            bucket_keys.append(key)
            db.add(
                Challenge(
                    id=identifier,
                    purpose="LOGIN",
                    user_id=None,
                    policy_version=service.settings.consent_policy_version,
                    type="EMAIL",
                    lookup_hash=service.digest("identifier", CANARY),
                    encrypted_identifier=service.encrypt(CANARY),
                    code_hash="synthetic-expired",
                    attempts=0,
                    expires_at=at,
                    consumed_at=None,
                )
            )
            db.add(RateBucket(key=key, count=5, expires_at=at))
    return challenge_ids, bucket_keys


def test_identity_expiry_batches_boundary_and_account_evidence(identity, caplog):
    service, client, messages, _ = identity
    headers, _ = login(client)
    profile(client, headers, "2000-01-01")
    assert consent(client, headers, "SELF").status_code == 200
    challenges, buckets = seed_expired(service, 210)
    with Session(service.engine) as db:
        before = {
            model: db.scalar(select(func.count()).select_from(model))
            for model in (User, AuthSession, Consent)
        }
    for expected in [100, 100, 10, 0]:
        assert expire_identity(service, uuid4()) == {
            "challenges": expected,
            "rate_buckets": expected,
        }
    with Session(service.engine) as db:
        for model, count in before.items():
            assert db.scalar(select(func.count()).select_from(model)) == count
        assert db.scalar(select(func.count()).select_from(Challenge)) == 1  # live consumed login
        assert db.scalar(select(func.count()).select_from(RateBucket)) == 4  # live send controls
        assert not db.scalar(select(Challenge.id).where(Challenge.id.in_(challenges)))
        assert not db.scalar(select(RateBucket.key).where(RateBucket.key.in_(buckets)))
    assert client.get("/api/v1/me", headers=headers).status_code == 200
    assert len(messages.messages) == 1
    events = [
        json.loads(r.message) for r in caplog.records if '"identity.ephemeral_expiry"' in r.message
    ]
    assert len(events) == 4
    for event in events:
        assert set(event) == {
            "event",
            "correlation_id",
            "status",
            "challenges",
            "rate_buckets",
            "schema_version",
        }
        assert event["status"] == "SUCCEEDED"
        assert 0 <= event["challenges"] <= 100 and 0 <= event["rate_buckets"] <= 100
    assert CANARY not in caplog.text


def test_identity_expiry_skips_locked_rows_and_preserves_refreshed_rate(identity):
    service, _, _, _ = identity
    challenges, buckets = seed_expired(service, 1)
    with Session(service.engine) as db, db.begin():
        challenge = db.scalar(
            select(Challenge).where(Challenge.id == challenges[0]).with_for_update()
        )
        bucket = db.scalar(select(RateBucket).where(RateBucket.key == buckets[0]).with_for_update())
        with ThreadPoolExecutor(max_workers=1) as pool:
            counts = pool.submit(expire_identity, service, uuid4()).result(timeout=5)
        assert counts == {"challenges": 0, "rate_buckets": 0}
        bucket.expires_at = service.clock() + timedelta(seconds=60)
        bucket.count = 4
        assert challenge.expires_at == service.clock()
    assert expire_identity(service, uuid4()) == {"challenges": 1, "rate_buckets": 0}
    with Session(service.engine) as db:
        assert db.get(RateBucket, buckets[0]).count == 4


def test_rate_refresh_locks_before_loading_an_expired_bucket(identity):
    service, _, _, _ = identity
    challenges, buckets = seed_expired(service, 1)
    loaded, resume = Event(), Event()

    def pause_after_load(connection, cursor, statement, parameters, context, many):
        if "WHERE identity_rate_buckets.key =" in statement:
            loaded.set()
            assert resume.wait(timeout=5), "Synthetic rate refresh barrier timed out"

    def refresh():
        with Session(service.engine) as db, db.begin():
            return service.rate(db, str(challenges[0]), 5, 60)

    sqlalchemy_event.listen(service.engine, "after_cursor_execute", pause_after_load)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(refresh)
            try:
                assert loaded.wait(timeout=5), "Synthetic rate refresh did not load"
                assert expire_identity(service, uuid4()) == {"challenges": 1, "rate_buckets": 0}
            finally:
                resume.set()
            assert pending.result(timeout=5)
    finally:
        resume.set()
        sqlalchemy_event.remove(service.engine, "after_cursor_execute", pause_after_load)
    with Session(service.engine) as db:
        bucket = db.get(RateBucket, buckets[0])
        assert bucket.count == 1 and bucket.expires_at > service.clock()


def test_identity_expiry_concurrent_jobs_and_safe_worker(identity, monkeypatch):
    service, _, _, _ = identity
    seed_expired(service, 200)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: expire_identity(service, uuid4()), range(2)))
    assert sum(r["challenges"] for r in results) == 200
    assert sum(r["rate_buckets"] for r in results) == 200
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Challenge)) == 0
        assert db.scalar(select(func.count()).select_from(RateBucket)) == 0
    monkeypatch.setattr("apps.worker.main.IdentityService", lambda *args: service)
    worker = make_worker(service.settings)
    try:
        assert worker.tasks["kasoma.expire_identity"].run() == {"challenges": 0, "rate_buckets": 0}
    finally:
        worker.close()


def test_identity_expiry_rolls_back_and_redacts_database_failure(identity, monkeypatch, caplog):
    service, _, _, _ = identity
    seed_expired(service, 1)
    original = Session.delete

    def fail(db, row):
        if isinstance(row, RateBucket):
            raise RuntimeError(CANARY)
        return original(db, row)

    monkeypatch.setattr(Session, "delete", fail)
    with pytest.raises(RuntimeError, match="diagnostics withheld") as failed:
        expire_identity(service, uuid4())
    assert failed.value.__suppress_context__
    assert CANARY not in caplog.text
    event = json.loads(
        next(r.message for r in caplog.records if '"identity.ephemeral_expiry"' in r.message)
    )
    assert event["status"] == "FAILED" and event["challenges"] == event["rate_buckets"] == 0
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Challenge)) == 1
        assert db.scalar(select(func.count()).select_from(RateBucket)) == 1
