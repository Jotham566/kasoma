# Kasoma API and Integration Contract

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Style | REST/JSON over HTTPS |
| Prefix | `/api/v1` |
| Contract authority | Generated OpenAPI plus this document |

## 1. Conventions

- JSON fields use `snake_case` in API and Python; generated TypeScript types preserve contract names.
- IDs are opaque UUID strings.
- Timestamps are RFC 3339 UTC.
- All protected responses include `request_id` header.
- Mutation requests that may be retried accept `Idempotency-Key`.
- Pagination uses `cursor` and `limit`; no offset pagination for event-like lists.
- API never accepts learner-supplied score, mastery, role or approval state.
- Unknown fields are rejected on privileged mutation endpoints and ignored only where explicitly documented.

## 2. Standard envelopes

Success returns the resource directly or:

```json
{"data": [], "next_cursor": null}
```

Error:

```json
{
  "error": {
    "code": "CONTENT_NOT_APPROVED",
    "message": "This item is unavailable.",
    "request_id": "...",
    "field_errors": []
  }
}
```

Do not expose stack traces, provider errors, internal prompts or database identifiers.

## 3. Identity endpoints

| Method/path | Purpose |
|---|---|
| `POST /auth/otp/request` | Request email/phone verification code; always generic response |
| `POST /auth/otp/verify` | Verify code; create/link identity; return access/refresh credentials |
| `POST /auth/refresh` | Rotate refresh token |
| `POST /auth/logout` | Revoke current refresh session |
| `POST /auth/logout-all` | Revoke all user sessions |
| `GET /me` | Current profile, consent state and subjects |
| `PATCH /me` | Allowed learner preferences only |
| `POST /me/consents` | Record valid consent evidence |
| `POST /me/data-requests` | Create export/deletion request |

OTP request always returns `202` to prevent identity enumeration. Rate-limit by identifier hash, IP and device-risk signals.

## 4. Curriculum/content read endpoints

| Method/path | Purpose |
|---|---|
| `GET /curriculum/subjects` | Active MVP subjects |
| `GET /curriculum/subjects/{id}/topics` | Active topic clusters |
| `GET /curriculum/topics/{id}/map` | Learner-safe concepts/competencies |
| `GET /content/media/{signed_id}` | Time-limited authorized media access |

Never expose answer keys or rubrics through learner content endpoints before submission.

## 5. Diagnostic and session endpoints

| Method/path | Purpose |
|---|---|
| `POST /diagnostics` | Start/resume subject diagnostic |
| `GET /diagnostics/{id}` | Diagnostic state and next action |
| `POST /revision-sessions` | Create recommended or topic-selected session |
| `GET /sessions/{id}` | Session summary/current position |
| `GET /sessions/{id}/next-item` | Fetch next assigned item without answer data |
| `POST /sessions/{id}/attempts` | Submit answer and synchronously return grade or pending status |
| `GET /attempts/{id}/grade` | Poll/retrieve asynchronous grade |
| `POST /attempts/{id}/hint` | Request next approved hint |
| `GET /attempts/{id}/solution` | Retrieve worked solution after attempt |
| `POST /attempts/{id}/flag` | Report content/grade issue |

### Start revision session

```json
{
  "subject_id": "uuid",
  "mode": "RECOMMENDED",
  "topic_id": null,
  "desired_item_count": 5,
  "channel": "WEB"
}
```

Response includes `recommendation_reason`, `plan_version` and session ID, but not future answer keys.

### Item response

```json
{
  "session_item_id": "uuid",
  "item_version_id": "uuid",
  "position": 1,
  "prompt_blocks": [{"type":"markdown","content":"..."}],
  "response_spec": {"type":"NUMERIC","unit_options":["m/s"],"input_mode":"decimal"},
  "maximum_points": 2
}
```

### Attempt submission

```json
{
  "session_item_id": "uuid",
  "response": {"type":"NUMERIC","value":"12.5","unit":"m/s"},
  "client_started_at": "2026-09-22T12:00:00Z",
  "client_submitted_at": "2026-09-22T12:01:10Z"
}
```

Synchronous grade:

```json
{
  "attempt_id": "uuid",
  "status": "GRADED",
  "score": 0.5,
  "points_awarded": 1,
  "points_possible": 2,
  "confidence": 1.0,
  "feedback": {
    "correct_elements": ["Correct substitution"],
    "missing_elements": ["Unit conversion"],
    "next_action": "Convert centimetres to metres before substitution."
  },
  "mastery_update_status": "COMPLETED"
}
```

AI-assisted submission may return `202` with `status=PENDING` and a poll URL. The client must not display a predicted score while pending.

## 6. Progress endpoints

| Method/path | Purpose |
|---|---|
| `GET /me/progress?subject_id=` | Subject/topic/competency estimates and confidence |
| `GET /me/recommendations/next` | Current recommended target and explanation |
| `GET /me/session-history` | Cursor-paginated session summaries |

Progress object:

```json
{
  "skill_id": "uuid",
  "skill_type": "CONCEPT_COMPETENCY",
  "mastery": 0.61,
  "confidence": 0.43,
  "display_state": "DEVELOPING_ESTIMATE",
  "evidence_count": 4,
  "last_evidence_at": "..."
}
```

## 7. WhatsApp endpoints

| Method/path | Authentication | Purpose |
|---|---|---|
| `POST /channels/whatsapp/link-code` | Learner | Generate one-time code |
| `POST /webhooks/whatsapp` | Provider signature | Receive messages/status |
| `GET /webhooks/whatsapp` | Provider challenge | Verify webhook |
| `DELETE /channels/whatsapp/link` | Learner | Unlink/opt out |

Webhook processing:

1. verify provider signature before parsing;
2. persist provider message ID uniquely;
3. acknowledge quickly;
4. process asynchronously;
5. use the same session, grading and mastery application services as web;
6. store outbound delivery status;
7. redact message content from routine logs.

Supported learner commands include `START`, `CONTINUE`, `PROGRESS`, `HELP`, `STOP` plus structured answer replies. Free-form chat tutoring is not an MVP feature.

## 8. Content administration endpoints

