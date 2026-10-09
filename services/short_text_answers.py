"""Bounded authenticated short-text answer envelopes; no persistence enablement yet."""

from typing import Final, Literal, Protocol
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator

from services.short_text_contracts import ShortTextResponse
from services.short_text_validation import StrictContract

FORMAT: Final = "kasoma-short-text-answer-v1"
MAX_ENVELOPE_BYTES: Final = 16384
MAX_CIPHERTEXT_BYTES: Final = 24576


class AnswerCipher(Protocol):
    """Implemented by the existing authenticated IdentityService encryption boundary."""

    def encrypt(self, value: str) -> str: ...

    def decrypt(self, value: str) -> str: ...


class AnswerProtectionError(RuntimeError):
    """Closed error: never expose ciphertext, plaintext or adapter diagnostics."""


class AnswerBinding(StrictContract):
    model_config = ConfigDict(frozen=True)
    learner_id: UUID
    attempt_id: UUID
    session_item_id: UUID
    item_version_id: UUID
    rubric_version_id: UUID

    @model_validator(mode="after")
    def pinned_rubric(self) -> "AnswerBinding":
        # ADR-044: the immutable rubric ID equals its owning item-version ID.
        if self.rubric_version_id != self.item_version_id:
            raise ValueError("Rubric must match the pinned item version")
        return self


class AnswerEnvelope(StrictContract):
    format: Literal["kasoma-short-text-answer-v1"]
    binding: AnswerBinding = Field(repr=False)
    response: ShortTextResponse = Field(repr=False)


def bounded_ciphertext(value: str) -> bool:
    return type(value) is str and 0 < len(value) <= MAX_CIPHERTEXT_BYTES and value.isascii()


def protect_answer(
    response: ShortTextResponse, binding: AnswerBinding, cipher: AnswerCipher
) -> str:
    """Encrypt exact response plus binding; caller must separately authorize ownership."""
    try:
        # Revalidate even instances: a caller may have bypassed/mutated Pydantic construction.
        envelope = AnswerEnvelope(
            format=FORMAT,
            binding=AnswerBinding.model_validate(binding.model_dump()),
            response=ShortTextResponse.model_validate(response.model_dump()),
        )
        raw = envelope.model_dump_json()
        if len(raw.encode("utf-8")) > MAX_ENVELOPE_BYTES:
            raise ValueError("Envelope exceeds byte limit")
        ciphertext = cipher.encrypt(raw)
        if not bounded_ciphertext(ciphertext):
            raise ValueError("Ciphertext exceeds bounds")
        return ciphertext
    except Exception:
        raise AnswerProtectionError("SHORT_TEXT_ANSWER_WRITE_FAILED") from None


def reveal_answer(
    ciphertext: str, binding: AnswerBinding, cipher: AnswerCipher
) -> ShortTextResponse:
    """Authenticate and bind before exposing text; never authorizes access by itself."""
    try:
        expected = AnswerBinding.model_validate(binding.model_dump())
        if not bounded_ciphertext(ciphertext):
            raise ValueError("Ciphertext exceeds bounds")
        raw = cipher.decrypt(ciphertext)
        if (
            type(raw) is not str
            or len(raw) > MAX_ENVELOPE_BYTES
            or len(raw.encode("utf-8")) > MAX_ENVELOPE_BYTES
        ):
            raise ValueError("Envelope exceeds byte limit")
        envelope = AnswerEnvelope.model_validate_json(raw)
        if envelope.binding != expected or envelope.model_dump_json() != raw:
            raise ValueError("Answer binding or canonical envelope mismatch")
        return envelope.response
    except Exception:
        raise AnswerProtectionError("SHORT_TEXT_ANSWER_READ_FAILED") from None
