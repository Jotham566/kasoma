"""Synthetic independent expert completion, privacy boundaries and disablement."""

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import timedelta
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import SubmitAnswer
from services.data_export_projection import project
from services.deletion_preview import inventory
from services.domain.assessment import AssessmentSession, Attempt, Grade, SessionItem
from services.domain.content import AuditLog
from services.domain.grading_audits import (
    GradingAuditAssignment,
    GradingAuditReview,
    GradingPublication,
    GradingReviewCounter,
)
from services.domain.grading_bands import GradingBandRow
from services.domain.grading_work import GradingWorkRow
from services.domain.mastery import MasteryEvidence
from services.grading_publications import publish
from services.grading_review_contracts import AuditReviewInput
from services.grading_reviews import GradingReviewService, audit_state
from services.identity import IdentityError
from services.providers import FakeModelProvider
from services.short_text_processor import ShortTextProcessor
from services.staff import provision
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_data_requests import claim, create
from tests.integration.test_grading_publications import publication_source as publication_fixture
from tests.integration.test_legal_holds import hold, prepare, release
from tests.integration.test_short_text_flow import save_short, start_short
from tests.integration.test_short_text_flow import short_text as short_text_fixture
from tests.integration.test_short_text_processing import candidate_results

assessment = assessment_fixture
publication_source = publication_fixture
short_text = short_text_fixture
pytestmark = pytest.mark.integration


@pytest.fixture
def published(short_text):
    identity, _, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    saved = save_short(short_text, session, item).json()
    gateway = FakeModelProvider(candidate_results(short_text, item))
    assert ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    ).process_one()
    with Session(identity.engine) as db:
        audit = db.scalar(select(GradingAuditAssignment))
        target = audit.id
    reviewer = actors["reviewer"]["Authorization"].removeprefix("Bearer ")
    return short_text, target, reviewer, UUID(saved["attempt_id"])


def input_points(points=1, critical="NONE"):
    return AuditReviewInput.model_validate_json(
        json.dumps(
            {
                "criterion_points": [{"criterion_id": "R1", "points_awarded": points}],
                "critical_error": critical,
                "affirmative": True,
            }
        )
    )


def test_blinded_task_and_immutable_exact_completion_without_grade_override(published):
    source, target, reviewer, attempt = published
    identity, _, _, _, _, band = source
    service = GradingReviewService(identity)
    assert service.list(reviewer).data[0].id == target
    task = service.get(reviewer, target)
    assert task.response == "  Alpha\n" and task.criteria[0].criterion_id == "R1"
    assert set(task.model_dump()) == {
        "id",
        "item_version_id",
        "rubric_version_id",
        "prompt",
        "response",
        "criteria",
    }
    key = uuid4()
    with Session(identity.engine) as db:
        original = db.get(Grade, attempt).result
    receipt = service.complete(reviewer, target, input_points(), key, uuid4())
    assert service.complete(reviewer, target, input_points(), key, uuid4()) == receipt
    assert service.list(reviewer).data == []
    with Session(identity.engine) as db:
        row = db.get(GradingAuditReview, target)
        assert row.exact_agreement and row.completion_ordinal == 1
        assert db.get(Grade, attempt).result == original
        current = db.get(GradingBandRow, band.id)
        assert current.enabled
        state = audit_state(db, band.id, disabled=False, now=identity.clock())
        assert state.completed_audits == 1 and state.recent[0].exact
    with pytest.raises(IdentityError, match="REVIEW_ALREADY_COMPLETED"):
        service.get(reviewer, target)
    for statement in (
        "UPDATE grading_audit_reviews SET criterion_points=criterion_points",
        "DELETE FROM grading_audit_reviews",
        "UPDATE grading_review_counters SET completed_audits=0",
    ):
        with pytest.raises(DBAPIError), identity.engine.begin() as db:
            db.execute(text(statement))


