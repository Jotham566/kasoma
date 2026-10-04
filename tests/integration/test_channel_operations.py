"""FR-OPS-002/004: real bounded transport cohorts and minimized authorized snapshots."""

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.channel_operations import channel_counts
from services.domain.messaging import InboundMessage, OutboundMessage
from services.health import Health
from tests.integration.test_whatsapp_practice import Flow

pytestmark = pytest.mark.integration


def incoming(at, status="PROCESSED"):
    return InboundMessage(
        id=uuid4(),
        message_hash=uuid4().hex,
        request_hash=uuid4().hex,
        request_id=uuid4(),
        sender_hash="synthetic-transport-cohort",
        sender_encrypted="synthetic" if status == "QUEUED" else None,
        command="HELP",
        provider_at=at,
        received_at=at,
        available_at=at,
        processed_at=None if status == "QUEUED" else at,
        status=status,
        attempts=0 if status == "QUEUED" else 3 if status == "FAILED" else 1,
    )


def outgoing(row, at, status):
    key = uuid4()
    return OutboundMessage(
        id=key,
        inbound_id=row.id,
        recipient_hash=row.sender_hash,
        recipient_encrypted="synthetic" if status == "PENDING" else None,
        template="HELP",
        status=status,
        provider_id=f"wamid.fake.{key}" if status == "SENT" else None,
        attempts=0 if status == "PENDING" else 3 if status == "FAILED" else 1,
        created_at=at,
        available_at=at,
        sent_at=at if status == "SENT" else None,
    )


def test_recent_cohort_boundaries_pending_age_and_empty_timing(identity):
    service, _, _, now = identity
    start = now[0] - timedelta(hours=24)
    with Session(service.engine) as db, db.begin():
        assert channel_counts(db, now[0]).feedback_dispatch.p95_ms is None
        rows = [
            incoming(start, "FAILED"),
            incoming(start - timedelta(microseconds=1), "FAILED"),
            incoming(now[0], "REJECTED"),
            incoming(now[0] + timedelta(seconds=1), "FAILED"),
            incoming(now[0] - timedelta(days=2), "QUEUED"),
        ]
        db.add_all(rows)
        db.flush()
        for at, status in [
            (start, "FAILED"),
            (start - timedelta(microseconds=1), "FAILED"),
            (now[0], "CANCELLED"),
            (now[0], "SENT"),
            (now[0] - timedelta(seconds=120), "PENDING"),
        ]:
            row = incoming(at)
            db.add(row)
            db.flush()
            db.add(outgoing(row, at, status))
        db.flush()
        result = channel_counts(db, now[0])
        assert result.failed_inbound_received_24h.value == 1
        assert result.rejected_inbound_received_24h.value == 1
        assert result.failed_outbound_created_24h.value == 1
        assert result.cancelled_outbound_created_24h.value == 1
        assert result.accepted_outbound_created_24h.value == 1
        assert result.queued_inbound.value == result.queued_outbound.value == 1
        assert result.oldest_pending_seconds == 172800
        assert result.feedback_dispatch.sample_size == 0 and result.feedback_dispatch.p95_ms is None


def test_latest_feedback_sample_cap_and_operator_projection(identity, content, monkeypatch):
    flow = Flow(identity, content)
    question = flow.begin()
    flow.send("1", question)
    flow.now[0] += timedelta(seconds=10)
    now = flow.now[0]
    with Session(flow.service.engine) as db, db.begin():
        original = db.scalar(
            select(OutboundMessage).where(OutboundMessage.template == "PRACTICE_FEEDBACK")
        )
        # Independent synthetic transport receipts reuse one already valid assessment reference.
        # No additional grades or learner evidence are fabricated for the timing sample.
        rows = []
        outgoing_rows = []
        for i in range(1001):
            sent = now - timedelta(milliseconds=i)
            duration = 99999 if i == 1000 else 1000
            row = incoming(sent - timedelta(milliseconds=duration))
            rows.append(row)
            record = outgoing(row, row.received_at, "SENT")
            record.sent_at = sent
            record.template = "PRACTICE_FEEDBACK"
            record.link_id, record.actor_id, record.link_revision = (
                original.link_id,
                original.actor_id,
                original.link_revision,
            )
            record.attempt_id, record.session_item_id = (
                original.attempt_id,
                original.session_item_id,
            )
            outgoing_rows.append(record)
        db.add_all(rows)
        db.flush()
        db.add_all(outgoing_rows)
        db.flush()
        timing = channel_counts(db, now).feedback_dispatch
        assert timing.sample_size == 1000 and timing.sample_capped and timing.p95_ms == 1000
    monkeypatch.setattr(
        "services.operations.dependency_health",
        lambda _: Health(status="ok", database="up", redis="up"),
    )
    monkeypatch.setattr("services.operations.heartbeat", lambda *args, **kwargs: "up")
    assert flow.client.get("/api/v1/admin/operations", headers=flow.headers).status_code == 403
    response = flow.client.get("/api/v1/admin/operations", headers=flow.actors["admin"])
    assert response.status_code == 200, response.text
    channel = response.json()["counts"]["channel"]
    assert channel["feedback_dispatch"] == {
        "sample_size": 1000,
        "sample_capped": True,
        "p95_ms": 1000,
        "measure": "LOCAL_FAKE_ACCEPTANCE",
    }
    for forbidden in [
        "256700000001",
        "wamid.",
        "actor_id",
        "reply_encrypted",
        "session_item_id",
        "Synthetic selector",
    ]:
        assert forbidden not in response.text


def test_dispatch_window_excludes_future_negative_and_non_feedback_samples(identity, content):
    flow = Flow(identity, content)
    question = flow.begin()
    flow.send("1", question)
    flow.now[0] += timedelta(seconds=1)
    now = flow.now[0]
    with Session(flow.service.engine) as db, db.begin():
        original = db.scalar(
            select(OutboundMessage).where(OutboundMessage.template == "PRACTICE_FEEDBACK")
        )
        for sent, duration, feedback in [
            (now, 250, True),
            (now - timedelta(hours=24, microseconds=1), 9999, True),
            (now + timedelta(seconds=1), 9999, True),
            (now, -100, True),
            (now, 9999, False),
        ]:
            row = incoming(sent - timedelta(milliseconds=duration))
            db.add(row)
            db.flush()
            record = outgoing(row, row.received_at, "SENT")
            record.sent_at = sent
            if feedback:
                record.template = "PRACTICE_FEEDBACK"
                record.link_id, record.actor_id, record.link_revision = (
                    original.link_id,
                    original.actor_id,
                    original.link_revision,
                )
                record.attempt_id, record.session_item_id = (
                    original.attempt_id,
                    original.session_item_id,
                )
            db.add(record)
        db.flush()
        timing = channel_counts(db, now).feedback_dispatch
        assert timing.sample_size == 2 and timing.p95_ms == 250 and not timing.sample_capped
