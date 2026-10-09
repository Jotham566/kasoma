"""Worker-boundary failures must not leak claims, database or provider diagnostics."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from services import export_processing as processing


@pytest.mark.parametrize("phase", ["claim", "failure_recording"])
def test_unhandled_processing_boundary_errors_are_closed(monkeypatch, phase):
    def failure(*args, **kwargs):
        raise RuntimeError("synthetic secret connection/identity/provider information")

    monkeypatch.setattr(
        processing,
        "claim_next",
        failure if phase == "claim" else lambda _: SimpleNamespace(correlation_id=uuid4()),
    )
    monkeypatch.setattr(processing, "snapshot", failure)
    monkeypatch.setattr(processing, "fail_claim", failure)
    with pytest.raises(RuntimeError) as exc:
        processing.process_one(None, None)
    assert str(exc.value) == "Personal export processing failed; diagnostics withheld"
    assert exc.value.__suppress_context__
