"""FR-WA-002: advancing clocks must still satisfy the exact 24-hour SQL invariant."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from services import whatsapp_practice as practice
from services.domain.messaging import ChannelLink, ConversationState


@pytest.mark.parametrize("operation", ["new", "update"])
def test_conversation_expiry_uses_the_same_instant_as_updated_at(monkeypatch, operation):
    start = datetime(2026, 10, 19, tzinfo=UTC)
    ticks = iter(start + timedelta(microseconds=n) for n in range(20))
    identity = SimpleNamespace(clock=lambda: next(ticks))
    link = ChannelLink(id=uuid4(), user_id=uuid4(), revision=1)
    db = SimpleNamespace(get=lambda *args: None, add=lambda row: None)
    if operation == "new":
        state = practice.state_for(identity, db, link)
    else:
        state = ConversationState(
            link_id=link.id,
            actor_id=link.user_id,
            link_revision=1,
            updated_at=start - timedelta(hours=1),
            expires_at=start + timedelta(hours=23),
        )
        monkeypatch.setattr(practice, "state_for", lambda *args: state)
        monkeypatch.setattr(
            practice,
            "AssessmentService",
            lambda *args: SimpleNamespace(authorize_actor=lambda *args: None),
        )
        monkeypatch.setattr(practice, "queue", lambda *args: None)
        practice.process(identity, db, SimpleNamespace(command="PROGRESS"), link)
    assert state.expires_at == state.updated_at + timedelta(hours=24)
