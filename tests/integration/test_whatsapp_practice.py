"""FR-WA-002–006: signed local messages through atomic shared practice and fake delivery."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.assessment import AssessmentService
from services.data_export_projection import project
from services.deletion_preview import inventory
from services.domain.assessment import AssessmentSession, Attempt
from services.domain.mastery import MasteryEvidence
from services.domain.messaging import ConversationState, InboundMessage, OutboundMessage
from services.whatsapp_delivery import FakeChannelDelivery, deliver_one
from services.whatsapp_processing import process_one
from services.whatsapp_retention import expire
from tests.integration.test_channel_assessment import ready
from tests.integration.test_identity import consent
from tests.integration.test_whatsapp_linking import issue, payload, send_webhook

pytestmark = pytest.mark.integration


class Recorder(FakeChannelDelivery):
    def __init__(self):
        self.messages = []

    def send(self, key, recipient, body):
        self.messages.append((key, body))
        return super().send(key, recipient, body)


class Flow:
    def __init__(self, identity, content, response_type="SINGLE_CHOICE"):
        self.identity = identity
        self.service, self.client, self.actors, _, self.versions, self.plan = ready(
            content, response_type
        )
        self.now = identity[3]
        self.service.settings.whatsapp_outbound_enabled = True
        self.service.settings.whatsapp_outbound_per_minute = 60
        self.service.settings.whatsapp_app_secret = SecretStr(
            "synthetic-signing-fixture-000000000000"
        )
        self.provider = Recorder()
        self.headers = self.actors["learner"]
        self.actor = UUID(self.client.get("/api/v1/me", headers=self.headers).json()["id"])
        self.send("LINK " + issue(self.client, self.headers).json()["code"])

    def incoming(self, body, reference=None):
        self.now[0] += timedelta(seconds=1)
        value = payload(self.now[0], body)
        if reference:
            value["entry"][0]["changes"][0]["value"]["messages"][0]["context"] = {"id": reference}
        assert send_webhook(self.identity, value).status_code == 200
        return value

    def send(self, body, reference=None):
        value = self.incoming(body, reference)
        assert process_one(self.service)
        assert deliver_one(self.service, self.provider)
        return value, "wamid.fake." + str(self.provider.messages[-1][0])

    def begin(self):
        _, menu = self.send("START")
        with Session(self.service.engine) as db:
            row = db.scalar(select(OutboundMessage).where(OutboundMessage.provider_id == menu))
            number = row.menu_topic_ids.index(self.plan["topic_id"]) + 1
        _, question = self.send(str(number), menu)
        return question


@pytest.mark.parametrize(
    "response_type,answer",
    [
        ("SINGLE_CHOICE", "1"),
        ("MULTIPLE_CHOICE", "1,2"),
        ("NUMERIC", "1.00 | m"),
    ],
)
def test_complete_five_question_signed_fake_flow(identity, content, response_type, answer, caplog):
    flow = Flow(identity, content, response_type)
    reference = flow.begin()
    for position in range(1, 6):
        assert f"Question {position}/5" in flow.provider.messages[-1][1]
        message, _ = flow.send(answer, reference)
        assert "Points:" in flow.provider.messages[-1][1]
        assert "/revise?session=" in flow.provider.messages[-1][1]
        assert send_webhook(identity, message).status_code == 200
        assert not process_one(flow.service)
        if position < 5:
            _, reference = flow.send("CONTINUE")
    assert "Five answers saved." in flow.provider.messages[-1][1]
    with Session(flow.service.engine) as db:
        attempts = list(db.scalars(select(Attempt)))
        assert len(attempts) == 5 and {a.channel for a in attempts} == {"WHATSAPP"}
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 5
        session = db.scalar(select(AssessmentSession))
        assert session.status == "COMPLETED"
        assert all(r.reply_encrypted is None for r in db.scalars(select(InboundMessage)))
        exported = project(flow.service, db, flow.actor, uuid4())
        assert len(exported.records["channel_conversations"]) == 1
        assert "expected_outbound_id" not in str(exported.records["channel_conversations"])
        counts = {row.source: row.count for row in inventory(db, flow.actor)}
        assert counts["conversation_states"] == 1
    assert all(len(body) <= 500 for _, body in flow.provider.messages)
    assert "SECRET" not in caplog.text and "1.00 | m" not in caplog.text
    assert "256700000001" not in caplog.text


def test_missing_stale_and_foreign_reply_context_cannot_grade(identity, content):
    flow = Flow(identity, content)
    first = flow.begin()
    foreign = payload(flow.now[0], "1", sender="256700000002")
    foreign["entry"][0]["changes"][0]["value"]["messages"][0]["context"] = {"id": first}
    assert send_webhook(identity, foreign).status_code == 200
    assert process_one(flow.service)
    assert deliver_one(flow.service, flow.provider)
    flow.send("1")
    flow.send("1", "wamid.fake." + str(uuid4()))
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
        assert all(r.reply_encrypted is None for r in db.scalars(select(InboundMessage)))
    flow.send("1", first)
    _, second = flow.send("CONTINUE")
    flow.send("2", first)
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
    flow.send("1", second)
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 2


def test_stop_barrier_blocks_already_queued_answer_and_clears_pointer(identity, content):
    flow = Flow(identity, content)
    reference = flow.begin()
    flow.incoming("1", reference)
    flow.incoming("STOP")
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(ConversationState)) == 0
    assert process_one(flow.service)
    assert process_one(flow.service)
    assert not deliver_one(flow.service, flow.provider)
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
        assert db.scalar(select(AssessmentSession)).status == "ACTIVE"
        assert all(r.reply_encrypted is None for r in db.scalars(select(InboundMessage)))


def test_consent_withdrawal_before_delivery_cancels_question(identity, content):
    flow = Flow(identity, content)
    flow.begin()
    flow.incoming("CONTINUE")
    assert process_one(flow.service)
    assert consent(flow.client, flow.headers, "WITHDRAW").status_code == 200
    assert deliver_one(flow.service, flow.provider)
    with Session(flow.service.engine) as db:
        row = db.scalar(select(OutboundMessage).where(OutboundMessage.status == "CANCELLED"))
        assert row.error_code == "CONSENT_REQUIRED"
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0


def test_grade_delivery_failure_rolls_back_and_retry_is_once(identity, content, monkeypatch):
    flow = Flow(identity, content)
    reference = flow.begin()
    original = AssessmentService.submit_in_transaction

    def failed(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("synthetic post-grade failure")

    monkeypatch.setattr(AssessmentService, "submit_in_transaction", failed)
    message = flow.incoming("1", reference)
    assert process_one(flow.service)
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 0
        row = db.scalar(select(InboundMessage).where(InboundMessage.status == "QUEUED"))
        assert row.attempts == 1 and row.reply_encrypted
    monkeypatch.setattr(AssessmentService, "submit_in_transaction", original)
    flow.now[0] += timedelta(seconds=61)
    assert process_one(flow.service)
    assert deliver_one(flow.service, flow.provider)
    assert send_webhook(identity, message).status_code == 200
    assert not process_one(flow.service)
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
        assert db.scalar(select(func.count()).select_from(MasteryEvidence)) == 1


def test_expiry_scrubs_queued_response_and_pointer_without_erasing_learning(identity, content):
    flow = Flow(identity, content)
    reference = flow.begin()
    flow.send("1", reference)
    _, reference = flow.send("CONTINUE")
    flow.incoming("1", reference)
    flow.now[0] += timedelta(hours=24)
    expire(flow.service)
    with Session(flow.service.engine) as db:
        assert db.scalar(select(func.count()).select_from(ConversationState)) == 0
        assert db.scalar(select(func.count()).select_from(Attempt)) == 1
        assert all(r.reply_encrypted is None for r in db.scalars(select(InboundMessage)))
        assert not list(db.scalars(select(InboundMessage).where(InboundMessage.status == "QUEUED")))


def test_retired_question_is_cancelled_before_delivery(identity, content):
    from tests.integration.test_content import mutate

    flow = Flow(identity, content)
    reference = flow.begin()
    flow.incoming("CONTINUE")
    assert process_one(flow.service)
    with Session(flow.service.engine) as db:
        outgoing = db.scalar(
            select(OutboundMessage).where(OutboundMessage.provider_id == reference)
        )
        from services.domain.assessment import SessionItem

        item = db.get(SessionItem, outgoing.session_item_id)
        version = next(v for v in flow.versions if v["id"] == str(item.item_version_id))
    retired = mutate(
        flow.client,
        f"item-versions/{version['id']}/retire",
        flow.actors["admin"],
        {
            "expected_revision": version["revision"],
            "reason": "Synthetic withdrawal before delivery",
        },
    )
    assert retired.status_code == 200, retired.text
    sent = len(flow.provider.messages)
    assert deliver_one(flow.service, flow.provider)
    assert len(flow.provider.messages) == sent
    with Session(flow.service.engine) as db:
        outgoing = db.scalar(select(OutboundMessage).where(OutboundMessage.status == "CANCELLED"))
        assert outgoing.error_code == "PRACTICE_UNAVAILABLE"
