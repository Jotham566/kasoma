# Erasure source inventory — public schema 0042

Status: factual assessment, not a deletion allowlist, transform or approved ADR.
Requirements: FR-ID-006, BR-010, FR-OPS-003, FR-GRD-003/004/005,
NFR-SEC-002 and NFR-MNT-001.

## Evidence and limits

On 19 October 2026, a read-only PostgreSQL catalog inspection of the local development
schema at migration 0042 was compared field-for-field against the working assessment
snapshot from main `ebbf00c97527899fb50a109f18ddc333f0017d3d`. All 69 table definitions
in that snapshot match: 488 columns, 120 foreign keys and 97 non-internal triggers.
Only catalog metadata and the migration/activation singleton were read; no learner
records, identifier hashes, payloads or credentials are included. Review retirement
remains false. This inventory is documentation evidence, not an application test.

The tables below include every column, FK definition, CHECK constraint name and
non-internal trigger name/function observed. Nullable columns have `?`; trigger `O`
means enabled for ordinary origin operations. CHECK expressions, primary/unique/index
constraints, trigger bodies, grants, JSON structures and application/provider code
are **not** reproduced here. Inspect migrations and domain services before deciding
ownership or transforms. A trigger name alone does not prove its protection semantics.
The foreign-key graph is relational evidence, not proof that embedded references,
free text, logs, queues, exported objects or backups have been accounted for.

## Assessment groups

These are reading groups, not mutually exclusive ownership or retention rules.
An owned learner's grading review also contains another person's reviewer provenance;
a staff actor's records may concern other learners. Group membership grants no DELETE,
UPDATE, preservation, new retention period or assertion of anonymity.

| Group | Ownership/dependency question for the proposed transform |
| --- | --- |
| Shared controls | Keep global curriculum, band authority and lifetime counters independent of learner ownership. Resolve affected rolling quality windows explicitly. |
| Shared academic/staff provenance | Separate subject-as-staff from subject-as-learner; never delete other people's content or rewrite reviewers merely to remove an FK. |
| Identity anchor | Decide the minimal lawful retained reference and its finite dependency lifecycle before removing identifiers; a disabled UUID stub remains personal linkage. |
| Authentication capabilities | Revoke early at actual authorized processing, including races with refresh, OTP verification and link-code consumption; do not preserve usable credentials. |
| Direct identity/profile | Decide exact field removal and necessary retained dependencies; a link's STOP/barrier semantics must survive safely. |
| Owned learning and grading | Trace subject through session/attempt/evidence/assignment ownership, with exact holds and minimal required source dependencies. Shared grading counters are not owned learning rows. |
| Identity events | Review current payload schema and unpublished worker behavior; references can survive without an FK. |
| Channel state and delivery | Terminal receipt holds and minimized version snapshots do not cover every live body, contact, reply or dispatch capability. Resolve worker/STOP/preservation races. |
| Consent evidence | Apply six years after actual closure/withdrawal with exact holds; do not fabricate a closure date. |
| Accountability | Distinguish material administrative, security and request evidence. Preserve original actors and exact deadlines; pending requests have no completion date. |
| Content flags | Keep approved resolution-based retention and exact evidence dependencies; do not invent a resolution or confuse a learner's original report with staff triage. |
| Export artifacts | Finish retryable copy/object cleanup without losing the locator or allowing post-closure publication to resurrect data. |
| Exact preservation body | Apply ADR-057's minimized field allowlist and finite exact-hold disposal; it does not authorize a new full-body archive. |
| Shared transient keys | Prove ownership independently; matching opaque hashes or preview counts do not justify deleting another account's anti-abuse/STOP state. |

## Complete table and column inventory

### `alembic_version`

Assessment group: Shared controls.

Columns: `version_num: varchar`.

Foreign keys: none.

CHECK names: none.

Triggers: none.

### `assessment_grading_history`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `attempt_id: uuid`, `revision: int4`, `snapshot: jsonb`.

Foreign keys:

- `assessment_grading_history_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES assessment_grading_work(attempt_id)`

CHECK names: none.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_grading_history` → `grading_history_guard` (O).

### `assessment_grading_work`

Assessment group: Owned learning and grading.

Columns: `attempt_id: uuid`, `correlation_id: uuid`, `revision: int4`, `status: text`, `queued_at: timestamptz`, `claim_id?: uuid`, `claimed_at?: timestamptz`, `lease_until?: timestamptz`, `finished_at?: timestamptz`, `reason?: text`.

Foreign keys:

- `assessment_grading_work_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES attempts(id)`

CHECK names: `assessment_grading_work_check`, `assessment_grading_work_check1`, `assessment_grading_work_check2`, `assessment_grading_work_check3`, `assessment_grading_work_check4`, `assessment_grading_work_check5`, `assessment_grading_work_check6`, `assessment_grading_work_check7`, `assessment_grading_work_reason_check`, `assessment_grading_work_revision_check`, `assessment_grading_work_status_check`.

Triggers: `bound_grading_work` → `grading_work_guard` (O); `record_grading_transition` → `record_grading_transition` (O); `record_neutral_grading_outcome` → `record_neutral_grading_outcome` (O).

### `assessment_outbox_events`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `session_id: uuid`, `attempt_id?: uuid`, `type: text`, `version: int4`, `request_id: uuid`, `created_at: timestamptz`, `published_at?: timestamptz`, `hint_count?: int4`, `highest_hint_level?: int4`.

Foreign keys:

- `assessment_outbox_events_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES attempts(id)`
- `assessment_outbox_events_session_id_fkey`: `FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)`

CHECK names: `assessment_outbox_events_highest_hint_level_check`, `assessment_outbox_events_hint_count_check`, `assessment_outbox_events_type_check`, `assessment_outbox_events_version_check`.

Triggers: none.

### `assessment_receipts`

Assessment group: Owned learning and grading.

Columns: `learner_id: uuid`, `key: uuid`, `request_hash: text`, `session_id: uuid`, `attempt_id?: uuid`, `hint_use_id?: uuid`.

Foreign keys:

- `assessment_receipts_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES attempts(id)`
- `assessment_receipts_hint_use_id_fkey`: `FOREIGN KEY (hint_use_id) REFERENCES hint_uses(id)`
- `assessment_receipts_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`
- `assessment_receipts_session_id_fkey`: `FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)`

CHECK names: none.

Triggers: `immutable_assessment_receipt` → `assessment_immutable` (O).

### `assessment_sessions`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `learner_id: uuid`, `subject_id: uuid`, `topic_id?: uuid`, `status: text`, `item_count: int4`, `reason: text`, `plan_version: text`, `started_at: timestamptz`, `expires_at: timestamptz`, `completed_at?: timestamptz`, `kind: text`, `diagnostic_result?: json`, `recommendation_snapshot?: json`.

Foreign keys:

- `assessment_sessions_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`
- `assessment_sessions_subject_id_fkey`: `FOREIGN KEY (subject_id) REFERENCES subjects(id)`
- `assessment_sessions_topic_id_fkey`: `FOREIGN KEY (topic_id) REFERENCES topics(id)`

CHECK names: `assessment_kind_count`, `assessment_sessions_check`, `assessment_sessions_kind_check`, `assessment_sessions_status_check`, `diagnostic_result_completed`, `recommendation_revision_only`.

Triggers: `fixed_diagnostic_result` → `diagnostic_result_guard` (O); `fixed_reassessment` → `fixed_reassessment_session` (O); `reassessment_session_complete` → `reassessment_assignment_guard` (O); `recommendation_snapshot_immutable` → `recommendation_snapshot_guard` (O).

### `attempts`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `learner_id: uuid`, `session_item_id: uuid`, `item_version_id: uuid`, `choice_id?: text`, `submitted_at: timestamptz`, `hint_count: int4`, `channel: text`, `response?: jsonb`, `highest_hint_level: int4`, `rubric_version_id?: uuid`.

Foreign keys:

- `attempts_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`
- `attempts_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`
- `attempts_rubric_version_id_fkey`: `FOREIGN KEY (rubric_version_id) REFERENCES rubrics(id)`
- `attempts_session_item_id_fkey`: `FOREIGN KEY (session_item_id) REFERENCES session_items(id)`

CHECK names: `attempts_channel_check`, `attempts_choice_id_check`, `bounded_hints`, `bounded_structured_response`, `one_response_representation`, `pinned_attempt_rubric`.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_attempt` → `assessment_attempt_guard` (O); `bound_attempt_hints` → `attempt_hint_guard` (O); `immutable_attempt` → `assessment_immutable` (O); `short_text_submission_consistent` → `short_text_submission_consistent` (O); `supported_channel_attempt` → `channel_attempt_guard` (O).

