"""FR-GRD-003/004, FR-MST-001, FR-ID-006: synthetic end-to-end worker publication."""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.grading_fixtures import unapproved_band
from services.assessment import AssessmentService
from services.assessment_contracts import ChoiceResponse, StartRevision, SubmitAnswer
from services.data_export_projection import project
from services.domain.assessment import Attempt, Grade
from services.domain.content import ItemVersion
from services.domain.grading_audits import GradingAuditAssignment, GradingPublication
from services.domain.grading_work import GradingWorkRow
from services.domain.mastery import MasteryEvidence
from services.grading_band_store import register
from services.providers import FakeModelProvider, ModelResult
from services.short_text_contracts import ShortTextResponse
from services.short_text_eligibility import GradingScope
from services.short_text_policy import ShortTextPolicy
from services.short_text_processor import ShortTextProcessor
from tests.integration.test_content import create, review, submit
from tests.integration.test_grading_bands import activate_synthetic
from tests.integration.test_reviewed_rubrics import document
from tests.integration.test_short_text_flow import save_short, start_short
from tests.integration.test_short_text_flow import short_text as short_text_fixture

short_text = short_text_fixture
pytestmark = pytest.mark.integration


def exercise_restricted_short_text_flow(assessment, identity):
    """Called under the existing real temporary login, with owner-only fixture setup."""
    owner, client, actors, body, _, plan = assessment
    for index in range(5):
        draft = create(
            client,
            actors,
            body | {"document": document(body) | {"title": f"Restricted synthetic rubric {index}"}},
        )
        approved = review(client, actors, submit(client, actors, draft))
        assert approved.status_code == 200, approved.text
    patched = client.patch(
        "/api/v1/me",
        headers=actors["other"],
        json={
            "display_name": "Synthetic restricted learner",
            "birth_date": "2000-01-01",
            "subject_ids": [plan["subject_id"]],
        },
    )
    assert patched.status_code == 200, patched.text
    token = actors["other"]["Authorization"].removeprefix("Bearer ")
    ordinary = AssessmentService(identity)
    baseline = ordinary.start(token, StartRevision.model_validate(plan), uuid4(), uuid4())
    for _ in range(5):
        question = ordinary.next_item(token, baseline.id, uuid4())
        ordinary.submit(
            token,
            baseline.id,
            SubmitAnswer(
                session_item_id=question.session_item_id, response=ChoiceResponse(choice_id="A")
            ),
            uuid4(),
            uuid4(),
        )
    settings = identity.settings
    band = unapproved_band(
        GradingScope(
            subject_id=UUID(plan["subject_id"]),
            topic_id=UUID(plan["topic_id"]),
            language="en",
            model_version=settings.short_text_model_version,
            prompt_version=settings.short_text_prompt_version,
            configuration_version=settings.short_text_configuration_version,
        )
    ).model_copy(
        update={"approval_id": uuid4(), "approved_at": owner.clock(), "subgroup_review": "APPROVED"}
    )
    with Session(owner.engine) as db, db.begin():
        register(db, band, owner.clock())
        activate_synthetic(db, band, owner.clock())
    settings.short_text_enabled = True
    settings.model_provider = "fake"
    policy = ShortTextPolicy(identity, lambda candidate: candidate.id == band.id)
    service = AssessmentService(identity, policy)
    started = service.start(token, StartRevision.model_validate(plan), uuid4(), uuid4())
    question = service.next_item(token, started.id, uuid4())
    assert question.response_spec.type == "SHORT_TEXT"
    pending = service.submit(
        token,
        started.id,
        SubmitAnswer(
            session_item_id=question.session_item_id,
            response=ShortTextResponse(type="SHORT_TEXT", text="Alpha"),
        ),
        uuid4(),
        uuid4(),
    )
    source = (identity, client, actors, plan, policy, band)
    gateway = FakeModelProvider(
        candidate_results(source, {"item_version_id": str(question.item_version_id)})
    )
    assert ShortTextProcessor(service, gateway, safety=lambda context, response: True).process_one()
    result = service.result(token, pending.attempt_id)
    assert result.method == "RUBRIC_MODEL" and result.points_awarded == 1
    assert len(gateway.calls) == 2
    from services.grading_review_contracts import AuditReviewInput
    from services.grading_reviews import GradingReviewService

    with Session(identity.engine) as db:
        audit = db.scalar(
            select(GradingAuditAssignment).where(
                GradingAuditAssignment.attempt_id == pending.attempt_id
            )
        )
        target = audit.id
    reviewer = actors["reviewer"]["Authorization"].removeprefix("Bearer ")
    reviews = GradingReviewService(identity)
    assert reviews.get(reviewer, target).response == "Alpha"
    body = AuditReviewInput.model_validate_json(
        json.dumps(
            {
                "criterion_points": [{"criterion_id": "R1", "points_awarded": 1}],
                "critical_error": "NONE",
                "affirmative": True,
            }
        )
    )
    assert reviews.complete(reviewer, target, body, uuid4(), uuid4()).status == "COMPLETED"


