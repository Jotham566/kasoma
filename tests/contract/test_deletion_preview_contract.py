"""A review response is structurally incapable of enabling deletion."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.data_request_contracts import DeletionPreview, DeletionSource


def test_preview_cannot_enable_execution_or_expose_uncontracted_identity():
    payload = dict(
        request_id=uuid4(), observed_at=datetime.now(UTC), sources=[], blockers=[], limitations=[]
    )
    with pytest.raises(ValidationError):
        DeletionPreview(**payload, execution_enabled=True)
    with pytest.raises(ValidationError):
        DeletionPreview(**payload, user_id=uuid4())
    with pytest.raises(ValidationError):
        DeletionSource(source="users", count=-1, at_least=False, retention="REMOVE_DIRECT_LINKAGE")
