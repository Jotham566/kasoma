"""Bounded exact numeric syntax and reviewed answer specifications (FR-GRD-002)."""

import re
from fractions import Fraction
from typing import Literal

from pydantic import Field

from services.identity_contracts import Contract

NumericForm = Literal["DECIMAL", "SCIENTIFIC", "FRACTION"]
DECIMAL = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]{1,2})?$")
FRACTION = re.compile(r"^[+-]?[0-9]+/[0-9]+$")


def parse_number(raw: str) -> tuple[Fraction, NumericForm, int | None]:
    if not 1 <= len(raw) <= 64:
        raise ValueError("Invalid numeric representation")
    raw = raw.strip()
    if FRACTION.fullmatch(raw):
        numerator, denominator = raw.split("/")
        if int(denominator) == 0:
            raise ValueError("Invalid numeric representation")
        value = Fraction(int(numerator), int(denominator))
        form: NumericForm = "FRACTION"
        figures = None
    elif DECIMAL.fullmatch(raw):
        pieces = re.split("[eE]", raw)
        if len(pieces) == 2 and abs(int(pieces[1])) > 12:
            raise ValueError("Numeric exponent outside supported bounds")
        value = Fraction(raw)
        form = "SCIENTIFIC" if len(pieces) == 2 else "DECIMAL"
        mantissa = pieces[0].lstrip("+-")
        digits = mantissa.replace(".", "").lstrip("0")
        if not digits:
            figures = max(1, len(mantissa.split(".")[1]) if "." in mantissa else 1)
        else:
            if "." not in mantissa and form == "DECIMAL":
                digits = digits.rstrip("0")
            figures = len(digits)
    else:
        raise ValueError("Unsupported numeric representation")
    if abs(value) > 10**12:
        raise ValueError("Numeric value outside supported bounds")
    return value, form, figures


class NumericUnit(Contract):
    label: str = Field(max_length=24, pattern=r"^[A-Za-z0-9°µμ/%^ ._-]*$")
    factor: str = Field(min_length=1, max_length=64)
    offset: str = Field(min_length=1, max_length=64)


class NumericSpec(Contract):
    expected_value: str = Field(max_length=64)
    canonical_unit: str = Field(max_length=24)
    units: list[NumericUnit] = Field(min_length=1, max_length=8)
    absolute_tolerance: str = Field(max_length=64)
    relative_tolerance: str = Field(max_length=64)
    accepted_forms: list[NumericForm] = Field(min_length=1, max_length=3)
    significant_figures_policy: Literal["IGNORE", "EXACT"]
    significant_figures: int | None = Field(default=None, ge=1, le=12)


def specification_errors(spec: NumericSpec) -> list[str]:
    errors = []
    for name in ["expected_value", "absolute_tolerance", "relative_tolerance"]:
        try:
            value, _, _ = parse_number(getattr(spec, name))
            if name != "expected_value" and value < 0:
                errors.append(name)
            if name == "relative_tolerance" and value > 1:
                errors.append(name)
        except ValueError:
            errors.append(name)
    labels = [u.label for u in spec.units]
    if len(set(labels)) != len(labels) or any(label != label.strip() for label in labels):
        errors.append("units")
    if spec.canonical_unit not in labels:
        errors.append("canonical_unit")
    for unit in spec.units:
        try:
            factor, _, _ = parse_number(unit.factor)
            offset, _, _ = parse_number(unit.offset)
            if factor <= 0 or (unit.label == spec.canonical_unit and (factor != 1 or offset != 0)):
                errors.append("units")
        except ValueError:
            errors.append("units")
    if len(set(spec.accepted_forms)) != len(spec.accepted_forms):
        errors.append("accepted_forms")
    if spec.significant_figures_policy == "EXACT":
        if spec.significant_figures is None or "FRACTION" in spec.accepted_forms:
            errors.append("significant_figures")
    elif spec.significant_figures is not None:
        errors.append("significant_figures")
    return sorted(set(errors))


def evaluate_numeric(spec: NumericSpec, raw: str, unit_label: str) -> tuple[bool, bool]:
    if specification_errors(spec):
        raise ValueError("Invalid approved numeric specification")
    value, form, figures = parse_number(raw)
    unit = next((u for u in spec.units if u.label == unit_label), None)
    if unit is None or form not in spec.accepted_forms:
        raise ValueError("Unsupported unit or response form")
    converted = value * parse_number(unit.factor)[0] + parse_number(unit.offset)[0]
    expected = parse_number(spec.expected_value)[0]
    tolerance = max(
        parse_number(spec.absolute_tolerance)[0],
        parse_number(spec.relative_tolerance)[0] * abs(expected),
    )
    precise = spec.significant_figures_policy == "IGNORE" or figures == spec.significant_figures
    return abs(converted - expected) <= tolerance, precise