def candidate_results(source, item):
    identity, _, _, _, policy, _ = source
    with Session(identity.engine) as db:
        context = policy.context(db.get(ItemVersion, UUID(item["item_version_id"])))
    candidate = {
        "criterion_results": [
            {
                "criterion_id": "R1",
                "points_awarded": 1,
                "evidence_excerpt": "Alpha",
                "justification_code": "SUPPORTED",
            }
        ],
        "total_points": 1,
        "confidence": 0.97,
        "detected_misconception_ids": [],
        "feedback": {
            "correct_elements": context.correct_elements,
            "missing_elements": [],
            "next_action": context.next_actions[0],
        },
    }
    result = ModelResult(
        status="CANDIDATE",
        provider="fake",
        model="fixture-v1",
        raw_output=json.dumps(candidate),
        input_tokens=100,
        output_tokens=100,
    )
    return [result, result.model_copy(deep=True)]


def test_worker_publishes_one_bound_grade_mastery_audit_and_owned_decrypted_export(short_text):
    identity, client, actors, _, policy, band = short_text
    session, item = start_short(short_text)
    key = str(uuid4())
    pending = save_short(short_text, session, item, key).json()
    gateway = FakeModelProvider(candidate_results(short_text, item))
    processor = ShortTextProcessor(
        AssessmentService(identity, policy),
        gateway,
        safety=lambda context, response: response.strip() == "Alpha",
    )
    assert processor.process_one()
    assert len(gateway.calls) == 2
    assert not processor.process_one()
    result = client.get(pending["poll_url"], headers=actors["learner"])
    assert result.status_code == 200, result.text
    grade = result.json()
    assert grade["status"] == "GRADED" and grade["method"] == "RUBRIC_MODEL"
    assert grade["score"] == 1.0 and grade["points_awarded"] == grade["points_possible"] == 1
    assert grade["rubric_version_id"] == grade["item_version_id"] == item["item_version_id"]
    assert grade["criterion_results"][0]["evidence_excerpt"] == "Alpha"
    assert grade["mastery_update_status"] == "COMPLETED"
    assert save_short(short_text, session, item, key).json() == grade
    with Session(identity.engine) as db:
        attempt_id = UUID(pending["attempt_id"])
        attempt = db.get(Attempt, attempt_id)
        stored = db.get(Grade, attempt_id)
        assert "Alpha" not in json.dumps(stored.result)
        assert stored.result["criterion_points"] == {"R1": 1}
        assert db.get(GradingWorkRow, attempt_id).status == "GRADED"
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 1
        publication = db.get(GradingPublication, attempt_id)
        assert publication.ordinal == 1 and publication.audit_required
        assert db.scalar(select(func.count()).select_from(GradingAuditAssignment)) == 1
        exported = project(identity, db, attempt.learner_id, uuid4()).model_dump(mode="json")
        assert exported["records"]["answers"][0]["response"] == {
            "type": "SHORT_TEXT",
            "text": "  Alpha\n",
        }
        assert (
            exported["records"]["grades"][0]["criterion_results"][0]["evidence_excerpt"] == "Alpha"
        )
        assert "ciphertext" not in json.dumps(exported) and str(band.id) not in json.dumps(exported)


@pytest.mark.parametrize("safety", [None, False])
def test_missing_or_rejecting_safety_check_prevents_all_model_calls(short_text, safety):
    identity, client, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    gateway = FakeModelProvider(candidate_results(short_text, item))
    processor = ShortTextProcessor(
        AssessmentService(identity, policy),
        gateway,
        safety=None if safety is None else lambda context, response: False,
    )
    assert processor.process_one() and gateway.calls == []
    neutral = client.get(pending["poll_url"], headers=actors["learner"])
    assert neutral.status_code == 200 and neutral.json()["status"] == "LOW_CONFIDENCE"
    with Session(identity.engine) as db:
        assert db.get(Grade, UUID(pending["attempt_id"])) is None
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0


