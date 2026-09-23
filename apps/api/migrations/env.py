from alembic import context

from services.config import Settings
from services.database import Base, engine_for
from services.domain import curriculum  # noqa: F401

settings = Settings()
engine = engine_for(settings)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
engine.dispose()
