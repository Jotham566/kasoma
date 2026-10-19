"""ADR-060 additive exact holds never grant retirement or change retry identity."""

import os
import subprocess
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.data_requests import DataRequestReceipt
from services.export_cleanup import sweep
from services.export_jobs import queue
from services.export_processing import process_one
from tests.integration.test_data_requests import create
from tests.integration.test_export_jobs import SweepStore
from tests.integration.test_legal_holds import hold, path, prepare, release

pytestmark = pytest.mark.integration


def references(client, headers, case, source, query=""):
    return client.get(f"{path(case)}/export-sources/{source}{query}", headers=headers)


def sources(content):
    identity, client, actors, _ = content
    case, body = prepare(content)
    source = create(client, actors["learner"]).json()["id"]
    return case, body, source


def test_exact_receipt_gate_retry_release_and_no_delete_authority(content):
    identity, client, actors, _ = content
    case, body, source = sources(content)
    page = references(client, actors["admin"], case, source)
    assert page.status_code == 200, page.text
    assert page.headers["cache-control"] == "no-store"
    assert set(page.json()) == {"receipt_ids", "next_cursor", "export_job_id"}
    receipt = page.json()["receipt_ids"][0]
    assert page.json()["export_job_id"] is None
    value = body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": receipt}
    assert hold(client, actors["admin"], case, value).status_code == 409
    identity.settings.export_evidence_holds_enabled = True
    key = str(uuid4())
    result = hold(client, actors["admin"], case, value, key)
    assert result.status_code == 201, result.text
    assert result.json()["status"] == "ACTIVE"
    assert hold(client, actors["admin"], case, value, key).json() == result.json()
    assert (
        hold(
            client, actors["admin"], case, value | {"reason": "SECURITY_INVESTIGATION"}, key
        ).status_code
        == 409
    )
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="legally held"):
        db.execute(text("DELETE FROM data_request_receipts WHERE id=:id"), {"id": receipt})
    identity.settings.export_evidence_holds_enabled = False
    listing = client.get(path(case), headers=actors["admin"]).json()
    assert "DATA_REQUEST_RECEIPT" not in listing["supported_record_types"]
    assert listing["data"][0]["id"] == result.json()["id"]
    assert release(client, actors["admin"], case, result.json()["id"]).status_code == 200
    for statement in [
        "DELETE FROM data_request_receipts WHERE id=:id",
        "UPDATE data_request_receipts SET id=gen_random_uuid() WHERE id=:id",
    ]:
        with identity.engine.begin() as db, pytest.raises(DBAPIError, match="append-only"):
            db.execute(text(statement), {"id": receipt})
    with Session(identity.engine) as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(DataRequestReceipt)
                .where(DataRequestReceipt.id == UUID(receipt))
            )
            == 1
        )


def test_lookup_and_holds_require_exact_owner_claim_recent_admin(content):
    identity, client, actors, _ = content
    case, body, source = sources(content)
    identity.settings.export_evidence_holds_enabled = True
    own = references(client, actors["admin"], case, source).json()["receipt_ids"][0]
    foreign = create(client, actors["other"]).json()["id"]
    for denied in [foreign, case, str(uuid4())]:
        assert references(client, actors["admin"], case, denied).status_code == 404
    for role in ["learner", "support", "author", "other"]:
        assert references(client, actors[role], case, source).status_code == 403
    assert references(client, {}, case, source).status_code == 401
    assert references(client, actors["admin"], case, source, "?limit=51").status_code == 422
    foreign_case = create(client, actors["other"], "DELETE").json()["id"]
    from tests.integration.test_data_requests import claim

    assert claim(client, actors["admin"], foreign_case).status_code == 200
    assert (
        hold(
            client,
            actors["admin"],
            foreign_case,
            body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": own},
        ).status_code
        == 404
    )
    deletion_receipt = references(client, actors["admin"], case, source).json()
    assert deletion_receipt["next_cursor"] is None
    now = identity.clock()
    identity.clock = lambda: now + timedelta(minutes=10)
    assert references(client, actors["admin"], case, source).status_code == 401


