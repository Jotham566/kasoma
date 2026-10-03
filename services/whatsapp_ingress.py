"""WhatsApp signature boundary. No provider calls, persistence or learner actions."""

import hashlib
import hmac
import json
import re
from typing import Any

MAX_WEBHOOK_BYTES = 65536


class WebhookRejected(Exception):
    """Safe codes only; never retain payloads, credentials or parser exception text."""

    def __init__(self, code: str, status: int):
        super().__init__(code)
        self.code = code
        self.status = status


def unique_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON number")


def authenticate_and_decode(raw: bytes, signature: str | None, app_secret: bytes) -> dict[str, Any]:
    if not raw or len(raw) > MAX_WEBHOOK_BYTES:
        raise WebhookRejected("WEBHOOK_SIZE_INVALID", 413)
    if len(app_secret) < 32:
        raise WebhookRejected("WEBHOOK_UNAVAILABLE", 503)
    if signature is None or re.fullmatch(r"sha256=[0-9a-f]{64}", signature) is None:
        raise WebhookRejected("WEBHOOK_SIGNATURE_INVALID", 401)
    expected = "sha256=" + hmac.new(app_secret, raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise WebhookRejected("WEBHOOK_SIGNATURE_INVALID", 401)
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_fields, parse_constant=reject_constant
        )
        if not isinstance(value, dict):
            raise ValueError("Object required")
    except (ValueError, UnicodeError, RecursionError):
        raise WebhookRejected("WEBHOOK_JSON_INVALID", 400) from None
    return value
