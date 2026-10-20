"""FR-ID-006: SQL-visible serialization without an erasure execution capability."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from time import monotonic
from uuid import uuid4

import pytest
from sqlalchemy import event, text
from sqlalchemy.orm import Session

from services.domain.identity import User
from services.identity import IdentityError
from services.identity_contracts import OTPRequest, OTPVerify

pytestmark = pytest.mark.integration

EXCLUSIVE = text("""
  SELECT pg_try_advisory_xact_lock(hashtextextended(
    'kasoma.account-processing.v1:' ||
    pg_catalog.to_regnamespace(current_schema())::oid::text || ':' || CAST(:subject AS text),0)
    | (-9223372036854775808)::bigint)
""")


def active_gate_count(engine, subject):
    with engine.connect() as db:
        return db.scalar(
            text("""
          WITH key AS (SELECT hashtextextended(
            'kasoma.account-processing.v1:' ||
    pg_catalog.to_regnamespace(current_schema())::oid::text || ':' || CAST(:subject AS text),0)
            | (-9223372036854775808)::bigint AS value)
          SELECT count(*) FROM pg_catalog.pg_locks l CROSS JOIN key
          WHERE l.locktype='advisory' AND l.granted AND l.objsubid=1
            AND l.database=(SELECT oid FROM pg_catalog.pg_database
                            WHERE datname=current_database())
            AND l.classid=((key.value>>32)&4294967295)::oid
            AND l.objid=(key.value&4294967295)::oid
        """),
            {"subject": subject},
        )


def wait_for_gate(engine, pid, future):
    deadline = monotonic() + 1.5
    tick = Event()
    while monotonic() < deadline:
        if future.done():
            raise AssertionError("Operation bypassed the SQL processing gate")
        with engine.connect() as db:
            waiting = db.scalar(
                text("""
              SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_locks
                WHERE pid=:pid AND locktype='advisory' AND NOT granted
                  AND mode='ShareLock')
            """),
                {"pid": pid},
            )
        if waiting:
            return
        tick.wait(0.01)
    raise AssertionError("Operation did not wait at the SQL processing gate")


@pytest.mark.parametrize("operation", ["ACCESS", "REFRESH", "LOGIN"])
def test_identity_waits_for_sql_gate_and_rechecks_disabled(identity, monkeypatch, operation):
    service, *_ = identity
    challenge = service.request_otp(
        OTPRequest(identifier="processing-gate@example.invalid", device_id=uuid4()), "test", None
    )
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    subject = service.me(credentials.access_token).id
    if operation == "LOGIN":
        instant = service.clock()
        service.clock = lambda: instant + timedelta(seconds=61)
        challenge = service.request_otp(
            OTPRequest(identifier="processing-gate@example.invalid", device_id=uuid4()),
            "test",
            None,
        )
    reached = Event()
    backend = []
    original = service.lock

    def observe(db, key):
        original(db, key)
        if key == str(subject):
            backend.append(db.scalar(text("SELECT pg_backend_pid()")))
            reached.set()

    monkeypatch.setattr(service, "lock", observe)

    def perform():
        if operation == "ACCESS":
            service.me(credentials.access_token)
        elif operation == "REFRESH":
            service.refresh(credentials.refresh_token)
        else:
            service.verify(
                OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
            )

    with ThreadPoolExecutor(max_workers=1) as pool:
        with Session(service.engine) as db, db.begin():
            assert db.scalar(EXCLUSIVE, {"subject": subject}) is True
            future = pool.submit(perform)
            assert reached.wait(5), "Operation did not reach account serialization"
            wait_for_gate(service.engine, backend[0], future)
            # Simulate the future closure transaction's ACTIVE->DISABLED effect only.
            # 0045 deliberately refuses setting closed_at or creating an erasure job.
            db.get(User, subject).status = "DISABLED"
        with pytest.raises(IdentityError, match="AUTH_REQUIRED"):
            future.result(timeout=5)


def test_gate_namespace_is_disjoint_from_hmac_and_blocks_only_its_subject(identity):
    from services.account_processing import coordinate

    service, *_ = identity
    subject, other = uuid4(), uuid4()
    with Session(service.engine) as db, db.begin():
        coordinate(db, subject)
        with service.engine.connect() as observer:
            assert observer.scalar(EXCLUSIVE, {"subject": subject}) is False
            assert observer.scalar(EXCLUSIVE, {"subject": other}) is True
            assert (
                observer.scalar(
                    text("""
              SELECT (hashtextextended('kasoma.account-processing.v1:' ||
    pg_catalog.to_regnamespace(current_schema())::oid::text || ':' || CAST(:subject AS text),0)
                | (-9223372036854775808)::bigint)<0
            """),
                    {"subject": subject},
                )
                is True
            )
    with service.engine.connect() as db:
        assert db.scalar(EXCLUSIVE, {"subject": subject}) is True


def test_failed_session_unlock_discards_real_connection_and_releases_owned_gate(identity):
    from services.account_processing import dispatch_gate

    service, *_ = identity
    subject = uuid4()

    def fail_unlock(conn, cursor, statement, parameters, context, executemany):
        if "pg_advisory_unlock_shared" in statement:
            raise RuntimeError("Synthetic unlock failure")

    event.listen(service.engine, "before_cursor_execute", fail_unlock)
    try:
        with pytest.raises(RuntimeError, match="Synthetic unlock failure"):
            with dispatch_gate(service.engine, subject):
                assert active_gate_count(service.engine, subject) == 1
    finally:
        event.remove(service.engine, "before_cursor_execute", fail_unlock)
    deadline = monotonic() + 1.5
    tick = Event()
    while active_gate_count(service.engine, subject) != 0 and monotonic() < deadline:
        tick.wait(0.01)
    assert active_gate_count(service.engine, subject) == 0
    with service.engine.connect() as db:
        assert db.scalar(EXCLUSIVE, {"subject": subject}) is True


def test_gate_does_not_block_same_uuid_in_another_owned_schema(identity):
    from services.account_processing import coordinate

    service, *_ = identity
    subject = uuid4()
    other_schema = "identity_test_" + uuid4().hex
    with service.engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{other_schema}"'))
    with Session(service.engine) as db, db.begin():
        coordinate(db, subject)
        with service.engine.begin() as observer:
            observer.execute(text(f'SET LOCAL search_path="{other_schema}",pg_catalog'))
            assert observer.scalar(EXCLUSIVE, {"subject": subject}) is True


def test_cached_principal_is_refreshed_after_processing_barrier(identity):
    service, *_ = identity
    challenge = service.request_otp(
        OTPRequest(identifier="cached-principal@example.invalid", device_id=uuid4()), "test", None
    )
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    subject = service.me(credentials.access_token).id
    with Session(service.engine) as db, db.begin():
        cached = db.get(User, subject)
        assert cached.status == "ACTIVE"
        with service.engine.begin() as writer:
            assert writer.scalar(EXCLUSIVE, {"subject": subject}) is True
            writer.execute(
                text("UPDATE users SET status='DISABLED' WHERE id=:subject"), {"subject": subject}
            )
        with pytest.raises(IdentityError, match="AUTH_REQUIRED"):
            service.authenticate(db, credentials.access_token)
        assert cached.status == "DISABLED"