@pytest.mark.parametrize(
    "points,critical,reason",
    [
        (0, "NONE", "AUDIT_AGREEMENT"),
        (1, "ACADEMIC_INTEGRITY", "CRITICAL_ERROR"),
        (1, "SAFEGUARDING", "CRITICAL_ERROR"),
        (1, "PRIVACY", "CRITICAL_ERROR"),
    ],
)
def test_review_atomically_disables_band_on_disagreement_or_critical_error(
    published, points, critical, reason
):
    source, target, reviewer, _ = published
    identity, _, _, _, _, band = source
    GradingReviewService(identity).complete(
        reviewer, target, input_points(points, critical), uuid4(), uuid4()
    )
    with Session(identity.engine) as db:
        current = db.get(GradingBandRow, band.id)
        assert not current.enabled and current.disable_reason == reason
        state = audit_state(db, band.id, disabled=True, now=identity.clock())
        assert state.completed_audits == 1 and state.disabled


def test_author_learner_and_admin_without_academic_role_cannot_inspect(published):
    source, target, _, _ = published
    identity, _, actors, *_ = source
    service = GradingReviewService(identity)
    for role in ("author", "learner", "admin", "other"):
        token = actors[role]["Authorization"].removeprefix("Bearer ")
        with pytest.raises(IdentityError):
            service.get(token, target)


def test_conflicting_completion_and_unknown_criterion_are_closed(published):
    source, target, reviewer, _ = published
    service = GradingReviewService(source[0])
    invalid = input_points().model_dump(mode="json")
    invalid["criterion_points"][0]["criterion_id"] = "UNKNOWN"
    with pytest.raises(IdentityError, match="VALIDATION_FAILED"):
        service.complete(
            reviewer,
            target,
            AuditReviewInput.model_validate_json(json.dumps(invalid)),
            uuid4(),
            uuid4(),
        )
    key = uuid4()
    service.complete(reviewer, target, input_points(), key, uuid4())
    with pytest.raises(IdentityError, match="IDEMPOTENCY_CONFLICT"):
        service.complete(reviewer, target, input_points(0), key, uuid4())


def test_review_export_inventory_exact_hold_and_release_preserve_original_grade(published):
    source, target, reviewer, attempt = published
    identity, client, actors, _, _, band = source
    GradingReviewService(identity).complete(reviewer, target, input_points(), uuid4(), uuid4())
    with Session(identity.engine) as db:
        owner = db.get(GradingAuditReview, target)
        learner = db.get(Attempt, attempt).learner_id
        own = project(identity, db, learner, uuid4()).records["grading_audit_reviews"]
        assert len(own) == 1 and own[0]["criterion_points"] == {"R1": 1}
        assert own[0]["overrides_original_grade"] is False
        assert set(own[0]) == {
            "id",
            "attempt_id",
            "criterion_points",
            "completed_at",
            "overrides_original_grade",
        }
        assert str(owner.reviewer_id) not in json.dumps(own) and str(band.id) not in json.dumps(own)
        assert (
            project(identity, db, owner.reviewer_id, uuid4()).records["grading_audit_reviews"] == []
        )
        assert any(
            row.source == "grading_audit_reviews" and row.count == 1
            for row in inventory(db, learner)
        )
        assert any(
            row.source == "grading_audit_reviews" and row.count == 1
            for row in inventory(db, owner.reviewer_id)
        )
    request, body = prepare(source)
    body |= {"record_type": "GRADING_REVIEW", "record_id": str(target)}
    result = hold(client, actors["admin"], request, body)
    assert result.status_code == 201, result.text
    foreign = create(client, actors["other"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], foreign).status_code == 200
    assert hold(client, actors["admin"], foreign, body).status_code == 404
    with pytest.raises(DBAPIError, match="Record is legally held"), identity.engine.begin() as db:
        db.execute(text("DELETE FROM grading_audit_reviews WHERE id=:id"), {"id": target})
    assert release(client, actors["admin"], request, result.json()["id"]).status_code == 200
    with pytest.raises(DBAPIError, match="immutable"), identity.engine.begin() as db:
        db.execute(text("DELETE FROM grading_audit_reviews WHERE id=:id"), {"id": target})


def test_http_contract_has_no_hidden_fields_and_preserves_exact_retry(published):
    source, target, _, _ = published
    _, client, actors, *_ = source
    path = f"/api/v1/admin/grading-audits/{target}"
    task = client.get(path, headers=actors["reviewer"])
    assert (
        task.status_code == 200
        and "learner_id" not in task.text
        and "exact_agreement" not in task.text
    )
    assert client.get(path, headers=actors["learner"]).status_code == 403
    headers = actors["reviewer"] | {"Idempotency-Key": str(uuid4())}
    body = input_points().model_dump(mode="json")
    first = client.post(path + "/review", headers=headers, json=body)
    assert first.status_code == 201, first.text
    assert set(first.json()) == {"id", "status", "completed_at"}
    assert client.post(path + "/review", headers=headers, json=body).json() == first.json()
    assert (
        client.post(
            path + "/review", headers=headers, json=body | {"exact_agreement": True}
        ).status_code
        == 422
    )


