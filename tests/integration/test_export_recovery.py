"""FR-ID-006/NFR-REL-002: the drill must verify bytes, not just restored row counts."""

import pytest
from sqlalchemy import event

from scripts.recovery_exports import populate_export
from services.export_artifacts import ArtifactError

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("damage", ["ciphertext", "missing_object", "expected_bytes"])
def test_populated_recovery_verification_is_read_only_and_rejects_damage(content, damage):
    identity, _, actors, _ = content
    state = populate_export(identity, actors["learner"]["Authorization"][7:])

    def read_only(conn, cursor, statement, parameters, context, executemany):
        assert statement.lstrip().upper().startswith("SELECT ")

    event.listen(identity.engine, "before_cursor_execute", read_only)
    try:
        state.verify(identity)
        key = next(iter(state.objects))
        if damage == "ciphertext":
            state.objects[key] = b"synthetic corrupt ciphertext"
        elif damage == "missing_object":
            del state.objects[key]
        else:
            state.frozen += b"synthetic change"
        with pytest.raises((ArtifactError, RuntimeError)):
            state.verify(identity)
    finally:
        event.remove(identity.engine, "before_cursor_execute", read_only)
