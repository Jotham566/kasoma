"use client";

import { useId } from "react";
import type { components } from "@kasoma/api-client";

type Rubric = components["schemas"]["RubricDraft"];
type Criterion = components["schemas"]["RubricCriterion"];
const input = "block w-full rounded border border-slate-500 p-3 mt-1 mb-4";
const button =
  "min-h-11 rounded border border-slate-500 px-4 py-2 disabled:opacity-50";
const empty = (id: string): Criterion => ({
  criterion_id: id,
  maximum_points: 1,
  criterion_text: "",
  acceptable_evidence: [""],
  common_errors: [],
  prohibited_inferences: [],
});

export function RubricFields({
  value,
  onChange,
}: {
  value: Rubric | null;
  onChange: (value: Rubric | null) => void;
}) {
  const fieldId = useId();
  const rows = value?.criteria ?? [];
  function change(index: number, patch: Partial<Criterion>) {
    onChange({
      criteria: rows.map((row, i) =>
        i === index ? { ...row, ...patch } : row,
      ),
    });
  }
  function add() {
    let id = 1;
    while (rows.some((row) => row.criterion_id === `R${id}`)) id += 1;
    onChange({ criteria: [...rows, empty(`R${id}`)] });
  }
  const lists = [
    ["acceptable_evidence", "Acceptable evidence"],
    ["common_errors", "Common error"],
    ["prohibited_inferences", "Prohibited inference"],
  ] as const;
  return (
    <section aria-label="Short-text rubric" className="space-y-4">
      <p>
        Short text is available for authoring and review only. Learner delivery
        remains disabled pending grading approval.
      </p>
      <p>
        You can save a draft without a rubric. Complete each included criterion
        before saving, and make its points sum to the item maximum before
        review.
      </p>
      {rows.map((row, index) => (
        <fieldset key={index} className="border p-4">
          <legend>Criterion {index + 1}</legend>
          <label>
            Criterion reference
            <input
              className={input}
              value={row.criterion_id}
              maxLength={64}
              pattern="[A-Za-z][A-Za-z0-9_-]{0,63}"
              required
              onChange={(event) =>
                change(index, { criterion_id: event.target.value })
              }
            />
          </label>
          <label htmlFor={`${fieldId}-${index}-text`}>Criterion text</label>
          <textarea
            id={`${fieldId}-${index}-text`}
            className={input}
            value={row.criterion_text}
            maxLength={2000}
            required
            onChange={(event) =>
              change(index, { criterion_text: event.target.value })
            }
          />
          <label>
            Criterion points
            <input
              className={input}
              type="number"
              min={1}
              max={20}
              step={1}
              required
              value={row.maximum_points}
              onChange={(event) =>
                change(index, { maximum_points: Number(event.target.value) })
              }
            />
          </label>
          {lists.map(([field, label]) => (
            <fieldset key={field} className="space-y-2 mb-4">
              <legend>
                {label}
                {field === "acceptable_evidence"
                  ? " (at least one)"
                  : " (optional)"}
              </legend>
              {row[field].map((entry, position) => (
                <div key={position}>
                  <label htmlFor={`${fieldId}-${index}-${field}-${position}`}>
                    {label} {position + 1}
                  </label>
                  <textarea
                    id={`${fieldId}-${index}-${field}-${position}`}
                    className={input}
                    value={entry}
                    maxLength={2000}
                    required
                    onChange={(event) =>
                      change(index, {
                        [field]: row[field].map((text, i) =>
                          i === position ? event.target.value : text,
                        ),
                      })
                    }
                  />
                  <button
                    className={button}
                    type="button"
                    disabled={
                      field === "acceptable_evidence" && row[field].length === 1
                    }
                    onClick={() =>
                      change(index, {
                        [field]: row[field].filter((_, i) => i !== position),
                      })
                    }
                  >
                    Remove {label.toLowerCase()} {position + 1}
                  </button>
                </div>
              ))}
              <button
                className={button}
                type="button"
                disabled={row[field].length >= 10}
                onClick={() => change(index, { [field]: [...row[field], ""] })}
              >
                Add {label.toLowerCase()}
              </button>
            </fieldset>
          ))}
          <button
            className={button}
            type="button"
            onClick={() => {
              const criteria = rows.filter((_, i) => i !== index);
              onChange(criteria.length ? { criteria } : null);
            }}
          >
            Remove criterion {index + 1}
          </button>
        </fieldset>
      ))}
      <button
        className={button}
        type="button"
        disabled={rows.length >= 20}
        onClick={add}
      >
        Add criterion
      </button>
    </section>
  );
}
