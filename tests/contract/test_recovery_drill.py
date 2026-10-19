"""Reject unsafe targets before recovery resources or tools can be invoked."""

from unittest.mock import MagicMock, Mock

import pytest
from pydantic import SecretStr

from scripts.recovery_drill import drill, local_database_url, validate_name


@pytest.mark.parametrize(
    "name",
    [
        "kasoma",
        "postgres",
        "kasoma_drill_src_",
        "kasoma_drill_src_" + "a" * 33,
        "kasoma_drill_src_; DROP DATABASE kasoma",
        "kasoma_drill_other_" + "a" * 32,
    ],
)
def test_only_generated_names_are_accepted(name):
    with pytest.raises(ValueError, match="generated recovery"):
        validate_name(name)


def test_both_generated_names_are_accepted():
    for kind in ["src", "dst"]:
        name = f"kasoma_drill_{kind}_" + "0" * 32
        assert validate_name(name) == name


@pytest.mark.parametrize(
    "url",
    [
        "http://kasoma:secret@localhost:55432/kasoma",
        "postgresql+psycopg://kasoma:secret@remote.invalid:55432/kasoma",
        "postgresql+psycopg://kasoma:secret@localhost:5432/kasoma",
        "postgresql+psycopg://other:secret@localhost:55432/kasoma",
        "postgresql+psycopg://kasoma:secret@localhost:55432/kasoma?options=unsafe",
    ],
)
def test_nonstandard_profiles_fail_before_connect(settings, monkeypatch, url):
    connect = Mock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr("scripts.recovery_drill.create_engine", connect)
    changed = settings.model_copy(update={"app_env": "development", "database_url": SecretStr(url)})
    with pytest.raises(ValueError, match="standard local"):
        drill(changed)
    connect.assert_not_called()


def test_production_rejected_and_local_target_is_not_overwritten(settings):
    for environment in ["test", "production"]:
        with pytest.raises(ValueError, match="standard local"):
            local_database_url(settings.model_copy(update={"app_env": environment}))
    configured = settings.model_copy(
        update={
            "app_env": "development",
            "database_url": SecretStr("postgresql+psycopg://kasoma:secret@localhost:55432/keep_me"),
        }
    )
    url = local_database_url(configured)
    assert url.database == "keep_me"
    assert url.set(database="postgres").database == "postgres"
    assert url.database == "keep_me"


def test_create_failure_never_drops_uncreated_database(settings, monkeypatch):
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value.execute.side_effect = RuntimeError("secret")
    monkeypatch.setattr("scripts.recovery_drill.create_engine", lambda *a, **k: engine)
    result = drill(
        settings.model_copy(
            update={
                "app_env": "development",
                "database_url": SecretStr(
                    "postgresql+psycopg://kasoma:secret@localhost:55432/keep_me"
                ),
            }
        )
    )
    assert result["status"] == "FAILED"
    assert result["failed_stage"] == "CREATE_ISOLATED_DATABASES"
    assert result["cleanup_failed"] == []
    executed = engine.connect.return_value.__enter__.return_value.execute.call_args_list
    assert len(executed) == 1
    assert "CREATE DATABASE" in str(executed[0].args[0])
    assert "secret" not in str(result)
    assert result["failure_kind"] == "UNEXPECTED"
    assert 1 <= len(result["failure_sites"]) <= 3
    assert all(
        "/" not in site and site.rsplit(":", 1)[-1].isdigit() for site in result["failure_sites"]
    )


def test_partial_creation_cleans_only_the_owned_source(settings, monkeypatch):
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value.scalar.return_value = False
    execute = engine.connect.return_value.__enter__.return_value.execute
    execute.side_effect = [None, RuntimeError("existing destination"), None]
    monkeypatch.setattr("scripts.recovery_drill.create_engine", lambda *a, **k: engine)
    result = drill(
        settings.model_copy(
            update={
                "app_env": "development",
                "database_url": SecretStr(
                    "postgresql+psycopg://kasoma:secret@localhost:55432/keep_me"
                ),
            }
        )
    )
    statements = [str(call.args[0]) for call in execute.call_args_list]
    assert len(statements) == 3
    assert statements[2] == statements[0].replace("CREATE", "DROP")
    assert result["status"] == "FAILED"
    assert result["cleanup_failed"] == []
    assert all("keep_me" not in statement for statement in statements)


def test_migration_failure_and_cleanup_failure_are_reported_safely(settings, monkeypatch):
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value.scalar.return_value = False
    execute = engine.connect.return_value.__enter__.return_value.execute
    execute.side_effect = [None, None, RuntimeError("private DB diagnostic"), None]
    monkeypatch.setattr("scripts.recovery_drill.create_engine", lambda *a, **k: engine)
    monkeypatch.setattr(
        "scripts.recovery_drill.subprocess.run", Mock(side_effect=RuntimeError("secret"))
    )
    result = drill(
        settings.model_copy(
            update={
                "app_env": "development",
                "database_url": SecretStr(
                    "postgresql+psycopg://kasoma:secret@localhost:55432/keep_me"
                ),
            }
        )
    )
    assert result["failed_stage"] == "MIGRATE_SYNTHETIC_SOURCE"
    assert len(result["cleanup_failed"]) == 1
    assert result["cleanup_failed"][0].startswith("kasoma_drill_dst_")
    assert "secret" not in str(result)
    assert "private DB diagnostic" not in str(result)
    statements = [str(call.args[0]) for call in execute.call_args_list]
    assert statements[2] == statements[1].replace("CREATE", "DROP")
    assert statements[3] == statements[0].replace("CREATE", "DROP")


@pytest.mark.parametrize("source_drop_fails", [False, True])
def test_cleanup_drops_only_derived_owner_after_its_created_database_is_gone(
    settings, monkeypatch, source_drop_fails
):
    from services.export_retirement_install import owner_name

    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    statements = []

    def execute(statement):
        value = str(statement)
        statements.append(value)
        if source_drop_fails and value.startswith('DROP DATABASE "kasoma_drill_src_'):
            raise RuntimeError("Synthetic retained database")

    connection.execute.side_effect = execute
    # Source has the installer-created role; destination never ran migrations.
    connection.scalar.side_effect = [False] if source_drop_fails else [True, False]
    monkeypatch.setattr("scripts.recovery_drill.create_engine", lambda *a, **k: engine)
    monkeypatch.setattr("scripts.recovery_drill.subprocess.run", Mock())
    monkeypatch.setattr(
        "scripts.recovery_drill.populate", Mock(side_effect=RuntimeError("fixture"))
    )
    result = drill(
        settings.model_copy(
            update={
                "app_env": "development",
                "database_url": SecretStr(
                    "postgresql+psycopg://kasoma:secret@localhost:55432/keep_me"
                ),
            }
        )
    )
    source = statements[0].split('"')[1]
    role_drop = f'DROP ROLE "{owner_name(source, "public")}"'
    if source_drop_fails:
        assert role_drop not in statements and result["cleanup_failed"] == [source]
    else:
        assert statements[-1] == role_drop and result["cleanup_failed"] == []
    assert all("keep_me" not in statement for statement in statements)
