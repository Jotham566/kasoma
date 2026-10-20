"""ADR-072 real private-principal plan issuance; no closure or deletion execution."""

from contextlib import contextmanager
from datetime import timedelta
from uuid import uuid4

import pytest
from psycopg import sql
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.erasure_capability import CapabilityInstallUnavailable, install
from services.data_request_contracts import DataRequestInput
from services.data_requests import DataRequestService
from services.database import engine_for
from services.domain.identity import IdentityEvent
from services.erasure_contracts import ErasurePlan
from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.providers import FakeMessagingProvider
from services.staff import provision
from tests.integration.test_erasure_capability import source

pytestmark = pytest.mark.integration


@contextmanager
def planned_source(*, lifetime=600):
    with source() as proof:
        try:
            capability = install(proof, plan_ttl_seconds=lifetime)
        except CapabilityInstallUnavailable as rejected:
            import sys

            # Closed installation phase only; never a statement, key or connection URL.
            print("Synthetic private installation failed at " + rejected.phase, file=sys.stderr)
            raise
        admin = engine_for(proof.settings)

        def now():
            with admin.connect() as db:
                return db.scalar(text("SELECT clock_timestamp()"))

        fake = FakeMessagingProvider()
        identity = IdentityService(admin, proof.settings, fake, fake, now, lambda: "246810")
        authorizer = engine_for(
            proof.settings.model_copy(update={"database_url": capability.authorizer_url})
        )
        executor = engine_for(
            proof.settings.model_copy(update={"database_url": capability.executor_url})
        )
        try:
            yield proof, capability, identity, authorizer, executor
        finally:
            authorizer.dispose()
            executor.dispose()
            admin.dispose()


def actor(identity, label, role=None):
    email = label + "@example.invalid"
    challenge = identity.request_otp(OTPRequest(identifier=email, device_id=uuid4()), label, None)
    tokens = identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    if role:
        provision(identity, email, role)
    with Session(identity.engine) as db:
        auth = identity.authenticate(db, tokens.access_token, recent=True)
        return tokens.access_token, auth.id, auth.user_id


def reviewed_case(identity, label="primary"):
    learner = actor(identity, label + "-learner")
    admin = actor(identity, label + "-admin", "ADMIN")
    requests = DataRequestService(identity)
    case = requests.create(
        learner[0], DataRequestInput(kind="DELETE", affirmative=True), uuid4(), uuid4()
    )
    requests.claim(admin[0], case.id, uuid4(), uuid4())
    return learner, admin, case.id


def issue(proof, capability, engine, session, case, *, nonce=None):
    with proof_engine(proof) as binding:
        original_nonce = binding.scalar(
            text("SELECT scope_nonce FROM public.account_erasure_state")
        )
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as db:
        with db.begin():
            db.execute(text("SET LOCAL statement_timeout='5000ms'"))
            statement = sql.SQL(
                "SELECT {}.issue_plan(:session,:case,CAST(:database AS oid),"
                "CAST(:namespace AS oid),:nonce,:correlation)"
            ).format(sql.Identifier(capability.namespace))
            try:
                return ErasurePlan.model_validate(
                    db.scalar(
                        text(statement.as_string()),
                        {
                            "session": session,
                            "case": case,
                            "database": proof.database_oid,
                            "namespace": proof.namespace_oid,
                            "nonce": nonce or original_nonce,
                            "correlation": uuid4(),
                        },
                    )
                )
            except DBAPIError as error:
                import json
                import sys

                codes = {
                    "42501": "AUTHORITY",
                    "42883": "FUNCTION",
                    "42703": "COLUMN",
                    "42P01": "RELATION",
                    "22P02": "FORMAT",
                    "57014": "BUDGET",
                }
                known = {
                    "Erasure plan unavailable",
                    "Erasure plan snapshot required",
                    "Erasure authority unavailable",
                    "Erasure case unavailable",
                    "Erasure source busy",
                    "Erasure source unavailable",
                }
                primary = getattr(getattr(error.orig, "diag", None), "message_primary", None)
                reason = primary if primary in known else "SQL_OPERATION_FAILED"
                print(
                    json.dumps(
                        {
                            "event": "synthetic.erasure_plan.failed",
                            "kind": codes.get(error.orig.sqlstate, "SQL_OPERATION_FAILED"),
                            "reason": reason,
                        }
                    ),
                    file=sys.stderr,
                )
                raise


