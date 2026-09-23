from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase

from services.config import Settings


class Base(DeclarativeBase):
    pass


def engine_for(settings: Settings) -> Engine:
    url = make_url(settings.database_url.get_secret_value())
    options = url.query.get("options", "")
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 2,
            "options": f"{options} -c timezone=UTC -c statement_timeout=2000",
        },
        hide_parameters=True,
    )
