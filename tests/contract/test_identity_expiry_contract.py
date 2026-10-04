"""Scheduled ephemeral cleanup and minimized operational event boundary."""

import json
from pathlib import Path

from apps.worker.main import make_worker


def test_ephemeral_expiry_is_scheduled_without_new_auth_validity(settings):
    worker = make_worker(settings)
    try:
        assert worker.conf.beat_schedule["expire-identity"] == {
            "task": "kasoma.expire_identity",
            "schedule": 60.0,
        }
        assert "kasoma.expire_identity" in worker.tasks
    finally:
        worker.close()


def test_expiry_event_has_a_closed_payload_free_schema():
    schema = json.loads(Path("packages/analytics-schema/identity-expiry.schema.json").read_text())
    assert schema["additionalProperties"] is False
    assert (
        set(schema["properties"])
        == set(schema["required"])
        == {
            "event",
            "correlation_id",
            "status",
            "challenges",
            "rate_buckets",
            "schema_version",
        }
    )
    for count in ["challenges", "rate_buckets"]:
        assert schema["properties"][count] == {"type": "integer", "minimum": 0, "maximum": 100}
    assert schema["allOf"][0]["then"]["properties"] == {
        "challenges": {"const": 0},
        "rate_buckets": {"const": 0},
    }
