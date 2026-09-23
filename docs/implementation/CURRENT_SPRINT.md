# Current Sprint: E1 local identity and consent

The E0 foundation commit `4faf65a` passed hosted CI, was fast-forwarded to main,
and its implementation branch was deleted locally and remotely on 23 September 2026.
E1 work is on `codex/e1-identity-consent` and remains uncommitted for review.

## Current slice

FR-ID-001–005: email/phone verification, linking, expiring/rotating/revocable sessions,
S4 profile selection, adult consent and minor guardian-consent/assent gates.
Supporting NFR-SEC-001/002, NFR-MNT-001, NFR-ACC-001, NFR-OBS-001 and registration
subset of FR-OPS-001. See [E1 verification](E1_VERIFICATION.md) for evidence.

Next: content-author/reviewer RBAC, audited independent approval, rights/publication
validators and one approved synthetic item (FR-CNT-001–005), then the first objective
assessment using the shared consent guard. FR-ID-006 remains in E8.

## Remaining gates

- Synthetic development only: no approved legal/guardian/assent wording for enrollment.
- No real OTP provider, staff MFA, production key rotation or long-term retention jobs.
- Contact OTP proves possession; pilot guardian-verification procedures need sign-off.
- Future diagnostic/revision/WhatsApp routes must call the identity learning guard.
- Identity events are persisted atomically; analytics export/dispatch remains E8 work.
- Week 5/6 short-text benchmark sequencing question E0-01 still needs resolution
  before grading work; no academic or safety release gate has been weakened.

## Foundation evidence

The local foundation checks and original file inventory remain in
[E0 verification](E0_VERIFICATION.md). Hosted CI passed before merge. No calendar
kickoff date or named delivery owners have been supplied; the approved horizon
remains 12 weeks. See [Phase 0 assessment](PHASE_0_ASSESSMENT.md) for the full mapping.
