"""FR-GRD-003/004 / FR-ID-006: complete synthetic learner grading integration."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scripts.grading_fixtures import unapproved_band
from services.assessment import AssessmentService
from services.assessment_contracts import StartRevision
from services.domain.assessment import AssessmentReceipt, Attempt, Grade, SessionItem
from services.domain.grading_work import GradingWorkRow
from services.domain.mastery import MasteryEvidence
from services.grading_band_store import register
from services.grading_work_store import claim_next, finish_neutral
from services.short_text_eligibility import GradingScope
from services.short_text_policy import ShortTextPolicy
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_content import create, review, submit
from tests.integration.test_grading_bands import activate_synthetic
from tests.integration.test_reviewed_rubrics import document

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def test_objective_plan_remains_usable_with_short_text_storage(assessment):
    identity, _, actors, _, _, plan = assessment
    token = actors["learner"]["Authorization"].removeprefix("Bearer ")
    result = AssessmentService(identity).start(
        token, StartRevision.model_validate(plan), uuid4(), uuid4()
    )
    assert result.item_count == 5 and result.answered_count == 0


@pytest.fixture
def short_text(content, request):
    identity, client, actors, body = content
    versions = []
    for i in range(getattr(request, "param", 5)):
        draft = create(
            client,
            actors,
            body
            | {
                "document": document(body)
                | {"title": f"Synthetic rubric {i}", "difficulty": "STANDARD"}
            },
        )
        approved = review(client, actors, submit(client, actors, draft))
        assert approved.status_code == 200, approved.text
        versions.append(approved.json()["id"])
    profile = client.patch(
        "/api/v1/me",
        headers=actors["learner"],
        json={
            "display_name": "Synthetic rubric learner",
            "birth_date": "2000-01-01",
            "subject_ids": [body["subject_id"]],
        },
    )
    assert profile.status_code == 200, profile.text
    consent = client.post(
        "/api/v1/me/consents",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "SELF",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert consent.status_code == 200, consent.text
    settings = identity.settings
    band = unapproved_band(
        GradingScope(
            subject_id=UUID(body["subject_id"]),
            topic_id=UUID(body["document"]["topic_id"]),
            language="en",
            model_version=settings.short_text_model_version,
            prompt_version=settings.short_text_prompt_version,
            configuration_version=settings.short_text_configuration_version,
        )
    ).model_copy(
        update={
            "approval_id": uuid4(),
            "approved_at": identity.clock(),
            "subgroup_review": "APPROVED",
        }
    )
    with Session(identity.engine) as db, db.begin():
        register(db, band, identity.clock())
        activate_synthetic(db, band, identity.clock())
    settings.short_text_enabled = True
    settings.model_provider = "fake"
    # Isolated synthetic report authority, deliberately absent from normal startup.
    policy = ShortTextPolicy(identity, lambda candidate: candidate.id == band.id)
    client.app.state.short_text_policy = policy
    client.app.state.grading_wakeup = lambda settings, request_id: None
    plan = {"subject_id": body["subject_id"], "topic_id": body["document"]["topic_id"]}
    return identity, client, actors, plan, policy, band


def start_short(source):
    _, client, actors, plan, _, _ = source
    started = client.post(
        "/api/v1/revision-sessions",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json=plan,
    )
    assert started.status_code == 201, started.text
    session = started.json()["id"]
    item = client.get(f"/api/v1/sessions/{session}/next-item", headers=actors["learner"])
    assert item.status_code == 200, item.text
    assert item.json()["response_spec"] == {"type": "SHORT_TEXT", "maximum_characters": 2000}
    assert "criterion_text" not in item.text and "acceptable_evidence" not in item.text
    return session, item.json()


def save_short(source, session, item, key=None):
    _, client, actors, *_ = source
    return client.post(
        f"/api/v1/sessions/{session}/attempts",
        headers=actors["learner"] | {"Idempotency-Key": key or str(uuid4())},
        json={
            "session_item_id": item["session_item_id"],
            "response": {"type": "SHORT_TEXT", "text": "  Alpha\n"},
        },
    )


def test_pinned_encrypted_submission_pending_replay_resume_and_owned_grade(short_text):
    identity, client, actors, _, _, band = short_text
    session, item = start_short(short_text)
    key = str(uuid4())
    saved = save_short(short_text, session, item, key)
    assert saved.status_code == 200, saved.text
    result = saved.json()
    assert result["status"] == "PENDING" and "score" not in result
    assert save_short(short_text, session, item, key).json() == result
    assert save_short(short_text, session, item).status_code == 409
    attempt_id = UUID(result["attempt_id"])
    with Session(identity.engine) as db:
        attempt = db.get(Attempt, attempt_id)
        assert "Alpha" not in str(attempt.response)
        assert set(attempt.response) == {"type", "ciphertext", "rubric_version_id"}
        assert db.get(SessionItem, attempt.session_item_id).grading_band_id == band.id
        assert db.get(GradingWorkRow, attempt_id).status == "QUEUED"
        assert db.get(Grade, attempt_id) is None
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(AssessmentReceipt)
                .where(AssessmentReceipt.attempt_id == attempt_id)
            )
            == 1
        )
    own = client.get(result["poll_url"], headers=actors["learner"])
    assert own.status_code == 200 and own.json() == result
    profile = client.patch(
        "/api/v1/me",
        headers=actors["other"],
        json={
            "display_name": "Another synthetic learner",
            "birth_date": "2000-01-01",
            "subject_ids": [short_text[3]["subject_id"]],
        },
    )
    assert profile.status_code == 200, profile.text
    consent = client.post(
        "/api/v1/me/consents",
        headers=actors["other"] | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "SELF",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert consent.status_code == 200, consent.text
    assert client.get(result["poll_url"], headers=actors["other"]).status_code == 404
    resumed = client.get(f"/api/v1/sessions/{session}", headers=actors["learner"])
    assert resumed.json()["answered_count"] == 1
    assert resumed.json()["answers"][0]["grade"] == result


def test_neutral_outcome_has_no_grade_or_mastery_and_replays_original_receipt(short_text):
    identity, client, actors, *_ = short_text
    session, item = start_short(short_text)
    key = str(uuid4())
    saved = save_short(short_text, session, item, key)
    assert saved.status_code == 200, saved.text
    attempt_id = UUID(saved.json()["attempt_id"])
    with Session(identity.engine) as db, db.begin():
        claimed = claim_next(db, identity.clock())
        finish_neutral(db, attempt_id, claimed.claim_id, identity.clock())
    neutral = client.get(saved.json()["poll_url"], headers=actors["learner"])
    assert neutral.status_code == 200, neutral.text
    assert neutral.json()["status"] == "LOW_CONFIDENCE"
    assert neutral.json()["fallback"] == {"kind": "REQUEST_REVIEW"}
    assert not {"score", "points_awarded", "confidence", "feedback"} & neutral.json().keys()
    assert save_short(short_text, session, item, key).json() == neutral.json()
    with Session(identity.engine) as db:
        assert db.get(Grade, attempt_id) is None
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0


def test_enabled_metadata_without_report_authority_does_not_allow_selection(short_text):
    identity, client, actors, plan, _, _ = short_text
    client.app.state.short_text_policy = ShortTextPolicy(identity)
    response = client.post(
        "/api/v1/revision-sessions",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json=plan,
    )
    assert (
        response.status_code == 409 and response.json()["error"]["code"] == "INSUFFICIENT_CONTENT"
    )


def test_failed_wakeup_does_not_undo_saved_attempt_or_original_receipt(short_text, caplog):
    identity, client, actors, *_ = short_text

    def unavailable(*args):
        raise RuntimeError("CANARY synthetic broker secret")

    client.app.state.grading_wakeup = unavailable
    session, item = start_short(short_text)
    key = str(uuid4())
    saved = save_short(short_text, session, item, key)
    assert saved.status_code == 200 and saved.json()["status"] == "PENDING"
    assert save_short(short_text, session, item, key).json() == saved.json()
    assert client.get(saved.json()["poll_url"], headers=actors["learner"]).json() == saved.json()
    with Session(identity.engine) as db:
        assert db.get(GradingWorkRow, UUID(saved.json()["attempt_id"])).status == "QUEUED"
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
        assert (
            db.scalar(
                select(func.count())
                .select_from(AssessmentReceipt)
                .where(AssessmentReceipt.attempt_id == UUID(saved.json()["attempt_id"]))
            )
            == 1
        )
    assert "grading.wakeup_failed" in caplog.text and "CANARY" not in caplog.text


def test_saved_feedback_has_an_account_bound_polling_limit(short_text):
    identity, client, actors, *_ = short_text
    session, item = start_short(short_text)
    saved = save_short(short_text, session, item).json()
    with Session(identity.engine) as db, db.begin():
        owner = db.get(Attempt, UUID(saved["attempt_id"])).learner_id
        for _ in range(120):
            assert identity.rate(db, "short-text-feedback:" + str(owner), 120, 60)
    denied = client.get(saved["poll_url"], headers=actors["learner"])
    assert denied.status_code == 429 and denied.json()["error"]["code"] == "USAGE_LIMIT_REACHED"
    clock = identity.clock
    identity.clock = lambda: clock() + timedelta(seconds=61)
    allowed = client.get(saved["poll_url"], headers=actors["learner"])
    assert allowed.status_code == 200 and allowed.json()["status"] == "PENDING"
