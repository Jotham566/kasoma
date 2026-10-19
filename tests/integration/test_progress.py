"""FR-MST-004/005: owned, consented, read-only progress and cursor history."""

from datetime import UTC, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from services.domain.assessment import AssessmentSession
from services.domain.mastery import MasteryEvidence, MasteryHistory
from services.identity_contracts import ConsentInput
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture
from tests.integration.test_diagnostics import start as start_diagnostic
from tests.integration.test_diagnostics import submit as submit_diagnostic
from tests.integration.test_identity import login

assessment = assessment_fixture
diagnostic = diagnostic_fixture
pytestmark = pytest.mark.integration


def read(client, headers, subject):
    response = client.get("/api/v1/me/progress", headers=headers, params={"subject_id": subject})
    assert response.status_code == 200, response.text
    return response.json()


def test_progress_coverage_history_and_read_immutability(assessment, monkeypatch):
    from services import progress_engine

    actual = progress_engine.estimate
    calls = []

    def observed(concept, competency, evidence, at):
        calls.append((concept, competency, tuple(e.input_hash for e in evidence), at))
        return actual(concept, competency, evidence, at)

    monkeypatch.setattr(progress_engine, "estimate", observed)
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    subject = body["subject_id"]
    before = read(client, headers, subject)
    assert before["practice_activity"]["days_practised"] == 0
    assert before["subject"]["confidence"] == 0
    assert before["subject"]["display_state"] == "NOT_ENOUGH_EVIDENCE"
    assert len(before["topics"]) == 3
    assert before["next_action"]["kind"] == "START_DIAGNOSTIC"
    assert client.get("/api/v1/me/session-history", headers=headers).json()["data"] == []
    session = start(client, headers, plan).json()["id"]
    assert answer(client, headers, session, next_item(client, headers, session)).status_code == 200
    calls.clear()
    after = read(client, headers, subject)
    assert calls and len(calls) == len(set(calls))
    first_read_calls = len(calls)
    assert after["practice_activity"]["days_practised"] == 1
    assert after["subject"]["evidence_count"] == 1
    assert after["subject"]["display_state"] == "NOT_ENOUGH_EVIDENCE"
    assert sum(t["evidence_count"] for t in after["topics"]) == 1
    with Session(identity.engine) as db:
        count = db.scalar(select(func.count()).select_from(MasteryHistory))
    calls.clear()
    assert read(client, headers, subject) == after
    assert len(calls) == first_read_calls  # Fresh authorization/read, fresh replay context.
    history = client.get("/api/v1/me/session-history", headers=headers).json()
    assert history["data"][0]["id"] == session
    assert history["data"][0]["answered_count"] == 1
    assert history["data"][0]["kind"] == "REVISION"
    assert (
        not {"score", "feedback", "prompt", "response", "selection_snapshot"}
        & history["data"][0].keys()
    )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(MasteryHistory)) == count
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == count
    # Recency is evaluated at read time without updating materialized evidence.
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=2)
    assert read(client, headers, subject)["subject"]["confidence"] < after["subject"]["confidence"]


def test_history_cursor_ties_tampering_filter_and_expiry(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    identifiers = []
    for _ in range(3):
        session = start(client, headers, plan).json()["id"]
        identifiers.append(session)
        assert (
            client.post(f"/api/v1/sessions/{session}/abandon", headers=headers).status_code == 200
        )
    active = start(client, headers, plan).json()["id"]
    identifiers.append(active)
    with identity.engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE assessment_sessions SET expires_at=started_at + interval '1 minute' "
                "WHERE status='ACTIVE'"
            )
        )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=2)
    page = client.get("/api/v1/me/session-history", headers=headers, params={"limit": 2}).json()
    assert page["next_cursor"]
    second = client.get(
        "/api/v1/me/session-history",
        headers=headers,
        params={"limit": 2, "cursor": page["next_cursor"]},
    ).json()
    assert second["next_cursor"] is None
    entries = page["data"] + second["data"]
    assert [e["id"] for e in entries] == sorted(identifiers, reverse=True)
    assert next(e for e in entries if e["id"] == active)["status"] == "EXPIRED"
    with Session(identity.engine) as db:
        assert db.get(AssessmentSession, UUID(active)).status == "ACTIVE"
    for params in [
        {"cursor": page["next_cursor"] + "x"},
        {"cursor": "invalid"},
        {"cursor": page["next_cursor"], "subject_id": body["subject_id"]},
        {"limit": 0},
        {"limit": 51},
    ]:
        assert (
            client.get("/api/v1/me/session-history", headers=headers, params=params).status_code
            == 422
        )