### `audit_log`

Assessment group: Accountability.

Columns: `id: uuid`, `actor_id?: uuid`, `target_id: uuid`, `action: text`, `reason: text`, `request_id: uuid`, `before_hash?: text`, `after_hash?: text`, `created_at: timestamptz`.

Foreign keys:

- `audit_log_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`

CHECK names: none.

Triggers: `immutable_history` → `reject_content_history_mutation` (O).

### `auth_sessions`

Assessment group: Authentication capabilities.

Columns: `id: uuid`, `user_id: uuid`, `family: uuid`, `access_hash: varchar`, `refresh_hash: varchar`, `authenticated_at: timestamptz`, `access_expires_at: timestamptz`, `expires_at: timestamptz`, `rotated_at?: timestamptz`, `revoked_at?: timestamptz`.

Foreign keys:

- `auth_sessions_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: none.

Triggers: none.

### `channel_links`

Assessment group: Direct identity/profile.

Columns: `id: uuid`, `user_id: uuid`, `sender_hash: text`, `external_identifier_encrypted?: text`, `status: text`, `revision: int4`, `linked_at: timestamptz`, `opted_out_at?: timestamptz`, `updated_at: timestamptz`.

Foreign keys:

- `channel_links_sender_hash_fkey`: `FOREIGN KEY (sender_hash) REFERENCES channel_senders(sender_hash)`
- `channel_links_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `channel_links_check`, `channel_links_check1`, `channel_links_linked_at_check`, `channel_links_revision_check`, `channel_links_status_check`, `channel_links_updated_at_check`.

Triggers: `channel_owner_guard` → `protect_channel_owner` (O).

### `channel_mutation_receipts`

Assessment group: Channel state and delivery.

Columns: `actor_id: uuid`, `key: uuid`, `request_hash: text`, `created_at: timestamptz`.

Foreign keys:

- `channel_mutation_receipts_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`

CHECK names: `channel_mutation_receipts_created_at_check`.

Triggers: none.

### `channel_preservation_bodies`

Assessment group: Exact preservation body.

Columns: `snapshot_id: uuid`, `encrypted_payload: text`.

Foreign keys:

- `channel_preservation_bodies_snapshot_id_fkey`: `FOREIGN KEY (snapshot_id) REFERENCES channel_preservation_snapshots(id)`

CHECK names: `channel_preservation_bodies_encrypted_payload_check`.

Triggers: `channel_snapshot_body` → `channel_snapshot_body_guard` (O).

### `channel_preservation_disposals`

Assessment group: Accountability.

Columns: `snapshot_id: uuid`, `disposed_at: timestamptz`.

Foreign keys:

- `channel_preservation_disposals_snapshot_id_fkey`: `FOREIGN KEY (snapshot_id) REFERENCES channel_preservation_snapshots(id)`

CHECK names: `channel_preservation_disposals_disposed_at_check`.

Triggers: `channel_snapshot_disposal_complete` → `channel_snapshot_disposal_complete` (O); `immutable_channel_disposal` → `assessment_immutable` (O).

### `channel_preservation_snapshots`

Assessment group: Accountability.

Columns: `id: uuid`, `request_id: uuid`, `source_kind: text`, `source_link_id: uuid`, `link_revision: int4`, `source_state_version?: int8`, `source_version: text`, `captured_by: uuid`, `captured_at: timestamptz`.

Foreign keys:

- `channel_preservation_snapshots_captured_by_fkey`: `FOREIGN KEY (captured_by) REFERENCES users(id)`
- `channel_preservation_snapshots_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES data_subject_requests(id)`

CHECK names: `channel_preservation_snapshots_captured_at_check`, `channel_preservation_snapshots_check`, `channel_preservation_snapshots_link_revision_check`, `channel_preservation_snapshots_source_kind_check`, `channel_preservation_snapshots_source_version_check`.

Triggers: `channel_snapshot_capture` → `channel_snapshot_capture_guard` (O); `channel_snapshot_complete` → `channel_snapshot_complete` (O); `immutable_channel_snapshot` → `assessment_immutable` (O).

### `channel_senders`

Assessment group: Shared transient keys.

Columns: `sender_hash: text`, `barrier_at?: timestamptz`, `last_provider_at?: timestamptz`, `updated_at: timestamptz`.

Foreign keys: none.

CHECK names: `channel_senders_barrier_at_check`, `channel_senders_last_provider_at_check`, `channel_senders_updated_at_check`.

Triggers: none.

### `competencies`

Assessment group: Shared controls.

Columns: `id: uuid`, `name: varchar`.

Foreign keys: none.

CHECK names: none.

Triggers: none.

### `concepts`

Assessment group: Shared controls.

