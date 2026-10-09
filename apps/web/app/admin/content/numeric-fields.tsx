"use client";

import { useState } from "react";
import type { components } from "@kasoma/api-client";

type Spec = components["schemas"]["NumericSpec"];
const input = "ui-input mb-4";

export function NumericFields({ initial }: { initial?: Spec | null }) {
  const [count, setCount] = useState(initial?.units.length ?? 1);
  const [precision, setPrecision] = useState(
    initial?.significant_figures_policy ?? "IGNORE",
  );
  function field(label: string, name: string, value: string, max = 64) {
    return (
      <label>
        {label}
        <input
          className={input}
          name={name}
          defaultValue={value}
          maxLength={max}
        />
      </label>
    );
  }
  return (
    <fieldset className="space-y-3">
      <legend>Numeric answer specification</legend>
      <p>
        Review every conversion and tolerance. Values use exact arithmetic;
        accepted boundaries are inclusive. No conversion is inferred.
      </p>
      {field(
        "Expected numeric value",
        "numeric_expected",
        initial?.expected_value ?? "",
      )}
      {field(
        "Canonical unit (empty for dimensionless)",
        "numeric_canonical",
        initial?.canonical_unit ?? "",
        24,
      )}
      {field(
        "Absolute tolerance in canonical units",
        "numeric_absolute",
        initial?.absolute_tolerance ?? "0",
      )}
      {field(
        "Relative tolerance (0 to 1)",
        "numeric_relative",
        initial?.relative_tolerance ?? "0",
      )}
      <p>
        Allowed error is the greater of absolute tolerance and relative
        tolerance × absolute expected value.
      </p>
      <input type="hidden" name="numeric_unit_count" value={count} />
      {Array.from({ length: count }, (_, index) => (
        <fieldset key={index} className="rounded border p-3">
          <legend>Allowed unit {index + 1}</legend>
          {field(
            `Unit ${index + 1} label`,
            `numeric_unit_${index}`,
            initial?.units[index]?.label ?? "",
            24,
          )}
          {field(
            `Unit ${index + 1} factor`,
            `numeric_factor_${index}`,
            initial?.units[index]?.factor ?? "1",
          )}
          {field(
            `Unit ${index + 1} offset`,
            `numeric_offset_${index}`,
            initial?.units[index]?.offset ?? "0",
          )}
        </fieldset>
      ))}
      <p>
        Canonical value = entered value × factor + offset. The canonical unit
        needs factor 1 and offset 0. Labels are case-sensitive.
      </p>
      <button
        className="min-h-11 border rounded px-3"
        type="button"
        disabled={count >= 8}
        onClick={() => setCount(count + 1)}
      >
        Add allowed unit
      </button>
      <button
        className="min-h-11 border rounded px-3"
        type="button"
        disabled={count <= 1}
        onClick={() => setCount(count - 1)}
      >
        Remove last unit
      </button>
      <fieldset>
        <legend>Accepted numeric forms</legend>
        {(["DECIMAL", "SCIENTIFIC", "FRACTION"] as const).map((form) => (
          <label key={form} className="flex min-h-11 items-center gap-3">
            <input
              type="checkbox"
              name="numeric_forms"
              value={form}
              defaultChecked={
                initial?.accepted_forms.includes(form) ?? form === "DECIMAL"
              }
            />
            {form}
          </label>
        ))}
      </fieldset>
      <label>
        Significant-figure policy
        <select
          className={input}
          name="numeric_precision"
          value={precision}
          onChange={(e) =>
            setPrecision(e.target.value as Spec["significant_figures_policy"])
          }
        >
          <option value="IGNORE">Ignore significant figures</option>
          <option value="EXACT">Require an exact count</option>
        </select>
      </label>
      {precision === "EXACT" && (
        <label>
          Required significant figures
          <input
            className={input}
            name="numeric_figures"
            type="number"
            min={1}
            max={12}
            defaultValue={initial?.significant_figures ?? 3}
            required
          />
        </label>
      )}
      <p>
        Exact precision excludes fractions. Trailing zeros count after a decimal
        point or in a scientific mantissa; integer trailing zeros do not. For
        zero, count decimal places, with a minimum of one. Precision applies
        before conversion.
      </p>
    </fieldset>
  );
}
