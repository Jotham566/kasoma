"""ADR-075 linked/guardian dispatch barriers, not closure executor acceptance."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier, local
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from services.identity import IdentityService
from services.identity_contracts import OTPRequest, OTPVerify
from tests.integration.test_account_processing import EXCLUSIVE, active_gate_count
from tests.integration.test_closed_credentials import (
    Observations,
    closed_fixture,
    credential_source,
    register,
)

pytestmark = pytest.mark.integration


def pair(identity):
    actor, tokens = register(identity, "dispatch-actor@example.invalid")
    recipient, _ = register(identity, "dispatch-recipient@example.invalid")
    return actor, tokens, recipient, "dispatch-recipient@example.invalid"


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
@pytest.mark.parametrize("recipient", ["closed-recipient@example.invalid", "+256700000051"])
def test_closed_bound_recipient_never_receives_link_or_guardian_code(purpose, recipient):
    with credential_source() as (proof, identity, fake, now):
        _, actor = register(identity, "active-actor@example.invalid")
        subject, _ = register(identity, recipient)
        closed_fixture(proof, identity, subject)
        now[0] += timedelta(seconds=61)
        sent = len(fake.messages)
        observations = Observations()
        result = identity.request_otp(
            OTPRequest(identifier=recipient, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            actor.access_token,
            observer=observations,
        )
        assert len(fake.messages) == sent and observations.events == []
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
@pytest.mark.parametrize("closed", ["ACTOR", "RECIPIENT"])
def test_closure_after_intake_suppresses_dispatch_and_preserves_closed_actor_source(
    monkeypatch,
    purpose,
    closed,
):
    with credential_source() as (proof, identity, fake, now):
        actor, tokens, recipient, address = pair(identity)
        now[0] += timedelta(seconds=61)
        original = identity.deliver_otp
        observations = Observations()
        sent = len(fake.messages)

        def after_commit(*args, **kwargs):
            closed_fixture(proof, identity, actor if closed == "ACTOR" else recipient)
            return original(*args, **kwargs)

        monkeypatch.setattr(identity, "deliver_otp", after_commit)
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
            observer=observations,
        )
        assert len(fake.messages) == sent and observations.events == []
        with identity.engine.connect() as db:
            row = db.execute(
                text("SELECT user_id,consumed_at,expires_at FROM otp_challenges WHERE id=:id"),
                {"id": result.challenge_id},
            ).one_or_none()
            if closed == "ACTOR":
                # Ordinary failure cleanup must not mutate a closed actor's source.
                assert row is not None and row.user_id == actor and row.consumed_at is None
                assert row.expires_at == now[0] + timedelta(minutes=10)
            else:
                assert row is None


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
@pytest.mark.parametrize("change", ["REVOKED", "RECENCY_EXPIRED"])
def test_current_actor_session_is_rechecked_before_dispatch(monkeypatch, purpose, change):
    with credential_source() as (_, identity, fake, now):
        actor, tokens, _, address = pair(identity)
        now[0] += timedelta(seconds=61)
        original = identity.deliver_otp
        observations = Observations()

        def revoke(*args, **kwargs):
            if change == "REVOKED":
                identity.logout(tokens.access_token, True, str(uuid4()))
            else:
                # Access is still within15 minutes; recent OTP authority is not.
                now[0] += timedelta(minutes=10)
            return original(*args, **kwargs)

        monkeypatch.setattr(identity, "deliver_otp", revoke)
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
            observer=observations,
        )
        assert len(fake.messages) == 2 and observations.events == []
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )
        assert active_gate_count(identity.engine, actor) == 0


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
def test_provider_has_two_idle_subject_gates_without_account_or_row_transaction(purpose):
    with credential_source() as (_, identity, _, now):
        actor, tokens, recipient, address = pair(identity)
        now[0] += timedelta(seconds=61)
        called = []

        class Provider:
            def send(self, destination, body):
                assert destination == address
                for subject in (actor, recipient):
                    assert active_gate_count(identity.engine, subject) == 1
                with identity.engine.connect() as db:
                    for subject in (actor, recipient):
                        assert db.scalar(EXCLUSIVE, {"subject": subject}) is False
                    assert (
                        db.scalar(
                            text("""
                      SELECT count(DISTINCT a.pid) FROM pg_catalog.pg_stat_activity a
                      JOIN pg_catalog.pg_locks l ON l.pid=a.pid
                      WHERE a.state='idle' AND a.xact_start IS NULL
                        AND l.locktype='advisory' AND l.granted
                        AND l.mode='ShareLock' AND l.objsubid=1
                    """)
                        )
                        == 1
                    )
                called.append(True)
                return "fake-linked"

        identity.email = Provider()
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
        )
        assert called == [True] and result.challenge_id
        with identity.engine.connect() as db:
            for subject in (actor, recipient):
                assert db.scalar(EXCLUSIVE, {"subject": subject}) is True


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
def test_partial_busy_recipient_acquisition_releases_actor_gate(monkeypatch, purpose):
    with credential_source() as (_, identity, fake, now):
        a, ta = register(identity, "lower-or-upper-a@example.invalid")
        b, tb = register(identity, "lower-or-upper-b@example.invalid")
        actor, tokens, recipient, address = (
            (a, ta, b, "lower-or-upper-b@example.invalid")
            if a.int < b.int
            else (b, tb, a, "lower-or-upper-a@example.invalid")
        )
        assert actor.int < recipient.int
        now[0] += timedelta(seconds=61)
        original = identity.deliver_otp
        observations = Observations()

        def busy(*args, **kwargs):
            with identity.engine.begin() as held:
                assert held.scalar(EXCLUSIVE, {"subject": recipient}) is True
                result = original(*args, **kwargs)
                assert active_gate_count(identity.engine, actor) == 0
                with identity.engine.connect() as db:
                    assert db.scalar(EXCLUSIVE, {"subject": actor}) is True
                return result

        monkeypatch.setattr(identity, "deliver_otp", busy)
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
            observer=observations,
        )
        assert len(fake.messages) == 2 and observations.events == []
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
def test_two_subject_dispatch_uses_one_connection_pool(purpose):
    with credential_source() as (proof, identity, fake, now):
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
            _, tokens, _, address = pair(identity)
            now[0] += timedelta(seconds=61)
            result = identity.request_otp(
                OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
                str(uuid4()),
                tokens.access_token,
            )
            assert len(fake.messages) == 3
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


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
def test_failure_cleanup_never_rewrites_source_after_actor_closure(monkeypatch, purpose):
    with credential_source() as (proof, identity, _, now):
        actor, tokens, _, address = pair(identity)
        now[0] += timedelta(seconds=61)
        original = identity.discard_new_challenge
        observations = Observations()
        captured = []

        class FailedProvider:
            def send(self, destination, body):
                raise RuntimeError("SYNTHETIC_PROVIDER_FAILURE")

        def close_before_cleanup(challenge, owner):
            with identity.engine.connect() as db:
                captured.append(
                    db.scalar(
                        text("SELECT to_jsonb(c) FROM otp_challenges c WHERE id=:id"),
                        {"id": challenge},
                    )
                )
            closed_fixture(proof, identity, actor)
            original(challenge, owner)

        identity.email = FailedProvider()
        monkeypatch.setattr(identity, "discard_new_challenge", close_before_cleanup)
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
            observer=observations,
        )
        assert observations.events == [("EMAIL", "FAILED")]
        with identity.engine.connect() as db:
            assert (
                db.scalar(
                    text("SELECT to_jsonb(c) FROM otp_challenges c WHERE id=:id"),
                    {"id": result.challenge_id},
                )
                == captured[0]
            )


def test_consumed_link_evidence_is_not_discarded_after_provider_failure(monkeypatch):
    with credential_source() as (_, identity, fake, now):
        actor, tokens = register(identity, "consumed-link-actor@example.invalid")
        address = "consumed-link-recipient@example.invalid"
        now[0] += timedelta(seconds=61)
        other = IdentityService(
            identity.engine, identity.settings, fake, fake, identity.clock, lambda: "246810"
        )
        original = identity.discard_new_challenge
        verified = []

        class FailedProvider:
            def send(self, destination, body):
                raise RuntimeError("SYNTHETIC_UNCERTAIN_DELIVERY")

        def consume_before_cleanup(challenge, owner):
            credentials = other.verify(
                OTPVerify(challenge_id=challenge, code="246810", purpose="LINK"),
                tokens.access_token,
                str(uuid4()),
            )
            verified.append(other.me(credentials.access_token).id)
            original(challenge, owner)

        identity.email = FailedProvider()
        monkeypatch.setattr(identity, "discard_new_challenge", consume_before_cleanup)
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose="LINK", device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
        )
        assert verified == [actor]
        with identity.engine.connect() as db:
            assert (
                db.scalar(
                    text("SELECT consumed_at IS NOT NULL FROM otp_challenges WHERE id=:id"),
                    {"id": result.challenge_id},
                )
                is True
            )


@pytest.mark.parametrize("purpose", ["LINK", "GUARDIAN"])
@pytest.mark.parametrize("stage", ["INTAKE", "DISPATCH"])
def test_binding_created_after_snapshot_is_refused_without_late_account_adoption(
    monkeypatch, purpose, stage
):
    with credential_source() as (_, identity, fake, now):
        actor, tokens = register(identity, "first-binding-actor@example.invalid")
        _, other_tokens = register(identity, "second-binding-actor@example.invalid")
        address = "changed-linked-recipient@example.invalid"
        now[0] += timedelta(seconds=61)
        prepared = identity.request_otp(
            OTPRequest(identifier=address, purpose="LINK", device_id=uuid4()),
            str(uuid4()),
            other_tokens.access_token,
        )
        now[0] += timedelta(seconds=61)
        other = IdentityService(
            identity.engine, identity.settings, fake, fake, identity.clock, lambda: "246810"
        )
        method = "rate" if stage == "INTAKE" else "deliver_otp"
        original_method, original_lock = getattr(identity, method), identity.lock_user
        bound, late = [], []
        sent = len(fake.messages)

        def rate(*args, **kwargs):
            if not bound:
                bound.append(True)
                other.verify(
                    OTPVerify(challenge_id=prepared.challenge_id, code="246810", purpose="LINK"),
                    other_tokens.access_token,
                    str(uuid4()),
                )
            return original_method(*args, **kwargs)

        def only_original_actor(db, subject):
            if subject != actor:
                late.append(subject)
                raise AssertionError("Cannot adopt newly bound owner after identifier work")
            return original_lock(db, subject)

        monkeypatch.setattr(identity, method, rate)
        monkeypatch.setattr(identity, "lock_user", only_original_actor)
        result = identity.request_otp(
            OTPRequest(identifier=address, purpose=purpose, device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
        )
        assert bound == [True] and late == [] and len(fake.messages) == sent
        with identity.engine.connect() as db:
            assert not db.scalar(
                text("SELECT EXISTS(SELECT 1 FROM otp_challenges WHERE id=:id)"),
                {"id": result.challenge_id},
            )


def test_self_link_duplicate_subject_does_not_leave_a_reentrant_session_gate():
    with credential_source() as (_, identity, fake, now):
        address = "self-link@example.invalid"
        actor, tokens = register(identity, address)
        now[0] += timedelta(seconds=61)
        identity.request_otp(
            OTPRequest(identifier=address, purpose="LINK", device_id=uuid4()),
            str(uuid4()),
            tokens.access_token,
        )
        assert len(fake.messages) == 2 and active_gate_count(identity.engine, actor) == 0
        with identity.engine.connect() as db:
            assert db.scalar(EXCLUSIVE, {"subject": actor}) is True


def test_opposing_actor_recipient_requests_do_not_invert_account_locks(monkeypatch):
    with credential_source() as (_, identity, fake, now):
        _, a = register(identity, "opposing-a@example.invalid")
        _, b = register(identity, "opposing-b@example.invalid")
        now[0] += timedelta(seconds=61)
        barrier, per_thread = Barrier(2), local()
        original = identity.authenticate

        def authenticated(*args, **kwargs):
            result = original(*args, **kwargs)
            if not getattr(per_thread, "passed", False):
                per_thread.passed = True
                barrier.wait(timeout=5)
            return result

        monkeypatch.setattr(identity, "authenticate", authenticated)

        def request(token, address):
            return identity.request_otp(
                OTPRequest(identifier=address, purpose="LINK", device_id=uuid4()),
                str(uuid4()),
                token,
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(request, a.access_token, "opposing-b@example.invalid")
            second = pool.submit(request, b.access_token, "opposing-a@example.invalid")
            results = [first.result(timeout=5), second.result(timeout=5)]
        assert len(fake.messages) == 4
        with identity.engine.connect() as db:
            assert (
                db.scalar(
                    text("SELECT count(*) FROM otp_challenges WHERE id=ANY(:ids)"),
                    {"ids": [r.challenge_id for r in results]},
                )
                == 2
            )
