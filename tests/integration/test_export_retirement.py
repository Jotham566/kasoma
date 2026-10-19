"""ADR-060 synthetic SQL retirement through a real EXECUTE-only database login."""

import secrets
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.data_request_contracts import DataRequestInput
from services.data_requests import DataRequestService
from services.database import engine_for
from services.domain.data_requests import DataRequest, DataRequestReceipt
from services.export_cleanup import sweep
from services.export_jobs import queue
from services.export_processing import process_one
from services.export_retirement_install import install_v1
from services.identity_contracts import OTPRequest, OTPVerify
from services.staff import provision
from tests.integration.test_export_jobs import SweepStore

pytestmark = pytest.mark.integration


def login(identity, email):
    challenge = identity.request_otp(
        OTPRequest(identifier=email, device_id=uuid4()), "fixture", None
    )
    return identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    ).access_token


def historical(
    content,
    expression="clock_timestamp()-interval '7 years'",
    *,
    pending=False,
    cleanup=True,
    legacy=False,
):
    identity, *_ = content
    with identity.engine.connect() as db:
        # Expressions are fixed test literals only, never application/caller cutoffs.
        at = db.scalar(text("SELECT " + expression))
    original = identity.clock
    identity.clock = lambda: at
    try:
        email = f"history-{uuid4()}@example.invalid"
        token = login(identity, email)
        service = DataRequestService(identity)
        key = uuid4()
        source = service.create(
            token, DataRequestInput(kind="EXPORT", affirmative=True), key, uuid4()
        ).id
        reviewer = f"review-{uuid4()}@example.invalid"
        admin = login(identity, reviewer)
        provision(identity, reviewer, "ADMIN")
        service.claim(admin, source, uuid4(), uuid4())
        if pending == "QUEUED":
            queue(identity, token, source, uuid4(), uuid4())
        if not pending:
            if legacy:
                from services.data_exports import download, expire

                download(identity, token, source, uuid4(), uuid4())
                if cleanup:
                    identity.clock = lambda: at + timedelta(days=2)
                    assert expire(identity, uuid4()) == 1
            else:
                queue(identity, token, source, uuid4(), uuid4())
                store = SweepStore(identity)
                assert process_one(identity, store)
                if cleanup:
                    identity.clock = lambda: at + timedelta(days=2)
                    assert sweep(identity, store).generations == 1
        with Session(identity.engine) as db:
            owner = db.get(DataRequest, source).user_id
        return source, owner, email, key
    finally:
        identity.clock = original


@pytest.fixture
def retirement(content):
    identity, *_ = content
    with identity.engine.begin() as db:
        schema = db.scalar(text("SELECT current_schema()"))
        assert schema.startswith("identity_test_")
        owner_role = install_v1(db)
    role = "kasoma_retire_test_" + uuid4().hex
    password = secrets.token_urlsafe(32)
    qs = identity.engine.dialect.identifier_preparer.quote_schema(schema)
    created, restricted = False, None
    try:
        try:
            with identity.engine.begin() as db:
                db.execute(
                    text("SELECT set_config('kasoma.test_role_password',:value,true)"),
                    {"value": password},
                )
                db.execute(
                    text(f"""DO $$ BEGIN
                  EXECUTE format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
                    NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD %L','{role}',
                    current_setting('kasoma.test_role_password'));
                END $$""")
                )
            created = True
            with identity.engine.begin() as db:
                db.execute(text(f"GRANT USAGE ON SCHEMA {qs} TO {role}"))
                db.execute(
                    text(
                        f"GRANT EXECUTE ON FUNCTION {qs}.retire_completed_export_evidence() "
                        f"TO {role}"
                    )
                )
                db.execute(text(f"ALTER ROLE {role} SET statement_timeout='2000ms'"))
                db.execute(text(f"ALTER ROLE {role} SET lock_timeout='100ms'"))
        except DBAPIError:
            raise RuntimeError(
                "Retirement LOGIN provisioning failed; diagnostics withheld"
            ) from None
        url = make_url(identity.settings.database_url.get_secret_value()).set(
            username=role, password=password
        )
        settings = identity.settings.model_copy(
            update={"database_url": SecretStr(url.render_as_string(hide_password=False))}
        )
        restricted = engine_for(settings)
        with restricted.connect() as db:
            assert db.scalar(text("SELECT current_user")) == role
        yield content, restricted, owner_role
    finally:
        if restricted is not None:
            restricted.dispose()
        if created:
            with identity.engine.begin() as db:
                db.execute(
                    text(
                        f"REVOKE EXECUTE ON FUNCTION {qs}.retire_completed_export_evidence() "
                        f"FROM {role}"
                    )
                )
                db.execute(text(f"REVOKE ALL ON SCHEMA {qs} FROM {role}"))
                db.execute(text(f"DROP ROLE {role}"))


