"""FR-CNT-001: bounded structured imports never execute uploaded content."""

import asyncio
from copy import deepcopy
from uuid import uuid4

import pytest
from pydantic import ValidationError
from starlette.types import Message, Scope

from apps.api.import_limit import ImportBodyLimit
from apps.worker.main import make_worker
from services.config import Settings
from services.import_contracts import ImportInput


def candidate():
    return {
        "format_version": "kasoma-draft-import-v1",
        "synthetic": True,
        "records": [
            {
                "subject_id": str(uuid4()),
                "document": {
                    "source": "Original synthetic item",
                    "source_locator": "fixture:1",
                    "rights_status": "ORIGINAL_KASOMA",
                    "rights_evidence": "Original fixture",
                },
                "change_reason": "Import synthetic candidate",
            }
        ],
    }


def test_import_schema_accepts_incomplete_drafts_and_rejects_unsafe_candidates():
    body = candidate()
    assert ImportInput.model_validate(body).records[0].document.source_locator == "fixture:1"
    for field, value in [
        ("source_locator", " "),
        ("rights_status", "LICENSED"),
        ("source", ""),
        ("rights_evidence", ""),
        ("prompt", "<script>alert(1)</script>"),
    ]:
        bad = deepcopy(body)
        bad["records"][0]["document"][field] = value
        with pytest.raises(ValidationError):
            ImportInput.model_validate(bad)
    for count in [0, 21]:
        with pytest.raises(ValidationError):
            ImportInput.model_validate(body | {"records": body["records"] * count})
    duplicate = deepcopy(body["records"][0])
    duplicate["document"]["source_locator"] = "different-page"
    with pytest.raises(ValidationError):
        ImportInput.model_validate(body | {"records": body["records"] + [duplicate]})
    with pytest.raises(ValidationError):
        ImportInput.model_validate(body | {"synthetic": False})
    body["records"][0]["source_version_id"] = str(uuid4())
    with pytest.raises(ValidationError):
        ImportInput.model_validate(body)


@pytest.mark.parametrize("size, expected", [(65536, 200), (65537, 413)])
def test_chunked_import_is_bounded_before_application(size, expected):
    async def run():
        sent: list[Message] = []
        chunks = iter([b"a" * 32768, b"b" * (size - 32768)])
        calls = []

        async def receive():
            chunk = next(chunks)
            return {"type": "http.request", "body": chunk, "more_body": chunk[:1] == b"a"}

        async def send(message):
            sent.append(message)

        async def app(scope, receive, send):
            body = await receive()
            calls.append(body["body"])
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        scope: Scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/admin/content-imports",
            "state": {"request_id": str(uuid4())},
        }
        await ImportBodyLimit(app)(scope, receive, send)
        assert sent[0]["status"] == expected
        assert bool(calls) == (expected == 200)
        if expected == 413:
            assert b"IMPORT_TOO_LARGE" in sent[1]["body"]
            assert b"bbbbbbbb" not in sent[1]["body"]

    asyncio.run(run())


def test_import_worker_queue_and_schedule_are_registered():
    worker = make_worker(Settings())
    assert "imports" in worker.amqp.queues
    assert worker.conf.beat_schedule["content-imports"]["options"]["queue"] == "imports"
    assert worker.tasks["kasoma.content_imports"].acks_late
