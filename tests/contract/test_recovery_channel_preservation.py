"""Synthetic preservation fixtures cannot target developer or opposite-stage databases."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import SecretStr

from scripts import recovery_channel_preservation as recovery
from scripts.recovery_channel_receipts import ChannelHoldAuthority


@pytest.mark.parametrize("operation", ["populate", "verify"])
@pytest.mark.parametrize("name", ["kasoma", "postgres", "kasoma_drill_src_bad", "opposite"])
def test_wrong_database_is_rejected_before_authentication_or_capture(monkeypatch, operation, name):
    if name == "opposite":
        name = f"kasoma_drill_{'dst' if operation == 'populate' else 'src'}_{uuid4().hex}"
    db = MagicMock()
    db.__enter__.return_value.scalar.return_value = name
    monkeypatch.setattr(recovery, "Session", lambda engine: db)
    identity = SimpleNamespace(engine=object())
    with pytest.raises(ValueError, match="isolated synthetic drill"):
        if operation == "populate":
            recovery.populate_preservation(
                identity,
                "synthetic-not-a-token",
                ChannelHoldAuthority(uuid4(), SecretStr("synthetic-not-a-token")),
            )
        else:
            recovery.verify_preservation(identity)
    assert db.__enter__.return_value.scalar.call_count == 1
    assert db.__enter__.return_value.add.call_count == 0
