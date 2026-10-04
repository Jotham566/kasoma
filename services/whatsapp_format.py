"""Lossless bounded channel presentation and response normalization, never grading."""

import re

from services.assessment_contracts import ChoiceResponse, MultipleChoiceResponse, NumericResponse
from services.content_contracts import DraftDocument
from services.numeric import parse_number, specification_errors

MAX_MESSAGE_CHARS = 500
MAX_REPLY_CHARS = 96
RICH_CONTENT = re.compile(
    r"!\[|<\s*(?:img|svg|math)\b|\\(?:includegraphics|begin)\b|\$\$|\\\[", re.I
)


def question_text(document: DraftDocument, position: int, limit: int = MAX_MESSAGE_CHARS) -> str:
    """Caller must check immutable version approval; this checks channel representation only."""
    if "WHATSAPP" not in document.channel_suitability or not 1 <= position <= 5:
        raise ValueError("Question is not channel suitable")
    if not 1 <= limit <= MAX_MESSAGE_CHARS:
        raise ValueError("Invalid message limit")
    parts = [f"Question {position}/5", document.prompt]
    if not document.prompt.strip() or RICH_CONTENT.search(document.prompt):
        raise ValueError("Plain text question required")
    if document.response_type in {"SINGLE_CHOICE", "MULTIPLE_CHOICE"}:
        if not 2 <= len(document.choices) <= 8 or len(
            {choice.id for choice in document.choices}
        ) != len(document.choices):
            raise ValueError("Unsupported choices")
        for index, choice in enumerate(document.choices, 1):
            if not choice.text.strip() or RICH_CONTENT.search(choice.text):
                raise ValueError("Plain text choices required")
            parts.append(f"{index}. {choice.text}")
        parts.append(
            "Reply to this message with "
            + (
                "one option number."
                if document.response_type == "SINGLE_CHOICE"
                else "option numbers separated by commas, e.g. 1,3."
            )
        )
    elif document.response_type == "NUMERIC" and document.numeric_spec:
        if specification_errors(document.numeric_spec):
            raise ValueError("Invalid numeric specification")
        units = [unit.label for unit in document.numeric_spec.units]
        parts.append("Units: " + ", ".join(label or "no unit" for label in units))
        parts.append(
            "Forms: " + ", ".join(form.lower() for form in document.numeric_spec.accepted_forms)
        )
        parts.append("Reply to this message with value | unit (or just a value for no unit).")
        if document.numeric_spec.significant_figures_policy == "EXACT":
            parts.append(f"Use {document.numeric_spec.significant_figures} significant figures.")
    else:
        raise ValueError("Unsupported response format")
    rendered = "\n".join(parts)
    if len(rendered) > limit:
        raise ValueError("Question exceeds channel limit")
    return rendered


def supports(document: DraftDocument, limit: int = MAX_MESSAGE_CHARS) -> bool:
    try:
        question_text(document, 5, limit)
    except ValueError:
        return False
    return True


def parse_reply(
    document: DraftDocument, raw: str
) -> ChoiceResponse | MultipleChoiceResponse | NumericResponse:
    """Call only after binding the provider reply to its exact owned session assignment."""
    if not 1 <= len(raw) <= MAX_REPLY_CHARS or not supports(document):
        raise ValueError("Unsupported reply")
    raw = raw.strip()
    if document.response_type in {"SINGLE_CHOICE", "MULTIPLE_CHOICE"}:
        tokens = [token.strip() for token in raw.split(",")]
        if (
            not 1 <= len(tokens) <= 8
            or len(set(tokens)) != len(tokens)
            or any(re.fullmatch(r"[1-8]", token) is None for token in tokens)
        ):
            raise ValueError("Invalid option numbers")
        indexes = [int(token) - 1 for token in tokens]
        if any(index >= len(document.choices) for index in indexes):
            raise ValueError("Unknown option")
        identifiers = [document.choices[index].id for index in indexes]
        if document.response_type == "SINGLE_CHOICE":
            if len(identifiers) != 1:
                raise ValueError("Select one option")
            return ChoiceResponse(choice_id=identifiers[0])
        return MultipleChoiceResponse(type="MULTIPLE_CHOICE", choice_ids=identifiers)
    if document.response_type == "NUMERIC" and document.numeric_spec:
        parts = [part.strip() for part in raw.split("|")]
        if not 1 <= len(parts) <= 2:
            raise ValueError("Invalid numeric reply")
        value, unit = parts[0], parts[1] if len(parts) == 2 else ""
        _, form, _ = parse_number(value)
        if form not in document.numeric_spec.accepted_forms or unit not in {
            u.label for u in document.numeric_spec.units
        }:
            raise ValueError("Unsupported number or unit")
        return NumericResponse(type="NUMERIC", value=value, unit=unit)
    raise ValueError("Unsupported response format")
