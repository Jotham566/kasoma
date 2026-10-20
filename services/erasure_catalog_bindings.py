"""ADR-079 typed expected-tree rendering; never normalize a live expression."""

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

BindingName = Literal[
    "database_oid",
    "namespace_oid",
    "owner_oid",
    "authorizer_oid",
    "executor_oid",
    "installation_nonce",
    "cap_name",
    "crypto_name",
    "hmac_name",
]
_EXPRESSION_BINDINGS: dict[str, tuple[BindingName, ...]] = {
    "CONSTRAINT:public.account_erasure_state:account_erasure_state_bound_owner": (
        "owner_oid",
        "executor_oid",
    ),
    "CONSTRAINT:CAPABILITY.control:control_database_oid_check": ("database_oid",),
    "CONSTRAINT:CAPABILITY.control:control_namespace_oid_check": ("namespace_oid",),
    "CONSTRAINT:CAPABILITY.control:control_owner_oid_check": ("owner_oid",),
    "CONSTRAINT:CAPABILITY.control:control_authorizer_oid_check": ("authorizer_oid",),
    "CONSTRAINT:CAPABILITY.control:control_executor_oid_check": ("executor_oid",),
    "CONSTRAINT:CAPABILITY.control:control_installation_nonce_check": ("installation_nonce",),
    "DEFAULT:CAPABILITY.control:cap_namespace_oid": ("cap_name",),
    "DEFAULT:CAPABILITY.control:crypto_namespace_oid": ("crypto_name",),
    "DEFAULT:CAPABILITY.control:crypto_hmac_oid": ("hmac_name",),
}
BOUND_EXPRESSIONS = MappingProxyType(_EXPRESSION_BINDINGS)
_CONST = re.compile(
    r"\{CONST :consttype (?P<oid>[0-9]+) [^{}]*?:constvalue (?P<declared>[0-9]+) "
    r"\[ (?P<octets>[0-9 ]*)\]\}"
)
_MARKER = re.compile(r"@[A-Z_]+@")


@dataclass(frozen=True)
class CatalogBindings:
    database_oid: int
    namespace_oid: int
    owner_oid: int
    authorizer_oid: int
    executor_oid: int
    creator_oid: int
    installation_nonce: UUID

    def __post_init__(self) -> None:
        # Fresh v7 templates use int4 constants and fixed-width decimal tokens.
        # Unknown/wider representations require a new checked profile, never coercion.
        if (
            any(
                type(value) is not int or not 0 < value < 2**31
                for value in (
                    self.database_oid,
                    self.namespace_oid,
                    self.owner_oid,
                    self.authorizer_oid,
                    self.executor_oid,
                    self.creator_oid,
                )
            )
            or type(self.installation_nonce) is not UUID
        ):
            raise ValueError("Unsupported installed catalog bindings")
        if len({self.owner_oid, self.authorizer_oid, self.executor_oid, self.creator_oid}) != 4:
            raise ValueError("Unsupported installed catalog principals")

    @property
    def namespace(self) -> str:
        return "kasoma_cap_" + self.installation_nonce.hex

    @property
    def crypto(self) -> str:
        return "kasoma_ec_" + self.installation_nonce.hex

    def value(self, name: BindingName) -> int | UUID | str:
        if name == "cap_name":
            return '"' + self.namespace + '"'
        if name == "crypto_name":
            return '"' + self.crypto + '"'
        if name == "hmac_name":
            return '"' + self.crypto + '".hmac(bytea,bytea,text)'
        if name in {
            "database_oid",
            "namespace_oid",
            "owner_oid",
            "authorizer_oid",
            "executor_oid",
            "installation_nonce",
        }:
            value = getattr(self, name)
            if isinstance(value, (int, UUID)):
                return value
        raise ValueError("Unknown installed catalog binding")


class ConstantSlot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    kind: Literal["INTEGER", "UUID", "TEXT"]
    width: int = Field(ge=8, le=256)
    prefix: tuple[int, ...] = ()

    @model_validator(mode="after")
    def closed_layout(self) -> Self:
        if (
            self.kind == "INTEGER"
            and (self.width != 8 or self.prefix)
            or self.kind == "UUID"
            and (self.width != 16 or self.prefix)
            or self.kind == "TEXT"
            and (
                len(self.prefix) != 4
                or self.prefix != tuple((self.width << 2).to_bytes(4, "little"))
            )
        ):
            raise ValueError("Unsupported installed constant layout")
        return self

    def encode(self, value: int | UUID | str) -> str:
        if self.kind == "INTEGER" and type(value) is int and 0 < value < 2**31:
            data = value.to_bytes(8, "little")
        elif self.kind == "UUID" and type(value) is UUID:
            data = value.bytes
        elif self.kind == "TEXT" and type(value) is str:
            data = bytes(self.prefix) + value.encode("utf-8")
            if len(data) != self.width:
                raise ValueError("Installed text constant width changed")
        else:
            raise ValueError("Installed constant type changed")
        return "".join(str(octet) + " " for octet in data)


class BoundExpression(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    key: str
    template: str
    slots: dict[BindingName, ConstantSlot]

    @model_validator(mode="after")
    def closed_slots(self) -> Self:
        expected = BOUND_EXPRESSIONS.get(self.key)
        markers = ["@" + name.upper() + "@" for name in self.slots]
        if (
            expected is None
            or set(expected) != self.slots.keys()
            or sorted(_MARKER.findall(self.template)) != sorted(markers)
        ):
            raise ValueError("Unsupported installed expression template")
        return self

    def render(self, bindings: CatalogBindings) -> str:
        result = self.template
        for name, slot in self.slots.items():
            result = result.replace("@" + name.upper() + "@", slot.encode(bindings.value(name)))
        return result


def freeze_expression(key: str, tree: str, bindings: CatalogBindings) -> BoundExpression:
    """Only the independent fresh generator calls this; runtime loads frozen templates."""
    names = BOUND_EXPRESSIONS.get(key)
    if names is None:
        raise ValueError("Unknown installed expression")
    template, slots = tree, {}
    for name in names:
        value = bindings.value(name)
        matches = []
        for match in _CONST.finditer(tree):
            octets = tuple(int(part) for part in match["octets"].split())
            if any(not 0 <= octet <= 255 for octet in octets):
                raise ValueError("Noncanonical installed constant")
            oid, declared = int(match["oid"]), int(match["declared"])
            slot = None
            if type(value) is int and oid == 23 and declared == 4 and len(octets) == 8:
                slot = ConstantSlot(kind="INTEGER", width=8)
            elif type(value) is UUID and oid == 2950 and declared == 16 and len(octets) == 16:
                slot = ConstantSlot(kind="UUID", width=16)
            elif type(value) is str and oid == 25 and declared == len(octets):
                slot = ConstantSlot(kind="TEXT", width=declared, prefix=octets[:4])
            if slot is not None and slot.encode(value) == match["octets"]:
                matches.append((match, slot))
        if len(matches) != 1:
            raise ValueError("Installed expression binding did not match exactly once")
        match, slot = matches[0]
        original = tree[match.start() : match.end()]
        relative = match.start("octets") - match.start()
        changed = (
            original[:relative]
            + "@"
            + name.upper()
            + "@"
            + original[relative + len(match["octets"]) :]
        )
        if template.count(original) != 1:
            raise ValueError("Ambiguous installed expression constant")
        template = template.replace(original, changed)
        slots[name] = slot
    result = BoundExpression(key=key, template=template, slots=slots)
    if result.render(bindings) != tree:
        raise ValueError("Installed expression did not reproduce")
    return result
