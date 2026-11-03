"""Public sign-in guidance must reflect the configured local delivery adapters."""

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app


@pytest.mark.parametrize("email_provider", ["mailpit", "fake"])
def test_auth_options_are_public_minimized_and_match_delivery(settings, email_provider):
    config = settings.model_copy(update={"email_provider": email_provider})
    with TestClient(create_app(config)) as client:
        response = client.get("/api/v1/auth/options")
    assert response.status_code == 200
    assert response.json() == {
        "email_delivery": email_provider,
        "sms_delivery": "fake",
        "local_inbox_url": "http://localhost:8025" if email_provider == "mailpit" else None,
    }
    assert response.headers["cache-control"] == "no-store"