@pytest.mark.parametrize("change", ["WITHDRAWAL", "BAND_DISABLED", "LEASE_EXPIRED"])
def test_rechecks_before_each_pass_and_after_model_work(short_text, change):
    identity, client, actors, _, policy, band = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    results = candidate_results(short_text, item)

    class ChangingProvider(FakeModelProvider):
        def execute(self, task):
            result = super().execute(task)
            if len(self.calls) == 1:
                if change == "WITHDRAWAL":
                    withdrawn = client.post(
                        "/api/v1/me/consents",
                        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
                        json={
                            "consent_type": "WITHDRAW",
                            "policy_version": identity.settings.consent_policy_version,
                            "affirmative": True,
                        },
                    )
                    assert withdrawn.status_code == 200, withdrawn.text
                elif change == "BAND_DISABLED":
                    from services.grading_band_store import disable

                    with Session(identity.engine) as db, db.begin():
                        disable(db, band.id, identity.clock(), "MANUAL")
                else:
                    original = identity.clock
                    identity.clock = lambda: original() + timedelta(seconds=31)
            return result

    gateway = ChangingProvider(results)
    processor = ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    )
    assert processor.process_one()
    assert len(gateway.calls) == 1
    if change == "WITHDRAWAL":
        # Assert outside the provider callback: model failures also fall back safely,
        # so a malformed withdrawal inside that callback must not masquerade as success.
        denied = client.get(f"/api/v1/sessions/{session}/next-item", headers=actors["learner"])
        assert denied.status_code == 403 and denied.json()["error"]["code"] == "CONSENT_REQUIRED"
    with Session(identity.engine) as db:
        assert db.get(Grade, UUID(pending["attempt_id"])) is None
        assert db.get(GradingWorkRow, UUID(pending["attempt_id"])).status == "LOW_CONFIDENCE"
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0


@pytest.mark.parametrize("short_text", [15], indirect=True)
def test_diagnostic_keeps_partial_grades_sealed_until_every_saved_answer_is_terminal(short_text):
    identity, client, actors, plan, policy, _ = short_text
    started = client.post(
        "/api/v1/diagnostics",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json={"subject_id": plan["subject_id"]},
    )
    assert started.status_code == 201, started.text
    session = started.json()["id"]
    for _ in range(15):
        item = client.get(f"/api/v1/sessions/{session}/next-item", headers=actors["learner"])
        assert item.status_code == 200, item.text
        saved = save_short(short_text, session, item.json())
        assert saved.status_code == 200 and saved.json()["status"] == "SAVED", saved.text
    waiting = client.get(f"/api/v1/diagnostics/{session}", headers=actors["learner"])
    assert waiting.status_code == 200 and waiting.json()["status"] == "ACTIVE"
    assert waiting.json()["answered_count"] == 15 and waiting.json()["result"] is None
    gateway = FakeModelProvider(candidate_results(short_text, item.json()))
    service = AssessmentService(identity, policy)
    assert ShortTextProcessor(service, gateway, safety=lambda context, response: True).process_one()
    with Session(identity.engine) as db:
        attempt = db.scalar(select(Attempt).join(Grade, Grade.attempt_id == Attempt.id))
        scored_attempt, owner = attempt.id, attempt.learner_id
        sealed = project(identity, db, owner, uuid4()).records
        assert sealed["grades"] == sealed["mastery_evidence"] == []
    assert (
        client.get(
            f"/api/v1/attempts/{scored_attempt}/grade", headers=actors["learner"]
        ).status_code
        == 403
    )
    fallback = ShortTextProcessor(
        service, FakeModelProvider(), safety=lambda context, response: True
    )
    for _ in range(14):
        assert fallback.process_one()
    complete = client.get(f"/api/v1/diagnostics/{session}", headers=actors["learner"])
    assert complete.status_code == 200, complete.text
    assert complete.json()["status"] == "COMPLETED" and complete.json()["result"] is not None
    released = client.get(f"/api/v1/attempts/{scored_attempt}/grade", headers=actors["learner"])
    assert released.status_code == 200 and released.json()["status"] == "GRADED"
    with Session(identity.engine) as db:
        exported = project(identity, db, owner, uuid4()).records
        assert len(exported["answers"]) == 15
        assert len(exported["grades"]) == len(exported["mastery_evidence"]) == 1


