"""FR-OPS-002/003: warning-only closed configuration contracts."""

from typing import get_args
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.config import Settings
from services.operations_configuration import SETTING_FIELDS, defaults, reference
from services.operations_configuration_contracts import (
    ConfigurationKey,
    ConfigurationPatch,
    ConfigurationView,
    WarningValues,
)


def test_closed_warning_keys_match_existing_environment_and_schema():
    assert set(get_args(ConfigurationKey)) == set(WarningValues.model_fields)
    assert set(SETTING_FIELDS) | {"retirement_stall_seconds"} == set(get_args(ConfigurationKey))
    assert len(WarningValues.model_fields) == 15
    settings = Settings()
    values = defaults(settings)
    assert values.retirement_stall_seconds == settings.export_retirement_interval_seconds * 2
    for key, field in SETTING_FIELDS.items():
        assert getattr(values, key) == getattr(settings, field)
    assert "provider" not in values.model_dump() and "enabled" not in values.model_dump()


@pytest.mark.parametrize("invalid", [True, "2", 2.5, None, -1, 0, 86401])
def test_patch_never_coerces_input(invalid):
    with pytest.raises(ValidationError):
        ConfigurationPatch(version="a" * 64, value=invalid, reason="REDUCE_NOISE")


@pytest.mark.parametrize("key", get_args(ConfigurationKey))
def test_snapshot_values_are_strict_for_every_key(key):
    values = defaults(Settings()).model_dump()
    for invalid in [True, "2", -1, 86401]:
        with pytest.raises(ValidationError):
            WarningValues.model_validate(values | {key: invalid})


def test_reference_binds_entire_defaults_snapshot_and_preserved_namespace():
    values = defaults(Settings())
    nonce = uuid4()
    original = reference(nonce, 0, None, values)
    assert original == reference(nonce, 0, None, values)
    assert original != reference(uuid4(), 0, None, values)
    assert original != reference(
        nonce, 0, None, WarningValues.model_validate(values.model_dump() | {"failed_imports": 2})
    )
    with pytest.raises(ValidationError):
        ConfigurationView(
            revision=1, version=original, source="VERSIONED", values=values, updated_at=None
        )
