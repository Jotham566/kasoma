"""Real loopback TCP proves cancelling a slow body closes the storage connection."""

from uuid import uuid4

import anyio
import pytest
from anyio.abc import SocketAttribute

from services import export_reader as module
from services.export_artifacts import ArtifactError

pytestmark = pytest.mark.integration


def test_dribbling_loopback_storage_cannot_extend_total_read_deadline(
    settings, monkeypatch, caplog
):
    monkeypatch.setattr(module, "READ_SECONDS", 0.08)
    caplog.set_level("DEBUG")

    async def run():
        disconnected = anyio.Event()
        listener = await anyio.create_tcp_listener(local_host="127.0.0.1", local_port=0)
        port = listener.extra(SocketAttribute.local_address)[1]
        config = settings.model_copy(update={"object_storage_endpoint": f"http://127.0.0.1:{port}"})

        async def handler(stream):
            async with stream:
                request = b""
                while b"\r\n\r\n" not in request:
                    request += await stream.receive(4096)
                    assert len(request) < 8192
                assert b"Authorization: AWS4-HMAC-SHA256" in request
                assert b"?" not in request.split(b"\r\n", 1)[0]
                await stream.send(b"HTTP/1.1 200 OK\r\nContent-Length: 1000\r\n\r\n")

                async def dribble():
                    try:
                        while True:
                            await stream.send(b"x")
                            await anyio.sleep(0.005)
                    except (anyio.BrokenResourceError, anyio.ClosedResourceError):
                        pass  # The test asserts the peer's disconnect below.

                async with anyio.create_task_group() as group:
                    group.start_soon(dribble)
                    try:
                        await stream.receive()
                    except (anyio.EndOfStream, anyio.BrokenResourceError):
                        disconnected.set()
                    finally:
                        group.cancel_scope.cancel()

        async with listener, anyio.create_task_group() as group:
            group.start_soon(listener.serve, handler)
            reader = module.PrivateExportReader(config)
            try:
                with anyio.fail_after(2):
                    with pytest.raises(ArtifactError, match="EXPORT_OBJECT_READ_FAILED"):
                        await reader.get(uuid4(), uuid4())
                    await disconnected.wait()
            finally:
                await reader.aclose()
                group.cancel_scope.cancel()

    anyio.run(run)
    assert "private-exports/" not in caplog.text
    assert settings.object_storage_secret_key.get_secret_value() not in caplog.text
    assert "AWS4-HMAC-SHA256" not in caplog.text