| Method/path | Role | Purpose |
|---|---|---|
| `POST /admin/items` | Author | Create stable item/draft version |
| `POST /admin/items/import` | Author | Validate bulk import and return row errors |
| `GET /admin/item-versions/{id}` | Author/reviewer | Full content record |
| `PATCH /admin/item-versions/{id}` | Author | Edit draft with optimistic version |
| `POST /admin/item-versions/{id}/submit` | Author | Submit for review |
| `POST /admin/item-versions/{id}/review` | Reviewer | Approve or return |
| `POST /admin/item-versions/{id}/retire` | Reviewer/admin | Prevent future delivery |
| `GET /admin/content-flags` | Reviewer/admin | Triage queue |
| `PATCH /admin/content-flags/{id}` | Reviewer/admin | Assign/resolve |

Approval must return `409` when author and reviewer are the same or when required fields/rights are incomplete.

## 9. Admin/operations endpoints

- `GET /admin/audit`
- `GET /admin/operations/health-summary`
- `GET /admin/operations/grading-quality`
- `GET /admin/operations/usage-cost`
- `PATCH /admin/configuration/{key}` with version and audit reason

Operational endpoints expose aggregates; access to learner-level records requires explicit support permission and audit.

## 10. Error codes

Required stable codes include:

`AUTH_REQUIRED`, `FORBIDDEN`, `OTP_INVALID`, `OTP_RATE_LIMITED`, `CONSENT_REQUIRED`, `RESOURCE_NOT_FOUND`, `VALIDATION_FAILED`, `SESSION_NOT_ACTIVE`, `ITEM_ALREADY_ANSWERED`, `CONTENT_NOT_APPROVED`, `GRADE_PENDING`, `GRADE_LOW_CONFIDENCE`, `IDEMPOTENCY_CONFLICT`, `LINK_CODE_INVALID`, `PROVIDER_SIGNATURE_INVALID`, `USAGE_LIMIT_REACHED`, `VERSION_CONFLICT`.

## 11. Compatibility

- Breaking change: remove/rename field, narrow accepted value or change semantics. Requires `/v2` or approved migration window.
- Additive optional fields are non-breaking.
- OpenAPI diff runs in CI.
- Web uses generated client; handwritten duplicate DTOs are prohibited.

## Reviewed revision hints (ADR-022)

The submitted attempt remains immutable. `POST /sessions/{session_id}/items/{item_id}/hint`
reveals the next reviewed hint for the current served, unanswered revision assignment.
`POST /attempts/{attempt_id}/hint` provides post-answer remediation, and
`GET /attempts/{attempt_id}/hints` resumes previously revealed hints. All require
current consent, ownership, subject access and an approved pinned content version.
Diagnostics never expose hints, including after completion.

Both mutations require `Idempotency-Key` and `{ "expected_hint_level": 0 }` (0–3).
Responses contain `session_item_id`, revealed `hints` with level/text/phase and
`has_more_hints`; no future hints or worked solution are included. Same-key retries
return the original disclosure boundary; stale levels return `VERSION_CONFLICT`,
exhausted hints `HINT_UNAVAILABLE`, and diagnostics `HINTS_DISABLED`.
The next-item response also resumes revealed pre-answer hints. Frozen grade fields
`hint_count` and `highest_hint_level` describe use before submission only.
See [ADR-022](../decisions/ADR/022-reviewed-hints.md) and the generated OpenAPI for
complete schemas. Historical stored grade JSON may omit these additive zero defaults.

## Unseen reassessment (ADR-023)

`POST /attempts/{attempt_id}/reassessment` requires `Idempotency-Key` and no body.
It creates or resumes the one-item reassessment linked to an owned submitted revision
attempt. `GET` on the same path reads that existing linked session, returning 404 if
none exists. Both enforce current consent, subject enrollment and ownership. Diagnostic
and reassessment origins return `REASSESSMENT_NOT_ALLOWED`; insufficient unseen eligible
inventory returns `REASSESSMENT_UNAVAILABLE` (409) without creating a session.

The additive `SessionView.kind`, `original_attempt_id` and `original_session_id` fields
support the shared player and return navigation. Existing session next-item, submit,
get and abandon routes apply; active discovery includes reassessments. Exactly one
new question is selected, with no hints before submission and no early worked solution.
The original grade is immutable. Completed, abandoned or expired reassessments remain
linked; repeated starts never replace them. Selection provenance stays server-side.
See [ADR-023](../decisions/ADR/023-unseen-reassessment.md) and generated OpenAPI.

## Learner progress and history (ADR-024)

`GET /me/progress?subject_id=<uuid>` requires a currently selected subject and current
learning consent. It returns `ProgressView`: subject, topics and competencies with
mastery/confidence/display state, unique answer count, assessed/mapped skill coverage,
last evidence time, recent change and input hash; also calculation/algorithm/aggregation
versions and a safe next action. Equal-weight skill means include unassessed priors;
empty scope has null mastery. Numeric mastery is hidden below 0.25 confidence in the UI.
Diagnostic evidence is invisible until its session is completed, including abandoned
and expired diagnostics. Reads never update grades, evidence or mastery projections.

`GET /me/session-history` accepts optional `subject_id`, `limit` (1–50, default 10)
and opaque `cursor` (maximum 512 characters). Returns `data` and nullable `next_cursor`.
Entries contain owned session ID, subject/topic, kind/status, UTC start/completion times,
item/answer counts and optional original session ID for reassessment. No scores, answers
or selection internals are included. Order is descending `(started_at,id)`; cursor
signatures bind actor and subject filter. Invalid or mismatched cursors return 422;
missing authentication returns 401 and unauthorized subject/consent returns 403.
Both endpoints rate-limit to 60 requests per learner per minute and recheck current access.
See [ADR-024](../decisions/ADR/024-progress-history.md) and generated OpenAPI for DTOs.

## Learner flags and triage (ADR-025)

`POST /attempts/{attempt_id}/flag` requires current learning consent, selected-subject
access, owned submitted attempt and `Idempotency-Key`. Body: `category` from
QUESTION_ERROR/GRADE_DISPUTE/UNCLEAR/ACCESSIBILITY/UNSAFE_CONTENT/OTHER and optional
trimmed `comment` (maximum 1000 characters). It returns 201 with `id`, `category` and
`created_at`. Source item/version/reporter are server-derived. One report per attempt/
category; same payload is idempotent across keys, differing comments conflict with
`FLAG_ALREADY_REPORTED`. Key reuse with a different request returns `IDEMPOTENCY_CONFLICT`.
`GET /attempts/{attempt_id}/flag` returns owned safe receipts for recovery, never staff
notes. Diagnostic `answered_attempts` contains only attempt ID and question position;
reporting does not reveal diagnostic grades or feedback.

