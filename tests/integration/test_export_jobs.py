"""ADR-048 in-progress lifecycle: owner commands, bounded claims and immutable grants."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.export_jobs import ExportGeneration, ExportJob
from services.export_jobs import claim_next, fail_claim, queue, status
from services.identity import IdentityError
from tests.integration.test_data_requests import create
from tests.integration.test_diagnostics import diagnostic as diagnostic_fixture

pytestmark = pytest.mark.integration
diagnostic = diagnostic_fixture


def test_diagnostic_completion_during_generation_cannot_mix_snapshot_visibility(
    diagnostic, monkeypatch
):
    import json

    from services import export_processing
    from services.export_downloads import prepare
    from tests.integration.test_diagnostics import next_item, start, submit

    identity, client, actors, body = diagnostic
    headers = actors["learner"]
    token = headers["Authorization"][7:]
    session = start(client, headers, body["subject_id"]).json()["id"]
    for _ in range(14):
        assert (
            submit(client, headers, session, next_item(client, headers, session)).status_code == 200
        )
    target = UUID(create(client, headers).json()["id"])
    queue(identity, token, target, uuid4(), uuid4())
    store = SweepStore(identity)
    original = export_processing.encoded_project
    completed = False

    def complete_before_projection(*args, **kwargs):
        nonlocal completed
        # The processor has established its read-only snapshot. The independent API
        # transaction now commits the final grade before any export section is read.
        result = submit(client, headers, session, next_item(client, headers, session))
        assert result.status_code == 200
        completed = True
        yield from original(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(export_processing, "encoded_project", complete_before_projection)
        assert export_processing.process_one(identity, store)
    assert completed
    frozen = b"".join(prepare(identity, store, token, target).chunks)
    records = json.loads(frozen)["records"]
    assert len(records["answers"]) == 14
    assert all(not row["grade_released"] for row in records["answers"])
    for section in ["grades", "mastery_evidence", "mastery_estimates", "mastery_history"]:
        assert records[section] == []
    assert b"".join(prepare(identity, store, token, target).chunks) == frozen

    following = UUID(create(client, headers).json()["id"])
    queue(identity, token, following, uuid4(), uuid4())
    assert export_processing.process_one(identity, store)
    released = json.loads(b"".join(prepare(identity, store, token, following).chunks))["records"]
    assert len(released["answers"]) == len(released["grades"]) == 15
    assert all(row["grade_released"] for row in released["answers"])
    assert released["mastery_history"]


def setup_job(content):
    identity, client, actors, _ = content
    token = actors["learner"]["Authorization"][7:]
    target = UUID(create(client, actors["learner"]).json()["id"])
    return identity, client, actors, token, target


def test_owner_queue_retry_receipt_and_status_are_minimized(content):
    identity, _, actors, token, target = setup_job(content)
    key = uuid4()
    first = queue(identity, token, target, key, uuid4())
    assert first.status == "QUEUED" and first.attempts == 0
    assert queue(identity, token, target, key, uuid4()) == first
    assert status(identity, token, target) == first
    for role in ["other", "admin"]:
        with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
            status(identity, actors[role]["Authorization"][7:], target)
        with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
            queue(identity, actors[role]["Authorization"][7:], target, uuid4(), uuid4())
    for forbidden in ["grant_family", "grant_authenticated_at", "generation_id", "manifest", token]:
        assert forbidden not in first.model_dump_json()
    with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
        queue(
            identity, token, uuid4(), key, uuid4()
        )  # Unknown resource fails before receipt lookup.


def test_only_one_concurrent_claim_and_stale_failure_cannot_renew_grant(content):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(lambda _: claim_next(identity), range(2)))
    actual = [claim for claim in claims if claim is not None]
    assert len(actual) == 1
    claim = actual[0]
    assert status(identity, token, target).status == "RUNNING"
    with Session(identity.engine) as db:
        generation = db.get(ExportGeneration, claim.generation_id)
        assert generation.lease_until == generation.created_at + timedelta(seconds=180)
        assert generation.published_at is None and generation.encrypted_manifest is None
    assert fail_claim(identity, claim, "PROCESSING_FAILED")
    assert not fail_claim(identity, claim, "PROCESSING_FAILED")
    assert claim_next(identity) is None  # Backoff must elapse before another attempt.
    old = identity.clock()
    identity.clock = lambda: old + timedelta(seconds=30)
    following = claim_next(identity)
    assert following is not None and following.generation_id != claim.generation_id
    assert following.family == claim.family and following.authenticated_at == claim.authenticated_at
    assert not fail_claim(identity, claim, "LIMIT_REACHED")
    assert status(identity, token, target).attempts == 2


def test_three_attempts_then_explicit_verified_retry(content):
    identity, _, _, token, target = setup_job(content)
    original_key = uuid4()
    queue(identity, token, target, original_key, uuid4())
    initial = identity.clock()
    for step, seconds in enumerate([0, 30, 90], 1):
        identity.clock = lambda seconds=seconds: initial + timedelta(seconds=seconds)
        claim = claim_next(identity)
        assert claim is not None
        assert fail_claim(identity, claim, "PROCESSING_FAILED")
        assert status(identity, token, target).attempts == step
    result = status(identity, token, target)
    assert result.status == "FAILED" and result.failure == "PROCESSING_FAILED"
    assert claim_next(identity) is None
    assert queue(identity, token, target, original_key, uuid4()).status == "FAILED"
    with Session(identity.engine) as db:
        job = db.get(ExportJob, target)
        assert job.grant_family is None and job.grant_authenticated_at is None
    renewed = queue(identity, token, target, uuid4(), uuid4())
    assert renewed.status == "QUEUED" and renewed.attempts == 0


def test_revoked_or_expired_grant_cannot_be_claimed(content):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    identity.logout(token, True, str(uuid4()))
    assert claim_next(identity) is None
    with Session(identity.engine) as db:
        job = db.get(ExportJob, target)
        assert job.status == "FAILED" and job.failure == "AUTH_REQUIRED"
        assert job.grant_family is None
        assert db.scalar(select(ExportGeneration.id)) is None


def test_expired_lease_requeues_without_allowing_late_failure_to_change_new_work(content):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    claim = claim_next(identity)
    now = identity.clock()
    identity.clock = lambda: now + timedelta(seconds=180)
    assert claim_next(identity) is None
    assert status(identity, token, target).status == "QUEUED"
    assert not fail_claim(identity, claim, "AUTH_REQUIRED")
    identity.clock = lambda: now + timedelta(seconds=210)
    assert claim_next(identity).generation_id != claim.generation_id


def test_database_blocks_job_rewrite_and_unbacked_ready_state(content):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    for sql in [
        "DELETE FROM personal_export_jobs",
        "UPDATE personal_export_jobs SET status='READY'",
        "UPDATE personal_export_jobs SET attempts=2",
        "UPDATE personal_export_jobs SET grant_family=gen_random_uuid()",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as db:
            db.execute(text(sql))
    assert status(identity, token, target).status == "QUEUED"


def artifact(identity, claim):
    from services.export_artifacts import write_artifact

    objects = {}
    raw = write_artifact(
        iter([b'{"synthetic":"private"}']),
        identity,
        objects.__setitem__,
        request_id=claim.request_id,
        generation_id=claim.generation_id,
    )
    return raw, objects


def test_publication_is_atomic_once_only_and_retires_temporary_grant(content, monkeypatch):
    from services.domain.data_requests import DataRequest
    from services.export_publication import ExportStopped, publish

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    claim = claim_next(identity)
    raw, _ = artifact(identity, claim)

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic outbox failure")

    with monkeypatch.context() as patch:
        patch.setattr(identity, "event", fail)
        with pytest.raises(RuntimeError, match="Synthetic outbox"):
            publish(identity, claim, raw)
    with Session(identity.engine) as db:
        assert db.get(DataRequest, target).completed_at is None
        assert db.get(ExportGeneration, claim.generation_id).published_at is None
        assert db.get(ExportJob, target).status == "RUNNING"
    publish(identity, claim, raw)
    assert status(identity, token, target).status == "READY"
    with pytest.raises(ExportStopped):
        publish(identity, claim, raw)
    with Session(identity.engine) as db:
        request = db.get(DataRequest, target)
        generation = db.get(ExportGeneration, claim.generation_id)
        job = db.get(ExportJob, target)
        assert request.completed_at == generation.published_at == job.finished_at
        assert request.retention_due_at.year == request.completed_at.year + 6
        assert generation.expires_at == request.completed_at + timedelta(hours=24)
        assert job.grant_family is None and job.grant_authenticated_at is None
        assert identity.decrypt(generation.encrypted_manifest).encode() == raw
    for sql in [
        "UPDATE personal_export_generations SET digest=repeat('0',64)",
        "UPDATE personal_export_jobs SET status='QUEUED'",
        "UPDATE data_subject_requests SET completed_at=completed_at+interval '1 second'",
    ]:
        with pytest.raises(DBAPIError), identity.engine.begin() as db:
            db.execute(text(sql))


def test_snapshot_is_read_only_consistent_and_releases_account_lock(content):
    from sqlalchemy import func

    from services.domain.identity import IdentityEvent
    from services.export_publication import snapshot

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    claim = claim_next(identity)
    query = (
        select(func.count())
        .select_from(IdentityEvent)
        .where(IdentityEvent.user_id == claim.actor_id)
    )
    with snapshot(identity, claim) as reader:
        assert reader.scalar(text("SHOW transaction_isolation")) == "repeatable read"
        assert reader.scalar(text("SHOW transaction_read_only")) == "on"
        count = reader.scalar(query)
        with identity.transaction() as writer:
            # This would timeout if the coordinator retained its account lock while yielding.
            identity.lock(writer, str(claim.actor_id))
            identity.event(writer, claim.actor_id, "synthetic.concurrent", str(uuid4()))
        assert reader.scalar(query) == count
    with Session(identity.engine) as db:
        assert db.scalar(query) == count + 1
        assert db.scalar(text("SHOW transaction_read_only")) == "off"


def test_waiting_snapshot_observes_revocation_committed_before_account_lock(content, monkeypatch):
    from threading import Event

    from sqlalchemy import update

    from services.domain.identity import AuthSession
    from services.export_publication import ExportStopped, snapshot

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    claim = claim_next(identity)
    waiting, original_lock = Event(), identity.lock

    def wait_lock(db, key):
        waiting.set()
        original_lock(db, key)

    def read_snapshot():
        with pytest.raises(ExportStopped, match="AUTH_REQUIRED"):
            with snapshot(identity, claim):
                pytest.fail("A snapshot may not authorize from pre-lock state")

    with ThreadPoolExecutor(max_workers=1) as pool:
        with Session(identity.engine) as db, db.begin():
            original_lock(db, str(claim.actor_id))
            monkeypatch.setattr(identity, "lock", wait_lock)
            future = pool.submit(read_snapshot)
            assert waiting.wait(timeout=1)
            db.execute(
                update(AuthSession)
                .where(AuthSession.family == claim.family)
                .values(revoked_at=identity.clock())
            )
        future.result(timeout=3)


def test_revocation_after_snapshot_prevents_publication(content):
    from services.domain.data_requests import DataRequest
    from services.export_publication import ExportStopped, publish, snapshot

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    claim = claim_next(identity)
    with snapshot(identity, claim):
        raw, _ = artifact(identity, claim)
        identity.logout(token, True, str(uuid4()))
    with pytest.raises(ExportStopped, match="AUTH_REQUIRED"):
        publish(identity, claim, raw)
    with Session(identity.engine) as db:
        assert db.get(DataRequest, target).completed_at is None
        assert db.get(ExportGeneration, claim.generation_id).published_at is None


def test_database_refuses_generation_publication_without_atomic_request_completion(content):
    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    claim = claim_next(identity)
    raw, _ = artifact(identity, claim)
    with pytest.raises(DBAPIError, match="requires atomic completion"):
        with Session(identity.engine) as db, db.begin():
            generation = db.get(ExportGeneration, claim.generation_id)
            generation.published_at = identity.clock()
            generation.expires_at = identity.clock() + timedelta(hours=24)
            generation.encrypted_manifest = identity.encrypt(raw.decode())
            generation.digest = "0" * 64
            generation.size = 1
    with Session(identity.engine) as db:
        assert db.get(ExportGeneration, claim.generation_id).published_at is None


class MemoryStore:
    def __init__(self):
        self.objects = {}

    def put(self, generation, object_id, ciphertext):
        self.objects[generation, object_id] = ciphertext

    def get(self, generation, object_id):
        return self.objects[generation, object_id]


def test_large_history_exceeds_both_synchronous_caps_and_publishes_complete_snapshot(content):
    import json

    from sqlalchemy import func

    from services.data_exports import MAX_BYTES as SYNC_BYTES
    from services.domain.identity import IdentityEvent
    from services.export_artifacts import read_artifact
    from services.export_processing import process_one

    identity, _, _, token, target = setup_job(content)
    queued = queue(identity, token, target, uuid4(), uuid4())
    with identity.transaction() as db:
        actor = identity.authenticate(db, token).user_id
        for _ in range(12_000):
            identity.event(db, actor, "synthetic.large." + "x" * 200, str(uuid4()))
    with Session(identity.engine) as db:
        expected_events = db.scalar(
            select(func.count()).select_from(IdentityEvent).where(IdentityEvent.user_id == actor)
        )
    store = MemoryStore()
    assert process_one(identity, store)
    view = status(identity, token, target)
    assert view.status == "READY" and view.size_bytes > SYNC_BYTES and queued.status == "QUEUED"
    with Session(identity.engine) as db:
        generation = db.get(ExportGeneration, db.get(ExportJob, target).generation_id)
        raw = b"".join(
            read_artifact(
                identity.decrypt(generation.encrypted_manifest).encode(),
                identity,
                lambda object_id: store.get(generation.id, object_id),
                request_id=target,
                generation_id=generation.id,
            )
        )
        bundle = json.loads(raw)
        assert len(raw) == view.size_bytes
        assert len(bundle["records"]["account_events"]) == expected_events > 10_000
        assert bundle["request_id"] == str(target)
        assert len(bundle["records"]["export_jobs"]) == 1
        assert bundle["records"]["export_jobs"][0]["status"] == "RUNNING"
        assert len(bundle["records"]["export_copies"]) == 1
        for hidden in [
            "grant_family",
            "grant_authenticated_at",
            "encrypted_manifest",
            "generation_id",
        ]:
            assert hidden not in raw.decode()
    assert not process_one(identity, store)


@pytest.mark.parametrize("failure", ["ambiguous_upload", "corrupt_readback", "revoked"])
def test_worker_never_completes_partial_or_unverified_generation(content, failure):
    from services.domain.data_requests import DataRequest
    from services.export_processing import process_one

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())

    class BrokenStore(MemoryStore):
        def put(self, generation, object_id, ciphertext):
            super().put(generation, object_id, ciphertext)
            if failure == "ambiguous_upload":
                raise RuntimeError("Synthetic upload acknowledgement lost")
            if failure == "revoked":
                identity.logout(token, True, str(uuid4()))

        def get(self, generation, object_id):
            return (
                b"corrupt" if failure == "corrupt_readback" else super().get(generation, object_id)
            )

    store = BrokenStore()
    assert not process_one(identity, store)
    assert store.objects  # These private unpublished objects must be swept by the lifecycle.
    with Session(identity.engine) as db:
        assert db.get(DataRequest, target).completed_at is None
        assert db.scalar(select(ExportGeneration.published_at)) is None
        job = db.get(ExportJob, target)
        assert job.status == ("FAILED" if failure == "revoked" else "QUEUED")
        assert job.failure == ("AUTH_REQUIRED" if failure == "revoked" else "PROCESSING_FAILED")


def test_cooperative_deadline_and_byte_exhaustion_are_terminal_not_partial(content, monkeypatch):
    import services.export_processing as processing
    from services.domain.data_requests import DataRequest

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    times = iter([0, 90])
    store = MemoryStore()
    assert not processing.process_one(identity, store, timer=lambda: next(times))
    assert status(identity, token, target).failure == "LIMIT_REACHED"
    assert not store.objects
    queue(identity, token, target, uuid4(), uuid4())
    monkeypatch.setattr(processing, "MAX_BYTES", 1)
    assert not processing.process_one(identity, store)
    view = status(identity, token, target)
    assert view.status == "FAILED" and view.failure == "LIMIT_REACHED"
    assert not store.objects
    with Session(identity.engine) as db:
        assert db.get(DataRequest, target).completed_at is None


class SweepStore(MemoryStore):
    scope = "0" * 64

    def __init__(self, identity):
        super().__init__()
        self.identity, self.times = identity, {}

    def put(self, generation, object_id, ciphertext):
        super().put(generation, object_id, ciphertext)
        self.times[generation, object_id] = self.identity.clock()

    def remove(self, generation, object_id):
        self.objects.pop((generation, object_id), None)
        self.times.pop((generation, object_id), None)

    def page(self, *, generation=None, after=None, limit=100):
        from services.export_storage import StoredExportObject

        rows = [
            StoredExportObject(g, o, self.times[g, o], self.scope)
            for g, o in self.objects
            if generation is None or g == generation
        ]
        return [r for r in sorted(rows, key=lambda r: r.key) if after is None or r.key > after][
            :limit
        ]


def test_expiry_cleans_only_disposable_copy_and_preserves_request_accountability(content):
    from services.domain.data_requests import DataRequest
    from services.export_cleanup import sweep
    from services.export_processing import process_one

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    store = SweepStore(identity)
    assert process_one(identity, store)
    assert sweep(identity, store).removed == 0
    assert store.objects
    with Session(identity.engine) as db:
        completed = db.get(DataRequest, target).completed_at
        digest = db.get(DataRequest, target).export_digest
    now = identity.clock()
    identity.clock = lambda: now + timedelta(days=2)
    result = sweep(identity, store)
    assert result.removed >= 1 and result.generations == 1 and result.failures == 0
    assert not store.objects
    with Session(identity.engine) as db:
        assert db.get(ExportJob, target).status == "EXPIRED"
        assert db.scalar(select(ExportGeneration.id)) is None
        request = db.get(DataRequest, target)
        assert request.completed_at == completed and request.export_digest == digest
        assert request.retention_due_at.year == completed.year + 6
    again = sweep(identity, store)
    assert again.removed == again.generations == again.failures == 0


def test_unpublished_cleanup_and_late_orphan_scan_preserve_live_generation(content):
    from services.export_cleanup import sweep

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    old = claim_next(identity)
    store = SweepStore(identity)
    object_id = uuid4()
    store.put(old.generation_id, object_id, b"synthetic encrypted bytes")
    now = identity.clock()
    identity.clock = lambda: now + timedelta(seconds=180)
    result = sweep(identity, store)
    assert result.removed == result.generations == 1 and result.failures == 0
    store.put(old.generation_id, object_id, b"late acknowledgement after registry cleanup")
    identity.clock = lambda: now + timedelta(seconds=210)
    current = claim_next(identity)
    live_object = uuid4()
    store.put(current.generation_id, live_object, b"live private bytes")
    assert sweep(identity, store).removed == 0  # New unknown objects receive the bounded grace.
    identity.clock = lambda: now + timedelta(seconds=360)
    result = sweep(identity, store, orphan_first=True)
    assert (old.generation_id, object_id) not in store.objects
    assert (current.generation_id, live_object) in store.objects
    assert result.failures == 0 and result.removed == 1 and result.generations == 0


def test_cleanup_storage_failure_keeps_metadata_for_retry(content):
    from services.export_cleanup import sweep
    from services.export_processing import process_one

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())

    class Broken(SweepStore):
        broken = True

        def remove(self, generation, object_id):
            if self.broken:
                raise RuntimeError("synthetic private storage diagnostics")
            super().remove(generation, object_id)

    store = Broken(identity)
    assert process_one(identity, store)
    now = identity.clock()
    identity.clock = lambda: now + timedelta(days=2)
    result = sweep(identity, store)
    assert result.failures == 1 and result.removed == 0 and store.objects
    with Session(identity.engine) as db:
        assert db.get(ExportJob, target).status == "EXPIRED"
        assert db.scalar(select(ExportGeneration.id)) is not None
    store.broken = False
    result = sweep(identity, store)
    assert result.failures == 0 and result.generations == 1 and not store.objects


def test_orphan_scan_is_bounded_resumable_and_ignores_recent_objects(content):
    from services.export_cleanup import sweep

    identity, *_ = content
    store = SweepStore(identity)
    for _ in range(35):
        store.put(uuid4(), uuid4(), b"synthetic orphan")
    now = identity.clock()
    identity.clock = lambda: now + timedelta(seconds=181)
    fresh = (uuid4(), uuid4())
    store.put(*fresh, b"recent private object")
    cursor, order = None, True
    removed = 0
    for _ in range(10):
        result = sweep(identity, store, cursor=cursor, orphan_first=order)
        assert result.removed <= 20 and result.examined <= 100 and result.failures == 0
        cursor, order = result.cursor, result.orphan_first
        removed += result.removed
        if removed == 35:
            break
    assert removed == 35 and set(store.objects) == {fresh}


def test_download_rechecks_owner_revocation_and_frozen_integrity(content):
    import json
    from contextlib import closing

    from services.export_downloads import prepare
    from services.export_processing import process_one

    identity, _, actors, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    with identity.transaction() as db:
        actor = identity.authenticate(db, token).user_id
        for _ in range(500):
            identity.event(db, actor, "synthetic.stream." + "x" * 200, str(uuid4()))
    store = SweepStore(identity)
    assert process_one(identity, store)
    first = prepare(identity, store, token, target)
    raw = b"".join(first.chunks)
    assert len(raw) == first.size and json.loads(raw)["request_id"] == str(target)
    assert b"".join(prepare(identity, store, token, target).chunks) == raw
    for role in ["admin", "other"]:
        with pytest.raises(IdentityError, match="RESOURCE_NOT_FOUND"):
            prepare(identity, store, actors[role]["Authorization"][7:], target)
    with closing(prepare(identity, store, token, target).chunks) as source:
        assert next(source)
        identity.logout(token, True, str(uuid4()))
        with pytest.raises(RuntimeError, match="transfer incomplete"):
            next(source)


def test_corrupt_or_expired_copy_cannot_complete_download(content):
    from services.export_downloads import prepare
    from services.export_processing import process_one
    from tests.integration.test_data_exports import fresh

    identity, _, _, token, target = setup_job(content)
    queue(identity, token, target, uuid4(), uuid4())
    store = SweepStore(identity)
    assert process_one(identity, store)
    key = next(iter(store.objects))
    store.objects[key] = b"corrupt synthetic ciphertext"
    with pytest.raises(RuntimeError, match="transfer incomplete"):
        b"".join(prepare(identity, store, token, target).chunks)
    now = identity.clock()
    identity.clock = lambda: now + timedelta(days=2)
    token = fresh(identity)["Authorization"][7:]
    with pytest.raises(IdentityError, match="EXPORT_EXPIRED"):
        prepare(identity, store, token, target)


def test_cleanup_rejects_foreign_namespace_callback_output_without_removal(content):
    from services.export_cleanup import sweep
    from services.export_storage import StoredExportObject

    identity, *_ = content

    class Foreign(SweepStore):
        def page(self, **kwargs):
            return [
                StoredExportObject(uuid4(), uuid4(), identity.clock() - timedelta(days=1), "f" * 64)
            ]

        def remove(self, *args):
            pytest.fail("Foreign storage scope must never grant deletion authority")

    result = sweep(identity, Foreign(identity))
    assert result.failures == 1 and result.removed == result.generations == 0
