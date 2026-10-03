"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiClient } from "@kasoma/api-client";
import type { components } from "@kasoma/api-client";

type Profile = components["schemas"]["ProfileView"];
type Subject = components["schemas"]["SubjectView"];
type Consent = components["schemas"]["ConsentInput"];
const client = () => apiClient("", crypto.randomUUID());
const inputClass = "block w-full rounded border border-slate-500 p-3 mt-1 mb-4";
const buttonClass =
  "rounded bg-slate-900 text-white px-5 py-3 my-2 disabled:opacity-50";

export default function Onboarding() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [challenge, setChallenge] = useState<string | null>(null);
  const [guardianChallenge, setGuardianChallenge] = useState<string | null>(
    null,
  );
  const [linkChallenge, setLinkChallenge] = useState<string | null>(null);
  const [status, setStatus] = useState("Checking your session…");
  const consentRetry = useRef<{ payload: string; key: string } | null>(null);
  const [busy, setBusy] = useState(true);

  async function load() {
    const api = client();
    const [me, catalog] = await Promise.all([
      api.GET("/api/v1/me"),
      api.GET("/api/v1/curriculum/subjects"),
    ]);
    if (catalog.data) setSubjects(catalog.data);
    setProfile(me.data ?? null);
    setStatus(
      me.data ? "Your profile is ready to review." : "Sign in to continue.",
    );
  }
  useEffect(() => {
    let active = true;
    const api = client();
    void Promise.all([
      api.GET("/api/v1/me"),
      api.GET("/api/v1/curriculum/subjects"),
    ])
      .then(([me, catalog]) => {
        if (!active) return;
        if (catalog.data) setSubjects(catalog.data);
        setProfile(me.data ?? null);
        setStatus(
          me.data ? "Your profile is ready to review." : "Sign in to continue.",
        );
      })
      .catch(() => {
        if (active) setStatus("Connection interrupted. Please try again.");
      })
      .finally(() => {
        if (active) setBusy(false);
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
        "This action could not be completed. Check your connection or sign in again. Your saved profile is preserved.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function requestCode(
    form: FormData,
    purpose: "LOGIN" | "GUARDIAN" | "LINK",
  ) {
    let device = sessionStorage.getItem("kasoma_device");
    if (!device) {
      device = crypto.randomUUID();
      sessionStorage.setItem("kasoma_device", device);
    }
    const result = await client().POST("/api/v1/auth/otp/request", {
      body: {
        identifier: String(form.get("identifier")),
        purpose,
        device_id: device,
      },
    });
    if (!result.data) throw new Error("Request unavailable");
    const id = result.data.challenge_id;
    if (purpose === "LOGIN") setChallenge(id);
    else if (purpose === "GUARDIAN") setGuardianChallenge(id);
    else setLinkChallenge(id);
    setStatus(
      "If eligible, a code was sent. It expires in 10 minutes. Wait at least 60 seconds before requesting another.",
    );
  }
  async function verify(form: FormData, id: string, purpose: "LOGIN" | "LINK") {
    const result = await client().POST("/api/v1/auth/otp/verify", {
      body: { challenge_id: id, code: String(form.get("code")), purpose },
    });
    if (!result.response.ok) throw new Error("Verification unavailable");
    setChallenge(null);
    setLinkChallenge(null);
    await load();
  }
  async function record(body: Consent) {
    const payload = JSON.stringify(body);
    if (consentRetry.current?.payload !== payload)
      consentRetry.current = { payload, key: crypto.randomUUID() };
    const result = await client().POST("/api/v1/me/consents", {
      body,
      params: { header: { "idempotency-key": consentRetry.current.key } },
    });
    if (!result.data) throw new Error("Consent unavailable");
    consentRetry.current = null;
    setProfile(result.data);
    setStatus(
      body.consent_type === "WITHDRAW"
        ? "Consent withdrawn. Learning access is paused."
        : "Your declaration was saved.",
    );
  }
  function contactForm(purpose: "LOGIN" | "GUARDIAN" | "LINK", label: string) {
    return (
      <form
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          void run(() => requestCode(form, purpose));
        }}
      >
        <label>
          {label}
          <input
            className={inputClass}
            name="identifier"
            required
            maxLength={254}
            autoComplete="off"
            placeholder="name@example.invalid or +256…"
          />
        </label>
        <button className={buttonClass} disabled={busy}>
          Send{" "}
          {purpose === "GUARDIAN"
            ? "guardian "
            : purpose === "LINK"
              ? "linking "
              : ""}
          code
        </button>
      </form>
    );
  }
  function verifyForm(id: string, purpose: "LOGIN" | "LINK") {
    return (
      <form
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          void run(() => verify(form, id, purpose));
        }}
      >
        <label>
          Verification code
          <input
            className={inputClass}
            name="code"
            inputMode="numeric"
            autoComplete="one-time-code"
            pattern="[0-9]{6}"
            required
            maxLength={6}
          />
        </label>
        <button className={buttonClass} disabled={busy}>
          Verify {purpose === "LINK" ? "new contact" : "and continue"}
        </button>
      </form>
    );
  }
  return (
    <main className="mx-auto max-w-2xl p-6">
      <Link className="underline" href="/">
        Kasoma home
      </Link>
      <h1 className="text-3xl font-semibold my-6">Your Kasoma profile</h1>
      <p className="mb-4">
        Synthetic development only. Use fictional details and local email
        capture. No learning sessions are available yet.
      </p>
      <p role="status" aria-live="polite" className="rounded border p-4 my-4">
        {status}
      </p>
      <button
        className={buttonClass}
        disabled={busy}
        onClick={() => {
          setProfile(null);
          setChallenge(null);
          setStatus(
            "Verify your existing contact again to continue sensitive actions.",
          );
        }}
      >
        Verify contact again
      </button>
      {!profile ? (
        <section aria-label="Sign in">
          <p>
            Verify your contact to keep your profile connected across devices.
          </p>
          {contactForm("LOGIN", "Email or mobile number")}
          {challenge && verifyForm(challenge, "LOGIN")}
          <button
            className={buttonClass}
            disabled={busy}
            onClick={() =>
              void run(async () => {
                const response = await fetch("/api/v1/auth/refresh", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: "{}",
                });
                if (!response.ok) throw new Error("Session expired");
                await load();
              })
            }
          >
            Resume saved session
          </button>
        </section>
      ) : (
        <>
          <section aria-labelledby="profile-heading">
            <h2 id="profile-heading" className="text-xl font-semibold my-4">
              Senior 4 profile
            </h2>
            <form
              key={profile.id}
              onSubmit={(event) => {
                event.preventDefault();
                const form = new FormData(event.currentTarget);
                void run(async () => {
                  const result = await client().PATCH("/api/v1/me", {
                    body: {
                      display_name: String(form.get("display_name")),
                      birth_date: String(form.get("birth_date")),
                      subject_ids: form.getAll("subject_ids").map(String),
                    },
                  });
                  if (!result.data) throw new Error("Profile unavailable");
                  setProfile(result.data);
                  setStatus("Profile saved.");
                });
              }}
            >
              <label>
                Display name
                <input
                  className={inputClass}
                  name="display_name"
                  required
                  maxLength={80}
                  defaultValue={profile.display_name ?? ""}
                />
              </label>
              <label>
                Date of birth
                <input
                  className={inputClass}
                  name="birth_date"
                  type="date"
                  required
                  readOnly={!!profile.birth_date}
                  defaultValue={profile.birth_date ?? ""}
                />
              </label>
              <p className="mb-4">
                Date of birth determines the consent pathway and cannot be
                changed here after saving.
              </p>
              <fieldset>
                <legend>Choose one or both subjects</legend>
                {subjects.map((subject) => (
                  <label
                    key={subject.id}
                    className="flex min-h-11 items-center gap-3"
                  >
                    <input
                      type="checkbox"
                      name="subject_ids"
                      value={subject.id}
                      defaultChecked={profile.subject_ids.includes(subject.id)}
                    />
                    {subject.name}
                  </label>
                ))}
              </fieldset>
              <button className={buttonClass} disabled={busy}>
                Save profile
              </button>
            </form>
          </section>
          {profile.birth_date && (
            <section aria-labelledby="consent-heading">
              <h2 id="consent-heading" className="text-xl font-semibold my-4">
                Consent and assent
              </h2>
              <p>
                <Link className="underline" href="/development-notice">
                  Read the synthetic development notice
                </Link>{" "}
                — version {profile.policy_version}.
              </p>
              <p className="my-4">
                {profile.learning_allowed
                  ? "Required declarations are recorded. Diagnostics are not implemented yet."
                  : "Learning access is paused until all required declarations are recorded."}
              </p>
              {(["SELF", "ASSENT"] as const)
                .filter((kind) => profile.consent_required.includes(kind))
                .map((kind) => (
                  <form
                    key={kind}
                    onSubmit={(event) => {
                      event.preventDefault();
                      void run(() =>
                        record({
                          consent_type: kind,
                          policy_version: profile.policy_version,
                          affirmative: true,
                        }),
                      );
                    }}
                  >
                    <label className="flex min-h-11 items-center gap-3">
                      <input type="checkbox" required />
                      {kind === "SELF"
                        ? "I give my own consent for this synthetic test."
                        : "I separately assent to this synthetic test."}
                    </label>
                    <button className={buttonClass} disabled={busy}>
                      Record {kind === "SELF" ? "my consent" : "learner assent"}
                    </button>
                  </form>
                ))}
              {profile.consent_required.includes("GUARDIAN") && (
                <section
                  aria-label="Guardian declaration"
                  className="border rounded p-4 my-4"
                >
                  <h3 className="font-semibold">
                    Parent or guardian declaration
                  </h3>
                  <p>
                    The guardian must use their own contact, review the notice
                    and make this declaration separately.
                  </p>
                  {contactForm("GUARDIAN", "Guardian email or mobile number")}
                  {guardianChallenge && (
                    <form
                      onSubmit={(event) => {
                        event.preventDefault();
                        const form = new FormData(event.currentTarget);
                        void run(() =>
                          record({
                            consent_type: "GUARDIAN",
                            policy_version: profile.policy_version,
                            affirmative: true,
                            guardian_name: String(form.get("guardian_name")),
                            guardian_relationship: String(
                              form.get("relationship"),
                            ),
                            challenge_id: guardianChallenge,
                            code: String(form.get("guardian_code")),
                          }),
                        );
                      }}
                    >
                      <label>
                        Guardian name
                        <input
                          className={inputClass}
                          name="guardian_name"
                          maxLength={80}
                          required
                        />
                      </label>
                      <label>
                        Relationship to learner
                        <input
                          className={inputClass}
                          name="relationship"
                          maxLength={80}
                          required
                        />
                      </label>
                      <label>
                        Guardian code
                        <input
                          className={inputClass}
                          name="guardian_code"
                          inputMode="numeric"
                          autoComplete="one-time-code"
                          pattern="[0-9]{6}"
                          maxLength={6}
                          required
                        />
                      </label>
                      <label className="flex min-h-11 items-center gap-3">
                        <input type="checkbox" required />I am the parent or
                        guardian and affirm this separate synthetic declaration.
                      </label>
                      <button className={buttonClass} disabled={busy}>
                        Record guardian consent
                      </button>
                    </form>
                  )}
                </section>
              )}
              <button
                className={buttonClass}
                disabled={busy}
                onClick={() =>
                  void run(() =>
                    record({
                      consent_type: "WITHDRAW",
                      policy_version: profile.policy_version,
                      affirmative: true,
                    }),
                  )
                }
              >
                Withdraw consent and assent
              </button>
            </section>
          )}
          <Link
            className="inline-flex min-h-11 items-center underline"
            href="/privacy"
          >
            Request export or deletion of your data
          </Link>
          <section aria-label="Additional contact">
            <h2 className="text-xl font-semibold my-4">Link another contact</h2>
            <p>
              {profile.identifier_count} verified contact(s). A recently
              verified session is required.
            </p>
            {contactForm("LINK", "New email or mobile number")}
            {linkChallenge && verifyForm(linkChallenge, "LINK")}
          </section>
          <div className="flex gap-4 flex-wrap">
            {(["/api/v1/auth/logout", "/api/v1/auth/logout-all"] as const).map(
              (path) => (
                <button
                  className={buttonClass}
                  disabled={busy}
                  key={path}
                  onClick={() =>
                    void run(async () => {
                      const response = await client().POST(path);
                      if (!response.response.ok)
                        throw new Error("Logout failed");
                      setProfile(null);
                      setGuardianChallenge(null);
                      setStatus("Signed out.");
                    })
                  }
                >
                  {path.endsWith("-all") ? "Sign out all devices" : "Sign out"}
                </button>
              ),
            )}
          </div>
        </>
      )}
    </main>
  );
}
