"""Fault controls for the isolated synthetic E2E process; never shipped in app images."""

import re
from typing import Literal
from uuid import UUID, uuid4

import anyio
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from apps.api.export_jobs import reader_factory
from services.domain.data_requests import DataRequest
from services.domain.export_jobs import ExportJob
from services.identity import IdentityService


class FakeExportStore:
    def __init__(self) -> None:
        self.objects: dict[tuple[UUID, UUID], bytes] = {}
        self.faults: dict[UUID, str] = {}
        self.reads: dict[UUID, int] = {}
        self.closed: dict[UUID, int] = {}

    def put(self, generation: UUID, object_id: UUID, ciphertext: bytes) -> None:
        self.objects[generation, object_id] = ciphertext

    def get(self, generation: UUID, object_id: UUID) -> bytes:
        return self.objects[generation, object_id]


class FakeExportReader:
    def __init__(self, store: FakeExportStore) -> None:
        self.store = store
        self.generation: UUID | None = None
        self.count = 0

    async def get(self, generation: UUID, object_id: UUID) -> bytes:
        self.generation = generation
        self.count += 1
        self.store.reads[generation] = self.store.reads.get(generation, 0) + 1
        if self.count >= 2:
            if self.store.faults.get(generation) == "stall":
                await anyio.sleep_forever()
            if self.store.faults.get(generation) == "corrupt":
                return b"synthetic invalid ciphertext"
        return self.store.get(generation, object_id)

    async def aclose(self) -> None:
        if self.generation is not None:
            self.store.closed[self.generation] = self.store.closed.get(self.generation, 0) + 1
            self.generation = None


def install(app: FastAPI, service: IdentityService) -> FakeExportStore:
    # A caller cannot attach destructive test controls to the ordinary developer database.
    options = str(service.engine.url.query.get("options", ""))
    if not re.fullmatch(r"-csearch_path=e2e_[0-9a-f]{32},public", options):
        raise ValueError("Export fixtures require an isolated E2E schema")
    store = FakeExportStore()
    populated: set[UUID] = set()
    app.dependency_overrides[reader_factory] = lambda: lambda: FakeExportReader(store)

    @app.post("/__fixture/exports/{target}/history", include_in_schema=False)
    def history(target: UUID) -> dict[str, bool]:
        with service.transaction() as db:
            request = db.get(DataRequest, target)
            if request is None or request.kind != "EXPORT" or db.get(ExportJob, target):
                raise HTTPException(409)
            if target not in populated:
                for _ in range(700):
                    service.event(
                        db, request.user_id, "synthetic.browser." + "x" * 200, str(uuid4())
                    )
        populated.add(target)
        return {"prepared": True}

    def generation(target: UUID) -> UUID:
        with Session(service.engine) as db:
            job = db.get(ExportJob, target)
            if job is None or job.status != "READY" or job.generation_id is None:
                raise HTTPException(409)
            return job.generation_id

    @app.post("/__fixture/exports/{target}/fault/{mode}", include_in_schema=False)
    def fault(target: UUID, mode: Literal["normal", "stall", "corrupt"]) -> dict[str, bool]:
        key = generation(target)
        store.faults[key] = mode
        store.reads[key] = 0
        store.closed[key] = 0
        return {"configured": True}

    @app.get("/__fixture/exports/{target}/observations", include_in_schema=False)
    def observations(target: UUID) -> dict[str, int]:
        key = generation(target)
        return {"reads": store.reads.get(key, 0), "closed": store.closed.get(key, 0)}

    return store