def test_concurrent_independent_completions_have_one_immutable_winner(published):
    source, target, reviewer, _ = published
    identity, _, actors, _, _, band = source
    second = actors["second"]["Authorization"].removeprefix("Bearer ")
    gate = Barrier(2)

    def complete(token):
        gate.wait(timeout=5)
        try:
            GradingReviewService(identity).complete(token, target, input_points(), uuid4(), uuid4())
            return "COMPLETED"
        except IdentityError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(complete, [reviewer, second]))
    assert sorted(outcomes) == ["COMPLETED", "REVIEW_ALREADY_COMPLETED"]
    with Session(identity.engine) as db:
        assert db.get(GradingReviewCounter, band.id).completed_audits == 1
        assert db.scalar(select(func.count()).select_from(GradingAuditReview)) == 1


def test_review_crash_rolls_back_counter_and_disablement(published, monkeypatch):
    source, target, reviewer, _ = published
    identity, _, _, _, _, band = source

    @contextmanager
    def crash():
        with Session(identity.engine) as db:
            yield db
            raise RuntimeError("Synthetic review crash before commit")

    with monkeypatch.context() as changes:
        changes.setattr(identity, "transaction", crash)
        with pytest.raises(RuntimeError, match="Synthetic review crash"):
            GradingReviewService(identity).complete(
                reviewer, target, input_points(0), uuid4(), uuid4()
            )
    with Session(identity.engine) as db:
        assert db.get(GradingAuditReview, target) is None
        assert db.get(GradingReviewCounter, band.id).completed_audits == 0
        assert db.get(GradingBandRow, band.id).enabled


def test_critical_review_after_first_pass_prevents_second_call_and_publication(published):
    source, target, reviewer, first_attempt = published
    identity, client, actors, _, policy, _ = source
    with Session(identity.engine) as db:
        first = db.get(Attempt, first_attempt)
        session = str(db.get(SessionItem, first.session_item_id).session_id)
    item = client.get(f"/api/v1/sessions/{session}/next-item", headers=actors["learner"]).json()
    pending = save_short(source, session, item).json()

    class ReviewingProvider(FakeModelProvider):
        def execute(self, task):
            result = super().execute(task)
            if len(self.calls) == 1:
                GradingReviewService(identity).complete(
                    reviewer, target, input_points(1, "ACADEMIC_INTEGRITY"), uuid4(), uuid4()
                )
            return result

    gateway = ReviewingProvider(candidate_results(source, item))
    assert ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    ).process_one()
    assert len(gateway.calls) == 1
    with Session(identity.engine) as db:
        attempt = UUID(pending["attempt_id"])
        assert db.get(Grade, attempt) is None
        assert db.get(GradingWorkRow, attempt).status == "LOW_CONFIDENCE"
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 1


@pytest.mark.parametrize("short_text", [15], indirect=True)
def test_abandoned_sealed_diagnostic_cannot_consume_revision_audit_coverage(short_text):
    identity, client, actors, plan, policy, _ = short_text
    diagnostic = client.post(
        "/api/v1/diagnostics",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json={"subject_id": plan["subject_id"]},
    ).json()["id"]
    item = client.get(f"/api/v1/sessions/{diagnostic}/next-item", headers=actors["learner"]).json()
    save_short(short_text, diagnostic, item)
    processor = ShortTextProcessor(
        AssessmentService(identity, policy),
        FakeModelProvider(candidate_results(short_text, item)),
        safety=lambda context, response: True,
    )
    assert processor.process_one()
    assert (
        client.post(f"/api/v1/sessions/{diagnostic}/abandon", headers=actors["learner"]).status_code
        == 200
    )
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    assert ShortTextProcessor(
        AssessmentService(identity, policy),
        FakeModelProvider(candidate_results(short_text, item)),
        safety=lambda context, response: True,
    ).process_one()
    with Session(identity.engine) as db:
        row = db.get(GradingPublication, UUID(pending["attempt_id"]))
        assert row.ordinal == 2 and row.session_ordinal == 1 and row.audit_required
        assert row.sampling_policy == "short-text-audit-release-unit-v1"
        owner = db.get(Attempt, row.attempt_id).learner_id
        exported = project(identity, db, owner, uuid4()).records
        assert (
            len(exported["grading_publications"]) == len(exported["grading_audit_assignments"]) == 1
        )


