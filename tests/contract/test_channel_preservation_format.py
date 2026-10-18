"""Synthetic, socket-disabled ADR-057 format boundary and tampering regressions."""

import base64
import json
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr, ValidationError

from services.channel_preservation_format import (
    FORMAT,
    MAX_CIPHERTEXT_BYTES,
    MAX_PLAINTEXT_BYTES,
    ConversationEvidence,
    Envelope,
    LinkEvidence,
    PreservationCipher,
    PreservationFormatError,
    SnapshotBinding,
)


@pytest.fixture(params=["CHANNEL_LINK_SNAPSHOT", "CHANNEL_CONVERSATION_SNAPSHOT"])
def material(request, settings):
    at = datetime(2026, 10, 19, 0, 0, 0, 123456, tzinfo=UTC)
    binding = SnapshotBinding(
        snapshot_id=uuid4(),
        request_id=uuid4(),
        owner_id=uuid4(),
        source_kind=request.param,
        source_link_id=uuid4(),
        link_revision=3,
        source_version="a" * 64,
    )
    if request.param == "CHANNEL_LINK_SNAPSHOT":
        evidence = LinkEvidence(
            source_link_id=binding.source_link_id,
            revision=3,
            status="ACTIVE",
            linked_at=at,
            opted_out_at=None,
            updated_at=at,
        )
    else:
        evidence = ConversationEvidence(
            source_link_id=binding.source_link_id,
            link_revision=3,
            session_id=uuid4(),
            expected_outbound_id=uuid4(),
            updated_at=at,
            expires_at=at + timedelta(hours=24),
        )
    return PreservationCipher(settings.identity_encryption_key), binding, evidence


def test_round_trip_is_randomized_private_and_has_exact_allowlist(material, settings):
    cipher, binding, evidence = material
    first, second = cipher.seal(binding, evidence), cipher.seal(binding, evidence)
    assert first.get_secret_value() != second.get_secret_value()
    assert first.get_secret_value() not in repr(first)
    assert len(first.get_secret_value()) <= MAX_CIPHERTEXT_BYTES
    opened = cipher.open(binding, first)
    assert opened == Envelope(format=FORMAT, binding=binding, evidence=evidence)
    assert len(opened.model_dump_json().encode()) < MAX_PLAINTEXT_BYTES
    allowed = (
        {"source_link_id", "revision", "status", "linked_at", "opted_out_at", "updated_at"}
        if isinstance(evidence, LinkEvidence)
        else {
            "source_link_id",
            "link_revision",
            "session_id",
            "expected_outbound_id",
            "updated_at",
            "expires_at",
        }
    )
    assert set(opened.evidence.model_dump()) == allowed
    # The identity-purpose cipher cannot decrypt preserved evidence or vice versa.
    identity_cipher = Fernet(settings.identity_encryption_key.get_secret_value())
    with pytest.raises(InvalidToken):
        identity_cipher.decrypt(first.get_secret_value())
    assert_closed(cipher, binding, SecretStr(identity_cipher.encrypt(b"synthetic").decode()))
    for value in (binding, evidence, opened):
        assert repr(value) == f"{type(value).__name__}()"
        assert str(value) == ""
    for value in (binding.source_link_id, binding.owner_id, evidence.updated_at):
        assert str(value) not in first.get_secret_value()


def assert_closed(cipher, binding, token):
    with pytest.raises(PreservationFormatError) as caught:
        cipher.open(binding, token)
    assert str(caught.value) == "CHANNEL_PRESERVATION_INVALID"
    assert caught.value.__suppress_context__


@pytest.mark.parametrize(
    "field",
    [
        "snapshot_id",
        "request_id",
        "owner_id",
        "source_link_id",
        "link_revision",
        "source_kind",
        "source_version",
    ],
)
def test_every_binding_field_is_authenticated(material, field):
    cipher, binding, evidence = material
    changed = {
        "link_revision": 4,
        "source_version": "b" * 64,
        "source_kind": (
            "CHANNEL_CONVERSATION_SNAPSHOT"
            if binding.source_kind == "CHANNEL_LINK_SNAPSHOT"
            else "CHANNEL_LINK_SNAPSHOT"
        ),
    }.get(field, uuid4())
    assert_closed(
        cipher, binding.model_copy(update={field: changed}), cipher.seal(binding, evidence)
    )


def test_wrong_root_key_and_corruption_fail_closed(material):
    cipher, binding, evidence = material
    token = cipher.seal(binding, evidence).get_secret_value()
    other = PreservationCipher(SecretStr(base64.urlsafe_b64encode(b"x" * 32).decode()))
    assert_closed(other, binding, SecretStr(token))
    raw = bytearray(base64.urlsafe_b64decode(token))
    raw[-1] ^= 1
    assert_closed(cipher, binding, SecretStr(base64.urlsafe_b64encode(raw).decode()))


