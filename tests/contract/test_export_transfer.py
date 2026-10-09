"""Exact-length attachments must abort and close on failure or client cancellation."""

from functools import partial
from uuid import uuid4

import anyio
import pytest
from starlette.requests import ClientDisconnect

from apps.api.export_transfer import AsyncExportResponse, ExportResponse
from services.export_downloads import AsyncDownload, Download


def run_response(
    parts,
    size,
    *,
    broken_send=False,
    disconnect=False,
    source_failure=False,
    stalled_send=False,
    asynchronous=False,
):
    closed, messages = [], []

    def source():
        try:
            yield from parts
            if source_failure:
                raise RuntimeError("synthetic confidential provider diagnostic")
        finally:
            closed.append(True)

    async def async_source():
        try:
            for part in parts:
                await anyio.sleep(0)
                yield part
            if source_failure:
                raise RuntimeError("synthetic confidential provider diagnostic")
        finally:
            closed.append(True)

    response = (
        AsyncExportResponse(AsyncDownload(size, async_source()), uuid4())
        if asynchronous
        else ExportResponse(Download(size, source()), uuid4())
    )

    async def run():
        emitted = anyio.Event()

        async def send(message):
            messages.append(message)
            if message["type"] == "http.response.body" and message.get("body"):
                emitted.set()
                if broken_send:
                    raise OSError("disconnected")
                if disconnect or stalled_send:
                    await anyio.sleep_forever()

        async def receive():
            await emitted.wait()
            return {"type": "http.disconnect"}

        await response(
            {"type": "http", "asgi": {"spec_version": "2.3" if disconnect else "2.4"}},
            receive,
            send,
        )

    error = None
    try:
        anyio.run(run)
    except Exception as exc:
        error = exc
    return response, messages, closed, error


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def runner(request):
    return partial(run_response, asynchronous=request.param)


def test_complete_attachment_preserves_exact_length_headers_and_closes(runner):
    response, messages, closed, error = runner([b'{"ok":', b"true}"], 11)
    assert error is None and closed == [True]
    assert response.headers["Content-Length"] == "11"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Content-Disposition"].startswith(
        'attachment; filename="kasoma-export-'
    )
    assert b"".join(m.get("body", b"") for m in messages) == b'{"ok":true}'
    assert messages[-1]["more_body"] is False


@pytest.mark.parametrize(
    ("parts", "size", "source_failure"),
    [([b"abc"], 4, False), ([b"abcd"], 3, False), ([b""], 1, False), ([b"a"], 2, True)],
)
def test_invalid_or_failed_body_has_no_successful_final_frame(runner, parts, size, source_failure):
    _, messages, closed, error = runner(parts, size, source_failure=source_failure)
    assert isinstance(error, RuntimeError)
    assert str(error) == "Private export transfer incomplete" and error.__suppress_context__
    assert closed == [True]
    assert not any(m.get("more_body") is False for m in messages)


@pytest.mark.parametrize("disconnect", [False, True])
def test_client_disconnect_closes_source_without_sending_remaining_chunks(runner, disconnect):
    _, messages, closed, error = runner(
        [b"first", b"second"], 11, broken_send=not disconnect, disconnect=disconnect
    )
    assert (error is None) if disconnect else isinstance(error, ClientDisconnect)
    assert closed == [True]
    assert [m["body"] for m in messages if m["type"] == "http.response.body"] == [b"first"]
    assert not any(m.get("more_body") is False for m in messages)


def test_downstream_backpressure_has_a_whole_transfer_deadline(runner, monkeypatch):
    from apps.api import export_transfer

    monkeypatch.setattr(export_transfer, "TRANSFER_SECONDS", 0.05)
    _, messages, closed, error = runner([b"first", b"second"], 11, stalled_send=True)
    assert isinstance(error, TimeoutError) and closed == [True]
    assert not any(m.get("more_body") is False for m in messages)


def test_async_provider_wait_is_cancelled_by_response_deadline(monkeypatch):
    from apps.api import export_transfer

    monkeypatch.setattr(export_transfer, "TRANSFER_SECONDS", 0.04)
    closed, messages = [], []

    async def source():
        try:
            await anyio.sleep_forever()
            yield b"never"
        finally:
            closed.append(True)

    async def run():
        response = AsyncExportResponse(AsyncDownload(5, source()), uuid4())

        async def receive():
            await anyio.sleep_forever()

        async def send(message):
            messages.append(message)

        with pytest.raises(TimeoutError):
            await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)

    anyio.run(run)
    assert closed == [True]
    assert [m["type"] for m in messages] == ["http.response.start"]
