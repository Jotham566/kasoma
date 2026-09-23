import json
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.identity import IdentityError, normalize
from services.identity_contracts import ConsentInput, ProfilePatch


@pytest.mark.parametrize(
    "raw, expected",
    [
        (" Synthetic@Example.Invalid ", ("EMAIL", "synthetic@example.invalid")),
        ("+256700000001", ("PHONE", "+256700000001")),
    ],
)
def test_normalization(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.parametrize(
    "raw", ["a@b\nBcc: target@example.invalid", "0700000001", "<script>", "+00000000"]
)
def test_invalid_contact(raw):
    with pytest.raises(IdentityError):
        normalize(raw)


def test_contract_does_not_accept_roles_or_false_consent():
    with pytest.raises(ValidationError):
        ProfilePatch(
            display_name="Synthetic", birth_date="2010-01-01", subject_ids=[uuid4()], role="ADMIN"
        )
    with pytest.raises(ValidationError):
        ConsentInput(consent_type="SELF", policy_version="synthetic", affirmative=False)


def test_event_schema_excludes_sensitive_properties():
    schema = json.loads(Path("packages/analytics-schema/identity-event.schema.json").read_text())
    assert schema["additionalProperties"] is False
    payload = schema["properties"]["payload"]
    assert payload["additionalProperties"] is False
    assert set(payload["properties"]) == {"request_id"}
    assert "registration.completed" in schema["properties"]["type"]["enum"]
