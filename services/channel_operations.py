"""Bounded channel queue truth and local fake-dispatch timing, without record identifiers."""

from datetime import datetime, timedelta
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from services.domain.messaging import InboundMessage, OutboundMessage
from services.operations_contracts import ChannelCounts, DispatchTiming


def dispatch_timing(durations_ms: list[float]) -> DispatchTiming:
    selected = sorted(durations_ms[:1000])
    return DispatchTiming(
        sample_size=len(selected),
        sample_capped=len(durations_ms) > 1000,
        p95_ms=ceil(selected[ceil(len(selected) * 0.95) - 1]) if selected else None,
    )


def channel_counts(db: Session, now: datetime) -> ChannelCounts:
    from services.operations import bounded_count

    start = now - timedelta(hours=24)
    incoming = select(1).select_from(InboundMessage)
    outgoing = select(1).select_from(OutboundMessage)
    incoming_recent = incoming.where(
        InboundMessage.received_at >= start, InboundMessage.received_at <= now
    )
    outgoing_recent = outgoing.where(
        OutboundMessage.created_at >= start, OutboundMessage.created_at <= now
    )
    oldest_incoming = db.scalar(
        select(func.min(InboundMessage.received_at)).where(InboundMessage.status == "QUEUED")
    )
    oldest_outgoing = db.scalar(
        select(func.min(OutboundMessage.created_at)).where(OutboundMessage.status == "PENDING")
    )
    ages = [
        max(0, int((now - at).total_seconds())) for at in [oldest_incoming, oldest_outgoing] if at
    ]
    timings = list(
        db.execute(
            select(InboundMessage.received_at, OutboundMessage.sent_at)
            .join(OutboundMessage, OutboundMessage.inbound_id == InboundMessage.id)
            .where(
                OutboundMessage.template == "PRACTICE_FEEDBACK",
                OutboundMessage.sent_at >= start,
                OutboundMessage.sent_at <= now,
                OutboundMessage.sent_at >= InboundMessage.received_at,
            )
            .order_by(OutboundMessage.sent_at.desc(), OutboundMessage.id)
            .limit(1001)
        )
    )
    return ChannelCounts(
        queued_inbound=bounded_count(db, incoming.where(InboundMessage.status == "QUEUED")),
        queued_outbound=bounded_count(db, outgoing.where(OutboundMessage.status == "PENDING")),
        oldest_pending_seconds=max(ages, default=0),
        failed_inbound_received_24h=bounded_count(
            db, incoming_recent.where(InboundMessage.status == "FAILED")
        ),
        rejected_inbound_received_24h=bounded_count(
            db, incoming_recent.where(InboundMessage.status == "REJECTED")
        ),
        failed_outbound_created_24h=bounded_count(
            db, outgoing_recent.where(OutboundMessage.status == "FAILED")
        ),
        cancelled_outbound_created_24h=bounded_count(
            db, outgoing_recent.where(OutboundMessage.status == "CANCELLED")
        ),
        accepted_outbound_created_24h=bounded_count(
            db, outgoing_recent.where(OutboundMessage.sent_at.is_not(None))
        ),
        feedback_dispatch=dispatch_timing(
            [(sent - received).total_seconds() * 1000 for received, sent in timings]
        ),
    )
