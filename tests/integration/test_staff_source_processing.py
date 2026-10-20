"""FR-ID-006/GRD-009: staff gates precede learner-owned source row locks."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from tests.integration.test_assessment import assessment as assessment_fixture

assessment = assessment_fixture
pytestmark = pytest.mark.integration


def assert_staff_waits_before_row_lock(
    service, monkeypatch, module, subject, model, target, action
):
    """An exclusive subject gate must win before staff holds any target row lock."""
    from services.account_processing import coordinate
    from tests.integration.test_account_processing import EXCLUSIVE, wait_for_gate

    reached = Event()
    backend = []

    def observed(db, owner):
        assert owner == subject
        backend.append(db.scalar(text("SELECT pg_backend_pid()")))
        reached.set()
        coordinate(db, owner)

    monkeypatch.setattr(module, "coordinate", observed, raising=False)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with Session(service.engine) as db, db.begin():
            assert db.scalar(EXCLUSIVE, {"subject": subject}) is True
            future = pool.submit(action)
            assert reached.wait(5), "Staff operation bypassed subject processing coordination"
            wait_for_gate(service.engine, backend[0], future)
            # NOWAIT exposes reversed case/flag-before-gate ordering without timing sleeps.
            db.scalar(select(model).where(model.id == target).with_for_update(nowait=True))
            assert db.scalar(EXCLUSIVE, {"subject": uuid4()}) is True
        result = future.result(timeout=5)
    assert result.status_code in {200, 201}, result.text


@pytest.mark.parametrize("operation", ["HOLD_CREATE", "HOLD_RELEASE", "CLAIM", "PREVIEW"])
def test_staff_case_changes_coordinate_before_case_row_lock(content, monkeypatch, operation):
    from services import data_requests, deletion_preview, legal_holds
    from services.domain.data_requests import DataRequest
    from tests.integration.test_data_requests import claim
    from tests.integration.test_legal_holds import hold, prepare, release

    service, client, actors, *_ = content
    target, body = prepare(content)
    with Session(service.engine) as db:
        subject = db.get(DataRequest, UUID(target)).user_id
    module = legal_holds
    if operation == "HOLD_CREATE":

        def action():
            return hold(client, actors["admin"], target, body)
    elif operation == "HOLD_RELEASE":
        created = hold(client, actors["admin"], target, body)
        assert created.status_code == 201

        def action():
            return release(client, actors["admin"], target, created.json()["id"])
    elif operation == "PREVIEW":
        module = deletion_preview

        def action():
            return client.get(
                f"/api/v1/admin/data-requests/{target}/deletion-preview", headers=actors["admin"]
            )
    else:
        module = data_requests

        def action():
            return claim(client, actors["admin"], target)

    assert_staff_waits_before_row_lock(
        service, monkeypatch, module, subject, DataRequest, UUID(target), action
    )


@pytest.mark.parametrize("operation", ["DETAIL", "TRIAGE"])
def test_staff_flag_work_coordinates_before_flag_row_lock(assessment, monkeypatch, operation):
    from services import flags
    from services.domain.flags import ContentFlag
    from tests.integration.test_flags import report, saved, triage

    service, client, actors, *_ = assessment
    grade = saved(assessment)
    created = report(client, actors["learner"], grade["attempt_id"])
    assert created.status_code == 201
    target = UUID(created.json()["id"])
    with Session(service.engine) as db:
        subject = db.get(ContentFlag, target).reporter_id

    def action():
        if operation == "DETAIL":
            return client.get(f"/api/v1/admin/content-flags/{target}", headers=actors["reviewer"])
        return triage(client, actors["reviewer"], {"id": str(target), "revision": 1})

    assert_staff_waits_before_row_lock(
        service, monkeypatch, flags, subject, ContentFlag, target, action
    )
