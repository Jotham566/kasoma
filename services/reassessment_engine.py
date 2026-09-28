"""FR-GRD-008: deterministic text-only selection safeguards; no academic claims."""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID

from services.content_contracts import DraftDocument

CONFIG: dict[str, Any] = {
    "version": "reassessment-v1",
    "sequence_threshold": 0.85,
    "word_overlap_threshold": 0.80,
}


def tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"\d+(?:[.,]\d+)*", " number ", normalized)
    return re.findall(r"\w+", normalized)


def near_duplicate(left: str, right: str) -> bool:
    a, b = tokens(left), tokens(right)
    union = set(a) | set(b)
    return (
        not union
        or SequenceMatcher(None, a, b, autojunk=False).ratio() >= CONFIG["sequence_threshold"]
        or len(set(a) & set(b)) / len(union) >= CONFIG["word_overlap_threshold"]
    )


def primary(document: DraftDocument) -> UUID | None:
    mappings = sorted(document.competency_mappings, key=lambda m: (-m.weight, str(m.competency_id)))
    return mappings[0].competency_id if mappings else None


def same_skill(left: DraftDocument, right: DraftDocument) -> bool:
    return (
        left.concept_id is not None
        and left.concept_id == right.concept_id
        and primary(left) is not None
        and primary(left) == primary(right)
        and left.difficulty == right.difficulty
    )


def select_candidate(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot["configuration"] != CONFIG:
        raise ValueError("Unsupported reassessment configuration")
    return min(snapshot["candidates"], key=lambda c: (c["basis"] != "EQUIVALENT", c["version_id"]))
