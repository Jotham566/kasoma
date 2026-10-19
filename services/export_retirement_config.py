"""Private maintenance settings; ordinary API/worker settings never load this credential."""

import os
import re
import stat
from pathlib import Path
from typing import Literal, Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

from services.config import require_local

CONFIG_PATH = Path(".local/export-retirement.env")


def isolated_scope(database: str, schema: str) -> bool:
    return bool(
        re.fullmatch(r"identity_test_[0-9a-f]{32}", schema)
        or schema == "public"
        and re.fullmatch(r"kasoma_(?:retirement_test|drill_src|drill_dst)_[0-9a-f]{32}", database)
    )


class ExecutorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="export_retirement_", env_file=None, extra="forbid", hide_input_in_errors=True
    )
    app_env: Literal["development", "test"] = "development"
    enabled: bool = False
    holds_enabled: bool = False
    namespace: str = "public"
    database_url: SecretStr | None = None
    redis_url: SecretStr = SecretStr("redis://localhost:6379/0")

    @model_validator(mode="after")
    def bounded(self) -> Self:
        if self.enabled and (not self.holds_enabled or self.database_url is None):
            raise ValueError("Retirement requires exact holds and a separate executor credential")
        if self.database_url is not None:
            value = self.database_url.get_secret_value()
            try:
                url = make_url(value)
                require_local(value, {"postgres"})
                if (
                    url.drivername != "postgresql+psycopg"
                    or not url.username
                    or not url.password
                    or not url.database
                    or url.query
                ):
                    raise ValueError
                if self.enabled and not isolated_scope(url.database, self.namespace):
                    raise ValueError
            except Exception:
                raise ValueError("Invalid local retirement executor configuration") from None
        require_local(self.redis_url.get_secret_value(), {"redis"})
        return self


def load_executor(path: Path = CONFIG_PATH, *, disabled: bool = False) -> ExecutorSettings:
    """Only the dedicated entrypoint/CLI calls this; do not load from shared .env."""
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Executor configuration requires an owned private regular file")
    if disabled:
        return ExecutorSettings(_env_file=path, enabled=False)
    return ExecutorSettings(_env_file=path)
