"""Local-only startup policy; rejected values never appear in validation errors."""

from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}


def require_local(url: str, services: set[str] | None = None) -> str:
    parsed = urlsplit(url)
    if parsed.hostname not in LOCAL_HOSTS | (services or set()):
        raise ValueError("Only explicitly supported local service endpoints are permitted")
    if parsed.scheme not in {"http", "https", "redis", "postgresql+psycopg"}:
        raise ValueError("Unsupported local protocol")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)
    app_env: Literal["development", "test", "production"] = "development"
    app_public_url: str = "http://localhost:3000"
    api_public_url: str = "http://localhost:8000"
    database_url: SecretStr
    redis_url: SecretStr
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_container: str = "kasoma-local"
    object_storage_access_key: SecretStr
    object_storage_secret_key: SecretStr
    jwt_signing_key: SecretStr
    token_issuer: str = "kasoma-local"
    model_provider: Literal["fake", "local"] = "fake"
    model_base_url: str = "http://localhost:11434/v1"
    ollama_model_alias: str = "local-quality"
    email_provider: Literal["fake", "mailpit"] = "mailpit"
    mailpit_host: Literal["localhost", "127.0.0.1", "mailpit"] = "localhost"
    mailpit_port: int = 1025
    sms_provider: Literal["fake"] = "fake"
    whatsapp_provider: Literal["fake"] = "fake"
    otp_provider: Literal["fake"] = "fake"
    allow_external_api_calls: bool = False
    allow_google_free_tier_eval: bool = False

    @model_validator(mode="after")
    def local_only(self) -> Self:
        if self.app_env == "production":
            raise ValueError("Production is unavailable until deployment and security gates pass")
        if self.allow_external_api_calls:
            raise ValueError("External services are not implemented in the foundation")
        if self.app_env == "test" and self.model_provider != "fake":
            raise ValueError("Automated tests require FakeModelProvider")
        for secret in (
            self.database_url,
            self.redis_url,
            self.object_storage_access_key,
            self.object_storage_secret_key,
            self.jwt_signing_key,
        ):
            if not secret.get_secret_value():
                raise ValueError("Required local configuration is empty; run make setup")
        require_local(self.database_url.get_secret_value(), {"postgres"})
        require_local(self.redis_url.get_secret_value(), {"redis"})
        require_local(self.object_storage_endpoint, {"minio"})
        require_local(self.model_base_url)
        require_local(self.app_public_url, {"web"})
        require_local(self.api_public_url, {"api"})
        return self
