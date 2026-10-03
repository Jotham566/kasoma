"""Bounded messaging queue drain using local fake transport only."""

from uuid import uuid4

from services.identity import IdentityService
from services.observability import emit
from services.whatsapp_delivery import FakeChannelDelivery, deliver_one
from services.whatsapp_processing import process_one
from services.whatsapp_retention import expire


def process_messages(identity: IdentityService) -> int:
    expire(identity)
    incoming = sum(1 for _ in range(5) if process_one(identity))
    outgoing = sum(1 for _ in range(5) if deliver_one(identity, FakeChannelDelivery()))
    emit("channel.batch_processed", str(uuid4()), "WORKER", 200)
    return incoming + outgoing
