from typing import Literal

from pydantic import BaseModel
from redis import Redis
from sqlalchemy import text

from services.config import Settings
from services.database import engine_for

State = Literal["up", "down"]


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    api: Literal["up"] = "up"
    database: State
    redis: State


def dependency_health(settings: Settings) -> Health:
    database: State = "down"
    redis_state: State = "down"
    engine = engine_for(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        database = "up"
    except Exception:
        database = "down"  # Never expose exception strings or connection credentials.
    finally:
        engine.dispose()
    try:
        with Redis.from_url(
            settings.redis_url.get_secret_value(),
            socket_connect_timeout=2,
            socket_timeout=2,
        ) as client:
            client.ping()
        redis_state = "up"
    except Exception:
        redis_state = "down"
    return Health(
        status="ok" if database == redis_state == "up" else "degraded",
        database=database,
        redis=redis_state,
    )
