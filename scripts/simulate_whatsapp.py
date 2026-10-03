"""Send one signed synthetic command to the local API; never contact WhatsApp."""

import hashlib
import hmac
import json
import os
import re
from datetime import UTC, datetime
from uuid import uuid4

import httpx

from services.config import Settings


def main() -> None:
    settings = Settings()
    command = os.environ.get("KASOMA_WHATSAPP_TEXT", "HELP").strip().upper()
    if re.fullmatch(r"(?:HELP|STOP|LINK [A-F0-9]{12})", command) is None:
        raise SystemExit("Use HELP, STOP or LINK followed by a 12-character local code.")
    secret = settings.whatsapp_app_secret
    if secret is None or len(secret.get_secret_value()) < 32:
        raise SystemExit("Run make setup to configure the local signing boundary.")
    raw = json.dumps(
        {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": settings.whatsapp_business_id,
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {"phone_number_id": settings.whatsapp_phone_number_id},
                                "messages": [
                                    {
                                        "id": "wamid.synthetic." + str(uuid4()),
                                        "from": "256700000090",
                                        "timestamp": str(int(datetime.now(UTC).timestamp())),
                                        "type": "text",
                                        "text": {"body": command},
                                    }
                                ],
                            },
                        }
                    ],
                }
            ],
        }
    ).encode()
    signature = hmac.new(secret.get_secret_value().encode(), raw, hashlib.sha256).hexdigest()
    try:
        with httpx.Client(timeout=5, trust_env=False, follow_redirects=False) as client:
            response = client.post(
                settings.api_public_url.rstrip("/") + "/api/v1/webhooks/whatsapp",
                content=raw,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": "sha256=" + signature,
                },
            )
        if response.status_code != 200:
            raise SystemExit(
                "Local synthetic intake rejected the command. Check local configuration."
            )
    except httpx.HTTPError:
        raise SystemExit("Local API unavailable. Start make dev and retry.") from None
    print("Synthetic command durably accepted. The messaging worker will process it.")


if __name__ == "__main__":
    main()
