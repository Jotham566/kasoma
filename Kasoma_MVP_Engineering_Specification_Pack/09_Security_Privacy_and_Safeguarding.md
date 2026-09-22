# Kasoma Security, Privacy and Safeguarding Specification

| Field | Value |
|---|---|
| Version | 1.1.0 |
| Data sensitivity | Contains minors' identity and learning data |
| Policy | Security and child safety override delivery convenience |

## 1. Data classification

| Class | Examples | Handling |
|---|---|---|
| Restricted | OTPs, tokens, guardian contact, direct identifiers | encrypt, strict access, never log |
| Confidential | learner answers, mastery history, consent evidence | least privilege, retention controls |
| Internal | content drafts, operations metrics, prompts | authenticated staff access |
| Public | approved public product copy | normal integrity controls |

## 2. Threat model priorities

- account takeover through OTP abuse or token theft;
- learner enumeration;
- cross-learner data access (IDOR);
- privilege escalation in content/admin tools;
- prompt injection through answers/imports;
- answer-key leakage;
- malicious/duplicate WhatsApp webhooks;
- unsafe contact with minors;
- excessive data collection or retention;
- content poisoning and unreviewed publication;
- denial-of-service/model-cost abuse;
- secrets in repositories/logs.

## 3. Required controls

### Identity

- Normalize identifiers; encrypt values and use keyed hash for lookup.
- OTP expires within 10 minutes, is single-use and has send/attempt limits.
- Generic request/recovery responses prevent enumeration.
- Rotate refresh tokens; detect reuse and revoke family.
- Require re-authentication for sensitive account/consent actions.
- Staff/admin accounts use MFA before production.

### Authorization

- Server-side deny-by-default policy.
- Object ownership checks for every learner resource.
- Separation of author and reviewer.
- Support access is read-only by default and audited.
- No admin authorization based only on UI visibility.

### Application/data

- Parameterized queries/ORM; output encoding; CSP and secure headers.
- CSRF protection where cookie credentials are used.
- Strict CORS allowlist.
- Malware/type/size validation on imports and uploads.
- Signed short-lived media URLs.
- Secrets in managed secret store.
- Dependency, container and secret scanning in CI.
- Production database access restricted and audited.

### API/provider

- Rate limits by route, account and risk signal.
- Verify WhatsApp signatures before body processing.
- Idempotency for webhooks and answer submissions.
- Provider timeouts and cost caps.
- Model tools disabled for grading.

## 4. Child safeguarding

- Interactions are educational and age-appropriate.
- No staff-to-learner private messaging outside approved support flows.
- Support interactions are logged and supervised.
- AI must not request personal contact, location, images or secrets.
- Crisis, abuse or harmful-content disclosures use an approved safe response and escalation process; the model must not improvise counselling.
- Public profiles, direct messaging between learners and public leaderboards do not exist in MVP.
- Notifications respect opt-out and reasonable hours in Africa/Kampala time.

The safeguarding lead approves escalation text, contacts and staff procedures before pilot launch.

## 5. Consent and privacy

- Treat all learners under 18 as children for the MVP.
- Require verifiable parent/guardian consent plus the learner's affirmative assent before any learning activity or WhatsApp linking; record each separately with policy version.
- Learners aged 18 or older provide their own informed consent.
- School authorization does not replace individual guardian consent and learner assent.
- Allow assent/consent withdrawal without academic penalty and stop new processing except what must be retained lawfully.
- Store policy version and lawful/approved consent basis.
- Collect only data necessary for identity, learning and operations.
- Explain automated grading and mastery estimates in plain language.
- Provide a method to flag/contest a grade.
- Do not sell learner data or use it for advertising profiles.
- Do not train external/general models on learner data by default.
- Use aggregate/de-identified metrics for product analysis whenever possible.

## 6. Approved MVP retention schedule

| Data | Baseline |
|---|---|
| OTP value | hashed; remove/expire promptly after verification window |
| Access logs | 90 days unless security incident requires hold |
| Raw provider webhook payload | minimize; ≤30 days unless dispute/incident |
| Active learner profile, answers, grades and mastery | while account is active; review after 24 months of inactivity, notify where possible, then delete direct identifiers and anonymize permitted learning evidence after a 30-day grace period |
| Consent, assent and material administrative audit evidence | six years after account closure/withdrawal, then delete unless a legal hold applies |
| Security audit logs | 12 months; longer only for an active investigation/legal hold |
| Support/content flags containing learner data | 24 months after resolution, then delete or anonymize |
| Data-subject request evidence | six years after completion, minimized to accountability evidence |
| AI debug payload | off by default; if specifically enabled for an approved incident/evaluation, redacted and deleted within 30 days |
| Operational database backups | point-in-time recovery for 35 days; expired backups are automatically deleted |
| Aggregated/de-identified metrics | may be retained while useful only after re-identification risk review |

No code shall hard-code an indefinite retention period. Scheduled deletion/anonymization jobs must be testable and observable.

Before processing real learner data, Kasoma must complete and approve:

- PDPO registration obligations for the controller/collector/processor roles that apply;
- a Data Protection Impact Assessment covering minors, adaptive profiling, AI grading and WhatsApp;
- a data-flow and processor register;
- processor/data-processing agreements;
- a cross-border transfer assessment and documented safeguards for South Africa and any AI/messaging processing region;
- privacy notice, guardian consent and learner assent wording reviewed for Uganda.

## 7. Data subject requests

- Verify requester's identity proportionately.
- Export in understandable machine-readable form.
- Deletion revokes sessions and channel links early in processing.
- Track request status without exposing internal security detail.
- Preserve only records required by approved obligations, with personal linkage minimized.

## 8. Security testing and release

Before pilot:

- threat-model review;
- automated SAST/dependency/secret/container scans;
- authorization matrix tests;
- OTP/rate-limit abuse tests;
- IDOR and answer-leakage tests;
- webhook signature/replay tests;
- prompt-injection benchmark;
- backup restore exercise;
- incident tabletop including a wrong grade and safeguarding disclosure.

Severity-1 security, privacy, safeguarding or academic-integrity defects block release.

## 9. Incident severity

- SEV-1: active child-safety risk, credential/PII exposure, cross-learner access, widespread wrong grades/mastery corruption.
- SEV-2: contained sensitive defect, significant provider outage, material content issue.
- SEV-3: limited defect with workaround and no sensitive exposure.

Runbooks must define detection, containment, evidence preservation, communication, remediation and post-incident review. Only authorized leaders communicate externally.
