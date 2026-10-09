"""The runtime probe is bounded to fictional local resources and never prints private data."""

import json

import httpx
import pytest

from scripts.export_smoke import MAIL, WEB, exercise


@pytest.mark.parametrize("corrupt", [False, True])
def test_export_smoke_uses_only_own_mail_and_detects_nonfrozen_retry(corrupt):
    state = {"polls": 0, "downloads": 0, "logout": False}
    email = ""
    encoded = b""
    waits = []

    def handle(request):
        nonlocal email, encoded
        assert str(request.url).startswith((WEB + "/", MAIL + "/"))
        path = request.url.path
        if path.endswith("otp/request"):
            email = json.loads(request.content)["identifier"]
            assert email.startswith("container-export-") and email.endswith("@example.invalid")
            encoded = json.dumps(
                {
                    "format_version": "kasoma-personal-export-v1",
                    "records": {"identifiers": [{"value": email}]},
                }
            ).encode()
            return httpx.Response(202, json={"challenge_id": "synthetic"})
        if path.endswith("search"):
            assert request.url.params["query"] == f"to:{email}"
            return httpx.Response(200, json={"count": 1, "messages": [{"ID": "own-message"}]})
        if path.endswith("message/own-message"):
            return httpx.Response(
                200, json={"Text": "Kasoma LOGIN code: 246810. Expires in 10 minutes."}
            )
        if path.endswith("otp/verify"):
            assert json.loads(request.content)["code"] == "246810"
            return httpx.Response(200, json={})
        if path.endswith("data-requests"):
            return httpx.Response(201, json={"id": "own-request"})
        if path.endswith("export-job"):
            if request.method == "POST":
                return httpx.Response(202, json={})
            state["polls"] += 1
            return httpx.Response(
                200,
                json={
                    "status": "READY" if state["polls"] > 1 else "QUEUED",
                    "size_bytes": len(encoded),
                },
            )
        if path.endswith("export-file"):
            state["downloads"] += 1
            body = b"corrupt" if corrupt and state["downloads"] > 1 else encoded
            return httpx.Response(
                200,
                content=body,
                headers={"cache-control": "no-store", "content-length": str(len(body))},
            )
        assert path.endswith("auth/logout")
        state["logout"] = True
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        if corrupt:
            with pytest.raises(RuntimeError, match="private diagnostics withheld"):
                exercise(client, waits.append)
        else:
            result = exercise(client, waits.append)
            assert result == {
                "size_bytes": len(encoded),
                "worker_completed": True,
                "frozen_retry": True,
            }
    assert waits == [1] and state["logout"]