`GET /admin/content-flags` requires ACADEMIC_REVIEWER or ADMIN. Optional UUID `cursor`,
`limit` (1–50, default 20), and `status` filter return a page of safe summaries in UUID
order. `GET /admin/content-flags/{flag_id}` adds the confidential comment, current
resolution, retention deadline and metadata history. Staff reads are audited. DTOs
omit learner identity, raw answers and grades; no general support access is granted.

`PATCH /admin/content-flags/{flag_id}` requires recent staff authentication and an
idempotency key. Body: `expected_revision`, `status` (IN_REVIEW/RESOLVED/DISMISSED),
`priority` (NORMAL/HIGH), optional `claim` (self-assignment), and `resolution` (required
nonempty for terminal states, empty for IN_REVIEW; maximum 1000 characters). The current
owner or claiming independent reviewer records the decision. Authors cannot triage
own content; stale revision returns `VERSION_CONFLICT`. Retry returns the current flag
without applying the operation again. No grade/evidence/content rewrite is implicit.
New reports are limited to 10 per hour; flag access/triage to 60 per minute per actor.
See [ADR-025](../decisions/ADR/025-learner-flags.md) and generated contracts.

## Deterministic multiple choice (ADR-026)

Reviewed documents may use MULTIPLE_CHOICE with 2–8 unique options and a nonempty
`correct_choice_ids` subset. `correct_choice_id` must be empty and numeric_spec null.
Keys are sorted and duplicate IDs rejected. Learner response_spec exposes only the
discriminator and options, never the key or its size. SubmitAnswer accepts
`{"type":"MULTIPLE_CHOICE","choice_ids":["C","A"]}` with 1–8 unique uppercase IDs.
Selections are sorted before the idempotency fingerprint and storage. Unknown IDs,
duplicates, empty sets and response-format mismatches return 422. A changed set with
a reused key returns 409. Exact set equality earns all points; any other valid set
scores zero. The stored grader version is `multiple-choice-set-v1`.
Existing consent, ownership, version pinning, hint, solution, diagnostic seal,
reassessment and flag controls apply. See [ADR-026](../decisions/ADR/026-multiple-choice.md).

## Data-request intake (ADR-027)

`POST /me/data-requests` accepts only `{kind: EXPORT|DELETE, affirmative: true}` and
requires Idempotency-Key plus OTP authentication within ten minutes. Return 201 with
id, kind, status QUEUED/IN_REVIEW/COMPLETED, created_at, nullable reviewed_at,
completed_at, retention_due_at, download_expires_at and retention_policy
SIX_YEARS_AFTER_COMPLETION. A new key for the same pending kind returns the existing
request; a reused key for another kind/action returns 409. No learning consent, completed
profile, age or subject selection is required to request or track privacy rights.

`GET /me/data-requests` lists owned requests; `GET /me/data-requests/{target}` returns
one owned request or 404. Listing supports UUID cursor and limit 1–50 (default 20),
ordered by UUID, returning data and next_cursor. Reads require an active session.
`GET /admin/data-requests` uses the same safe page shape and requires recent ADMIN
access, auditing the queue read. It exposes no requester identity or internal notes.
`POST /admin/data-requests/{target}/claim` accepts an empty object and idempotency key,
requires recent ADMIN authentication, and starts review (200). Own-request claims are
403; another administrator's claimed request returns 409. Claims never imply fulfillment.
There is no arbitrary status update or deletion-fulfillment endpoint. New claims on
completed requests return 409; exact claim retries recover current status.

New intake keys are limited to ten/account/hour; reads and claims to sixty/account/minute.
Exact-key retries recover current status, after rechecking authentication/authorization.
Safe identity events and audit records commit atomically with request/review/receipt rows.
See [ADR-027](../decisions/ADR/027-data-request-intake.md) and its export extension below.

## Owned data exports (ADR-028)

`POST /me/data-requests/{target}/export` accepts `{}` and Idempotency-Key. The active
owner must have verified OTP within ten minutes; learning consent is not required.
Return 200 `DataExportBundle` with format_version, request_id, generated_at, exclusions
and allowlisted records. The response uses no-store, nosniff and an attachment filename
bound to the request UUID. Other owners/admins receive 404; DELETE kinds return 409.
No public download URL or staff impersonation route is provided.

Completion, digest, six-calendar-year deadline, encrypted retry copy, audit/outbox and
receipt commit atomically. COMPLETED means made available, not confirmation of saving.
Same-request downloads return the same snapshot for 24 hours; after expiry return 410
EXPORT_EXPIRED, never regenerate. A new explicit request may capture newer records.
Export calls are limited to ten/account/minute, including retries. A reused key for
another operation returns 409. Exceeding 10,000 related queried rows (besides the account profile) or 2 MiB
canonical JSON returns 409 EXPORT_LIMIT_REACHED with the request still pending.

Answers, released grades and visible mastery are projected explicitly. Credentials,
guardian evidence, internal staff/security records, keys/solutions, future assignments
and unfinished/abandoned diagnostic grades or derived mastery remain excluded. The
manifest explains the boundary. See [ADR-028](../decisions/ADR/028-owned-data-exports.md).
Deletion/anonymization, exceptional/large-history disclosure and six-year evidence
expiry with legal holds remain pending.


## Deletion-impact preview (ADR-029)

`GET /admin/data-requests/{target}/deletion-preview` requires recent OTP, ADMIN,
a pending DELETE request and an independent claim owned by that administrator.
Unknown request returns 404; EXPORT returns 409 DELETE_REQUIRED; absent/different
claim returns 403 REVIEW_OWNERSHIP_REQUIRED; own request returns 403 SELF_REVIEW_FORBIDDEN.
Limit ten previews/admin/minute, including repeat reads. Each successful read is audited.
No idempotency key is needed: this observes current counts rather than starting processing.

