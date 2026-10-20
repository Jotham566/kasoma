"""ADR-076 M4-only paired catalog rehearsal; no scope/URL/image selector."""

import json
import platform
import sys
from unittest.mock import patch

from sqlalchemy import event, text

from scripts import browser_database
from scripts.browser_database import (
    cleanup_on_termination,
    pinned_local_docker,
    require_fake_profile,
)
from scripts.erasure_scope import fresh_erasure_scope
from scripts.recovery_containers import RecoveryCommandError, command, image_id
from services.config import Settings
from services.database import engine_for
from services.erasure_catalog import (
    CATEGORIES,
    RAW_CATEGORIES,
    CatalogUnavailable,
    check_preinstall_catalog,
)

# Both immutable manifests belong to the already-approved image index, not new technology.
INDEX = "sha256:00ba258a66dac104fd5171074a0084462a64a1369d8513f3d0a634e2f24d15bc"
VARIANTS = (
    (
        "arm64",
        "pgvector/pgvector@sha256:b759abdeb144e561a4dbfe9863b5ac58cdd3fb6350cee7e68035baffdbca9693",
    ),
    (
        "amd64",
        "pgvector/pgvector@sha256:6d5c7b5aa3eb2098a2365f6d8cff723fded9e0e680757908b0b144b47f9c069c",
    ),
)


def variant_image(architecture: str, reference: str) -> str:
    if (architecture, reference) not in VARIANTS:
        raise ValueError("CATALOG_VARIANT_UNAVAILABLE")
    try:
        raw = command(["docker", "image", "inspect", reference])
    except RecoveryCommandError as failure:
        if failure.kind != "IMAGE_UNAVAILABLE":
            raise
        command(["docker", "pull", reference])
        raw = command(["docker", "image", "inspect", reference])
    item = json.loads(raw)[0]
    if item["Architecture"] != architecture or not isinstance(item["Id"], str):
        raise ValueError("CATALOG_VARIANT_UNAVAILABLE")
    return image_id(item["Id"])


def run_variant(settings: Settings, architecture: str, reference: str) -> dict[str, object]:
    approved = variant_image(architecture, reference)

    def selected(service: str) -> str:
        if service != "postgres":
            raise ValueError("CATALOG_VARIANT_UNAVAILABLE")
        return approved

    # Test-only constructor override in this standalone process; no existing resource
    # is adopted, and the normal API/worker never imports this tool or selects an image.
    with patch.object(browser_database, "compose_image", selected):
        with fresh_erasure_scope(settings) as proof:
            cid = proof._container_id
            command(
                ["make", "migrate"],
                environment={
                    "DATABASE_URL": proof.settings.database_url.get_secret_value(),
                },
            )
            engine = engine_for(proof.settings)
            stages: list[str] = []

            def observed(
                conn: object,
                cursor: object,
                statement: str,
                parameters: object,
                context: object,
                executemany: bool,
            ) -> None:
                if "raw_objects(category,body)" in statement:
                    stages.append("RAW")
                elif "acl_objects AS (" in statement:
                    stages.append("FULL")

            try:
                with engine.begin() as db:
                    proof.verify()
                    check_preinstall_catalog(db)
                    version = int(str(db.scalar(text("SHOW server_version_num"))))
                    if version // 10000 != 16:
                        raise ValueError("CATALOG_SERVER_UNAVAILABLE")
                    flags = db.execute(
                        text(
                            "SELECT original_scope_eligible,creation_enabled,"
                            "execution_enabled FROM account_erasure_state"
                        )
                    ).one()
                    if tuple(flags) != (False, False, False):
                        raise ValueError("CATALOG_ACTIVATION_UNAVAILABLE")
                    if db.scalar(text("SELECT count(*) FROM users")) != 0:
                        raise ValueError("CATALOG_SOURCE_NOT_EMPTY")
                    if db.scalar(text("SELECT count(*) FROM account_erasure_jobs")) != 0:
                        raise ValueError("CATALOG_SOURCE_NOT_EMPTY")
                    with db.begin_nested() as mutation:
                        db.execute(
                            text("ALTER TABLE public.users DROP CONSTRAINT users_closed_disabled")
                        )
                        db.execute(
                            text(
                                "ALTER TABLE public.users ADD CONSTRAINT users_closed_disabled "
                                "CHECK (closed_at IS NULL OR status='DISABLEE')"
                            )
                        )
                        event.listen(engine, "before_cursor_execute", observed)
                        try:
                            try:
                                check_preinstall_catalog(db)
                            except CatalogUnavailable:
                                if stages != ["RAW"]:
                                    raise ValueError("CATALOG_GUARD_ORDER_UNAVAILABLE") from None
                            else:
                                raise ValueError("CATALOG_DRIFT_WAS_NOT_REFUSED")
                        finally:
                            event.remove(engine, "before_cursor_execute", observed)
                        mutation.rollback()
                    check_preinstall_catalog(db)
            finally:
                engine.dispose()
        if (
            cid
            in command(["docker", "ps", "--all", "--no-trunc", "--format", "{{.ID}}"]).splitlines()
        ):
            raise ValueError("CATALOG_SOURCE_CLEANUP_UNAVAILABLE")
    return {
        "architecture": architecture,
        "image": approved,
        "container_id": cid,
        "server_version_num": version,
        "full_categories": len(CATEGORIES),
        "raw_categories": len(RAW_CATEGORIES),
        "catalog_match": True,
        "changed_constant_refused_before_deparse": True,
        "exact_container_absent": True,
    }


def main() -> None:
    try:
        if sys.argv[1:] or sys.platform != "darwin" or platform.machine() != "arm64":
            raise ValueError("SUPPORTED_M4_HOST_REQUIRED")
        settings = Settings(
            model_provider="fake",
            email_provider="fake",
            sms_provider="fake",
            whatsapp_provider="fake",
            allow_external_api_calls=False,
        )
        require_fake_profile(settings)
        with cleanup_on_termination(), pinned_local_docker():
            results = [run_variant(settings, arch, reference) for arch, reference in VARIANTS]
        print(
            json.dumps(
                {
                    "profile": "fresh-catalog-arm64-amd64-v2",
                    "image_index": INDEX,
                    "variants": results,
                    "activation_enabled": False,
                    "cleanup_failed": [],
                },
                sort_keys=True,
            )
        )
    except Exception:
        raise SystemExit(
            "Catalog portability verification unavailable; diagnostics withheld"
        ) from None


if __name__ == "__main__":
    main()
