"""Local-only startup policy; rejected values never appear in validation errors."""

from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
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
    identity_encryption_key: SecretStr
    identity_lookup_key: SecretStr
    consent_policy_version: str = "synthetic-development-v1"
    assessment_session_days: int = Field(default=7, ge=1, le=30)
    assessment_repetition_days: int = Field(default=7, ge=1, le=90)
    short_text_enabled: bool = False
    short_text_max_requests: int = Field(default=3, ge=2, le=3)
    short_text_max_tokens: int = Field(default=16384, ge=2, le=16384)
    short_text_timeout_ms: int = Field(default=5000, ge=1, le=5000)
    short_text_model_version: str = Field(
        default="fixture-v1", pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"
    )
    short_text_prompt_version: str = Field(
        default="synthetic-short-text-dual-pass-v2",
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$",
    )
    short_text_configuration_version: str = Field(
        default="short-text-runtime-v1", pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"
    )
    ops_failed_import_threshold: int = Field(default=1, ge=1, le=10000)
    ops_request_p95_ms: int = Field(default=500, ge=1, le=60000)
    ops_request_min_samples: int = Field(default=20, ge=1, le=10000)
    ops_import_age_seconds: int = Field(default=300, ge=60, le=86400)
    ops_flag_backlog_threshold: int = Field(default=20, ge=1, le=10000)
    export_evidence_holds_enabled: bool = False
    export_retirement_enabled: bool = False
    export_retirement_interval_seconds: int = Field(default=300, ge=60, le=3600)
    channel_receipt_holds_enabled: bool = False
    channel_preservation_enabled: bool = False
    otp_observation_enabled: bool = False
    ops_otp_failures_threshold: int = Field(default=1, ge=1, le=10000)
    model_observation_enabled: bool = False
    ops_model_gateway_attempts_threshold: int = Field(default=100, ge=1, le=10000)
    ops_grading_age_seconds: int = Field(default=60, ge=1, le=86400)
    ops_export_failure_threshold: int = Field(default=1, ge=1, le=10000)
    ops_export_age_seconds: int = Field(default=300, ge=60, le=86400)
    ops_channel_failure_threshold: int = Field(default=1, ge=1, le=10000)
    ops_channel_queue_age_seconds: int = Field(default=60, ge=1, le=86400)
    ops_channel_dispatch_p95_ms: int = Field(default=1500, ge=1, le=60000)
    ops_channel_dispatch_min_samples: int = Field(default=20, ge=1, le=1000)
    token_issuer: str = "kasoma-local"
    model_provider: Literal["fake", "local"] = "fake"
    model_base_url: str = "http://localhost:11434/v1"
    ollama_model_alias: str = "local-quality"
    email_provider: Literal["fake", "mailpit"] = "mailpit"
    mailpit_host: Literal["localhost", "127.0.0.1", "mailpit"] = "localhost"
    mailpit_port: int = 1025
    sms_provider: Literal["fake"] = "fake"
    whatsapp_provider: Literal["fake"] = "fake"
    whatsapp_app_secret: SecretStr | None = None
    whatsapp_verify_token: SecretStr | None = None
    whatsapp_business_id: Literal["synthetic-business"] = "synthetic-business"
    whatsapp_phone_number_id: Literal["synthetic-phone"] = "synthetic-phone"
    whatsapp_outbound_enabled: bool = False
    whatsapp_outbound_per_minute: int = Field(default=10, ge=1, le=60)
    whatsapp_link_attempts_per_minute: int = Field(default=5, ge=1, le=20)
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
        from cryptography.fernet import Fernet

        try:
            Fernet(self.identity_encryption_key.get_secret_value().encode())
        except Exception:
            raise ValueError("Invalid identity encryption key; run make setup") from None
        if len(self.identity_lookup_key.get_secret_value()) < 32:
            raise ValueError("Identity lookup key must have at least 32 characters")
        if self.export_retirement_enabled:
            import re

            from sqlalchemy.engine import make_url

            from services.export_retirement_config import isolated_scope

            url = make_url(self.database_url.get_secret_value())
            options = url.query.get("options", "")
            if not isinstance(options, str):
                raise ValueError("Invalid retirement scheduling scope")
            match = re.fullmatch(r"-csearch_path=(identity_test_[0-9a-f]{32}),public", options)
            namespace = match.group(1) if match else "public"
            if (
                not self.export_evidence_holds_enabled
                or not url.database
                or not isolated_scope(url.database, namespace)
                or options
                and match is None
            ):
                raise ValueError(
                    "Retirement scheduling requires exact holds and an isolated synthetic scope"
                )
        require_local(self.database_url.get_secret_value(), {"postgres"})
        require_local(self.redis_url.get_secret_value(), {"redis"})
        require_local(self.object_storage_endpoint, {"minio"})
        require_local(self.model_base_url)
        require_local(self.app_public_url, {"web"})
        require_local(self.api_public_url, {"api"})
        return self
