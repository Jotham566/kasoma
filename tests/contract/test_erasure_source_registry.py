"""Closed source coverage; neither names nor a fingerprint constitute clearance."""

import pytest

from services.erasure_inventory import SourceManifestChanged
from services.erasure_manifest import BASELINE
from services.erasure_sources import OWNERSHIP_EDGES, PREDICATES, assert_registry, source_query


def test_every_manifest_source_has_explicit_ownership_or_nonownership():
    assert_registry()
    assert len(PREDICATES) == len(BASELINE) == 74
    assert PREDICATES["otp_challenges"] == "x.user_id=:subject"
    for name in ["channel_senders", "identity_rate_buckets"]:
        assert PREDICATES[name] is None
    for child, column, parent, target in OWNERSHIP_EDGES:
        assert column in {c.name for c in BASELINE[child].columns}
        assert target in {c.name for c in BASELINE[parent].columns}


@pytest.mark.parametrize("name", ["unknown", "users;DROP TABLE users", "identity_rate_buckets"])
def test_no_arbitrary_or_shared_table_selector(name):
    with pytest.raises(SourceManifestChanged):
        source_query(name, "public")


def test_schema_is_quoted_and_values_are_bound_without_returning_bodies_or_keys():
    query = source_query("users", 'synthetic"schema')
    assert '"synthetic""schema"."users"' in query
    assert ":subject" in query and 'ORDER BY x."id"' in query
    assert "SELECT encode(sha256(" in query and "x.xmin::text" in query
    assert "SELECT x.*" not in query
    with pytest.raises(TypeError):
        PREDICATES["users"] = "true"
