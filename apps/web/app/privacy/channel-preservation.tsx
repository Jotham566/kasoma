"use client";

import { useId, useRef, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type S = components["schemas"];
type Selected = S["PreservationSource"] & S["PreservationVersion"];
type Pending = { key: string; body: S["PreservationCapture"] };
const uuid = "[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}";
const api = () => apiClient("", crypto.randomUUID());
function check<T>(value: { data?: T; error?: S["ErrorEnvelope"] }): T {
  if (!value.data) throw new Error(value.error?.error.code ?? "UNAVAILABLE");
  return value.data;
}

export function ChannelPreservation({
  target,
  onCaptured,
  onAttempt,
}: {
  target: string;
  onCaptured: () => Promise<void>;
  onAttempt: () => void;
}) {
  const id = useId();
  const form = useRef<HTMLFormElement>(null);
  const sourceFields = useRef<HTMLFieldSetElement>(null);
  const [selected, setSelected] = useState<Selected | null>(null);
  const [pending, setPending] = useState<Pending | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  function clearSelection() {
    setSelected(null);
    const affirmative = form.current?.elements.namedItem("affirmative");
    if (affirmative instanceof HTMLInputElement) affirmative.checked = false;
  }
  function failure(error: unknown) {
    const code = error instanceof Error ? error.message : "UNAVAILABLE";
    if (
      [
        "AUTH_REQUIRED",
        "REAUTH_REQUIRED",
        "FORBIDDEN",
        "REVIEW_OWNERSHIP_REQUIRED",
        "SELF_REVIEW_FORBIDDEN",
      ].includes(code)
    ) {
      setPending(null);
      clearSelection();
      form.current?.reset();
      setStatus(
        "A recent sign-in by the independent administrator who claimed this request is required.",
      );
    } else if (
      [
        "RESOURCE_NOT_FOUND",
        "SOURCE_VERSION_CONFLICT",
        "HOLD_TARGET_UNAVAILABLE",
        "HOLD_END_REQUIRED",
        "IDEMPOTENCY_CONFLICT",
        "REQUEST_COMPLETED",
        "VALIDATION_ERROR",
      ].includes(code)
    ) {
      setPending(null);
      clearSelection();
      setStatus(
        "The source or decision could not be accepted. Check the exact source, current version and future end date again.",
      );
    } else if (code === "RATE_LIMITED") {
      setStatus("Too many requests. Wait before retrying the same operation.");
    } else {
      setStatus(
        "Could not confirm the operation. Retry the same capture if available, or check the source again.",
      );
    }
  }
  async function inspect() {
    const inputs =
      sourceFields.current?.querySelectorAll<HTMLInputElement>("input");
    if (
      !form.current ||
      !inputs ||
      !Array.from(inputs).every((input) => input.reportValidity())
    )
      return;
    const data = new FormData(form.current);
    const source: S["PreservationSource"] = {
      source_kind: String(
        data.get("source_kind"),
      ) as S["PreservationSource"]["source_kind"],
      source_link_id: String(data.get("source_link_id")).trim(),
      link_revision: Number(data.get("link_revision")),
    };
    setBusy(true);
    clearSelection();
    setStatus("Checking the exact current source…");
    try {
      const version = check(
        await api().POST(
          "/api/v1/admin/data-requests/{target}/channel-preservations/inspect",
          { params: { path: { target } }, body: source },
        ),
      );
      setSelected({ ...source, ...version });
      setStatus(
        "Current source version checked. Confirm the authorized finite decision before capturing.",
      );
    } catch (error) {
      failure(error);
    } finally {
      setBusy(false);
    }
  }
  async function send(operation: Pending) {
    onAttempt();
    setPending(operation);
    setBusy(true);
    setStatus("Saving the exact minimized snapshot and decision…");
    try {
      check(
        await api().POST(
          "/api/v1/admin/data-requests/{target}/channel-preservations",
          {
            params: {
              path: { target },
              header: { "Idempotency-Key": operation.key },
            },
            body: operation.body,
          },
        ),
      );
      setPending(null);
      clearSelection();
      form.current?.reset();
      setStatus(
        "Snapshot and finite decision saved. STOP and unlink remain available.",
      );
      try {
        await onCaptured();
      } catch {
        setStatus("Snapshot saved. Reload holds to refresh the list.");
      }
    } catch (error) {
      failure(error);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      aria-labelledby={id}
      className="channel-preservation space-y-3 border-t pt-4"
    >
      <h3 id={id} className="font-semibold">
        Preserve an exact channel version
      </h3>
      <p>
        Capture an encrypted, minimized copy for an already authorized decision.
        Contacts, message bodies, codes and tokens are excluded. STOP, unlink
        and expiry continue. Account deletion remains disabled.
      </p>
      <form
        ref={form}
        className="space-y-4"
        onSubmit={(event) => {
          event.preventDefault();
          if (!selected) {
            setStatus("Check the exact source version first.");
            return;
          }
          const data = new FormData(event.currentTarget);
          void send({
            key: crypto.randomUUID(),
            body: {
              ...selected,
              decision_reference: String(data.get("decision_reference")).trim(),
              reason: String(
                data.get("reason"),
              ) as S["PreservationCapture"]["reason"],
              expires_at: new Date(
                String(data.get("expires_at")),
              ).toISOString(),
              affirmative: true,
            },
          });
        }}
      >
        <fieldset
          ref={sourceFields}
          disabled={busy || !!pending}
          className="min-w-0 space-y-3"
        >
          <legend>Exact source version</legend>
          <p>
            Use the existing link ID and revision from the authorized
            preservation decision.
          </p>
          <div>
            <label className="block" htmlFor={`${id}-source-kind`}>
              Capture source
            </label>
            <select
              id={`${id}-source-kind`}
              name="source_kind"
              className="ui-select"
              onChange={clearSelection}
            >
              <option value="CHANNEL_LINK_SNAPSHOT">Link revision</option>
              <option value="CHANNEL_CONVERSATION_SNAPSHOT">
                Conversation version
              </option>
            </select>
          </div>
          <label className="block">
            Source link UUID
            <input
              name="source_link_id"
              required
              pattern={uuid}
              className="ui-input"
              autoComplete="off"
              onChange={clearSelection}
            />
          </label>
          <label className="block">
            Source link revision
            <input
              name="link_revision"
              type="number"
              min={1}
              max={2147483647}
              step={1}
              required
              className="ui-input"
              onChange={clearSelection}
            />
          </label>
          <button
            type="button"
            className="ui-button ui-button-secondary"
            onClick={() => void inspect()}
          >
            Check source version
          </button>
        </fieldset>
        <fieldset disabled={busy || !!pending} className="min-w-0 space-y-3">
          <legend>Authorized capture decision</legend>
          <label className="block">
            Capture decision reference
            <input
              name="decision_reference"
              required
              pattern={uuid}
              className="ui-input"
              autoComplete="off"
            />
          </label>
          <div>
            <label className="block" htmlFor={`${id}-reason`}>
              Capture reason
            </label>
            <select id={`${id}-reason`} name="reason" className="ui-select">
              <option value="LEGAL_OBLIGATION">Legal obligation</option>
              <option value="SECURITY_INVESTIGATION">
                Security investigation
              </option>
            </select>
          </div>
          <label className="block">
            Capture end date and time (device local time)
            <input
              name="expires_at"
              type="datetime-local"
              required
              className="ui-input"
            />
          </label>
          <label className="flex min-h-11 items-center gap-3">
            <input name="affirmative" type="checkbox" required />I confirm an
            authorized finite decision for this exact checked version.
          </label>
          <button className="ui-button ui-button-primary" disabled={!selected}>
            Capture selected version
          </button>
        </fieldset>
      </form>
      {pending && (
        <button
          className="ui-button ui-button-secondary"
          disabled={busy}
          onClick={() => void send(pending)}
        >
          Retry same capture
        </button>
      )}
      {status && <p role="status">{status}</p>}
    </section>
  );
}