def test_duplicate_worker_cannot_reclaim_running_budget(short_text):
    identity, client, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    dispatched, release = Event(), Event()

    class PausedProvider(FakeModelProvider):
        def execute(self, task):
            if not self.calls:
                dispatched.set()
                assert release.wait(timeout=4)
            return super().execute(task)

    gateway = PausedProvider(candidate_results(short_text, item))
    service = AssessmentService(identity, policy)
    with ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(
            ShortTextProcessor(service, gateway, safety=lambda context, response: True).process_one
        )
        try:
            assert dispatched.wait(timeout=3)
            duplicate = FakeModelProvider(candidate_results(short_text, item))
            assert not ShortTextProcessor(
                service, duplicate, safety=lambda context, response: True
            ).process_one()
            assert not duplicate.calls
        finally:
            release.set()
        assert first.result(timeout=5)
    assert len(gateway.calls) == 2
    assert client.get(pending["poll_url"], headers=actors["learner"]).json()["status"] == "GRADED"
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 1
        assert db.scalar(select(func.count()).select_from(GradingPublication)) == 1


def test_crash_after_publication_rolls_back_grade_audit_and_mastery_without_redispatch(
    short_text, monkeypatch
):
    import services.short_text_processor as processor_module

    identity, client, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    attempt_id = UUID(pending["attempt_id"])
    gateway = FakeModelProvider(candidate_results(short_text, item))
    original_publish = processor_module.publish

    def crash(*args, **kwargs):
        original_publish(*args, **kwargs)
        raise RuntimeError("Synthetic publication crash")

    monkeypatch.setattr(processor_module, "publish", crash)
    processor = ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    )
    with pytest.raises(RuntimeError, match="Synthetic publication crash"):
        processor.process_one()
    assert len(gateway.calls) == 2
    with Session(identity.engine) as db:
        assert db.get(Grade, attempt_id) is None
        assert db.get(GradingWorkRow, attempt_id).status == "RUNNING"
        for model in (MasteryEvidence, GradingPublication, GradingAuditAssignment):
            assert db.scalar(select(func.count()).select_from(model)) == 0
    assert not processor.process_one()
    original_clock = identity.clock
    identity.clock = lambda: original_clock() + timedelta(seconds=31)
    assert not processor.process_one()
    assert len(gateway.calls) == 2
    neutral = client.get(pending["poll_url"], headers=actors["learner"])
    assert neutral.status_code == 200 and neutral.json()["status"] == "LOW_CONFIDENCE"


def test_report_revocation_after_second_pass_prevents_publication(short_text):
    identity, client, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()

    class RevokingProvider(FakeModelProvider):
        def execute(self, task):
            result = super().execute(task)
            if len(self.calls) == 2:
                policy.authority = None
            return result

    gateway = RevokingProvider(candidate_results(short_text, item))
    assert ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    ).process_one()
    assert len(gateway.calls) == 2
    assert (
        client.get(pending["poll_url"], headers=actors["learner"]).json()["status"]
        == "LOW_CONFIDENCE"
    )
    with Session(identity.engine) as db:
        assert db.get(Grade, UUID(pending["attempt_id"])) is None
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0


@pytest.mark.parametrize("omitted", ["publish", "reconcile"])
def test_sql_refuses_grade_without_atomic_publication_and_mastery(short_text, monkeypatch, omitted):
    identity, _, _, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    monkeypatch.setattr(f"services.short_text_processor.{omitted}", lambda *args, **kwargs: None)
    gateway = FakeModelProvider(candidate_results(short_text, item))
    processor = ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    )
    with pytest.raises(DBAPIError):
        processor.process_one()
    assert len(gateway.calls) == 2 and not processor.process_one()
    with Session(identity.engine) as db:
        assert db.get(Grade, UUID(pending["attempt_id"])) is None
        assert db.get(GradingWorkRow, UUID(pending["attempt_id"])).status == "RUNNING"
        for model in (MasteryEvidence, GradingPublication, GradingAuditAssignment):
            assert db.scalar(select(func.count()).select_from(model)) == 0


