"""Private MinIO reads cancel under stalled headers or dribbling bodies, without live calls."""

from uuid import uuid4

import anyio
import httpx
import pytest

from services import export_reader as module
from services.export_artifacts import MAX_CIPHERTEXT_BYTES, ArtifactError


class Body(httpx.AsyncByteStream):
    def __init__(self, chunks, *, dribble=False):
        self.chunks, self.dribble = chunks, dribble
        self.closed = False
        self.reads = 0

    async def __aiter__(self):
        for chunk in self.chunks:
            self.reads += 1
            yield chunk
        if self.dribble:
            while True:
                await anyio.sleep(0.005)
                yield b"x"

    async def aclose(self):
        self.closed = True


def invoke(settings, body, *, status=200, headers=None, capture=None):
    async def respond(request):
        if capture is not None:
            capture.append(request)
        wire_headers = [(key.encode(), value.encode()) for key, value in (headers or {}).items()]
        return httpx.Response(status, headers=wire_headers, stream=body)

    async def run():
        reader = module.PrivateExportReader(settings, transport=httpx.MockTransport(respond))
        try:
            return await reader.get(uuid4(), uuid4())
        finally:
            await reader.aclose()

    return anyio.run(run)


def test_signed_private_get_is_bounded_and_not_logged(settings, caplog):
    caplog.set_level("DEBUG")
    raw = b"x" * MAX_CIPHERTEXT_BYTES
    body, requests = Body([raw]), []
    assert (
        invoke(settings, body, headers={"Content-Length": str(len(raw))}, capture=requests) == raw
    )
    assert body.closed
    request = requests[0]
    assert request.url.host == "localhost" and request.url.query == b""
    assert request.headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=")
    assert request.headers["X-Amz-Content-Sha256"] == module.EMPTY_DIGEST
    assert "us-east-1/s3/aws4_request" in request.headers["Authorization"]
    assert request.url.path not in caplog.text
    assert settings.object_storage_secret_key.get_secret_value() not in caplog.text


@pytest.mark.parametrize(
    "header", [None, "", "0", "-1", "9999999", "131073", "１２", "1, 1", "1.0"]
)
def test_invalid_length_rejected_before_read(settings, header):
    body = Body([b"secret"])
    with pytest.raises(ArtifactError, match="EXPORT_OBJECT_READ_FAILED") as exc:
        invoke(settings, body, headers={} if header is None else {"Content-Length": header})
    assert body.closed and body.reads == 0 and exc.value.__suppress_context__


@pytest.mark.parametrize(
    ("status", "headers", "raw"),
    [
        (302, {"Location": "https://example.invalid", "Content-Length": "1"}, b"a"),
        (404, {"Content-Length": "1"}, b"a"),
        (200, {"Content-Length": "1", "Content-Encoding": "gzip"}, b"a"),
        (200, {"Content-Length": "1", "Transfer-Encoding": "chunked"}, b"a"),
        (200, {"Content-Length": "1"}, b"ab"),
        (200, {"Content-Length": "2"}, b"a"),
    ],
)
def test_redirect_encoding_and_inconsistent_bodies_fail_closed(settings, status, headers, raw):
    body = Body([raw])
    with pytest.raises(ArtifactError, match="EXPORT_OBJECT_READ_FAILED"):
        invoke(settings, body, status=status, headers=headers)
    assert body.closed


@pytest.mark.parametrize("phase", ["headers", "body", "cancel"])
def test_absolute_deadline_and_cancellation_release_stalled_reads(settings, monkeypatch, phase):
    monkeypatch.setattr(module, "READ_SECONDS", 0.04)
    body = Body([b"a"], dribble=True)
    entered, left = [], []

    async def respond(request):
        entered.append(True)
        try:
            if phase == "headers":
                await anyio.sleep_forever()
            return httpx.Response(200, headers={"Content-Length": "1000"}, stream=body)
        finally:
            left.append(True)

    async def run():
        reader = module.PrivateExportReader(settings, transport=httpx.MockTransport(respond))
        try:
            if phase == "cancel":
                with anyio.move_on_after(0.015) as cancelled:
                    await reader.get(uuid4(), uuid4())
                assert cancelled.cancel_called
            else:
                with pytest.raises(ArtifactError, match="EXPORT_OBJECT_READ_FAILED"):
                    await reader.get(uuid4(), uuid4())
        finally:
            await reader.aclose()

    anyio.run(run)
    assert entered == left == [True]
    assert phase == "headers" or body.closed


@pytest.mark.parametrize(
    "endpoint",
    ["http://localhost:9000/a", "http://localhost:9000?q=1", "http://user@localhost:9000"],
)
def test_ambiguous_local_endpoints_rejected(settings, endpoint):
    with pytest.raises(ArtifactError, match="EXPORT_READER_UNAVAILABLE"):
        module.PrivateExportReader(
            settings.model_copy(update={"object_storage_endpoint": endpoint})
        )