Columns: `id: uuid`, `topic_id: uuid`, `name: varchar`, `syllabus_reference: text`, `synthetic: bool`.

Foreign keys:

- `concepts_topic_id_fkey`: `FOREIGN KEY (topic_id) REFERENCES topics(id)`

CHECK names: none.

Triggers: none.

### `consent_records`

Assessment group: Consent evidence.

Columns: `id: uuid`, `user_id: uuid`, `consent_type: text`, `basis: text`, `policy_version: text`, `evidence_encrypted?: text`, `granted_at: timestamptz`, `revoked_at?: timestamptz`, `idempotency_key: uuid`, `request_hash: text`.

Foreign keys:

- `consent_records_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `consent_records_consent_type_check`.

Triggers: `aa_protect_held_record` → `protect_held_record` (O).

### `content_flag_history`

Assessment group: Content flags.

Columns: `id: uuid`, `flag_id: uuid`, `actor_id: uuid`, `revision: int4`, `status: text`, `priority: text`, `owner_id?: uuid`, `resolution_hash?: text`, `created_at: timestamptz`.

Foreign keys:

- `content_flag_history_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `content_flag_history_flag_id_fkey`: `FOREIGN KEY (flag_id) REFERENCES content_flags(id)`
- `content_flag_history_owner_id_fkey`: `FOREIGN KEY (owner_id) REFERENCES users(id)`

CHECK names: none.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_flag_history` → `flag_history_guard` (O); `immutable_flag_history` → `assessment_immutable` (O).

### `content_flag_receipts`

Assessment group: Content flags.

Columns: `actor_id: uuid`, `key: uuid`, `request_hash: text`, `flag_id: uuid`.

Foreign keys:

- `content_flag_receipts_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `content_flag_receipts_flag_id_fkey`: `FOREIGN KEY (flag_id) REFERENCES content_flags(id)`

CHECK names: none.

Triggers: `immutable_flag_receipt` → `assessment_immutable` (O).

### `content_flags`

Assessment group: Content flags.

Columns: `id: uuid`, `item_id: uuid`, `item_version_id: uuid`, `attempt_id: uuid`, `reporter_id: uuid`, `category: text`, `comment_encrypted: text`, `report_hash: text`, `status: text`, `priority: text`, `owner_id?: uuid`, `revision: int4`, `resolution_encrypted?: text`, `created_at: timestamptz`, `updated_at: timestamptz`, `resolved_at?: timestamptz`, `retention_due_at?: timestamptz`.

Foreign keys:

- `content_flags_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES attempts(id)`
- `content_flags_item_id_fkey`: `FOREIGN KEY (item_id) REFERENCES items(id)`
- `content_flags_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`
- `content_flags_owner_id_fkey`: `FOREIGN KEY (owner_id) REFERENCES users(id)`
- `content_flags_reporter_id_fkey`: `FOREIGN KEY (reporter_id) REFERENCES users(id)`

CHECK names: `content_flags_category_check`, `content_flags_check`, `content_flags_check1`, `content_flags_priority_check`, `content_flags_revision_check`, `content_flags_status_check`, `terminal_flag_retention_required`.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_flag` → `flag_binding_guard` (O); `complete_flag_history` → `flag_audit_required` (O).

### `content_import_jobs`

Assessment group: Shared academic/staff provenance.

Columns: `id: uuid`, `actor_id: uuid`, `key: uuid`, `request_hash: text`, `request_id: uuid`, `payload?: jsonb`, `results: jsonb`, `status: text`, `attempts: int4`, `error_code?: text`, `created_at: timestamptz`, `available_at: timestamptz`, `expires_at: timestamptz`, `finished_at?: timestamptz`.

Foreign keys:

- `content_import_jobs_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`

CHECK names: `content_import_jobs_attempts_check`, `content_import_jobs_check`, `content_import_jobs_check1`, `content_import_jobs_check2`, `content_import_jobs_check3`, `content_import_jobs_results_check`.

Triggers: `protect_content_import` → `content_import_guard` (O).

### `content_mutation_receipts`

Assessment group: Shared academic/staff provenance.

Columns: `actor_id: uuid`, `key: uuid`, `request_hash: text`, `item_version_id: uuid`.

Foreign keys:

- `content_mutation_receipts_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `content_mutation_receipts_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`

CHECK names: none.

Triggers: none.

### `content_outbox_events`

Assessment group: Shared academic/staff provenance.

Columns: `id: uuid`, `item_version_id: uuid`, `type: text`, `version: int4`, `request_id: uuid`, `created_at: timestamptz`.

Foreign keys:

- `content_outbox_events_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`

CHECK names: none.

Triggers: none.

### `content_reviews`

Assessment group: Shared academic/staff provenance.

Columns: `id: uuid`, `item_version_id: uuid`, `reviewer_id: uuid`, `content_hash: text`, `review_round: int4`, `decision: text`, `checklist: json`, `reason: text`, `created_at: timestamptz`.

Foreign keys:

- `content_reviews_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`
- `content_reviews_reviewer_id_fkey`: `FOREIGN KEY (reviewer_id) REFERENCES users(id)`

CHECK names: `content_reviews_decision_check`.

Triggers: `immutable_history` → `reject_content_history_mutation` (O); `protect_review` → `guard_content_review` (O).

### `conversation_states`

Assessment group: Channel state and delivery.

Columns: `link_id: uuid`, `actor_id: uuid`, `link_revision: int4`, `session_id?: uuid`, `expected_outbound_id?: uuid`, `updated_at: timestamptz`, `expires_at: timestamptz`, `state_version: int8`.

Foreign keys:

- `conversation_states_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `conversation_states_expected_outbound_id_fkey`: `FOREIGN KEY (expected_outbound_id) REFERENCES outbound_messages(id) ON DELETE CASCADE`
- `conversation_states_link_id_fkey`: `FOREIGN KEY (link_id) REFERENCES channel_links(id)`
- `conversation_states_session_id_fkey`: `FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)`

CHECK names: `conversation_states_check`, `conversation_states_link_revision_check`, `conversation_states_updated_at_check`.

Triggers: `bound_conversation` → `conversation_owner_guard` (O); `conversation_version` → `assign_conversation_version` (O).

### `data_exports`

Assessment group: Export artifacts.

Columns: `request_id: uuid`, `encrypted_payload: text`, `digest: text`, `created_at: timestamptz`, `expires_at: timestamptz`.

Foreign keys:

- `data_exports_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES data_subject_requests(id)`

CHECK names: `data_exports_check`, `data_exports_digest_check`, `data_exports_encrypted_payload_check`.

Triggers: `export_completion` → `export_requires_completion` (O); `protect_export` → `data_export_guard` (O).

### `data_request_receipts`

Assessment group: Accountability.

Columns: `actor_id: uuid`, `key: uuid`, `request_hash: text`, `request_id: uuid`, `id: uuid`.

Foreign keys:

- `data_request_receipts_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `data_request_receipts_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES data_subject_requests(id)`

