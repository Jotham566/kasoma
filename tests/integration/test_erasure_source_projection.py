"""Read-only source sealing and malicious relational inputs; no executor/erasure."""

from contextlib import contextmanager
from uuid import UUID, uuid4

import pytest
from psycopg import sql
from sqlalchemy import text
from sqlalchemy.orm import Session

from services.domain.identity import IdentityEvent
from services.erasure_manifest import BASELINE
from services.erasure_sources import OwnershipConflict, fingerprint, validate_relations
from services.identity_contracts import OTPRequest, OTPVerify
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_flags import report, saved, triage

assessment = assessment_fixture

pytestmark = pytest.mark.integration
KEY = b"synthetic-purpose-key-only-32bytes!"


@contextmanager
def snapshot(service):
    with service.engine.connect().execution_options(isolation_level="REPEATABLE READ") as db:
        with db.begin():
            db.execute(text("SET TRANSACTION READ ONLY"))
            yield db


def register(service, address):
    challenge = service.request_otp(OTPRequest(identifier=address, device_id=uuid4()), "test", None)
    credentials = service.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    return service.me(credentials.access_token).id


def test_all_source_queries_are_scoped_stable_and_uncapped(identity):
    service, *_ = identity
    subject = register(service, "source-owner@example.invalid")
    with service.engine.connect() as db:
        with pytest.raises(OwnershipConflict):
            fingerprint(db, subject, KEY)
    with snapshot(service) as db:
        initial = fingerprint(db, subject, KEY)
        assert initial.semantic_clearance is False
        assert initial.counts["users"] == initial.counts["auth_sessions"] == 1
        assert initial.counts["otp_challenges"] == 0  # Unbound LOGIN has no account ownership.
        assert initial.counts["identity_rate_buckets"] == 0
        with pytest.raises(TypeError):
            initial.counts["users"] = 0
        assert (
            fingerprint(db, subject, b"other-purpose-key-only-32bytes!!!").version
            != initial.version
        )
    register(service, "other-source-owner@example.invalid")
    with snapshot(service) as db:
        assert fingerprint(db, subject, KEY).version == initial.version
    with Session(service.engine) as db, db.begin():
        db.add_all(
            [
                IdentityEvent(
                    id=uuid4(),
                    user_id=subject,
                    type="registration.completed",
                    version=1,
                    payload={"request_id": str(uuid4())},
                    created_at=service.clock(),
                )
                for _ in range(10_001)
            ]
        )
    with snapshot(service) as db:
        changed = fingerprint(db, subject, KEY)
        assert (
            changed.counts["identity_outbox_events"]
            == initial.counts["identity_outbox_events"] + 10_001
        )
        assert changed.version != initial.version
        assert "source-owner@" not in repr(changed)
        assert KEY.decode() not in repr(changed)


def test_incoming_and_outgoing_cross_owner_rows_are_rejected_without_disabling_guards(identity):
    service, *_ = identity
    # A separate unguarded mirror represents corrupt input. Original guards, rows
    # and FKs are untouched; only this invocation's disposable source owns the mirror.
    mirror = "identity_test_" + uuid4().hex
    with service.engine.begin() as db:
        original = db.scalar(text("SELECT current_schema()"))
        db.execute(text(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(mirror)).as_string()))
        for name in BASELINE:
            db.execute(
                text(
                    sql.SQL("CREATE TABLE {}.{} (LIKE {}.{} INCLUDING ALL)")
                    .format(
                        sql.Identifier(mirror),
                        sql.Identifier(name),
                        sql.Identifier(original),
                        sql.Identifier(name),
                    )
                    .as_string()
                )
            )
        alice, bob, session, item, attempt = [uuid4() for _ in range(5)]

        def execute(query, params):
            db.execute(text(query.replace("__S__", sql.Identifier(mirror).as_string())), params)

        execute(
            """INSERT INTO __S__.users(id,status,created_at)
               VALUES(:alice,'ACTIVE',clock_timestamp()),(:bob,'ACTIVE',clock_timestamp())""",
            {"alice": alice, "bob": bob},
        )
        execute(
            """INSERT INTO __S__.assessment_sessions(id,learner_id,subject_id,topic_id,
                status,item_count,reason,plan_version,started_at,expires_at)
               VALUES(:id,:owner,:subject,:topic,'ACTIVE',5,'synthetic','synthetic',
                 clock_timestamp(),clock_timestamp()+interval '1 hour')""",
            {"id": session, "owner": bob, "subject": uuid4(), "topic": uuid4()},
        )
        execute(
            """INSERT INTO __S__.session_items(id,session_id,item_version_id,position,reason)
               VALUES(:id,:session,:version,1,'synthetic')""",
            {"id": item, "session": session, "version": uuid4()},
        )
        execute(
            """INSERT INTO __S__.attempts(id,learner_id,session_item_id,item_version_id,
               submitted_at,hint_count,channel,choice_id)
               VALUES(:id,:owner,:item,:version,clock_timestamp(),0,'WEB','A')""",
            {"id": attempt, "owner": alice, "item": item, "version": uuid4()},
        )
        for subject in [alice, bob]:
            with pytest.raises(OwnershipConflict):
                validate_relations(db, subject, mirror)


def test_revoked_staff_role_is_not_treated_as_learner_ownership(identity):
    from services.staff import provision

    service, *_ = identity
    email = "former-staff-source@example.invalid"
    subject = register(service, email)
    provision(service, email, "SUPPORT_READONLY")
    provision(service, email, "SUPPORT_READONLY", revoke=True)
    with snapshot(service) as db:
        with pytest.raises(OwnershipConflict, match="STAFF_PROVENANCE_REQUIRES_REVIEW"):
            fingerprint(db, subject, KEY)


def test_own_report_and_independent_triage_are_not_subject_staff_provenance(assessment):
    service, client, actors, *_ = assessment
    grade = saved(assessment)
    subject = service.me(actors["learner"]["Authorization"].removeprefix("Bearer ")).id
    with snapshot(service) as db:
        before = fingerprint(db, subject, KEY)
    response = report(client, actors["learner"], grade["attempt_id"])
    assert response.status_code == 201, response.text
    flag_id = UUID(response.json()["id"])
    with snapshot(service) as db:
        reported = fingerprint(db, subject, KEY)
        assert reported.semantic_clearance is False
        assert reported.counts["content_flags"] == reported.counts["content_flag_history"] == 1
        assert reported.counts["content_flag_receipts"] == 1
        assert reported.counts["items"] == reported.counts["item_versions"] == 0
        assert reported.version != before.version
    detail = client.get(f"/api/v1/admin/content-flags/{flag_id}", headers=actors["reviewer"])
    assert detail.status_code == 200, detail.text
    changed = triage(client, actors["reviewer"], detail.json())
    assert changed.status_code == 200, changed.text
    with snapshot(service) as db:
        reviewed = fingerprint(db, subject, KEY)
        assert reviewed.counts["content_flag_history"] == 2
        assert reviewed.counts["content_flag_receipts"] == 2
        assert reviewed.version != reported.version
        assert reviewed.semantic_clearance is False
