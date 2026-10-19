"use client";

import Link from "next/link";
import { useRef, useState, type FormEvent } from "react";
import { apiClient, type components } from "@kasoma/api-client";
import { settings, type Key } from "./settings";

type View = components["schemas"]["ConfigurationView"];
type Patch = components["schemas"]["ConfigurationPatch"];
type Pending = { key: Key; body: Patch; command: string };

export default function Configuration() {
  const [view, setView] = useState<View | null>(null);
  const [busy, setBusy] = useState(false);
  const [key, setKey] = useState<Key>("failed_imports");
  const [value, setValue] = useState("");
  const [reason, setReason] = useState<Patch["reason"] | "">("");
  const [pending, setPending] = useState<Pending | null>(null);
  const [status, setStatus] = useState(
    "Load warning settings. ADMIN access required.",
  );
  const inFlight = useRef(false);

  async function load() {
    if (inFlight.current || pending) return;
    inFlight.current = true;
    setBusy(true);
    setView(null);
    setStatus("Loading current warning settings…");
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/admin/configuration",
      );
      if (!result.data) {
        setStatus(
          "Settings unavailable. Check ADMIN access, sign-in or rate limit, then reload.",
        );
        return;
      }
      setView(result.data);
      setValue(String(result.data.values[key]));
      setReason("");
      setStatus(
        "Current settings loaded. Review one warning threshold before saving.",
      );
    } catch {
      setStatus(
        "Connection interrupted. Current settings unavailable; reload when connected.",
      );
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    if (inFlight.current || (!view && !pending)) return;
    if (!pending && (!reason || !/^\d+$/.test(value))) {
      setStatus("Choose an audit reason and enter a whole-number threshold.");
      return;
    }
    const command: Pending = pending ?? {
      key,
      body: {
        version: view!.version,
        value: Number(value),
        reason: reason as Patch["reason"],
      },
      command: crypto.randomUUID(),
    };
    // Keep the exact intent and key through lost acknowledgements. Never auto-resubmit
    // edited values against a newly fetched version.
    setPending(command);
    inFlight.current = true;
    setBusy(true);
    setStatus("Saving reviewed warning threshold…");
    try {
      const result = await apiClient("", crypto.randomUUID()).PATCH(
        "/api/v1/admin/configuration/{key}",
        {
          params: {
            path: { key: command.key },
            header: { "Idempotency-Key": command.command },
          },
          body: command.body,
        },
      );
      if (!result.data) {
        if ([400, 401, 403, 409, 422].includes(result.response.status)) {
          setPending(null);
          setView(null);
          setStatus(
            result.response.status === 409
              ? "Configuration conflict. Reload current settings and review your change again."
              : "Change refused. Check ADMIN access, sign in again for recent verification, and reload settings.",
          );
        } else {
          setStatus(
            "Save outcome unconfirmed. Retry the same change when connected; its original command is preserved in this tab.",
          );
        }
        return;
      }
      setPending(null);
      setView(null);
      setReason("");
      setStatus(
        `Change recorded as revision ${result.data.recorded.revision}${result.data.replayed ? " (confirmed retry)" : ""}. Reload to see the current settings; later changes may exist.`,
      );
    } catch {
      setStatus(
        "Connection interrupted; save outcome unconfirmed. Retry the same change without editing it. Keep this tab open to preserve its command.",
      );
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  const selected = settings[key];
  return (
    <main className="staff-page operations-page configuration-page">
      <section className="surface-card operations-section">
        <p className="eyebrow">Staff operations</p>
        <h1 className="text-3xl font-semibold">Warning settings</h1>
        <p>
          Tune the existing operational warnings. Saving requires ADMIN access
          and sign-in verification within the last 10 minutes.
        </p>
        <p>
          These thresholds affect warning sensitivity. They do not change
          processing limits, privacy controls or feature activation.
        </p>
        <Link
          href="/admin/operations"
          className="ui-button ui-button-secondary"
        >
          Back to operational health
        </Link>
        <div>
          <button
            type="button"
            className="ui-button ui-button-secondary"
            disabled={busy || !!pending}
            onClick={load}
          >
            Load current settings
          </button>
        </div>
        <p role="status">{status}</p>
      </section>
      {view && (
        <section
          className="surface-card operations-section"
          aria-label="Current warning settings"
        >
          <h2 className="text-xl font-semibold">
            Current snapshot · revision {view.revision}
          </h2>
          <p>
            {view.source === "ENVIRONMENT_DEFAULTS"
              ? "Using startup defaults. The first saved change records all current warning values."
              : `Saved ${new Date(view.updated_at!).toLocaleString("en-UG", { timeZone: "Africa/Kampala" })} (Africa/Kampala).`}
          </p>
          <dl className="operations-grid">
            {(Object.keys(settings) as Key[]).map((name) => (
              <div className="operations-counter" key={name}>
                <dt>{settings[name].label}</dt>
                <dd>
                  {view.values[name].toLocaleString("en-UG")}{" "}
                  {settings[name].unit}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      )}
      {(view || pending) && (
        <section
          className="surface-card operations-section"
          aria-label="Edit one warning threshold"
        >
          <h2 className="text-xl font-semibold">Review a change</h2>
          <form onSubmit={save} className="operations-section">
            <fieldset
              disabled={busy || !!pending}
              className="operations-section"
            >
              <legend>Warning threshold</legend>
              <label htmlFor="warning-key">Setting</label>
              <select
                className="ui-select"
                id="warning-key"
                value={key}
                onChange={(event) => {
                  const name = event.target.value as Key;
                  setKey(name);
                  setValue(String(view!.values[name]));
                  setReason("");
                }}
              >
                {(Object.keys(settings) as Key[]).map((name) => (
                  <option key={name} value={name}>
                    {settings[name].label}
                  </option>
                ))}
              </select>
              <label htmlFor="warning-value">
                New threshold ({selected.unit})
              </label>
              <input
                className="ui-input"
                id="warning-value"
                type="number"
                inputMode="numeric"
                min={selected.min}
                max={selected.max}
                step="1"
                required
                value={value}
                onChange={(event) => setValue(event.target.value)}
                aria-describedby="warning-range"
              />
              <p id="warning-range">
                Whole numbers from {selected.min.toLocaleString("en-UG")} to{" "}
                {selected.max.toLocaleString("en-UG")} {selected.unit}. Current
                value: {view?.values[key] ?? pending?.body.value}.
              </p>
              <label htmlFor="warning-reason">Audit reason</label>
              <select
                className="ui-select"
                id="warning-reason"
                required
                value={reason}
                onChange={(event) =>
                  setReason(event.target.value as Patch["reason"])
                }
              >
                <option value="">Choose a reason</option>
                <option value="INCREASE_SENSITIVITY">
                  Increase warning sensitivity
                </option>
                <option value="REDUCE_NOISE">Reduce warning noise</option>
                <option value="REVIEWED_BASELINE">
                  Apply a reviewed baseline
                </option>
              </select>
            </fieldset>
            <button
              type="submit"
              className="ui-button ui-button-primary"
              disabled={busy}
            >
              {busy
                ? "Saving…"
                : pending
                  ? "Retry same change"
                  : "Save reviewed threshold"}
            </button>
          </form>
        </section>
      )}
    </main>
  );
}
