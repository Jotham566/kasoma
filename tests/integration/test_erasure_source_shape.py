"""Real isolated metadata only; does not provision or execute erasure."""

import pytest
from sqlalchemy import text

from services.erasure_inventory import SourceManifestChanged, check_source_shape

pytestmark = pytest.mark.integration


def test_actual0044_catalog_and_unknown_source_or_column_refusal(identity):
    service, *_ = identity
    with service.engine.connect() as db:
        check_source_shape(db)
        savepoint = db.begin_nested()
        db.execute(text("ALTER TABLE users ADD COLUMN unreviewed_copy text"))
        with pytest.raises(SourceManifestChanged):
            check_source_shape(db)
        savepoint.rollback()
        check_source_shape(db)
        savepoint = db.begin_nested()
        # A foreign/custom-type column must be observed and rejected, never filtered away.
        db.execute(text("CREATE TYPE unreviewed_value AS ENUM ('SYNTHETIC')"))
        db.execute(text("ALTER TABLE users ADD COLUMN unknown_value unreviewed_value"))
        with pytest.raises(SourceManifestChanged):
            check_source_shape(db)
        savepoint.rollback()
        savepoint = db.begin_nested()
        db.execute(text("CREATE VIEW unreviewed_view AS SELECT 1 AS synthetic"))
        with pytest.raises(SourceManifestChanged):
            check_source_shape(db)
        savepoint.rollback()
        check_source_shape(db)