@contextmanager
def proof_engine(proof):
    engine = engine_for(proof.settings)
    try:
        with engine.connect() as db:
            yield db
    finally:
        engine.dispose()


def recompute(proof, capability, subject, plan):
    with proof_engine(proof) as db, db.begin():
        owner = db.scalar(
            text("SELECT rolname FROM pg_catalog.pg_roles WHERE oid=:owner"),
            {"owner": capability.owner_oid},
        )
        db.execute(text(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(owner)).as_string()))
        db.execute(text("SET LOCAL statement_timeout='5000ms'"))
        statement = sql.SQL("SELECT {}.source_version(:subject,:plan)").format(
            sql.Identifier(capability.namespace)
        )
        return db.scalar(text(statement.as_string()), {"subject": subject, "plan": plan})


def test_plan_is_current_claimant_only_database_clock_sealed_and_uncapped():
    with planned_source() as (proof, capability, identity, authorizer, executor):
        learner, admin, case = reviewed_case(identity)
        first = issue(proof, capability, authorizer, admin[1], case)
        assert first.request_id == case and first.expires_at - first.observed_at == timedelta(
            minutes=10
        )
        assert first.authorization_available is False
        assert first.blockers == ["EXECUTION_DISABLED", "VERIFICATION_INCOMPLETE"]
        assert recompute(proof, capability, learner[2], first.plan_id) == first.version
        actor(identity, "unrelated")
        assert recompute(proof, capability, learner[2], first.plan_id) == first.version
        with Session(identity.engine) as db, db.begin():
            db.add_all(
                [
                    IdentityEvent(
                        id=uuid4(),
                        user_id=learner[2],
                        type="registration.completed",
                        version=1,
                        payload={"request_id": str(uuid4())},
                        created_at=identity.clock(),
                    )
                    for _ in range(10_001)
                ]
            )
        assert recompute(proof, capability, learner[2], first.plan_id) != first.version
        second = issue(proof, capability, authorizer, admin[1], case)
        assert second.version != first.version
        assert recompute(proof, capability, learner[2], second.plan_id) == second.version
        with proof_engine(proof) as db:
            assert (
                db.scalar(
                    text("SELECT count(*) FROM identity_outbox_events WHERE user_id=:subject"),
                    {"subject": learner[2]},
                )
                >= 10_001
            )
            assert db.scalar(text("SELECT count(*) FROM public.account_erasure_jobs")) == 0
            assert (
                db.scalar(text("SELECT count(*) FROM public.users WHERE closed_at IS NOT NULL"))
                == 0
            )
        with pytest.raises(DBAPIError):
            issue(proof, capability, executor, admin[1], case)


@pytest.mark.parametrize(
    "bad",
    [
        "learner",
        "other_admin",
        "revoked",
        "rotated",
        "expired",
        "future",
        "role_revoked",
        "wrong_nonce",
        "wrong_case",
    ],
)
def test_sql_rechecks_current_authority_case_and_source(bad):
    with planned_source() as (proof, capability, identity, authorizer, executor):
        learner, admin, case = reviewed_case(identity)
        other = actor(identity, "other-admin", "ADMIN")
        session = learner[1] if bad == "learner" else other[1] if bad == "other_admin" else admin[1]
        if bad in {"revoked", "rotated", "expired", "future"}:
            changes = {
                "revoked": "revoked_at=clock_timestamp()",
                "rotated": "rotated_at=clock_timestamp()",
                "expired": "access_expires_at=clock_timestamp()",
                "future": "authenticated_at=clock_timestamp()+interval '1 day'",
            }
            with identity.engine.begin() as db:
                db.execute(
                    text("UPDATE public.auth_sessions SET " + changes[bad] + " WHERE id=:id"),
                    {"id": session},
                )
        if bad == "role_revoked":
            provision(identity, "primary-admin@example.invalid", "ADMIN", revoke=True)
        with pytest.raises(DBAPIError) as rejected:
            issue(
                proof,
                capability,
                authorizer,
                session,
                uuid4() if bad == "wrong_case" else case,
                nonce=uuid4() if bad == "wrong_nonce" else None,
            )
        assert rejected.value.orig.sqlstate == "42501"
        with proof_engine(proof) as db:
            assert db.scalar(text("SELECT count(*) FROM public.account_erasure_plans")) == 0


