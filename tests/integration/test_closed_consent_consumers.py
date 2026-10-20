"""Future closed-row consumer fixtures, never account-closure acceptance."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Event
from uuid import uuid4

import pytest
from sqlalchemy import text

from services.identity import IdentityError
from services.identity_contracts import ConsentInput, OTPRequest, ProfilePatch
from services.seed import fixture_id, seed
from services.staff import provision
from tests.integration.test_account_processing import EXCLUSIVE, wait_for_gate
from tests.integration.test_closed_credentials import closed_fixture, credential_source, register

pytestmark = pytest.mark.integration


def minor(identity, proof):
    seed(proof.settings, foundation_only=True)
    subject, tokens = register(identity, "minor@example.invalid")
    identity.update_profile(
        tokens.access_token,
        ProfilePatch(
            display_name="Synthetic learner",
            birth_date=date(2012, 1, 1),
            subject_ids=[fixture_id("Mathematics")],
        ),
        str(uuid4()),
    )
    return subject, tokens


def guardian_request(identity, tokens):
    challenge = identity.request_otp(
        OTPRequest(identifier="guardian@example.invalid", purpose="GUARDIAN", device_id=uuid4()),
        str(uuid4()),
        tokens.access_token,
    )
    return ConsentInput(
        consent_type="GUARDIAN",
        policy_version=identity.settings.consent_policy_version,
        affirmative=True,
        guardian_name="Synthetic guardian",
        guardian_relationship="Parent",
        challenge_id=challenge.challenge_id,
        code="246810",
    )


@pytest.mark.parametrize("code", ["246810", "000000"])
def test_closed_guardian_refused_before_consumption_or_new_evidence(code):
    with credential_source() as (proof, identity, _, now):
        seed(proof.settings, foundation_only=True)
        guardian, _ = register(identity, "guardian@example.invalid")
        _, tokens = register(identity, "minor@example.invalid")
        identity.update_profile(
            tokens.access_token,
            ProfilePatch(
                display_name="Synthetic learner",
                birth_date=date(2012, 1, 1),
                subject_ids=[fixture_id("Mathematics")],
            ),
            str(uuid4()),
        )
        now[0] += timedelta(seconds=61)
        challenge = identity.request_otp(
            OTPRequest(
                identifier="guardian@example.invalid", purpose="GUARDIAN", device_id=uuid4()
            ),
            str(uuid4()),
            tokens.access_token,
        )
        closed_fixture(proof, identity, guardian)
        with identity.engine.connect() as db:
            before = db.execute(text("SELECT to_jsonb(c) FROM otp_challenges c ORDER BY id")).all()
            events = db.scalar(text("SELECT count(*) FROM identity_outbox_events"))
        with pytest.raises(IdentityError) as refused:
            identity.consent(
                tokens.access_token,
                ConsentInput(
                    consent_type="GUARDIAN",
                    policy_version=proof.settings.consent_policy_version,
                    affirmative=True,
                    guardian_name="Synthetic guardian",
                    guardian_relationship="Parent",
                    challenge_id=challenge.challenge_id,
                    code=code,
                ),
                uuid4(),
                str(uuid4()),
            )
        assert refused.value.code == "OTP_INVALID"
        with identity.engine.connect() as db:
            assert (
                db.execute(text("SELECT to_jsonb(c) FROM otp_challenges c ORDER BY id")).all()
                == before
            )
            assert db.scalar(text("SELECT count(*) FROM consent_records")) == 0
            assert db.scalar(text("SELECT count(*) FROM identity_outbox_events")) == events


@pytest.mark.parametrize("state", ["ACTIVE", "DISABLED", "CLOSED"])
def test_role_revocation_preserves_closed_sources_but_allows_temporary_disable(state):
    with credential_source() as (proof, identity, _, _):
        email = "roles@example.invalid"
        subject, _ = register(identity, email)
        # Keep this a nonstaff closure fixture: no authority to erase staff provenance.
        if state == "CLOSED":
            closed_fixture(proof, identity, subject)
        else:
            provision(identity, email, "ADMIN")
            if state == "DISABLED":
                with identity.engine.begin() as db:
                    db.execute(
                        text("UPDATE users SET status='DISABLED' WHERE id=:id"), {"id": subject}
                    )
        with identity.engine.connect() as db:
            before = db.execute(text("SELECT to_jsonb(a) FROM audit_log a ORDER BY id")).all()
        if state == "CLOSED":
            with pytest.raises(ValueError, match="Closed identities"):
                provision(identity, email, "ADMIN", revoke=True)
        else:
            assert provision(identity, email, "ADMIN", revoke=True) == subject
        with identity.engine.connect() as db:
            after = db.execute(text("SELECT to_jsonb(a) FROM audit_log a ORDER BY id")).all()
            assert len(after) == len(before) + (state != "CLOSED")
            if state == "CLOSED":
                assert after == before
            assert db.scalar(text("SELECT count(*) FROM user_roles")) == 0


@pytest.mark.parametrize("recipient_state", ["UNBOUND", "ACTIVE", "DISABLED"])
def test_open_guardian_consent_replay_and_withdrawal_remain_available(recipient_state):
    with credential_source() as (proof, identity, _, now):
        _, tokens = minor(identity, proof)
        if recipient_state != "UNBOUND":
            guardian, _ = register(identity, "guardian@example.invalid")
            if recipient_state == "DISABLED":
                with identity.engine.begin() as db:
                    db.execute(
                        text("UPDATE users SET status='DISABLED' WHERE id=:id"), {"id": guardian}
                    )
        now[0] += timedelta(seconds=61)
        body = guardian_request(identity, tokens)
        key = uuid4()
        identity.consent(tokens.access_token, body, key, str(uuid4()))
        identity.consent(tokens.access_token, body, key, str(uuid4()))
        with identity.engine.connect() as db:
            assert db.scalar(text("SELECT count(*) FROM consent_records")) == 1
            assert (
                db.scalar(
                    text("SELECT attempts FROM otp_challenges WHERE id=:id"),
                    {"id": body.challenge_id},
                )
                == 1
            )
        # Already recorded evidence is not a new grant. Withdrawal must remain usable.
        if recipient_state != "UNBOUND":
            closed_fixture(proof, identity, guardian)
        identity.consent(tokens.access_token, body, key, str(uuid4()))
        identity.consent(
            tokens.access_token,
            ConsentInput(
                consent_type="WITHDRAW", policy_version=body.policy_version, affirmative=True
            ),
            uuid4(),
            str(uuid4()),
        )
        with identity.engine.connect() as db:
            assert (
                db.scalar(text("SELECT count(*) FROM consent_records WHERE revoked_at IS NULL"))
                == 0
            )


def test_new_binding_after_guardian_preread_is_not_adopted(monkeypatch):
    with credential_source() as (proof, identity, _, now):
        _, tokens = minor(identity, proof)
        now[0] += timedelta(seconds=61)
        body = guardian_request(identity, tokens)
        original = identity.identifier_binding
        changed = []

        def bind_after_read(db, kind, lookup):
            result = original(db, kind, lookup)
            if not changed:
                changed.append(True)
                register(identity, "guardian@example.invalid")
            return result

        monkeypatch.setattr(identity, "identifier_binding", bind_after_read)
        with pytest.raises(IdentityError, match="OTP_INVALID"):
            identity.consent(tokens.access_token, body, uuid4(), str(uuid4()))
        with identity.engine.connect() as db:
            assert db.scalar(text("SELECT count(*) FROM consent_records")) == 0
            row = db.execute(
                text("SELECT attempts,consumed_at FROM otp_challenges WHERE id=:id"),
                {"id": body.challenge_id},
            ).one()
            assert row == (0, None)


@pytest.mark.parametrize("bound", [False, True])
def test_open_guardian_wrong_code_still_counts_without_changing_expiry(bound):
    with credential_source() as (proof, identity, _, now):
        _, tokens = minor(identity, proof)
        if bound:
            register(identity, "guardian@example.invalid")
        now[0] += timedelta(seconds=61)
        body = guardian_request(identity, tokens).model_copy(update={"code": "000000"})
        query = text("SELECT attempts,consumed_at,expires_at FROM otp_challenges WHERE id=:id")
        with identity.engine.connect() as db:
            before = db.execute(query, {"id": body.challenge_id}).one()
        with pytest.raises(IdentityError, match="OTP_INVALID"):
            identity.consent(tokens.access_token, body, uuid4(), str(uuid4()))
        with identity.engine.connect() as db:
            assert db.execute(query, {"id": body.challenge_id}).one() == (
                before.attempts + 1,
                None,
                before.expires_at,
            )
            assert db.scalar(text("SELECT count(*) FROM consent_records")) == 0


def test_guardian_gate_precedes_challenge_lock_and_rechecks_committed_closure(monkeypatch):
    with credential_source() as (proof, identity, _, now):
        guardian, _ = register(identity, "guardian@example.invalid")
        _, tokens = minor(identity, proof)
        now[0] += timedelta(seconds=61)
        body = guardian_request(identity, tokens)
        reached, backend = Event(), []
        import services.identity as implementation

        original = implementation.coordinate

        def observe(db, subject):
            if subject == guardian:
                backend.append(db.scalar(text("SELECT pg_backend_pid()")))
                reached.set()
            original(db, subject)

        monkeypatch.setattr(implementation, "coordinate", observe)
        with ThreadPoolExecutor(max_workers=1) as pool:
            with identity.engine.begin() as db:
                assert db.scalar(EXCLUSIVE, {"subject": guardian}) is True
                future = pool.submit(
                    identity.consent, tokens.access_token, body, uuid4(), str(uuid4())
                )
                assert reached.wait(5)
                wait_for_gate(identity.engine, backend[0], future)
                # This NOWAIT succeeds only if the blocked consumer has not locked the code.
                assert (
                    db.scalar(
                        text("SELECT id FROM otp_challenges WHERE id=:id FOR UPDATE NOWAIT"),
                        {"id": body.challenge_id},
                    )
                    == body.challenge_id
                )
                # Exact owned future-state fixture, not a closure capability or authorization.
                proof.verify()
                db.execute(text("ALTER TABLE public.users DISABLE TRIGGER users_erasure_closure"))
                db.execute(
                    text(
                        "UPDATE users SET status='DISABLED',closed_at=clock_timestamp() "
                        "WHERE id=:id"
                    ),
                    {"id": guardian},
                )
                db.execute(text("ALTER TABLE public.users ENABLE TRIGGER users_erasure_closure"))
            with pytest.raises(IdentityError, match="OTP_INVALID"):
                future.result(timeout=5)
        with identity.engine.connect() as db:
            assert db.scalar(text("SELECT count(*) FROM consent_records")) == 0
            assert db.execute(
                text("SELECT attempts,consumed_at FROM otp_challenges WHERE id=:id"),
                {"id": body.challenge_id},
            ).one() == (0, None)
            assert db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) == 0
            assert (
                db.scalar(
                    text(
                        "SELECT tgenabled FROM pg_catalog.pg_trigger "
                        "WHERE tgrelid='public.users'::regclass AND tgname='users_erasure_closure'"
                    )
                )
                == "O"
            )
