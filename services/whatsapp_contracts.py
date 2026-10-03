"""Owned linking responses; no sender identifiers or provider payloads exposed."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from services.identity_contracts import Contract


class LinkCodeView(Contract):
    id: UUID
    code: str = Field(pattern=r"^[A-F0-9]{12}$")
    expires_at: datetime
    synthetic: Literal[True] = True


class ChannelLinkView(Contract):
    link_id: UUID | None
    status: Literal["NOT_LINKED", "ACTIVE", "STOPPED", "UNLINKED"]
    revision: int = Field(ge=0)
    linked_at: datetime | None
    opted_out_at: datetime | None
    outbound_enabled: bool
    synthetic: Literal[True] = True


class WebhookAccepted(Contract):
    accepted: Literal[True] = True


class UnlinkInput(Contract):
    expected_link_id: UUID | None
    expected_revision: int = Field(ge=0, le=2147483647)
