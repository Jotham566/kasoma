"""Durable substrate using valid synthetic ungraded attempts; not short-text delivery acceptance."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.assessment import AssessmentSession, Attempt, Grade
from services.domain.grading_work import GradingHistory, GradingWorkRow
from services.grading_work_store import claim_next, enqueue, expire_due, finish_neutral
from services.short_text_workflow import WorkflowError
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_assessment import next_item, start

assessment = assessment_fixture
pytestmark = pytest.mark.integration


@pytest.fixture
def ungraded(assessment):
    identity, client, actors, _, _, plan = assessment
    session = start(client, actors["learner"], plan).json()
    item = next_item(client, actors["learner"], session["id"])
    attempt_id = uuid4()
    with Session(identity.engine) as db, db.begin():
        owner = db.get(AssessmentSession, UUID(session["id"])).learner_id
        # This valid ungraded objective attempt exercises storage independently of format
        # enablement. No trigger is disabled and no learner short-text approval is implied.
        db.add(
            Attempt(
                id=attempt_id,
                learner_id=owner,
                session_item_id=UUID(item["session_item_id"]),
                item_version_id=UUID(item["item_version_id"]),
                choice_id="A",
                response=None,
                submitted_at=identity.clock(),
                hint_count=0,
                highest_hint_level=0,
                channel="WEB",
            )
        )
    return identity, attempt_id


def test_atomic_queue_replay_and_only_one_concurrent_claim(ungraded):
    identity, attempt = ungraded
    now = identity.clock()
    correlation = uuid4()
    with Session(identity.engine) as db, db.begin():
        original = enqueue(db, attempt, correlation, now)
    with Session(identity.engine) as db, db.begin():
        assert enqueue(db, attempt, uuid4(), now + timedelta(seconds=1)) == original
        assert db.get(GradingWorkRow, attempt).correlation_id == correlation

    def claim(_):
        with Session(identity.engine) as db, db.begin():
            return claim_next(db, now)

    with ThreadPoolExecutor(max_workers=2) as executor:
        claims = list(executor.map(claim, range(2)))
    live = [claim for claim in claims if claim is not None]
    assert len(live) == 1
    state = live[0]
    with Session(identity.engine) as db, db.begin():
        finished = finish_neutral(db, attempt, state.claim_id, now + timedelta(seconds=1))
    with Session(identity.engine) as db, db.begin():
        assert finish_neutral(db, attempt, state.claim_id, now + timedelta(seconds=2)) == finished
        assert claim_next(db, now + timedelta(seconds=2)) is None
        assert db.scalar(select(func.count()).select_from(Grade)) == 0
        history = list(db.scalars(select(GradingHistory).order_by(GradingHistory.revision)))
        assert [h.snapshot["status"] for h in history] == ["QUEUED", "RUNNING", "LOW_CONFIDENCE"]
        assert [h.revision for h in history] == [1, 2, 3]


def test_rollback_removes_command_and_triggered_history(ungraded):
    identity, attempt = ungraded
    with Session(identity.engine) as db:
        enqueue(db, attempt, uuid4(), identity.clock())
        db.rollback()
    with Session(identity.engine) as db:
        assert db.get(GradingWorkRow, attempt) is None
        assert db.scalar(select(func.count()).select_from(GradingHistory)) == 0


def test_lease_expiry_is_durable_and_late_worker_cannot_publish(ungraded):
    identity, attempt = ungraded
    with Session(identity.engine) as db, db.begin():
        enqueue(db, attempt, uuid4(), identity.clock())
        running = claim_next(db, identity.clock())
    with Session(identity.engine) as db, db.begin():
        assert expire_due(db, running.lease_until) == 1
        assert expire_due(db, running.lease_until) == 0
    with Session(identity.engine) as db, db.begin(), pytest.raises(WorkflowError):
        finish_neutral(db, attempt, running.claim_id, running.lease_until)
    with Session(identity.engine) as db:
        result = db.get(GradingWorkRow, attempt)
        assert result.status == "LOW_CONFIDENCE" and result.reason == "WORKER_EXPIRED"
        assert db.scalar(select(func.count()).select_from(Grade)) == 0


def test_database_rejects_lease_renewal_identity_changes_and_history_mutation(ungraded):
    identity, attempt = ungraded
    with Session(identity.engine) as db, db.begin():
        enqueue(db, attempt, uuid4(), identity.clock())
        claim_next(db, identity.clock())
    commands = [
        "UPDATE assessment_grading_work SET lease_until=lease_until+interval '1 second'",
        "UPDATE assessment_grading_work SET queued_at=queued_at-interval '1 second'",
        "UPDATE assessment_grading_work SET correlation_id=gen_random_uuid()",
        "UPDATE assessment_grading_work SET status='QUEUED',revision=revision+1",
        "UPDATE assessment_grading_work SET status='GRADED',"
        "finished_at=claimed_at,revision=revision+1",
        "DELETE FROM assessment_grading_work",
        "UPDATE assessment_grading_history SET snapshot='{}'::jsonb",
        "DELETE FROM assessment_grading_history",
        "INSERT INTO assessment_grading_history(attempt_id,revision,snapshot) "
        "SELECT attempt_id,3,'{}'::jsonb FROM assessment_grading_work",
    ]
    for command in commands:
        with identity.engine.begin() as db, pytest.raises(DBAPIError):
            db.execute(text(command))


def test_unclaimed_queue_expiry_and_claim_rollback(ungraded):
    identity, attempt = ungraded
    with Session(identity.engine) as db, db.begin():
        enqueue(db, attempt, uuid4(), identity.clock())
    with Session(identity.engine) as db:
        assert claim_next(db, identity.clock()) is not None
        db.rollback()  # No model dispatch is allowed before this transaction commits.
    at = identity.clock() + timedelta(minutes=5)
    with Session(identity.engine) as db, db.begin():
        assert claim_next(db, at) is None
        assert expire_due(db, at, limit=1) == 1
        assert db.get(GradingWorkRow, attempt).reason == "QUEUE_EXPIRED"


def test_owned_inventory_and_minimized_export_projection(ungraded):
    from services.data_export_projection import project
    from services.deletion_preview import inventory

    identity, attempt = ungraded
    with Session(identity.engine) as db, db.begin():
        owner = db.get(Attempt, attempt).learner_id
        correlation = uuid4()
        enqueue(db, attempt, correlation, identity.clock())
        running = claim_next(db, identity.clock())
        finish_neutral(db, attempt, running.claim_id, identity.clock())
    with Session(identity.engine) as db:
        counts = {row.source: row.count for row in inventory(db, owner)}
        assert counts["assessment_grading_work"] == 1
        assert counts["assessment_grading_history"] == 3
        exported = project(identity, db, owner, uuid4())
        assert len(exported.records["grading_work"]) == 1
        assert len(exported.records["grading_history"]) == 3
        raw = exported.model_dump_json()
        assert str(correlation) not in raw and str(running.claim_id) not in raw
        assert "NOT_ELIGIBLE" not in raw
        # A different existing user's projection must contain none of this work.
        from services.domain.identity import User

        other = db.scalar(select(User.id).where(User.id != owner).limit(1))
        foreign = project(identity, db, other, uuid4())
        assert foreign.records["grading_work"] == foreign.records["grading_history"] == []


def test_grade_commit_requires_atomic_work_publication(ungraded):
    from services.content_contracts import DraftDocument
    from services.domain.content import ItemVersion
    from services.grading import grade_choice

    identity, attempt_id = ungraded
    with Session(identity.engine) as db, db.begin():
        enqueue(db, attempt_id, uuid4(), identity.clock())
        claim_next(db, identity.clock())
    with pytest.raises(DBAPIError, match="publication must be atomic"):
        with Session(identity.engine) as db, db.begin():
            attempt = db.get(Attempt, attempt_id)
            version = db.get(ItemVersion, attempt.item_version_id)
            result = grade_choice(
                attempt_id, version.id, DraftDocument.model_validate(version.document), "A"
            )
            db.add(
                Grade(
                    attempt_id=attempt_id,
                    item_version_id=version.id,
                    answer_specification_hash=version.content_hash,
                    result=result.model_dump(mode="json"),
                )
            )
    with Session(identity.engine) as db:
        assert db.get(Grade, attempt_id) is None
        assert db.get(GradingWorkRow, attempt_id).status == "RUNNING"
