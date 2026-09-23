"""FR-CNT-001–005, FR-OPS-003: real transactions, synthetic content, no model calls."""

from concurrent.futures import ThreadPoolExecutor
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.content import ContentError, ContentService
from services.content_contracts import CHECKLIST, EditDraft
from services.domain.content import AuditLog, ContentEvent, ContentReview, ItemMapping, ItemVersion
from services.identity_contracts import OTPRequest, OTPVerify
from services.seed import seed
from services.staff import provision

pytestmark = pytest.mark.integration


@pytest.fixture
def content(identity):
    identity_service, client, messages, now = identity
    seed(identity_service.settings)
    actors = {}
    for name, roles in {
        "author": ["CONTENT_AUTHOR", "ACADEMIC_REVIEWER"],
        "reviewer": ["ACADEMIC_REVIEWER"],
        "second": ["ACADEMIC_REVIEWER"],
        "other": ["CONTENT_AUTHOR"],
        "admin": ["ADMIN"],
        "support": ["SUPPORT_READONLY"],
        "learner": [],
    }.items():
        email = f"{name}@example.invalid"
        challenge = identity_service.request_otp(
            OTPRequest(identifier=email, device_id=uuid4()), name, None
        )
        credentials = identity_service.verify(
            OTPVerify(challenge_id=challenge.challenge_id, code="246810"), None, str(uuid4())
        )
        for role in roles:
            provision(identity_service, email, role)
        actors[name] = {"Authorization": "Bearer " + credentials.access_token}
    context = client.get("/api/v1/admin/content-context", headers=actors["author"]).json()
    subject = context["subjects"][0]
    topic = next(t for t in context["topics"] if t["parent_id"] == subject["id"])
    concept = next(c for c in context["concepts"] if c["parent_id"] == topic["id"])
    document = {
        "title": "Synthetic selector fixture",
        "topic_id": topic["id"],
        "concept_id": concept["id"],
        "competency_mappings": [{"competency_id": context["competencies"][0]["id"], "weight": 1}],
        "learning_outcome_reference": concept["syllabus_reference"],
        "prompt": "Synthetic test: choose the option labelled Alpha.",
        "choices": [{"id": "A", "text": "Alpha"}, {"id": "B", "text": "Beta"}],
        "correct_choice_id": "A",
        "worked_solution": "The requested label is Alpha, option A.",
        "remediation": "Read the two labels again.",
        "source": "Original synthetic workflow fixture",
        "rights_status": "ORIGINAL_KASOMA",
        "rights_evidence": "Original fixture, no third-party material",
        "rights_conditions": "Test use only; not academic release content",
    }
    return (
        identity_service,
        client,
        actors,
        {
            "subject_id": subject["id"],
            "document": document,
            "change_reason": "Synthetic workflow test",
        },
    )


def mutate(client, path, headers, body, method="post", key=None):
    return getattr(client, method)(
        "/api/v1/admin/" + path,
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json=body,
    )


def create(client, actors, body):
    response = mutate(client, "items", actors["author"], body)
    assert response.status_code == 201, response.text
    return response.json()


def submit(client, actors, version):
    result = mutate(
        client,
        f"item-versions/{version['id']}/submit",
        actors["author"],
        {"expected_revision": version["revision"], "reason": "Ready for independent review"},
    )
    assert result.status_code == 200, result.text
    return result.json()


def review(client, actors, version, actor="reviewer", decision="APPROVE", **extra):
    return mutate(
        client,
        f"item-versions/{version['id']}/review",
        actors[actor],
        {
            "expected_revision": version["revision"],
            "reason": "Synthetic checklist review",
            "decision": decision,
            "checklist": sorted(CHECKLIST) if decision == "APPROVE" else [],
            **extra,
        },
    )


