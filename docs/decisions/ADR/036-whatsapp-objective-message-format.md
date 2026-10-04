# ADR-036: Bounded objective question and reply format

Date: 3 October 2026
Status: Accepted within delegated MVP implementation discretion; base implementation verified; follow-up delivery work in progress
Requirements: FR-WA-002/003/005, FR-CNT-004, FR-GRD-001/002

## Decision

WhatsApp objective practice requires an independently approved item version explicitly marked
WHATSAPP-suitable. The formatting boundary accepts only the existing supported single-choice,
multiple-choice and numeric schemas. It renders five-question positions and numbered choice
labels without exposing keys, rubrics, worked solutions or remediation before an answer.
The complete question, options and reply instructions must fit a 500-character local ceiling;
reject unsuitable items before assignment rather than truncate assessment meaning. Content
requiring image/rich rendering is excluded. This is a channel capability check, not an academic
approval or a substitute for source/version eligibility.

Choice replies use one-based displayed option numbers; multiple selection uses comma-separated
numbers. Numeric replies preserve the entered representation (including significant figures)
and use `value | unit` when a unit is required. Convert only to existing ChoiceResponse,
MultipleChoiceResponse or NumericResponse contracts. Reject missing/duplicate/unknown selections,
unsupported numeric syntax, unknown units and oversized replies. The shared grader alone
calculates scores and mastery; the formatting boundary never reads answer keys to normalize a reply.

The eventual conversation worker must bind each answer to the exact outbound question using
provider reply context before applying this parser. A bare number is not permission to grade the
current question: without an unambiguous binding, request a reply to the question instead.
Conversation persistence, menus, STOP/session handling and atomic worker integration follow as
separate implementation work. This pure boundary does not enable practice by itself.

## Post-grade feedback

Project the shared grade's awarded/possible points and concise reviewed next action only after
owned revision submission. If the complete next action is rich or does not fit, omit it and link
to the existing authenticated `/revise?session=<UUID>` page; never truncate academic instructions.
Every message includes the web link and STOP instruction, and CONTINUE until the fifth answer.
The complete message must respect the same ceiling. Only the configured local application origin
is accepted; credentials, query parameters, fragments and path prefixes are rejected to prevent
secret-bearing links. This pure formatter does not authorize delivery or expose sealed diagnostics.

## Verification

Use deterministic contract tests for complete-message limits, unsupported/rich prompts, explicit
channel suitability, keys not leaked, numbering, multiple-choice canonicalization, exact numeric
representation and malformed/oversized replies. Integration must additionally prove current
approval/consent and web/channel grade/mastery parity before enabling the practice path.
