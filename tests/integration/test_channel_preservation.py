"""ADR-057 exact versions, atomic evidence and finite synthetic preservation."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.channel_preservation import (
    ChannelSnapshot,
    ChannelSnapshotBody,
    ChannelSnapshotDisposal,
)
from services.domain.data_requests import LegalHold, LegalHoldReceipt
from services.domain.messaging import ChannelLink, ChannelSender, ConversationState, OutboundMessage
from services.whatsapp_retention import expire
from tests.integration.test_legal_holds import hold, prepare, release

pytestmark = pytest.mark.integration


def capture_path(target):
    return f"/api/v1/admin/data-requests/{target}/channel-preservations"


def inspect_source(client, headers, target, source):
    return client.post(capture_path(target) + "/inspect", headers=headers, json=source)


def capture(client, headers, target, body, key=None):
    return client.post(
        capture_path(target),
        headers=headers | {"Idempotency-Key": key or str(uuid4())},
        json=body,
    )


def prepared_capture(content):
    identity, client, actors, *_ = content
    target, decision = prepare(content)
    link, owner = channel_source(content)
    source = {
        "source_kind": "CHANNEL_LINK_SNAPSHOT",
        "source_link_id": str(link),
        "link_revision": 1,
    }
    body = {
        key: decision[key] for key in ("decision_reference", "reason", "expires_at", "affirmative")
    }
    return target, source, body, owner


def checked_capture(content):
    identity, client, actors, *_ = content
    target, source, decision, owner = prepared_capture(content)
    identity.settings.channel_preservation_enabled = True
    selected = inspect_source(client, actors["admin"], target, source)
    assert selected.status_code == 200, selected.text
    assert set(selected.json()) == {"source_version"}
    assert len(selected.json()["source_version"]) == 64
    assert selected.headers["cache-control"] == "no-store"
    return target, source | selected.json() | decision, owner


def channel_source(content):
    identity, client, actors, *_ = content
    owner = UUID(client.get("/api/v1/me", headers=actors["learner"]).json()["id"])
    link, sender = uuid4(), identity.digest("wa-sender", "+256700000001")
    at = identity.clock()
    with Session(identity.engine) as db, db.begin():
        db.add(ChannelSender(sender_hash=sender, updated_at=at))
        db.flush()
        db.add(
            ChannelLink(
                id=link,
                user_id=owner,
                sender_hash=sender,
                external_identifier_encrypted=identity.encrypt("synthetic-contact-do-not-send"),
                revision=1,
                status="ACTIVE",
                linked_at=at,
                opted_out_at=None,
                updated_at=at,
            )
        )
    return link, owner


def test_conversation_versions_distinguish_same_time_updates_and_reinsertion(content):
    identity = content[0]
    link, owner = channel_source(content)

    def insert():
        with Session(identity.engine) as db, db.begin():
            row = ConversationState(
                link_id=link,
                actor_id=owner,
                link_revision=1,
                session_id=None,
                expected_outbound_id=None,
                updated_at=identity.clock(),
                expires_at=identity.clock() + timedelta(hours=24),
            )
            db.add(row)
            db.flush()
            return row.state_version

    first = insert()
    with identity.engine.begin() as db:
        second = db.scalar(
            text(
                "UPDATE conversation_states SET updated_at=updated_at,state_version=1 "
                "WHERE link_id=:id RETURNING state_version"
            ),
            {"id": link},
        )
        assert second > first
        db.execute(text("DELETE FROM conversation_states WHERE link_id=:id"), {"id": link})
    assert insert() > second
    with Session(identity.engine) as db:
        assert db.get(ConversationState, link).updated_at == identity.clock()


def test_metadata_without_body_and_finite_decision_cannot_commit(content):
    identity, client, actors, *_ = content
    target, _ = prepare(content)
    link, _ = channel_source(content)
    actor = UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"])
    snapshot = uuid4()
    with pytest.raises(DBAPIError, match="Snapshot capture requires encrypted evidence"):
        with identity.engine.begin() as db:
            db.execute(
                text("""INSERT INTO channel_preservation_snapshots
                  (id,request_id,source_kind,source_link_id,link_revision,source_version,
                    captured_by,captured_at)
                  VALUES(:id,:request,'CHANNEL_LINK_SNAPSHOT',:link,1,:version,
                    :actor,clock_timestamp())"""),
                {
                    "id": snapshot,
                    "request": UUID(target),
                    "link": link,
                    "version": "a" * 64,
                    "actor": actor,
                },
            )
    with Session(identity.engine) as db:
        assert db.scalar(select(ChannelSnapshot.id)) is None


def test_default_disabled_and_capability_discovery(content):
    identity, client, actors, *_ = content
    target, source, decision, _ = prepared_capture(content)
    identity.settings.channel_preservation_enabled = False
    assert inspect_source(client, actors["admin"], target, source).status_code == 409
    assert (
        capture(
            client, actors["admin"], target, source | decision | {"source_version": "a" * 64}
        ).status_code
        == 409
    )
    page = client.get(f"/api/v1/admin/data-requests/{target}/holds", headers=actors["admin"]).json()
    assert "CHANNEL_LINK_SNAPSHOT" not in page["supported_record_types"]
    identity.settings.channel_preservation_enabled = True
    page = client.get(f"/api/v1/admin/data-requests/{target}/holds", headers=actors["admin"]).json()
    assert {"CHANNEL_LINK_SNAPSHOT", "CHANNEL_CONVERSATION_SNAPSHOT"} <= set(
        page["supported_record_types"]
    )


def test_exact_capture_replay_and_bound_private_body(content, caplog):
    from pydantic import SecretStr

    from services.channel_preservation_format import PreservationCipher, SnapshotBinding

    identity, client, actors, *_ = content
    target, body, owner = checked_capture(content)
    key = str(uuid4())
    created = capture(client, actors["admin"], target, body, key)
    assert created.status_code == 201, created.text
    record = created.json()
    assert record["record_type"] == "CHANNEL_LINK_SNAPSHOT"
    assert record["record_id"] != body["source_link_id"]
    assert capture(client, actors["admin"], target, body, key).json() == record
    assert (
        capture(
            client, actors["admin"], target, body | {"decision_reference": str(uuid4())}, key
        ).status_code
        == 409
    )
    assert body["source_link_id"] not in created.text and body["source_version"] not in created.text
    with Session(identity.engine) as db:
        meta = db.get(ChannelSnapshot, UUID(record["record_id"]))
        stored = db.get(ChannelSnapshotBody, meta.id)
        binding = SnapshotBinding(
            snapshot_id=meta.id,
            request_id=UUID(target),
            owner_id=owner,
            source_kind=meta.source_kind,
            source_link_id=meta.source_link_id,
            link_revision=meta.link_revision,
            source_version=meta.source_version,
        )
        opened = PreservationCipher(identity.settings.identity_encryption_key).open(
            binding, SecretStr(stored.encrypted_payload)
        )
        assert opened.evidence.source_link_id == UUID(body["source_link_id"])
        assert "synthetic-contact-do-not-send" not in opened.model_dump_json()
        assert len(list(db.scalars(select(ChannelSnapshot)))) == 1
        assert len(list(db.scalars(select(LegalHold)))) == 1
        assert len(list(db.scalars(select(LegalHoldReceipt)))) == 1
    assert "synthetic-contact-do-not-send" not in caplog.text


def test_same_key_does_not_recapture_changed_source_and_stale_version_fails(content):
    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    key = str(uuid4())
    created = capture(client, actors["admin"], target, body, key)
    assert created.status_code == 201, created.text
    with identity.engine.begin() as db:
        db.execute(
            text("UPDATE channel_links SET revision=revision+1 WHERE id=:id"),
            {"id": UUID(body["source_link_id"])},
        )
    assert capture(client, actors["admin"], target, body, key).json() == created.json()
    assert capture(client, actors["admin"], target, body).status_code == 404
    changed = body | {"link_revision": 2}
    assert capture(client, actors["admin"], target, changed).status_code == 409


def test_late_identity_error_rolls_back_all_capture_evidence(content, monkeypatch):
    from services.identity import IdentityError

    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)

    def fail(*args, **kwargs):
        raise IdentityError("SYNTHETIC_FAILURE", 409)

    monkeypatch.setattr(identity, "event", fail)
    result = capture(client, actors["admin"], target, body)
    assert result.status_code == 409
    with Session(identity.engine) as db:
        for model in (ChannelSnapshot, ChannelSnapshotBody, LegalHold, LegalHoldReceipt):
            assert list(db.scalars(select(model))) == []
        assert (
            db.scalar(text("SELECT count(*) FROM audit_log WHERE action='legal_hold.created'")) == 0
        )
        assert (
            db.scalar(
                text("SELECT count(*) FROM identity_outbox_events WHERE type='legal_hold.created'")
            )
            == 0
        )


@pytest.mark.parametrize("actor", [None, "learner", "author", "reviewer", "support", "other"])
def test_source_selection_and_capture_require_independent_current_admin(content, actor):
    _, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    headers = actors[actor] if actor else {}
    source = {key: body[key] for key in ("source_kind", "source_link_id", "link_revision")}
    status = 403 if actor else 401
    assert inspect_source(client, headers, target, source).status_code == status
    assert capture(client, headers, target, body).status_code == status


def test_revoked_admin_and_stale_reauthentication_fail_closed(identity, content):
    from services.staff import provision

    service, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    identity[3][0] += timedelta(minutes=11)
    assert capture(client, actors["admin"], target, body).status_code == 401
    identity[3][0] -= timedelta(minutes=11)
    provision(service, "admin@example.invalid", "ADMIN", revoke=True)
    assert capture(client, actors["admin"], target, body).status_code == 403


def test_version_cannot_be_used_for_a_different_request_owner(content):
    from tests.integration.test_data_requests import claim, create

    _, client, actors, *_ = content
    _, body, _ = checked_capture(content)
    target = create(client, actors["author"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    assert capture(client, actors["admin"], target, body).status_code == 404


def test_database_wall_clock_expiry_disposes_body_with_logical_clock_behind(content):
    from time import monotonic, sleep

    from services.legal_holds import database_now

    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    with Session(identity.engine) as db:
        expiry = database_now(db) + timedelta(seconds=3)
    created = capture(client, actors["admin"], target, body | {"expires_at": expiry.isoformat()})
    assert created.status_code == 201, created.text
    snapshot = UUID(created.json()["record_id"])
    expire(identity)
    with Session(identity.engine) as db:
        assert db.get(ChannelSnapshotBody, snapshot) is not None
    deadline = monotonic() + 8
    while True:
        with Session(identity.engine) as db:
            if database_now(db) >= expiry:
                break
        assert monotonic() < deadline, "Bounded database expiry did not advance"
        sleep(0.05)
    expire(identity)
    page = client.get(f"/api/v1/admin/data-requests/{target}/holds", headers=actors["admin"]).json()
    assert page["data"][0]["status"] == "EXPIRED"
    with Session(identity.engine) as db:
        assert db.get(ChannelSnapshotBody, snapshot) is None
        assert db.get(ChannelSnapshotDisposal, snapshot) is not None
    preview = client.get(
        f"/api/v1/admin/data-requests/{target}/deletion-preview", headers=actors["admin"]
    ).json()
    assert preview["active_legal_holds"] == 0
    assert preview["execution_enabled"] is False
    assert "LEGAL_HOLD_COVERAGE_INCOMPLETE" in preview["blockers"]


def test_capture_and_unlink_serialize_without_deadlock(content):
    from concurrent.futures import ThreadPoolExecutor

    from services.channel_preservation import ChannelPreservationService
    from services.channel_preservation_contracts import PreservationCapture
    from services.identity import IdentityError
    from services.whatsapp_linking import LinkingService

    identity, _, actors, *_ = content
    target, body, _ = checked_capture(content)
    admin = actors["admin"]["Authorization"].removeprefix("Bearer ")
    learner = actors["learner"]["Authorization"].removeprefix("Bearer ")

    def preserve():
        try:
            ChannelPreservationService(identity).capture(
                admin, UUID(target), PreservationCapture.model_validate(body), uuid4(), uuid4()
            )
            return 201
        except IdentityError as error:
            return error.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        capturing = pool.submit(preserve)
        unlinking = pool.submit(
            LinkingService(identity).unlink,
            learner,
            1,
            uuid4(),
            uuid4(),
            UUID(body["source_link_id"]),
        )
        assert unlinking.result(timeout=10).status == "UNLINKED"
        status = capturing.result(timeout=10)
        assert status in {201, 404}
    with Session(identity.engine) as db:
        assert len(list(db.scalars(select(ChannelSnapshotBody)))) == (1 if status == 201 else 0)
        assert (
            db.get(ChannelLink, UUID(body["source_link_id"])).external_identifier_encrypted is None
        )


@pytest.mark.parametrize("action", ["additional", "release"])
def test_late_identity_error_rolls_back_additional_snapshot_decision_or_release(
    content, monkeypatch, action
):
    from services.identity import IdentityError

    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    original = capture(client, actors["admin"], target, body)
    assert original.status_code == 201, original.text
    row = original.json()

    def fail(*args, **kwargs):
        raise IdentityError("SYNTHETIC_FAILURE", 409)

    monkeypatch.setattr(identity, "event", fail)
    if action == "additional":
        decision = {key: body[key] for key in ("reason", "expires_at", "affirmative")}
        result = hold(
            client,
            actors["admin"],
            target,
            decision
            | {
                "record_type": row["record_type"],
                "record_id": row["record_id"],
                "decision_reference": str(uuid4()),
            },
        )
    else:
        result = release(client, actors["admin"], target, row["id"])
    assert result.status_code == 409
    with Session(identity.engine) as db:
        rows = list(db.scalars(select(LegalHold)))
        assert len(rows) == 1 and rows[0].released_at is None
        assert len(list(db.scalars(select(LegalHoldReceipt)))) == 1


def test_snapshot_inventory_is_advisory_and_owned_export_excludes_internal_evidence(content):
    from tests.integration.test_data_exports import export
    from tests.integration.test_data_requests import create

    _, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    result = capture(client, actors["admin"], target, body)
    assert result.status_code == 201, result.text
    preview = client.get(
        f"/api/v1/admin/data-requests/{target}/deletion-preview", headers=actors["admin"]
    ).json()
    sources = {
        row["source"]: row
        for row in preview["sources"]
        if row["retention"] != "STAFF_PROVENANCE_REVIEW"
    }
    assert sources["channel_preservation_snapshots"]["count"] == 1
    assert sources["channel_preservation_bodies"]["count"] == 1
    assert sources["channel_preservation_bodies"]["retention"] == "ACTIVE_EXACT_PRESERVATION_ONLY"
    assert sources["channel_preservation_disposals"]["count"] == 0
    assert preview["active_legal_holds"] == 1
    assert preview["execution_enabled"] is False
    assert "LEGAL_HOLD_COVERAGE_INCOMPLETE" in preview["blockers"]
    requested = create(client, actors["learner"]).json()["id"]
    exported = export(client, actors["learner"], requested)
    assert exported.status_code == 200, exported.text
    for value in (
        "channel_preservation",
        result.json()["record_id"],
        body["decision_reference"],
        body["source_version"],
    ):
        assert value not in exported.text


def test_active_prefix_does_not_starve_disposal_and_batch_is_hard_bounded(content):
    from pydantic import SecretStr

    from services.channel_preservation import dispose_bodies
    from services.channel_preservation_format import (
        LinkEvidence,
        PreservationCipher,
        SnapshotBinding,
    )
    from services.legal_holds import database_now
    from services.whatsapp_linking import channel_lock

    identity, client, actors, *_ = content
    target, body, owner = checked_capture(content)
    actor = UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"])
    cipher = PreservationCipher(identity.settings.identity_encryption_key)
    with Session(identity.engine) as db, db.begin():
        channel_lock(identity, db)
        now = database_now(db)
        link = db.get(ChannelLink, UUID(body["source_link_id"]))
        evidence = LinkEvidence(
            source_link_id=link.id,
            revision=link.revision,
            status="ACTIVE",
            linked_at=link.linked_at,
            opted_out_at=link.opted_out_at,
            updated_at=link.updated_at,
        )
        # Controlled synthetic fixture construction; the public mutation budget is unchanged.
        for index in range(1, 103):
            snapshot = UUID(int=index)
            binding = SnapshotBinding(
                snapshot_id=snapshot,
                request_id=UUID(target),
                owner_id=owner,
                source_kind="CHANNEL_LINK_SNAPSHOT",
                source_link_id=link.id,
                link_revision=link.revision,
                source_version=body["source_version"],
            )
            db.add(
                ChannelSnapshot(
                    id=snapshot,
                    request_id=UUID(target),
                    source_kind="CHANNEL_LINK_SNAPSHOT",
                    source_link_id=link.id,
                    link_revision=link.revision,
                    source_state_version=None,
                    source_version=body["source_version"],
                    captured_by=actor,
                    captured_at=now,
                )
            )
            db.flush()
            encrypted = cipher.seal(binding, evidence)
            db.add(
                ChannelSnapshotBody(
                    snapshot_id=snapshot, encrypted_payload=encrypted.get_secret_value()
                )
            )
            db.flush()
            db.add(
                LegalHold(
                    id=uuid4(),
                    request_id=UUID(target),
                    record_type="CHANNEL_LINK_SNAPSHOT",
                    record_id=snapshot,
                    decision_reference=uuid4(),
                    reason="LEGAL_OBLIGATION",
                    created_by=actor,
                    created_at=now,
                    expires_at=now + timedelta(days=1),
                    released_at=None,
                    released_by=None,
                    release_reference=None,
                )
            )
            db.flush()
    with identity.engine.begin() as db:
        db.execute(
            text("""UPDATE legal_holds SET released_at=clock_timestamp(),released_by=:actor,
          release_reference=:reference WHERE record_id=:snapshot"""),
            {"actor": actor, "reference": uuid4(), "snapshot": UUID(int=102)},
        )
    with Session(identity.engine) as db, db.begin():
        channel_lock(identity, db)
        assert dispose_bodies(db) == 1
        assert db.get(ChannelSnapshotBody, UUID(int=102)) is None
        # The remaining bound evidence still decodes after unrelated evidence disposal.
        sample = db.get(ChannelSnapshotBody, UUID(int=1))
        meta = db.get(ChannelSnapshot, UUID(int=1))
        cipher.open(
            SnapshotBinding(
                snapshot_id=meta.id,
                request_id=UUID(target),
                owner_id=owner,
                source_kind=meta.source_kind,
                source_link_id=meta.source_link_id,
                link_revision=meta.link_revision,
                source_version=meta.source_version,
            ),
            SecretStr(sample.encrypted_payload),
        )
    with identity.engine.begin() as db:
        db.execute(
            text("""UPDATE legal_holds SET released_at=clock_timestamp(),released_by=:actor,
          release_reference=:reference WHERE released_at IS NULL"""),
            {"actor": actor, "reference": uuid4()},
        )
    for expected in (100, 1, 0):
        with Session(identity.engine) as db, db.begin():
            channel_lock(identity, db)
            assert dispose_bodies(db) == expected


def test_preserved_conversation_does_not_block_shared_grading_or_stop(identity, content):
    from services.domain.assessment import Attempt
    from services.domain.mastery import MasteryEvidence
    from services.legal_holds import database_now
    from tests.integration.test_identity import login
    from tests.integration.test_whatsapp_practice import Flow

    service, client, actors, *_ = content
    with Session(service.engine) as db:
        identity[3][0] = database_now(db) - timedelta(seconds=30)
    # Keep real database-time eligibility while every test actor re-authenticates
    # against the explicit deterministic near-wall-clock fixture.
    for name in actors:
        actors[name] = login(client, f"{name}@example.invalid")[0]
    flow = Flow(identity, content)
    reference = flow.begin()
    target, decision = prepare(content)
    service.settings.channel_preservation_enabled = True
    with Session(service.engine) as db:
        link = db.scalar(select(ChannelLink).where(ChannelLink.user_id == flow.actor))
        source = {
            "source_kind": "CHANNEL_CONVERSATION_SNAPSHOT",
            "source_link_id": str(link.id),
            "link_revision": link.revision,
        }
        before = db.scalar(select(func.count()).select_from(Attempt))
    version = inspect_source(client, actors["admin"], target, source)
    assert version.status_code == 200, version.text
    body = (
        source
        | version.json()
        | {
            key: decision[key]
            for key in ("decision_reference", "reason", "expires_at", "affirmative")
        }
    )
    held = capture(client, actors["admin"], target, body)
    assert held.status_code == 201, held.text
    flow.send("1", reference)
    assert "Points:" in flow.provider.messages[-1][1]
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == before + 1
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 1
    flow.incoming("STOP")
    with Session(service.engine) as db:
        assert db.scalar(select(ConversationState)) is None
        assert db.get(ChannelSnapshotBody, UUID(held.json()["record_id"])) is not None


def test_unbound_outbound_reference_cannot_be_captured_through_an_owned_conversation(content):
    from services.legal_holds import database_now
    from tests.integration.test_channel_receipt_holds import receipt

    service, client, actors, *_ = content
    target, original, owner = checked_capture(content)
    _, outgoing = receipt(content, owner=False)
    link = UUID(original["source_link_id"])
    with Session(service.engine) as db, db.begin():
        row = db.get(OutboundMessage, outgoing)
        row.link_id, row.link_revision = link, 1
        now = database_now(db)
        state = ConversationState(
            link_id=link,
            actor_id=owner,
            link_revision=1,
            session_id=None,
            expected_outbound_id=outgoing,
            updated_at=now,
            expires_at=now + timedelta(hours=24),
        )
        db.add(state)
        db.flush()
        state_version = state.state_version
    source = {
        "source_kind": "CHANNEL_CONVERSATION_SNAPSHOT",
        "source_link_id": str(link),
        "link_revision": 1,
    }
    assert inspect_source(client, actors["admin"], target, source).status_code == 404
    assert (
        capture(
            client,
            actors["admin"],
            target,
            original | {"source_kind": "CHANNEL_CONVERSATION_SNAPSHOT"},
        ).status_code
        == 404
    )
    actor = UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"])
    with (
        pytest.raises(DBAPIError, match="owned conversation version"),
        service.engine.begin() as db,
    ):
        db.execute(
            text("""INSERT INTO channel_preservation_snapshots
          (id,request_id,source_kind,source_link_id,link_revision,source_state_version,
            source_version,captured_by,captured_at)
          VALUES(:id,:target,'CHANNEL_CONVERSATION_SNAPSHOT',:link,1,:version,
            :opaque,:actor,clock_timestamp())"""),
            {
                "id": uuid4(),
                "target": UUID(target),
                "link": link,
                "version": state_version,
                "opaque": "a" * 64,
                "actor": actor,
            },
        )


def test_multiple_decisions_release_disposal_and_no_resurrection(content):
    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    created = capture(client, actors["admin"], target, body)
    assert created.status_code == 201, created.text
    first = created.json()
    snapshot = UUID(first["record_id"])
    with Session(identity.engine) as db:
        encrypted = db.get(ChannelSnapshotBody, snapshot).encrypted_payload
    another = {key: body[key] for key in ("reason", "expires_at", "affirmative")}
    another |= {
        "record_type": first["record_type"],
        "record_id": str(snapshot),
        "decision_reference": str(uuid4()),
    }
    second = hold(client, actors["admin"], target, another)
    assert second.status_code == 201, second.text
    with pytest.raises(DBAPIError, match="actively preserved"), identity.engine.begin() as db:
        db.execute(
            text("DELETE FROM channel_preservation_bodies WHERE snapshot_id=:id"), {"id": snapshot}
        )
    with pytest.raises(DBAPIError, match="immutable"), identity.engine.begin() as db:
        db.execute(
            text("UPDATE channel_preservation_bodies SET encrypted_payload=encrypted_payload")
        )
    assert release(client, actors["admin"], target, first["id"]).status_code == 200
    expire(identity)
    with Session(identity.engine) as db:
        assert db.get(ChannelSnapshotBody, snapshot) is not None
    identity.settings.channel_preservation_enabled = False
    assert release(client, actors["admin"], target, second.json()["id"]).status_code == 200
    expire(identity)
    with Session(identity.engine) as db:
        assert db.get(ChannelSnapshotBody, snapshot) is None
        assert db.get(ChannelSnapshotDisposal, snapshot) is not None
        assert db.get(ChannelSnapshot, snapshot) is not None
    with pytest.raises(DBAPIError, match="cannot be recreated"), identity.engine.begin() as db:
        db.execute(
            text("INSERT INTO channel_preservation_bodies VALUES(:id,:encrypted)"),
            {"id": snapshot, "encrypted": encrypted},
        )
    identity.settings.channel_preservation_enabled = True
    assert hold(client, actors["admin"], target, another).status_code == 404


def test_unlink_and_ordinary_source_cleanup_do_not_erase_active_evidence(content):
    from services.whatsapp_linking import LinkingService

    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    created = capture(client, actors["admin"], target, body)
    assert created.status_code == 201, created.text
    token = actors["learner"]["Authorization"].removeprefix("Bearer ")
    unlinked = LinkingService(identity).unlink(
        token, 1, uuid4(), uuid4(), UUID(body["source_link_id"])
    )
    assert unlinked.status == "UNLINKED"
    assert (
        inspect_source(
            client,
            actors["admin"],
            target,
            {k: body[k] for k in ("source_kind", "source_link_id", "link_revision")},
        ).status_code
        == 404
    )
    at = identity.clock() + timedelta(days=31)
    identity.clock = lambda: at
    expire(identity)
    with Session(identity.engine) as db:
        assert db.get(ChannelLink, UUID(body["source_link_id"])) is None
        assert db.get(ChannelSnapshotBody, UUID(created.json()["record_id"])) is not None


def test_signed_stop_barrier_blocks_capture_before_link_processing(identity, content):
    from pydantic import SecretStr

    from tests.integration.test_whatsapp_linking import payload, send_webhook

    service, client, actors, *_ = content
    target, body, _ = checked_capture(content)
    service.settings.whatsapp_app_secret = SecretStr("synthetic-signing-fixture-000000000000")
    assert send_webhook(identity, payload(service.clock(), "STOP")).status_code == 200
    with Session(service.engine) as db:
        assert db.get(ChannelLink, UUID(body["source_link_id"])).status == "ACTIVE"
    assert capture(client, actors["admin"], target, body).status_code == 404
    with Session(service.engine) as db:
        assert list(db.scalars(select(ChannelSnapshot))) == []


def test_exact_conversation_version_changes_without_timestamp_or_link_revision_change(content):
    from sqlalchemy import func

    from tests.integration.test_channel_receipt_holds import receipt

    identity, client, actors, *_ = content
    target, body, owner = checked_capture(content)
    _, outgoing = receipt(content)
    link = UUID(body["source_link_id"])
    with Session(identity.engine) as db, db.begin():
        row = db.get(OutboundMessage, outgoing)
        row.link_id, row.link_revision = link, 1
        now = db.scalar(select(func.clock_timestamp()))
        db.add(
            ConversationState(
                link_id=link,
                actor_id=owner,
                link_revision=1,
                session_id=None,
                expected_outbound_id=outgoing,
                updated_at=now,
                expires_at=now + timedelta(hours=24),
            )
        )
    source = {
        "source_kind": "CHANNEL_CONVERSATION_SNAPSHOT",
        "source_link_id": str(link),
        "link_revision": 1,
    }
    first = inspect_source(client, actors["admin"], target, source)
    assert first.status_code == 200, first.text
    decision = {
        key: body[key] for key in ("decision_reference", "reason", "expires_at", "affirmative")
    }
    with identity.engine.begin() as db:
        db.execute(
            text("UPDATE conversation_states SET updated_at=updated_at WHERE link_id=:id"),
            {"id": link},
        )
    rejected = capture(client, actors["admin"], target, source | first.json() | decision)
    assert (
        rejected.status_code == 409
        and rejected.json()["error"]["code"] == "SOURCE_VERSION_CONFLICT"
    )
    second = inspect_source(client, actors["admin"], target, source)
    assert first.json() != second.json()
    accepted = capture(client, actors["admin"], target, source | second.json() | decision)
    assert accepted.status_code == 201, accepted.text


@pytest.mark.parametrize(
    "stage", [ChannelSnapshot, ChannelSnapshotBody, LegalHold, LegalHoldReceipt]
)
def test_every_flushed_capture_stage_rolls_back_on_identity_error(content, stage):
    from sqlalchemy import event

    from services.identity import IdentityError

    identity, client, actors, *_ = content
    target, body, _ = checked_capture(content)

    def fail(session, context):
        if any(isinstance(row, stage) for row in session.new):
            raise IdentityError("SYNTHETIC_FAILURE", 409)

    event.listen(Session, "after_flush", fail)
    try:
        assert capture(client, actors["admin"], target, body).status_code == 409
    finally:
        event.remove(Session, "after_flush", fail)
    with Session(identity.engine) as db:
        for model in (ChannelSnapshot, ChannelSnapshotBody, LegalHold, LegalHoldReceipt):
            assert list(db.scalars(select(model))) == []
