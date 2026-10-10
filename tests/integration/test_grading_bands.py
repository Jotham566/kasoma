"""Synthetic metadata and real SQL guards; no genuine approval or scoring enablement."""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from services.domain.curriculum import Topic
from services.domain.grading_bands import GradingBandHistory, GradingBandRow
from services.grading_band_store import disable, locked, register, snapshot
from services.seed import seed
from services.short_text_eligibility import CalibrationBand, GradingScope

pytestmark = pytest.mark.integration


@pytest.fixture
def catalog(identity):
    service, _, _, _ = identity
    seed(service.settings)
    with Session(service.engine) as db:
        topic = db.scalar(select(Topic).order_by(Topic.id))
        scope = GradingScope(
            subject_id=topic.subject_id,
            topic_id=topic.id,
            language="en",
            model_version="fake-v1",
            prompt_version="synthetic-v2",
            configuration_version="test-v1",
        )
    band = CalibrationBand(
        id=uuid4(),
        scope=scope,
        minimum_characters=1,
        maximum_characters=2000,
        benchmark_id=uuid4(),
        report_sha256="a" * 64,
        benchmark_cases=100,
        benchmark_within_tolerance=85,
        held_out_cases=20,
        held_out_exact=18,
        critical_errors=0,
        subgroup_review="APPROVED",
        approval_id=uuid4(),
        approved_at=service.clock(),
    )
    with Session(service.engine) as db, db.begin():
        register(db, band, service.clock())
    return service, band


def activate_synthetic(db, band, now):
    # Exercise the owner-only storage transition. No activation application command
    # exists, and this metadata is not proof of real academic approval.
    assert db.scalar(text("SELECT current_schema()")).startswith("identity_test_")
    db.execute(
        text("""UPDATE grading_bands SET enabled=true, activated_at=:now,
        updated_at=:now, revision=revision+1 WHERE id=:id"""),
        {"id": band.id, "now": now},
    )


def test_registration_is_disabled_and_exact_history_is_automatic(catalog):
    service, band = catalog
    with Session(service.engine) as db:
        row = locked(db, band.id)
        assert snapshot(row) == band
        assert not row.enabled and row.activated_at is None
        history = db.scalar(select(GradingBandHistory))
        assert history.snapshot["id"] == str(band.id)
        assert history.snapshot["report_sha256"] == band.report_sha256
        assert history.revision == 1
    with Session(service.engine) as db:
        with pytest.raises(ValueError, match="cannot enable"):
            register(db, band.model_copy(update={"id": uuid4(), "enabled": True}), service.clock())
        with pytest.raises(ValueError, match="timezone"):
            register(db, band, service.clock().replace(tzinfo=None))


def test_sticky_disable_and_exact_replay_survive_new_transactions(catalog):
    service, band = catalog
    now = service.clock()
    with Session(service.engine) as db, db.begin():
        activate_synthetic(db, band, now)
    with Session(service.engine) as db, db.begin():
        assert disable(db, band.id, now + timedelta(seconds=1), "CRITICAL_ERROR")
    with Session(service.engine) as db, db.begin():
        assert not disable(db, band.id, now + timedelta(seconds=2), "MANUAL")
        row = locked(db, band.id)
        assert not snapshot(row).enabled
        assert row.revision == 3 and row.disable_reason == "CRITICAL_ERROR"
        assert row.disabled_at == now + timedelta(seconds=1)
        history = list(db.scalars(select(GradingBandHistory).order_by(GradingBandHistory.revision)))
        assert [h.snapshot["enabled"] for h in history] == [False, True, False]
    with pytest.raises(DBAPIError):
        with Session(service.engine) as db, db.begin():
            activate_synthetic(db, band, now + timedelta(seconds=3))


def test_only_one_concurrent_disable_transition(catalog):
    service, band = catalog

    def stop(_):
        with Session(service.engine) as db, db.begin():
            return disable(db, band.id, service.clock(), "MANUAL")

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(stop, range(2))) == [False, True]
    with Session(service.engine) as db:
        assert db.scalar(select(func.count()).select_from(GradingBandHistory)) == 2


