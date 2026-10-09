"""NFR-SEC-002: real local authenticated encryption, synthetic answers, no network."""

import json
from uuid import UUID

import pytest
from cryptography.fernet import Fernet

from services.short_text_answers import (
    MAX_CIPHERTEXT_BYTES,
    MAX_ENVELOPE_BYTES,
    AnswerBinding,
    AnswerProtectionError,
    protect_answer,
    reveal_answer,
)
from services.short_text_contracts import ShortTextResponse


class LocalCipher:
    def __init__(self):
        self.cipher = Fernet(Fernet.generate_key())
        self.decryptions = 0

    def encrypt(self, raw):
        return self.cipher.encrypt(raw.encode()).decode()

    def decrypt(self, token):
        self.decryptions += 1
        return self.cipher.decrypt(token.encode()).decode()


@pytest.fixture
def binding():
    return AnswerBinding(
        learner_id=UUID(int=401),
        attempt_id=UUID(int=402),
        session_item_id=UUID(int=403),
        item_version_id=UUID(int=404),
        rubric_version_id=UUID(int=404),
    )


@pytest.mark.parametrize(
    "answer", ["  synthetic answer\n", "Δ" * 2000, "🌍" * 2000, "\x00" * 1999 + "x"]
)
def test_exact_unicode_and_escaped_text_round_trip_within_byte_bounds(binding, answer):
    cipher = LocalCipher()
    response = ShortTextResponse(type="SHORT_TEXT", text=answer)
    token = protect_answer(response, binding, cipher)
    assert answer not in token
    assert str(binding.learner_id) not in token
    assert len(token) <= MAX_CIPHERTEXT_BYTES
    assert len(cipher.decrypt(token).encode()) <= MAX_ENVELOPE_BYTES
    assert reveal_answer(token, binding, cipher) == response


@pytest.mark.parametrize(
    "field", ["learner_id", "attempt_id", "session_item_id", "item_version_id"]
)
def test_ciphertext_cannot_be_replayed_under_a_different_binding(binding, field):
    cipher = LocalCipher()
    token = protect_answer(ShortTextResponse(type="SHORT_TEXT", text="synthetic"), binding, cipher)
    values = binding.model_dump() | {field: UUID(int=405)}
    if field == "item_version_id":
        values["rubric_version_id"] = values[field]
    with pytest.raises(AnswerProtectionError, match="READ_FAILED"):
        reveal_answer(token, AnswerBinding(**values), cipher)


def test_wrong_key_and_tampered_ciphertext_are_closed_errors(binding):
    cipher = LocalCipher()
    token = protect_answer(
        ShortTextResponse(type="SHORT_TEXT", text="synthetic private"), binding, cipher
    )
    for value, reader in [(token, LocalCipher()), (token[:-8] + "AAAAAAAA", cipher)]:
        with pytest.raises(AnswerProtectionError) as error:
            reveal_answer(value, binding, reader)
        assert str(error.value) == "SHORT_TEXT_ANSWER_READ_FAILED"
        assert error.value.__suppress_context__


@pytest.mark.parametrize("token", ["", "x" * (MAX_CIPHERTEXT_BYTES + 1), "π", None, b"bytes"])
def test_oversized_or_invalid_ciphertext_is_rejected_before_decryption(binding, token):
    cipher = LocalCipher()
    with pytest.raises(AnswerProtectionError):
        reveal_answer(token, binding, cipher)
    assert cipher.decryptions == 0


@pytest.mark.parametrize("change", ["format", "extra", "blank", "duplicate", "oversized", "rubric"])
def test_authenticated_but_invalid_envelopes_are_rejected(binding, change):
    cipher = LocalCipher()
    token = protect_answer(ShortTextResponse(type="SHORT_TEXT", text="synthetic"), binding, cipher)
    raw = cipher.decrypt(token)
    data = json.loads(raw)
    if change == "format":
        data["format"] = "another-encrypted-domain"
    elif change == "extra":
        data["provider_output"] = "hidden"
    elif change == "blank":
        data["response"]["text"] = " "
    elif change == "rubric":
        data["binding"]["rubric_version_id"] = str(UUID(int=499))
    if change == "duplicate":
        raw = raw.replace('"text":"synthetic"', '"text":"ignored","text":"synthetic"')
    elif change == "oversized":
        raw = "x" * (MAX_ENVELOPE_BYTES + 1)
    else:
        raw = json.dumps(data)
    with pytest.raises(AnswerProtectionError):
        reveal_answer(cipher.encrypt(raw), binding, cipher)


def test_mutated_response_is_revalidated_before_encryption(binding):
    response = ShortTextResponse(type="SHORT_TEXT", text="synthetic")
    response.text = "x" * 2001

    class NeverEncrypt:
        def encrypt(self, value):
            pytest.fail("Invalid input must not reach cipher")

    with pytest.raises(AnswerProtectionError, match="WRITE_FAILED"):
        protect_answer(response, binding, NeverEncrypt())


def test_adapter_failures_never_expose_private_diagnostics(binding):
    class BrokenCipher:
        def encrypt(self, value):
            raise RuntimeError("synthetic private plaintext")

        def decrypt(self, value):
            raise RuntimeError("synthetic secret key")

    with pytest.raises(AnswerProtectionError) as error:
        protect_answer(
            ShortTextResponse(type="SHORT_TEXT", text="synthetic"), binding, BrokenCipher()
        )
    assert str(error.value) == "SHORT_TEXT_ANSWER_WRITE_FAILED"
    assert error.value.__suppress_context__
    with pytest.raises(AnswerProtectionError) as error:
        reveal_answer("synthetic-token", binding, BrokenCipher())
    assert str(error.value) == "SHORT_TEXT_ANSWER_READ_FAILED"
    assert error.value.__suppress_context__


@pytest.mark.parametrize("output", [None, b"bytes", "π", "x" * (MAX_CIPHERTEXT_BYTES + 1)])
def test_invalid_cipher_output_cannot_be_published(binding, output):
    class InvalidCipher:
        def encrypt(self, value):
            return output

    with pytest.raises(AnswerProtectionError, match="WRITE_FAILED"):
        protect_answer(
            ShortTextResponse(type="SHORT_TEXT", text="synthetic"), binding, InvalidCipher()
        )


@pytest.mark.parametrize("output", [None, b"bytes", "x" * (MAX_ENVELOPE_BYTES + 1), "🌍" * 5000])
def test_invalid_plaintext_is_bounded_before_parsing(binding, output):
    class InvalidCipher:
        def decrypt(self, value):
            return output

    with pytest.raises(AnswerProtectionError, match="READ_FAILED"):
        reveal_answer("synthetic-token", binding, InvalidCipher())


def test_bypassed_rubric_binding_is_revalidated_before_cipher_access(binding):
    invalid = binding.model_copy(update={"rubric_version_id": UUID(int=499)})

    class NeverCipher:
        def encrypt(self, value):
            pytest.fail("Invalid rubric must not reach encryption")

        def decrypt(self, value):
            pytest.fail("Invalid rubric must not reach decryption")

    with pytest.raises(AnswerProtectionError, match="WRITE_FAILED"):
        protect_answer(
            ShortTextResponse(type="SHORT_TEXT", text="synthetic"), invalid, NeverCipher()
        )
    with pytest.raises(AnswerProtectionError, match="READ_FAILED"):
        reveal_answer("synthetic-token", invalid, NeverCipher())