CHECK names: none.

Triggers: `aa_protect_export_evidence_hold` → `protect_export_evidence_hold` (O); `immutable_data_request` → `export_retirement_leaf_guard` (O).

### `data_request_reviews`

Assessment group: Accountability.

Columns: `request_id: uuid`, `actor_id: uuid`, `created_at: timestamptz`.

Foreign keys:

- `data_request_reviews_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `data_request_reviews_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES data_subject_requests(id)`

CHECK names: none.

Triggers: `aa_protect_held_record` → `protect_held_request_review` (O); `immutable_data_request` → `export_retirement_leaf_guard` (O); `protect_data_review` → `data_request_review_guard` (O).

### `data_subject_requests`

Assessment group: Accountability.

Columns: `id: uuid`, `user_id: uuid`, `kind: text`, `authenticated_at: timestamptz`, `verification_method: text`, `retention_policy: text`, `created_at: timestamptz`, `completed_at?: timestamptz`, `retention_due_at?: timestamptz`, `export_digest?: text`.

Foreign keys:

- `data_subject_requests_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `data_subject_requests_check`, `data_subject_requests_kind_check`, `data_subject_requests_retention_policy_check`, `data_subject_requests_verification_method_check`.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `immutable_data_request` → `data_request_completion_guard` (O).

### `export_retirement_state`

Assessment group: Shared controls.

Columns: `singleton: bool`, `enabled: bool`, `phase: int2`, `next_receipt?: uuid`, `next_review?: uuid`, `next_job?: uuid`, `next_request?: uuid`, `updated_at: timestamptz`.

Foreign keys: none.

CHECK names: `export_retirement_state_phase_check`, `export_retirement_state_singleton_check`.

Triggers: none.

### `grades`

Assessment group: Owned learning and grading.

Columns: `attempt_id: uuid`, `item_version_id: uuid`, `answer_specification_hash: text`, `result: json`, `rubric_version_id?: uuid`.

Foreign keys:

- `grades_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES attempts(id)`
- `grades_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`
- `grades_rubric_version_id_fkey`: `FOREIGN KEY (rubric_version_id) REFERENCES rubrics(id)`

CHECK names: `grades_result_check`, `grades_result_check1`, `grades_result_check2`, `pinned_grade_rubric`.

Triggers: `aa_protect_held_record` → `protect_held_grade` (O); `bound_encrypted_rubric_grade` → `encrypted_rubric_grade_guard` (O); `bound_grade` → `assessment_grade_guard` (O); `grading_publication_consistent` → `grading_publication_consistent` (O); `immutable_grade` → `assessment_immutable` (O); `rubric_publication_consistent` → `rubric_publication_consistent` (O).

### `grading_audit_assignments`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `attempt_id: uuid`, `assigned_at: timestamptz`.

Foreign keys:

- `grading_audit_assignments_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES grading_publications(attempt_id)`

CHECK names: none.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_grading_audit_assignment` → `grading_audit_assignment_guard` (O).

### `grading_audit_reviews`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `band_id: uuid`, `reviewer_id: uuid`, `criterion_points: jsonb`, `critical_error: text`, `exact_agreement: bool`, `completion_ordinal: int8`, `completed_at: timestamptz`, `request_key: uuid`, `request_hash: text`, `correlation_id: uuid`.

Foreign keys:

- `grading_audit_reviews_band_id_fkey`: `FOREIGN KEY (band_id) REFERENCES grading_bands(id)`
- `grading_audit_reviews_id_fkey`: `FOREIGN KEY (id) REFERENCES grading_audit_assignments(id)`
- `grading_audit_reviews_reviewer_id_fkey`: `FOREIGN KEY (reviewer_id) REFERENCES users(id)`

CHECK names: `grading_audit_reviews_completion_ordinal_check`, `grading_audit_reviews_critical_error_check`, `grading_audit_reviews_request_hash_check`.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_grading_audit_review` → `grading_audit_review_guard` (O); `record_grading_audit_review` → `record_grading_audit_review` (O).

### `grading_band_history`

Assessment group: Shared controls.

Columns: `id: uuid`, `band_id: uuid`, `revision: int4`, `snapshot: jsonb`.

Foreign keys:

- `grading_band_history_band_id_fkey`: `FOREIGN KEY (band_id) REFERENCES grading_bands(id)`

CHECK names: none.

Triggers: `protect_grading_band_history` → `grading_band_history_guard` (O).

### `grading_bands`

Assessment group: Shared controls.

Columns: `id: uuid`, `subject_id: uuid`, `topic_id: uuid`, `language: text`, `model_version: text`, `prompt_version: text`, `configuration_version: text`, `policy_version: text`, `minimum_characters: int4`, `maximum_characters: int4`, `benchmark_id: uuid`, `report_sha256: text`, `benchmark_cases: int8`, `benchmark_within_tolerance: int8`, `held_out_cases: int8`, `held_out_exact: int8`, `critical_errors: int8`, `subgroup_review: text`, `approval_id?: uuid`, `approved_at?: timestamptz`, `enabled: bool`, `created_at: timestamptz`, `updated_at: timestamptz`, `activated_at?: timestamptz`, `disabled_at?: timestamptz`, `disable_reason?: text`, `revision: int4`.

Foreign keys:

- `grading_band_topic_subject_fk`: `FOREIGN KEY (topic_id, subject_id) REFERENCES topics(id, subject_id)`
- `grading_bands_subject_id_fkey`: `FOREIGN KEY (subject_id) REFERENCES subjects(id)`
- `grading_bands_topic_id_fkey`: `FOREIGN KEY (topic_id) REFERENCES topics(id)`

CHECK names: `grading_bands_benchmark_cases_check`, `grading_bands_check`, `grading_bands_check1`, `grading_bands_check10`, `grading_bands_check2`, `grading_bands_check3`, `grading_bands_check4`, `grading_bands_check5`, `grading_bands_check6`, `grading_bands_check7`, `grading_bands_check8`, `grading_bands_check9`, `grading_bands_configuration_version_check`, `grading_bands_critical_errors_check`, `grading_bands_disable_reason_check`, `grading_bands_held_out_cases_check`, `grading_bands_language_check`, `grading_bands_minimum_characters_check`, `grading_bands_model_version_check`, `grading_bands_policy_version_check`, `grading_bands_prompt_version_check`, `grading_bands_report_sha256_check`, `grading_bands_revision_check`, `grading_bands_subgroup_review_check`.

