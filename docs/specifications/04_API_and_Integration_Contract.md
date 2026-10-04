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
MASTERY_EVIDENCE, MASTERY_HISTORY), owned record_id
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
labels reflect seven supported targets; deletion and complete hold coverage remain unavailable.
See [ADR-043](../decisions/ADR/043-learning-record-holds.md).