def test_bounded_expiry_uses_actual_database_time_and_keeps_unexpired_plans():
    import time

    with planned_source(lifetime=1) as (proof, capability, identity, authorizer, executor):
        for i in range(11):
            _, admin, case = reviewed_case(identity, "expiry" + str(i))
            for _ in range(10):
                issue(proof, capability, authorizer, admin[1], case)
        deadline = time.monotonic() + 5
        with identity.engine.connect() as db:
            while not db.scalar(
                text(
                    "SELECT bool_and(expires_at<=clock_timestamp()) "
                    "FROM public.account_erasure_plans"
                )
            ):
                assert time.monotonic() < deadline, "Database plan clocks did not become due"
                time.sleep(0.05)
        call = (
            sql.SQL("SELECT {}.expire_plans()")
            .format(sql.Identifier(capability.namespace))
            .as_string()
        )
        with pytest.raises(DBAPIError):
            with authorizer.begin() as db:
                db.scalar(text(call))
        removed = []
        for _ in range(3):
            with executor.begin() as db:
                removed.append(db.scalar(text(call)))
        assert removed == [100, 10, 0]
        with proof_engine(proof) as db:
            assert db.scalar(text("SELECT count(*) FROM public.account_erasure_plans")) == 0
            assert (
                db.scalar(
                    text(
                        "SELECT count(*) FROM public.audit_log "
                        "WHERE action='data_request.erasure_plan_expiry_batch'"
                    )
                )
                == 2
            )
        assert all(value <= 100 for value in removed)


def test_http_plan_uses_verified_context_private_profile_and_returns_only_blocked_plan(monkeypatch):
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from services import erasure_plans
    from services.erasure_config import ErasureSettings

    with planned_source() as (proof, capability, identity, authorizer, executor):
        learner, admin, case = reviewed_case(identity)
        config = ErasureSettings(
            enabled=True,
            database_url=capability.executor_url,
            authorizer_database_url=capability.authorizer_url,
            capability_namespace=capability.namespace,
        )
        loader = []

        def load():
            loader.append(True)
            return config

        monkeypatch.setattr(erasure_plans, "load_erasure", load)
        app = create_app(proof.settings, identity, channel_wakeup=lambda settings, request_id: None)
        path = f"/api/v1/admin/data-requests/{case}/erasure-plan"
        with TestClient(app) as client:
            assert client.get(path).status_code == 401
            assert (
                client.get(path, headers={"Authorization": "Bearer " + learner[0]}).status_code
                == 403
            )
            assert not loader
            response = client.get(path, headers={"Authorization": "Bearer " + admin[0]})
            assert response.status_code == 200, response.text
            result = ErasurePlan.model_validate(response.json())
            assert result.authorization_available is False and result.request_id == case
            assert set(response.json()) == set(ErasurePlan.model_fields)
            assert "source_nonce" not in response.text and "session_id" not in response.text
            assert capability.authorizer_url.get_secret_value() not in response.text
            with proof_engine(proof) as db:
                assert db.scalar(text("SELECT count(*) FROM public.account_erasure_jobs")) == 0


def test_http_rechecks_revocation_after_normal_authentication_has_finished(monkeypatch):
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from services import erasure_plans
    from services.erasure_config import ErasureSettings

    with planned_source() as (proof, capability, identity, authorizer, executor):
        learner, admin, case = reviewed_case(identity)
        config = ErasureSettings(
            enabled=True,
            database_url=capability.executor_url,
            authorizer_database_url=capability.authorizer_url,
            capability_namespace=capability.namespace,
        )
        monkeypatch.setattr(erasure_plans, "load_erasure", lambda: config)
        original = erasure_plans.context

        def revoke(*args):
            value = original(*args)
            provision(identity, "primary-admin@example.invalid", "ADMIN", revoke=True)
            return value

        monkeypatch.setattr(erasure_plans, "context", revoke)
        with TestClient(create_app(proof.settings, identity)) as client:
            response = client.get(
                f"/api/v1/admin/data-requests/{case}/erasure-plan",
                headers={"Authorization": "Bearer " + admin[0]},
            )
            assert response.status_code == 503
        with proof_engine(proof) as db:
            assert db.scalar(text("SELECT count(*) FROM public.account_erasure_plans")) == 0


