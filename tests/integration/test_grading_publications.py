"""Publication substrate with valid synthetic objective grades, not AI acceptance."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from scripts.grading_fixtures import unapproved_band
from services.data_export_projection import project
from services.deletion_preview import inventory
from services.domain.assessment import Attempt
from services.domain.content import ItemVersion
from services.domain.curriculum import Topic
from services.domain.grading_audits import (
    GradingAuditAssignment,
    GradingPublication,
    GradingPublicationCounter,
)
from services.domain.identity import User
from services.grading_band_store import disable, register
from services.grading_publications import publish
from services.short_text_eligibility import GradingScope
from tests.integration.test_assessment import (
    answer,
    next_item,
    start,
)
from tests.integration.test_assessment import (
    assessment as assessment_fixture,
)
from tests.integration.test_data_requests import claim, create
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture
from tests.integration.test_diagnostics import (
    next_item as diagnostic_next,
)
from tests.integration.test_diagnostics import start as start_diagnostic
from tests.integration.test_diagnostics import (
    submit as diagnostic_submit,
)
from tests.integration.test_grading_bands import activate_synthetic
from tests.integration.test_identity import consent, profile
from tests.integration.test_legal_holds import hold, prepare, release

assessment = assessment_fixture
diagnostic = diagnostic_fixture
pytestmark = pytest.mark.integration


def test_diagnostic_publication_and_audit_stay_sealed_until_completion(diagnostic):
    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    session = start_diagnostic(client, headers, body["subject_id"]).json()["id"]
    response = diagnostic_submit(
        client, headers, session, diagnostic_next(client, headers, session)
    )
    assert response.status_code == 200, response.text
    attempt_id = UUID(response.json()["attempt_id"])
    with Session(identity.engine) as db, db.begin():
        attempt = db.get(Attempt, attempt_id)
        owner = attempt.learner_id
        version = db.get(ItemVersion, attempt.item_version_id)
        band = unapproved_band(
            GradingScope(
                subject_id=UUID(body["subject_id"]),
                topic_id=version.topic_id,
                language="en",
                model_version="fake-v1",
                prompt_version="synthetic-v2",
                configuration_version="test-v1",
            )
        ).model_copy(
            update={
                "approval_id": uuid4(),
                "approved_at": identity.clock(),
                "subgroup_review": "APPROVED",
            }
        )
        register(db, band, identity.clock())
        activate_synthetic(db, band, identity.clock())
        publish(db, band.id, attempt_id, identity.clock())
    with Session(identity.engine) as db:
        sealed = project(identity, db, owner, uuid4()).records
        assert sealed["grading_publications"] == sealed["grading_audit_assignments"] == []
    for _ in range(14):
        response = diagnostic_submit(
            client, headers, session, diagnostic_next(client, headers, session)
        )
        assert response.status_code == 200, response.text
    with Session(identity.engine) as db:
        released = project(identity, db, owner, uuid4()).records
        assert (
            len(released["grading_publications"]) == len(released["grading_audit_assignments"]) == 1
        )


@pytest.fixture
def publication_source(assessment):
    identity, client, actors, _, _, plan = assessment
    band = unapproved_band(
        GradingScope(
            subject_id=UUID(plan["subject_id"]),
            topic_id=UUID(plan["topic_id"]),
            language="en",
            model_version="fake-v1",
            prompt_version="synthetic-v2",
            configuration_version="test-v1",
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
    session = start(client, actors["learner"], plan).json()["id"]
    item = next_item(client, actors["learner"], session)
    grade = answer(client, actors["learner"], session, item)
    assert grade.status_code == 200, grade.text
    return identity, band, UUID(grade.json()["attempt_id"]), session


def test_atomic_sampling_and_duplicate_concurrent_publication(publication_source):
    identity, band, attempt, _ = publication_source

    def send(_):
        with Session(identity.engine) as db, db.begin():
            row = publish(db, band.id, attempt, identity.clock())
            return row.ordinal, row.audit_required

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(send, range(2))) == [(1, True), (1, True)]
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(GradingPublication)) == 1
        assert db.scalar(select(func.count()).select_from(GradingAuditAssignment)) == 1
        count = db.get(GradingPublicationCounter, band.id)
        assert (count.returned_grades, count.assigned_audits) == (1, 1)


def test_eleven_publications_allocate_two_audits_without_reusing_ordinals(
    publication_source, assessment
):
    identity, band, first, session = publication_source
    _, client, actors, _, _, plan = assessment
    attempts = [first]
    for _ in range(4):
        item = next_item(client, actors["learner"], session)
        response = answer(client, actors["learner"], session, item)
        assert response.status_code == 200, response.text
        attempts.append(UUID(response.json()["attempt_id"]))
    for label, count in [("other", 5), ("reviewer", 1)]:
        profile(client, actors[label], "2000-01-01")
        assert consent(client, actors[label], "SELF").status_code == 200
        created = start(client, actors[label], plan)
        assert created.status_code == 201, created.text
        for _ in range(count):
            item = next_item(client, actors[label], created.json()["id"])
            response = answer(client, actors[label], created.json()["id"], item)
            assert response.status_code == 200, response.text
            attempts.append(UUID(response.json()["attempt_id"]))
    for ordinal, attempt in enumerate(attempts, start=1):
        with Session(identity.engine) as db, db.begin():
            row = publish(db, band.id, attempt, identity.clock())
            assert row.ordinal == ordinal
            assert row.audit_required == (ordinal in {1, 11})
            counter = db.get(GradingPublicationCounter, band.id)
            assert counter.returned_grades == ordinal
            assert counter.assigned_audits == (ordinal + 9) // 10
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(GradingAuditAssignment)) == 2


def test_rollback_covers_publication_counter_and_assignment(publication_source):
    identity, band, attempt, _ = publication_source
    with Session(identity.engine) as db:
        publish(db, band.id, attempt, identity.clock())
        db.rollback()
    with Session(identity.engine) as db:
        assert db.get(GradingPublication, attempt) is None
        assert db.get(GradingPublicationCounter, band.id).returned_grades == 0
        assert db.scalar(select(func.count()).select_from(GradingAuditAssignment)) == 0
    with Session(identity.engine) as db, db.begin():
        assert publish(db, band.id, attempt, identity.clock()).ordinal == 1


def test_invalid_publication_does_not_consume_an_ordinal(publication_source):
    identity, band, attempt, _ = publication_source
    with Session(identity.engine) as db, pytest.raises(ValueError, match="timezone"):
        publish(db, band.id, attempt, identity.clock().replace(tzinfo=None))
    for target, timestamp, message in (
        (uuid4(), identity.clock(), "definitive grade"),
        (attempt, identity.clock() - timedelta(seconds=1), "Enabled current band"),
    ):
        with Session(identity.engine) as db, pytest.raises(DBAPIError, match=message):
            publish(db, band.id, target, timestamp)
    with Session(identity.engine) as db, db.begin():
        assert publish(db, band.id, attempt, identity.clock()).ordinal == 1


def test_publication_rejects_grade_from_another_calibration_scope(publication_source):
    identity, band, attempt, _ = publication_source
    with Session(identity.engine) as db, db.begin():
        topic = db.scalar(select(Topic).where(Topic.id != band.scope.topic_id))
        other = band.model_copy(
            update={
                "id": uuid4(),
                "scope": band.scope.model_copy(
                    update={"subject_id": topic.subject_id, "topic_id": topic.id}
                ),
            }
        )
        register(db, other, identity.clock())
        activate_synthetic(db, other, identity.clock())
    with Session(identity.engine) as db, pytest.raises(DBAPIError, match="definitive grade"):
        publish(db, other.id, attempt, identity.clock())
    with Session(identity.engine) as db, db.begin():
        assert db.get(GradingPublicationCounter, other.id).returned_grades == 0
        assert publish(db, band.id, attempt, identity.clock()).ordinal == 1
    with Session(identity.engine) as db, pytest.raises(ValueError, match="Conflicting"):
        publish(db, other.id, attempt, identity.clock())


def test_unsampled_publication_cannot_receive_a_forged_assignment(publication_source, assessment):
    identity, band, attempt, session = publication_source
    _, client, actors, *_ = assessment
    response = answer(
        client, actors["learner"], session, next_item(client, actors["learner"], session)
    )
    assert response.status_code == 200, response.text
    other = UUID(response.json()["attempt_id"])
    with Session(identity.engine) as db, db.begin():
        publish(db, band.id, attempt, identity.clock())
        assert not publish(db, band.id, other, identity.clock()).audit_required
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="sampled publication"):
        db.execute(
            text("INSERT INTO grading_audit_assignments(attempt_id,assigned_at) VALUES(:id,:now)"),
            {"id": other, "now": identity.clock()},
        )


def test_disabled_band_blocks_new_publication_but_preserves_replay(publication_source, assessment):
    identity, band, attempt, session = publication_source
    _, client, actors, *_ = assessment
    with Session(identity.engine) as db, db.begin():
        publish(db, band.id, attempt, identity.clock())
        disable(db, band.id, identity.clock(), "CRITICAL_ERROR")
    with Session(identity.engine) as db, db.begin():
        assert publish(db, band.id, attempt, identity.clock()).ordinal == 1
    response = answer(
        client, actors["learner"], session, next_item(client, actors["learner"], session)
    )
    other = UUID(response.json()["attempt_id"])
    with Session(identity.engine) as db, pytest.raises(ValueError, match="disabled"):
        publish(db, band.id, other, identity.clock())
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="Enabled current band"):
        db.execute(
            text("""INSERT INTO grading_publications
            VALUES(:attempt,:band,10,false,:now)"""),
            {"attempt": other, "band": band.id, "now": identity.clock()},
        )


def test_counter_and_immutable_records_cannot_be_forged(publication_source):
    identity, band, attempt, _ = publication_source
    with Session(identity.engine) as db, db.begin():
        publish(db, band.id, attempt, identity.clock())
    for sql in (
        "UPDATE grading_publication_counters SET returned_grades=0,assigned_audits=0",
        "UPDATE grading_publication_counters SET returned_grades=returned_grades+1",
        "DELETE FROM grading_publication_counters",
        "UPDATE grading_publications SET ordinal=ordinal",
        "DELETE FROM grading_publications",
        "UPDATE grading_audit_assignments SET assigned_at=assigned_at",
        "DELETE FROM grading_audit_assignments",
    ):
        with identity.engine.begin() as db, pytest.raises(DBAPIError):
            db.execute(text(sql))


def test_owned_projection_minimizes_and_inventory_includes_both_records(publication_source):
    identity, band, attempt, _ = publication_source
    with Session(identity.engine) as db, db.begin():
        publish(db, band.id, attempt, identity.clock())
    with Session(identity.engine) as db:
        owner = db.get(Attempt, attempt).learner_id
        own = project(identity, db, owner, uuid4())
        assert len(own.records["grading_publications"]) == 1
        assert set(own.records["grading_publications"][0]) == {"attempt_id", "published_at"}
        assert len(own.records["grading_audit_assignments"]) == 1
        assert set(own.records["grading_audit_assignments"][0]) == {
            "id",
            "attempt_id",
            "assigned_at",
        }
        assert str(band.id) not in own.model_dump_json()
        assert "ordinal" not in own.model_dump_json()
        other = db.scalar(select(User.id).where(User.id != owner).limit(1))
        foreign = project(identity, db, other, uuid4())
        assert (
            foreign.records["grading_publications"]
            == foreign.records["grading_audit_assignments"]
            == []
        )
        counts = {row.source: row.count for row in inventory(db, owner)}
        assert counts["grading_publications"] == counts["grading_audit_assignments"] == 1


@pytest.mark.parametrize("kind", ["GRADING_PUBLICATION", "GRADING_AUDIT"])
def test_exact_holds_independent_ownership_and_immutable_release(
    publication_source, assessment, kind
):
    identity, band, attempt, _ = publication_source
    _, client, actors, *_ = assessment
    with Session(identity.engine) as db, db.begin():
        publish(db, band.id, attempt, identity.clock())
        audit = db.scalar(select(GradingAuditAssignment.id))
    target, body = prepare(assessment)
    record = attempt if kind == "GRADING_PUBLICATION" else audit
    body |= {"record_type": kind, "record_id": str(record)}
    key = str(uuid4())
    result = hold(client, actors["admin"], target, body, key)
    assert result.status_code == 201, result.text
    assert hold(client, actors["admin"], target, body, key).json() == result.json()
    for label in ("learner", "support", "reviewer"):
        assert hold(client, actors[label], target, body).status_code == 403
    foreign = create(client, actors["other"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], foreign).status_code == 200
    assert hold(client, actors["admin"], foreign, body).status_code == 404
    table, column = (
        ("grading_publications", "attempt_id")
        if kind == "GRADING_PUBLICATION"
        else ("grading_audit_assignments", "id")
    )
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="Record is legally held"):
        db.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": record})
    assert release(client, actors["admin"], target, result.json()["id"]).status_code == 200
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="immutable"):
        db.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": record})
