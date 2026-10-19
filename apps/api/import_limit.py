"""Bound import bytes before JSON validation, including chunked requests."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ImportBodyLimit:
    maximum = 65536
    code = "IMPORT_TOO_LARGE"
    message = "Import exceeds 64 KiB."

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    def applies(self, scope: Scope) -> bool:
        return (
            scope["type"] == "http"
            and scope.get("path") == "/api/v1/admin/content-imports"
            and scope.get("method") == "POST"
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.applies(scope):
            await self.app(scope, receive, send)
            return
        raw = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(raw) + len(chunk) > self.maximum:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": self.code,
                            "message": self.message,
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


class ConfigurationBodyLimit(ImportBodyLimit):
    maximum = 1024
    code = "CONFIGURATION_TOO_LARGE"
    message = "Configuration command exceeds 1 KiB."

    def applies(self, scope: Scope) -> bool:
        return (
            scope["type"] == "http"
            and scope.get("method") == "PATCH"
            and scope.get("path", "").startswith("/api/v1/admin/configuration/")
        )
