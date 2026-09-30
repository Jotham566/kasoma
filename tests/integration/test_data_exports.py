"""FR-ID-006 exports: owned, atomic, bounded and unable to unseal diagnostics."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.data_exports import download, expire
from services.domain.data_requests import DataExport, DataRequest
from services.identity_contracts import OTPRequest, OTPVerify
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_data_requests import create
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture
from tests.integration.test_diagnostics import start as start_diagnostic
from tests.integration.test_diagnostics import (
    submit,
)

pytestmark = pytest.mark.integration
assessment = assessment_fixture
diagnostic = diagnostic_fixture


def export(client, headers, target, key=None):
    return client.post(
        f"/api/v1/me/data-requests/{target}/export",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={},
    )


def fresh(identity):
    challenge = identity.request_otp(
        OTPRequest(identifier="learner@example.invalid", device_id=uuid4()), "export", None
    )
    credentials = identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    )
    return {"Authorization": "Bearer " + credentials.access_token}


def test_owned_export_atomic_completion_retry_and_new_request(content):
    identity, client, actors, _ = content
    headers = actors["learner"]
    creation_key = str(uuid4())
    saved = create(client, headers, key=creation_key).json()
    target, key = saved["id"], str(uuid4())
    result = export(client, headers, target, key)
    assert result.status_code == 200, result.text
    bundle = result.json()
    assert bundle["records"]["identifiers"][0]["value"] == "learner@example.invalid"
    assert bundle["exclusions"] and bundle["format_version"] == "kasoma-personal-export-v1"
    assert result.headers["cache-control"] == "no-store"
    assert (
        result.headers["content-disposition"]
        == f'attachment; filename="kasoma-export-{target}.json"'
    )
    assert export(client, headers, target, key).json() == bundle
    assert export(client, headers, target).json() == bundle
    assert export(client, headers, target, creation_key).status_code == 409
    view = client.get(f"/api/v1/me/data-requests/{target}", headers=headers).json()
    assert view["status"] == "COMPLETED" and view["retention_due_at"].startswith("2032-09-23")
    assert view["download_expires_at"].startswith("2026-09-24")
    assert create(client, headers, key=creation_key).json()["id"] == target
    assert create(client, headers).json()["id"] != target
    with Session(identity.engine) as db:
        artifact = db.get(DataExport, UUID(target))
        assert "learner@example.invalid" not in artifact.encrypted_payload
        assert identity.decrypt(artifact.encrypted_payload)
        assert db.scalar(select(func.count()).select_from(DataExport)) == 1
    for forbidden in ["admin@example.invalid", "246810", "token_hash", "authenticated_at"]:
        assert forbidden not in result.text
    for statement in [
        "UPDATE data_exports SET encrypted_payload='tampered'",
        "UPDATE data_subject_requests SET retention_due_at=completed_at",
        "DELETE FROM data_subject_requests",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as conn:
            conn.execute(text(statement))


def test_authorization_fresh_identity_expiry_and_idempotent_sweep(content):
    identity, client, actors, _ = content
    headers = actors["learner"]
    target = create(client, headers).json()["id"]
    assert export(client, {}, target).status_code == 401
    for role in ["other", "admin"]:
        assert export(client, actors[role], target).status_code == 404
    assert export(client, headers, str(uuid4())).status_code == 404
    deletion = create(client, headers, "DELETE").json()["id"]
    assert export(client, headers, deletion).status_code == 409
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=10)
    assert export(client, headers, target).json()["error"]["code"] == "REAUTH_REQUIRED"
    headers = fresh(identity)
    assert export(client, headers, target).status_code == 200
    assert expire(identity, uuid4()) == 0
    identity.clock = lambda: now + timedelta(days=2)
    headers = fresh(identity)
    assert export(client, headers, target).json()["error"]["code"] == "EXPORT_EXPIRED"
    assert expire(identity, uuid4()) == 1
    assert expire(identity, uuid4()) == 0
    assert export(client, headers, target).status_code == 410
    assert (
        client.get(f"/api/v1/me/data-requests/{target}", headers=headers).json()["status"]
        == "COMPLETED"
    )
    assert client.post("/api/v1/auth/logout-all", headers=headers).status_code == 204
    assert export(client, headers, target).status_code == 401


def test_concurrent_retry_and_failure_roll_back_artifact_and_completion(content, monkeypatch):
    identity, client, actors, _ = content
    headers = actors["learner"]
    target = UUID(create(client, headers).json()["id"])
    token = headers["Authorization"][7:]
    original = identity.event

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic event write failure")

    monkeypatch.setattr(identity, "event", fail)
    assert export(client, headers, target).status_code == 500
    with Session(identity.engine) as db:
        assert db.get(DataExport, target) is None
        assert db.get(DataRequest, target).completed_at is None
    monkeypatch.setattr(identity, "event", original)
    key = uuid4()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda _: download(identity, token, target, key, uuid4()), range(2))
        )
    assert results[0] == results[1]


@pytest.mark.parametrize("bound", ["bytes", "records"])
def test_bounds_fail_without_partial_completion(content, monkeypatch, bound):
    import services.data_export_projection as projection
    import services.data_exports as exports

    identity, client, actors, _ = content
    target = create(client, actors["learner"]).json()["id"]
    if bound == "bytes":
        monkeypatch.setattr(exports, "MAX_BYTES", 1)
    else:
        monkeypatch.setattr(projection, "MAX_RECORDS", 0)
    result = export(client, actors["learner"], target)
    assert result.status_code == 409, result.text
    assert result.json()["error"]["code"] == "EXPORT_LIMIT_REACHED"
    with Session(identity.engine) as db:
        assert db.get(DataExport, UUID(target)) is None
        assert db.get(DataRequest, UUID(target)).completed_at is None


def test_released_answers_grades_mastery_without_content_keys_after_withdrawal(assessment):
    identity, client, actors, _, _, plan = assessment
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    result = answer(client, headers, session, item)
    assert result.status_code == 200
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "WITHDRAW",
                "policy_version": identity.settings.consent_policy_version,
                "affirmative": True,
            },
        ).status_code
        == 200
    )
    target = create(client, headers).json()["id"]
    exported = export(client, headers, target)
    assert exported.status_code == 200, exported.text
    records = exported.json()["records"]
    assert records["profile"][0]["display_name"] == "Synthetic learner"
    assert len(records["answers"]) == len(records["grades"]) == 1
    assert records["grades"][0]["score"] == result.json()["score"]
    assert records["mastery_evidence"] and records["mastery_history"]
    for secret in [
        "correct_choice_id",
        "worked_solution",
        "remediation",
        "candidate_snapshot",
        "author@example.invalid",
    ]:
        assert secret not in exported.text


def test_diagnostic_seal_and_frozen_snapshot_until_explicit_new_request(diagnostic):
    _, client, actors, body = diagnostic
    headers = actors["learner"]
    session = start_diagnostic(client, headers, body["subject_id"]).json()["id"]
    assert submit(client, headers, session, next_item(client, headers, session)).status_code == 200
    target = create(client, headers).json()["id"]
    result = export(client, headers, target)
    assert result.status_code == 200, result.text
    first = result.json()
    records = first["records"]
    assert len(records["answers"]) == 1 and not records["answers"][0]["grade_released"]
    for section in ["grades", "mastery_evidence", "mastery_estimates", "mastery_history"]:
        assert records[section] == []
    for _ in range(14):
        assert (
            submit(client, headers, session, next_item(client, headers, session)).status_code == 200
        )
    assert export(client, headers, target).json() == first
    new = create(client, headers).json()["id"]
    completed = export(client, headers, new)
    assert completed.status_code == 200, completed.text
    assert len(completed.json()["records"]["grades"]) == 15
    assert completed.json()["records"]["mastery_history"]
    released = {a["id"] for a in completed.json()["records"]["answers"]}
    following = start_diagnostic(client, headers, body["subject_id"]).json()["id"]
    assert (
        submit(client, headers, following, next_item(client, headers, following)).status_code == 200
    )
    assert client.post(f"/api/v1/sessions/{following}/abandon", headers=headers).status_code == 200
    mixed = export(client, headers, create(client, headers).json()["id"]).json()["records"]
    assert len(mixed["answers"]) == 16 and len(mixed["grades"]) == 15
    assert len(mixed["mastery_evidence"]) == 15
    for estimate in mixed["mastery_estimates"] + mixed["mastery_history"]:
        assert set(estimate["input_attempt_ids"]) <= released


def test_guardian_evidence_is_not_decrypted_or_disclosed(content, monkeypatch):
    from tests.integration.test_identity import consent, profile, request_code

    identity, client, actors, _ = content
    headers = actors["learner"]
    profile(client, headers, "2010-01-01")
    assert consent(client, headers, "ASSENT").status_code == 200
    challenge = request_code(client, "guardian@example.invalid", "GUARDIAN", headers)
    assert (
        consent(
            client,
            headers,
            "GUARDIAN",
            guardian_name="Synthetic guardian",
            guardian_relationship="Parent",
            challenge_id=challenge,
            code="246810",
        ).status_code
        == 200
    )
    original = identity.decrypt

    def guarded(ciphertext):
        value = original(ciphertext)
        assert "guardian@example.invalid" not in value
        assert "Synthetic guardian" not in value
        return value

    monkeypatch.setattr(identity, "decrypt", guarded)
    target = create(client, headers).json()["id"]
    result = export(client, headers, target)
    assert result.status_code == 200, result.text
    assert "guardian@example.invalid" not in result.text and "Synthetic guardian" not in result.text
    assert any(c["consent_type"] == "GUARDIAN" for c in result.json()["records"]["consents"])


def test_database_blocks_early_copy_removal_and_orphan_completion(content):
    from datetime import UTC, datetime

    from apps.worker.main import make_worker

    identity, client, _, _ = content
    # SQL guards use the database clock, so this fixture explicitly tracks wall time.
    now = datetime.now(UTC)
    identity.clock = lambda: now
    headers = fresh(identity)
    target = create(client, headers).json()["id"]
    assert export(client, headers, target).status_code == 200
    with pytest.raises(DBAPIError, match="Export not expired"), identity.engine.begin() as conn:
        conn.execute(text("DELETE FROM data_exports"))
    pending = create(client, headers).json()["id"]
    with (
        pytest.raises(DBAPIError, match="Invalid export completion"),
        identity.engine.begin() as conn,
    ):
        conn.execute(
            text("""UPDATE data_subject_requests SET completed_at=created_at,
          retention_due_at=created_at+interval '6 years',export_digest=:digest WHERE id=:id"""),
            {"id": UUID(pending), "digest": "0" * 64},
        )
    with (
        pytest.raises(DBAPIError, match="Export requires atomic completion"),
        identity.engine.begin() as conn,
    ):
        conn.execute(
            text("""INSERT INTO data_exports
          SELECT id,'opaque',:digest,created_at,created_at+interval '24 hours'
          FROM data_subject_requests WHERE id=:id"""),
            {"id": UUID(pending), "digest": "0" * 64},
        )
    worker = make_worker(identity.settings)
    try:
        assert worker.tasks["kasoma.expire_exports"].run() == 0
    finally:
        worker.close()