def enable(identity):
    with identity.engine.begin() as db:
        db.execute(text("UPDATE export_retirement_state SET enabled=true"))


def batch(engine):
    with engine.begin() as db:
        return db.scalar(text("SELECT retire_completed_export_evidence()"))


def test_execute_only_login_default_off_and_independent_permissions(retirement):
    content, restricted, owner_role = retirement
    identity, *_ = content
    assert batch(restricted) == {"status": "DISABLED"}
    for sql in [
        "DELETE FROM data_request_receipts",
        "DELETE FROM data_subject_requests",
        "DELETE FROM data_request_reviews",
        "DELETE FROM personal_export_jobs",
        "SELECT * FROM data_subject_requests",
        "UPDATE export_retirement_state SET enabled=true",
        "SELECT export_retirement_allowed('DATA_REQUEST',gen_random_uuid())",
        "ALTER TABLE data_request_receipts DISABLE TRIGGER ALL",
        "CREATE TABLE unauthorized_retirement(id int)",
        f"SET ROLE {owner_role}",
    ]:
        with restricted.begin() as db, pytest.raises(DBAPIError) as rejected:
            db.execute(text(sql))
        assert rejected.value.orig.sqlstate == "42501"
    with restricted.begin() as db:
        db.execute(text("SET LOCAL kasoma.retirement_authorized='true'"))
        db.execute(text("SET LOCAL statement_timeout=0"))
        assert db.scalar(text("SELECT retire_completed_export_evidence()")) == {
            "status": "DISABLED"
        }
    with identity.engine.connect() as db:
        role = db.execute(
            text(
                "SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolinherit,"
                "rolreplication,rolbypassrls FROM pg_roles WHERE rolname=:role"
            ),
            {"role": owner_role},
        ).one()
        assert role == (False,) * 7


def test_due_completed_export_retires_only_allowlist_and_atomic_count_audit(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    source, owner, _, key = historical(content)
    with Session(identity.engine) as db:
        old_receipts = list(
            db.scalars(select(DataRequestReceipt.id).where(DataRequestReceipt.request_id == source))
        )
        assert len(old_receipts) == 3
    enable(identity)
    results = [batch(restricted) for _ in range(4)]
    assert all(r["status"] == "PROCESSED" for r in results)
    removed = {name: sum(r["removed"][name] for r in results) for name in results[0]["removed"]}
    assert removed == {
        "data_request_receipts": 3,
        "data_request_reviews": 1,
        "personal_export_jobs": 1,
        "data_subject_requests": 1,
    }
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
            )
            == 0
        )
        assert db.scalar(text("SELECT count(*) FROM users WHERE id=:id"), {"id": owner}) == 1
        audits = db.execute(
            text(
                "SELECT actor_id,target_id,request_id,reason FROM audit_log "
                "WHERE action='data_request.export_retirement_batch'"
            )
        ).all()
        assert len(audits) == 4
        for actor, target, correlation, reason in audits:
            assert actor is None and target == correlation
            assert str(source) not in reason and str(owner) not in reason and str(key) not in reason
            assert all(str(ref) not in reason for ref in old_receipts)
    assert sum(batch(restricted)["removed"].values()) == 0