Triggers: `initialize_grading_publication_counter` → `initialize_grading_publication_counter` (O); `initialize_grading_review_counter` → `initialize_grading_review_counter` (O); `protect_grading_band` → `grading_band_guard` (O); `record_grading_band_transition` → `record_grading_band_transition` (O).

### `grading_publication_counters`

Assessment group: Shared controls.

Columns: `band_id: uuid`, `returned_grades: int8`, `assigned_audits: int8`.

Foreign keys:

- `grading_publication_counters_band_id_fkey`: `FOREIGN KEY (band_id) REFERENCES grading_bands(id)`

CHECK names: `grading_publication_counters_returned_grades_check`, `minimum_audit_coverage`.

Triggers: `protect_grading_publication_counter` → `grading_publication_counter_guard` (O).

### `grading_publications`

Assessment group: Owned learning and grading.

Columns: `attempt_id: uuid`, `band_id: uuid`, `ordinal: int8`, `audit_required: bool`, `published_at: timestamptz`, `sampling_policy: text`, `session_ordinal?: int4`.

Foreign keys:

- `grading_publications_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES grades(attempt_id)`
- `grading_publications_band_id_fkey`: `FOREIGN KEY (band_id) REFERENCES grading_bands(id)`

CHECK names: `grading_publications_ordinal_check`, `versioned_audit_sampling`.

Triggers: `aa_protect_held_record` → `protect_held_grading_publication` (O); `bound_grading_publication` → `grading_publication_guard` (O); `record_grading_publication` → `record_grading_publication` (O).

### `grading_review_counters`

Assessment group: Shared controls.

Columns: `band_id: uuid`, `completed_audits: int8`.

Foreign keys:

- `grading_review_counters_band_id_fkey`: `FOREIGN KEY (band_id) REFERENCES grading_bands(id)`

CHECK names: `grading_review_counters_completed_audits_check`.

Triggers: `protect_grading_review_counter` → `grading_review_counter_guard` (O).

### `hint_uses`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `learner_id: uuid`, `session_item_id: uuid`, `level: int4`, `phase: text`, `created_at: timestamptz`.

Foreign keys:

- `hint_uses_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`
- `hint_uses_session_item_id_fkey`: `FOREIGN KEY (session_item_id) REFERENCES session_items(id)`

CHECK names: `hint_uses_level_check`, `hint_uses_phase_check`.

Triggers: `immutable_hint_use` → `assessment_immutable` (O); `valid_hint_use` → `hint_use_guard` (O).

### `identity_outbox_events`

Assessment group: Identity events.

Columns: `id: uuid`, `user_id: uuid`, `type: text`, `version: int4`, `payload: json`, `created_at: timestamptz`.

Foreign keys:

- `identity_outbox_events_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: none.

Triggers: none.

### `identity_rate_buckets`

Assessment group: Shared transient keys.

Columns: `key: varchar`, `count: int4`, `expires_at: timestamptz`.

Foreign keys: none.

CHECK names: none.

Triggers: none.

### `inbound_messages`

Assessment group: Channel state and delivery.

Columns: `id: uuid`, `message_hash: text`, `request_hash: text`, `request_id: uuid`, `sender_hash: text`, `sender_encrypted?: text`, `actor_id?: uuid`, `command: text`, `code_hash?: text`, `status_reference?: text`, `delivery_status?: text`, `provider_at: timestamptz`, `received_at: timestamptz`, `available_at: timestamptz`, `processed_at?: timestamptz`, `status: text`, `attempts: int4`, `error_code?: text`, `reply_reference?: text`, `reply_encrypted?: text`.

Foreign keys:

- `inbound_messages_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`

CHECK names: `inbound_messages_attempts_check`, `inbound_messages_available_at_check`, `inbound_messages_check`, `inbound_messages_command_check`, `inbound_messages_provider_at_check`, `inbound_messages_received_at_check`, `inbound_messages_status_check`, `transient_reply`.

Triggers: `aa_protect_channel_receipt_hold` → `protect_channel_receipt_hold` (O).

### `item_mappings`

Assessment group: Shared academic/staff provenance.

Columns: `item_version_id: uuid`, `competency_id: uuid`, `weight: float8`.

Foreign keys:

- `item_mappings_competency_id_fkey`: `FOREIGN KEY (competency_id) REFERENCES competencies(id)`
- `item_mappings_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`

CHECK names: `item_mappings_weight_check`.

Triggers: `protect_mapping` → `guard_item_mapping` (O).

### `item_versions`

Assessment group: Shared academic/staff provenance.

Columns: `id: uuid`, `item_id: uuid`, `version: int4`, `revision: int4`, `review_round: int4`, `status: varchar`, `author_id: uuid`, `topic_id?: uuid`, `concept_id?: uuid`, `document: json`, `content_hash: varchar`, `requires_second_review: bool`, `synthetic: bool`, `created_at: timestamptz`, `updated_at: timestamptz`.

Foreign keys:

- `item_versions_author_id_fkey`: `FOREIGN KEY (author_id) REFERENCES users(id)`
- `item_versions_concept_id_fkey`: `FOREIGN KEY (concept_id) REFERENCES concepts(id)`
- `item_versions_item_id_fkey`: `FOREIGN KEY (item_id) REFERENCES items(id)`
- `item_versions_topic_id_fkey`: `FOREIGN KEY (topic_id) REFERENCES topics(id)`

CHECK names: `item_versions_check`, `item_versions_status_check`.

Triggers: `protect_version` → `guard_item_version` (O); `verify_review_rubric` → `review_rubric_guard` (O).

### `items`

Assessment group: Shared academic/staff provenance.

Columns: `id: uuid`, `subject_id: uuid`, `author_id: uuid`, `created_at: timestamptz`.

Foreign keys:

- `items_author_id_fkey`: `FOREIGN KEY (author_id) REFERENCES users(id)`
- `items_subject_id_fkey`: `FOREIGN KEY (subject_id) REFERENCES subjects(id)`

CHECK names: none.

Triggers: `immutable_history` → `reject_content_history_mutation` (O).

### `learner_profiles`

Assessment group: Direct identity/profile.

Columns: `user_id: uuid`, `level_id: uuid`.

Foreign keys:

- `learner_profiles_level_id_fkey`: `FOREIGN KEY (level_id) REFERENCES levels(id)`
- `learner_profiles_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: none.

Triggers: none.

### `learner_subjects`

Assessment group: Direct identity/profile.

Columns: `user_id: uuid`, `subject_id: uuid`.

Foreign keys:

- `learner_subjects_subject_id_fkey`: `FOREIGN KEY (subject_id) REFERENCES subjects(id)`
- `learner_subjects_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES learner_profiles(user_id)`

