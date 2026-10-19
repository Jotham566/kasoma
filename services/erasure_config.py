"""ADR-061 private synthetic profile; configuration alone never authorizes a closure."""

import os
import re
import stat
from io import StringIO
from pathlib import Path
from typing import Literal, Self

from dotenv import dotenv_values
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

from services.config import require_local

CONFIG_PATH = Path(".local/account-erasure.env")
PREFIX = "ACCOUNT_ERASURE_"
MAX_CONFIG_BYTES = 8192


def isolated_scope(database: str, schema: str) -> bool:
    """Necessary name fence only; a fresh owned SQL capability is separately required."""
    return bool(
        re.fullmatch(r"identity_test_[0-9a-f]{32}", schema)
        or schema == "public"
        and re.fullmatch(r"kasoma_erasure_test_[0-9a-f]{32}", database)
    )


class ErasureSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=PREFIX, env_file=None, extra="forbid", hide_input_in_errors=True
    )
    app_env: Literal["development", "test"] = "development"
    enabled: bool = False
    namespace: str = Field(default="public", pattern=r"^[a-z_][a-z_0-9]{0,62}$")
    database_url: SecretStr | None = None
    model_provider: Literal["fake"] = "fake"
    email_provider: Literal["fake"] = "fake"
    sms_provider: Literal["fake"] = "fake"
    whatsapp_provider: Literal["fake"] = "fake"

    @model_validator(mode="after")
    def synthetic_only(self) -> Self:
        if self.enabled and self.database_url is None:
            raise ValueError("A separate isolated erasure capability is required")
        if self.database_url is not None:
            try:
                raw = self.database_url.get_secret_value()
                url = make_url(raw)
                require_local(raw)
                if (
                    url.drivername != "postgresql+psycopg"
                    or not url.username
                    or not url.password
                    or not url.database
                    or url.query
                    or not isolated_scope(url.database, self.namespace)
                ):
                    raise ValueError
            except Exception:
                raise ValueError("Invalid isolated synthetic erasure configuration") from None
        return self


def load_erasure(path: Path = CONFIG_PATH) -> ErasureSettings:
    """Read the same owned0600 regular file checked by descriptor; refuse symlinks."""
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o077
            or info.st_size > MAX_CONFIG_BYTES
        ):
            raise ValueError("Erasure configuration requires an owned private bounded regular file")
        raw = stream.read(MAX_CONFIG_BYTES + 1)
    if len(raw) > MAX_CONFIG_BYTES:
        raise ValueError("Erasure configuration is too large")
    try:
        # Disable interpolation: a private file cannot copy arbitrary process secrets.
        values = dotenv_values(stream=StringIO(raw.decode("utf-8")), interpolate=False)
        if any(not name.startswith(PREFIX) or value is None for name, value in values.items()):
            raise ValueError
        fields = {name.removeprefix(PREFIX).lower(): value for name, value in values.items()}
        if any(name != name.upper() for name in values) or not fields.keys() <= (
            ErasureSettings.model_fields.keys()
        ):
            # BaseSettings has private constructor options: never permit file-supplied
            # _env_file/_secrets_dir or parser overrides through those options.
            raise ValueError
        return ErasureSettings.model_validate(fields)
    except Exception:
        raise ValueError("Invalid private erasure configuration; diagnostics withheld") from None
