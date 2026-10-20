"""Reproduce ADR-073 metadata only from newly created fake-only sources; no URL input."""

import sys

from sqlalchemy import text

from scripts.browser_database import cleanup_on_termination
from scripts.erasure_scope import fresh_erasure_scope
from scripts.recovery_containers import command
from services.config import Settings
from services.database import engine_for
from services.erasure_catalog import (
    BASELINE_PATH,
    CATEGORIES,
    DYNAMIC_BODIES,
    OWNER_PLACEHOLDER,
    RAW_CATEGORIES,
    CatalogUnavailable,
    _observe_catalog,
    baseline_text,
    check_preinstall_catalog,
    load_baseline,
    retirement_owner,
)
from services.erasure_inventory import check_source_shape


def reproduce(*, write: bool = False) -> None:
    settings = Settings(
        model_provider="fake",
        email_provider="fake",
        sms_provider="fake",
        whatsapp_provider="fake",
        allow_external_api_calls=False,
    )
    with cleanup_on_termination(), fresh_erasure_scope(settings) as proof:
        command(
            ["make", "migrate"],
            environment={"DATABASE_URL": proof.settings.database_url.get_secret_value()},
        )
        engine = engine_for(proof.settings)
        try:
            with engine.begin() as db:
                proof.verify()
                check_source_shape(db)
                database = db.scalar(text("SELECT current_database()"))
                if not isinstance(database, str):
                    raise CatalogUnavailable()
                owner = retirement_owner(database)
                rows = db.execute(
                    text("""
                  SELECT p.proname,p.prosrc FROM pg_catalog.pg_proc p
                  JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
                  WHERE n.nspname='public' AND p.pronargs=0 AND p.proname=ANY(:names)
                """),
                    {"names": list(DYNAMIC_BODIES)},
                ).all()
                if len(rows) != len(DYNAMIC_BODIES) or any(
                    owner not in row.prosrc or OWNER_PLACEHOLDER in row.prosrc for row in rows
                ):
                    raise CatalogUnavailable()
                templates = {
                    str(row.proname): str(row.prosrc).replace(owner, OWNER_PLACEHOLDER)
                    for row in rows
                }
                baseline = _observe_catalog(db, templates, raw_expected=None)
            if write:
                BASELINE_PATH.write_text(baseline_text(baseline))
            elif baseline != load_baseline():
                raise CatalogUnavailable()
            else:
                with engine.begin() as db:
                    check_preinstall_catalog(db)
            print(
                f"Fresh catalog reproduced:{len(CATEGORIES)} metadata/"
                f"{len(RAW_CATEGORIES)} raw safety categories; "
                "no application rows read"
            )
        finally:
            engine.dispose()


def main() -> None:
    arguments = sys.argv[1:]
    if arguments not in ([], ["--write"]):
        raise SystemExit("Unsupported catalog reproduction command")
    try:
        reproduce(write=arguments == ["--write"])
    except CatalogUnavailable as failure:
        raise SystemExit(
            f"Catalog reproduction unavailable ({failure.code}:{failure.position})"
        ) from None
    except Exception:
        raise SystemExit("Catalog reproduction unavailable; diagnostics withheld") from None


if __name__ == "__main__":
    main()