def test_complete_review_retire_versioning_and_append_only_audit(content):
    identity, client, actors, body = content
    key = str(uuid4())
    version = mutate(client, "items", actors["author"], body, key=key).json()
    assert mutate(client, "items", actors["author"], body, key=key).json()["id"] == version["id"]
    assert (
        mutate(
            client, "items", actors["author"], body | {"change_reason": "Different"}, key=key
        ).status_code
        == 409
    )
    assert not version["production_eligible"] and version["synthetic"]
    draft = version
    version = submit(client, actors, version)
    assert review(client, actors, version, "author").status_code == 409
    approved = review(client, actors, version)
    assert approved.status_code == 200, approved.text
    version = approved.json()
    assert version["status"] == "APPROVED"
    assert (
        mutate(
            client,
            f"item-versions/{version['id']}",
            actors["author"],
            {
                "expected_revision": version["revision"],
                "document": body["document"],
                "change_reason": "Cannot overwrite",
            },
            "patch",
        ).status_code
        == 409
    )
    successor = create(client, actors, body | {"source_version_id": version["id"]})
    assert successor["item_id"] == version["item_id"] and successor["version"] == 2
    assert (
        client.get(
            f"/api/v1/admin/item-versions/{version['id']}", headers=actors["reviewer"]
        ).json()["document"]
        == version["document"]
    )
    selector = ContentService(identity)
    with Session(identity.engine) as db:
        assert selector.eligible_version(
            db, UUID(version["id"]), UUID(body["subject_id"]), synthetic=True
        )
        with pytest.raises(ContentError):
            selector.eligible_version(
                db, UUID(successor["id"]), UUID(body["subject_id"]), synthetic=True
            )
        with pytest.raises(ContentError):
            selector.eligible_version(db, UUID(version["id"]), UUID(body["subject_id"]))
        with pytest.raises(ContentError):
            selector.eligible_version(db, UUID(version["id"]), uuid4(), synthetic=True)
    retired = mutate(
        client,
        f"item-versions/{version['id']}/retire",
        actors["admin"],
        {"expected_revision": version["revision"], "reason": "Synthetic withdrawal"},
    )
    assert retired.status_code == 200, retired.text
    assert retired.json()["status"] == "RETIRED"
    with Session(identity.engine) as db:
        with pytest.raises(ContentError):
            selector.eligible_version(
                db, UUID(version["id"]), UUID(body["subject_id"]), synthetic=True
            )
        assert db.scalar(select(func.count()).select_from(ContentEvent)) == 5
        assert db.scalar(select(func.count()).select_from(ContentReview)) == 1
        audit = db.scalar(select(AuditLog).where(AuditLog.target_id == UUID(version["id"])))
        assert audit.actor_id and audit.request_id and audit.reason
    # Test the database protection, not only the API's prohibition.
    statements = [
        ("UPDATE item_versions SET document='{}', revision=revision+1 WHERE id=:id", version["id"]),
        ("DELETE FROM item_versions WHERE id=:id", version["id"]),
        ("DELETE FROM item_mappings WHERE item_version_id=:id", version["id"]),
        ("DELETE FROM content_reviews WHERE item_version_id=:id", version["id"]),
        ("UPDATE audit_log SET reason='rewritten' WHERE target_id=:id", version["id"]),
    ]
    for statement, identifier in statements:
        with pytest.raises(DBAPIError), identity.engine.begin() as connection:
            connection.execute(text(statement), {"id": UUID(identifier)})
    assert draft["status"] == "DRAFT"


def test_return_comments_corrections_and_two_independent_reviews(content):
    identity, client, actors, body = content
    version = submit(client, actors, create(client, actors, body))
    returned = review(client, actors, version, decision="RETURN", require_second_review=True)
    assert returned.status_code == 200, returned.text
    version = returned.json()
    assert version["status"] == "DRAFT"
    changed = body["document"] | {"remediation": "Synthetic corrected feedback"}
    edited = mutate(
        client,
        f"item-versions/{version['id']}",
        actors["author"],
        {
            "expected_revision": version["revision"],
            "document": changed,
            "change_reason": "Corrected feedback",
        },
        "patch",
    )
    assert edited.status_code == 200, edited.text
    version = submit(client, actors, edited.json())
    first = review(client, actors, version)
    assert first.status_code == 200, first.text
    version = first.json()
    assert version["requires_second_review"] and version["status"] == "IN_REVIEW"
    assert review(client, actors, version).status_code == 409
    second = review(client, actors, version, "second")
    assert second.status_code == 200, second.text
    assert second.json()["status"] == "APPROVED" and second.json()["approval_count"] == 2
    history = client.get(
        f"/api/v1/admin/item-versions/{version['id']}/reviews", headers=actors["author"]
    )
    assert len(history.json()) == 3
    assert history.json()[0]["reason"] == "Synthetic checklist review"