Return 200 DeletionPreview with request_id, observed_at, execution_enabled=false,
sources (fixed table code, count, at_least, retention category), known blockers and
explicit limitations. Each source is bounded to 10,000 with at_least=true when additional
rows exist. Overlapping staff relationships are not disjoint totals. Responses use
no-store. Errors never return partial inventories. Only relational counts are queried;
no identifiers, credentials, answers, guardian evidence or comments are decrypted or exposed.

The schema cannot enable execution. A preview changes only rate bookkeeping and a
minimized audit entry; it cannot revoke sessions, fulfill deletion, establish legal-hold
clearance or prove anonymity. Counts can change; future processing must revalidate all
conditions. See [ADR-029](../decisions/ADR/029-deletion-impact-preview.md).

## Record legal holds (ADR-030)

All paths below are under `/api/v1` and require the pending DELETE request's independent
ADMIN claimant with recent OTP authentication, including retries. Responses are no-store.

| Method/path | Contract |
| --- | --- |
| `GET /admin/data-requests/{target}/holds` | HoldPage: data and next_cursor; UUID cursor, limit 1–50 (default 20), audited, 60 reads/admin/minute |
| `POST /admin/data-requests/{target}/holds` | HoldInput plus Idempotency-Key UUID; 201 HoldView |
| `POST /admin/data-requests/{target}/holds/{hold}/release` | HoldRelease plus Idempotency-Key UUID; 200 HoldView |

HoldInput has record_type (CONSENT, ATTEMPT, CONTENT_FLAG, DATA_REQUEST, GRADE,
MASTERY_EVIDENCE, MASTERY_HISTORY, FLAG_HISTORY, DATA_REQUEST_REVIEW), owned record_id
UUID, opaque decision_reference UUID, reason (LEGAL_OBLIGATION or SECURITY_INVESTIGATION),
a timezone-aware finite future expires_at and affirmative=true. Reject extras, narratives,
unsupported record types and indefinite dates. HoldRelease has only decision_reference
and affirmative=true. These record an already authorized decision; they do not determine law.

HoldView exposes id, request_id, record_type/id, decision_reference, reason, derived
ACTIVE/EXPIRED/RELEASED status, created_at/expires_at, nullable released_at/release_reference
and retention_policy=SIX_YEARS_AFTER_REQUEST_COMPLETION. No actor or learner identifier,
record body or legal narrative is returned. Expiry does not erase metadata or underlying data.
New mutations are limited to ten/admin/minute. Exact-key retries return current hold state
without spending another write quota; the same key with another body/path returns 409
IDEMPOTENCY_CONFLICT. Equivalent end-time offsets canonicalize to UTC. Authorization is
always rechecked. Absent/foreign target or hold returns 404; inactive release returns 409
HOLD_NOT_ACTIVE; a nonfuture end returns 422 HOLD_END_REQUIRED. Claim, self-review, request
kind/completion and authentication errors use the existing deletion-review codes.

DeletionPreview now includes active_legal_holds (bounded at 10,000) and
active_holds_at_least. Sources include hold and receipt evidence. ACTIVE_RECORD_HOLDS
indicates active registered holds; LEGAL_HOLD_COVERAGE_INCOMPLETE is always present.
The old LEGAL_HOLD_CHECK_UNAVAILABLE schema literal is retained for compatibility but
is no longer emitted. execution_enabled remains false. Counts are advisory and do not
clear unrelated records. Learner exports omit internal hold details and hold outbox events.
See [ADR-030](../decisions/ADR/030-record-legal-holds.md).

## Implemented bounded synthetic import contract (ADR-032)

- `POST /api/v1/admin/content-imports`: recent CONTENT_AUTHOR, Idempotency-Key UUID;
  `ImportInput` with `format_version=kasoma-draft-import-v1`, `synthetic=true`, 1–20 records
  `{subject_id,document,change_reason}`. Maximum 64 KiB before JSON parsing. Returns 202
  `ImportView` after complete candidate validation. No successor/import approval route.
- `GET /api/v1/admin/content-imports` and `/{job_id}`: current author, owner-only cursor
  listing/status. Foreign job IDs return 404. Page limit 1–50; five new submissions/hour,
  sixty reads/minute/author. Status contains safe result positions/version IDs/outcomes,
  attempt count and error code; no raw document, bearer or exception detail.
- Exact actor/key/body replay returns current status; changed body returns 409. Oversize
  returns 413, invalid schema/taxonomy/provenance 422, rate limit 429. Responses are no-store.
- Source locator is an additive optional draft field (empty for historical documents);
  import requires it. Existing independent submission/review/publication gates apply.

Generated OpenAPI and TypeScript contracts define the exact request/response fields.
See [ADR-032](../decisions/ADR/032-bounded-draft-imports.md) and
[verification](../implementation/E2_IMPORTS_VERIFICATION.md).

## Local operations snapshot (ADR-033)

`GET /api/v1/admin/operations` requires current ADMIN membership; reads are limited to
20 per account/minute. The no-store `OperationsView` contains UTC sampling time, sanitized
PostgreSQL/Redis health, monitoring heartbeat availability, configured thresholds,
bounded counts and typed active alerts. Counts contain only numbers and lower-bound
indicators; no content/learner/staff IDs or free text. Query failure gives unavailable
counts and degraded dependency status, never fabricated zeros or raw exception text.
Uninstrumented AI/messaging/grade-failure/latency/mastery/channel metrics are explicit.
This read-only extension does not change the public health contract or domain records.

ADR-049 candidate adds nullable `request_timing`: observed sample size, p95 exclusive
lower/inclusive upper bounds, interval count, capping indicator and fixed best-effort
response-start/300-second retention labels. Empty collections have zero samples and
null bounds; measured zero has upper bound zero; overflow has no finite upper bound.
Absent/stale/malformed storage gives null and keeps REQUEST_LATENCY unavailable.
No source/process/request identifiers are exposed. Percentiles are intervals, not exact
latency or agreed-load acceptance. REQUEST_RESPONSE_START_SLOW alerts use the proven
integer lower bound after the configured minimum samples. Existing ADMIN, rate-limit
and no-store boundaries remain unchanged.

## Synthetic WhatsApp linking implementation (ADR-034)

- `POST /api/v1/channels/whatsapp/link-code`: recent owner authentication, current-policy
  learning consent and UUID `Idempotency-Key`; 201 returns a one-time 12-hex code, UUID,
  five-minute expiry and synthetic marker. Five new requests/hour; valid same-key retries
  return the original code, expired/revoked/consumed retries return 410.