def test_locked_snapshot_refreshes_stale_identity_map_and_serializes(catalog):
    service, band = catalog
    with Session(service.engine) as db, db.begin():
        activate_synthetic(db, band, service.clock())
    with Session(service.engine) as stale:
        cached = stale.get(GradingBandRow, band.id)
        assert cached.enabled
        with Session(service.engine) as other, other.begin():
            disable(other, band.id, service.clock(), "AUDIT_AGREEMENT")
        assert not locked(stale, band.id).enabled
        with pytest.raises(DBAPIError) as caught:
            with Session(service.engine) as other, other.begin():
                other.execute(
                    select(GradingBandRow)
                    .where(GradingBandRow.id == band.id)
                    .with_for_update(nowait=True)
                )
        assert caught.value.orig.sqlstate == "55P03"


def test_rollback_includes_history_and_metadata_cannot_be_rewritten(catalog):
    service, band = catalog
    with Session(service.engine) as db:
        disable(db, band.id, service.clock(), "MANUAL")
        db.rollback()
    with Session(service.engine) as db:
        assert locked(db, band.id).disabled_at is None
        assert db.scalar(select(func.count()).select_from(GradingBandHistory)) == 1
    for sql in (
        "INSERT INTO grading_bands SELECT (jsonb_populate_record(NULL::grading_bands, "
        "to_jsonb(b)||jsonb_build_object('id',gen_random_uuid(),'enabled',true,"
        "'activated_at',updated_at))).* FROM grading_bands b WHERE id=:id",
        "UPDATE grading_bands SET held_out_exact=19 WHERE id=:id",
        "UPDATE grading_bands SET revision=revision+1 WHERE id=:id",
        "DELETE FROM grading_bands WHERE id=:id",
        "UPDATE grading_band_history SET snapshot=snapshot WHERE band_id=:id",
        "DELETE FROM grading_band_history WHERE band_id=:id",
        "INSERT INTO grading_band_history(band_id,revision,snapshot) VALUES(:id,2,'{}')",
    ):
        with pytest.raises(DBAPIError):
            with Session(service.engine) as db, db.begin():
                db.execute(text(sql), {"id": band.id})


@pytest.mark.parametrize(
    "changed",
    [
        {"approval_id": None, "approved_at": None},
        {"held_out_exact": 17},
        {"benchmark_within_tolerance": 84},
        {"critical_errors": 1},
        {"subgroup_review": "HARMFUL"},
    ],
)
def test_sql_activation_cannot_bypass_calibration_requirements(catalog, changed):
    service, original = catalog
    band = original.model_copy(update={"id": uuid4(), **changed})
    with Session(service.engine) as db, db.begin():
        register(db, band, service.clock())
    with pytest.raises(DBAPIError):
        with Session(service.engine) as db, db.begin():
            activate_synthetic(db, band, service.clock())


def test_registration_scope_and_approval_time_are_database_constraints(catalog):
    service, original = catalog
    with Session(service.engine) as db:
        foreign = db.scalar(select(Topic).where(Topic.subject_id != original.scope.subject_id))
    for change in (
        {"scope": original.scope.model_copy(update={"topic_id": foreign.id})},
        {"approved_at": service.clock() + timedelta(seconds=1)},
    ):
        with pytest.raises(DBAPIError):
            with Session(service.engine) as db, db.begin():
                register(db, original.model_copy(update={"id": uuid4(), **change}), service.clock())


def test_topic_cannot_move_to_another_subject_after_band_registration(catalog):
    service, band = catalog
    with Session(service.engine) as db:
        foreign = db.scalar(select(Topic).where(Topic.subject_id != band.scope.subject_id))
    with pytest.raises(DBAPIError):
        with Session(service.engine) as db, db.begin():
            db.execute(
                text("UPDATE topics SET subject_id=:subject WHERE id=:topic"),
                {"subject": foreign.subject_id, "topic": band.scope.topic_id},
            )


@pytest.mark.parametrize("identity", ["0028"], indirect=True)
def test_scope_upgrade_preserves_populated_band_and_history(catalog):
    service, band = catalog
    env = os.environ | {"DATABASE_URL": service.settings.database_url.get_secret_value()}
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            env=env,
            check=True,
            capture_output=True,
        )
    with Session(service.engine) as db:
        assert snapshot(locked(db, band.id)) == band
        assert db.scalar(select(func.count()).select_from(GradingBandHistory)) == 1
    test_topic_cannot_move_to_another_subject_after_band_registration(catalog)
