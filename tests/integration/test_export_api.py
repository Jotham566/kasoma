"""Isolated registration tests the proposed transport before application activation."""

from datetime import timedelta
from uuid import UUID, uuid4

import anyio
import pytest
from sqlalchemy.orm import Session

from apps.api.export_jobs import reader_factory
from services.domain.export_jobs import ExportJob
from services.export_processing import process_one
from tests.integration.test_data_exports import export, fresh
from tests.integration.test_data_requests import claim, create
from tests.integration.test_export_jobs import SweepStore, setup_job

pytestmark = pytest.mark.integration


def test_delivery_bounds_a_stalled_adapter_without_client_disconnect(content, monkeypatch):
    import services.export_downloads as downloads

    identity, client, actors, token, target = setup_job(content)
    store = SweepStore(identity)
    headers = actors["learner"] | {"Idempotency-Key": str(uuid4())}
    url = f"/api/v1/me/data-requests/{target}/export-job"
    assert client.post(url, headers=headers, json={}).status_code == 202
    assert process_one(identity, store)
    events = []

    class StalledReader:
        async def get(self, generation, object_id):
            try:
                await anyio.sleep_forever()
            finally:
                events.append("read-cancelled")

        async def aclose(self):
            events.append("reader-closed")

    monkeypatch.setattr(downloads, "OBJECT_READ_SECONDS", 0.01)

    async def exercise():
        download = await downloads.prepare_async(identity, StalledReader, token, target)
        # No client disconnect: the service itself must enforce the per-object bound.
        with anyio.fail_after(1):
            with pytest.raises(RuntimeError, match="^Private export transfer incomplete$"):
                await anext(download.chunks)
        assert events == ["read-cancelled", "reader-closed"]

    anyio.run(exercise)
    assert client.get(url, headers=actors["learner"]).json()["status"] == "READY"


def setup_api(content):
    identity, client, actors, token, target = setup_job(content)
    store = SweepStore(identity)
    readers = []

    class Reader:
        closed = False

        async def get(self, generation, object_id):
            return store.get(generation, object_id)

        async def aclose(self):
            self.closed = True

    def factory():
        reader = Reader()
        readers.append(reader)
        return reader

    client.app.dependency_overrides[reader_factory] = lambda: factory
    return identity, client, actors, target, store, readers


def test_http_job_receipt_status_attachment_and_expiry(content):
    identity, client, actors, target, store, readers = setup_api(content)
    headers = actors["learner"]
    url = f"/api/v1/me/data-requests/{target}"
    key, correlation = str(uuid4()), str(uuid4())
    command_headers = headers | {"Idempotency-Key": key, "request_id": correlation}
    queued = client.post(url + "/export-job", headers=command_headers, json={})
    assert queued.status_code == 202 and queued.json()["status"] == "QUEUED"
    assert queued.headers["request_id"] == correlation
    assert (
        client.post(url + "/export-job", headers=command_headers, json={}).json() == queued.json()
    )
    assert client.get(url + "/export-file", headers=headers).status_code == 409
    assert readers == []
    with Session(identity.engine) as db:
        assert str(db.get(ExportJob, target).correlation_id) == correlation
    assert process_one(identity, store)
    state = client.get(url + "/export-job", headers=headers)
    assert state.status_code == 200 and state.json()["status"] == "READY"
    for secret in ["grant_family", "generation_id", "manifest", "object_id", "lookup_hash"]:
        assert secret not in state.text
    result = client.get(url + "/export-file", headers=headers)
    assert result.status_code == 200 and result.json()["request_id"] == str(target)
    assert (
        len(result.content) == int(result.headers["Content-Length"]) == state.json()["size_bytes"]
    )
    assert result.headers["cache-control"] == "no-store"
    assert (
        result.headers["content-disposition"]
        == f'attachment; filename="kasoma-export-{target}.json"'
    )
    assert result.headers["x-content-type-options"] == "nosniff"
    assert readers[-1].closed
    assert client.get(url + "/export-file", headers=headers).content == result.content
    legacy = export(client, headers, str(target))
    assert legacy.status_code == 409 and legacy.json()["error"]["code"] == "EXPORT_FILE_REQUIRED"
    # A lost command acknowledgement returns the completed status, without another generation.
    assert (
        client.post(url + "/export-job", headers=command_headers, json={}).json()["status"]
        == "READY"
    )
    now = identity.clock()
    identity.clock = lambda: now + timedelta(hours=24)
    renewed = fresh(identity)
    assert client.get(url + "/export-file", headers=renewed).status_code == 410
    assert export(client, renewed, str(target)).status_code == 410
    assert client.get(url + "/export-job", headers=renewed).json()["status"] == "EXPIRED"


