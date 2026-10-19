"""Explicit local provisioning/configuration commands; no batch execution in this CLI."""

import os
from pathlib import Path
from uuid import uuid4

from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url

from services.config import Settings
from services.database import engine_for
from services.export_retirement import executor_engine, profile
from services.export_retirement_access import provision
from services.export_retirement_config import CONFIG_PATH, isolated_scope, load_executor


def main() -> None:
    engine = None
    created_path = False
    try:
        action = os.environ.get("KASOMA_RETIREMENT_ACTION", "provision")
        settings = Settings(export_retirement_enabled=False)
        path = Path(os.environ.get("KASOMA_RETIREMENT_CONFIG", str(CONFIG_PATH)))
        target_schema = os.environ.get("KASOMA_RETIREMENT_SCHEMA")
        if target_schema:
            url = make_url(settings.database_url.get_secret_value())
            if not url.database or not isolated_scope(url.database, target_schema):
                raise ValueError
            url = url.update_query_dict({"options": f"-csearch_path={target_schema},public"})
            settings = settings.model_copy(
                update={"database_url": SecretStr(url.render_as_string(hide_password=False))}
            )
        engine = engine_for(settings)
        with engine.begin() as db:
            if action == "provision":
                provision(
                    db,
                    path,
                    settings.database_url.get_secret_value(),
                    settings.redis_url.get_secret_value(),
                )
                created_path = True
            elif action in {"enable", "disable"}:
                private = load_executor(path, disabled=action == "disable")
                if private.database_url is None:
                    raise ValueError
                target = make_url(private.database_url.get_secret_value())
                database, schema = db.execute(
                    text("SELECT current_database(),current_schema()")
                ).one()
                if (
                    target.database != database
                    or private.namespace != schema
                    or not isolated_scope(database, schema)
                ):
                    raise ValueError
                if action == "enable" and (not private.enabled or not private.holds_enabled):
                    raise ValueError
                ordinary = make_url(settings.database_url.get_secret_value())
                if (ordinary.host, ordinary.port, ordinary.database) != (
                    target.host,
                    target.port,
                    target.database,
                ):
                    raise ValueError
                if action == "enable":
                    check = executor_engine(private)
                    try:
                        with check.connect() as connection:
                            if profile(connection) != (database, schema):
                                raise ValueError
                    finally:
                        check.dispose()
                db.execute(
                    text(
                        "UPDATE export_retirement_state SET enabled=:enabled,"
                        "updated_at=clock_timestamp()"
                    ),
                    {"enabled": action == "enable"},
                )
            else:
                raise ValueError
            event = uuid4()
            db.execute(
                text("""INSERT INTO audit_log(id,actor_id,target_id,action,reason,
              request_id,before_hash,after_hash,created_at) VALUES(:id,NULL,:id,
              'data_request.retirement_configuration',:reason,:id,NULL,NULL,clock_timestamp())"""),
                {
                    "id": event,
                    "reason": {
                        "provision": "EXECUTOR_PROVISIONED",
                        "enable": "SYNTHETIC_RETIREMENT_ENABLED",
                        "disable": "SYNTHETIC_RETIREMENT_DISABLED",
                    }[action],
                },
            )
        print("Synthetic retirement configuration recorded. No batch executed.")
    except Exception:
        if created_path:
            path.unlink(
                missing_ok=True
            )  # A failed DB commit must not leave a usable-looking config.
        raise SystemExit(
            "Retirement configuration refused; existing data preserved, diagnostics withheld"
        ) from None
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()