def test_readable_ordinary_sql_login_cannot_delegate_an_admin_session():
    import secrets

    from pydantic import SecretStr
    from sqlalchemy.engine import make_url

    with planned_source() as (proof, capability, identity, authorizer, executor):
        _, admin, case = reviewed_case(identity)
        role = "kasoma_plan_reader_" + uuid4().hex
        password = secrets.token_urlsafe(32)
        with identity.engine.begin() as db:
            db.execute(
                text("SELECT set_config('kasoma.reader_password',:password,true)"),
                {"password": password},
            )
            statement = sql.SQL("""
              DO $$ BEGIN
                EXECUTE format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
                  NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD %L',{},
                  current_setting('kasoma.reader_password'));
              EXCEPTION WHEN OTHERS THEN
                RAISE EXCEPTION 'Synthetic reader unavailable' USING ERRCODE='P0001';
              END $$;
              GRANT USAGE ON SCHEMA public TO {};
              GRANT SELECT ON public.auth_sessions,public.account_erasure_state TO {};
            """).format(sql.Literal(role), sql.Identifier(role), sql.Identifier(role))
            db.execute(text(statement.as_string()))
        url = make_url(proof.settings.database_url.get_secret_value()).set(
            username=role, password=password
        )
        ordinary = engine_for(
            proof.settings.model_copy(
                update={"database_url": SecretStr(url.render_as_string(hide_password=False))}
            )
        )
        try:
            with ordinary.connect() as db:
                assert (
                    db.scalar(
                        text("SELECT count(*) FROM public.auth_sessions WHERE id=:id"),
                        {"id": admin[1]},
                    )
                    == 1
                )
            with pytest.raises(DBAPIError) as rejected:
                issue(proof, capability, ordinary, admin[1], case)
            assert rejected.value.orig.sqlstate == "42501"
            with pytest.raises(DBAPIError), ordinary.begin() as db:
                db.execute(
                    text(
                        sql.SQL("SET ROLE {}")
                        .format(sql.Identifier("kasoma_ea_" + proof.nonce.hex))
                        .as_string()
                    )
                )
        finally:
            ordinary.dispose()


def test_source_catalog_drift_cannot_issue_a_plan():
    with planned_source() as (proof, capability, identity, authorizer, executor):
        _, admin, case = reviewed_case(identity)
        with identity.engine.begin() as db:
            db.execute(text("ALTER TABLE public.users ADD COLUMN synthetic_unknown text"))
        with pytest.raises(DBAPIError) as rejected:
            issue(proof, capability, authorizer, admin[1], case)
        assert rejected.value.orig.sqlstate == "42501"
        with proof_engine(proof) as db:
            assert db.scalar(text("SELECT count(*) FROM public.account_erasure_plans")) == 0


def test_private_plan_gate_agrees_with_public_subject_and_precedes_case_row_locks():
    from services.domain.data_requests import DataRequest
    from tests.integration.test_account_processing import EXCLUSIVE

    with planned_source() as (proof, capability, identity, authorizer, executor):
        learner, admin, case = reviewed_case(identity)
        with proof_engine(proof) as fence, fence.begin():
            assert fence.scalar(EXCLUSIVE, {"subject": learner[2]}) is True
            # The private call must reach the busy gate before trying this locked row.
            # Reversed ordering fails with a lock timeout, not the fixed busy denial.
            fence.execute(select(DataRequest.id).where(DataRequest.id == case).with_for_update())
            with pytest.raises(DBAPIError, match="Erasure source busy"):
                issue(proof, capability, authorizer, admin[1], case)
            # A failed busy call must write no plan/audit.
            with Session(identity.engine) as db, db.begin():
                assert db.scalar(text("SELECT count(*) FROM account_erasure_plans")) == 0
                assert (
                    db.scalar(
                        text(
                            "SELECT count(*) FROM audit_log "
                            "WHERE action='data_request.erasure_plan_read'"
                        )
                    )
                    == 0
                )
        with authorizer.connect().execution_options(isolation_level="REPEATABLE READ") as db:
            with db.begin():
                db.execute(text("SET LOCAL statement_timeout='5000ms'"))
                assert call_private_plan(db, proof, capability, admin[1], case).request_id == case
                with proof_engine(proof) as observer:
                    assert observer.scalar(EXCLUSIVE, {"subject": learner[2]}) is False
                    assert observer.scalar(EXCLUSIVE, {"subject": uuid4()}) is True
        with proof_engine(proof) as observer:
            assert observer.scalar(EXCLUSIVE, {"subject": learner[2]}) is True


