"""Normal review sources cannot opt into installed erasure planning via configuration."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import text

from services import erasure_plans
from tests.integration.test_data_requests import claim, create

pytestmark = pytest.mark.integration


def test_normal_review_case_refuses_before_private_configuration(content, monkeypatch):
    identity, client, actors, *_ = content
    request = create(client, actors["learner"], "DELETE")
    assert request.status_code == 201, request.text
    target = request.json()["id"]
    assert claim(client, actors["admin"], target).status_code == 200
    loader = Mock(
        side_effect=AssertionError("Normal review must not read private erasure configuration")
    )
    monkeypatch.setattr(erasure_plans, "load_erasure", loader)
    path = f"/api/v1/admin/data-requests/{target}/erasure-plan"
    assert client.get(path).status_code == 401
    for actor in ["learner", "support", "author"]:
        assert client.get(path, headers=actors[actor]).status_code == 403
    assert client.get(path, headers=actors["admin"]).status_code == 503
    loader.assert_not_called()
    with identity.engine.connect() as db:
        assert db.scalar(text("SELECT count(*) FROM account_erasure_plans")) == 0
        assert db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) == 0
    assert (
        client.post(
            f"/api/v1/admin/data-requests/{target}/erasure",
            headers=actors["admin"] | {"Idempotency-Key": str(uuid4())},
            json={"affirmative": True},
        ).status_code
        == 404
    )
