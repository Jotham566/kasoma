"""Bounded attachment transport for ADR-048 owned exports."""

from collections.abc import AsyncGenerator, Generator
from uuid import UUID

import anyio
from starlette.responses import StreamingResponse
from starlette.types import Receive, Scope, Send

from services.export_artifacts import CHUNK_BYTES, MAX_CHUNKS
from services.export_downloads import AsyncDownload, Download

TRANSFER_SECONDS = 300


class ExportResponse(StreamingResponse):
    def __init__(self, download: Download, target: UUID) -> None:
        if type(target) is not UUID or not 0 < download.size <= CHUNK_BYTES * MAX_CHUNKS:
            download.chunks.close()
            raise ValueError("Invalid export attachment")
        self.download = download
        self.source = self.bounded()
        super().__init__(
            self.source,
            media_type="application/json",
            headers={
                "Content-Length": str(download.size),
                "Content-Disposition": f'attachment; filename="kasoma-export-{target}.json"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    def bounded(self) -> Generator[bytes, None, None]:
        remaining = self.download.size
        try:
            for part in self.download.chunks:
                if type(part) is not bytes or not 0 < len(part) <= min(CHUNK_BYTES, remaining):
                    raise ValueError("Export chunk length")
                remaining -= len(part)
                yield part
            if remaining:
                raise ValueError("Incomplete export body")
        except Exception:
            raise RuntimeError("Private export transfer incomplete") from None
        finally:
            self.download.chunks.close()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            # Bound downstream backpressure as well as producer progress checks.
            with anyio.fail_after(TRANSFER_SECONDS):
                await super().__call__(scope, receive, send)
        finally:
            # Starlette's synchronous iterator bridge does not close a cancelled producer.
            # Its thread work is shielded; close only after the in-flight next() has returned.
            with anyio.CancelScope(shield=True):
                await anyio.to_thread.run_sync(self.source.close)
                await anyio.to_thread.run_sync(self.download.chunks.close)


class AsyncExportResponse(StreamingResponse):
    """Learner delivery uses async storage; no blocked synchronous provider thread survives."""

    def __init__(self, download: AsyncDownload, target: UUID) -> None:
        if type(target) is not UUID or not 0 < download.size <= CHUNK_BYTES * MAX_CHUNKS:
            raise ValueError("Invalid export attachment")
        self.download = download
        self.source = self.bounded()
        super().__init__(
            self.source,
            media_type="application/json",
            headers={
                "Content-Length": str(download.size),
                "Content-Disposition": f'attachment; filename="kasoma-export-{target}.json"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    async def bounded(self) -> AsyncGenerator[bytes, None]:
        remaining = self.download.size
        try:
            async for part in self.download.chunks:
                if type(part) is not bytes or not 0 < len(part) <= min(CHUNK_BYTES, remaining):
                    raise ValueError("Export chunk length")
                remaining -= len(part)
                yield part
            if remaining:
                raise ValueError("Incomplete export body")
        except Exception:
            raise RuntimeError("Private export transfer incomplete") from None
        finally:
            with anyio.CancelScope(shield=True):
                await self.download.chunks.aclose()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            with anyio.fail_after(TRANSFER_SECONDS):
                await super().__call__(scope, receive, send)
        finally:
            with anyio.CancelScope(shield=True):
                await self.source.aclose()
                await self.download.chunks.aclose()
