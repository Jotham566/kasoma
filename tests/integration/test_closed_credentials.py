"""ADR-061 future-state credential denials; not closure/executor acceptance."""

from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, text

from services.database import engine_for
from services.identity import IdentityError, IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from services.providers import FakeMessagingProvider
from tests.integration.test_account_processing import EXCLUSIVE, active_gate_count
from tests.integration.test_erasure_capability import source

pytestmark = pytest.mark.integration


@contextmanager
def credential_source():
    with source() as proof:
        engine = engine_for(proof.settings)
        now = [datetime.now(UTC)]
        fake = FakeMessagingProvider()
        identity = IdentityService(
            engine, proof.settings, fake, fake, lambda: now[0], lambda: "246810"
        )
        try:
            yield proof, identity, fake, now
        finally:
            engine.dispose()


def register(identity, identifier):
    challenge = identity.request_otp(
        OTPRequest(identifier=identifier, device_id=uuid4()), str(uuid4()), None
    )
    tokens = identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    return identity.me(tokens.access_token).id, tokens


def closed_fixture(proof, identity, subject):
    """Create only a future-state fixture in this invocation's exclusive source.

    The real closure capability does not exist. This exact test-only trigger toggle
    cannot prove authorization/closure or erasure; it only exercises credential
    consumers against a committed closed row with all normal guards restored.
    There is no URL, schema, table, trigger or SQL selector supplied by a caller.
    """
    proof.verify()
    with identity.engine.begin() as db:
        assert db.scalar(EXCLUSIVE, {"subject": subject}) is True
        db.execute(text("ALTER TABLE public.users DISABLE TRIGGER users_erasure_closure"))
        db.execute(
            text(
                "UPDATE public.users SET status='DISABLED',closed_at=clock_timestamp() WHERE id=:id"
            ),
            {"id": subject},
        )
        db.execute(text("ALTER TABLE public.users ENABLE TRIGGER users_erasure_closure"))
        assert db.scalar(text("SELECT count(*) FROM public.account_erasure_jobs")) == 0
        assert (
            db.scalar(
                text(
                    "SELECT tgenabled FROM pg_catalog.pg_trigger "
                    "WHERE tgrelid='public.users'::regclass "
                    "AND tgname='users_erasure_closure'"
                )
            )
            == "O"
        )


@pytest.mark.parametrize("identifier", ["closed@example.invalid", "+256700000041"])
def test_closed_retained_identifier_gets_generic_acceptance_without_code_or_dispatch(identifier):
    with credential_source() as (proof, identity, fake, now):
        subject, _ = register(identity, identifier)
        closed_fixture(proof, identity, subject)
        now[0] += timedelta(seconds=61)
        sent = len(fake.messages)
        with identity.engine.connect() as db:
            before = db.scalar(text("SELECT count(*) FROM otp_challenges"))
        result = identity.request_otp(
            OTPRequest(identifier=identifier, device_id=uuid4()), str(uuid4()), None
        )
        assert result.challenge_id and len(fake.messages) == sent
        with identity.engine.connect() as db:
            assert db.scalar(text("SELECT count(*) FROM otp_challenges")) == before
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )


@pytest.mark.parametrize("rotated", [False, True])
def test_closed_refresh_rejection_does_not_revoke_or_rewrite_a_session_family(rotated):
    with credential_source() as (proof, identity, _, _):
        subject, tokens = register(identity, "refresh-closed@example.invalid")
        if rotated:
            identity.refresh(tokens.refresh_token)
        closed_fixture(proof, identity, subject)
        with identity.engine.connect() as db:
            before = db.execute(text("SELECT to_jsonb(s) FROM auth_sessions s ORDER BY id")).all()
        with pytest.raises(IdentityError) as refused:
            identity.refresh(tokens.refresh_token)
        assert refused.value.code == "AUTH_REQUIRED" and refused.value.status == 401
        with identity.engine.connect() as db:
            after = db.execute(text("SELECT to_jsonb(s) FROM auth_sessions s ORDER BY id")).all()
        assert after == before


@pytest.mark.parametrize("code", ["246810", "000000"])
def test_closed_login_does_not_consume_or_increment_an_unbound_challenge(code):
    with credential_source() as (proof, identity, _, now):
        email = "verify-closed@example.invalid"
        subject, _ = register(identity, email)
        now[0] += timedelta(seconds=61)
        challenge = identity.request_otp(
            OTPRequest(identifier=email, device_id=uuid4()), str(uuid4()), None
        )
        closed_fixture(proof, identity, subject)
        with identity.engine.connect() as db:
            before = db.execute(
                text("SELECT to_jsonb(c) FROM otp_challenges c WHERE id=:id"),
                {"id": challenge.challenge_id},
            ).scalar_one()
        with pytest.raises(IdentityError) as denied:
            identity.verify(
                OTPVerify(challenge_id=challenge.challenge_id, code=code), None, str(uuid4())
            )
        assert denied.value.code == "AUTH_REQUIRED"
        with identity.engine.connect() as db:
            assert (
                db.execute(
                    text("SELECT to_jsonb(c) FROM otp_challenges c WHERE id=:id"),
                    {"id": challenge.challenge_id},
                ).scalar_one()
                == before
            )