@pytest.mark.parametrize("case", ["FUTURE", "PENDING", "LEAP", "DUE"])
def test_database_calendar_deadline_not_caller_clock_or_timezone(retirement, case):
    content, restricted, _ = retirement
    identity, *_ = content
    expression = {
        "FUTURE": "clock_timestamp()+interval '10 minutes'-interval '6 years'",
        "PENDING": "clock_timestamp()-interval '7 years'",
        "LEAP": "timestamptz '2020-02-29 12:00:00+00'",
        "DUE": "clock_timestamp()-interval '6 years'",
    }[case]
    source, *_ = historical(content, expression, pending=case == "PENDING")
    enable(identity)
    results = []
    for _ in range(4):
        with restricted.begin() as db:
            db.execute(text("SET LOCAL timezone='Pacific/Auckland'"))
            db.execute(text("SET LOCAL kasoma.retirement_cutoff='2099-01-01'"))
            results.append(db.scalar(text("SELECT retire_completed_export_evidence()")))
    with identity.engine.connect() as db:
        retained = db.scalar(
            text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
        )
    assert retained == (1 if case in {"FUTURE", "PENDING"} else 0)
    if retained:
        assert sum(sum(r["removed"].values()) for r in results) == 0


def case_for(content, email):
    from tests.integration.test_data_requests import claim, create

    identity, client, actors, _ = content
    headers = {"Authorization": "Bearer " + login(identity, email)}
    target = create(client, headers, "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    with identity.engine.connect() as db:
        observed = db.scalar(text("SELECT clock_timestamp()"))
    body = {
        "decision_reference": str(uuid4()),
        "reason": "LEGAL_OBLIGATION",
        "expires_at": (observed + timedelta(days=365)).isoformat(),
        "affirmative": True,
    }
    identity.settings.export_evidence_holds_enabled = True
    return target, body


@pytest.mark.parametrize(
    "kind", ["DATA_REQUEST_RECEIPT", "DATA_REQUEST_REVIEW", "EXPORT_JOB_RECEIPT", "DATA_REQUEST"]
)
def test_exact_holds_keep_only_named_leaf_and_structural_parent(retirement, kind):
    from tests.integration.test_legal_holds import hold, release

    content, restricted, _ = retirement
    identity, client, actors, _ = content
    source, _, email, _ = historical(content)
    case, body = case_for(content, email)
    record = source
    if kind == "DATA_REQUEST_RECEIPT":
        with Session(identity.engine) as db:
            record = db.scalar(
                select(DataRequestReceipt.id)
                .where(DataRequestReceipt.request_id == source)
                .order_by(DataRequestReceipt.id)
            )
    held = hold(
        client, actors["admin"], case, body | {"record_type": kind, "record_id": str(record)}
    )
    assert held.status_code == 201, held.text
    enable(identity)
    results = [batch(restricted) for _ in range(4)]
    totals = {name: sum(r["removed"][name] for r in results) for name in results[0]["removed"]}
    assert totals == {
        "data_request_receipts": 2 if kind == "DATA_REQUEST_RECEIPT" else 3,
        "data_request_reviews": 0 if kind == "DATA_REQUEST_REVIEW" else 1,
        "personal_export_jobs": 0 if kind == "EXPORT_JOB_RECEIPT" else 1,
        "data_subject_requests": 0,
    }
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
            )
            == 1
        )
    identity.settings.export_evidence_holds_enabled = False
    assert release(client, actors["admin"], case, held.json()["id"]).status_code == 200
    after = [batch(restricted) for _ in range(4)]
    assert sum(r["removed"]["data_subject_requests"] for r in after) == 1


@pytest.mark.parametrize("failure", ["ROLLBACK", "AUDIT"])
def test_source_removals_cursor_and_batch_audit_are_atomic(retirement, failure):
    content, restricted, _ = retirement
    identity, *_ = content
    source, *_ = historical(content)
    enable(identity)
    if failure == "AUDIT":
        with identity.engine.begin() as db:
            db.execute(
                text("""CREATE FUNCTION fail_retirement_audit() RETURNS trigger
              LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Synthetic audit failure'; END $$;
              CREATE TRIGGER fail_retirement_audit BEFORE INSERT ON audit_log FOR EACH ROW
              WHEN (NEW.action='data_request.export_retirement_batch')
              EXECUTE FUNCTION fail_retirement_audit();""")
            )
        with pytest.raises(DBAPIError, match="Synthetic audit failure"):
            batch(restricted)
    else:
        with restricted.connect() as db:
            transaction = db.begin()
            assert (
                db.scalar(text("SELECT retire_completed_export_evidence()"))["removed"][
                    "data_request_receipts"
                ]
                == 3
            )
            transaction.rollback()
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_request_receipts WHERE request_id=:id"),
                {"id": source},
            )
            == 3
        )
        assert db.scalar(text("SELECT phase FROM export_retirement_state")) == 1
        assert (
            db.scalar(
                text(
                    "SELECT count(*) FROM audit_log "
                    "WHERE action='data_request.export_retirement_batch'"
                )
            )
            == 0
        )