@pytest.mark.parametrize("raw", ["", "x", "💥", "a" * (MAX_CIPHERTEXT_BYTES + 1)])
def test_untrusted_ciphertext_bounds(material, raw):
    cipher, binding, _ = material
    assert_closed(cipher, binding, SecretStr(raw))


@pytest.mark.parametrize("field", ["source_link_id", "revision"])
def test_cannot_seal_wrong_source_or_revision(material, field):
    cipher, binding, evidence = material
    if field == "revision":
        field = "revision" if isinstance(evidence, LinkEvidence) else "link_revision"
    changed = evidence.model_copy(update={field: uuid4() if field == "source_link_id" else 4})
    with pytest.raises(PreservationFormatError, match="^CHANNEL_PRESERVATION_INVALID$"):
        cipher.seal(binding, changed)


@pytest.mark.parametrize(
    "field",
    [
        "sender_hash",
        "external_identifier_encrypted",
        "provider_id",
        "code_hash",
        "reply_encrypted",
        "answer",
        "prompt",
        "token",
        "contact",
    ],
)
def test_forbidden_payload_fields_are_rejected_not_silently_dropped(material, field):
    _, _, evidence = material
    with pytest.raises(ValidationError) as caught:
        type(evidence).model_validate({**dict(evidence), field: "synthetic-restricted"})
    assert "synthetic-restricted" not in str(caught.value)


@pytest.mark.parametrize("revision", [0, -1, True, "3", 2_147_483_648])
def test_revisions_are_strict_database_sized_integers(material, revision):
    cipher, binding, evidence = material
    with pytest.raises(PreservationFormatError, match="^CHANNEL_PRESERVATION_INVALID$"):
        cipher.seal(binding.model_copy(update={"link_revision": revision}), evidence)


def test_naive_timestamps_and_invalid_instance_copies_are_revalidated(material):
    cipher, binding, evidence = material
    for value in (datetime(2026, 10, 19), "not-a-date"):
        bad = evidence.model_copy(update={"updated_at": value})
        with pytest.raises(PreservationFormatError, match="^CHANNEL_PRESERVATION_INVALID$"):
            cipher.seal(binding, bad)
    with pytest.raises(ValidationError):
        evidence.updated_at = datetime.now(UTC)


def test_utc_canonicalization_is_stable_and_preserves_microseconds(material):
    cipher, binding, evidence = material
    zone = timezone(timedelta(hours=3))
    shifted = evidence.model_copy(update={"updated_at": evidence.updated_at.astimezone(zone)})
    opened = cipher.open(binding, cipher.seal(binding, shifted))
    assert opened.evidence.updated_at == evidence.updated_at
    assert opened.evidence.updated_at.microsecond == 123456
    raw = opened.model_dump_json()
    assert "123456+00:00" in raw and "+03:00" not in raw


@pytest.mark.parametrize(
    "change",
    [
        "format",
        "extra-envelope",
        "extra-evidence",
        "wrong-kind",
        "duplicate",
        "whitespace",
        "oversize",
        "missing",
    ],
)
def test_authenticated_but_invalid_envelope_is_not_accepted(material, change):
    cipher, binding, evidence = material
    body = Envelope(format=FORMAT, binding=binding, evidence=evidence).model_dump(mode="json")
    if change == "format":
        body["format"] = "another-purpose-v1"
    elif change == "extra-envelope":
        body["contact"] = "synthetic-restricted"
    elif change == "extra-evidence":
        body["evidence"]["contact"] = "synthetic-restricted"
    elif change == "wrong-kind":
        body["binding"]["source_kind"] = (
            "CHANNEL_LINK_SNAPSHOT"
            if isinstance(evidence, ConversationEvidence)
            else "CHANNEL_CONVERSATION_SNAPSHOT"
        )
    elif change == "missing":
        del body["evidence"]["updated_at"]
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    if change == "duplicate":
        raw = raw.replace(b'"format":', b'"format":"ignored", "format":')
    elif change == "whitespace":
        raw = b" " + raw
    elif change == "oversize":
        raw += b" " * MAX_PLAINTEXT_BYTES
    # Deliberately forge authenticated ciphertext as a faulty internal producer.
    token = SecretStr(cipher._cipher(binding).encrypt(raw).decode())
    assert_closed(cipher, binding, token)


@pytest.mark.parametrize("raw", ["", "not-a-key", "💥", base64.urlsafe_b64encode(b"x").decode()])
def test_invalid_key_diagnostics_are_closed(raw):
    with pytest.raises(PreservationFormatError) as caught:
        PreservationCipher(SecretStr(raw))
    assert str(caught.value) == "CHANNEL_PRESERVATION_KEY_INVALID"
    assert caught.value.__suppress_context__