@pytest.mark.parametrize("disabled", [False, True])
def test_nonclosed_refresh_reuse_still_revokes_the_family(disabled):
    with credential_source() as (_, identity, _, _):
        subject, tokens = register(identity, "nonclosed-reuse@example.invalid")
        identity.refresh(tokens.refresh_token)
        if disabled:
            with identity.engine.begin() as db:
                db.execute(text("UPDATE users SET status='DISABLED' WHERE id=:id"), {"id": subject})
        with pytest.raises(IdentityError) as refused:
            identity.refresh(tokens.refresh_token)
        assert refused.value.code == "AUTH_REQUIRED"
        with identity.engine.connect() as db:
            assert (
                db.scalar(text("SELECT count(*) FROM auth_sessions WHERE revoked_at IS NULL")) == 0
            )
            assert db.scalar(text("SELECT count(*) FROM auth_sessions")) == 2


class Observations:
    def __init__(self):
        self.events = []

    def record(self, kind, outcome):
        self.events.append((kind, outcome))


@pytest.mark.parametrize("identifier", ["dispatch@example.invalid", "+256700000042"])
@pytest.mark.parametrize("failure", [False, True])
def test_bound_fake_dispatch_holds_only_idle_subject_gate_and_cleans_failure(identifier, failure):
    with credential_source() as (_, identity, _, now):
        subject, _ = register(identity, identifier)
        now[0] += timedelta(seconds=61)
        observations = Observations()
        called = []

        class Provider:
            def send(self, recipient, body):
                assert recipient == identifier
                assert active_gate_count(identity.engine, subject) == 1
                with identity.engine.connect() as db:
                    assert db.scalar(EXCLUSIVE, {"subject": subject}) is False
                    # The sole session advisory gate, not the observing transaction,
                    # is idle outside a transaction while the provider runs.
                    assert (
                        db.scalar(
                            text("""
                      SELECT count(*) FROM pg_catalog.pg_stat_activity a
                      WHERE a.state='idle' AND a.xact_start IS NULL AND a.pid IN
                        (SELECT pid FROM pg_catalog.pg_locks WHERE locktype='advisory'
                          AND granted AND mode='ShareLock' AND objsubid=1)
                    """)
                        )
                        == 1
                    )
                called.append(True)
                if failure:
                    raise RuntimeError("SYNTHETIC_PROVIDER_DIAGNOSTIC_MUST_NOT_ESCAPE")
                return "fake-dispatched"

        identity.email = identity.sms = Provider()
        result = identity.request_otp(
            OTPRequest(identifier=identifier, device_id=uuid4()),
            str(uuid4()),
            None,
            observer=observations,
        )
        assert called == [True] and active_gate_count(identity.engine, subject) == 0
        kind = "EMAIL" if "@" in identifier else "SMS"
        assert observations.events == [(kind, "FAILED" if failure else "RETURNED")]
        with identity.engine.connect() as db:
            assert db.scalar(EXCLUSIVE, {"subject": subject}) is True
            assert (
                db.scalar(
                    text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                    {"id": result.challenge_id},
                )
                is not failure
            )


def test_closure_between_challenge_commit_and_dispatch_suppresses_without_provider_observation(
    monkeypatch,
):
    with credential_source() as (proof, identity, fake, now):
        email = "late-closure@example.invalid"
        subject, _ = register(identity, email)
        now[0] += timedelta(seconds=61)
        original = identity.deliver_otp
        sent = len(fake.messages)
        observations = Observations()

        def after_commit(*args, **kwargs):
            closed_fixture(proof, identity, subject)
            return original(*args, **kwargs)

        monkeypatch.setattr(identity, "deliver_otp", after_commit)
        result = identity.request_otp(
            OTPRequest(identifier=email, device_id=uuid4()),
            str(uuid4()),
            None,
            observer=observations,
        )
        assert len(fake.messages) == sent and observations.events == []
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )


def test_busy_dispatch_gate_returns_generic_and_does_not_claim_provider_failure(monkeypatch):
    with credential_source() as (_, identity, fake, now):
        email = "busy-dispatch@example.invalid"
        subject, _ = register(identity, email)
        now[0] += timedelta(seconds=61)
        original = identity.deliver_otp
        observations = Observations()

        def after_commit(*args, **kwargs):
            with identity.engine.begin() as db:
                assert db.scalar(EXCLUSIVE, {"subject": subject}) is True
                return original(*args, **kwargs)

        monkeypatch.setattr(identity, "deliver_otp", after_commit)
        result = identity.request_otp(
            OTPRequest(identifier=email, device_id=uuid4()),
            str(uuid4()),
            None,
            observer=observations,
        )
        assert len(fake.messages) == 1 and observations.events == []
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )
        assert active_gate_count(identity.engine, subject) == 0