def call_private_plan(db, proof, capability, session, case):
    with proof_engine(proof) as binding:
        nonce = binding.scalar(text("SELECT scope_nonce FROM account_erasure_state"))
    return ErasurePlan.model_validate(
        db.scalar(
            text(
                sql.SQL(
                    "SELECT {}.issue_plan(:session,:case,CAST(:database AS oid),"
                    "CAST(:namespace AS oid),:nonce,:correlation)"
                )
                .format(sql.Identifier(capability.namespace))
                .as_string()
            ),
            {
                "session": session,
                "case": case,
                "database": proof.database_oid,
                "namespace": proof.namespace_oid,
                "nonce": nonce,
                "correlation": uuid4(),
            },
        )
    )


def test_private_plan_rejects_subject_row_changed_after_snapshot_before_gate():
    from tests.integration.test_account_processing import EXCLUSIVE

    with planned_source() as (proof, capability, identity, authorizer, executor):
        learner, admin, case = reviewed_case(identity)
        with pytest.raises(DBAPIError) as failed:
            with authorizer.connect().execution_options(isolation_level="REPEATABLE READ") as db:
                with db.begin():
                    db.execute(text("SET LOCAL statement_timeout='5000ms'"))
                    # Establish the same snapshot used by the private scope/auth checks.
                    db.scalar(
                        text(
                            sql.SQL("SELECT {}.readiness()")
                            .format(sql.Identifier(capability.namespace))
                            .as_string()
                        )
                    )
                    with proof_engine(proof) as fence, fence.begin():
                        assert fence.scalar(EXCLUSIVE, {"subject": learner[2]}) is True
                        # Ordinary disablement represents a changed subject row; closed_at
                        # remains dormant and no erasure authority is manufactured here.
                        fence.execute(
                            text("UPDATE users SET status='DISABLED' WHERE id=:subject"),
                            {"subject": learner[2]},
                        )
                    call_private_plan(db, proof, capability, admin[1], case)
        assert failed.value.orig.sqlstate == "40001"
        with proof_engine(proof) as db:
            assert db.scalar(text("SELECT count(*) FROM account_erasure_plans")) == 0
            assert (
                db.scalar(
                    text(
                        "SELECT count(*) FROM audit_log "
                        "WHERE action='data_request.erasure_plan_read'"
                    )
                )
                == 0
            )
        # A fresh snapshot remains able to exercise this disabled learner's privacy case.
        assert issue(proof, capability, authorizer, admin[1], case).request_id == case


@pytest.mark.parametrize("version", [2, 3, 4, 5])
def test_http_refuses_legacy_private_recipe_before_plan_writes(monkeypatch, version):
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from scripts import erasure_capability
    from services import erasure_plans
    from services.erasure_config import ErasureSettings

    # Rehearse the actual historical v2/v3/v4/v5 recipes in a fresh disposable source only.
    with monkeypatch.context() as legacy:
        legacy.setattr(
            erasure_capability, "CAPABILITY_VERSION", f"isolated-erasure-capability-v{version}"
        )
        legacy.setattr(
            erasure_capability,
            "SQL_PLAN_SOURCE",
            erasure_capability.SQL_SOURCE.parent / f"erasure_plans_v{min(version, 3)}.sql",
        )
        with planned_source() as (proof, capability, identity, authorizer, executor):
            _, admin, case = reviewed_case(identity)
            config = ErasureSettings(
                enabled=True,
                database_url=capability.executor_url,
                authorizer_database_url=capability.authorizer_url,
                capability_namespace=capability.namespace,
            )
            legacy.setattr(erasure_plans, "load_erasure", lambda: config)
            with TestClient(create_app(proof.settings, identity)) as client:
                response = client.get(
                    f"/api/v1/admin/data-requests/{case}/erasure-plan",
                    headers={"Authorization": "Bearer " + admin[0]},
                )
                assert response.status_code == 503
            with proof_engine(proof) as db:
                assert db.scalar(text("SELECT count(*) FROM account_erasure_plans")) == 0
