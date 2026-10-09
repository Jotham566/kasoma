"""Version-pinned rubric review never enables learner assignment or model scoring."""

import os
import subprocess
from copy import deepcopy
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.content import ContentError, ContentService
from services.domain.content import ItemVersion, Rubric, RubricCriterionRow
from tests.integration.test_assessment import assessment as assessment_fixture
from tests.integration.test_assessment import start
from tests.integration.test_content import create, mutate, review, submit
from tests.integration.test_data_requests import claim
from tests.integration.test_data_requests import create as request_data
from tests.integration.test_deletion_preview import get as preview

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def document(body):
    return body["document"] | {
        "title": "Synthetic reviewed short-text fixture",
        "response_type": "SHORT_TEXT",
        "choices": [],
        "correct_choice_id": "",
        "partial_credit": "CRITERION_SUM",
        "maximum_points": 1,
        "prompt": "Synthetic fixture: write the label Alpha.",
        "rubric": {
            "criteria": [
                {
                    "criterion_id": "R1",
                    "maximum_points": 1,
                    "criterion_text": "Explicitly write the requested synthetic label.",
                    "acceptable_evidence": ["Alpha"],
                    "common_errors": ["Beta"],
                    "prohibited_inferences": ["Do not infer a label from an empty response."],
                }
            ]
        },
    }


