"""NFR-SEC-002: shared ownership helper rejects every non-generated source."""

from unittest.mock import Mock

import pytest

from scripts.disposable_owner import cleanup_owner, create_owner, validate_owner_database


@pytest.mark.parametrize("prefix", ["kasoma_load_", "kasoma_drill_src_"])
def test_owned_source_namespace(prefix):
    name = prefix + "a" * 32
    assert validate_owner_database(name) == name


@pytest.mark.parametrize(
    "name",
    [
        "kasoma",
        "postgres",
        "kasoma_drill_dst_" + "a" * 32,
        "kasoma_drill_src_" + "a" * 33,
        "kasoma_load_" + "A" * 32,
        'kasoma_drill_src_"; DROP ROLE unrelated',
    ],
)
def test_invalid_sources_cannot_connect_for_creation_or_cleanup(name):
    admin = Mock()
    with pytest.raises(ValueError):
        create_owner(admin, name)
    with pytest.raises(ValueError):
        cleanup_owner(admin, name, 1)
    admin.connect.assert_not_called()
