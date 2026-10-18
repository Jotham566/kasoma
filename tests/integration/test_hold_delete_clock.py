"""Real hold-wrapper timing without disabling original append-only protections."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError

from services.grading_publications import publish
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_grading_publications import publication_source as publication_fixture
from tests.integration.test_legal_holds import prepare

assessment = assessment_fixture
publication_source = publication_fixture
pytestmark = pytest.mark.integration
CASES = [
    ("protect_held_record", "DATA_REQUEST", "id", "data_subject_requests"),
    ("protect_held_grade", "GRADE", "attempt_id", "grades"),
    ("protect_held_request_review", "DATA_REQUEST_REVIEW", "request_id", "data_request_reviews"),
    (
        "protect_held_grading_publication",
        "GRADING_PUBLICATION",
        "attempt_id",
        "grading_publications",
    ),
]


@pytest.mark.parametrize("guard,kind,column,original_table", CASES)
def test_long_delete_transaction_observes_new_committed_hold(
    assessment, publication_source, guard, kind, column, original_table
):
    exercise_guard(assessment, publication_source, guard, kind, column, original_table)


def exercise_guard(assessment, publication_source, guard, kind, column, original_table):
    identity, band, attempt, _ = publication_source
    if kind == "GRADING_PUBLICATION":
        with identity.engine.begin() as connection:
            from sqlalchemy.orm import Session

            with Session(bind=connection) as db:
                publish(db, band.id, attempt, identity.clock())
    target, body = prepare(assessment)
    source = UUID(target) if kind in {"DATA_REQUEST", "DATA_REQUEST_REVIEW"} else attempt
    table = "hold_clock_probe_" + uuid4().hex
    arguments = "'DATA_REQUEST'" if guard == "protect_held_record" else ""
    decision, identifier = uuid4(), uuid4()
    with identity.engine.begin() as deleting:
        deleting.execute(
            text(f"CREATE TEMP TABLE {table}({column} uuid PRIMARY KEY) ON COMMIT DROP")
        )
        deleting.execute(text(f"INSERT INTO {table}({column}) VALUES (:id)"), {"id": source})
        deleting.execute(
            text(
                f"CREATE TRIGGER guard_probe BEFORE DELETE ON {table} FOR EACH ROW "
                f"EXECUTE FUNCTION {guard}({arguments})"
            )
        )
        began = deleting.scalar(select(func.transaction_timestamp()))
        with identity.engine.begin() as creating:
            creating.execute(
                text("""INSERT INTO legal_holds
                (id,request_id,record_type,record_id,decision_reference,reason,created_by,created_at,expires_at)
                SELECT :id,request_id,:kind,:source,:decision,'LEGAL_OBLIGATION',actor_id,
                  clock_timestamp(),:expires FROM data_request_reviews
                WHERE request_id=:request"""),
                {
                    "id": identifier,
                    "kind": kind,
                    "source": source,
                    "decision": decision,
                    "expires": datetime.fromisoformat(body["expires_at"]),
                    "request": UUID(target),
                },
            )
        assert not deleting.scalar(select(func.record_is_held(kind, source, began)))
        assert deleting.scalar(select(func.record_is_held(kind, source, func.clock_timestamp())))
        with pytest.raises(DBAPIError, match="Record is legally held"), deleting.begin_nested():
            deleting.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": source})
        assert deleting.scalar(text(f"SELECT count(*) FROM {table}")) == 1
        # Release only the synthetic decision at database time; never alter its scope.
        with identity.engine.begin() as releasing:
            releasing.execute(
                text("""UPDATE legal_holds SET released_at=clock_timestamp(),
                released_by=created_by,release_reference=:reference WHERE id=:id"""),
                {"reference": uuid4(), "id": identifier},
            )
        deleting.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": source})
        assert deleting.scalar(text(f"SELECT count(*) FROM {table}")) == 0
    # A released wrapper does not grant permission to erase original evidence.
    with identity.engine.begin() as protected, pytest.raises(DBAPIError) as denied:
        protected.execute(text(f"DELETE FROM {original_table} WHERE {column}=:id"), {"id": source})
    assert denied.value.orig.sqlstate == "P0001"


@pytest.mark.parametrize("identity", ["0035"], indirect=True)
def test_forward_upgrade_preserves_registered_hold_replay_and_historical_predicate(
    assessment, publication_source
):
    import os
    import subprocess

    from tests.integration.test_legal_holds import hold

    identity, client, actors, *_ = assessment
    target, body = prepare(assessment)
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
    exercise_guard(
        assessment, publication_source, "protect_held_grade", "GRADE", "attempt_id", "grades"
    )
