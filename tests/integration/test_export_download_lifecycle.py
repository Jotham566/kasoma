"""ADR-048 privacy access and cancellation boundaries before HTTP activation."""

import json
from datetime import timedelta
from uuid import uuid4

import anyio
import pytest

from services.export_downloads import prepare, prepare_async
from services.export_jobs import queue
from services.export_processing import process_one
from tests.integration.test_export_jobs import SweepStore, setup_job
from tests.integration.test_identity import consent, profile

pytestmark = pytest.mark.integration


def test_async_privacy_access_remains_available_after_learning_consent_withdrawal(content):
    identity, client, actors, token, target = setup_job(content)
    profile(client, actors["learner"])
    assert consent(client, actors["learner"], "SELF").status_code == 200
    result = client.post(
        "/api/v1/me/consents",
        headers=actors["learner"] | {"Idempotency-Key": str(uuid4())},
        json={
            "consent_type": "WITHDRAW",
            "policy_version": identity.settings.consent_policy_version,
            "affirmative": True,
        },
    )
    assert result.status_code == 200
    queue(identity, token, target, uuid4(), uuid4())
    store = SweepStore(identity)
    assert process_one(identity, store)
    download = prepare(identity, store, token, target)
    raw = b"".join(download.chunks)
    assert len(raw) == download.size
    records = json.loads(raw)["records"]
    assert any(row["consent_type"] == "WITHDRAW" for row in records["consents"])


@pytest.mark.parametrize("stop", ["recent_auth", "deadline", "cancel"])
def test_slow_or_cancelled_download_does_not_deliver_remaining_chunks(content, stop):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    with identity.transaction() as db:
        actor = identity.authenticate(db, token).user_id
        for _ in range(500):
            identity.event(db, actor, "synthetic.slow." + "x" * 200, str(uuid4()))

    class CountingStore(SweepStore):
        reads = 0

        def get(self, generation, object_id):
            self.reads += 1
            return super().get(generation, object_id)

    store = CountingStore(identity)
    assert process_one(identity, store)
    elapsed = [0.0]
    download = prepare(identity, store, token, target, timer=lambda: elapsed[0])
    source = download.chunks
    first = next(source)
    assert 0 < len(first) < download.size
    reads = store.reads
    if stop == "cancel":
        source.close()
        assert list(source) == [] and store.reads == reads
    else:
        if stop == "recent_auth":
            initial = identity.clock()
            identity.clock = lambda: initial + timedelta(minutes=10)
        else:
            elapsed[0] = 300.0
        with pytest.raises(RuntimeError, match="Private export transfer incomplete") as exc:
            next(source)
        assert exc.value.__suppress_context__
        assert list(source) == []
        if stop == "deadline":
            assert store.reads == reads  # Deadline is checked before fetching another object.


@pytest.mark.parametrize("mode", ["complete", "revoke", "corrupt", "cancel"])
def test_async_download_shares_integrity_and_authority_and_closes_store(content, mode):
    identity, _, actors, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    with identity.transaction() as db:
        actor = identity.authenticate(db, token).user_id
        for _ in range(500):
            identity.event(db, actor, "synthetic.async." + "x" * 200, str(uuid4()))
    store = SweepStore(identity)
    assert process_one(identity, store)
    frozen = b"".join(prepare(identity, store, token, target).chunks)

    class Reader:
        reads = 0
        closed = False

        async def get(self, generation, object_id):
            await anyio.sleep(0)
            self.reads += 1
            if mode == "corrupt" and self.reads > 1:
                return b"corrupt synthetic bytes"
            return store.get(generation, object_id)

        async def aclose(self):
            self.closed = True

    reader = Reader()

    async def run():
        def forbidden_factory():
            pytest.fail("Cross-owner access must fail before allocating storage")

        from services.identity import IdentityError

        with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
            await prepare_async(
                identity, forbidden_factory, actors["other"]["Authorization"][7:], target
            )
        download = await prepare_async(identity, lambda: reader, token, target)
        source = download.chunks
        first = await anext(source)
        assert len(first) < download.size
        if mode == "complete":
            raw = first + b"".join([part async for part in source])
            assert raw == frozen and len(raw) == download.size
        elif mode == "cancel":
            await source.aclose()
            assert reader.reads == 1
        else:
            if mode == "revoke":
                identity.logout(token, True, str(uuid4()))
            with pytest.raises(RuntimeError, match="Private export transfer incomplete"):
                await anext(source)
        assert reader.closed

    anyio.run(run)
