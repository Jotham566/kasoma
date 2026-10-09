"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiClient, type components } from "@kasoma/api-client";

type View = components["schemas"]["ChannelLinkView"];
type Code = components["schemas"]["LinkCodeView"];
type Unlink = components["schemas"]["UnlinkInput"];

export default function WhatsApp() {
  const [view, setView] = useState<View | null>(null);
  const [code, setCode] = useState<Code | null>(null);
  const [issueKey, setIssueKey] = useState<string | null>(null);
  const [unlink, setUnlink] = useState<{ key: string; body: Unlink } | null>(
    null,
  );
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Load your channel status to begin.");
  useEffect(() => {
    if (!code) return;
    const timer = setTimeout(
      () => {
        setCode(null);
        setStatus("Link code expired. Request a new code if needed.");
      },
      Math.max(0, Date.parse(code.expires_at) - Date.now()),
    );
    return () => clearTimeout(timer);
  }, [code]);

  async function refresh() {
    setBusy(true);
    try {
      const result = await apiClient("", crypto.randomUUID()).GET(
        "/api/v1/channels/whatsapp/link",
      );
      setView(result.data ?? null);
      if (result.data?.status === "ACTIVE" || result.data?.status === "STOPPED")
        setCode(null);
      setStatus(
        result.data
          ? "Channel status refreshed."
          : "Sign in again to view your channel.",
      );
    } catch {
      setView(null);
      setStatus("Could not load channel status. Retry when connected.");
    } finally {
      setBusy(false);
    }
  }
  async function issue() {
    setBusy(true);
    setCode(null);
    const key = issueKey ?? crypto.randomUUID();
    setIssueKey(key);
    try {
      const result = await apiClient("", crypto.randomUUID()).POST(
        "/api/v1/channels/whatsapp/link-code",
        {
          params: { header: { "Idempotency-Key": key } },
        },
      );
      if (result.data) {
        setCode(result.data);
        setIssueKey(null);
        setStatus(
          "Code ready. It expires in five minutes and can be used once.",
        );
      } else {
        setIssueKey(null);
        setStatus(
          "Code unavailable. Check current consent, recent sign-in and the request limit.",
        );
      }
    } catch {
      setStatus(
        "Could not confirm the code request. Retry to recover the same code.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function disconnect() {
    if (!view) return;
    setBusy(true);
    const pending = unlink ?? {
      key: crypto.randomUUID(),
      body: {
        expected_link_id: view.link_id,
        expected_revision: view.revision,
      },
    };
    setUnlink(pending);
    try {
      const result = await apiClient("", crypto.randomUUID()).DELETE(
        "/api/v1/channels/whatsapp/link",
        {
          params: { header: { "Idempotency-Key": pending.key } },
          body: pending.body,
        },
      );
      if (result.data) {
        setView(result.data);
        setCode(null);
        setUnlink(null);
        setIssueKey(null);
        setStatus(
          result.data.status === "UNLINKED" ||
            result.data.status === "NOT_LINKED"
            ? "Channel unlinked. Outstanding link codes have been cancelled."
            : "Request already handled. A newer channel link remains; review its status.",
        );
      } else {
        setUnlink(null);
        setView(null);
        setStatus(
          "Could not unlink. Refresh the status and check recent sign-in.",
        );
      }
    } catch {
      setStatus("Could not confirm unlinking. Retry the same request.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="account-tools-page">
      <p className="eyebrow">Connected channels</p>
      <h1 className="text-3xl font-semibold">WhatsApp channel</h1>
      <p>
        Synthetic local testing only. No real WhatsApp number or message
        delivery is connected.
      </p>
      <p>
        Linking requires current consent and a recent sign-in. Linking does not
        create a new account.
      </p>
      <Link className="ui-text-link" href="/onboarding">
        Sign in and review consent
      </Link>
      <section
        className="surface-card channel-controls"
        aria-label="Channel controls"
      >
        <button
          className="ui-button ui-button-secondary"
          disabled={busy}
          onClick={() => void refresh()}
        >
          Refresh channel status
        </button>
        <p role="status">{status}</p>
        {view && (
          <>
            <p>
              Channel state: <strong>{view.status}</strong>
            </p>
            <p>
              {view.outbound_enabled
                ? "Local fake replies enabled."
                : "Local fake replies disabled."}
            </p>
            <button
              className="ui-button ui-button-primary"
              disabled={busy || !!unlink}
              onClick={() => void issue()}
            >
              {issueKey ? "Retry code request" : "Get a link code"}
            </button>
            <button
              className="ui-button ui-button-secondary"
              disabled={busy}
              onClick={() => void disconnect()}
            >
              {unlink ? "Retry unlink" : "Unlink and cancel codes"}
            </button>
          </>
        )}
      </section>
      {code && (
        <section
          aria-label="One-time link code"
          className="surface-card channel-code"
        >
          <p>
            For the local simulator, use <code>LINK {code.code}</code>.
          </p>
          <p>
            Expires at{" "}
            <time dateTime={code.expires_at}>
              {new Date(code.expires_at).toLocaleTimeString("en-UG", {
                timeZone: "Africa/Kampala",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
            </time>{" "}
            (Kampala). Keep this code private.
          </p>
        </section>
      )}
      <p>
        STOP blocks replies and keeps channel ownership. Unlink releases it and
        cancels unused codes. Request a fresh code after STOP to link again.
        Local synthetic practice supports START and CONTINUE with five
        questions. Reply directly to the latest menu or question. Real WhatsApp
        delivery is not enabled.
      </p>
    </main>
  );
}