@pytest.mark.parametrize("limit", ["REQUESTS", "TOKENS", "DEADLINE"])
def test_configured_runtime_budget_exhaustion_saves_neutral_and_never_repeats(
    short_text, limit, monkeypatch
):
    identity, client, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    key = str(uuid4())
    pending = save_short(short_text, session, item, key).json()
    good = candidate_results(short_text, item)
    fixtures = good
    if limit == "REQUESTS":
        identity.settings.short_text_max_requests = 2
        fixtures = [good[0].model_copy(update={"raw_output": "{}"}), *good]
    elif limit == "TOKENS":
        identity.settings.short_text_max_tokens = 2
    else:
        identity.settings.short_text_timeout_ms = 10
        ticks = iter([0.0, 0.02])
        monkeypatch.setattr("services.short_text_processor.monotonic", lambda: next(ticks))
    gateway = FakeModelProvider(fixtures)
    processor = ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    )
    assert processor.process_one()
    assert len(gateway.calls) == (2 if limit == "REQUESTS" else 0)
    result = client.get(pending["poll_url"], headers=actors["learner"])
    assert result.status_code == 200 and result.json()["status"] == "LOW_CONFIDENCE"
    assert "points_awarded" not in result.text and "score" not in result.json()
    assert save_short(short_text, session, item, key).json() == result.json()
    assert not processor.process_one()
    assert len(gateway.calls) == (2 if limit == "REQUESTS" else 0)
    with Session(identity.engine) as db:
        attempt = UUID(pending["attempt_id"])
        assert db.get(Attempt, attempt) is not None
        assert db.get(Grade, attempt) is None
        assert db.get(GradingWorkRow, attempt).status == "LOW_CONFIDENCE"
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 0


@pytest.mark.parametrize("safe", [True, False])
def test_worker_observation_counts_actual_authorized_dispatches_only(short_text, safe):
    from services.metric_reader import DeltaReader
    from services.model_metrics import ModelMetrics, activate

    identity, _, _, _, policy, _ = short_text
    session, item = start_short(short_text)
    save_short(short_text, session, item)
    gateway = FakeModelProvider(candidate_results(short_text, item))
    reader = DeltaReader()
    metrics = ModelMetrics(reader)
    activate(metrics)
    try:
        worker = ShortTextProcessor(
            AssessmentService(identity, policy), gateway, safety=lambda context, response: safe
        )
        assert worker.process_one()
        observed = metrics.take(reader)
        if safe:
            assert observed.counts == (2, 0, 0, 0, 200, 200)
        else:
            assert observed is None
        assert not worker.process_one()
        assert metrics.take(reader) is None
        assert len(gateway.calls) == (2 if safe else 0)
    finally:
        activate(None)
        metrics.shutdown()


@pytest.mark.parametrize("failure", [False, True])
def test_model_dispatch_keeps_sql_gate_without_open_transaction(short_text, failure):
    from sqlalchemy import text

    from tests.integration.test_account_processing import EXCLUSIVE, active_gate_count

    identity, client, actors, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    subject = identity.me(actors["learner"]["Authorization"].removeprefix("Bearer ")).id
    observations = []

    class InspectingProvider(FakeModelProvider):
        def execute(self, task):
            with identity.engine.connect() as db:
                exclusive = db.scalar(EXCLUSIVE, {"subject": subject})
                idle_gate = db.scalar(
                    text("""
                  WITH key AS (SELECT hashtextextended(
                    'kasoma.account-processing.v1:' ||
    pg_catalog.to_regnamespace(current_schema())::oid::text || ':' || CAST(:subject AS text),0)
                    | (-9223372036854775808)::bigint AS value)
                  SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_locks l
                    JOIN pg_catalog.pg_stat_activity a ON a.pid=l.pid CROSS JOIN key
                    WHERE l.locktype='advisory' AND l.granted AND l.mode='ShareLock'
                      AND l.classid=((key.value>>32)&4294967295)::oid
                      AND l.objid=(key.value&4294967295)::oid AND l.objsubid=1
                      AND a.datname=current_database() AND a.state='idle'
                      AND a.xact_start IS NULL)
                """),
                    {"subject": subject},
                )
                observations.append((exclusive, idle_gate))
            if failure:
                raise RuntimeError("Synthetic provider failure")
            return super().execute(task)

    gateway = InspectingProvider(candidate_results(short_text, item))
    assert ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    ).process_one()
    # Assert outside the callback: processor fallback must not hide a broken guard.
    assert observations == ([(False, True)] if failure else [(False, True), (False, True)])
    assert active_gate_count(identity.engine, subject) == 0
    with identity.engine.connect() as db:
        assert db.scalar(EXCLUSIVE, {"subject": subject}) is True
    with Session(identity.engine) as db:
        assert (db.get(Grade, UUID(pending["attempt_id"])) is None) == failure