@pytest.mark.parametrize("barrier", ["WITHDRAWAL", "ROLE_REVOKED", "STALE_AUTH"])
def test_authorization_is_rechecked_after_blinded_task_access(published, barrier):
    source, target, reviewer, _ = published
    identity, client, actors, *_ = source
    service = GradingReviewService(identity)
    service.get(reviewer, target)
    if barrier == "WITHDRAWAL":
        withdrawn = client.post(
            "/api/v1/me/consents",
            headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "WITHDRAW",
                "policy_version": identity.settings.consent_policy_version,
                "affirmative": True,
            },
        )
        assert withdrawn.status_code == 200
    elif barrier == "ROLE_REVOKED":
        provision(identity, "reviewer@example.invalid", "ACADEMIC_REVIEWER", revoke=True)
    else:
        before = identity.clock()
        identity.clock = lambda: before + timedelta(minutes=10)
    for operation in (
        lambda: service.get(reviewer, target),
        lambda: service.complete(reviewer, target, input_points(), uuid4(), uuid4()),
    ):
        with pytest.raises(IdentityError):
            operation()
    with Session(identity.engine) as db:
        assert db.get(GradingAuditReview, target) is None


def test_audit_logs_keep_original_correlation_without_response_or_points(published):
    source, target, reviewer, _ = published
    identity = source[0]
    service = GradingReviewService(identity)
    read, write, retry, key = uuid4(), uuid4(), uuid4(), uuid4()
    service.get(reviewer, target, read)
    service.complete(reviewer, target, input_points(), key, write)
    service.complete(reviewer, target, input_points(), key, retry)
    with Session(identity.engine) as db:
        rows = list(db.scalars(select(AuditLog).where(AuditLog.target_id == target)))
        assert {(row.action, row.request_id) for row in rows} == {
            ("grading_review.read", read),
            ("grading_review.completed", write),
            ("grading_review.receipt_read", retry),
        }
        assert all(row.reason == "Independent synthetic grading review" for row in rows)
        assert all(row.before_hash is None and row.after_hash is None for row in rows)


