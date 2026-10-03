"""FR-WA-004/NFR-SEC-002: verify exact bytes before parsing untrusted JSON."""

import hashlib
import hmac

import pytest

from services.whatsapp_ingress import MAX_WEBHOOK_BYTES, WebhookRejected, authenticate_and_decode

# Synthetic public fixture only; never used by application configuration.
KEY = b"synthetic-whatsapp-fixture-key-0001"


def sign(raw: bytes) -> str:
    return "sha256=" + hmac.new(KEY, raw, hashlib.sha256).hexdigest()


def test_signed_whatsapp_json_uses_exact_bytes():
    raw = b'{"object":"whatsapp_business_account", "entry":[]}'
    assert authenticate_and_decode(raw, sign(raw), KEY)["entry"] == []
    with pytest.raises(WebhookRejected, match="WEBHOOK_SIGNATURE_INVALID"):
        authenticate_and_decode(raw.replace(b", ", b","), sign(raw), KEY)
    with pytest.raises(WebhookRejected, match="WEBHOOK_SIGNATURE_INVALID"):
        authenticate_and_decode(raw, sign(raw), b"different-synthetic-fixture-key-0001")


@pytest.mark.parametrize("signature", [None, "", "sha1=abcd", "sha256=" + "0" * 64])
def test_bad_signature_never_reaches_json_parser(monkeypatch, signature):
    def forbidden(*args, **kwargs):
        pytest.fail("Unverified input reached the parser")

    monkeypatch.setattr("services.whatsapp_ingress.json.loads", forbidden)
    with pytest.raises(WebhookRejected) as result:
        authenticate_and_decode(b"private malformed input", signature, KEY)
    assert result.value.status == 401
    assert "private" not in str(result.value)


@pytest.mark.parametrize(
    "raw", [b"[]", b"null", b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b"\xff", b"{"]
)
def test_verified_invalid_json_is_rejected_without_echo(raw):
    with pytest.raises(WebhookRejected, match="WEBHOOK_JSON_INVALID") as result:
        authenticate_and_decode(raw, sign(raw), KEY)
    assert result.value.status == 400


def test_webhook_size_and_missing_secret_fail_closed():
    raw = b'{"padding":"' + b"a" * (MAX_WEBHOOK_BYTES - 14) + b'"}'
    assert len(raw) == MAX_WEBHOOK_BYTES
    assert authenticate_and_decode(raw, sign(raw), KEY)["padding"]
    for body in [b"", raw + b" "]:
        with pytest.raises(WebhookRejected) as result:
            authenticate_and_decode(body, sign(body), KEY)
        assert result.value.status == 413
    with pytest.raises(WebhookRejected) as result:
        authenticate_and_decode(raw, sign(raw), b"")
    assert result.value.status == 503


@pytest.mark.parametrize(
    "field,value",
    [
        ("whatsapp_outbound_per_minute", 0),
        ("whatsapp_outbound_per_minute", 61),
        ("whatsapp_link_attempts_per_minute", 0),
        ("whatsapp_link_attempts_per_minute", 21),
        ("whatsapp_provider", "meta"),
        ("whatsapp_phone_number_id", "real-phone"),
    ],
)
def test_channel_configuration_fails_closed(field, value):
    from pydantic import ValidationError

    from services.config import Settings

    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_local_messaging_worker_schedule_and_safe_template_lengths():
    from apps.worker.main import make_worker
    from services.config import Settings
    from services.whatsapp_delivery import TEMPLATES

    app = make_worker(Settings())
    try:
        assert app.conf.beat_schedule["channel-messages"] == {
            "task": "kasoma.channel_messages",
            "schedule": 10.0,
            "options": {"queue": "messaging"},
        }
        assert "kasoma.channel_messages" in app.tasks
        assert all(len(value) <= 500 for value in TEMPLATES.values())
    finally:
        app.close()