- `GET /api/v1/channels/whatsapp/link`: authenticated owned status, link UUID/revision,
  link/opt-out times and local outbound flag. No sender/phone identifiers. 60 reads/minute.
- `DELETE /api/v1/channels/whatsapp/link`: recent authentication, UUID key and body
  `{expected_link_id, expected_revision}`; mismatches return 409. Current consent is not
  required to unlink. Cancels codes and pending replies, clears the bound encrypted number,
  and returns current owned status. Actor/key retries cannot undo a later link.
- `GET /api/v1/webhooks/whatsapp`: constant-time local verify-token comparison and bounded
  numeric challenge. `POST` verifies exact raw bytes with `X-Hub-Signature-256` before JSON,
  caps streaming bodies at 64 KiB and normalized batches at 20. The configured synthetic
  business/phone IDs must match. Accepted means durable receipt, not completed processing.
  Exact duplicates are acknowledged; conflicting ID reuse returns 409 and rolls back the batch.
  Events older than 30 days or over five minutes in the future are rejected.
- Every unique STOP sets a delivery barrier before acknowledgement. Worker processing rechecks
  current consent, code/sender ownership and expiry. Replies use only the deterministic fake.
  Production callbacks/delivery and WhatsApp practice have not passed acceptance.

The browser proxy exposes owner routes only; provider webhooks terminate directly at the API.
Generated OpenAPI is the exact field contract. See [readiness](../implementation/E7_LINKING_READINESS.md).

## Internal assessment transaction boundary (ADR-035, verified transaction boundary)

Public web authentication, schemas and idempotency fingerprints remain unchanged. Internal
start/serve/submit operations accept a trusted actor and caller-owned transaction, rechecking
current account, consent, level and enrollment. They do not commit and are not exposed as HTTP
actor-override endpoints. This enables future atomic channel receipt/learning writes without
manufacturing bearer tokens; channel grading remains disabled pending its migration and tests.

## Internal channel capability (ADR-037, verified foundation)

Shared start/next/submit methods accept a trusted internal `channel` argument. Default WEB and its
receipt fingerprints are unchanged. WHATSAPP fingerprints use a separate namespace, and public
start schemas still reject WHATSAPP. Channel callers must first authorize the linked sender.
Only explicit-topic five-item revision plans whose assigned versions pass approval and channel
format checks can run through these internal methods. Unsupported sessions fail closed without
replacing assignments. This is not a new HTTP endpoint or a webhook practice enablement.

## Local practice webhook flow (ADR-038, verification pending)

Signed text commands START, CONTINUE, PROGRESS and HELP require a currently linked, consented
actor for practice. START/CONTINUE shows enrolled topic choices or resumes the current five-item
revision. A menu choice or objective answer must include Meta-shaped `context.id` matching the
current successfully sent outgoing menu/question. Missing, stale or foreign context cannot select
or grade an assignment. Grade feedback includes the existing authenticated `/revise?session=UUID`
link; CONTINUE serves the next question. PROGRESS provides the authenticated web progress link.

Encrypted structured reply text is bounded to 96 characters and transient; arbitrary conversation
text is discarded. After durable intake, a bounded best-effort local Redis wake-up requests a queue
drain. Broker outages preserve accepted messages and rely on periodic recovery. New replies remain
fake-only; no cloud transport or public actor/channel override is introduced.

## Channel operational projection (ADR-039, verification pending)

`GET /admin/operations` keeps current ADMIN/rate authorization and adds optional
`counts.channel`: bounded incoming/outgoing pending counts, oldest age, recent received/created
message status cohorts and `feedback_dispatch`. Each count has `value` and `at_least`; the cap
remains 10,000. Failure/cancellation cohorts use receipt/creation time, not completion time.

`feedback_dispatch` contains `sample_size` (0–1,000), `sample_capped`, nullable `p95_ms`, and
`measure=LOCAL_FAKE_ACCEPTANCE`. It samples the latest eligible feedback dispatches sent during
the preceding 24 hours and measures durable receipt to fake transport acceptance. No observations
returns null p95. It is not proof of learner receipt or load-tested latency. No message, answer,
command, actor, recipient or domain record IDs enter the view.

Thresholds add channel failure counts, pending age, p95 milliseconds and a minimum sample size.
New warning codes are CHANNEL_INBOUND_FAILED, CHANNEL_OUTBOUND_FAILED, CHANNEL_STALLED and
CHANNEL_DISPATCH_SLOW. Missing database/query results remain unavailable, not zero. Existing
uninstrumented metrics still include AI/SMS/email usage and pre-intake webhook failures.

## Learning-record hold references (ADR-043)

The existing hold routes additionally accept GRADE, MASTERY_EVIDENCE and MASTERY_HISTORY.
For GRADE, record_id is the grade's attempt_id; for the other two it is the record's own id.
Ownership is checked through immutable parent relationships; absent or foreign targets return 404.
No parent/child cascade of hold scope is implied. All recent-auth, independent claimant, rate,
idempotency, expiry, release and audit controls remain unchanged. Generated enums and administrator
labels were extended to seven targets by ADR-043 and to nine by ADR-045 below; deletion and complete hold coverage remain unavailable.
See [ADR-043](../decisions/ADR/043-learning-record-holds.md).

## Reviewed rubric authoring (ADR-044)

Existing staff draft create/edit/review endpoints accept response_type=SHORT_TEXT and optional
rubric.criteria; VersionView adds nullable rubric_version_id. Each criterion requires an ID,
maximum_points, criterion_text, acceptable_evidence, common_errors and prohibited_inferences.
The latter two lists may explicitly be empty. Criteria are unique and ordered (1–20); text entries
are nonblank and at most 2,000 characters, lists at most ten entries. These are engineering bounds.
Review requires summed points equal the item maximum, CRITERION_SUM, no choices/answer keys/numeric
specification and all existing rights/mapping/checklist controls. Objective formats retain
ALL_OR_NOTHING and cannot carry rubrics. Absent/null rubrics serialize as absent, preserving legacy
idempotency/hash semantics. See generated OpenAPI for exact strict schemas.

