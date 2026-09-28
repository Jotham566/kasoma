# ADR-025: Learner flags and independent staff triage

Date: 28 September 2026
Status: Accepted within delegated implementation discretion
Requirements: FR-GRD-009, FR-CNT-006; supporting FR-CNT-003/004, FR-ID-003,
FR-OPS-001/003, NFR-SEC-002, NFR-ACC-001, NFR-MNT-001

## Decision

Implement the specified POST /attempts/{id}/flag, GET /admin/content-flags and
PATCH /admin/content-flags/{id}. Add GET /attempts/{id}/flag for owned recovery,
and GET /admin/content-flags/{id} for audited detail/history. This first complete
path flags an already submitted attempt, including diagnostic acknowledgements;
it never discloses a sealed diagnostic grade. Diagnostic views add only saved
attempt IDs and question positions as `answered_attempts` for reload-safe reporting. Reporting before an attempt is outside
this attempt-bound API. Learner responses contain only receipt/category/time, not
staff notes, owner or resolution. Current consent and subject access apply every time.

A strict category is QUESTION_ERROR, GRADE_DISPUTE, UNCLEAR, ACCESSIBILITY,
UNSAFE_CONTENT or OTHER. Optional trimmed comment is at most 1000 characters. Text
is confidential, encrypted using the existing server cipher, rendered as plain text,
and excluded from logs, audit payloads and analytics. No uploads or rich text.
Warn against adding personal/contact details. UNSAFE_CONTENT starts HIGH priority;
this local queue does not promise live monitoring, contact minors or improvise a
safeguarding response. Approved procedures remain a production gate.

Keep one immutable report per learner attempt/category; exact retries return it,
different text conflicts. An actor-bound idempotency receipt also detects key reuse
across attempts/payloads. The UI freezes the payload during retry after a lost response;
GET recovery shows already recorded categories after reload. No browser persistence
of comment text. All item/version/reporter/attempt bindings derive from the database.

Reviewer/admin roles may list and inspect flags; author-only and support-readonly roles
cannot. Staff DTOs omit learner identity, contact, raw answers and grades; item-version
links supply content context through the existing independent review interface.
Every staff read and mutation is audited. No general learner-record access is granted.
Mutations require recent authentication. Owners are assigned by claiming a flag for
oneself; another eligible reviewer may take over with an audited revision. Authors
cannot triage their own content even with a reviewer/admin role.

States are OPEN, IN_REVIEW, RESOLVED, DISMISSED. Claiming/reopening uses IN_REVIEW;
terminal states require current actor ownership and a nonempty encrypted resolution
(1–1000 characters). Priority is NORMAL or HIGH. Every successful mutation increments
a checked revision and appends immutable metadata history with actor/status/owner/
priority and keyed resolution digest. Idempotent retry returns current state without
reapplying a stale operation. Free text is held once on the flag, not copied into
long-lived audits. No flag action automatically retires content, changes grades,
replays mastery or messages learners; explicit existing content retirement remains
available to authorized reviewers.

Non-dismissed QUESTION_ERROR, GRADE_DISPUTE and UNSAFE_CONTENT reports mark the stable
item disputed for successor creation and approval. Such versions require two independent
reviewers, using existing publication controls. Resolved defects remain disputed history;
dismissing a flag does not lower an already required second review. Published content
and learning evidence remain immutable. Serialize dispute publication checks on the item.

## Data, retention and failure handling

Add migration 0011 for flags, mutation receipts and metadata history, with foreign keys,
unique report scope, immutable source binding and append-only history guards. Audit and
safe content outbox events commit atomically with the flag. List uses UUID cursor and
limit 1–50; optional status filter. Read/mutation limits are 60/minute; new reports 10/hour.
No comment, answer or reporter ID is sent through the outbox.

Resolved/dismissed flags set a retention-due timestamp exactly 24 calendar months after
resolution, following specification 09; reopening clears it until re-resolution. There
is no deletion endpoint or destructive migration. The repository's pending production
retention/anonymization jobs must consume this timestamp before real learner use.
Do not introduce an indefinite retention policy or claim those jobs are implemented.

Tests cover schema bounds, owned/version binding, consent/roles, replay/conflict,
concurrency/rollback, terminal-state and revision guards, encrypted text, audited reads,
second review, diagnostic sealing, and browser recovery/triage/keyboard/accessibility.
No external provider, model call, production data or new academic rule is introduced.

Migration 0012 adds an explicit non-null terminal retention constraint: SQL CHECK
accepts UNKNOWN, so equality with a nullable deadline alone is insufficient. This
forward fix preserves the already locally applied 0011 migration and existing records.