CHECK names: none.

Triggers: none.

### `legal_hold_receipts`

Assessment group: Accountability.

Columns: `actor_id: uuid`, `key: uuid`, `request_hash: text`, `hold_id: uuid`.

Foreign keys:

- `legal_hold_receipts_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `legal_hold_receipts_hold_id_fkey`: `FOREIGN KEY (hold_id) REFERENCES legal_holds(id)`

CHECK names: none.

Triggers: `immutable_hold_receipt` → `assessment_immutable` (O).

### `legal_holds`

Assessment group: Accountability.

Columns: `id: uuid`, `request_id: uuid`, `record_type: text`, `record_id: uuid`, `decision_reference: uuid`, `reason: text`, `created_by: uuid`, `created_at: timestamptz`, `expires_at: timestamptz`, `released_at?: timestamptz`, `released_by?: uuid`, `release_reference?: uuid`.

Foreign keys:

- `legal_holds_created_by_fkey`: `FOREIGN KEY (created_by) REFERENCES users(id)`
- `legal_holds_released_by_fkey`: `FOREIGN KEY (released_by) REFERENCES users(id)`
- `legal_holds_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES data_subject_requests(id)`

CHECK names: `legal_holds_check`, `legal_holds_check1`, `legal_holds_reason_check`, `legal_holds_record_type_check`.

Triggers: `protect_legal_hold` → `legal_hold_guard` (O).

### `levels`

Assessment group: Shared controls.

Columns: `id: uuid`, `name: varchar`.

Foreign keys: none.

CHECK names: none.

Triggers: none.

### `link_codes`

Assessment group: Authentication capabilities.

Columns: `id: uuid`, `user_id: uuid`, `key: uuid`, `code_hash?: text`, `created_at: timestamptz`, `expires_at: timestamptz`, `consumed_at?: timestamptz`, `revoked_at?: timestamptz`.

Foreign keys:

- `link_codes_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `link_codes_check`, `link_codes_check1`, `link_codes_check2`, `link_codes_check3`.

Triggers: `link_code_guard` → `protect_link_code` (O).

### `mastery_estimate_history`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `evidence_id: uuid`, `snapshot: json`.

Foreign keys:

- `mastery_estimate_history_evidence_id_fkey`: `FOREIGN KEY (evidence_id) REFERENCES mastery_evidence(id)`

CHECK names: none.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `immutable_mastery_history` → `assessment_immutable` (O).

### `mastery_estimates`

Assessment group: Owned learning and grading.

Columns: `learner_id: uuid`, `concept_id: uuid`, `competency_id: uuid`, `snapshot: json`.

Foreign keys:

- `mastery_estimates_competency_id_fkey`: `FOREIGN KEY (competency_id) REFERENCES competencies(id)`
- `mastery_estimates_concept_id_fkey`: `FOREIGN KEY (concept_id) REFERENCES concepts(id)`
- `mastery_estimates_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`

CHECK names: `mastery_estimates_snapshot_check`, `mastery_estimates_snapshot_check1`.

Triggers: none.

### `mastery_evidence`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `learner_id: uuid`, `attempt_id: uuid`, `concept_id: uuid`, `competency_id: uuid`, `occurred_at: timestamptz`, `snapshot: json`.

Foreign keys:

- `mastery_evidence_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES grades(attempt_id)`
- `mastery_evidence_competency_id_fkey`: `FOREIGN KEY (competency_id) REFERENCES competencies(id)`
- `mastery_evidence_concept_id_fkey`: `FOREIGN KEY (concept_id) REFERENCES concepts(id)`
- `mastery_evidence_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`

CHECK names: `mastery_evidence_snapshot_check`, `mastery_evidence_snapshot_check1`.

Triggers: `aa_protect_held_record` → `protect_held_record` (O); `bound_evidence_hints` → `evidence_hint_guard` (O); `bound_mastery` → `mastery_evidence_guard` (O); `immutable_mastery` → `assessment_immutable` (O).

### `otp_challenges`

Assessment group: Authentication capabilities.

Columns: `id: uuid`, `purpose: varchar`, `user_id?: uuid`, `policy_version: text`, `type: varchar`, `lookup_hash: varchar`, `encrypted_identifier: text`, `code_hash: varchar`, `attempts: int4`, `expires_at: timestamptz`, `consumed_at?: timestamptz`.

Foreign keys:

- `otp_challenges_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `otp_challenges_attempts_check`, `otp_challenges_purpose_check`.

Triggers: none.

### `outbound_messages`

Assessment group: Channel state and delivery.

Columns: `id: uuid`, `inbound_id: uuid`, `link_id?: uuid`, `actor_id?: uuid`, `recipient_hash: text`, `recipient_encrypted?: text`, `template: text`, `status: text`, `provider_id?: text`, `attempts: int4`, `error_code?: text`, `created_at: timestamptz`, `available_at: timestamptz`, `sent_at?: timestamptz`, `status_at?: timestamptz`, `link_revision?: int4`, `session_item_id?: uuid`, `attempt_id?: uuid`, `menu_topic_ids?: json`.

Foreign keys:

- `outbound_messages_actor_id_fkey`: `FOREIGN KEY (actor_id) REFERENCES users(id)`
- `outbound_messages_attempt_id_fkey`: `FOREIGN KEY (attempt_id) REFERENCES attempts(id)`
- `outbound_messages_inbound_id_fkey`: `FOREIGN KEY (inbound_id) REFERENCES inbound_messages(id)`
- `outbound_messages_link_id_fkey`: `FOREIGN KEY (link_id) REFERENCES channel_links(id)`
- `outbound_messages_session_item_id_fkey`: `FOREIGN KEY (session_item_id) REFERENCES session_items(id)`

CHECK names: `bound_practice_reply`, `outbound_messages_attempts_check`, `outbound_messages_available_at_check`, `outbound_messages_check`, `outbound_messages_check1`, `outbound_messages_created_at_check`, `outbound_messages_status_at_check`, `outbound_messages_status_check`, `outbound_messages_template_check`, `practice_reply_shape`.

Triggers: `aa_protect_channel_receipt_hold` → `protect_channel_receipt_hold` (O).

### `personal_export_generations`

Assessment group: Export artifacts.

Columns: `id: uuid`, `request_id: uuid`, `created_at: timestamptz`, `lease_until: timestamptz`, `published_at?: timestamptz`, `expires_at?: timestamptz`, `encrypted_manifest?: text`, `digest?: text`, `size?: int4`.

Foreign keys:

- `personal_export_generations_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES personal_export_jobs(request_id)`

CHECK names: `personal_export_generations_check`, `personal_export_generations_check1`, `personal_export_generations_check2`, `personal_export_generations_check3`, `personal_export_generations_check4`, `personal_export_generations_check5`, `personal_export_generations_digest_check`, `personal_export_generations_size_check`.

Triggers: `private_export_completion` → `personal_export_requires_completion` (O); `protect_personal_export_generation` → `personal_export_generation_guard` (O).

### `personal_export_jobs`

Assessment group: Accountability.

Columns: `request_id: uuid`, `status: text`, `correlation_id: uuid`, `created_at: timestamptz`, `queued_at: timestamptz`, `updated_at: timestamptz`, `finished_at?: timestamptz`, `next_attempt_at?: timestamptz`, `attempts: int4`, `failure?: text`, `grant_family?: uuid`, `grant_authenticated_at?: timestamptz`, `generation_id?: uuid`.

Foreign keys:

- `export_job_current_generation`: `FOREIGN KEY (request_id, generation_id) REFERENCES personal_export_generations(request_id, id) DEFERRABLE INITIALLY DEFERRED`
- `personal_export_jobs_request_id_fkey`: `FOREIGN KEY (request_id) REFERENCES data_subject_requests(id)`

CHECK names: `personal_export_jobs_attempts_check`, `personal_export_jobs_check`, `personal_export_jobs_check1`, `personal_export_jobs_check2`, `personal_export_jobs_check3`, `personal_export_jobs_check4`, `personal_export_jobs_check5`, `personal_export_jobs_check6`, `personal_export_jobs_check7`, `personal_export_jobs_check8`, `personal_export_jobs_check9`, `personal_export_jobs_failure_check`, `personal_export_jobs_status_check`.

Triggers: `aa_protect_export_evidence_hold` → `protect_export_evidence_hold` (O); `private_export_ready` → `personal_export_ready_guard` (O); `protect_personal_export_job` → `personal_export_job_guard` (O).

### `reassessments`

Assessment group: Owned learning and grading.

Columns: `original_attempt_id: uuid`, `session_id: uuid`, `item_version_id: uuid`, `basis: text`, `elapsed_seconds: float8`, `snapshot: json`, `input_hash: text`.

Foreign keys:

- `reassessments_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`
- `reassessments_original_attempt_id_fkey`: `FOREIGN KEY (original_attempt_id) REFERENCES attempts(id)`
- `reassessments_session_id_fkey`: `FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)`

CHECK names: `reassessments_basis_check`, `reassessments_elapsed_seconds_check`.

Triggers: `bound_reassessment` → `reassessment_guard` (O); `immutable_reassessment` → `assessment_immutable` (O).

### `recommendation_snapshots`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `learner_id: uuid`, `subject_id: uuid`, `input_hash: text`, `snapshot: json`.

Foreign keys:

- `recommendation_snapshots_learner_id_fkey`: `FOREIGN KEY (learner_id) REFERENCES users(id)`
- `recommendation_snapshots_subject_id_fkey`: `FOREIGN KEY (subject_id) REFERENCES subjects(id)`

CHECK names: `recommendation_snapshots_check`.

Triggers: `recommendation_snapshots_immutable` → `assessment_immutable` (O).

### `rubric_criteria`

Assessment group: Shared academic/staff provenance.

Columns: `rubric_id: uuid`, `criterion_id: text`, `position: int4`, `maximum_points: int4`, `criterion_text: text`, `acceptable_evidence: jsonb`, `common_errors: jsonb`, `prohibited_inferences: jsonb`.

Foreign keys:

- `rubric_criteria_rubric_id_fkey`: `FOREIGN KEY (rubric_id) REFERENCES rubrics(id)`

CHECK names: `rubric_criteria_acceptable_evidence_check`, `rubric_criteria_common_errors_check`, `rubric_criteria_criterion_id_check`, `rubric_criteria_criterion_text_check`, `rubric_criteria_maximum_points_check`, `rubric_criteria_position_check`, `rubric_criteria_prohibited_inferences_check`.

Triggers: `protect_rubric_criterion` → `draft_rubric_guard` (O).

### `rubrics`

Assessment group: Shared academic/staff provenance.

Columns: `id: uuid`, `maximum_points: int4`.

Foreign keys:

- `rubrics_id_fkey`: `FOREIGN KEY (id) REFERENCES item_versions(id)`

CHECK names: `rubrics_maximum_points_check`.

Triggers: `protect_rubric` → `draft_rubric_guard` (O).

### `session_items`

Assessment group: Owned learning and grading.

Columns: `id: uuid`, `session_id: uuid`, `item_version_id: uuid`, `position: int4`, `reason: text`, `served_at?: timestamptz`, `grading_band_id?: uuid`.

Foreign keys:

- `session_items_grading_band_id_fkey`: `FOREIGN KEY (grading_band_id) REFERENCES grading_bands(id)`
- `session_items_item_version_id_fkey`: `FOREIGN KEY (item_version_id) REFERENCES item_versions(id)`
- `session_items_session_id_fkey`: `FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)`

CHECK names: `bounded_position`.

Triggers: `aa_reject_disabled_short_text` → `reject_disabled_short_text` (O); `fixed_assignment` → `assessment_assignment_guard` (O); `reassessment_item_count` → `reassessment_assignment_guard` (O).

### `subjects`

Assessment group: Shared controls.

Columns: `id: uuid`, `level_id: uuid`, `name: varchar`.

Foreign keys:

- `subjects_level_id_fkey`: `FOREIGN KEY (level_id) REFERENCES levels(id)`

CHECK names: none.

Triggers: none.

### `topics`

Assessment group: Shared controls.

Columns: `id: uuid`, `subject_id: uuid`, `name: varchar`.

Foreign keys:

- `topics_subject_id_fkey`: `FOREIGN KEY (subject_id) REFERENCES subjects(id)`

CHECK names: none.

Triggers: none.

### `user_identifiers`

Assessment group: Direct identity/profile.

Columns: `id: uuid`, `user_id: uuid`, `type: varchar`, `normalized_value_encrypted: text`, `lookup_hash: varchar`, `verified_at: timestamptz`.

Foreign keys:

- `user_identifiers_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `user_identifiers_type_check`.

Triggers: none.

### `user_roles`

Assessment group: Shared academic/staff provenance.

Columns: `user_id: uuid`, `role: varchar`, `granted_at: timestamptz`.

Foreign keys:

- `user_roles_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES users(id)`

CHECK names: `user_roles_role_check`.

Triggers: none.

### `users`

Assessment group: Identity anchor.

Columns: `id: uuid`, `status: varchar`, `display_name?: text`, `birth_date?: date`, `created_at: timestamptz`.

Foreign keys: none.

CHECK names: `users_status_check`.