No learner submission format is added. Selectors and a database guard exclude short-text items;
content approval alone does not authorize model grading. Rubric bodies remain staff-only.
[Verification](../implementation/E2_REVIEWED_RUBRICS_VERIFICATION.md).

## Accountability-record hold references (ADR-045)

The same hold routes accept FLAG_HISTORY (content_flag_history.id, owned through the flag reporter)
and DATA_REQUEST_REVIEW (data_request_reviews.request_id, owned through the reviewed request).
The review key is its request reference, not a separate review UUID. API and SQL check/lock the
named row and parent. Missing/foreign targets return 404; no record or staff payload is exposed.
A history hold permits ordinary parent triage to append new history; it preserves only the named
immutable row. All existing claimant, recent-auth, retry, finite expiry/release and audit controls
remain. See [ADR-045](../decisions/ADR/045-accountability-record-holds.md).


## Proposed asynchronous owned exports (ADR-048; not activated)

The isolated test router defines `POST /me/data-requests/{target}/export-job` (empty closed body,
Idempotency-Key, 202 current job status), `GET /me/data-requests/{target}/export-job` (bounded owner
status) and `GET /me/data-requests/{target}/export-file` (private JSON attachment). Every operation
requires the active owner and recent OTP; administrator status grants no cross-owner access.
Status excludes session-family grants, generation/object references and manifests. Download
returns exact Content-Length, no-store, nosniff and a server-generated filename; it rechecks
authority during streaming and aborts incomplete transfers. No public/presigned URL is returned.

The original synchronous export endpoint returns `EXPORT_FILE_REQUIRED` (409) for a live async
copy and `EXPORT_EXPIRED` (410) after expiry. It does not regenerate a completed request.
These routes remain unregistered in the application until the lifecycle/worker/web acceptance
gates in [ADR-048](../decisions/ADR/048-asynchronous-owned-export-delivery.md) pass; generated
application OpenAPI changes travel with that activation.


ADR-048 gateway preparation (API still unregistered): GET export-file rejects cross-site/same-site
fetch metadata, forwards only server-held cookie authorization and requests identity encoding.
It never follows upstream redirects or forwards error-body diagnostics. Initial response deadline
is eight seconds; exact-length attachment streaming has a separate 300-second deadline and propagates
disconnect cancellation. Owner queue/status routes retain ordinary gateway method/CSRF controls.

For an attachment navigation failure before response start, the web gateway returns a no-store
303 to `/privacy?export_error=<closed-code>`; it accepts no return destination and includes no
record ID/token/provider text. The privacy page maps known codes to fixed alerts. Programmatic
requests retain the closed JSON/status error. Errors after response start abort the transfer.

The ADMIN operations snapshot now includes optional `counts.exports`: bounded `queued`, `running`,
`failed_finished_24h`, and `oldest_pending_seconds`. Failure counts describe current terminal state
with finish times in the inclusive previous 24 hours; retries can remove that observation. Additive
thresholds `export_failures`/`export_age_seconds` drive closed `EXPORT_FAILED`/`EXPORT_STALLED`
warnings. No record IDs, grants or object references are disclosed. Null/missing metrics mean
unavailable, not zero. Owner async routes remain unregistered pending ADR-048 acceptance.

Current candidate: owner export-job/export-file routes are now registered and included in the
generated client for local synthetic acceptance. Earlier unregistered-stage notes are historical.
The transport/authorization contract above applies; full ADR-048 promotion remains gated.

### Durable grading metadata in owned exports

The personal-export records map adds `grading_work` and `grading_history` groups.
Both are owned through attempts and preserve the existing diagnostic-release filter.
Only attempt/status/time metadata is exposed, plus history ID/revision; correlation
IDs, worker claim tokens, internal reasons and whole snapshots remain excluded. The
new storage is not yet wired to learner short-text routes or workers. See
[durable grading verification](../implementation/E4_DURABLE_GRADING_VERIFICATION.md).

The record-hold API also accepts `GRADING_HISTORY`, with `record_id` equal to the
immutable grading-history row UUID. An attempt ID is not a history ID. Independent
ADMIN review, ownership, finite expiry, retry and release semantics remain unchanged.
Holding a history snapshot does not prevent new workflow transitions; release does
not permit mutation of retained evidence. Deletion remains disabled.

### Grading publication and audit preservation (candidate ADR-050)

The existing independently claimed administrator hold routes additionally accept
`GRADING_PUBLICATION` (record ID is the attempt UUID) and `GRADING_AUDIT` (record ID
is the audit-assignment UUID). Ownership derives from the attempt. Release preserves
record immutability. No grading or expert-review endpoint is introduced.
Owned export groups `grading_publications` and `grading_audit_assignments` contain
attempt reference/publication time and assignment reference/attempt reference/assignment
time respectively. Diagnostic sealing applies; band IDs, ordinals and sampling flags
are excluded. These groups do not disclose model grades or authorize learner scoring.

### Short-text learner flow candidate (ADR-050; not accepted yet)

Draft `SubmitAnswer.response` adds bounded nonblank SHORT_TEXT with exact preserved text.
Learner item response specs provide only type and 2000-character ceiling, never rubrics,
solutions or calibration metadata. The existing attempt submit/grade routes and session
answers distinguish PENDING, LOW_CONFIDENCE and definitive rubric GRADED results.
Pending/neutral projections contain no points, confidence or grading judgment. A pending
poll URL is relative and attempt-bound; LOW_CONFIDENCE offers an explicit review action.
A replay returns the same attempt's current outcome without re-enqueueing its work.

Rubric grades identify their pinned rubric and validated criterion evidence/feedback.
Owned exports decrypt only authorized answer/result material; internal ciphertext and
calibration band identifiers are excluded. Diagnostic feedback remains sealed until all
saved attempts have terminal outcomes; neutral attempts add no mastery evidence.
The candidate is installed in the local synthetic review stack with normal short-text
selection disabled; it is not approved for real data. Owned short-text grade reads are
limited to 120 per account per minute. The web permits twelve automatic polls at
three-second intervals with one in flight, followed by manual retry; 429 creates no grade.


### Independent synthetic grading review (candidate ADR-051)

Recent-authenticated ACADEMIC_REVIEWER only; ADMIN alone grants no access:

| Method/path | Contract |
| --- | --- |
| GET `/api/v1/admin/grading-audits` | UUID cursor, limit 1–50 (default 20), UUID-only entries and optional next cursor; 60 reads/account/minute |
| GET `/api/v1/admin/grading-audits/{audit_id}` | Blinded pinned question, exact owned encrypted response projection and complete rubric criteria; 120 reads/account/minute |
| POST `/api/v1/admin/grading-audits/{audit_id}/review` | Required Idempotency-Key, complete distinct criterion-point set, closed critical-error category, affirmative independent completion; 30 new completions/account/minute |

Task access/completion excludes the learner and item/version authors and rechecks
current roles, recent authentication and learner consent/enrollment under stable account
locks. Diagnostic tasks remain sealed until completion. Staff sees no learner identity,
model points/confidence/feedback, band IDs, sampling ordinals or previous reviews.
The queue is UUID-ordered and bounded; confidential task projection has its own current
checks. The web proxy forwards only approved cursor/limit parameters for this route.

Review categories are NONE, ACADEMIC_INTEGRITY, SAFEGUARDING and PRIVACY. All rubric
criteria require explicit integer points within their pinned maxima. SQL calculates
agreement; the client cannot submit agreement, model scores or completion ordinals.
A 201 receipt contains only id, COMPLETED status and completed_at. Exact same-actor,
same-key/body retry returns that receipt; changed input/key binding conflicts. A second
completion cannot replace the immutable first review. No grade/mastery override occurs.
Read/completion audit records retain the original correlation ID without response text
or points. GET of an already completed task returns REVIEW_ALREADY_COMPLETED.

Owned export group `grading_audit_reviews` contains review ID, attempt ID, criterion
points, completion time and `overrides_original_grade:false`; diagnostic sealing applies.
It excludes reviewer identity, agreement/critical classification, request provenance,
ordinals and band IDs. Exact hold type GRADING_REVIEW uses the completed review UUID
(equal to its assignment UUID); requester ownership derives through the attempt.
Deletion remains disabled; releasing a hold does not permit immutable-record mutation.


### Grading operations projection (candidate ADR-053)

The existing ADMIN-only rate-limited operations snapshot adds optional `counts.grading`:
queued/running, expired_running_leases, oldest_pending_seconds, graded_finished_24h,
neutral_finished_24h, processing_fallback_finished_24h, pending_audits and disabled_bands.
Counts are capped at 10,000 with the existing lower-bound marker. The terminal window
is inclusive `[now-24h,now]`; future completions are excluded. Age starts at original
queue time, spans queued/running work, and clamps future timestamps to zero. Lease
expiry is observed at `lease_until<=now`; it does not itself execute cleanup.

Processing fallback means LOW_CONFIDENCE with stored GRADING_FAILED reason, including
provider refusal and budget/validation failure. It is neither academic incorrectness
nor proof of an unexpected incident. Pending audits include sealed assignments, and
disabled bands require both activation and disablement timestamps. No record, reviewer
or band identifiers/scope are disclosed. These are read-only current-state samples.

`thresholds.grading_age_seconds` drives GRADING_STALLED at exact age equality or above;
there is no new processing-fallback or historical-disablement alert. AI_USAGE and
GRADING_FAILURE_RATE remain unavailable. Missing grading metrics are unavailable, not
zero. Existing authorization, error, monitoring and safe alert logging remain unchanged.


### Local worker model observations (ADR-054 candidate)

The existing ADMIN-only `GET /api/v1/admin/operations` adds optional `model_usage`.
Null means unavailable, expired, corrupt or unobserved instrumentation. A fresh empty
SDK collection may report zero. The closed measure is `LOCAL_WORKER_GATEWAY_ATTEMPTS`;
`retention_seconds=300`, `best_effort=true`, at most 256 intervals and explicit capping.
Only the ordinary local worker collects actual provider-port outcomes, after dispatch
barriers, including fixed fake development probes. Candidates precede validation.

`observed_attempts` equals candidate/fallback/no-result observations. Unknown token
attempts include failed calls and returned results without both explicitly supplied
usage fields. `reported_input_tokens`/`reported_output_tokens` are known subtotals;
`total_input_tokens`/`total_output_tokens` are null whenever any retained attempt has
unknown usage. Explicit provider-reported zero remains zero. Aggregates contain no
actor/request/attempt/model/provider identifiers, content or fingerprints.

`MODEL_GATEWAY_VOLUME` is a WARNING at `thresholds.model_gateway_attempts`, default100,
configurable 1–10,000. It does not enforce quotas. AI_USAGE leaves unavailable_metrics
only while this local aggregate is available; this does not imply fleet completeness,
billing or academic error-rate measurement. Existing authorization/rate limits remain.


### Terminal receipt hold extension (ADR-055 candidate)

Existing ADMIN hold routes accept CHANNEL_INBOUND_RECEIPT and
CHANNEL_OUTBOUND_RECEIPT only when the typed staged-creation flag is enabled. They
refer to original owned message UUIDs after terminal processing has cleared transient
sender/recipient/code/reply material. Queued, unbound and cross-owner targets remain
not found. No receipt body or plaintext is returned. Ownership, independent claimant,
recent auth, finite expiry, exact replay/rates and audit remain required.

HoldPage adds supported_record_types. UI clients show new choices only when advertised;
older responses may omit that field. With creation disabled, new-kind creates/replays
return409 HOLD_TARGET_UNAVAILABLE; listing and releasing registered holds still work.
No new route, body upload, broad account hold, data-copy artifact or deletion permission.
Delivery callbacks may advance only the existing monotonic lifecycle; held receipt core
fields cannot be rewritten/requeued. The preview remains advisory/incomplete.

## Bounded audit activity (ADR-058 candidate)

`GET /api/v1/admin/audit` requires ADMIN on every read; no learner/support/reviewer-only
access, object search, arbitrary filter or individual-record payload is provided. Limit
twenty reads per administrator per minute. Return `AuditActivity` with `window_start`,
`window_end` (last 24 hours, inclusive bounds), `sampled_count`, `capped`, fixed
`sample_limit=10000`, `measure=AUDIT_ACTIVITY_SAMPLE` and seven `counts` entries.
Categories are CONTENT, FLAGS, IMPORTS, PRIVACY, ROLES, GRADING_REVIEW and OTHER.
Counts sum to the newest sampled rows, ordered by created_at then UUID descending;
future rows are excluded. A cap means older actions in this window may be omitted,
including from any category. Zero means no matching audited actions in this window,
not absence of incidents or proof of complete auditing.

