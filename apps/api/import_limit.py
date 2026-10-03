"""Bound import bytes before JSON validation, including chunked requests."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ImportBodyLimit:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope.get("path") != "/api/v1/admin/content-imports"
            or scope.get("method") != "POST"
        ):
            await self.app(scope, receive, send)
            return
        raw = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(raw) + len(chunk) > 65536:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "IMPORT_TOO_LARGE",
                            "message": "Import exceeds 64 KiB.",
                            "request_id": scope.get("state", {}).get("request_id"),
                            "field_errors": [],
                        }
                    },
                )
                await response(scope, receive, send)
                return
            raw.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(raw), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)