@pytest.mark.parametrize(
    "change, field",
    [
        ({"rights_status": "UNKNOWN_BLOCKED"}, "rights_status"),
        ({"rights_status": "REFERENCE_ONLY_NO_REPRODUCTION"}, "rights_status"),
        ({"rights_evidence": ""}, "rights_evidence"),
        ({"worked_solution": ""}, "worked_solution"),
        ({"remediation": ""}, "remediation"),
        ({"correct_choice_id": "C"}, "correct_choice_id"),
        ({"learning_outcome_reference": "invented-NCDC"}, "learning_outcome_reference"),
        ({"competency_mappings": []}, "competency_mappings"),
    ],
)
def test_incomplete_content_cannot_enter_review(content, change, field):
    identity, client, actors, body = content
    version = create(client, actors, body | {"document": body["document"] | change})
    response = mutate(
        client,
        f"item-versions/{version['id']}/submit",
        actors["author"],
        {"expected_revision": 1, "reason": "Invalid submission"},
    )
    assert response.status_code == 409
    assert field in {error["field"] for error in response.json()["error"]["field_errors"]}
    assert "Alpha" not in response.text


def test_roles_ownership_revocation_and_hidden_answers(content):
    identity, client, actors, body = content
    version = create(client, actors, body)
    for role in ["learner", "support"]:
        assert client.get("/api/v1/admin/items", headers=actors[role]).status_code == 403
        response = client.get(f"/api/v1/admin/item-versions/{version['id']}", headers=actors[role])
        assert response.status_code == 403 and "Alpha" not in response.text
    assert client.get("/api/v1/admin/items").status_code == 401
    assert (
        client.get(
            f"/api/v1/admin/item-versions/{version['id']}", headers=actors["other"]
        ).status_code
        == 404
    )
    assert mutate(client, "items", actors["reviewer"], body).status_code == 403
    assert (
        mutate(client, "items", actors["author"], body | {"status": "APPROVED"}).status_code == 422
    )
    assert (
        client.get("/api/v1/content/" + version["id"], headers=actors["learner"]).status_code == 404
    )
    provision(identity, "author@example.invalid", "CONTENT_AUTHOR", revoke=True)
    assert mutate(client, "items", actors["author"], body).status_code == 403
    with pytest.raises(ValueError):
        provision(identity, "real@example.com", "ADMIN")


def test_invalid_mappings_checklist_and_concurrent_edits(content):
    identity, client, actors, body = content
    invalid = body | {"document": body["document"] | {"topic_id": str(uuid4())}}
    assert mutate(client, "items", actors["author"], invalid).status_code == 409
    version = create(client, actors, body)
    service = ContentService(identity)
    token = actors["author"]["Authorization"][7:]
    edit = EditDraft(
        expected_revision=1, document=body["document"], change_reason="Concurrent test"
    )

    def update_once(_):
        try:
            service.mutate(token, UUID(version["id"]), "edit", edit, uuid4(), uuid4())
            return "ok"
        except ContentError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(update_once, range(2))) == ["VERSION_CONFLICT", "ok"]
    version = client.get(
        f"/api/v1/admin/item-versions/{version['id']}", headers=actors["author"]
    ).json()
    version = submit(client, actors, version)
    assert review(client, actors, version, checklist=[]).status_code == 409
    # Directly changing status without a real independent review is rejected.
    with pytest.raises(DBAPIError), identity.engine.begin() as connection:
        connection.execute(
            text("UPDATE item_versions SET status='APPROVED', revision=revision+1 WHERE id=:id"),
            {"id": UUID(version["id"])},
        )
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(ItemMapping)) == 1
        assert (
            db.scalar(select(ItemVersion.status).where(ItemVersion.id == UUID(version["id"])))
            == "IN_REVIEW"
        )


def test_publication_revalidates_mapping_and_paginates_without_duplicates(content):
    identity, client, actors, body = content
    version = submit(client, actors, create(client, actors, body))
    # An academic reference change invalidates earlier submission validation.
    with identity.engine.begin() as connection:
        connection.execute(
            text("UPDATE concepts SET syllabus_reference=:reference WHERE id=:id"),
            {"reference": "SYNTHETIC-UPDATED", "id": UUID(body["document"]["concept_id"])},
        )
    response = review(client, actors, version)
    assert response.status_code == 409
    assert response.json()["error"]["field_errors"][0]["field"] == "learning_outcome_reference"
    create(client, actors, body)
    first = client.get("/api/v1/admin/items?limit=1", headers=actors["author"]).json()
    second = client.get(
        "/api/v1/admin/items",
        params={"limit": 1, "cursor": first["next_cursor"]},
        headers=actors["author"],
    ).json()
    assert len(first["data"]) == len(second["data"]) == 1
    assert first["data"][0]["id"] != second["data"][0]["id"]
    assert second["next_cursor"] is None