def test_uncertain_dispatch_release_keeps_actual_return_observation_and_discards_new_code(caplog):
    with credential_source() as (_, identity, fake, now):
        email = "release-failure@example.invalid"
        subject, _ = register(identity, email)
        now[0] += timedelta(seconds=61)
        observations = Observations()

        def fail_release(conn, cursor, statement, parameters, context, executemany):
            if "pg_advisory_unlock_shared" in statement:
                raise RuntimeError("SYNTHETIC_RELEASE_DIAGNOSTIC_MUST_NOT_ESCAPE")

        event.listen(identity.engine, "before_cursor_execute", fail_release)
        try:
            result = identity.request_otp(
                OTPRequest(identifier=email, device_id=uuid4()),
                str(uuid4()),
                None,
                observer=observations,
            )
        finally:
            event.remove(identity.engine, "before_cursor_execute", fail_release)
        assert len(fake.messages) == 2 and observations.events == [("EMAIL", "RETURNED")]
        assert active_gate_count(identity.engine, subject) == 0
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )
        assert "SYNTHETIC_RELEASE_DIAGNOSTIC_MUST_NOT_ESCAPE" not in caplog.text


@pytest.mark.parametrize("stage", ["INTAKE", "DISPATCH"])
def test_newly_bound_identifier_is_not_adopted_and_older_unbound_code_is_not_swept(
    monkeypatch, stage
):
    with credential_source() as (_, identity, fake, now):
        _, owner = register(identity, "link-owner@example.invalid")
        target = "new-binding@example.invalid"
        now[0] += timedelta(seconds=61)
        older = identity.request_otp(
            OTPRequest(identifier=target, device_id=uuid4()), str(uuid4()), None
        )
        now[0] += timedelta(seconds=61)
        linking = identity.request_otp(
            OTPRequest(identifier=target, device_id=uuid4(), purpose="LINK"),
            str(uuid4()),
            owner.access_token,
        )
        now[0] += timedelta(seconds=61)
        other = IdentityService(
            identity.engine, identity.settings, fake, fake, identity.clock, lambda: "246810"
        )
        sent = len(fake.messages)
        observations = Observations()
        invoked = []
        late_locks = []
        method = "rate" if stage == "INTAKE" else "deliver_otp"
        original = getattr(identity, method)

        def bind_once(*args, **kwargs):
            if not invoked:
                invoked.append(True)
                other.verify(
                    OTPVerify(challenge_id=linking.challenge_id, code="246810", purpose="LINK"),
                    owner.access_token,
                    str(uuid4()),
                )
            return original(*args, **kwargs)

        def no_late_account_lock(*args):
            late_locks.append(True)
            raise AssertionError("New owner must not be locked/adopted after the pre-read")

        monkeypatch.setattr(identity, method, bind_once)
        monkeypatch.setattr(identity, "lock_user", no_late_account_lock)
        result = identity.request_otp(
            OTPRequest(identifier=target, device_id=uuid4()),
            str(uuid4()),
            None,
            observer=observations,
        )
        assert invoked == [True] and len(fake.messages) == sent and observations.events == []
        assert late_locks == []
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )
            assert (
                db.scalar(
                    text(
                        "SELECT user_id IS NULL AND consumed_at IS NULL FROM otp_challenges "
                        "WHERE id=:id"
                    ),
                    {"id": older.challenge_id},
                )
                is True
            )


def test_bound_dispatch_can_recheck_using_a_single_connection_pool():
    with credential_source() as (proof, identity, fake, now):
        # Same invocation-owned database; deliberately no spare checkout is available.
        limited = create_engine(
            proof.settings.database_url.get_secret_value(),
            pool_size=1,
            max_overflow=0,
            pool_timeout=0.1,
            hide_parameters=True,
            connect_args={
                "connect_timeout": 2,
                "options": "-c timezone=UTC -c statement_timeout=2000",
            },
        )
        identity.engine = limited
        try:
            register(identity, "one-connection@example.invalid")
            now[0] += timedelta(seconds=61)
            result = identity.request_otp(
                OTPRequest(identifier="one-connection@example.invalid", device_id=uuid4()),
                str(uuid4()),
                None,
            )
            assert len(fake.messages) == 2
            with limited.connect() as db:
                assert (
                    db.scalar(
                        text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                        {"id": result.challenge_id},
                    )
                    is True
                )
        finally:
            limited.dispose()
