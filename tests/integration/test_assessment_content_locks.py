"""Concurrent assessment reads still exclude content withdrawal and recheck approval."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.content import ContentError, ContentService
from services.domain.content import ItemVersion
from tests.integration.test_assessment import assessment as assessment_fixture

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def test_batched_plan_preserves_order_and_rechecks_every_reference(assessment):
    identity, _, _, body, versions, _ = assessment
    service = ContentService(identity)
    subject = UUID(body["subject_id"])
    ids = [UUID(version["id"]) for version in reversed(versions)]
    with Session(identity.engine) as db, db.begin():
        assert [v.id for v in service.assessment_versions(db, ids, subject)] == ids
    for invalid, target_subject in [
        ([], subject),
        ([ids[0], ids[0]], subject),
        ([uuid4() for _ in range(16)], subject),
        (ids + [uuid4()], subject),
        (ids, uuid4()),
    ]:
        with pytest.raises(ContentError), Session(identity.engine) as db, db.begin():
            service.assessment_versions(db, invalid, target_subject)
    with Session(identity.engine) as db:
        cached = db.get(ItemVersion, ids[0])
        assert cached.status == "APPROVED"
        with Session(identity.engine) as writer, writer.begin():
            row = writer.get(ItemVersion, ids[0])
            row.status = "RETIRED"
            row.revision += 1
        with pytest.raises(ContentError):
            service.assessment_versions(db, ids, subject)


@pytest.mark.parametrize("selection", ["version", "candidates", "batch"])
def test_readers_share_content_but_writer_still_cannot_change_it(assessment, selection):
    identity, _, _, body, versions, _ = assessment
    service = ContentService(identity)
    target, subject = UUID(versions[0]["id"]), UUID(body["subject_id"])

    def read(db):
        if selection == "version":
            return service.assessment_version(db, target, subject)
        if selection == "batch":
            return service.assessment_versions(db, [target], subject)
        return service.assessment_candidates(
            db, subject, UUID(body["document"]["topic_id"]), set(), 5
        )

    with Session(identity.engine) as first, first.begin():
        read(first)
        with Session(identity.engine) as second, second.begin():
            second.execute(text("SET LOCAL lock_timeout = '100ms'"))
            read(second)
            with pytest.raises(DBAPIError), Session(identity.engine) as writer, writer.begin():
                writer.scalar(
                    select(ItemVersion).where(ItemVersion.id == target).with_for_update(nowait=True)
                )
            with (
                pytest.raises(DBAPIError) as blocked,
                Session(identity.engine) as writer,
                writer.begin(),
            ):
                writer.execute(text("SET LOCAL lock_timeout = '100ms'"))
                writer.execute(
                    update(ItemVersion)
                    .where(ItemVersion.id == target)
                    .values(status="RETIRED", revision=ItemVersion.revision + 1)
                )
            assert blocked.value.orig.sqlstate == "55P03"
    with Session(identity.engine) as writer, writer.begin():
        assert (
            writer.scalar(
                select(ItemVersion).where(ItemVersion.id == target).with_for_update(nowait=True)
            )
            is not None
        )


def test_refresh_rejects_retirement_after_eligibility_read(assessment, monkeypatch):
    identity, _, _, body, versions, _ = assessment
    service = ContentService(identity)
    target, subject = UUID(versions[0]["id"]), UUID(body["subject_id"])
    eligible = service.eligible_version
    checked = Event()
    continue_reader = Event()

    def pause_after_eligibility(*args, **kwargs):
        value = eligible(*args, **kwargs)
        checked.set()
        assert continue_reader.wait(5)
        return value

    monkeypatch.setattr(service, "eligible_version", pause_after_eligibility)

    def reader():
        with Session(identity.engine) as db, db.begin():
            return service.assessment_version(db, target, subject)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(reader)
        try:
            assert checked.wait(5)
            with Session(identity.engine) as writer, writer.begin():
                row = writer.scalar(
                    select(ItemVersion).where(ItemVersion.id == target).with_for_update()
                )
                row.status = "RETIRED"
                row.revision += 1
            continue_reader.set()
            with pytest.raises(ContentError, match="CONTENT_NOT_APPROVED"):
                future.result(timeout=5)
        finally:
            continue_reader.set()


def test_manual_topic_filter_preserves_candidates_and_skips_unrelated_topics(
    assessment, monkeypatch
):
    identity, client, actors, body, _, plan = assessment
    service = AssessmentService(identity)
    actor = UUID(client.get("/api/v1/me", headers=actors["learner"]).json()["id"])
    subject, topic = UUID(body["subject_id"]), UUID(plan["topic_id"])
    calls = []
    original = service.content.assessment_candidates

    def observe(db, subject, topic, *args, **kwargs):
        calls.append((topic, args[1]))
        return original(db, subject, topic, *args, **kwargs)

    monkeypatch.setattr(service.content, "assessment_candidates", observe)
    with Session(identity.engine) as db:
        full = service.diagnostics.candidates(db, actor, subject)
        assert len(calls) > 1
        calls.clear()
        filtered = service.diagnostics.candidates(
            db, actor, subject, topic_id=topic, per_topic_limit=2
        )
        assert calls == [(topic, 2)]
        assert [v.id for v in filtered] == [v.id for v in full if v.topic_id == topic][:2]
        for limit in (0, 1001):
            with pytest.raises(ValueError):
                service.diagnostics.candidates(db, actor, subject, per_topic_limit=limit)