def test_auth_current_consent_subject_and_learner_isolation(assessment):
    identity, client, actors, body, versions, plan = assessment
    headers = actors["learner"]
    subject = body["subject_id"]
    start(client, headers, plan)
    for path in [f"/api/v1/me/progress?subject_id={subject}", "/api/v1/me/session-history"]:
        assert client.get(path).status_code == 401
        assert client.get(path, headers=actors["other"]).status_code == 403
    other = actors["other"]
    client.patch(
        "/api/v1/me",
        headers=other,
        json={
            "display_name": "Synthetic other",
            "birth_date": "2000-01-01",
            "subject_ids": [subject],
        },
    )
    client.post(
        "/api/v1/me/consents",
        headers=other | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "SELF",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    other_progress = read(client, other, subject)
    assert other_progress["subject"]["evidence_count"] == 0
    assert other_progress["practice_activity"]["days_practised"] == 0
    assert client.get("/api/v1/me/session-history", headers=other).json()["data"] == []
    for path in ["/api/v1/me/progress", "/api/v1/me/session-history"]:
        assert (
            client.get(path, headers=headers, params={"subject_id": str(uuid4())}).status_code
            == 403
        )
    identity.consent(
        headers["Authorization"][7:],
        ConsentInput(
            consent_type="WITHDRAW",
            affirmative=True,
            policy_version=identity.settings.consent_policy_version,
        ),
        uuid4(),
        str(uuid4()),
    )
    for path in [f"/api/v1/me/progress?subject_id={subject}", "/api/v1/me/session-history"]:
        assert client.get(path, headers=headers).status_code == 403


@pytest.mark.parametrize("ending", ["COMPLETED", "ABANDONED", "EXPIRED"])
def test_unfinished_diagnostic_scores_stay_sealed(diagnostic, ending):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    subject = body["subject_id"]
    baseline = read(client, headers, subject)["subject"]
    session = start_diagnostic(client, headers, subject).json()["id"]
    for index in range(15 if ending == "COMPLETED" else 1):
        item = next_item(client, headers, session)
        assert submit_diagnostic(client, headers, session, item).status_code == 200
        view = read(client, headers, subject)
        if index < 14:
            assert view["practice_activity"]["days_practised"] == 0
            assert view["subject"] == baseline
            assert view["next_action"]["kind"] == "CONTINUE_DIAGNOSTIC"
        else:
            assert view["practice_activity"]["days_practised"] == 1
            assert view["subject"]["evidence_count"] == 15
        entry = client.get("/api/v1/me/session-history", headers=headers).json()["data"][0]
        assert entry["answered_count"] == index + 1
        assert "score" not in entry

    if ending == "ABANDONED":
        assert (
            client.post(f"/api/v1/sessions/{session}/abandon", headers=headers).status_code == 200
        )
    elif ending == "EXPIRED":
        with identity.engine.begin() as conn:
            conn.execute(
                text("UPDATE assessment_sessions SET expires_at=started_at + interval '1 minute'")
            )
        now = identity.clock()
        identity.clock = lambda: now + timedelta(minutes=2)
    if ending != "COMPLETED":
        view = read(client, headers, subject)
        assert view["practice_activity"]["days_practised"] == 0
        assert view["subject"]["evidence_count"] == 0
        assert view["subject"]["confidence"] == 0
        assert view["next_action"]["kind"] == "START_DIAGNOSTIC"


def test_practice_dates_follow_kampala_midnight_and_selected_subject(assessment):
    identity, client, actors, body, _, plan = assessment
    subjects = [str(subject.id) for subject in identity.subjects()]
    response = client.patch(
        "/api/v1/me",
        headers=actors["learner"],
        json={
            "display_name": "Synthetic learner",
            "birth_date": "2000-01-01",
            "subject_ids": subjects,
        },
    )
    assert response.status_code == 200
    at = identity.clock().astimezone(UTC).replace(hour=20, minute=59, second=0, microsecond=0)
    identity.clock = lambda: at
    headers, _ = login(client)
    session = start(client, headers, plan).json()["id"]
    assert answer(client, headers, session, next_item(client, headers, session)).status_code == 200
    assert read(client, headers, body["subject_id"])["practice_activity"]["days_practised"] == 1
    identity.clock = lambda: at + timedelta(minutes=2)
    wrong = answer(client, headers, session, next_item(client, headers, session), choice="B")
    assert wrong.status_code == 200 and wrong.json()["score"] == 0
    activity = read(client, headers, body["subject_id"])["practice_activity"]
    assert activity["days_practised"] == 2
    assert activity["window_end"] == (at + timedelta(days=1)).date().isoformat()
    other = next(subject for subject in subjects if subject != body["subject_id"])
    assert read(client, headers, other)["practice_activity"]["days_practised"] == 0
