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
id, kind, status QUEUED/IN_REVIEW, created_at, nullable reviewed_at and retention_policy
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
No update/completion or deletion endpoint exists in this slice.

New intake keys are limited to ten/account/hour; reads and claims to sixty/account/minute.
Exact-key retries recover current status, after rechecking authentication/authorization.
Safe identity events and audit records commit atomically with request/review/receipt rows.
Machine-readable export delivery, anonymization and retention-aware fulfillment remain
pending. See [ADR-027](../decisions/ADR/027-data-request-intake.md).