def test_stable_bounded_pagination_excludes_retry_material(content):
    identity, client, actors, _ = content
    case, _, source = sources(content)
    with Session(identity.engine) as db:
        original = db.scalar(
            select(DataRequestReceipt).where(DataRequestReceipt.request_id == UUID(source))
        )
        owner, digest = original.actor_id, original.request_hash
    with identity.engine.begin() as db:
        for _ in range(104):
            db.execute(
                text(
                    "INSERT INTO data_request_receipts(actor_id,key,request_hash,request_id) "
                    "VALUES(:actor,:key,:hash,:source)"
                ),
                {"actor": owner, "key": uuid4(), "hash": digest, "source": source},
            )
    ids, cursor = [], None
    for count in [50, 50, 5]:
        page = references(
            client,
            actors["admin"],
            case,
            source,
            "?limit=50" + (f"&cursor={cursor}" if cursor else ""),
        ).json()
        assert len(page["receipt_ids"]) == count
        ids.extend(page["receipt_ids"])
        cursor = page["next_cursor"]
        assert "request_hash" not in page and "key" not in page
    assert cursor is None and len(set(ids)) == 105 and ids == sorted(ids)


def clear_job(content, source):
    identity, _, actors, _ = content
    token = actors["learner"]["Authorization"][7:]
    queue(identity, token, UUID(source), uuid4(), uuid4())
    store = SweepStore(identity)
    assert process_one(identity, store)
    now = identity.clock()
    identity.clock = lambda: now + timedelta(days=2)
    assert sweep(identity, store).generations == 1
    identity.clock = lambda: now


def test_only_cleared_expired_job_is_holdable_and_guards_remain_after_release(content):
    identity, client, actors, _ = content
    case, body, source = sources(content)
    identity.settings.export_evidence_holds_enabled = True
    value = body | {"record_type": "EXPORT_JOB_RECEIPT", "record_id": source}
    token = actors["learner"]["Authorization"][7:]
    queue(identity, token, UUID(source), uuid4(), uuid4())
    assert hold(client, actors["admin"], case, value).status_code == 404
    store = SweepStore(identity)
    assert process_one(identity, store)
    assert references(client, actors["admin"], case, source).json()["export_job_id"] is None
    assert hold(client, actors["admin"], case, value).status_code == 404
    now = identity.clock()
    identity.clock = lambda: now + timedelta(days=2)
    assert sweep(identity, store).generations == 1
    identity.clock = lambda: now
    assert references(client, actors["admin"], case, source).json()["export_job_id"] == source
    held = hold(client, actors["admin"], case, value)
    assert held.status_code == 201, held.text
    with identity.engine.begin() as db, pytest.raises(DBAPIError, match="legally held"):
        db.execute(text("DELETE FROM personal_export_jobs WHERE request_id=:id"), {"id": source})
    assert release(client, actors["admin"], case, held.json()["id"]).status_code == 200
    with (
        identity.engine.begin() as db,
        pytest.raises(DBAPIError, match="accountability is retained"),
    ):
        db.execute(text("DELETE FROM personal_export_jobs WHERE request_id=:id"), {"id": source})


@pytest.mark.parametrize("identity", ["0038", "0039"], indirect=True)
def test_populated_upgrade_preserves_composite_retry_binding_and_assigns_stable_ids(content):
    identity, client, actors, _ = content
    key = str(uuid4())
    saved = create(client, actors["learner"], key=key)
    assert saved.status_code == 201, saved.text
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            capture_output=True,
            env=os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()},
        )
        assert create(client, actors["learner"], key=key).json() == saved.json()
        with Session(identity.engine) as db:
            receipt = db.scalar(select(DataRequestReceipt))
            assert receipt.id is not None
            reference = receipt.id
    with identity.engine.connect() as db:
        assert (
            db.scalar(text("SELECT id FROM data_request_receipts WHERE key=:key"), {"key": key})
            == reference
        )
        assert db.scalar(
            text(
                """SELECT array_agg(a.attname ORDER BY k.ord) FROM pg_index i
                    CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY k(attnum,ord)
                    JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=k.attnum
                    WHERE i.indrelid='data_request_receipts'::regclass AND i.indisprimary"""
            )
        ) == ["actor_id", "key"]


