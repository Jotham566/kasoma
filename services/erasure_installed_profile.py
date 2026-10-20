"""ADR-079 immutable technical expectation format; never learner payload storage."""

import hashlib
import json
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from services.erasure_catalog import CATEGORIES, RAW_CATEGORIES, CatalogDigest, migration_digest
from services.erasure_catalog_bindings import BOUND_EXPRESSIONS, BoundExpression, CatalogBindings

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "services/erasure_installed_catalog_v1.json"
PROFILE: Literal["installed-erasure-catalog-v1"] = "installed-erasure-catalog-v1"
RECIPE_SOURCES = (
    "scripts/erasure_capability.py",
    "scripts/erasure_plan_sql.py",
    "scripts/erasure_acl_sql.py",
    "scripts/erasure_catalog_code.py",
    "scripts/erasure_installed_queries.py",
    "scripts/erasure_installed_profile.py",
    "services/erasure_catalog_bindings.py",
    "services/erasure_installed_profile.py",
    "services/erasure_capability_contract.py",
    "services/erasure_catalog.py",
    "services/erasure_catalog.sql",
    "services/erasure_catalog_raw_v2.sql",
    "services/erasure_catalog_v2.json",
    "services/erasure_datum.py",
    "services/erasure_manifest.py",
    "services/erasure_sources.py",
    "apps/api/migrations/sql/erasure_capability_v1.sql",
    "apps/api/migrations/sql/erasure_plans_v3.sql",
)


def recipe_digest() -> str:
    digest = hashlib.sha256()
    for name in RECIPE_SOURCES:
        digest.update(name.encode() + b"\0" + (ROOT / name).read_bytes() + b"\0")
    return digest.hexdigest()


class InstalledProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    profile: Literal["installed-erasure-catalog-v1"] = PROFILE
    capability: Literal["isolated-erasure-capability-v7"] = "isolated-erasure-capability-v7"
    revision: Literal["0045"] = "0045"
    datum_codec: Literal["unsigned-octets-v1"] = "unsigned-octets-v1"
    postgres_major: Literal[16] = 16
    migration_sources_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    recipe_sources_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expressions: dict[str, BoundExpression]
    raw: dict[str, CatalogDigest]
    full: dict[str, CatalogDigest]

    @model_validator(mode="after")
    def complete_profile(self) -> Self:
        if (
            self.expressions.keys() != BOUND_EXPRESSIONS.keys()
            or any(key != expression.key for key, expression in self.expressions.items())
            or self.raw.keys() != RAW_CATEGORIES
            or self.full.keys() != CATEGORIES
        ):
            raise ValueError("Incomplete installed catalog profile")
        return self

    def canonical(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"

    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical().encode()).hexdigest()

    def expectation(self, bindings: CatalogBindings, code: dict[str, str]) -> dict[str, object]:
        return {
            "profile": self.profile,
            "artifact_sha256": self.fingerprint(),
            "recipe_sha256": self.recipe_sources_sha256,
            "code": code,
            "expressions": {
                key: hashlib.sha256(value.render(bindings).encode()).hexdigest()
                for key, value in self.expressions.items()
            },
            "raw": {key: value.model_dump() for key, value in self.raw.items()},
            "full": {key: value.model_dump() for key, value in self.full.items()},
        }


def load_installed_profile() -> InstalledProfile:
    result = InstalledProfile.model_validate_json(PROFILE_PATH.read_text())
    if (
        result.migration_sources_sha256 != migration_digest()
        or result.recipe_sources_sha256 != recipe_digest()
    ):
        raise ValueError("Installed catalog recipe changed")
    return result
