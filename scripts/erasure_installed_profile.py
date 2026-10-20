"""ADR-079 observation only inside a rolled-back fresh definition preparation."""

import hashlib
import json
from dataclasses import dataclass

from sqlalchemy import Connection, text

from scripts.erasure_catalog_code import expected_code_hashes
from scripts.erasure_installed_queries import installed_queries, prepared_expressions
from services.erasure_catalog import CATEGORIES, RAW_CATEGORIES, CatalogDigest, retirement_owner
from services.erasure_catalog_bindings import BoundExpression, CatalogBindings, freeze_expression
from services.erasure_datum import DATUM_PATTERN


@dataclass(frozen=True)
class PreparedSnapshot:
    expressions: dict[str, BoundExpression]
    raw: dict[str, CatalogDigest]
    full: dict[str, CatalogDigest]


def observe_prepared(
    db: Connection,
    bindings: CatalogBindings,
    definitions: tuple[str, ...],
    templates: dict[str, BoundExpression] | None = None,
) -> PreparedSnapshot:
    """Never called by an accepting verifier; no initialized keys/learner rows read."""
    db.execute(text("SET LOCAL search_path=pg_catalog"))
    db.execute(text("SET LOCAL timezone='UTC'"))
    db.execute(text("SET LOCAL jit=off"))
    db.execute(text("SET LOCAL statement_timeout='5000ms'"))
    db.execute(text("SET LOCAL lock_timeout='100ms'"))
    database = db.scalar(text("SELECT current_database()"))
    if not isinstance(database, str):
        raise ValueError("Prepared database unavailable")
    code = expected_code_hashes(bindings, database, definitions)
    actual_code = db.scalar(
        text("""
      SELECT count(*) FROM jsonb_each_text(CAST(:code AS jsonb)) e
      JOIN pg_catalog.pg_proc p ON p.oid=to_regprocedure(e.key)
      WHERE encode(sha256(convert_to(p.prosrc,'UTF8')),'hex')=e.value
    """),
        {"code": json.dumps(code)},
    )
    if actual_code != len(code):
        raise ValueError("Prepared code did not match trusted definitions")
    trees = prepared_expressions(db, bindings)
    expressions = (
        templates
        if templates is not None
        else {key: freeze_expression(key, tree, bindings) for key, tree in trees.items()}
    )
    if {key: value.render(bindings) for key, value in expressions.items()} != trees:
        raise ValueError("Prepared expressions did not reproduce")
    parameters = {
        "cap": bindings.namespace,
        "crypto": bindings.crypto,
        "owner": bindings.owner_oid,
        "authorizer": bindings.authorizer_oid,
        "executor": bindings.executor_oid,
        "retirement_owner": retirement_owner(database),
        "code_hashes": json.dumps(code),
        "datum_pattern": DATUM_PATTERN,
        "expression_hashes": json.dumps(
            {
                key: hashlib.sha256(value.render(bindings).encode()).hexdigest()
                for key, value in expressions.items()
            }
        ),
    }
    full_query, raw_query = installed_queries()
    stages = []
    for query, categories in ((raw_query, RAW_CATEGORIES), (full_query, CATEGORIES)):
        rows = db.execute(text(query), parameters).mappings().all()
        observed = {
            row["category"]: CatalogDigest(count=row["count"], digest=row["digest"]) for row in rows
        }
        if observed.keys() != categories:
            raise ValueError("Incomplete prepared metadata")
        stages.append(observed)
    return PreparedSnapshot(expressions, stages[0], stages[1])