def test_rubric_review_versioning_exact_storage_and_staff_inventory(content):
    identity, client, actors, body = content
    original = body | {"document": document(body)}
    key = str(uuid4())
    created = mutate(client, "items", actors["author"], original, key=key)
    assert created.status_code == 201, created.text
    draft = created.json()
    assert draft["rubric_version_id"] == draft["id"]
    assert draft["document"]["rubric"] == original["document"]["rubric"]
    fetched = client.get(f"/api/v1/admin/item-versions/{draft['id']}", headers=actors["author"])
    assert fetched.status_code == 200 and fetched.json()["document"] == draft["document"]
    assert mutate(client, "items", actors["author"], original, key=key).json() == draft
    queued = submit(client, actors, draft)
    assert review(client, actors, queued, "author").status_code == 409
    for sql in [
        "UPDATE rubrics SET maximum_points=2",
        "DELETE FROM rubric_criteria",
        "UPDATE rubric_criteria SET criterion_text='Changed'",
    ]:
        with identity.engine.begin() as db, pytest.raises(DBAPIError, match="Rubric is frozen"):
            db.execute(text(sql))
    returned = review(client, actors, queued, decision="RETURN").json()
    modified = deepcopy(original["document"])
    modified["rubric"]["criteria"][0]["acceptable_evidence"] = ["Alpha", "Alpha."]
    edited = mutate(
        client,
        f"item-versions/{draft['id']}",
        actors["author"],
        {
            "expected_revision": returned["revision"],
            "document": modified,
            "change_reason": "Clarify original synthetic acceptable labels",
        },
        method="patch",
    )
    assert edited.status_code == 200, edited.text
    approved = review(client, actors, submit(client, actors, edited.json()))
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "APPROVED"
    with Session(identity.engine) as db:
        rubric = db.get(Rubric, UUID(draft["id"]))
        criterion = db.get(RubricCriterionRow, (rubric.id, "R1"))
        assert rubric.maximum_points == 1 and criterion.position == 1
        assert criterion.acceptable_evidence == ["Alpha", "Alpha."]
    for sql in ["DELETE FROM rubrics", "UPDATE rubric_criteria SET maximum_points=2"]:
        with identity.engine.begin() as db, pytest.raises(DBAPIError, match="Rubric is frozen"):
            db.execute(text(sql))
    following = create(client, actors, original | {"source_version_id": draft["id"]})
    assert (
        following["version"] == 2 and following["rubric_version_id"] != draft["rubric_version_id"]
    )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(Rubric)) == 2
        assert db.scalar(select(func.count()).select_from(RubricCriterionRow)) == 2
    for name in ["learner", "support"]:
        assert (
            client.get(
                f"/api/v1/admin/item-versions/{draft['id']}", headers=actors[name]
            ).status_code
            == 403
        )
    target = request_data(client, actors["author"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    inventory = preview(client, actors["admin"], target).json()
    sources = {
        row["source"]: row["count"]
        for row in inventory["sources"]
        if row["retention"] == "STAFF_PROVENANCE_REVIEW"
    }
    assert sources["rubrics"] == sources["rubric_criteria"] == 2
    assert inventory["execution_enabled"] is False


@pytest.mark.parametrize(
    "change,field",
    [
        ({"rubric": None}, "rubric"),
        ({"maximum_points": 2}, "rubric.criteria"),
        ({"partial_credit": "ALL_OR_NOTHING"}, "partial_credit"),
        ({"choices": [{"id": "A", "text": "Alpha"}]}, "choices"),
    ],
)
def test_incomplete_short_text_cannot_enter_review(content, change, field):
    _, client, actors, body = content
    draft = create(client, actors, body | {"document": document(body) | change})
    result = mutate(
        client,
        f"item-versions/{draft['id']}/submit",
        actors["author"],
        {
            "expected_revision": draft["revision"],
            "reason": "Synthetic incomplete submission",
        },
    )
    assert result.status_code == 409
    assert field in {entry["field"] for entry in result.json()["error"]["field_errors"]}


def test_sql_rejects_mismatched_rubric_and_preserves_draft_rollback(content):
    identity, client, actors, body = content
    draft = create(client, actors, body | {"document": document(body)})
    with identity.engine.begin() as db:
        db.execute(text("UPDATE rubric_criteria SET acceptable_evidence='[\"Changed\"]'::jsonb"))
    result = mutate(
        client,
        f"item-versions/{draft['id']}/submit",
        actors["author"],
        {
            "expected_revision": draft["revision"],
            "reason": "Synthetic mismatch probe",
        },
    )
    assert result.status_code == 500  # SQL boundary rejects divergence after valid API validation.
    with Session(identity.engine) as db:
        assert db.get(ItemVersion, UUID(draft["id"])).status == "DRAFT"
    with identity.engine.begin() as db, pytest.raises(DBAPIError):
        db.execute(text("UPDATE rubric_criteria SET acceptable_evidence='[]'::jsonb"))
    repaired = mutate(
        client,
        f"item-versions/{draft['id']}",
        actors["author"],
        {
            "expected_revision": draft["revision"],
            "document": document(body),
            "change_reason": "Restore the canonical synthetic rubric projection",
        },
        method="patch",
    )
    assert repaired.status_code == 200, repaired.text
    assert review(client, actors, submit(client, actors, repaired.json())).status_code == 200
    # Objective documents also reject a rubric at the service boundary.
    objective = create(
        client, actors, body | {"document": body["document"] | {"rubric": document(body)["rubric"]}}
    )
    result = mutate(
        client,
        f"item-versions/{objective['id']}/submit",
        actors["author"],
        {
            "expected_revision": objective["revision"],
            "reason": "Synthetic mixed format probe",
        },
    )
    assert result.status_code == 409


def test_approved_rubric_is_excluded_from_web_whatsapp_and_sql_assignment(assessment):
    identity, client, actors, body, _, plan = assessment
    approved = review(
        client,
        actors,
        submit(client, actors, create(client, actors, body | {"document": document(body)})),
    )
    assert approved.status_code == 200, approved.text
    target = UUID(approved.json()["id"])
    content = ContentService(identity)
    with Session(identity.engine) as db:
        for channel in ["WEB", "WHATSAPP"]:
            candidates = content.assessment_candidates(
                db, UUID(body["subject_id"]), UUID(plan["topic_id"]), set(), 100, channel=channel
            )
            assert target not in {candidate.id for candidate in candidates}
        with pytest.raises(ContentError, match="CONTENT_NOT_APPROVED"):
            content.assessment_version(db, target, UUID(body["subject_id"]))
        with pytest.raises(ContentError, match="CONTENT_NOT_APPROVED"):
            content.assessment_versions(db, [target], UUID(body["subject_id"]))
    session = start(client, actors["learner"], plan)
    assert session.status_code == 201, session.text
    with (
        identity.engine.begin() as db,
        pytest.raises(DBAPIError, match="Short-text learner delivery is disabled"),
    ):
        db.execute(
            text("""INSERT INTO session_items(id,session_id,item_version_id,position,reason)
          VALUES (:id,:session,:version,6,'Synthetic disabled format probe')"""),
            {
                "id": uuid4(),
                "session": UUID(session.json()["id"]),
                "version": target,
            },
        )


@pytest.mark.parametrize("identity", ["0022"], indirect=True)
def test_rubric_migration_preserves_objective_hashes_and_retries(content):
    identity, client, actors, body = content
    key = str(uuid4())
    before = mutate(client, "items", actors["author"], body, key=key)
    assert before.status_code == 201, before.text
    version = review(client, actors, submit(client, actors, before.json()))
    assert version.status_code == 200, version.text
    with Session(identity.engine) as db:
        digest = db.get(ItemVersion, UUID(before.json()["id"])).content_hash
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
        )
    with Session(identity.engine) as db:
        assert db.get(ItemVersion, UUID(before.json()["id"])).content_hash == digest
        assert db.scalar(select(func.count()).select_from(Rubric)) == 0
    replay = mutate(client, "items", actors["author"], body, key=key)
    assert replay.status_code == 201 and replay.json()["id"] == before.json()["id"]
    created = create(client, actors, body | {"document": document(body)})
    assert created["rubric_version_id"] == created["id"]