def test_last_hundred_completed_reviews_evict_old_error_without_reenabling(published):
    source, first_target, reviewer, first_attempt = published
    identity, _, actors, _, policy, band = source
    learner = actors["learner"]["Authorization"].removeprefix("Bearer ")
    assessment = AssessmentService(identity, policy)
    with Session(identity.engine) as db:
        attempt = db.get(Attempt, first_attempt)
        original = db.get(
            AssessmentSession, db.get(SessionItem, attempt.session_item_id).session_id
        )
        original_id = original.id
        owner, subject, topic = original.learner_id, original.subject_id, original.topic_id
        versions = list(
            db.scalars(
                select(SessionItem.item_version_id)
                .where(SessionItem.session_id == original_id)
                .order_by(SessionItem.position)
            )
        )
    assessment.abandon(learner, original_id, uuid4())
    # Compact storage/window fixture: allocate valid five-item plans directly, then
    # use normal encrypted submission, grading and publication with every SQL guard.
    # Reusing these synthetic items does not assert unseen selector acceptance.
    for _ in range(100):
        target, served = uuid4(), uuid4()
        with Session(identity.engine) as db, db.begin():
            db.add(
                AssessmentSession(
                    id=target,
                    learner_id=owner,
                    subject_id=subject,
                    topic_id=topic,
                    status="ACTIVE",
                    kind="REVISION",
                    item_count=5,
                    reason="TOPIC",
                    plan_version="synthetic-window-fixture-v1",
                    started_at=identity.clock(),
                    expires_at=identity.clock() + timedelta(days=1),
                )
            )
            db.flush()
            for position, version in enumerate(versions, start=1):
                db.add(
                    SessionItem(
                        id=served if position == 1 else uuid4(),
                        session_id=target,
                        item_version_id=version,
                        position=position,
                        reason="TOPIC",
                        served_at=identity.clock() if position == 1 else None,
                        grading_band_id=band.id,
                    )
                )
        body = SubmitAnswer.model_validate_json(
            json.dumps(
                {
                    "session_item_id": str(served),
                    "response": {"type": "SHORT_TEXT", "text": "  Alpha\n"},
                }
            )
        )
        assessment.submit(learner, target, body, uuid4(), uuid4())
        gateway = FakeModelProvider(
            candidate_results(source, {"item_version_id": str(versions[0])})
        )
        assert ShortTextProcessor(
            assessment, gateway, safety=lambda context, response: True
        ).process_one()
        assessment.abandon(learner, target, uuid4())
    with Session(identity.engine) as db:
        targets = list(
            db.scalars(
                select(GradingAuditAssignment.id).where(GradingAuditAssignment.id != first_target)
            )
        )
        assert len(targets) == 100
    service = GradingReviewService(identity)
    service.complete(reviewer, first_target, input_points(0), uuid4(), uuid4())
    clock = identity.clock()
    for index, target in enumerate(targets):
        # Respect the actual write limit and ten-minute recent-auth window.
        identity.clock = lambda index=index: clock + timedelta(seconds=61 * (index // 25))
        service.complete(reviewer, target, input_points(), uuid4(), uuid4())
    with Session(identity.engine) as db:
        row = db.get(GradingBandRow, band.id)
        state = audit_state(db, band.id, disabled=not row.enabled, now=identity.clock())
        assert state.completed_audits == 101 and len(state.recent) == 100
        assert all(outcome.exact for outcome in state.recent)
        assert all(outcome.grade_id != first_attempt for outcome in state.recent)
        assert state.disabled and row.disable_reason == "AUDIT_AGREEMENT"


@pytest.mark.parametrize("identity", ["0032"], indirect=True)
def test_upgrade_preserves_existing_publication_and_initializes_review_counter(publication_source):
    identity, band, attempt, _ = publication_source
    with Session(identity.engine) as db, db.begin():
        # Use original columns because the current ORM also knows additive 0033 columns.
        db.execute(
            text(
                "INSERT INTO grading_publications(attempt_id,band_id,ordinal,"
                "audit_required,published_at) VALUES(:attempt,:band,1,true,:now)"
            ),
            {"attempt": attempt, "band": band.id, "now": identity.clock()},
        )
        original = dict(db.execute(text("SELECT * FROM grading_publications")).mappings().one())
    env = os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()}
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            env=env,
            capture_output=True,
        )
    with Session(identity.engine) as db, db.begin():
        row = db.get(GradingPublication, attempt)
        assert row.ordinal == original["ordinal"] and row.published_at == original["published_at"]
        assert row.audit_required and row.sampling_policy == "global-publication-v1"
        assert row.session_ordinal is None
        assert db.get(GradingReviewCounter, band.id).completed_audits == 0
        assert publish(db, band.id, attempt, identity.clock()).ordinal == 1


def test_completion_preserves_future_timestamp_guard_under_host_database_clock_skew(published):
    from services.identity_contracts import OTPRequest, OTPVerify

    source, target, _, _ = published
    identity = source[0]
    with Session(identity.engine) as db:
        database_now = db.scalar(select(func.clock_timestamp()))
    # A frozen ahead-of-database host clock makes the original INSERT fail, without
    # relying on submillisecond native timing luck. Renew synthetic auth under that clock.
    ahead = database_now + timedelta(seconds=30)
    identity.clock = lambda: ahead
    challenge = identity.request_otp(
        OTPRequest(identifier="reviewer@example.invalid", device_id=uuid4()), "synthetic-skew", None
    )
    token = identity.verify(
        OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
    ).access_token
    receipt = GradingReviewService(identity).complete(
        token, target, input_points(), uuid4(), uuid4()
    )
    with Session(identity.engine) as db:
        row = db.get(GradingAuditReview, target)
        assert row.completed_at == receipt.completed_at
        assert row.completed_at <= db.scalar(select(func.clock_timestamp()))
        assert row.completed_at < ahead
        assert row.exact_agreement
