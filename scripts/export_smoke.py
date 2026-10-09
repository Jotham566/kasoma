"""Synthetic loopback-only acceptance through the running Compose stack."""

import re
from collections.abc import Callable
from time import sleep
from uuid import uuid4

import httpx

from services.config import Settings

WEB = "http://localhost:3000"
MAIL = "http://localhost:8025"


def require(condition: bool) -> None:
    if not condition:
        raise RuntimeError("Local export smoke failed; private diagnostics withheld")


def exercise(client: httpx.Client, wait: Callable[[float], None] = sleep) -> dict[str, int | bool]:
    email = f"container-export-{uuid4()}@example.invalid"
    origin = {"Origin": WEB}

    def post(path: str, body: dict[str, object], *, key: bool = False) -> httpx.Response:
        headers = origin | ({"Idempotency-Key": str(uuid4())} if key else {})
        return client.post(WEB + "/api/v1/" + path, headers=headers, json=body)

    response = post("auth/otp/request", {"identifier": email, "device_id": str(uuid4())})
    require(response.status_code == 202)
    challenge = response.json()["challenge_id"]
    # Search only this invocation's unpredictable fictional recipient, never read a mailbox dump.
    found = client.get(MAIL + "/api/v1/search", params={"query": f"to:{email}"})
    require(found.status_code == 200 and found.json()["count"] == 1)
    message_id = found.json()["messages"][0]["ID"]
    message = client.get(MAIL + "/api/v1/message/" + message_id)
    require(message.status_code == 200)
    codes = re.findall(r"Kasoma LOGIN code: ([0-9]{6})\.", message.json()["Text"])
    require(len(codes) == 1)
    verified = post("auth/otp/verify", {"challenge_id": challenge, "code": codes[0]})
    require(verified.status_code == 200)
    try:
        created = post("me/data-requests", {"kind": "EXPORT", "affirmative": True}, key=True)
        require(created.status_code == 201)
        path = "me/data-requests/" + created.json()["id"]
        queued = post(path + "/export-job", {}, key=True)
        require(queued.status_code == 202)
        for _ in range(45):
            response = client.get(WEB + "/api/v1/" + path + "/export-job")
            require(response.status_code == 200)
            job = response.json()
            if job["status"] == "READY":
                break
            require(job["status"] in {"QUEUED", "RUNNING"})
            wait(1)
        else:
            raise RuntimeError("Local export worker did not publish within the smoke deadline")
        download = client.get(WEB + "/api/v1/" + path + "/export-file")
        require(download.status_code == 200)
        require(download.headers.get("cache-control") == "no-store")
        require(
            len(download.content) == int(download.headers["content-length"]) == job["size_bytes"]
        )
        bundle = download.json()
        require(bundle["format_version"] == "kasoma-personal-export-v1")
        require(bundle["records"]["identifiers"][0]["value"] == email)
        repeated = client.get(WEB + "/api/v1/" + path + "/export-file")
        require(repeated.status_code == 200 and repeated.content == download.content)
        return {"size_bytes": len(download.content), "worker_completed": True, "frozen_retry": True}
    finally:
        # Revoke only this smoke session. Normal retention handles its synthetic request/copy.
        require(post("auth/logout", {}).status_code == 204)


def main() -> None:
    try:
        settings = Settings()
        require(settings.app_env == "development" and settings.model_provider == "fake")
        require(settings.email_provider == "mailpit" and not settings.allow_external_api_calls)
        with httpx.Client(trust_env=False, timeout=10, follow_redirects=False) as client:
            result = exercise(client)
    except Exception:
        raise SystemExit("Local export smoke failed; private diagnostics withheld") from None
    print(f"Local synthetic export smoke passed: {result}")


if __name__ == "__main__":
    main()
