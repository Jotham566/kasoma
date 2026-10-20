"""Expected code cannot be blessed from unrelated or incomplete source text."""

from uuid import UUID

import pytest

from scripts.erasure_catalog_code import expected_code_hashes
from services.erasure_catalog_bindings import CatalogBindings


@pytest.mark.parametrize(
    "definition",
    [
        "SELECT 1;",
        "CREATE FUNCTION public.unexpected() RETURNS boolean LANGUAGE sql AS $$SELECT true$$;",
        'CREATE FUNCTION "kasoma_cap_'
        + UUID(int=3).hex
        + '".readiness(foo text) RETURNS jsonb LANGUAGE sql AS $$SELECT NULL$$;',
        'CREATE FUNCTION "kasoma_cap_'
        + UUID(int=3).hex
        + '".readiness() RETURNS jsonb LANGUAGE sql AS $$SELECT NULL$$;',
    ],
)
def test_incomplete_or_unapproved_definition_is_not_an_expected_profile(definition):
    bindings = CatalogBindings(16384, 2200, 18001, 18002, 18003, 10, UUID(int=3))
    with pytest.raises(ValueError):
        expected_code_hashes(bindings, "synthetic", (definition,))
