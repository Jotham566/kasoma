"""FR-ID-006/FR-WA-006: only owned minimized receipts, never active capabilities."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.messaging import InboundMessage, OutboundMessage
from services.whatsapp_retention import expire
from tests.integration.test_legal_holds import hold, path, prepare, release

pytestmark = pytest.mark.integration


def receipt(content, *, owner=None, queued=False, pending=False):
    service, client, actors, *_ = content
    if owner is None:
        owner = UUID(client.get("/api/v1/me", headers=actors["learner"]).json()["id"])
    incoming, outgoing = uuid4(), uuid4()
    at = service.clock() - timedelta(days=31)
    with Session(service.engine) as db, db.begin():
        db.add(
            InboundMessage(
                id=incoming,
                message_hash=uuid4().hex,
                request_hash=uuid4().hex,
                request_id=uuid4(),
                sender_hash=uuid4().hex,
                sender_encrypted="synthetic-encrypted" if queued else None,
                actor_id=None if owner is False else owner,
                command="HELP",
                code_hash=None,
                status_reference=None,
                delivery_status=None,
                reply_reference=None,
                reply_encrypted=None,
                provider_at=at,
                received_at=at,
                available_at=at,
                processed_at=None if queued else at,
                status="QUEUED" if queued else "PROCESSED",
                attempts=0 if queued else 1,
                error_code=None,
            )
        )
        db.flush()
        db.add(
            OutboundMessage(
                id=outgoing,
                inbound_id=incoming,
                link_id=None,
                actor_id=None if owner is False else owner,
                recipient_hash=uuid4().hex,
                recipient_encrypted="synthetic-encrypted" if pending else None,
                template="HELP",
                link_revision=None,
                session_item_id=None,
                attempt_id=None,
                menu_topic_ids=None,
                status="PENDING" if pending else "SENT",
                provider_id=None if pending else "fake-" + uuid4().hex,
                attempts=0 if pending else 1,
                error_code=None,
                created_at=at,
                available_at=at,
                sent_at=None if pending else at,
                status_at=None,
            )
        )
    return incoming, outgoing


def scoped(body, kind, target):
    return body | {"record_type": kind, "record_id": str(target)}


def test_default_disabled_supported_types_and_release_remain_available(content):
    service, client, actors, *_ = content
    target, body = prepare(content)
    incoming, _ = receipt(content)
    request = scoped(body, "CHANNEL_INBOUND_RECEIPT", incoming)
    service.settings.channel_receipt_holds_enabled = False
    assert hold(client, actors["admin"], target, request).status_code == 409
    listing = client.get(path(target), headers=actors["admin"]).json()
    assert "CHANNEL_INBOUND_RECEIPT" not in listing["supported_record_types"]
    service.settings.channel_receipt_holds_enabled = True
    key = str(uuid4())
    created = hold(client, actors["admin"], target, request, key)
    assert created.status_code == 201, created.text
    assert hold(client, actors["admin"], target, request, key).json() == created.json()
    service.settings.channel_receipt_holds_enabled = False
    assert hold(client, actors["admin"], target, request, key).status_code == 409
    listing = client.get(path(target), headers=actors["admin"]).json()
    assert listing["data"][0]["id"] == created.json()["id"]
    assert release(client, actors["admin"], target, created.json()["id"]).status_code == 200


@pytest.mark.parametrize("state", ["queued", "pending", "unbound", "other"])
def test_nonterminal_unbound_and_other_owner_are_not_hold_targets(content, state):
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    owner = False if state == "unbound" else None
    if state == "other":
        owner = UUID(client.get("/api/v1/me", headers=actors["author"]).json()["id"])
    incoming, outgoing = receipt(
        content, owner=owner, queued=state == "queued", pending=state == "pending"
    )
    kind = "CHANNEL_OUTBOUND_RECEIPT" if state == "pending" else "CHANNEL_INBOUND_RECEIPT"
    source = outgoing if state == "pending" else incoming
    assert hold(client, actors["admin"], target, scoped(body, kind, source)).status_code == 404


@pytest.mark.parametrize("terminal", ["READ", "FAILED"])
def test_active_hold_guards_core_and_allows_only_monotonic_delivery(content, terminal):
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    incoming, outgoing = receipt(content)
    for kind, source in [
        ("CHANNEL_INBOUND_RECEIPT", incoming),
        ("CHANNEL_OUTBOUND_RECEIPT", outgoing),
    ]:
        created = hold(client, actors["admin"], target, scoped(body, kind, source))
        assert created.status_code == 201, created.text
    for table, source in [("inbound_messages", incoming), ("outbound_messages", outgoing)]:
        with (
            service.engine.begin() as db,
            pytest.raises(DBAPIError, match="Record is legally held"),
        ):
            db.execute(text(f"DELETE FROM {table} WHERE id=:id"), {"id": source})
    with service.engine.begin() as db, pytest.raises(DBAPIError, match="Terminal channel receipt"):
        db.execute(
            text("UPDATE inbound_messages SET command='STOP' WHERE id=:id"), {"id": incoming}
        )
    with service.engine.begin() as db, pytest.raises(DBAPIError, match="Terminal channel receipt"):
        db.execute(
            text("UPDATE outbound_messages SET recipient_hash='changed' WHERE id=:id"),
            {"id": outgoing},
        )
    if terminal == "FAILED":
        with service.engine.begin() as db:
            db.execute(
                text(
                    "UPDATE outbound_messages SET status='FAILED',error_code='PROVIDER_FAILED',"
                    "status_at=:at WHERE id=:id"
                ),
                {"id": outgoing, "at": service.clock()},
            )
    else:
        for status in ["DELIVERED", "READ"]:
            with service.engine.begin() as db:
                db.execute(
                    text("UPDATE outbound_messages SET status=:status,status_at=:at WHERE id=:id"),
                    {"id": outgoing, "status": status, "at": service.clock()},
                )
    with service.engine.begin() as db, pytest.raises(DBAPIError, match="Terminal channel receipt"):
        db.execute(
            text("UPDATE outbound_messages SET status='SENT' WHERE id=:id"), {"id": outgoing}
        )
    with service.engine.begin() as db, pytest.raises(DBAPIError, match="Terminal channel receipt"):
        db.execute(
            text("UPDATE outbound_messages SET status_at=:at WHERE id=:id"),
            {"id": outgoing, "at": service.clock() - timedelta(seconds=1)},
        )


def test_held_receipts_do_not_fill_cleanup_batch_and_multiple_holds_apply(content):
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    incoming, outgoing = receipt(content)
    held = []
    for _ in range(2):
        result = hold(
            client, actors["admin"], target, scoped(body, "CHANNEL_OUTBOUND_RECEIPT", outgoing)
        )
        assert result.status_code == 201, result.text
        held.append(result.json()["id"])
    with Session(service.engine) as db:
        owner = db.get(InboundMessage, incoming).actor_id
    for _ in range(101):
        receipt(content, owner=owner)
    expire(service)
    with Session(service.engine) as db:
        assert db.get(OutboundMessage, outgoing) is not None
        assert db.get(InboundMessage, incoming) is not None
        assert db.scalar(select(func.count()).select_from(OutboundMessage)) == 2
    expire(service)
    assert release(client, actors["admin"], target, held[0]).status_code == 200
    expire(service)
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(OutboundMessage)) == 1
    assert release(client, actors["admin"], target, held[1]).status_code == 200
    expire(service)
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(OutboundMessage)) == 0
        assert db.scalar(select(func.count()).select_from(InboundMessage)) == 0


def insert_hold(db, original, kind, source):
    db.execute(
        text("""INSERT INTO legal_holds
        (id,request_id,record_type,record_id,decision_reference,reason,created_by,created_at,expires_at)
        SELECT :id,request_id,:kind,:source,:decision,reason,created_by,clock_timestamp(),expires_at
        FROM legal_holds WHERE id=:original"""),
        {"id": uuid4(), "kind": kind, "source": source, "decision": uuid4(), "original": original},
    )


@pytest.mark.parametrize("outbound", [False, True])
def test_sql_hold_validation_cannot_bypass_nonterminal_eligibility(content, outbound):
    service, client, actors, *_ = content
    target, body = prepare(content)
    original = hold(client, actors["admin"], target, body).json()["id"]
    incoming, outgoing = receipt(content, queued=not outbound, pending=outbound)
    kind = "CHANNEL_OUTBOUND_RECEIPT" if outbound else "CHANNEL_INBOUND_RECEIPT"
    with service.engine.begin() as db, pytest.raises(DBAPIError, match="Hold target must belong"):
        insert_hold(db, UUID(original), kind, outgoing if outbound else incoming)


def test_delete_transaction_started_before_hold_uses_current_database_clock(content):
    service, client, actors, *_ = content
    target, body = prepare(content)
    original = UUID(hold(client, actors["admin"], target, body).json()["id"])
    incoming, _ = receipt(content)
    with service.engine.begin() as deleting:
        deleting.execute(select(func.transaction_timestamp()))
        with service.engine.begin() as creating:
            insert_hold(creating, original, "CHANNEL_INBOUND_RECEIPT", incoming)
        assert deleting.scalar(
            select(func.record_is_held("CHANNEL_INBOUND_RECEIPT", incoming, func.clock_timestamp()))
        )
        assert not deleting.scalar(
            select(
                func.record_is_held(
                    "CHANNEL_INBOUND_RECEIPT", incoming, func.transaction_timestamp()
                )
            )
        )
        with pytest.raises(DBAPIError, match="Record is legally held"):
            deleting.execute(text("DELETE FROM inbound_messages WHERE id=:id"), {"id": incoming})


def test_historical_expired_hold_does_not_extend_normal_retention(content):
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    incoming, outgoing = receipt(content)
    with service.engine.connect() as db:
        already_ended = db.scalar(select(func.clock_timestamp())) - timedelta(seconds=1)
    # The fixture clock is historical. Store a finite historical decision whose end
    # is now past under the database clock used by ordinary retention/DELETE guards.
    result = hold(
        client,
        actors["admin"],
        target,
        scoped(body, "CHANNEL_INBOUND_RECEIPT", incoming)
        | {"expires_at": already_ended.isoformat()},
    )
    assert result.status_code == 201, result.text
    expire(service)
    with Session(service.engine) as db:
        assert db.get(InboundMessage, incoming) is None
        assert db.get(OutboundMessage, outgoing) is None


def test_host_clock_ahead_is_capped_at_database_clock(content):
    from tests.integration.test_identity import login

    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    incoming, _ = receipt(content)
    with service.engine.connect() as db:
        ahead = db.scalar(select(func.clock_timestamp())) + timedelta(seconds=30)
    service.clock = lambda: ahead
    fresh, _ = login(client, "admin@example.invalid")
    result = hold(client, fresh, target, scoped(body, "CHANNEL_INBOUND_RECEIPT", incoming))
    assert result.status_code == 201, result.text
    from datetime import datetime

    with service.engine.connect() as db:
        assert datetime.fromisoformat(result.json()["created_at"]) <= db.scalar(
            select(func.clock_timestamp())
        )


@pytest.mark.parametrize("identity", ["0033"], indirect=True)
def test_upgrade_preserves_existing_hold_and_adds_channel_receipt_target(content):
    import os
    import subprocess

    service, client, actors, *_ = content
    target, body = prepare(content)
    key = str(uuid4())
    original = hold(client, actors["admin"], target, body, key)
    assert original.status_code == 201, original.text
    incoming, _ = receipt(content)
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": service.settings.database_url.get_secret_value()},
        )
    assert hold(client, actors["admin"], target, body, key).json() == original.json()
    service.settings.channel_receipt_holds_enabled = True
    created = hold(
        client, actors["admin"], target, scoped(body, "CHANNEL_INBOUND_RECEIPT", incoming)
    )
    assert created.status_code == 201, created.text


@pytest.mark.parametrize("action", ["STOP", "UNLINK"])
def test_real_signed_channel_opt_out_still_clears_live_state_with_receipt_holds(
    identity, content, action
):
    from services.domain.messaging import ChannelLink, ConversationState
    from services.whatsapp_delivery import deliver_one
    from services.whatsapp_processing import process_one
    from tests.integration.test_whatsapp_practice import Flow

    flow = Flow(identity, content)
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    with Session(service.engine) as db:
        incoming = db.scalar(select(InboundMessage).where(InboundMessage.command == "LINK"))
        outgoing = db.scalar(
            select(OutboundMessage).where(OutboundMessage.inbound_id == incoming.id)
        )
        sources = [
            ("CHANNEL_INBOUND_RECEIPT", incoming.id),
            ("CHANNEL_OUTBOUND_RECEIPT", outgoing.id),
        ]
    for kind, source in sources:
        result = hold(client, actors["admin"], target, scoped(body, kind, source))
        assert result.status_code == 201, result.text
    flow.begin()
    flow.incoming("HELP")
    assert process_one(service)
    if action == "STOP":
        flow.incoming("STOP")
        assert process_one(service)
    else:
        link = client.get("/api/v1/channels/whatsapp/link", headers=flow.headers).json()
        result = client.request(
            "DELETE",
            "/api/v1/channels/whatsapp/link",
            headers=flow.headers | {"Idempotency-Key": str(uuid4())},
            json={"expected_revision": link["revision"], "expected_link_id": link["link_id"]},
        )
        assert result.status_code == 200, result.text
    assert not deliver_one(service, flow.provider)
    with Session(service.engine) as db:
        link = db.scalar(select(ChannelLink))
        assert link.status == ("STOPPED" if action == "STOP" else "UNLINKED")
        if action == "UNLINK":
            assert link.external_identifier_encrypted is None
        assert db.scalar(select(func.count()).select_from(ConversationState)) == 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(OutboundMessage)
                .where(OutboundMessage.status == "PENDING")
            )
            == 0
        )
        for kind, source in sources:
            model = InboundMessage if kind == "CHANNEL_INBOUND_RECEIPT" else OutboundMessage
            assert db.get(model, source) is not None


def test_hold_creation_serializes_with_cleanup_before_receipt_selection(content, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from time import monotonic, sleep

    from services import whatsapp_linking
    from services.legal_hold_contracts import HoldInput
    from services.legal_holds import LegalHoldService

    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    target, body = prepare(content)
    incoming, _ = receipt(content)
    acquired, proceed = Event(), Event()
    original = whatsapp_linking.channel_lock

    def paused(identity, db):
        original(identity, db)
        acquired.set()
        assert proceed.wait(5)

    monkeypatch.setattr(whatsapp_linking, "channel_lock", paused)
    value = HoldInput.model_validate(scoped(body, "CHANNEL_INBOUND_RECEIPT", incoming))
    token = actors["admin"]["Authorization"].removeprefix("Bearer ")
    number = int(service.digest("lock", "whatsapp-channel-mutations")[:15], 16)
    with ThreadPoolExecutor(max_workers=2) as pool:
        creating = pool.submit(
            LegalHoldService(service).create, token, UUID(target), value, uuid4(), uuid4()
        )
        try:
            assert acquired.wait(5)
            cleanup = pool.submit(expire, service)
            deadline = monotonic() + 3
            waiting = False
            while monotonic() < deadline:
                with service.engine.connect() as db:
                    waiting = db.scalar(
                        text("""SELECT EXISTS(SELECT 1 FROM pg_locks
                        WHERE locktype='advisory' AND NOT granted
                        AND classid::bigint=:upper AND objid::bigint=:lower)"""),
                        {"upper": number >> 32, "lower": number & 0xFFFFFFFF},
                    )
                if waiting:
                    break
                sleep(0.01)
            assert waiting and not cleanup.done()
        finally:
            proceed.set()
        assert creating.result(timeout=5).record_id == incoming
        cleanup.result(timeout=5)
    with Session(service.engine) as db:
        assert db.get(InboundMessage, incoming) is not None


def test_future_claim_clock_fails_closed_without_database_error_or_hold(content):
    from services.domain.data_requests import LegalHold
    from tests.integration.test_data_requests import claim, create
    from tests.integration.test_identity import login

    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    incoming, _ = receipt(content)
    with service.engine.connect() as db:
        ahead = db.scalar(select(func.clock_timestamp())) + timedelta(seconds=30)
    service.clock = lambda: ahead
    learner, _ = login(client, "learner@example.invalid")
    admin, _ = login(client, "admin@example.invalid")
    target = create(client, learner, "DELETE").json()["id"]
    assert claim(client, admin, target).status_code == 200
    response = hold(
        client,
        admin,
        target,
        {
            "record_type": "CHANNEL_INBOUND_RECEIPT",
            "record_id": str(incoming),
            "decision_reference": str(uuid4()),
            "reason": "LEGAL_OBLIGATION",
            "expires_at": (ahead + timedelta(days=1)).isoformat(),
            "affirmative": True,
        },
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HOLD_TARGET_UNAVAILABLE"
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 0


def test_held_practice_menu_json_supports_noop_and_delivery_callback(identity, content):
    from sqlalchemy import update

    from services.whatsapp_delivery import deliver_one
    from services.whatsapp_processing import process_one
    from tests.integration.test_whatsapp_practice import Flow

    flow = Flow(identity, content)
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    flow.incoming("START")
    assert process_one(service)
    assert deliver_one(service, flow.provider)
    with Session(service.engine) as db:
        menu = db.scalar(select(OutboundMessage).where(OutboundMessage.template == "PRACTICE_MENU"))
        source, topics = menu.id, list(menu.menu_topic_ids)
        assert topics
    target, body = prepare(content)
    result = hold(client, actors["admin"], target, scoped(body, "CHANNEL_OUTBOUND_RECEIPT", source))
    assert result.status_code == 201, result.text
    with service.engine.begin() as db:
        db.execute(
            text("UPDATE outbound_messages SET status_at=status_at WHERE id=:id"), {"id": source}
        )
        db.execute(
            text("UPDATE outbound_messages SET status='DELIVERED',status_at=:at WHERE id=:id"),
            {"id": source, "at": service.clock()},
        )
    with service.engine.begin() as db, pytest.raises(DBAPIError, match="Terminal channel receipt"):
        db.execute(
            update(OutboundMessage)
            .where(OutboundMessage.id == source)
            .values(menu_topic_ids=["synthetic-other"])
        )
    with Session(service.engine) as db:
        assert db.get(OutboundMessage, source).menu_topic_ids == topics


@pytest.mark.parametrize("identity", ["0034"], indirect=True)
def test_json_guard_forward_upgrade_keeps_existing_menu_hold(identity, content):
    import os
    import subprocess

    from services.whatsapp_delivery import deliver_one
    from services.whatsapp_processing import process_one
    from tests.integration.test_whatsapp_practice import Flow

    flow = Flow(identity, content)
    service, client, actors, *_ = content
    service.settings.channel_receipt_holds_enabled = True
    flow.incoming("START")
    assert process_one(service)
    assert deliver_one(service, flow.provider)
    with Session(service.engine) as db:
        source = db.scalar(
            select(OutboundMessage.id).where(OutboundMessage.template == "PRACTICE_MENU")
        )
    target, body = prepare(content)
    value, key = scoped(body, "CHANNEL_OUTBOUND_RECEIPT", source), str(uuid4())
    held = hold(client, actors["admin"], target, value, key)
    assert held.status_code == 201, held.text
    with (
        service.engine.begin() as db,
        pytest.raises(DBAPIError, match="equality operator for type json"),
    ):
        db.execute(
            text("UPDATE outbound_messages SET status_at=status_at WHERE id=:id"), {"id": source}
        )
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": service.settings.database_url.get_secret_value()},
        )
    assert hold(client, actors["admin"], target, value, key).json() == held.json()
    with service.engine.begin() as db:
        db.execute(
            text("UPDATE outbound_messages SET status_at=status_at WHERE id=:id"), {"id": source}
        )
        db.execute(
            text("UPDATE outbound_messages SET status='DELIVERED',status_at=:at WHERE id=:id"),
            {"id": source, "at": service.clock()},
        )
