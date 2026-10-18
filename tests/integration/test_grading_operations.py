"""FR-OPS-002: real durable queue states, bounded aggregates, never academic accuracy."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.domain.grading_audits import GradingAuditAssignment
from services.grading_operations import grading_counts
from services.grading_reviews import GradingReviewService
from services.grading_work_store import claim_next, expire_due
from services.health import Health
from services.providers import FakeModelProvider
from services.short_text_processor import ShortTextProcessor
from tests.integration.test_grading_reviews import input_points
from tests.integration.test_short_text_flow import save_short, start_short
from tests.integration.test_short_text_flow import short_text as short_text_fixture
from tests.integration.test_short_text_processing import candidate_results

short_text = short_text_fixture
pytestmark = pytest.mark.integration


def current(source):
    identity, client, actors, *_ = source
    result = client.get("/api/v1/admin/operations", headers=actors["admin"])
    assert result.status_code == 200, result.text
    view = result.json()
    assert "AI_USAGE" in view["unavailable_metrics"]
    assert "GRADING_FAILURE_RATE" in view["unavailable_metrics"]
    assert "attempt_id" not in result.text and "band_id" not in result.text
    return view["counts"]["grading"], {row["code"] for row in view["alerts"]}


def test_queue_claim_expired_lease_and_neutral_recovery_are_visible(short_text, monkeypatch):
    identity, client, actors, *_ = short_text
    now = [identity.clock()]
    identity.clock = lambda: now[0]
    monkeypatch.setattr(
        "services.operations.dependency_health",
        lambda _: Health(status="ok", database="up", redis="up"),
    )
    session, item = start_short(short_text)
    saved = save_short(short_text, session, item)
    assert saved.status_code == 200
    queued, alerts = current(short_text)
    assert queued["queued"]["value"] == 1 and queued["running"]["value"] == 0
    assert queued["oldest_pending_seconds"] == 0 and "GRADING_STALLED" not in alerts
    now[0] += timedelta(seconds=identity.settings.ops_grading_age_seconds)
    assert "GRADING_STALLED" in current(short_text)[1]
    with Session(identity.engine) as db, db.begin():
        work = claim_next(db, now[0])
        assert work is not None
    running, _ = current(short_text)
    assert running["queued"]["value"] == 0 and running["running"]["value"] == 1
    assert running["expired_running_leases"]["value"] == 0
    now[0] = work.lease_until
    expired, _ = current(short_text)
    assert expired["expired_running_leases"]["value"] == 1
    with Session(identity.engine) as db, db.begin():
        assert expire_due(db, now[0]) == 1
    finished, alerts = current(short_text)
    assert finished["neutral_finished_24h"]["value"] == 1
    assert finished["processing_fallback_finished_24h"]["value"] == 0
    assert finished["oldest_pending_seconds"] == 0 and "GRADING_STALLED" not in alerts
    for role in ["learner", "author", "reviewer", "support"]:
        assert client.get("/api/v1/admin/operations", headers=actors[role]).status_code == 403


def test_provider_processing_fallback_is_not_an_academic_error_rate(short_text):
    identity, _, _, _, policy, _ = short_text
    session, item = start_short(short_text)
    pending = save_short(short_text, session, item).json()
    gateway = FakeModelProvider([RuntimeError("PRIVATE_PROVIDER_DIAGNOSTIC")])
    assert ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    ).process_one()
    counts, alerts = current(short_text)
    assert counts["neutral_finished_24h"]["value"] == 1
    assert counts["processing_fallback_finished_24h"]["value"] == 1
    assert counts["graded_finished_24h"]["value"] == 0
    assert alerts.isdisjoint({"GRADING_FAILED", "GRADING_FALLBACKS"})
    assert str(UUID(pending["attempt_id"])) not in str(counts)
    with Session(identity.engine) as db:
        at = identity.clock()
        assert (
            grading_counts(db, at + timedelta(hours=24)).processing_fallback_finished_24h.value == 1
        )
        assert (
            grading_counts(
                db, at + timedelta(hours=24, microseconds=1)
            ).processing_fallback_finished_24h.value
            == 0
        )
        assert (
            grading_counts(
                db, at - timedelta(microseconds=1)
            ).processing_fallback_finished_24h.value
            == 0
        )


def test_grade_pending_audit_and_sticky_disablement_counts_are_minimized(short_text):
    identity, _, actors, _, policy, band = short_text
    session, item = start_short(short_text)
    save_short(short_text, session, item)
    gateway = FakeModelProvider(candidate_results(short_text, item))
    assert ShortTextProcessor(
        AssessmentService(identity, policy), gateway, safety=lambda context, response: True
    ).process_one()
    from services.grading_band_store import disable, register

    # A rejected, never-activated candidate is not a previously enabled band.
    dormant = band.model_copy(update={"id": uuid4()})
    with Session(identity.engine) as db, db.begin():
        register(db, dormant, identity.clock())
        disable(db, dormant.id, identity.clock(), "MANUAL")
    first, _ = current(short_text)
    assert first["graded_finished_24h"]["value"] == first["pending_audits"]["value"] == 1
    assert first["disabled_bands"]["value"] == 0
    with Session(identity.engine) as db:
        audit = db.scalar(select(GradingAuditAssignment.id))
    GradingReviewService(identity).complete(
        actors["reviewer"]["Authorization"][7:],
        audit,
        input_points(1, "ACADEMIC_INTEGRITY"),
        uuid4(),
        uuid4(),
    )
    completed, alerts = current(short_text)
    assert completed["pending_audits"]["value"] == 0
    assert completed["disabled_bands"]["value"] == 1
    assert completed["graded_finished_24h"]["value"] == 1
    assert not any(code.startswith("GRADING_") for code in alerts)
    assert str(band.id) not in str(completed)
