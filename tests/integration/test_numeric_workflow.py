"""FR-GRD-002 and CNT-004/005: reviewed numeric content through durable grades."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.assessment import AssessmentEvent, Attempt, Grade
from tests.contract.test_numeric import spec
from tests.integration.test_assessment import next_item, start
from tests.integration.test_content import create, mutate, review, submit

pytestmark = pytest.mark.integration


def numeric_document(body):
    return body["document"] | {
        "response_type": "NUMERIC",
        "choices": [],
        "correct_choice_id": "",
        "numeric_spec": spec(
            accepted_forms=["DECIMAL", "SCIENTIFIC"],
            significant_figures_policy="EXACT",
            significant_figures=3,
        ).model_dump(),
        "worked_solution": "Synthetic example: 100 cm is 1.00 m, with three significant figures.",
    }


@pytest.fixture
def numeric(content):
    identity, client, actors, body = content
    versions = []
    for index in range(5):
        document = numeric_document(body) | {"title": f"Numeric synthetic fixture {index}"}
        response = review(
            client,
            actors,
            submit(client, actors, create(client, actors, body | {"document": document})),
        )
        assert response.status_code == 200, response.text
        versions.append(response.json())
    headers = actors["learner"]
    assert (
        client.patch(
            "/api/v1/me",
            headers=headers,
            json={
                "display_name": "Synthetic numeric learner",
                "birth_date": "2000-01-01",
                "subject_ids": [body["subject_id"]],
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/me/consents",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={
                "consent_type": "SELF",
                "policy_version": identity.settings.consent_policy_version,
                "affirmative": True,
            },
        ).status_code
        == 200
    )
    plan = {
        "subject_id": body["subject_id"],
        "topic_id": body["document"]["topic_id"],
        "desired_item_count": 5,
    }
    return identity, client, actors, body, versions, plan


def numeric_answer(client, headers, session, item, value, unit="m", key=None):
    return client.post(
        f"/api/v1/sessions/{session}/attempts",
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json={
            "session_item_id": item["session_item_id"],
            "response": {"type": "NUMERIC", "value": value, "unit": unit},
        },
    )


def test_numeric_grade_replay_solution_and_immutable_history(numeric):
    identity, client, actors, body, versions, plan = numeric
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    assert item["response_spec"]["type"] == "NUMERIC"
    for forbidden in [
        "expected_value",
        "absolute_tolerance",
        "relative_tolerance",
        "factor",
        "offset",
        "numeric_spec",
    ]:
        assert forbidden not in str(item)
    key = str(uuid4())
    result = numeric_answer(client, headers, session, item, "1.00e2", "cm", key)
    assert result.status_code == 200, result.text
    grade = result.json()
    assert grade["score"] == 1 and grade["grader_version"] == "numeric-rational-v1"
    assert numeric_answer(client, headers, session, item, "1.00e2", "cm", key).json() == grade
    assert numeric_answer(client, headers, session, item, "100", "cm", key).status_code == 409
    assert numeric_answer(client, headers, session, item, "1.00", "m").status_code == 409
    next_ = next_item(client, headers, session)
    wrong_precision = numeric_answer(client, headers, session, next_, "1", "m")
    assert wrong_precision.status_code == 200 and wrong_precision.json()["score"] == 0
    assert wrong_precision.json()["feedback"]["correct_elements"]
    assert wrong_precision.json()["feedback"]["missing_elements"]
    version = next(v for v in versions if v["id"] == grade["item_version_id"])
    assert (
        mutate(
            client,
            f"item-versions/{version['id']}/retire",
            actors["reviewer"],
            {"expected_revision": version["revision"], "reason": "Numeric history test"},
        ).status_code
        == 200
    )
    successor = create(
        client,
        actors,
        body
        | {
            "source_version_id": version["id"],
            "document": numeric_document(body)
            | {"numeric_spec": spec(expected_value="2").model_dump()},
        },
    )
    assert successor["version"] == 2
    assert (
        client.get(f"/api/v1/attempts/{grade['attempt_id']}/grade", headers=headers).json() == grade
    )
    assert (
        client.get(f"/api/v1/attempts/{grade['attempt_id']}/solution", headers=headers).json()[
            "item_version_id"
        ]
        == version["id"]
    )
    with Session(identity.engine) as db:
        attempt = db.get(Attempt, UUID(grade["attempt_id"]))
        assert attempt.choice_id is None
        assert attempt.response == {"type": "NUMERIC", "value": "1.00e2", "unit": "cm"}
        assert (
            db.scalar(
                select(func.count())
                .select_from(AssessmentEvent)
                .where(AssessmentEvent.type == "attempt.graded")
            )
            == 2
        )
        assert db.get(Grade, attempt.id).answer_specification_hash
    with pytest.raises(DBAPIError), identity.engine.begin() as connection:
        connection.execute(text("UPDATE attempts SET response='{}'"))


def test_invalid_numeric_submissions_never_create_evidence(numeric):
    identity, client, actors, body, versions, plan = numeric
    headers = actors["learner"]
    session = start(client, headers, plan).json()["id"]
    item = next_item(client, headers, session)
    for value, unit in [
        ("NaN", "m"),
        ("1/1", "m"),
        ("1.00", "M"),
        ("1e99", "m"),
        ("1+0", "m"),
        ("1.00", ""),
    ]:
        result = numeric_answer(client, headers, session, item, value, unit)
        assert result.status_code == 422, result.text
        assert value not in result.json()["error"]["message"]
    assert (
        client.post(
            f"/api/v1/sessions/{session}/attempts",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={"session_item_id": item["session_item_id"], "response": {"choice_id": "A"}},
        ).status_code
        == 422
    )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
        assert db.scalar(select(func.count()).select_from(Grade)) == 0
    assert numeric_answer(client, headers, session, item, "1.00").status_code == 200


@pytest.mark.parametrize(
    "change,field",
    [
        ({"numeric_spec": None}, "numeric_spec"),
        (
            {"numeric_spec": spec(absolute_tolerance="-1").model_dump()},
            "numeric_spec.absolute_tolerance",
        ),
        (
            {
                "numeric_spec": spec(
                    units=[{"label": "m", "factor": "0", "offset": "0"}]
                ).model_dump()
            },
            "numeric_spec.units",
        ),
        (
            {
                "numeric_spec": spec(
                    significant_figures_policy="EXACT", significant_figures=3
                ).model_dump()
            },
            "numeric_spec.significant_figures",
        ),
        ({"correct_choice_id": "A"}, "choices"),
    ],
)
def test_invalid_numeric_publication_is_field_specific(content, change, field):
    identity, client, actors, body = content
    version = create(client, actors, body | {"document": numeric_document(body) | change})
    result = mutate(
        client,
        f"item-versions/{version['id']}/submit",
        actors["author"],
        {"expected_revision": version["revision"], "reason": "Invalid numeric specification"},
    )
    assert result.status_code == 409
    assert field in {f["field"] for f in result.json()["error"]["field_errors"]}


@pytest.mark.parametrize("identity", ["0004"], indirect=True)
def test_numeric_migration_preserves_existing_choice_attempts(content):
    import json
    import os
    import subprocess
    from datetime import timedelta

    from services.content_contracts import DraftDocument
    from services.grading import grade_choice

    identity, client, actors, body = content
    version = review(client, actors, submit(client, actors, create(client, actors, body))).json()
    token = actors["learner"]["Authorization"][7:]
    learner = identity.me(token).id
    session_id, item_id, attempt_id = uuid4(), uuid4(), uuid4()
    grade = grade_choice(
        attempt_id, UUID(version["id"]), DraftDocument.model_validate(version["document"]), "A"
    )
    params = {
        "session": session_id,
        "item": item_id,
        "attempt": attempt_id,
        "learner": learner,
        "subject": UUID(body["subject_id"]),
        "topic": UUID(body["document"]["topic_id"]),
        "version": UUID(version["id"]),
        "now": identity.clock(),
        "expiry": identity.clock() + timedelta(days=7),
        "result": json.dumps(grade.model_dump(mode="json")),
    }
    with identity.engine.begin() as connection:
        # This is the exact legacy choice representation, before numeric storage exists.
        connection.execute(
            text("""INSERT INTO assessment_sessions
          (id,learner_id,subject_id,topic_id,status,item_count,reason,plan_version,started_at,expires_at)
          VALUES (:session,:learner,:subject,:topic,'ACTIVE',5,
            'Synthetic legacy','topic-choice-v1',:now,:expiry)
        """),
            params,
        )
        connection.execute(
            text("""INSERT INTO session_items
          (id,session_id,item_version_id,position,reason,served_at)
          VALUES (:item,:session,:version,1,'Synthetic legacy',:now)"""),
            params,
        )
        connection.execute(
            text("""INSERT INTO attempts
          (id,learner_id,session_item_id,item_version_id,choice_id,submitted_at,hint_count,channel)
          VALUES (:attempt,:learner,:item,:version,'A',:now,0,'WEB')"""),
            params,
        )
        connection.execute(
            text("""INSERT INTO grades
          (attempt_id,item_version_id,answer_specification_hash,result)
          SELECT :attempt,:version,content_hash,CAST(:result AS json) FROM item_versions
          WHERE id=:version"""),
            params,
        )
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
        )
    with Session(identity.engine) as db:
        attempt = db.get(Attempt, attempt_id)
        assert attempt.choice_id == "A" and attempt.response is None
        assert db.get(Grade, attempt_id).result == grade.model_dump(mode="json")
