"""NFR-PERF-001/002: avoid empty reads only for a genuinely new locked revision."""

from contextlib import contextmanager
from uuid import uuid4

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.assessment_contracts import StartRevision
from services.domain.assessment import AssessmentSession
from tests.integration.test_assessment import answer, next_item, start
from tests.integration.test_channel_assessment import actor_id, ready

pytestmark = pytest.mark.integration


@contextmanager
def response_reads(engine):
    """Collect operation labels only, never SQL parameters, bodies or identifiers."""
    reads = []

    def observe(connection, cursor, statement, parameters, context, many):
        sql = " ".join(statement.lower().split())
        if sql.startswith("select "):
            if "from session_items join attempts " in sql:
                reads.append("answers")
            if "from reassessments " in sql:
                reads.append("reassessment")

    event.listen(engine, "after_cursor_execute", observe)
    try:
        yield reads
    finally:
        event.remove(engine, "after_cursor_execute", observe)


@pytest.mark.parametrize(
    "mode,channel", [("TOPIC", "WEB"), ("RECOMMENDED", "WEB"), ("TOPIC", "WHATSAPP")]
)
def test_new_revision_has_full_committed_view_without_empty_response_reads(content, mode, channel):
    identity, client, actors, _, _, plan = ready(content)
    service = AssessmentService(identity)
    actor = actor_id(client, actors["learner"])
    if mode == "RECOMMENDED":
        plan = plan | {"mode": mode, "topic_id": None}
    key = uuid4()
    with response_reads(identity.engine) as reads:
        with Session(identity.engine) as db, db.begin():
            fresh = service.start_in_transaction(
                db, actor, StartRevision.model_validate(plan), key, uuid4(), channel=channel
            )
    assert reads == []
    assert fresh.kind == "REVISION"
    assert fresh.answered_count == 0 and fresh.answers == []
    assert fresh.original_attempt_id is None and fresh.original_session_id is None
    # Compare the complete serialized contract against an independent, committed DB read.
    with Session(identity.engine) as db, db.begin():
        session = db.get(AssessmentSession, fresh.id)
        assert session is not None
        committed = service.view(db, session)
    assert fresh.model_dump(mode="json") == committed.model_dump(mode="json")
    # Both the exact receipt and a new key resuming an active plan retain current DB reads.
    for resume_key in (key, uuid4()):
        with response_reads(identity.engine) as reads:
            with Session(identity.engine) as db, db.begin():
                resumed = service.start_in_transaction(
                    db,
                    actor,
                    StartRevision.model_validate(plan),
                    resume_key,
                    uuid4(),
                    channel=channel,
                )
        assert reads == ["answers", "reassessment"]
        assert resumed.model_dump(mode="json") == fresh.model_dump(mode="json")


def test_existing_answer_never_becomes_a_fresh_empty_response(content):
    identity, client, actors, _, _, plan = ready(content)
    headers = actors["learner"]
    key = str(uuid4())
    created = start(client, headers, plan, key)
    assert created.status_code == 201
    session = created.json()["id"]
    item = next_item(client, headers, session)
    submitted = answer(client, headers, session, item)
    assert submitted.status_code == 200
    for resume_key in (key, str(uuid4())):
        with response_reads(identity.engine) as reads:
            resumed = start(client, headers, plan, resume_key)
        assert resumed.status_code == 201
        assert reads == ["answers", "reassessment"]
        assert resumed.json()["id"] == session
        assert resumed.json()["answered_count"] == 1
        assert resumed.json()["answers"][0]["session_item_id"] == item["session_item_id"]
        assert resumed.json()["answers"][0]["grade"] == submitted.json()
