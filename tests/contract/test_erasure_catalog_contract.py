"""ADR-073 closed metadata baseline; no SQL adoption or data-erasure authority."""

import pytest
from pydantic import ValidationError

from services.erasure_catalog import (
    CATEGORIES,
    RAW_CATEGORIES,
    CatalogBaseline,
    CatalogUnavailable,
    load_baseline,
    migration_digest,
    retirement_owner,
)
from services.export_retirement_install import owner_name


def test_versioned_baseline_is_closed_and_bound_to_approved_migrations():
    baseline = load_baseline()
    assert len(CATEGORIES) == 32 and len(RAW_CATEGORIES) == 9
    assert baseline.migration_sources_sha256 == migration_digest()
    assert baseline.categories["triggers"].count > 500
    assert baseline.categories["functions"].count > 100
    for mutation in (
        {"revision": "0044"},
        {"postgres_major": 17},
        {"categories": {}},
        {"raw_categories": {}},
        {"body_templates": {}},
        {
            "categories": baseline.model_dump()["categories"]
            | {"unknown": {"count": 0, "digest": "0" * 64}}
        },
    ):
        with pytest.raises(ValidationError):
            CatalogBaseline.model_validate(baseline.model_dump() | mutation)
    changed = baseline.model_dump()
    changed["categories"]["roles"]["count"] = True
    with pytest.raises(ValidationError):
        CatalogBaseline.model_validate(changed)


@pytest.mark.parametrize("database", ["kasoma", "kasoma_erasure_test_" + "1" * 32, "other"])
def test_owner_normalization_matches_only_the_exact_existing_derivation(database):
    assert retirement_owner(database) == owner_name(database, "public")
    assert retirement_owner(database) != owner_name(database, "identity_test_" + "1" * 32)


def test_error_text_never_echoes_unknown_diagnostics():
    failure = CatalogUnavailable("SYNTHETIC_UNTRUSTED_DIAGNOSTIC", 99999999)
    assert failure.code == "QUERY" and failure.position == 100000
    assert str(failure) == "ERASURE_CATALOG_UNAVAILABLE"