def test_sql_rejects_foreign_missing_and_delete_receipts_independently(content):
    from services.domain.data_requests import LegalHold

    identity, client, actors, _ = content
    case, body, source = sources(content)
    identity.settings.export_evidence_holds_enabled = True
    record = references(client, actors["admin"], case, source).json()["receipt_ids"][0]
    valid = hold(
        client,
        actors["admin"],
        case,
        body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": record},
    ).json()
    foreign = create(client, actors["other"]).json()["id"]
    with Session(identity.engine) as db:
        foreign_receipt = db.scalar(
            select(DataRequestReceipt.id).where(DataRequestReceipt.request_id == UUID(foreign))
        )
        deletion_receipt = db.scalar(
            select(DataRequestReceipt.id).where(
                DataRequestReceipt.request_id == UUID(case),
                DataRequestReceipt.actor_id
                != UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"]),
            )
        )
        held = db.get(LegalHold, UUID(valid["id"]))
        values = {column.name: getattr(held, column.name) for column in LegalHold.__table__.columns}
    for kind, ref in [
        ("DATA_REQUEST_RECEIPT", foreign_receipt),
        ("DATA_REQUEST_RECEIPT", deletion_receipt),
        ("DATA_REQUEST_RECEIPT", uuid4()),
        ("EXPORT_JOB_RECEIPT", UUID(source)),
    ]:
        with (
            Session(identity.engine) as db,
            pytest.raises(DBAPIError, match="must belong to requester"),
        ):
            db.add(LegalHold(**(values | {"id": uuid4(), "record_type": kind, "record_id": ref})))
            db.commit()


def test_hold_atomicity_exact_scope_and_wall_clock_expiry(content, monkeypatch):
    from services.domain.data_requests import LegalHold
    from services.legal_holds import active

    identity, client, actors, _ = content
    case, body, source = sources(content)
    assert create(client, actors["learner"]).json()["id"] == source
    refs = references(client, actors["admin"], case, source).json()["receipt_ids"]
    assert len(refs) == 2
    identity.settings.export_evidence_holds_enabled = True
    value = body | {"record_type": "DATA_REQUEST_RECEIPT", "record_id": refs[0]}
    original = identity.event

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic hold evidence failure")

    monkeypatch.setattr(identity, "event", fail)
    assert hold(client, actors["admin"], case, value).status_code == 500
    with Session(identity.engine) as db:
        assert db.scalar(select(func.count()).select_from(LegalHold)) == 0
    monkeypatch.setattr(identity, "event", original)
    held = hold(client, actors["admin"], case, value)
    assert held.status_code == 201, held.text
    with Session(identity.engine) as db:
        at = db.scalar(select(func.clock_timestamp()))
        assert active(db, "DATA_REQUEST_RECEIPT", UUID(refs[0]), at)
        assert not active(db, "DATA_REQUEST_RECEIPT", UUID(refs[1]), at)
        assert not active(db, "DATA_REQUEST", UUID(source), at)
        row = db.get(LegalHold, UUID(held.json()["id"]))
        assert not active(db, "DATA_REQUEST_RECEIPT", UUID(refs[0]), row.expires_at)


def test_staff_claim_receipt_ownership_follows_export_subject_not_staff_actor(content):
    from tests.integration.test_data_requests import claim

    identity, client, actors, _ = content
    case, body, source = sources(content)
    assert claim(client, actors["admin"], source).status_code == 200
    identity.settings.export_evidence_holds_enabled = True
    with Session(identity.engine) as db:
        staff = UUID(client.get("/api/v1/me", headers=actors["admin"]).json()["id"])
        record = db.scalar(
            select(DataRequestReceipt.id).where(
                DataRequestReceipt.request_id == UUID(source),
                DataRequestReceipt.actor_id == staff,
            )
        )
    refs = references(client, actors["admin"], case, source).json()["receipt_ids"]
    assert len(refs) == 2 and str(record) in refs
    assert (
        hold(
            client,
            actors["admin"],
            case,
            body
            | {
                "record_type": "DATA_REQUEST_RECEIPT",
                "record_id": str(record),
            },
        ).status_code
        == 201
    )
