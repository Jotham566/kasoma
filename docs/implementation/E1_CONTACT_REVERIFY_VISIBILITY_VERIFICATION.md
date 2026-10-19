# E1 profile contact reverification visibility

Requirements: FR-ID-001/005, NFR-ACC-001, NFR-MNT-001.
Status: corrected three-engine journeys and running Docker preview verified locally;
hosted acceptance pending.

## Finding and bounded correction

A read-only inspection of the local preview finds “Verify contact again” above the
ordinary sign-in form while no profile is loaded. The component renders that action
unconditionally, including initial sign-in and logout. It duplicates the visible
contact form and obscures the next useful action required by the UX specification.

Render this action only when a profile is loaded. Its existing handler still opens
contact verification for authenticated users. This changes presentation only: no
server authorization, OTP, recent-auth requirement, consent rule, session lifetime,
API contract or sensitive-action capability is altered. No new ADR is necessary.

Extend the existing real-API adult identity journey to require the control absent
when signed out, present after verification and absent after logout. Existing profile,
consent/withdrawal, cookie confidentiality, keyboard/axe and sign-out assertions remain.
Capture a public signed-out screenshot before any fictional contact is entered.
Add `make test-web-identity` for the existing three identity journeys in each engine.

## Verification record

- Before the correction, `make test-web-identity` stops in Chromium: the new adult
  assertion expects zero reverification buttons and finds one. The other two identity
  cases pass (16.9 seconds total). No timeout or assertion is weakened.
- `make format lint build` passes after the conditional correction.
- Corrected `make test-web-identity` passes nine real-API executions: Chromium three
  in 12.3 seconds, Firefox three in 12.9 seconds and WebKit three in 13.1 seconds.
  Signed-out, authenticated and logout assertions pass alongside the retained
  adult/minor, consent/assent, cookie/axe, cross-origin and offline cases.
- `make test-unit openapi-check security` passes: 1,092 unit/contract, 35 tooling,
  unchanged generated contracts, secret-boundary checks and dependency audits.
- The [public WebKit screenshot](evidence/E1_SIGNED_OUT_PROFILE_2026_10_19.png) is
  captured before any fictional contact is entered. It is an automated test output,
  not branded-browser evidence.
- `make containers` succeeds. Recreate only the web service with the built image;
  all eight services remain healthy and database volumes are preserved. A fresh
  in-app preview at `localhost:3000/onboarding` confirms the signed-out control is
  absent and the contact form visible. No contact or consent form is submitted.
- Full hosted [39222489376](https://github.com/Jotham566/kasoma/actions/runs/39222489376)
  at source `44ae9ad` is pending. Local preview success is not hosted acceptance.
- Native Edge Beta selection through the UI tool times out; the subsequent review
  uses the existing in-app preview. No native Edge, stable/current-previous browser,
  physical-device or manual screen-reader acceptance is claimed.

Normal learner short-text delivery and capture creation remain disabled. No model,
external messaging, email or cloud application call is needed. Use fictional fixture
identities only. Parent load and provider-isolation increments retain their own source
verification; this frontend change needs its own build/browser acceptance.
