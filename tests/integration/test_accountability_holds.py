"""Accountability holds preserve exact history without freezing normal parent workflows."""

import os
import subprocess
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.data_requests import LegalHold
from services.domain.flags import FlagHistory
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_flags import report, saved, triage
from tests.integration.test_legal_holds import hold, prepare

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def test_held_flag_history_allows_new_triage_and_keeps_old_revision_immutable(assessment):
    identity, client, actors, *_ = assessment
    flag = report(client, actors["learner"], saved(assessment)["attempt_id"]).json()
    with Session(identity.engine) as db:
        record = db.scalar(select(FlagHistory.id).where(FlagHistory.flag_id == UUID(flag["id"])))
    target, body = prepare(assessment)
    held = hold(
        client,
        actors["admin"],
        target,
        body | {"record_type": "FLAG_HISTORY", "record_id": str(record)},
    )
    assert held.status_code == 201, held.text
    detail = client.get(f"/api/v1/admin/content-flags/{flag['id']}", headers=actors["admin"]).json()
    updated = triage(client, actors["admin"], detail)
    assert updated.status_code == 200, updated.text
    with Session(identity.engine) as db:
        assert db.get(FlagHistory, record).revision == 1
        assert db.scalar(select(func.count()).select_from(FlagHistory)) == 2
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="append-only"):
        db.execute(
            text("UPDATE content_flag_history SET status='RESOLVED' WHERE id=:id"), {"id": record}
        )


@pytest.mark.parametrize("identity", ["0023"], indirect=True)
def test_upgrade_preserves_old_holds_and_adds_exact_review_target(content):
    identity, client, actors, _ = content
    target, body = prepare(content)
    key = str(uuid4())
    original = hold(client, actors["admin"], target, body, key)
    assert original.status_code == 201, original.text
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
        )
    assert hold(client, actors["admin"], target, body, key).json() == original.json()
    added = hold(client, actors["admin"], target, body | {"record_type": "DATA_REQUEST_REVIEW"})
    assert added.status_code == 201, added.text
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 2
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="Record is legally held"):
        db.execute(
            text("DELETE FROM data_request_reviews WHERE request_id=:id"), {"id": UUID(target)}
        )
