"""ADR-057 additive upgrade and real SQL disposal/decision serialization."""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.channel_preservation import dispose_bodies
from services.domain.messaging import ConversationState
from services.whatsapp_linking import channel_lock
from tests.integration.test_channel_preservation import (
    capture,
    channel_source,
    checked_capture,
)
from tests.integration.test_legal_holds import hold, prepare, release

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("identity", ["0037"], indirect=True)
def test_upgrade_assigns_versions_without_changing_state_or_existing_holds(identity, content):
    owner, client, actors, *_ = content
    link, actor = channel_source(content)
    target, body = prepare(content)
    created = hold(client, actors["admin"], target, body)
    assert created.status_code == 201, created.text
    with owner.engine.begin() as db:
        db.execute(
            text("""INSERT INTO conversation_states(link_id,actor_id,link_revision,
          updated_at,expires_at) VALUES(:link,:actor,1,:at,
            CAST(:at AS timestamptz)+interval '24 hours')"""),
            {"link": link, "actor": actor, "at": owner.clock()},
        )
    for _ in range(2):
        subprocess.run(
            ["make", "migrate"],
            env=os.environ | {"DATABASE_URL": owner.settings.database_url.get_secret_value()},
            capture_output=True,
            check=True,
        )
    with Session(owner.engine) as db:
        row = db.get(ConversationState, link)
        assert row.actor_id == actor and row.link_revision == 1
        assert row.updated_at == owner.clock()
        assert row.expires_at - row.updated_at == timedelta(hours=24)
        assert row.state_version > 0
        first = row.state_version
    with owner.engine.begin() as db:
        next_version = db.scalar(
            text(
                "UPDATE conversation_states SET state_version=0 "
                "WHERE link_id=:id RETURNING state_version"
            ),
            {"id": link},
        )
        assert next_version > first
    with pytest.raises(DBAPIError, match="legally held"), owner.engine.begin() as db:
        db.execute(text("DELETE FROM data_subject_requests WHERE id=:id"), {"id": UUID(target)})


def test_uncommitted_sql_decision_locks_evidence_out_of_cleanup(content):
    owner, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    created = capture(client, actors["admin"], target, body)
    assert created.status_code == 201, created.text
    original = created.json()
    assert release(client, actors["admin"], target, original["id"]).status_code == 200
    actor = UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"])
    snapshot = UUID(original["record_id"])
    inserted, finish = Event(), Event()
    additional = uuid4()

    def write():
        with owner.engine.begin() as db:
            db.execute(
                text("""INSERT INTO legal_holds(id,request_id,record_type,record_id,
              decision_reference,reason,created_by,created_at,expires_at)
              VALUES(:id,:request,'CHANNEL_LINK_SNAPSHOT',:snapshot,:reference,
                'LEGAL_OBLIGATION',:actor,clock_timestamp(),clock_timestamp()+interval '1 day')"""),
                {
                    "id": additional,
                    "request": UUID(target),
                    "snapshot": snapshot,
                    "reference": uuid4(),
                    "actor": actor,
                },
            )
            inserted.set()
            assert finish.wait(5), "Bounded fixture transaction was not released"

    with ThreadPoolExecutor(max_workers=1) as pool:
        writing = pool.submit(write)
        try:
            assert inserted.wait(5)
            with Session(owner.engine) as db, db.begin():
                channel_lock(owner, db)
                assert dispose_bodies(db) == 0
        finally:
            finish.set()
        writing.result(timeout=5)
    with Session(owner.engine) as db, db.begin():
        channel_lock(owner, db)
        assert dispose_bodies(db) == 0
    assert release(client, actors["admin"], target, str(additional)).status_code == 200
    with Session(owner.engine) as db, db.begin():
        channel_lock(owner, db)
        assert dispose_bodies(db) == 1
