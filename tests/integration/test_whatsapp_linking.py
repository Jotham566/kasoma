"""FR-WA-001/006: current consent, recent auth and replay-safe owner mutations."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import Session

from services.domain.messaging import ChannelLink, ChannelSender, LinkCode
from services.whatsapp_linking import LinkingService
from tests.integration.test_identity import consent, login, profile, request_code

pytestmark = pytest.mark.integration
PATH = "/api/v1/channels/whatsapp"


def ready(identity, birth="2000-01-01", email="learner@example.invalid"):
    service, client, _, _ = identity
    # Explicit deterministic test-only configuration, independent of a developer's .env.
    service.settings.whatsapp_app_secret = SecretStr("synthetic-signing-fixture-000000000000")
    headers, tokens = login(client, email)
    view, _ = profile(client, headers, birth)
    if birth == "2000-01-01":
        assert consent(client, headers, "SELF").json()["learning_allowed"]
    return headers, tokens, UUID(view["id"])


def issue(client, headers, key=None):
    return client.post(
        PATH + "/link-code", headers=headers | {"Idempotency-Key": str(key or uuid4())}
    )


def test_code_consent_recent_auth_expiry_idempotency_and_safe_storage(identity, caplog):
    service, client, _, now = identity
    headers, _, actor = ready(identity)
    assert issue(client, {}).status_code == 401
    key = uuid4()
    created = issue(client, headers, key)
    assert created.status_code == 201, created.text
    assert created.headers["cache-control"] == "no-store"
    assert created.json() == issue(client, headers, key).json()
    with Session(service.engine) as db:
        row = db.scalar(select(LinkCode).where(LinkCode.user_id == actor))
        assert row.code_hash != created.json()["code"]
        assert row.expires_at - row.created_at == timedelta(minutes=5)
    now[0] += timedelta(minutes=5)
    assert issue(client, headers, key).status_code == 410
    assert issue(client, headers).status_code == 201
    assert consent(client, headers, "WITHDRAW").status_code == 200
    assert issue(client, headers).status_code == 403
    assert client.get(PATH + "/link", headers=headers).json()["status"] == "NOT_LINKED"
    assert consent(client, headers, "SELF").status_code == 200
    now[0] += timedelta(minutes=5)
    result = issue(client, headers)
    assert result.status_code == 401 and result.json()["error"]["code"] == "REAUTH_REQUIRED"
    assert created.json()["code"] not in caplog.text


def test_minor_requires_guardian_assent_and_current_policy(identity):
    service, client, _, _ = identity
    headers, _, _ = ready(identity, "2010-01-01")
    assert issue(client, headers).status_code == 403
    assert consent(client, headers, "ASSENT").status_code == 200
    assert issue(client, headers).status_code == 403
    challenge = request_code(client, "guardian@example.invalid", "GUARDIAN", headers)
    assert consent(
        client,
        headers,
        "GUARDIAN",
        guardian_name="Synthetic guardian",
        guardian_relationship="Parent",
        challenge_id=challenge,
        code="246810",
    ).json()["learning_allowed"]
    assert issue(client, headers).status_code == 201
    service.settings.consent_policy_version = "synthetic-development-v2"
    assert issue(client, headers).status_code == 403


def test_new_code_revokes_old_rate_limit_and_concurrent_same_key(identity):
    service, client, _, _ = identity
    headers, tokens, actor = ready(identity)
    key = uuid4()
    linking = LinkingService(service)

    def run(_):
        return linking.issue(tokens["access_token"], key, uuid4())

    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = list(pool.map(run, range(2)))
    assert first == second
    for _ in range(4):
        assert issue(client, headers).status_code == 201
    assert issue(client, headers).status_code == 429
    assert issue(client, headers, key).status_code == 410
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(LinkCode)) == 5
        assert (
            db.scalar(
                select(func.count())
                .select_from(LinkCode)
                .where(LinkCode.user_id == actor, LinkCode.code_hash.is_not(None))
            )
            == 1
        )
        original = db.get(LinkCode, first.id)
        assert original.revoked_at and original.code_hash is None
    with pytest.raises(ProgrammingError), service.engine.begin() as db:
        db.execute(
            text("UPDATE link_codes SET code_hash='resurrected' WHERE id=:id"), {"id": first.id}
        )


def linked_fixture(service, actor, now):
    sender_hash = service.digest("wa-sender", "+256700000001")
    with Session(service.engine) as db, db.begin():
        db.add(ChannelSender(sender_hash=sender_hash, updated_at=now))
        db.flush()
        link = ChannelLink(
            id=uuid4(),
            user_id=actor,
            sender_hash=sender_hash,
            external_identifier_encrypted=service.encrypt("+256700000001"),
            revision=1,
            status="ACTIVE",
            linked_at=now,
            opted_out_at=None,
            updated_at=now,
        )
        db.add(link)
        db.flush()
        return link.id


def test_unlink_revision_retry_after_relink_and_ownership(identity):
    service, client, _, now = identity
    headers, tokens, actor = ready(identity)
    link_id = linked_fixture(service, actor, now[0])
    key = uuid4()
    linking = LinkingService(service)
    assert issue(client, headers).status_code == 201
    other, _, _ = ready(identity, email="other@example.invalid")
    assert client.get(PATH + "/link", headers=other).json()["status"] == "NOT_LINKED"
    wrong = client.request(
        "DELETE",
        PATH + "/link",
        headers=headers | {"Idempotency-Key": str(key)},
        json={"expected_revision": 0, "expected_link_id": str(link_id)},
    )
    assert wrong.status_code == 409
    # Consent withdrawal cannot trap the owner in a bound channel.
    assert consent(client, headers, "WITHDRAW").status_code == 200
    view = linking.unlink(tokens["access_token"], 1, key, uuid4(), link_id)
    assert view.status == "UNLINKED" and view.revision == 2
    with Session(service.engine) as db:
        assert db.get(ChannelLink, link_id).external_identifier_encrypted is None
        assert db.scalar(select(LinkCode)).code_hash is None
    now[0] += timedelta(seconds=1)
    with Session(service.engine) as db, db.begin():
        row = db.get(ChannelLink, link_id)
        row.status, row.linked_at, row.updated_at = "ACTIVE", now[0], now[0]
        row.external_identifier_encrypted = service.encrypt("+256700000001")
        row.opted_out_at, row.revision = None, 3
    retry = linking.unlink(tokens["access_token"], 1, key, uuid4(), link_id)
    assert retry.status == "ACTIVE" and retry.revision == 3
    result = client.request(
        "DELETE",
        PATH + "/link",
        headers=headers | {"Idempotency-Key": str(key)},
        json={"expected_revision": 3, "expected_link_id": str(link_id)},
    )
    assert result.status_code == 409
    with pytest.raises((ProgrammingError, IntegrityError)), service.engine.begin() as db:
        db.execute(
            text("UPDATE channel_links SET user_id=:actor WHERE id=:id"),
            {"actor": uuid4(), "id": link_id},
        )


def test_missing_signing_key_fails_closed(identity):
    service, client, _, _ = identity
    headers, _, _ = ready(identity)
    service.settings.whatsapp_app_secret = None
    assert issue(client, headers).status_code == 503


def payload(now, body="HELP", sender="256700000001", message_id=None):
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "synthetic-business",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "synthetic-phone"},
                            "messages": [
                                {
                                    "id": message_id or "wamid." + str(uuid4()),
                                    "from": sender,
                                    "timestamp": str(int(now.timestamp())),
                                    "type": "text",
                                    "text": {"body": body},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def send_webhook(identity, value, *, signature=True):
    import hashlib
    import hmac
    import json

    service, client, _, _ = identity
    raw = json.dumps(value).encode()
    key = service.settings.whatsapp_app_secret.get_secret_value().encode()
    headers = {"Content-Type": "application/json"}
    if signature:
        headers["X-Hub-Signature-256"] = "sha256=" + hmac.new(key, raw, hashlib.sha256).hexdigest()
    return client.post("/api/v1/webhooks/whatsapp", content=raw, headers=headers)


def test_durable_replay_conflict_atomic_batch_and_stop_before_worker(identity):
    from services.domain.messaging import InboundMessage, OutboundMessage
    from services.whatsapp_delivery import FakeChannelDelivery, deliver_one
    from services.whatsapp_processing import process_one

    service, client, _, now = identity
    headers, _, _ = ready(identity)
    service.settings.whatsapp_outbound_enabled = True
    issued = issue(client, headers).json()
    message = payload(now[0], "LINK " + issued["code"])
    assert send_webhook(identity, message, signature=False).status_code == 401
    assert send_webhook(identity, message).status_code == 200
    assert send_webhook(identity, message).status_code == 200
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(InboundMessage)) == 1
        assert db.scalar(select(InboundMessage)).status == "QUEUED"
    assert process_one(service)
    assert not process_one(service)
    assert client.get(PATH + "/link", headers=headers).json()["status"] == "ACTIVE"
    now[0] += timedelta(seconds=1)
    stopped = payload(now[0], "STOP")
    assert send_webhook(identity, stopped).status_code == 200
    # Intake itself stops delivery before the worker processes the STOP command.
    view = client.get(PATH + "/link", headers=headers).json()
    assert view["status"] == "STOPPED" and view["opted_out_at"]
    assert not deliver_one(service, FakeChannelDelivery())
    with Session(service.engine) as db:
        out = db.scalar(select(OutboundMessage))
        assert out.status == "CANCELLED" and out.recipient_encrypted is None
    assert process_one(service)
    assert client.get(PATH + "/link", headers=headers).json()["status"] == "STOPPED"
    value = message["entry"][0]["changes"][0]["value"]
    value["messages"][0]["text"]["body"] = "changed conflicting content"
    value["messages"].insert(0, payload(now[0])["entry"][0]["changes"][0]["value"]["messages"][0])
    assert send_webhook(identity, message).status_code == 409
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(InboundMessage)) == 2
        assert all(
            r.sender_encrypted is None and r.code_hash is None
            for r in db.scalars(select(InboundMessage))
        )


def test_delivery_withdrawal_retry_and_terminal_failure(identity, caplog):
    from services.domain.messaging import OutboundMessage
    from services.whatsapp_delivery import FakeChannelDelivery, deliver_one
    from services.whatsapp_processing import process_one

    service, client, _, now = identity
    headers, _, _ = ready(identity)
    service.settings.whatsapp_outbound_enabled = True
    code = issue(client, headers).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + code)).status_code == 200
    assert process_one(service)
    assert consent(client, headers, "WITHDRAW").status_code == 200
    assert deliver_one(service, FakeChannelDelivery())
    with Session(service.engine) as db:
        assert db.scalar(select(OutboundMessage)).error_code == "CONSENT_REQUIRED"
    assert consent(client, headers, "SELF").status_code == 200
    now[0] += timedelta(seconds=1)
    assert send_webhook(identity, payload(now[0], "HELP")).status_code == 200
    assert process_one(service)

    class Failed:
        def send(self, *args):
            raise RuntimeError("CANARY confidential provider diagnostic")

    assert deliver_one(service, Failed())
    assert not deliver_one(service, Failed())
    now[0] += timedelta(seconds=60)
    assert deliver_one(service, Failed())
    now[0] += timedelta(seconds=120)
    assert deliver_one(service, Failed())
    with Session(service.engine) as db:
        failed = db.scalar(select(OutboundMessage).where(OutboundMessage.status == "FAILED"))
        assert failed.attempts == 3 and failed.recipient_encrypted is None
    assert "CANARY" not in caplog.text
    assert send_webhook(identity, payload(now[0], "HELP")).status_code == 200
    assert process_one(service)
    assert deliver_one(service, FakeChannelDelivery())
    with Session(service.engine) as db:
        sent = db.scalar(select(OutboundMessage).where(OutboundMessage.status == "SENT"))
        assert sent.provider_id == "wamid.fake." + str(sent.id)
        assert sent.recipient_encrypted is None


def test_webhook_challenge_streaming_size_and_destination(identity):
    service, client, _, now = identity
    ready(identity)
    service.settings.whatsapp_verify_token = SecretStr("synthetic-challenge-token-000000000")
    endpoint = "/api/v1/webhooks/whatsapp"
    args = {
        "hub.mode": "subscribe",
        "hub.challenge": "123456",
        "hub.verify_token": service.settings.whatsapp_verify_token.get_secret_value(),
    }
    assert client.get(endpoint, params=args).text == "123456"
    assert client.get(endpoint, params=args | {"hub.verify_token": "wrong"}).status_code == 401
    assert client.post(endpoint, content=iter([b"x" * 32768] * 3)).status_code == 413
    bad = payload(now[0])
    bad["entry"][0]["id"] = "different-business"
    assert send_webhook(identity, bad).status_code == 400


def test_processing_rolls_back_link_and_code_before_bounded_retry(identity, monkeypatch, caplog):
    import services.whatsapp_processing as processing
    from services.domain.messaging import InboundMessage, OutboundMessage

    service, client, _, now = identity
    headers, _, _ = ready(identity)
    code = issue(client, headers).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + code)).status_code == 200
    original = processing.queue_reply

    def broken(*args):
        raise RuntimeError("DO NOT LOG raw private payload")

    monkeypatch.setattr(processing, "queue_reply", broken)
    assert processing.process_one(service)
    with Session(service.engine) as db:
        assert db.scalar(select(LinkCode)).code_hash is not None
        assert db.scalar(select(ChannelLink)) is None
        assert db.scalar(select(OutboundMessage)) is None
        assert db.scalar(select(InboundMessage)).attempts == 1
    assert not processing.process_one(service)
    now[0] += timedelta(seconds=60)
    monkeypatch.setattr(processing, "queue_reply", original)
    assert processing.process_one(service)
    with Session(service.engine) as db:
        row = db.scalar(select(InboundMessage))
        assert row.status == "PROCESSED" and row.attempts == 2 and row.error_code is None
        assert db.scalar(select(ChannelLink)).status == "ACTIVE"
        correlation = str(row.request_id)
    assert "DO NOT LOG" not in caplog.text
    assert correlation in caplog.text and "channel.inbound.processed" in caplog.text


def test_unbound_stop_blocks_later_help_and_expired_codes_clear(identity):
    from services.domain.messaging import InboundMessage, OutboundMessage
    from services.whatsapp_delivery import FakeChannelDelivery, deliver_one
    from services.whatsapp_processing import process_one
    from services.whatsapp_retention import expire

    service, client, _, now = identity
    headers, _, _ = ready(identity)
    service.settings.whatsapp_outbound_enabled = True
    assert issue(client, headers).status_code == 201
    assert send_webhook(identity, payload(now[0], "STOP")).status_code == 200
    assert process_one(service)
    now[0] += timedelta(seconds=1)
    assert send_webhook(identity, payload(now[0], "HELP")).status_code == 200
    assert process_one(service)
    assert deliver_one(service, FakeChannelDelivery())
    with Session(service.engine) as db:
        assert db.scalar(select(OutboundMessage)).status == "CANCELLED"
    now[0] += timedelta(minutes=5)
    expire(service)
    with Session(service.engine) as db:
        assert db.scalar(select(LinkCode)).code_hash is None
    now[0] += timedelta(days=31)
    expire(service)
    with Session(service.engine) as db:
        for model in [LinkCode, InboundMessage, OutboundMessage, ChannelSender]:
            assert db.scalar(select(func.count()).select_from(model)) == 0


def test_owned_export_and_deletion_inventory_include_only_bound_channel_records(identity):
    from services.data_export_projection import project
    from services.deletion_preview import inventory
    from services.whatsapp_processing import process_one

    service, client, _, now = identity
    headers, _, actor = ready(identity)
    _, _, other = ready(identity, email="another@example.invalid")
    code = issue(client, headers).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + code)).status_code == 200
    assert process_one(service)
    with Session(service.engine) as db:
        bundle = project(service, db, actor, uuid4())
        assert bundle.records["channel_links"][0]["identifier"] == "+256700000001"
        assert len(bundle.records["channel_inbound"]) == 1
        assert len(bundle.records["channel_outbound"]) == 1
        assert code not in bundle.model_dump_json()
        foreign = project(service, db, other, uuid4())
        assert foreign.records["channel_links"] == foreign.records["channel_inbound"] == []
        counts = {r.source: r.count for r in inventory(db, actor)}
        assert (
            counts["channel_links"]
            == counts["inbound_messages"]
            == counts["outbound_messages"]
            == 1
        )


def test_sender_collision_stop_relink_and_verified_phone_conflict(identity):
    from services.domain.messaging import InboundMessage
    from services.whatsapp_processing import process_one

    service, client, _, now = identity
    first, _, _ = ready(identity)
    other, _, _ = ready(identity, email="second-owner@example.invalid")
    code = issue(client, first).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + code)).status_code == 200
    assert process_one(service)
    # Single-use even under a different sender/provider message ID.
    assert (
        send_webhook(identity, payload(now[0], "LINK " + code, "256700000002")).status_code == 200
    )
    assert process_one(service)
    other_code = issue(client, other).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + other_code)).status_code == 200
    assert process_one(service)
    assert client.get(PATH + "/link", headers=other).json()["status"] == "NOT_LINKED"
    # A pre-STOP code cannot reactivate; a fresh post-STOP code can.
    old = issue(client, first).json()["code"]
    now[0] += timedelta(seconds=1)
    assert send_webhook(identity, payload(now[0], "STOP")).status_code == 200
    assert process_one(service)
    assert send_webhook(identity, payload(now[0], "LINK " + old)).status_code == 200
    assert process_one(service)
    assert client.get(PATH + "/link", headers=first).json()["status"] == "STOPPED"
    now[0] += timedelta(seconds=1)
    fresh = issue(client, first).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + fresh)).status_code == 200
    assert process_one(service)
    assert client.get(PATH + "/link", headers=first).json()["status"] == "ACTIVE"
    login(client, "+256700000003")
    assert (
        send_webhook(identity, payload(now[0], "LINK " + other_code, "256700000003")).status_code
        == 200
    )
    assert process_one(service)
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(ChannelLink)) == 1
        assert (
            db.scalar(
                select(func.count())
                .select_from(InboundMessage)
                .where(InboundMessage.status == "REJECTED")
            )
            == 4
        )


def test_status_callbacks_bound_to_recipient_and_never_regress(identity):
    from services.domain.messaging import OutboundMessage
    from services.whatsapp_delivery import FakeChannelDelivery, deliver_one
    from services.whatsapp_processing import process_one

    service, client, _, now = identity
    headers, _, _ = ready(identity)
    service.settings.whatsapp_outbound_enabled = True
    code = issue(client, headers).json()["code"]
    assert send_webhook(identity, payload(now[0], "LINK " + code)).status_code == 200
    assert process_one(service) and deliver_one(service, FakeChannelDelivery())
    with Session(service.engine) as db:
        provider_id = db.scalar(select(OutboundMessage)).provider_id

    def callback(status, sender="256700000001"):
        document = payload(now[0])
        value = document["entry"][0]["changes"][0]["value"]
        del value["messages"]
        value["statuses"] = [
            {
                "id": provider_id,
                "status": status,
                "recipient_id": sender,
                "timestamp": str(int(now[0].timestamp())),
            }
        ]
        assert send_webhook(identity, document).status_code == 200
        assert process_one(service)

    callback("read", "256700000002")
    with Session(service.engine) as db:
        assert db.scalar(select(OutboundMessage)).status == "SENT"
    now[0] += timedelta(seconds=1)
    callback("read")
    now[0] += timedelta(seconds=1)
    callback("sent")
    now[0] += timedelta(seconds=1)
    callback("failed")
    with Session(service.engine) as db:
        assert db.scalar(select(OutboundMessage)).status == "READ"


def test_final_processing_failure_scrubs_payload_and_outbound_limit_is_configurable(
    identity, monkeypatch
):
    import services.whatsapp_processing as processing
    from services.domain.messaging import InboundMessage, OutboundMessage
    from services.whatsapp_delivery import FakeChannelDelivery, deliver_one

    service, client, _, now = identity
    ready(identity)
    service.settings.whatsapp_outbound_enabled = True
    service.settings.whatsapp_outbound_per_minute = 1
    for _ in range(2):
        assert send_webhook(identity, payload(now[0])).status_code == 200
        assert processing.process_one(service)
        assert deliver_one(service, FakeChannelDelivery())
    with Session(service.engine) as db:
        assert {r.status for r in db.scalars(select(OutboundMessage))} == {"SENT", "CANCELLED"}
    assert send_webhook(identity, payload(now[0], "LINK ABCDEF012345")).status_code == 200

    def broken(*args):
        raise RuntimeError("private diagnostic")

    monkeypatch.setattr(processing, "apply_command", broken)
    for elapsed in [0, 60, 120]:
        now[0] += timedelta(seconds=elapsed)
        assert processing.process_one(service)
    with Session(service.engine) as db:
        failed = db.scalar(select(InboundMessage).where(InboundMessage.status == "FAILED"))
        assert failed.attempts == 3 and failed.sender_encrypted is None and failed.code_hash is None
