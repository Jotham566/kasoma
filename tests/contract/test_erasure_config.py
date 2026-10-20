"""Scope names/config switches are necessary fences, never proof of SQL authority."""

import os
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.config import Settings
from services.erasure_config import ErasureSettings, isolated_scope, load_erasure


def test_default_profile_has_no_capability_and_shared_settings_have_no_erasure_secret():
    config = ErasureSettings(_env_file=None)
    assert config.enabled is False
    assert config.database_url is None
    assert not any(name.startswith("account_erasure_") for name in Settings.model_fields)


@pytest.mark.parametrize(
    "changes",
    [
        {"enabled": True},
        {"app_env": "production"},
        {"model_provider": "local"},
        {"model_provider": "gemini-free-eval"},
        {"email_provider": "mailpit"},
        {"sms_provider": "africas_talking"},
        {"whatsapp_provider": "meta"},
        {"force": True},
        {"database_url": "postgresql+psycopg://u:canary-secret@localhost/kasoma"},
        {"database_url": "postgresql+psycopg://u:canary-secret@remote.invalid/synthetic"},
        {"database_url": "postgresql+psycopg://u:canary-secret@postgres/synthetic"},
        {"database_url": "postgresql+psycopg://u:canary-secret@localhost/synthetic?host=x"},
        {"namespace": "identity_test_" + "a" * 32 + ";public"},
    ],
)
def test_configuration_refuses_review_cloud_provider_and_incomplete_authority(changes):
    with pytest.raises(ValidationError) as failure:
        ErasureSettings(_env_file=None, **changes)
    assert "canary-secret" not in str(failure.value)


def test_configuration_does_not_read_normal_env_or_enable_from_generic_variables(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ACCOUNT_ERASURE_ENABLED=true\nAPP_ENV=production\n")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ENABLED", "true")
    assert ErasureSettings().enabled is False


def test_explicit_synthetic_profile_passes_only_the_name_fence():
    database = "kasoma_erasure_test_" + uuid4().hex
    assert isolated_scope(database, "public")
    assert not isolated_scope("kasoma", "public")
    assert not isolated_scope(database, "other")
    config = ErasureSettings(
        enabled=True, database_url=f"postgresql+psycopg://user:synthetic@localhost/{database}"
    )
    assert config.enabled
    schema = "identity_test_" + uuid4().hex
    assert (
        ErasureSettings(
            enabled=True,
            namespace=schema,
            database_url="postgresql+psycopg://user:synthetic@localhost/kasoma",
        ).namespace
        == schema
    )
    # No connection, provisioner or state mutation occurs during settings construction.


def test_private_loader_preserves_source_and_refuses_public_permissions_symlink_and_fifo(tmp_path):
    path = tmp_path / "capability.env"
    content = "ACCOUNT_ERASURE_ENABLED=false\n"
    path.write_text(content)
    path.chmod(0o644)
    with pytest.raises(ValueError, match="owned private"):
        load_erasure(path)
    path.chmod(0o600)
    assert load_erasure(path).enabled is False
    link = tmp_path / "link.env"
    link.symlink_to(path)
    with pytest.raises(OSError):
        load_erasure(link)
    fifo = tmp_path / "pipe.env"
    os.mkfifo(fifo, mode=0o600)
    with pytest.raises(ValueError, match="regular file"):
        load_erasure(fifo)
    assert path.read_text() == content


@pytest.mark.parametrize(
    "content",
    [
        "ACCOUNT_ERASURE_ENABLED=true\n",
        "DATABASE_URL=canary-secret\n",
        "ACCOUNT_ERASURE_UNKNOWN=canary-secret\n",
        "ACCOUNT_ERASURE__ENV_FILE=canary-secret\n",
        "ACCOUNT_ERASURE__SECRETS_DIR=canary-secret\n",
        "ACCOUNT_ERASURE__CASE_SENSITIVE=true\n",
        "ACCOUNT_ERASURE_enabled=false\n",
        "ACCOUNT_ERASURE_DATABASE_URL=${OTHER_PRIVATE_SECRET}\n",
        "ACCOUNT_ERASURE_ENABLED\n",
        "ACCOUNT_ERASURE_ENABLED=" + "x" * 8192,
    ],
)
def test_private_loader_refuses_unknown_oversized_or_interpolated_configuration(
    content, tmp_path, monkeypatch
):
    monkeypatch.setenv("OTHER_PRIVATE_SECRET", "canary-secret")
    path = tmp_path / "private.env"
    path.write_text(content)
    path.chmod(0o600)
    with pytest.raises(ValueError) as failure:
        load_erasure(path)
    assert "canary-secret" not in str(failure.value)


def test_private_authorizer_fields_are_closed_local_and_secret():
    from pydantic import ValidationError

    database = "kasoma_erasure_test_" + "a" * 32
    uri = f"postgresql+psycopg://private:synthetic@localhost:12345/{database}"
    value = ErasureSettings(
        authorizer_database_url=uri, capability_namespace="kasoma_cap_" + "b" * 32
    )
    assert "synthetic" not in repr(value.authorizer_database_url)
    for change in [
        {"authorizer_database_url": uri.replace("localhost", "remote.invalid")},
        {"authorizer_database_url": uri + "?options=-csearch_path=public"},
        {"capability_namespace": "public"},
    ]:
        with pytest.raises(ValidationError):
            ErasureSettings(**change)