def test_restore_without_owner_or_acl_fails_closed_until_privileged_repair_and_opt_in(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    historical(content)
    enable(identity)
    with identity.engine.begin() as db:
        migrator = db.scalar(text("SELECT current_user"))
        quote = identity.engine.dialect.identifier_preparer.quote
        db.execute(
            text(f"ALTER FUNCTION retire_completed_export_evidence() OWNER TO {quote(migrator)}")
        )
        db.execute(text("GRANT EXECUTE ON FUNCTION retire_completed_export_evidence() TO PUBLIC"))
    with pytest.raises(DBAPIError, match="Retirement capability unavailable"):
        batch(restricted)
    with identity.engine.begin() as db:
        assert db.scalar(text("SELECT count(*) FROM data_request_receipts")) == 3
        install_v1(db)
    assert batch(restricted) == {"status": "DISABLED"}
    enable(identity)
    assert batch(restricted)["removed"]["data_request_receipts"] == 3


@pytest.mark.parametrize("case", ["COPY", "GENERATION", "MALFORMED", "MISSING", "INFINITE"])
def test_uncleared_copies_and_corrupt_deadlines_fail_closed(retirement, case):
    content, restricted, _ = retirement
    identity, *_ = content
    source, *_ = historical(
        content, cleanup=case not in {"COPY", "GENERATION"}, legacy=case == "COPY"
    )
    if case in {"MALFORMED", "MISSING", "INFINITE"}:
        value = {
            "MALFORMED": "retention_due_at-interval '1 day'",
            "MISSING": "NULL",
            "INFINITE": "'infinity'::timestamptz",
        }[case]
        with identity.engine.begin() as db:
            assert db.scalar(text("SELECT current_schema()")).startswith("identity_test_")
            # Explicit owned synthetic corruption fixture; restore the unchanged guard.
            db.execute(
                text("ALTER TABLE data_subject_requests DISABLE TRIGGER immutable_data_request")
            )
            db.execute(
                text(f"UPDATE data_subject_requests SET retention_due_at={value} WHERE id=:id"),
                {"id": source},
            )
            db.execute(
                text("ALTER TABLE data_subject_requests ENABLE TRIGGER immutable_data_request")
            )
    enable(identity)
    results = [batch(restricted) for _ in range(4)]
    assert sum(sum(r["removed"].values()) for r in results) == 0
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
            )
            == 1
        )


def test_large_held_prefix_cannot_starve_later_receipts_or_exceed_bounds(retirement):
    from services.domain.data_requests import LegalHold
    from tests.integration.test_legal_holds import hold

    content, restricted, _ = retirement
    identity, client, actors, _ = content
    source, owner, email, _ = historical(content)
    case, body = case_for(content, email)
    with identity.engine.begin() as db:
        for index in range(1, 321):
            db.execute(
                text("""INSERT INTO data_request_receipts(id,actor_id,key,request_hash,request_id)
              VALUES(:id,:actor,:key,:hash,:source)"""),
                {
                    "id": UUID(int=index),
                    "actor": owner,
                    "key": uuid4(),
                    "hash": "synthetic",
                    "source": source,
                },
            )
    first = hold(
        client,
        actors["admin"],
        case,
        body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": str(UUID(int=1))},
    )
    assert first.status_code == 201, first.text
    with Session(identity.engine) as db, db.begin():
        original = db.get(LegalHold, UUID(first.json()["id"]))
        values = {c.name: getattr(original, c.name) for c in LegalHold.__table__.columns}
        for index in range(2, 221):
            db.add(
                LegalHold(
                    **(
                        values
                        | {
                            "id": uuid4(),
                            "record_id": UUID(int=index),
                            "decision_reference": uuid4(),
                        }
                    )
                )
            )
    enable(identity)
    results = [batch(restricted) for _ in range(12)]
    assert results[0]["examined"] == results[0]["skipped"]["HELD"] == 200
    assert sum(results[0]["removed"].values()) == 0
    assert all(r["examined"] <= 200 and sum(r["removed"].values()) <= 100 for r in results)
    assert sum(r["removed"]["data_request_receipts"] for r in results) == 103
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_request_receipts WHERE request_id=:id"),
                {"id": source},
            )
            == 220
        )
        cursor = db.scalar(text("SELECT next_receipt FROM export_retirement_state"))
        if cursor:
            assert (
                db.scalar(
                    text("SELECT count(*) FROM data_request_receipts WHERE id=:id"), {"id": cursor}
                )
                == 1
            )


