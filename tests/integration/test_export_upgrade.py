"""Migration 0025 preserves pre-existing frozen exports and pending requests."""

import os
import subprocess
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from services import data_exports
from services.data_request_contracts import DataExportBundle
from services.domain.data_requests import DataExport, DataRequest
from services.export_jobs import queue
from services.export_processing import process_one
from tests.integration.test_data_exports import export
from tests.integration.test_data_requests import create
from tests.integration.test_export_jobs import SweepStore

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("identity", ["0024"], indirect=True)
def test_upgrade_preserves_frozen_legacy_bytes_and_accepts_new_async_job(content, monkeypatch):
    identity, client, actors, _ = content
    headers = actors["learner"]
    completed = UUID(create(client, headers).json()["id"])

    def legacy_projection(identity, db, actor, target, *, max_bytes):
        # Valid original v1 envelope, before job/copy sections existed.
        yield (
            DataExportBundle(
                request_id=target,
                generated_at=identity.clock(),
                exclusions=["Synthetic original-format fixture"],
                records={"identity_events": []},
            )
            .model_dump_json()
            .encode()
        )

    with monkeypatch.context() as patch:
        patch.setattr(data_exports, "encoded_project", legacy_projection)
        original = export(client, headers, str(completed))
    assert original.status_code == 200
    pending = UUID(create(client, headers).json()["id"])
    with Session(identity.engine) as db:
        ciphertext = db.get(DataExport, completed).encrypted_payload
        digest = db.get(DataRequest, completed).export_digest

    env = os.environ | {"DATABASE_URL": identity.settings.database_url.get_secret_value()}
    for _ in range(2):
        subprocess.run(
            ["uv", "run", "--frozen", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            check=True,
            env=env,
            capture_output=True,
        )
    replay = export(client, headers, str(completed))
    assert replay.status_code == 200 and replay.json() == original.json()
    with Session(identity.engine) as db:
        assert db.get(DataExport, completed).encrypted_payload == ciphertext
        assert db.get(DataRequest, completed).export_digest == digest
        assert db.get(DataRequest, pending).completed_at is None
    token = headers["Authorization"][7:]
    queue(identity, token, pending, uuid4(), uuid4())
    assert process_one(identity, SweepStore(identity))
    with Session(identity.engine) as db:
        assert db.get(DataRequest, pending).completed_at is not None
