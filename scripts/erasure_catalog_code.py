"""Expected complete bodies from trusted recipe definitions, never live prosrc."""

import hashlib
import re
from typing import Literal

from scripts.erasure_acl_sql import FUNCTIONS
from services.erasure_catalog import load_baseline, retirement_owner
from services.erasure_catalog_bindings import CatalogBindings

_NAME = r'(?:"[a-z_0-9]+"|[a-z_0-9]+)'
_FUNCTION = re.compile(
    r"CREATE(?: OR REPLACE)? FUNCTION (?P<name>"
    + _NAME
    + r"\."
    + _NAME
    + r")\s*\((?P<arguments>[^()]*)\).*?\bAS\s+(?P<tag>\$[a-z_]*\$)"
    r"(?P<body>.*?)(?P=tag)\s*;",
    re.S,
)
_ARGUMENT = re.compile(r"(?:[a-z_][a-z_0-9]*\s+)?(bytea|uuid|oid|jsonb)", re.I)


def expected_code_hashes(
    bindings: CatalogBindings,
    database: str,
    definitions: tuple[str, ...],
    *,
    recipe: Literal["v6", "v7"] = "v6",
) -> dict[str, str]:
    """Compiler input is the closed repository recipe; no caller SQL or live bodies.

    Retain exact leading/trailing whitespace inside dollar quoting. Later trusted
    CREATE OR REPLACE definitions replace earlier bodies, as PostgreSQL does.
    Body hashes include all bytes and every instance-specific constant.
    """
    private = set(FUNCTIONS)
    historical = set()
    if recipe == "v7":
        private.remove("initialize_control(bytea)")
        private.update({"initialize_control(bytea,jsonb)", "installed_catalog_ok()"})
        historical.add(bindings.namespace + ".initialize_control(bytea)")
    elif recipe != "v6":
        raise ValueError("Unknown installed code recipe")
    required = {bindings.namespace + "." + name for name in private}
    required.add("public.account_erasure_dormant_guard()")
    result = {}
    for definition in definitions:
        matches = list(_FUNCTION.finditer(definition))
        if not matches:
            raise ValueError("Missing trusted function definition")
        for match in matches:
            arguments = []
            if match["arguments"].strip():
                for argument in match["arguments"].split(","):
                    parsed = _ARGUMENT.fullmatch(argument.strip())
                    if parsed is None:
                        raise ValueError("Unsupported trusted function interface")
                    arguments.append(parsed[1].lower())
            name = match["name"].replace('"', "") + "(" + ",".join(arguments) + ")"
            if name not in required | historical:
                raise ValueError("Unknown trusted function definition")
            result[name] = hashlib.sha256(match["body"].encode()).hexdigest()
    if result.keys() - historical != required:
        raise ValueError("Incomplete trusted function definitions")
    result = {name: value for name, value in result.items() if name in required}
    baseline = load_baseline()
    owner = retirement_owner(database)
    for name, body in baseline.body_templates.items():
        result["public." + name + "()"] = hashlib.sha256(
            body.replace("@EXPORT_RETIREMENT_OWNER@", owner).encode()
        ).hexdigest()
    return result
