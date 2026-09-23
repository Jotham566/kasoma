from alembic import context
from sqlalchemy import text

from services.config import Settings
from services.database import Base, engine_for
from services.domain import curriculum, identity  # noqa: F401

settings = Settings()
engine = engine_for(settings)
with engine.connect() as connection:
    # Pin the version table to the current schema: public fallback must not make
    # a fresh isolated schema look migrated.
    schema = connection.scalar(text("SELECT current_schema()"))
    connection.commit()
    context.configure(
        connection=connection, target_metadata=Base.metadata, version_table_schema=schema
    )
    with context.begin_transaction():
        context.run_migrations()
engine.dispose()