def test_http_export_commands_are_closed_and_owner_only(content):
    _, client, actors, target, _, readers = setup_api(content)
    url = f"/api/v1/me/data-requests/{target}"
    for role in ["other", "admin"]:
        headers = actors[role] | {"Idempotency-Key": str(uuid4())}
        assert client.post(url + "/export-job", headers=headers, json={}).status_code == 404
        assert client.get(url + "/export-job", headers=headers).status_code == 404
        assert client.get(url + "/export-file", headers=headers).status_code == 404
    assert client.get(url + "/export-file").status_code == 401
    headers = actors["learner"] | {"Idempotency-Key": str(uuid4())}
    assert (
        client.post(
            url + "/export-job", headers=headers, json={"user_id": str(uuid4())}
        ).status_code
        == 422
    )
    assert client.post(url + "/export-job", headers=actors["learner"], json={}).status_code == 422
    assert readers == []
    schema = client.app.openapi()
    operation = schema["paths"]["/api/v1/me/data-requests/{target}/export-file"]["get"]
    assert (
        operation["responses"]["200"]["content"]["application/json"]["schema"]["format"] == "binary"
    )


def test_deletion_inventory_counts_owned_jobs_and_copies_without_disclosing_grants(content):
    identity, client, actors, target, store, _ = setup_api(content)
    for role, request_id in [
        ("learner", target),
        ("other", UUID(create(client, actors["other"]).json()["id"])),
    ]:
        response = client.post(
            f"/api/v1/me/data-requests/{request_id}/export-job",
            headers=actors[role] | {"Idempotency-Key": str(uuid4())},
            json={},
        )
        assert response.status_code == 202
        assert process_one(identity, store)
    deletion = create(client, actors["learner"], "DELETE").json()["id"]
    assert claim(client, actors["admin"], deletion).status_code == 200
    response = client.get(
        f"/api/v1/admin/data-requests/{deletion}/deletion-preview", headers=actors["admin"]
    )
    assert response.status_code == 200
    values = {item["source"]: item for item in response.json()["sources"]}
    assert values["personal_export_jobs"]["count"] == 1
    assert values["personal_export_jobs"]["retention"] == "SIX_YEARS_AFTER_COMPLETION"
    assert values["personal_export_generations"]["count"] == 1
    assert values["personal_export_generations"]["retention"] == "TRANSIENT_EXPIRY"
    assert response.json()["execution_enabled"] is False
    for secret in [
        "grant_family",
        "grant_authenticated_at",
        "encrypted_manifest",
        "private-exports",
    ]:
        assert secret not in response.text


def test_real_http_disconnect_cancels_inflight_reader_and_closes_resources(content):
    import socket
    import threading
    import time

    import anyio
    import httpx
    import uvicorn

    identity, client, actors, target, store, _ = setup_api(content)
    headers = actors["learner"]
    with identity.transaction() as db:
        actor = identity.authenticate(db, headers["Authorization"][7:]).user_id
        for _ in range(500):
            identity.event(db, actor, "synthetic.http." + "x" * 200, str(uuid4()))
    assert (
        client.post(
            f"/api/v1/me/data-requests/{target}/export-job",
            headers=headers | {"Idempotency-Key": str(uuid4())},
            json={},
        ).status_code
        == 202
    )
    assert process_one(identity, store)
    entered, cancelled, closed = (threading.Event() for _ in range(3))

    class Reader:
        calls = 0

        async def get(self, generation, object_id):
            self.calls += 1
            if self.calls > 1:
                entered.set()
                try:
                    await anyio.sleep_forever()
                finally:
                    cancelled.set()
            return store.get(generation, object_id)

        async def aclose(self):
            closed.set()

    client.app.dependency_overrides[reader_factory] = lambda: Reader
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(16)
        port = listener.getsockname()[1]
        server = uvicorn.Server(
            uvicorn.Config(client.app, lifespan="off", log_level="error", access_log=False)
        )
        thread = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 5
            while not server.started and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert server.started
            with httpx.Client(trust_env=False, timeout=3) as http:
                with http.stream(
                    "GET",
                    f"http://127.0.0.1:{port}/api/v1/me/data-requests/{target}/export-file",
                    headers=headers,
                ) as response:
                    assert response.status_code == 200
                    assert next(response.iter_raw())
                    assert entered.wait(timeout=3)
                assert cancelled.wait(timeout=3) and closed.wait(timeout=3)
        finally:
            server.should_exit = True
            thread.join(timeout=5)
            if thread.is_alive():
                server.force_exit = True
                thread.join(timeout=2)
            assert not thread.is_alive(), "Owned synthetic HTTP server did not close"
