"use client";

import { useState } from "react";
import type { components } from "@kasoma/api-client";
import { NumericFields } from "./numeric-fields";

type Context = components["schemas"]["ContentContext"];
type Document = components["schemas"]["DraftDocument"];
type Version = components["schemas"]["VersionView"];
const input = "block w-full rounded border border-slate-500 p-3 mt-1 mb-4";

export function Editor({
  context,
  selected,
  busy,
  save,
}: {
  context: Context;
  selected: Version | null;
  busy: boolean;
  save: (subject: string, document: Document, reason: string) => Promise<void>;
}) {
  const initial = selected?.document;
  const [format, setFormat] = useState<Document["response_type"]>(
    initial?.response_type ?? "SINGLE_CHOICE",
  );
  const choices = initial?.choices?.length
    ? initial.choices
    : [
        { id: "A", text: "" },
        { id: "B", text: "" },
      ];
  const [subject, setSubject] = useState(
    selected?.subject_id ?? context.subjects[0]?.id ?? "",
  );
  const topics = context.topics.filter((topic) => topic.parent_id === subject);
  const [topic, setTopic] = useState(initial?.topic_id ?? topics[0]?.id ?? "");
  const concepts = context.concepts.filter(
    (concept) => concept.parent_id === topic,
  );
  const [concept, setConcept] = useState(
    initial?.concept_id ?? concepts[0]?.id ?? "",
  );
  function area(label: string, name: string, value = "", max = 4000) {
    return (
      <label>
        {label}
        <textarea
          className={input}
          name={name}
          defaultValue={value}
          maxLength={max}
          rows={3}
        />
      </label>
    );
  }
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        const value = (key: string) => String(data.get(key) ?? "");
        const document: Document = {
          title: value("title"),
          topic_id: topic || null,
          concept_id: concept || null,
          competency_mappings: context.competencies
            .map((entry) => ({
              competency_id: entry.id,
              weight: Number(value(`weight_${entry.id}`)),
            }))
            .filter((entry) => entry.weight > 0),
          learning_outcome_reference: value("learning_outcome_reference"),
          difficulty: value("difficulty") as Document["difficulty"],
          expected_seconds: Number(value("expected_seconds")),
          response_type: format,
          channel_suitability: data.has("whatsapp")
            ? ["WEB", "WHATSAPP"]
            : ["WEB"],
          prompt: value("prompt"),
          choices:
            format === "NUMERIC"
              ? []
              : choices.map((choice) => ({
                  id: choice.id,
                  text: value(`choice_${choice.id}`),
                })),
          correct_choice_id:
            format === "NUMERIC" ? "" : value("correct_choice_id"),
          numeric_spec:
            format === "NUMERIC"
              ? {
                  expected_value: value("numeric_expected"),
                  canonical_unit: value("numeric_canonical"),
                  absolute_tolerance: value("numeric_absolute"),
                  relative_tolerance: value("numeric_relative"),
                  units: Array.from(
                    { length: Number(value("numeric_unit_count")) },
                    (_, i) => ({
                      label: value(`numeric_unit_${i}`),
                      factor: value(`numeric_factor_${i}`),
                      offset: value(`numeric_offset_${i}`),
                    }),
                  ),
                  accepted_forms: data
                    .getAll("numeric_forms")
                    .map(
                      String,
                    ) as components["schemas"]["NumericSpec"]["accepted_forms"],
                  significant_figures_policy: value(
                    "numeric_precision",
                  ) as components["schemas"]["NumericSpec"]["significant_figures_policy"],
                  significant_figures:
                    value("numeric_precision") === "EXACT"
                      ? Number(value("numeric_figures"))
                      : null,
                }
              : null,
          maximum_points: Number(value("maximum_points")),
          partial_credit: "ALL_OR_NOTHING",
          worked_solution: value("worked_solution"),
          remediation: value("remediation"),
          prerequisite_concept_ids: data.getAll("prerequisites").map(String),
          source: value("source"),
          rights_status: value("rights_status") as Document["rights_status"],
          rights_evidence: value("rights_evidence"),
          rights_conditions: value("rights_conditions"),
          high_risk: data.has("high_risk"),
        };
        void save(subject, document, value("change_reason"));
      }}
    >
      <h2 className="text-xl font-semibold my-4">
        {selected ? "Edit draft" : "Create draft"}
      </h2>
      <p className="mb-4">
        Text-only choice or numeric response. Drafts may be incomplete;
        submission validates every required field. No media uploads or imports
        in this slice.
      </p>
      <label>
        Title
        <input
          name="title"
          className={input}
          defaultValue={initial?.title ?? ""}
          maxLength={160}
        />
      </label>
      <label>
        Subject
        <select
          className={input}
          value={subject}
          disabled={!!selected}
          onChange={(event) => {
            const subject = event.target.value;
            setSubject(subject);
            const next =
              context.topics.find((entry) => entry.parent_id === subject)?.id ??
              "";
            setTopic(next);
            setConcept(
              context.concepts.find((entry) => entry.parent_id === next)?.id ??
                "",
            );
          }}
        >
          {context.subjects.map((entry) => (
            <option key={entry.id} value={entry.id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Topic cluster
        <select
          className={input}
          value={topic}
          onChange={(event) => {
            setTopic(event.target.value);
            setConcept(
              context.concepts.find(
                (entry) => entry.parent_id === event.target.value,
              )?.id ?? "",
            );
          }}
        >
          {topics.map((entry) => (
            <option key={entry.id} value={entry.id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Primary concept
        <select
          className={input}
          value={concept}
          onChange={(event) => setConcept(event.target.value)}
        >
          {concepts.map((entry) => (
            <option key={entry.id} value={entry.id}>
              {entry.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Learning-outcome reference
        <input
          className={input}
          name="learning_outcome_reference"
          key={concept}
          defaultValue={
            initial?.concept_id === concept
              ? initial.learning_outcome_reference
              : (concepts.find((entry) => entry.id === concept)
                  ?.syllabus_reference ?? "")
          }
          maxLength={300}
        />
      </label>
      <fieldset>
        <legend>Competency weights (sum to 1; use 0 for unmapped)</legend>
        {context.competencies.map((entry, index) => (
          <label key={entry.id}>
            {entry.name} weight
            <input
              className={input}
              name={`weight_${entry.id}`}
              type="number"
              min={0}
              max={1}
              step="any"
              defaultValue={
                initial
                  ? (initial.competency_mappings?.find(
                      (mapping) => mapping.competency_id === entry.id,
                    )?.weight ?? 0)
                  : index === 0
                    ? 1
                    : 0
              }
            />
          </label>
        ))}
      </fieldset>
      <label>
        Difficulty
        <select
          className={input}
          name="difficulty"
          defaultValue={initial?.difficulty ?? "FOUNDATIONAL"}
        >
          <option value="FOUNDATIONAL">Foundational</option>
          <option value="STANDARD">Standard</option>
          <option value="CHALLENGING">Challenging</option>
        </select>
      </label>
      <label>
        Expected time in seconds
        <input
          className={input}
          type="number"
          name="expected_seconds"
          min={10}
          max={3600}
          defaultValue={initial?.expected_seconds ?? 60}
          required
        />
      </label>
      {area("Question prompt", "prompt", initial?.prompt)}
      <label>
        Response format
        <select
          className={input}
          value={format}
          onChange={(e) =>
            setFormat(e.target.value as Document["response_type"])
          }
        >
          <option value="SINGLE_CHOICE">Single choice</option>
          <option value="NUMERIC">Numeric</option>
        </select>
      </label>
      {format === "NUMERIC" ? (
        <NumericFields initial={initial?.numeric_spec} />
      ) : (
        <>
          {choices.map((choice) => (
            <div key={choice.id}>
              {area(`Option ${choice.id}`, `choice_${choice.id}`, choice.text)}
            </div>
          ))}
          <label>
            Correct option
            <select
              className={input}
              name="correct_choice_id"
              defaultValue={initial?.correct_choice_id ?? ""}
            >
              <option value="">Not yet specified</option>
              {choices.map((choice) => (
                <option key={choice.id} value={choice.id}>
                  {choice.id}
                </option>
              ))}
            </select>
          </label>
        </>
      )}
      <label>
        Maximum points
        <input
          className={input}
          name="maximum_points"
          type="number"
          min={1}
          max={20}
          required
          defaultValue={initial?.maximum_points ?? 1}
        />
      </label>
      <p>Scoring policy: all or nothing.</p>
      {area("Worked solution", "worked_solution", initial?.worked_solution)}
      {area("Feedback and remediation", "remediation", initial?.remediation)}
      <fieldset className="mb-4">
        <legend>Prerequisites (leave empty when none apply)</legend>
        {context.concepts
          .filter(
            (entry) =>
              entry.id !== concept &&
              context.topics.some(
                (t) => t.id === entry.parent_id && t.parent_id === subject,
              ),
          )
          .map((entry) => (
            <label className="flex min-h-11 items-center gap-3" key={entry.id}>
              <input
                name="prerequisites"
                type="checkbox"
                value={entry.id}
                defaultChecked={initial?.prerequisite_concept_ids?.includes(
                  entry.id,
                )}
              />
              {entry.syllabus_reference}
            </label>
          ))}
      </fieldset>
      {area("Source and provenance", "source", initial?.source, 500)}
      <label>
        Rights status
        <select
          className={input}
          name="rights_status"
          defaultValue={initial?.rights_status ?? "UNKNOWN_BLOCKED"}
        >
          <option value="UNKNOWN_BLOCKED">Unknown — publication blocked</option>
          <option value="ORIGINAL_KASOMA">Original Kasoma</option>
          <option value="LICENSED">Licensed</option>
          <option value="PUBLIC_DOMAIN_CONFIRMED">
            Public domain confirmed
          </option>
          <option value="PERMISSION_CONFIRMED">Permission confirmed</option>
          <option value="REFERENCE_ONLY_NO_REPRODUCTION">
            Reference only — no reproduction
          </option>
        </select>
      </label>
      {area(
        "Rights evidence",
        "rights_evidence",
        initial?.rights_evidence,
        1000,
      )}
      {area(
        "Rights conditions",
        "rights_conditions",
        initial?.rights_conditions,
        1000,
      )}
      <label className="flex min-h-11 items-center gap-3">
        <input
          type="checkbox"
          name="whatsapp"
          defaultChecked={initial?.channel_suitability?.includes("WHATSAPP")}
        />
        Suitable for simple WhatsApp delivery as well as web
      </label>
      <label className="flex min-h-11 items-center gap-3">
        <input
          type="checkbox"
          name="high_risk"
          defaultChecked={initial?.high_risk}
        />
        High risk: require two independent reviewers
      </label>
      <label>
        Change reason
        <input
          className={input}
          name="change_reason"
          maxLength={500}
          required
        />
      </label>
      <button
        disabled={busy}
        className="rounded bg-slate-900 text-white px-5 py-3 my-3 disabled:opacity-50"
      >
        Save draft
      </button>
    </form>
  );
}
