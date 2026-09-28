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
