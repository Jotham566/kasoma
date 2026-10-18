"""ADR-057 private evidence format. No capture, authorization, storage or delivery.

Callers must authorize and lock/revalidate the exact owned source before sealing.
Neither a binding nor ciphertext confers permission to read or resume a conversation.
"""

import base64
import json
from datetime import UTC, datetime
from typing import Annotated, Final, Literal, Self
from uuid import UUID

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_serializer,
    model_validator,
)

FORMAT: Final = "kasoma-channel-preservation-v1"
MAX_PLAINTEXT_BYTES: Final = 2048
MAX_CIPHERTEXT_BYTES: Final = 4096
Revision = Annotated[int, Field(ge=1, le=2_147_483_647)]


class PreservationFormatError(RuntimeError):
    """Closed failure; never render a payload, key, source ID or validation details."""


class PrivateValue(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
        hide_input_in_errors=True,
        revalidate_instances="always",
    )

    def __repr_args__(self) -> tuple[()]:
        # Internal identifiers and timestamps are confidential too.
        return ()


class LinkEvidence(PrivateValue):
    source_link_id: UUID
    revision: Revision
    status: Literal["ACTIVE", "STOPPED", "UNLINKED"]
    linked_at: AwareDatetime
    opted_out_at: AwareDatetime | None
    updated_at: AwareDatetime

    @field_serializer("linked_at", "opted_out_at", "updated_at")
    def utc(self, value: datetime | None) -> str | None:
        return value.astimezone(UTC).isoformat(timespec="microseconds") if value else None


class ConversationEvidence(PrivateValue):
    source_link_id: UUID
    link_revision: Revision
    session_id: UUID | None
    expected_outbound_id: UUID | None
    updated_at: AwareDatetime
    expires_at: AwareDatetime

    @field_serializer("updated_at", "expires_at")
    def utc(self, value: datetime) -> str:
        return value.astimezone(UTC).isoformat(timespec="microseconds")


class SnapshotBinding(PrivateValue):
    """Capture metadata, supplied by the future authorized transaction, not a token."""

    snapshot_id: UUID
    request_id: UUID
    owner_id: UUID
    source_kind: Literal["CHANNEL_LINK_SNAPSHOT", "CHANNEL_CONVERSATION_SNAPSHOT"]
    source_link_id: UUID
    link_revision: Revision
    source_version: str = Field(pattern=r"^[a-f0-9]{64}$")


class Envelope(PrivateValue):
    format: Literal["kasoma-channel-preservation-v1"]
    binding: SnapshotBinding
    evidence: LinkEvidence | ConversationEvidence

    @model_validator(mode="after")
    def bound(self) -> Self:
        link = self.binding.source_kind == "CHANNEL_LINK_SNAPSHOT"
        if link != isinstance(self.evidence, LinkEvidence):
            raise ValueError("Invalid evidence binding")
        revision = (
            self.evidence.revision
            if isinstance(self.evidence, LinkEvidence)
            else self.evidence.link_revision
        )
        if (
            self.evidence.source_link_id != self.binding.source_link_id
            or revision != self.binding.link_revision
        ):
            raise ValueError("Invalid evidence binding")
        return self


def _canonical(value: PrivateValue) -> bytes:
    return json.dumps(
        value.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


class PreservationCipher:
    """Existing Fernet primitive, independently derived for purpose and exact binding.

    No TTL here: a future database transaction must enforce finite active decisions,
    including release/expiry and disposal. Fernet timestamps are not legal-hold clocks.
    """

    def __init__(self, encryption_key: SecretStr):
        # Validate using the same primitive as identity, without printing the key.
        try:
            encoded = encryption_key.get_secret_value().encode("ascii")
            Fernet(encoded)
            self._key = base64.urlsafe_b64decode(encoded)
        except (ValueError, TypeError, UnicodeError):
            raise PreservationFormatError("CHANNEL_PRESERVATION_KEY_INVALID") from None

    def _cipher(self, binding: SnapshotBinding) -> Fernet:
        key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=FORMAT.encode("ascii") + b"\x00" + _canonical(binding),
        ).derive(self._key)
        return Fernet(base64.urlsafe_b64encode(key))

    def seal(
        self, binding: SnapshotBinding, evidence: LinkEvidence | ConversationEvidence
    ) -> SecretStr:
        try:
            envelope = Envelope(format=FORMAT, binding=binding, evidence=evidence)
            raw = _canonical(envelope)
            if not 0 < len(raw) <= MAX_PLAINTEXT_BYTES:
                raise ValueError("Evidence size")
            ciphertext = self._cipher(binding).encrypt(raw)
            if len(ciphertext) > MAX_CIPHERTEXT_BYTES:
                raise ValueError("Evidence size")
            return SecretStr(ciphertext.decode("ascii"))
        except Exception:
            raise PreservationFormatError("CHANNEL_PRESERVATION_INVALID") from None

    def open(self, binding: SnapshotBinding, ciphertext: SecretStr) -> Envelope:
        """Internal integrity/recovery primitive; never an application read endpoint."""
        try:
            token = ciphertext.get_secret_value()
            if not 0 < len(token) <= MAX_CIPHERTEXT_BYTES:
                raise ValueError("Evidence size")
            raw = self._cipher(binding).decrypt(token.encode("ascii"))
            if not 0 < len(raw) <= MAX_PLAINTEXT_BYTES:
                raise ValueError("Evidence size")
            envelope = Envelope.model_validate_json(raw)
            if envelope.binding != binding or raw != _canonical(envelope):
                raise ValueError("Evidence binding")
            return envelope
        except Exception:
            raise PreservationFormatError("CHANNEL_PRESERVATION_INVALID") from None
