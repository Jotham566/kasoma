"""FR-CNT-001/002/004/005: atomic synthetic imports and independent publication."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.content import ContentService
from services.content_imports import process_one
from services.domain.content import ContentEvent, ContentImport, ItemVersion
from services.staff import provision
from tests.integration.test_content import mutate, review, submit

pytestmark = pytest.mark.integration


def batch(body):
    record = deepcopy(body)
    record["document"]["source_locator"] = "synthetic-fixture:1"
    return {"format_version": "kasoma-draft-import-v1", "synthetic": True, "records": [record]}


def enqueue(client, actors, body, key=None):
    result = mutate(client, "content-imports", actors["author"], batch(body), key=key)
    assert result.status_code == 202, result.text
    return result.json()


def read(client, actors, identifier, actor="author"):
    return client.get(f"/api/v1/admin/content-imports/{identifier}", headers=actors[actor])


def test_import_owner_replay_drafts_review_and_duplicates(content):
    identity, client, actors, body = content
    key = str(uuid4())
    job = enqueue(client, actors, body, key)
    assert enqueue(client, actors, body, key)["id"] == job["id"]
    assert read(client, actors, job["id"], "other").status_code == 404
    for actor in ["learner", "reviewer", "admin", "support"]:
        assert mutate(client, "content-imports", actors[actor], batch(body)).status_code == 403
    changed = batch(body)
    changed["records"][0]["change_reason"] = "Different reason"
    assert mutate(client, "content-imports", actors["author"], changed, key=key).status_code == 409
    assert process_one(identity)
    assert not process_one(identity)
    done = read(client, actors, job["id"]).json()
    assert done["status"] == "COMPLETED" and done["attempts"] == 1
    assert enqueue(client, actors, body, key) == done
    identifier = done["results"][0]["version_id"]
    version = client.get(
        f"/api/v1/admin/item-versions/{identifier}", headers=actors["author"]
    ).json()
    assert version["status"] == "DRAFT" and not version["production_eligible"]
    assert version["document"]["source_locator"] == "synthetic-fixture:1"
    submitted = submit(client, actors, version)
    assert review(client, actors, submitted, "author").status_code == 409
    assert review(client, actors, submitted).status_code == 200
    duplicate = enqueue(client, actors, body)
    assert process_one(identity)
    assert read(client, actors, duplicate["id"]).json()["results"] == [
        {"position": 1, "version_id": identifier, "outcome": "DUPLICATE"}
    ]
    with Session(identity.engine) as db:
        row = db.get(ContentImport, UUID(job["id"]))
        assert row.payload is None and row.finished_at
        assert db.scalar(select(func.count()).select_from(ItemVersion)) == 1
    for statement in [
        "UPDATE content_import_jobs SET request_hash='changed' WHERE id=:id",
        "DELETE FROM content_import_jobs WHERE id=:id",
        "UPDATE content_import_jobs SET status='QUEUED',attempts=2 WHERE id=:id",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as connection:
            connection.execute(text(statement), {"id": UUID(job["id"])})


def test_import_all_candidate_validation_before_queue(content):
    identity, client, actors, body = content
    invalid = batch(body)
    invalid["records"].append(deepcopy(invalid["records"][0]))
    invalid["records"][1]["document"]["title"] = "Second invalid candidate"
    invalid["records"][1]["document"]["concept_id"] = str(uuid4())
    assert mutate(client, "content-imports", actors["author"], invalid).status_code == 422
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(ContentImport)) == 0
        assert db.scalar(select(func.count()).select_from(ItemVersion)) == 0


def test_import_atomic_retry_then_terminal_redaction(content, identity, monkeypatch):
    service, client, actors, body = content
    now = identity[3]
    payload = batch(body)
    payload["records"].append(deepcopy(payload["records"][0]))
    payload["records"][1]["document"]["title"] = "Second candidate"
    job = mutate(client, "content-imports", actors["author"], payload).json()
    original = ContentService.create_in_transaction
    count = [0]

    def fail_second(self, *args, **kwargs):
        count[0] += 1
        if count[0] % 2 == 0:
            raise RuntimeError("confidential exception never persisted")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ContentService, "create_in_transaction", fail_second)
    for attempt in range(1, 4):
        assert process_one(service)
        with Session(service.engine) as db:
            row = db.get(ContentImport, UUID(job["id"]))
            assert row.attempts == attempt and row.error_code == "TRANSIENT_FAILURE"
            assert row.status == ("FAILED" if attempt == 3 else "QUEUED")
            assert (row.payload is None) == (attempt == 3)
            assert db.scalar(select(func.count()).select_from(ItemVersion)) == 0
            assert db.scalar(select(func.count()).select_from(ContentEvent)) == 0
        assert not process_one(service)
        now[0] += timedelta(seconds=60 * attempt)


@pytest.mark.parametrize("condition", ["expired", "revoked"])
def test_import_execution_rechecks_author_and_expiry(content, identity, condition):
    service, client, actors, body = content
    job = enqueue(client, actors, body)
    if condition == "expired":
        identity[3][0] += timedelta(hours=24)
    else:
        provision(service, "author@example.invalid", "CONTENT_AUTHOR", revoke=True)
    assert process_one(service)
    with Session(service.engine) as db:
        row = db.get(ContentImport, UUID(job["id"]))
        assert row.status == "FAILED" and row.payload is None
        assert row.error_code == (
            "IMPORT_EXPIRED" if condition == "expired" else "AUTHOR_UNAVAILABLE"
        )
        assert db.scalar(select(func.count()).select_from(ItemVersion)) == 0


def test_import_competing_workers_and_rate_limit(content):
    identity, client, actors, body = content
    for _ in range(5):
        enqueue(client, actors, body)
    assert mutate(client, "content-imports", actors["author"], batch(body)).status_code == 429
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert all(pool.map(lambda _: process_one(identity), range(5)))
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(ItemVersion)) == 1
        assert all(row.status == "COMPLETED" for row in db.scalars(select(ContentImport)))
    page = client.get("/api/v1/admin/content-imports?limit=2", headers=actors["author"]).json()
    assert len(page["data"]) == 2 and page["next_cursor"]
    next_page = client.get(
        "/api/v1/admin/content-imports?limit=2&cursor=" + page["next_cursor"],
        headers=actors["author"],
    ).json()
    assert len(next_page["data"]) == 2
    assert not ({j["id"] for j in page["data"]} & {j["id"] for j in next_page["data"]})
