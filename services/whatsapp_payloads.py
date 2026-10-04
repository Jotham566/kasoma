"""Normalize authenticated Meta-shaped fixtures without retaining free text or contact names."""

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from services.identity import IdentityService
from services.whatsapp_ingress import WebhookRejected
from services.whatsapp_linking import code_hash


@dataclass(frozen=True)
class Incoming:
    message_hash: str
    request_hash: str
    sender_hash: str
    sender_encrypted: str
    command: str
    code_hash: str | None
    status_reference: str | None
    delivery_status: str | None
    provider_at: datetime
    reply_reference: str | None = None
    reply_encrypted: str | None = None


def sequence(value: Any) -> list[Any]:
    if not isinstance(value, list) or not 1 <= len(value) <= 20:
        raise ValueError("Invalid batch")
    return value


def object_value(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Invalid object")
    return value


def string(value: Any, maximum: int) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise ValueError("Invalid field")
    return value


def normalize_payload(identity: IdentityService, payload: dict[str, Any]) -> list[Incoming]:
    try:
        return parse(identity, payload)
    except (ValueError, TypeError, OverflowError, OSError):
        raise WebhookRejected("WEBHOOK_PAYLOAD_INVALID", 400) from None


def parse(identity: IdentityService, payload: dict[str, Any]) -> list[Incoming]:
    settings = identity.settings
    if payload.get("object") != "whatsapp_business_account":
        raise ValueError("Invalid object")
    results: list[Incoming] = []
    for entry_raw in sequence(payload.get("entry")):
        entry = object_value(entry_raw)
        if entry.get("id") != settings.whatsapp_business_id:
            raise ValueError("Invalid business")
        for change_raw in sequence(entry.get("changes")):
            change = object_value(change_raw)
            value = object_value(change.get("value"))
            if (
                change.get("field") != "messages"
                or value.get("messaging_product") != "whatsapp"
                or object_value(value.get("metadata")).get("phone_number_id")
                != settings.whatsapp_phone_number_id
            ):
                raise ValueError("Invalid destination")
            if ("messages" in value) == ("statuses" in value):
                raise ValueError("Ambiguous batch")
            statuses = "statuses" in value
            for raw in sequence(value.get("statuses" if statuses else "messages")):
                if len(results) >= 20:
                    raise ValueError("Batch limit")
                message = object_value(raw)
                provider_id = string(message.get("id"), 256)
                if re.fullmatch(r"wamid\.[A-Za-z0-9_.=+/-]{1,240}", provider_id) is None:
                    raise ValueError("Invalid provider message ID")
                sender = string(message.get("recipient_id" if statuses else "from"), 15)
                if re.fullmatch(r"[1-9][0-9]{7,14}", sender) is None:
                    raise ValueError("Invalid sender")
                stamp = string(message.get("timestamp"), 12)
                if re.fullmatch(r"[0-9]{1,12}", stamp) is None:
                    raise ValueError("Invalid timestamp")
                at = datetime.fromtimestamp(int(stamp), UTC)
                now = identity.clock()
                if at <= now - timedelta(days=30) or at > now + timedelta(minutes=5):
                    raise ValueError("Expired or future event")
                command, hashed_code, delivery, reference = "UNSUPPORTED", None, None, None
                reply_reference, reply_encrypted = None, None
                event_key = f"message:{provider_id}"
                if statuses:
                    delivery = string(message.get("status"), 16).upper()
                    if delivery not in {"SENT", "DELIVERED", "READ", "FAILED"}:
                        raise ValueError("Invalid status")
                    command, reference = "STATUS", provider_id
                    event_key = f"status:{provider_id}:{delivery}:{stamp}"
                elif message.get("type") == "text":
                    body = string(object_value(message.get("text")).get("body"), 4096)
                    words = body.strip().upper().split()
                    if words == ["STOP"]:
                        command = "STOP"
                    elif len(words) == 1 and words[0] in {"HELP", "START", "CONTINUE", "PROGRESS"}:
                        command = words[0]
                    elif len(words) == 2 and words[0] == "LINK":
                        command = "LINK"
                        if re.fullmatch(r"[0-9A-F]{12}", words[1]):
                            hashed_code = code_hash(identity, words[1])
                    elif "context" in message and len(body) <= 96:
                        reference = string(object_value(message["context"]).get("id"), 256)
                        if re.fullmatch(r"wamid\.[A-Za-z0-9_.=+/-]{1,240}", reference) is None:
                            raise ValueError("Invalid reply reference")
                        command, reply_reference = "ANSWER", reference
                        reply_encrypted = identity.encrypt(body)
                canonical = json.dumps(message, sort_keys=True, separators=(",", ":"))
                results.append(
                    Incoming(
                        message_hash=identity.digest("wa-message", event_key),
                        request_hash=identity.digest("wa-payload", canonical),
                        sender_hash=identity.digest("wa-sender", "+" + sender),
                        sender_encrypted=identity.encrypt("+" + sender),
                        command=command,
                        code_hash=hashed_code,
                        status_reference=reference,
                        delivery_status=delivery,
                        provider_at=at,
                        reply_reference=reply_reference,
                        reply_encrypted=reply_encrypted,
                    )
                )
    return results