Triggers: none.

## Required execution design and acceptance

Use this inventory with the [readiness assessment](E8_ERASURE_TRANSFORM_READINESS.md)
and accepted ADRs. It is not sufficient to generate deletion SQL by reversing FKs:
retention, exact preservation, current authorization, worker barriers and shared
academic state all require independent rules. Any new schema source or embedded
payload version must be assessed before execution is enabled for it.

The execution proposal must identify per-column retained/removed/transformed values,
exact ownership, original-record or approved snapshot preservation, retention anchor,
required ancestors, removal ordering and post-completion custody. It must include
restricted-login denials, hold/delete and worker races, crash/replay/rollback,
large-history progress, clean/additive migration and populated logical recovery tests.
The restore plan must prevent erased data being silently served again from a backup;
this catalog inventory proves neither backup deletion nor production recovery.

No account erasure, new snapshots, anonymization, migration or legal policy is approved
by publishing this assessment. Full MVP privacy fulfillment remains incomplete.

## Documentation verification

`make check-docs` passes with 173 Markdown files and 61 requirement IDs checked;
`make lint` passes, including formatting, Python/TypeScript types and generated-source
format checks. The catalog equality assertion passes for all table metadata described
above. No application, migration, API, provider or architecture changes are made.
Application acceptance remains tied to its separately recorded exact source/CI evidence.

## Additive0043 candidate catalog assessment — ADR-067

A read-only catalog inspection of an isolated actual0043 integration schema on19 October
finds71 tables,501 columns,121 foreign keys and102 non-internal triggers. The13 new
columns, one FK and five triggers below are additive; the public review DB is still0042
at this observation. This is not erasure authority or a new approved manifest. Two broad
catalog-count attempts hit the existing statement timeout while tests ran; indexed
per-relation catalog inspection succeeds without increasing timeouts or removing schemas.
No learner rows or credentials are read by the inventory query.

### operations_configuration_versions

Group: Shared controls. PK id. All columns non-null:
id uuid, revision integer, thresholds jsonb, version_ref text, previous_ref text,
command_hash text, changed_key text, reason text, created_at timestamptz.
No FK or actor/contact/answer/free-text field. command_hash is a hash of the closed
numeric command, not a raw retry key. Staff linkage exists in the existing AuditLog only.

CHECK names: operations_configuration_versions_revision_check,
operations_configuration_versions_thresholds_check,
operations_configuration_versions_version_ref_check,
operations_configuration_versions_previous_ref_check,
operations_configuration_versions_command_hash_check,
operations_configuration_versions_reason_check. Unique revision/version_ref and id PK.
Triggers: operations_configuration_versions_immutable and
operations_configuration_versions_no_truncate → operations_configuration_version_guard;
operations_configuration_atomic → operations_configuration_commit_guard (deferred).
Inspect0043 for full closed15-key bounds, atomic staff-audit/pointer and immutable behavior.

### operations_configuration_state

Group: Shared controls. PK id. Columns: id integer, nonce uuid, revision integer
(all non-null), current_id nullable uuid. FK operations_configuration_state_current_id_fkey
references operations_configuration_versions(id). nonce unique. CHECK names:
operations_configuration_state_id_check, operations_configuration_state_revision_check,
operations_configuration_state_check. Triggers: operations_configuration_pointer_monotonic
and operations_configuration_state_no_truncate → operations_configuration_pointer_guard.
The immutable random namespace is shared configuration provenance, not a learner identity.
Neither row grants subject ownership or deletion of administrative audit evidence.

0044 forward repair changes only operations_configuration_version_guard, not these
71-table/501-column/121-FK/102-trigger catalog counts. The normal synthetic preview is
subsequently migrated through0044; no erasure or retention authority follows.

## Dormant lifecycle0045 implementation inventory

The structural manifest advances to0045:74 tables and545 columns. Existing69 historical
sections and the0043/0044 addendum remain factual prior-source evidence. New fields in
physical SQL order are listed below. No privileged execution, ownership/preservation
clearance or release acceptance is inferred from this inventory.

- users appends `closed_at?: timestamptz`; all pre-existing values remain null.
- account_erasure_state: `singleton: int4`, `original_scope_eligible: bool`,
  `database_oid: int8`, `namespace_oid: int8`, `owner_oid?: int8`, `executor_oid?: int8`,
  `scope_nonce: uuid`, `creation_enabled: bool`, `execution_enabled: bool`,
  `policy: varchar`, `manifest: varchar`, `installed_at: timestamptz`.
- account_erasure_plans: `id: uuid`, `request_id: uuid`, `scope_nonce: uuid`,
  `policy: varchar`, `manifest: varchar`, `inventory_hash: varchar`, `version?: varchar`,
  `observed_at: timestamptz`, `expires_at: timestamptz`.
- account_erasure_jobs: `request_id: uuid`, `subject_id: uuid`, `authorized_by: uuid`,
  `decision_reference: uuid`, `authorized_at: timestamptz`, `authenticated_at: timestamptz`,
  `policy: varchar`, `manifest: varchar`, `plan_id: uuid`, `plan_version: varchar`,
  `command_key: uuid`, `command_hash: varchar`, `phase: varchar`, `blocker?: varchar`,
  `failure?: varchar`, `closed_at?: timestamptz`, `completed_at?: timestamptz`,
  `examined: int8`, `removed: int8`, `batches: int8`, `private_cursor?: json`,
  `correlation_id: uuid`.

No new role, executor/login membership, plaintext body, source-ID ledger or payload
reading endpoint is added. Source shape is a drift fence, not constraint/ACL/hold proof.


## ADR-071 private disabled capability installation inventory

The ordinary0045 public baseline stays74 tables/545 columns. The explicit fresh-source
installer adds one capability-specific private table with16 columns, making75/561
across application and installed control namespaces. No normal migration/startup creates
that namespace. This is K/shared control metadata, not a learner/source-reference map.
An executor must validate the additional namespace/functions/ACLs and pgcrypto bindings
independently; the ordinary public shape check alone cannot authorize closure.

The private control primary key is singleton. Exact columns are singleton integer;
database_oid, namespace_oid, cap_namespace_oid, crypto_namespace_oid, crypto_hmac_oid,
owner_oid, authorizer_oid, executor_oid (oid); source_nonce and installation_nonce (uuid);
version (text); fingerprint_key (bytea,32 bytes); creation_enabled and execution_enabled
(boolean, false); installed_at (timestamptz, actual database clock). All are non-null.
The key is private cryptographic material, never an API/status/log/export field. Public
and both login roles have no control-table rights. Installed function/role identity and
all activation controls remain separate gates; no borrower may treat these totals as
preservation, ownership, erasure or production clearance.
