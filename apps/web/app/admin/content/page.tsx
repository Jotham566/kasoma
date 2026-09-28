"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";
import { Editor } from "./editor";

type Context = components["schemas"]["ContentContext"];
type Version = components["schemas"]["VersionView"];
type Document = components["schemas"]["DraftDocument"];
type Review = components["schemas"]["ReviewView"];
type ReviewInput = components["schemas"]["ReviewInput"];
const api = () => apiClient("", crypto.randomUUID());
const button =
  "rounded border border-slate-600 px-4 py-3 my-2 disabled:opacity-50";
const labels: Record<string, string> = {
  curriculum: "Curriculum and learning-outcome alignment",
  competency_difficulty: "Competency and difficulty tags",
  factual_accuracy: "Scenario and factual accuracy",
  clarity: "Clear interpretation",
  answer_rubric: "Complete answer specification",
  units_precision: "Units and precision checked or not applicable",
  partial_credit: "Partial-credit policy checked",
  worked_solution: "Worked solution is accurate",
  feedback: "Feedback, hints and misconception handling",
  equivalence: "Equivalence checked or no equivalence claimed",
  language_age: "Clear, age-appropriate language",
  accessibility: "Accessible text and media",
  rights: "Rights evidence and conditions",
  channel: "Channel suitability",
  safety: "No sensitive, discriminatory or unsafe content",
};
export default function ContentWorkspace() {
  const [context, setContext] = useState<Context | null>(null);
  const [items, setItems] = useState<Version[]>([]);
  const [selected, setSelected] = useState<Version | null>(null);
  const [history, setHistory] = useState<Review[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [status, setStatus] = useState("Checking staff access…");
  const [busy, setBusy] = useState(false);
  const retry = useRef<{ request: string; key: string } | null>(null);
  useEffect(() => {
    let active = true;
    void api()
      .GET("/api/v1/admin/content-context")
      .then(async (result) => {
        if (!active) return;
        if (!result.data) {
          setStatus(
            "Staff access required. Sign in with a provisioned account.",
          );
          return;
        }
        setContext(result.data);
        const list = await api().GET("/api/v1/admin/items");
        if (!active) return;
        setItems(list.data?.data ?? []);
        setCursor(list.data?.next_cursor ?? null);
        setStatus("Staff workspace ready.");
      })
      .catch(() => {
        if (active) setStatus("Connection interrupted. Reload to try again.");
      });
    return () => {
      active = false;
    };
  }, []);
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setStatus("Working…");
    try {
      await action();
    } catch {
      setStatus(
        "Connection interrupted. Your inputs are preserved; retry the action.",
      );
    } finally {
      setBusy(false);
    }
  }
  function key(request: object) {
    const serialized = JSON.stringify(request);
    if (retry.current?.request !== serialized)
      retry.current = { request: serialized, key: crypto.randomUUID() };
    return { "Idempotency-Key": retry.current.key };
  }
  async function result(
    data: Version | undefined,
    response: Response,
    failure?: components["schemas"]["ErrorEnvelope"],
  ) {
    if (!data) {
      const error = failure;
      const code = error?.error?.code;
      const fields = error?.error?.field_errors
        ?.map((value) => value.field)
        .join(", ");
      setStatus(
        response.status === 401
          ? "Sign in again for this staff action."
          : code === "VERSION_CONFLICT"
            ? "This version changed. Reload the selected item before editing."
            : code === "SELF_REVIEW_FORBIDDEN"
              ? "The author cannot review their own item."
              : fields
                ? `Review these fields: ${fields}.`
                : "Action denied. Check your role, review checklist or recent sign-in.",
      );
      return;
    }
    retry.current = null;
    setSelected(data);
    setItems((old) => [data, ...old.filter((v) => v.id !== data.id)]);
    setStatus(`Version ${data.version}: ${data.status}.`);
    const reviews = await api().GET(
      "/api/v1/admin/item-versions/{version_id}/reviews",
      { params: { path: { version_id: data.id } } },
    );
    setHistory(reviews.data ?? []);
  }
  async function select(item: Version) {
    const found = await api().GET("/api/v1/admin/item-versions/{version_id}", {
      params: { path: { version_id: item.id } },
    });
    await result(found.data, found.response, found.error);
  }
  async function save(subject: string, document: Document, reason: string) {
    await run(async () => {
      if (selected) {
        const body = {
          expected_revision: selected.revision,
          document,
          change_reason: reason,
        };
        const response = await api().PATCH(
          "/api/v1/admin/item-versions/{version_id}",
          {
            body,
            headers: key({ target: selected.id, body }),
            params: {
              path: { version_id: selected.id },
              header: {
                "Idempotency-Key": key({ target: selected.id, body })[
                  "Idempotency-Key"
                ],
              },
            },
          },
        );
        await result(response.data, response.response, response.error);
      } else {
        const body = { subject_id: subject, document, change_reason: reason };
        const response = await api().POST("/api/v1/admin/items", {
          body,
          params: { header: key(body) },
        });
        await result(response.data, response.response, response.error);
      }
    });
  }
  async function transition(action: "submit" | "retire", reason: string) {
    if (!selected) return;
    const body = { expected_revision: selected.revision, reason };
    const response = await api().POST(
      action === "submit"
        ? "/api/v1/admin/item-versions/{version_id}/submit"
        : "/api/v1/admin/item-versions/{version_id}/retire",
      {
        body,
        params: {
          path: { version_id: selected.id },
          header: key({ action, target: selected.id, body }),
        },
      },
    );
    await result(response.data, response.response, response.error);
  }
  const author =
    context?.roles.includes("CONTENT_AUTHOR") &&
    (!selected || selected.author_id === context.actor_id);
  return (
    <main className="mx-auto max-w-4xl p-6">
      <Link
        className="underline inline-flex min-h-11 items-center"
        href="/onboarding"
      >
        Sign in or refresh staff verification
      </Link>
      <h1 className="text-3xl font-semibold my-6">Content workspace</h1>
      <p>
        Synthetic development only. Workflow approval does not certify academic
        quality or count toward the production content target.
      </p>
      <p role="status" aria-live="polite" className="border rounded p-4 my-4">
        {status}
      </p>
      {context && (
        <>
          <section aria-labelledby="queue">
            <h2 id="queue" className="text-xl font-semibold">
              Items and review queue
            </h2>
            {!items.length && <p className="my-4">No items yet.</p>}
            <ul>
              {items.map((item) => (
                <li key={item.id}>
                  <button
                    disabled={busy}
                    className={button}
                    onClick={() => void run(() => select(item))}
                  >
                    {item.document.title || "Untitled draft"} — v{item.version}{" "}
                    · {item.status}
                  </button>
                </li>
              ))}
            </ul>
            {cursor && (
              <button
                className={button}
                disabled={busy}
                onClick={() =>
                  void run(async () => {
                    const list = await api().GET("/api/v1/admin/items", {
                      params: { query: { cursor } },
                    });
                    if (!list.data) throw new Error();
                    setItems((old) => [
                      ...old,
                      ...list.data!.data.filter(
                        (entry) => !old.some((v) => v.id === entry.id),
                      ),
                    ]);
                    setCursor(list.data.next_cursor);
                    setStatus("More items loaded.");
                  })
                }
              >
                Load more
              </button>
            )}
            {context.roles.includes("CONTENT_AUTHOR") && (
              <button
                className={button}
                disabled={busy}
                onClick={() => {
                  setSelected(null);
                  setHistory([]);
                  retry.current = null;
                  setStatus("New draft.");
                }}
              >
                New draft
              </button>
            )}
            {selected && (
              <button
                className={button}
                disabled={busy}
                onClick={() => void run(() => select(selected))}
              >
                Reload selected item
              </button>
            )}
          </section>
          {author && (!selected || selected.status === "DRAFT") && (
            <Editor
              key={selected ? `${selected.id}:${selected.revision}` : "new"}
              context={context}
              selected={selected}
              busy={busy}
              save={save}
            />
          )}
          {selected && (
            <section aria-labelledby="preview">
              <h2 id="preview" className="text-xl font-semibold my-4">
                Staff preview — version {selected.version}, {selected.status}
              </h2>
              <p className="my-4 whitespace-pre-wrap">
                {selected.document.prompt || "Prompt not supplied."}
              </p>
              <ul>
                {selected.document.choices?.map((choice) => (
                  <li key={choice.id}>
                    {choice.id}. {choice.text}
                  </li>
                ))}
              </ul>
              {selected.document.response_type === "NUMERIC" &&
              selected.document.numeric_spec ? (
                <section
                  aria-label="Numeric answer preview"
                  className="space-y-2 my-4"
                >
                  <p>
                    Expected value:{" "}
                    {selected.document.numeric_spec.expected_value}{" "}
                    {selected.document.numeric_spec.canonical_unit}
                  </p>
                  <p>
                    Absolute tolerance:{" "}
                    {selected.document.numeric_spec.absolute_tolerance};
                    relative tolerance:{" "}
                    {selected.document.numeric_spec.relative_tolerance}
                  </p>
                  <p>
                    Accepted forms:{" "}
                    {selected.document.numeric_spec.accepted_forms.join(", ")}
                  </p>
                  <p>
                    Precision:{" "}
                    {selected.document.numeric_spec.significant_figures_policy}{" "}
                    {selected.document.numeric_spec.significant_figures ?? ""}
                  </p>
                  <ul>
                    {selected.document.numeric_spec.units.map((u) => (
                      <li key={u.label}>
                        Unit {u.label || "(dimensionless)"}: factor {u.factor},
                        offset {u.offset}
                      </li>
                    ))}
                  </ul>
                  <p>Maximum points: {selected.document.maximum_points}</p>
                </section>
              ) : (
                <p className="my-4">
                  Correct option:{" "}
                  {selected.document.correct_choice_id || "Missing"}. Maximum
                  points: {selected.document.maximum_points}.
                </p>
              )}
              <p className="whitespace-pre-wrap">
                Worked solution: {selected.document.worked_solution}
              </p>
              <p className="whitespace-pre-wrap">
                Remediation: {selected.document.remediation}
              </p>
              <section aria-label="Equivalent item claims">
                <h3 className="font-semibold">Equivalence for transfer</h3>
                <p>
                  Review both scenarios; reject pairs answered by recalling
                  prior wording or answers.
                </p>
                <ul>
                  {selected.document.equivalents?.map((claim) => (
                    <li key={claim.version_id}>
                      <button
                        className={button}
                        disabled={busy}
                        onClick={() =>
                          void run(async () => {
                            const other = await api().GET(
                              "/api/v1/admin/item-versions/{version_id}",
                              {
                                params: {
                                  path: { version_id: claim.version_id },
                                },
                              },
                            );
                            if (!other.data) throw new Error();
                            await result(
                              other.data,
                              other.response,
                              other.error,
                            );
                          })
                        }
                      >
                        Inspect equivalent version {claim.version_id}
                      </button>{" "}
                      Confidence: {claim.confidence}
                    </li>
                  ))}
                </ul>
              </section>
              <section aria-label="Authored hints">
                <h3 className="font-semibold">Hints</h3>
                <p>
                  Confirm that hints scaffold thinking without revealing the
                  answer or worked solution.
                </p>
                <ol>
                  {selected.document.hints?.map((hint, i) => (
                    <li key={i}>
                      Level {i + 1}: {hint}
                    </li>
                  ))}
                </ol>
              </section>
              <dl className="my-4">
                <dt>Subject / topic / concept</dt>
                <dd>
                  {
                    context.subjects.find(
                      (entry) => entry.id === selected.subject_id,
                    )?.name
                  }{" "}
                  /{" "}
                  {
                    context.topics.find(
                      (entry) => entry.id === selected.document.topic_id,
                    )?.name
                  }{" "}
                  /{" "}
                  {
                    context.concepts.find(
                      (entry) => entry.id === selected.document.concept_id,
                    )?.name
                  }
                </dd>
                <dt>Competency weights</dt>
                <dd>
                  {selected.document.competency_mappings
                    ?.map(
                      (mapping) =>
                        `${context.competencies.find((entry) => entry.id === mapping.competency_id)?.name}: ${mapping.weight}`,
                    )
                    .join(", ")}
                </dd>
                <dt>Difficulty and expected time</dt>
                <dd>
                  {selected.document.difficulty};{" "}
                  {selected.document.expected_seconds} seconds
                </dd>
                <dt>Channels and scoring</dt>
                <dd>
                  {selected.document.channel_suitability?.join(", ")};{" "}
                  {selected.document.partial_credit}
                </dd>
                <dt>Prerequisites</dt>
                <dd>
                  {selected.document.prerequisite_concept_ids
                    ?.map(
                      (id) =>
                        context.concepts.find((entry) => entry.id === id)
                          ?.syllabus_reference,
                    )
                    .join(", ") || "None declared"}
                </dd>
                <dt>Equivalence and misconceptions</dt>
                <dd>
                  No equivalence relationship or misconception mapping claimed
                  in this initial fixture format.
                </dd>
                <dt>Learning-outcome reference</dt>
                <dd>{selected.document.learning_outcome_reference}</dd>
                <dt>Rights</dt>
                <dd>
                  {selected.document.rights_status}:{" "}
                  {selected.document.rights_evidence}
                </dd>
                <dt>Conditions</dt>
                <dd>{selected.document.rights_conditions}</dd>
                <dt>Provenance</dt>
                <dd>{selected.document.source}</dd>
              </dl>
              <p>
                {selected.requires_second_review
                  ? "Two independent reviewers required."
                  : "One independent reviewer required."}{" "}
                Current approvals: {selected.approval_count}.
              </p>
              {author && selected.status === "DRAFT" && (
                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    const form = new FormData(event.currentTarget);
                    void run(() =>
                      transition("submit", String(form.get("reason"))),
                    );
                  }}
                >
                  <label>
                    Submission reason
                    <input
                      className="block border p-3 my-2 w-full"
                      name="reason"
                      maxLength={500}
                      required
                    />
                  </label>
                  <button className={button} disabled={busy}>
                    Submit for review
                  </button>
                </form>
              )}
              {context.roles.includes("ACADEMIC_REVIEWER") &&
                selected.status === "IN_REVIEW" && (
                  <form
                    key={`review:${selected.id}:${selected.revision}`}
                    onSubmit={(event) => {
                      event.preventDefault();
                      const form = new FormData(event.currentTarget);
                      const submitter = (event.nativeEvent as SubmitEvent)
                        .submitter as HTMLButtonElement;
                      const body: ReviewInput = {
                        expected_revision: selected.revision,
                        reason: String(form.get("reason")),
                        decision: submitter.value as "APPROVE" | "RETURN",
                        checklist: form.getAll(
                          "checklist",
                        ) as ReviewInput["checklist"],
                        require_second_review: form.has("second"),
                      };
                      void run(async () => {
                        const response = await api().POST(
                          "/api/v1/admin/item-versions/{version_id}/review",
                          {
                            body,
                            params: {
                              path: { version_id: selected.id },
                              header: key({
                                action: "review",
                                target: selected.id,
                                body,
                              }),
                            },
                          },
                        );
                        await result(
                          response.data,
                          response.response,
                          response.error,
                        );
                      });
                    }}
                  >
                    <fieldset>
                      <legend className="font-semibold my-4">
                        Independent academic checklist
                      </legend>
                      {context.checklist.map((entry) => (
                        <label
                          key={entry}
                          className="flex min-h-11 items-center gap-3"
                        >
                          <input
                            type="checkbox"
                            name="checklist"
                            value={entry}
                          />
                          {labels[entry] ?? entry}
                        </label>
                      ))}
                    </fieldset>
                    <label className="flex min-h-11 items-center gap-3">
                      <input type="checkbox" name="second" />
                      Disputed or high-risk: require a second reviewer
                    </label>
                    <label>
                      Review comments
                      <input
                        className="block border p-3 my-2 w-full"
                        name="reason"
                        maxLength={500}
                        required
                      />
                    </label>
                    {selected.author_id === context.actor_id && (
                      <p>
                        You authored this item. Another reviewer must decide.
                      </p>
                    )}
                    <button
                      className={button}
                      disabled={busy || selected.author_id === context.actor_id}
                      type="submit"
                      value="APPROVE"
                    >
                      Approve
                    </button>{" "}
                    <button
                      className={button}
                      disabled={busy || selected.author_id === context.actor_id}
                      type="submit"
                      value="RETURN"
                    >
                      Return for correction
                    </button>
                  </form>
                )}
              {selected.status === "APPROVED" &&
                context.roles.some((role) =>
                  ["ACADEMIC_REVIEWER", "ADMIN"].includes(role),
                ) && (
                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      const form = new FormData(event.currentTarget);
                      void run(() =>
                        transition("retire", String(form.get("reason"))),
                      );
                    }}
                  >
                    <label>
                      Retirement reason
                      <input
                        className="block border p-3 my-2 w-full"
                        name="reason"
                        maxLength={500}
                        required
                      />
                    </label>
                    <button className={button} disabled={busy}>
                      Retire version
                    </button>
                  </form>
                )}
              {author && ["APPROVED", "RETIRED"].includes(selected.status) && (
                <button
                  className={button}
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      const body = {
                        subject_id: selected.subject_id,
                        document: selected.document,
                        source_version_id: selected.id,
                        change_reason: "Create a corrected draft version",
                      };
                      const response = await api().POST("/api/v1/admin/items", {
                        body,
                        params: { header: key(body) },
                      });
                      await result(
                        response.data,
                        response.response,
                        response.error,
                      );
                    })
                  }
                >
                  Create next draft version
                </button>
              )}
              <h3 className="font-semibold mt-6">Review history</h3>
              {!history.length ? (
                <p>No reviews yet.</p>
              ) : (
                <ul>
                  {history.map((entry, index) => (
                    <li className="my-3" key={index}>
                      {entry.decision}: {entry.reason} (
                      {new Date(entry.created_at).toLocaleString("en-UG", {
                        timeZone: "Africa/Kampala",
                      })}
                      )
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}
        </>
      )}
    </main>
  );
}