SQL maps known action prefixes to fixed labels before transfer; unknown action text,
actor/target/request identifiers, reasons and hashes never enter this response. No
read-self audit row or record decryption occurs. Existing authorization and audit
immutability/retention remain; aggregate access does not grant learner-level support.

## Channel preservation format boundary (ADR-057 first increment)

The approved synthetic private-format increment introduces no API, generated schema,
reader permission or supported hold kind. In particular, internal integrity decoding
is not a payload-reading/export endpoint. No client may submit snapshot kinds through
the existing original-record hold contract. Capture/capability/version-selection
contracts remain pending and must ship with authorization, SQL/lifecycle and UI tests.

## Synthetic channel capture candidate (ADR-057)

CHANNEL_PRESERVATION_ENABLED defaults false. Both new routes require a recent-OTP
independent ADMIN claimant of the pending DELETE request, before inspecting feature
availability. Creation disabled returns409 HOLD_TARGET_UNAVAILABLE. No payload-read
or source-browsing endpoint exists.

- POST `/admin/data-requests/{target}/channel-preservations/inspect`: strict
  PreservationSource contains source_kind (CHANNEL_LINK_SNAPSHOT or
  CHANNEL_CONVERSATION_SNAPSHOT), actual source_link_id UUID and positive int32
  link_revision. Return only PreservationVersion.source_version, a64-hex opaque keyed
  current-version value. Share the existing60/minute hold-read budget and audit the
  inspection without source payload/IDs. JSON body keeps operational IDs out of URLs.
- POST `/admin/data-requests/{target}/channel-preservations`: strict PreservationCapture
  adds source_version, authorized decision_reference UUID, existing reason code,
  finite future expires_at and affirmative=true. Require Idempotency-Key UUID; share
  the existing10/minute hold-write pool. Return201 HoldView with a newly generated
  snapshot UUID in record_id and the explicit snapshot kind. It is not a source-row hold.

Stale versions return409 SOURCE_VERSION_CONFLICT. Unavailable, cleared, stopped,
unlinked, expired or cross-owner sources return404 without guessing history. Claim
timestamps ahead of database time fail503; an invalid finite end returns422. Exact
key/body retries return the existing decision and never recapture changing state.
Input expiry normalizes to UTC for retry binding; all response data remains no-store.

HoldPage.supported_record_types advertises snapshot kinds only when creation is enabled.
The existing hold POST may add a finite decision to an existing same-request snapshot
UUID while its body exists. These IDs never authorize source access, dispatch or resume.
Existing list/release and disposal remain available after creation is disabled. New
snapshot decisions use database wall clock for creation/status/release and preview counts;
historical record_is_held queries and legacy original-record behavior remain unchanged.

The exact web proxy admits only POST for the two new paths. Operator controls separately
check the source and confirm an authorized finite capture, preserve the same key/body
after an uncertain response, and clear stale selections before a new capture. No
source version, payload or internal ciphertext is displayed. Browser acceptance remains pending.

### Exact export evidence references (ADR-060 additive candidate)

`GET /api/v1/admin/data-requests/{target}/holds/export-sources/{source}` requires
recent independent ADMIN ownership of the pending DELETE case target and an exact
EXPORT source owned by its requester. It shares the 60/minute hold-read pool and
returns no-store ExportHoldSources: receipt_ids (at most50), next_cursor and optional
export_job_id. limit defaults20/max50; cursor is an exclusive receipt UUID, ordered
ascending. No keys, hashes, grants, contacts or source bodies are disclosed. Missing,
foreign and non-EXPORT sources return404; unauthenticated/unauthorized access uses
existing401/403 policy. Lookup remains readable independently of the creation flag.

Existing hold POST additionally accepts DATA_REQUEST_RECEIPT (receipt UUID) and
EXPORT_JOB_RECEIPT (request UUID). Both require EXPORT_EVIDENCE_HOLDS_ENABLED, false
by default, otherwise409 HOLD_TARGET_UNAVAILABLE. Receipt ownership follows its EXPORT parent; a staff claim actor is not the
subject owner. Jobs must be EXPIRED with no grant/current generation or generation rows.
Finite dates use database wall clock and exact ownership is independently guarded in
SQL. Missing/ineligible sources return404; release/listing remain independent of the
creation flag. Existing exact retry semantics and DELETE guards are unchanged.
The approved finite retry-retirement boundary awaits the separate processor increment.

### Finite request retry evidence (ADR-060 synthetic SQL candidate)

The bounded SQL processor can retire only eligible completed EXPORT evidence after
its six-year deadline, exact hold checks and completed24-hour copy cleanup. During
retention existing actor/key retry binding is unchanged. After lawful receipt removal,
a subsequent current recently authenticated POST with that key follows ordinary
rate limits and pending-kind deduplication, potentially creating a fresh request.
It never restores the retired request or copy; retired owned GET uses existing404
absence. No indefinite key tombstone or API-triggered retirement is added. This is
synthetic-only; real-data execution/account erasure remains unauthorized.

### ADR-060 synthetic maintenance operations (candidate)

The existing ADMIN-only, rate-limited snapshot adds optional `counts.retirement`:
non-secret schedule/database/scope booleans, capped due completed-EXPORT parent count,
database progress age, closed last-attempt status/time and bounded removed/examined
counts, plus a capped current five-minute failure count. `observation_available`
distinguishes cache loss from zero; `failure_interval_seconds=300` and
`best_effort=true` make its finite diagnostic scope explicit. No source IDs, executor
DSN, receipt retry identity or payload is returned. Due counts do not establish
removability. Existing authorization and operation-count schemas remain compatible.

`RETIREMENT_FAILED` and `RETIREMENT_STALLED` are fixed WARNING codes, gated on all
three activation/scope booleans. The former starts at one retained interval failure;
the latter starts at twice the configured interval without a database batch/activation.
There is no HTTP enablement, provisioning or deletion endpoint. Review-stack state
stays false; the separately credentialed SQL execution is isolated synthetic only.
See [candidate verification](../implementation/E8_EXPORT_RETIREMENT_OPERATIONS_VERIFICATION.md).