def test_retirement_wins_race_and_hold_never_acknowledges_missing_source(retirement):
    from concurrent.futures import ThreadPoolExecutor, TimeoutError
    from threading import Event

    from services.identity import IdentityError
    from services.legal_hold_contracts import HoldInput
    from services.legal_holds import LegalHoldService

    content, restricted, _ = retirement
    identity, _, actors, _ = content
    source, _, email, _ = historical(content)
    case, body = case_for(content, email)
    with Session(identity.engine) as db:
        record = db.scalar(
            select(DataRequestReceipt.id).where(DataRequestReceipt.request_id == source)
        )
    enable(identity)
    started = Event()

    def attempt():
        started.set()
        return LegalHoldService(identity).create(
            actors["admin"]["Authorization"][7:],
            UUID(case),
            HoldInput(**(body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": record})),
            uuid4(),
            uuid4(),
        )

    with restricted.connect() as db, ThreadPoolExecutor(max_workers=1) as pool:
        transaction = db.begin()
        try:
            assert (
                db.scalar(text("SELECT retire_completed_export_evidence()"))["removed"][
                    "data_request_receipts"
                ]
                == 3
            )
            future = pool.submit(attempt)
            assert started.wait(2)
            with pytest.raises(TimeoutError):
                future.result(timeout=0.1)
            transaction.commit()
            with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
                future.result(timeout=3)
        finally:
            if transaction.is_active:
                transaction.rollback()


def test_committed_hold_wins_race_and_batch_skips_its_locked_parent(retirement, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    from services.legal_hold_contracts import HoldInput
    from services.legal_holds import LegalHoldService

    content, restricted, _ = retirement
    identity, _, actors, _ = content
    source, _, email, _ = historical(content)
    case, body = case_for(content, email)
    with Session(identity.engine) as db:
        record = db.scalar(
            select(DataRequestReceipt.id).where(DataRequestReceipt.request_id == source)
        )
    locked, finish = Event(), Event()
    original = identity.event

    def pause(*args, **kwargs):
        if args[2] == "legal_hold.created":
            locked.set()
            assert finish.wait(5)
        return original(*args, **kwargs)

    monkeypatch.setattr(identity, "event", pause)
    enable(identity)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            LegalHoldService(identity).create,
            actors["admin"]["Authorization"][7:],
            UUID(case),
            HoldInput(**(body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": record})),
            uuid4(),
            uuid4(),
        )
        try:
            assert locked.wait(3)
            result = batch(restricted)
            assert result["skipped"]["BUSY"] >= 3 and sum(result["removed"].values()) == 0
        finally:
            finish.set()
        assert future.result(timeout=3).record_id == record
    # Rotate through the remaining phases and then revisit receipts with the hold committed.
    results = [batch(restricted) for _ in range(4)]
    assert sum(r["removed"]["data_request_receipts"] for r in results) == 2
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_request_receipts WHERE id=:id"), {"id": record}
            )
            == 1
        )


def test_execute_grant_cannot_be_replaced_by_public_or_session_settings(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    with restricted.connect() as db:
        role = db.scalar(text("SELECT current_user"))
    with identity.engine.begin() as db:
        db.execute(
            text(f"REVOKE EXECUTE ON FUNCTION retire_completed_export_evidence() FROM {role}")
        )
    with restricted.begin() as db, pytest.raises(DBAPIError) as rejected:
        db.execute(text("SET LOCAL kasoma.retirement_authorized='true'"))
        db.execute(text("SELECT retire_completed_export_evidence()"))
    assert rejected.value.orig.sqlstate == "42501"


def test_owner_role_security_drift_fails_closed(retirement):
    content, restricted, owner_role = retirement
    identity, *_ = content
    source, *_ = historical(content)
    enable(identity)
    try:
        with identity.engine.begin() as db:
            db.execute(text(f"ALTER ROLE {owner_role} LOGIN"))
        with pytest.raises(DBAPIError, match="Retirement capability unavailable"):
            batch(restricted)
        with identity.engine.connect() as db:
            assert (
                db.scalar(
                    text("SELECT count(*) FROM data_subject_requests WHERE id=:id"), {"id": source}
                )
                == 1
            )
    finally:
        with identity.engine.begin() as db:
            db.execute(text(f"ALTER ROLE {owner_role} NOLOGIN"))


@pytest.mark.parametrize("identity", ["0040"], indirect=True)
def test_populated_upgrade_keeps_exact_holds_and_does_not_enable_retirement(content):
    import os
    import subprocess

    from tests.integration.test_legal_holds import hold

    identity, client, actors, _ = content
    source, _, email, _ = historical(content)
    case, body = case_for(content, email)
    with Session(identity.engine) as db:
        record = db.scalar(
            select(DataRequestReceipt.id).where(DataRequestReceipt.request_id == source)
        )
    key = str(uuid4())
    body |= {"record_type": "DATA_REQUEST_RECEIPT", "record_id": str(record)}
    held = hold(client, actors["admin"], case, body, key)
    assert held.status_code == 201, held.text
    subprocess.run(
        ["make", "migrate"],
        check=True,
        capture_output=True,
        timeout=120,
        env=os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
    )
    assert hold(client, actors["admin"], case, body, key).json() == held.json()
    assert batch(identity.engine) == {"status": "DISABLED"}
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_request_receipts WHERE request_id=:id"),
                {"id": source},
            )
            == 3
        )


def test_nonapproved_isolated_scope_cannot_be_enabled_by_database_flag(content):
    import os
    import subprocess

    identity, *_ = content
    schema = "retirement_denied_" + uuid4().hex
    with identity.engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    url = make_url(identity.settings.database_url.get_secret_value()).update_query_dict(
        {"options": f"-csearch_path={schema},public"}
    )
    settings = identity.settings.model_copy(
        update={"database_url": SecretStr(url.render_as_string(hide_password=False))}
    )
    subprocess.run(
        ["make", "migrate"],
        check=True,
        capture_output=True,
        timeout=120,
        env=os.environ | {"DATABASE_URL": settings.database_url.get_secret_value()},
    )
    engine = engine_for(settings)
    try:
        with engine.begin() as db:
            db.execute(text("UPDATE export_retirement_state SET enabled=true"))
        with pytest.raises(DBAPIError, match="Retirement capability unavailable"):
            batch(engine)
        with engine.connect() as db:
            assert db.scalar(text("SELECT phase FROM export_retirement_state")) == 1
    finally:
        engine.dispose()


def test_session_timezone_cannot_make_malformed_calendar_deadline_valid(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    source, *_ = historical(content, "timestamptz '2018-03-11 02:30:00+00'")
    with identity.engine.begin() as db:
        db.execute(text("ALTER TABLE data_subject_requests DISABLE TRIGGER immutable_data_request"))
        db.execute(
            text(
                "UPDATE data_subject_requests "
                "SET retention_due_at=retention_due_at-interval '1 hour' WHERE id=:id"
            ),
            {"id": source},
        )
        db.execute(text("ALTER TABLE data_subject_requests ENABLE TRIGGER immutable_data_request"))
    enable(identity)
    for _ in range(4):
        with restricted.begin() as db:
            db.execute(text("SET LOCAL timezone='America/New_York'"))
            assert (
                sum(
                    db.scalar(text("SELECT retire_completed_export_evidence()"))["removed"].values()
                )
                == 0
            )


def test_lawful_receipt_retirement_allows_fresh_current_request_without_resurrection(retirement):
    from tests.integration.test_data_requests import create

    content, restricted, _ = retirement
    identity, client, _, _ = content
    source, _, email, key = historical(content)
    enable(identity)
    for _ in range(4):
        batch(restricted)
    headers = {"Authorization": "Bearer " + login(identity, email)}
    assert client.get(f"/api/v1/me/data-requests/{source}", headers=headers).status_code == 404
    new = create(client, headers, key=str(key))
    assert new.status_code == 201, new.text
    assert new.json()["id"] != str(source) and new.json()["status"] == "QUEUED"
    assert create(client, headers, key=str(key)).json() == new.json()


def test_stale_pending_job_grant_is_not_retirement_authority(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    source, *_ = historical(content, pending="QUEUED")
    enable(identity)
    assert sum(sum(batch(restricted)["removed"].values()) for _ in range(4)) == 0
    with identity.engine.connect() as db:
        assert db.execute(
            text(
                "SELECT status,grant_family IS NOT NULL FROM personal_export_jobs "
                "WHERE request_id=:id"
            ),
            {"id": source},
        ).one() == ("QUEUED", True)


def test_hold_expiry_uses_database_time_even_when_application_clock_advances(retirement):
    from time import monotonic, sleep

    from tests.integration.test_legal_holds import hold

    content, restricted, _ = retirement
    identity, client, actors, _ = content
    source, _, email, _ = historical(content)
    case, body = case_for(content, email)
    with Session(identity.engine) as db:
        record = db.scalar(
            select(DataRequestReceipt.id).where(DataRequestReceipt.request_id == source)
        )
        expires = db.scalar(text("SELECT clock_timestamp()+interval '3 seconds'"))
    held = hold(
        client,
        actors["admin"],
        case,
        body
        | {
            "record_type": "DATA_REQUEST_RECEIPT",
            "record_id": str(record),
            "expires_at": expires.isoformat(),
        },
    )
    assert held.status_code == 201, held.text
    enable(identity)
    original = identity.clock
    identity.clock = lambda: original() + timedelta(days=500)
    try:
        first = batch(restricted)
        assert first["skipped"]["HELD"] == 1 and first["removed"]["data_request_receipts"] == 2
        finish = monotonic() + 6
        while True:
            with identity.engine.connect() as db:
                remaining = (expires - db.scalar(text("SELECT clock_timestamp()"))).total_seconds()
            if remaining <= 0:
                break
            assert monotonic() < finish
            sleep(min(remaining, 0.05))
        after = [batch(restricted) for _ in range(8)]
        assert sum(r["removed"]["data_request_receipts"] for r in after) == 1
        assert sum(r["removed"]["data_subject_requests"] for r in after) == 1
    finally:
        identity.clock = original


def test_concurrent_batch_is_busy_without_waiting_or_partial_evidence(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    source, *_ = historical(content)
    enable(identity)
    with restricted.connect() as db:
        transaction = db.begin()
        try:
            assert (
                db.scalar(text("SELECT retire_completed_export_evidence()"))["removed"][
                    "data_request_receipts"
                ]
                == 3
            )
            assert batch(restricted) == {"status": "BUSY"}
        finally:
            transaction.rollback()
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_request_receipts WHERE request_id=:id"),
                {"id": source},
            )
            == 3
        )
        assert db.scalar(text("SELECT phase FROM export_retirement_state")) == 1


def test_database_lock_timeout_rolls_back_batch_without_erasure(retirement):
    content, restricted, _ = retirement
    identity, *_ = content
    source, *_ = historical(content)
    enable(identity)
    with identity.engine.connect() as blocker:
        transaction = blocker.begin()
        try:
            blocker.execute(text("LOCK TABLE data_subject_requests IN ACCESS EXCLUSIVE MODE"))
            with pytest.raises(DBAPIError) as rejected:
                batch(restricted)
            assert rejected.value.orig.sqlstate == "55P03"
        finally:
            transaction.rollback()
    with identity.engine.connect() as db:
        assert (
            db.scalar(
                text("SELECT count(*) FROM data_request_receipts WHERE request_id=:id"),
                {"id": source},
            )
            == 3
        )
        assert db.scalar(text("SELECT phase FROM export_retirement_state")) == 1
