"""The isolated browser fault fixture must never attach to an ordinary database."""

from types import SimpleNamespace
from uuid import uuid4

import anyio
import pytest
from fastapi import FastAPI
from sqlalchemy.engine import make_url

from scripts.e2e_exports import FakeExportReader, FakeExportStore, install


@pytest.mark.parametrize("options", [None, "-csearch_path=public", "-csearch_path=e2e_bad,public"])
def test_export_fault_controls_reject_nonisolated_databases(options):
    url = make_url("postgresql://localhost/synthetic")
    if options:
        url = url.update_query_dict({"options": options})
    service = SimpleNamespace(engine=SimpleNamespace(url=url))
    app = FastAPI()
    with pytest.raises(ValueError, match="isolated E2E schema"):
        install(app, service)
    assert not app.dependency_overrides
    assert not any(route.path.startswith("/__fixture") for route in app.routes)


def test_export_fault_reader_preserves_objects_and_closes_after_cancel():
    async def scenario():
        store = FakeExportStore()
        generation, target = uuid4(), uuid4()
        store.put(generation, target, b"synthetic ciphertext")
        for mode in ["normal", "stall", "corrupt"]:
            reader = FakeExportReader(store)
            store.faults[generation] = mode
            assert await reader.get(generation, target) == b"synthetic ciphertext"
            if mode == "stall":
                with anyio.move_on_after(0.01) as scope:
                    await reader.get(generation, target)
                assert scope.cancel_called
            else:
                expected = (
                    b"synthetic invalid ciphertext"
                    if mode == "corrupt"
                    else b"synthetic ciphertext"
                )
                assert await reader.get(generation, target) == expected
            await reader.aclose()
            await reader.aclose()
            assert store.get(generation, target) == b"synthetic ciphertext"
        assert store.closed[generation] == 3

    anyio.run(scenario)
