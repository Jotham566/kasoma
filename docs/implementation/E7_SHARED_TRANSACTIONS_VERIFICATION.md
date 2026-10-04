# E7 shared assessment and channel foundation verification

Status: published and verified through `c0b5b55`; conversation delivery is separate.
Requirements: FR-WA-002/003/004/005, FR-ID-003, FR-REV-001/002, FR-CNT-004,
FR-GRD-001/002, FR-MST-001.
Decisions: [ADR-035](../decisions/ADR/035-shared-assessment-transactions.md),
[ADR-036](../decisions/ADR/036-whatsapp-objective-message-format.md),
[ADR-037](../decisions/ADR/037-channel-assessment-provenance.md).

## Hosted acceptance

| Commit | CI | Passing tests |
| --- | --- | --- |
| `50044d4` shared transactions | [37149982356](https://github.com/Jotham566/kasoma/actions/runs/37149982356) | 257 unit/contract + 141 integration = 398 Python; 20 browser; five tooling |
| `dd1c8d8` objective formatting | [37217488323](https://github.com/Jotham566/kasoma/actions/runs/37217488323) | 290 unit/contract + 141 integration = 431 Python; 20 browser; five tooling |
| `c0b5b55` channel provenance | [37217857047](https://github.com/Jotham566/kasoma/actions/runs/37217857047) | 290 unit/contract + 147 integration = 437 Python; 20 browser; five tooling |

Every run passed setup, clean migrations/seed, lint/types/contracts/build, dependency/source/image
security gates and container smoke. All three commits are on main; completed branches were removed.
Public OpenAPI/TypeScript contracts are unchanged. Migration 0019 adds channel evidence guards.

## Verified behavior

Transaction-scoped start/serve/submit operations reuse existing graders, canonical web receipts,
mastery and outbox logic. Internal actor authorization locks/reloads current account state and
checks consent, S4 level and subject enrollment. Rollback removes session/assignment/attempt/grade/
receipt/mastery/events together; unknown/inactive/foreign actors receive no bypass.

Objective questions require explicit WHATSAPP suitability, plain supported representation and
complete-message bounds. Numbered choice/multiple-choice and numeric replies normalize into the
existing contracts without a second grader. Numeric representation preserves significant figures.

Internal WHATSAPP operations accept exactly five-item topic revision, filter capability before
selection, preserve assignments on supported web continuation, and recheck current approval.
Channel receipts use their own namespace; public clients cannot spoof WHATSAPP provenance.
Six real-database cases prove three-format grade/mastery evidence parity, retry identity, current
approval, unsupported plans, web continuation and immutable database channel guards.
Use `make test-assessment-transactions` and `make test-channel-assessment` for focused checks.

## Native limitations and follow-up

Local formatting, lint, type, unit and security checks passed. Docker subsequently became unavailable
without a running engine socket; focused channel tests produced six database fixture setup errors,
and migration/setup could not connect. Those are failed native attempts, not passing evidence.
Hosted checks above independently verified the exact source and clean schema. No volumes were reset.
A transient dependency-audit connection reset passed on retry without dependency changes.

The subsequent concise-feedback formatter, stable content lock order and signed conversation
integration are tracked in [conversation verification](E7_CONVERSATION_VERIFICATION.md). No full
WhatsApp, latency, academic or production acceptance is inferred from these foundation results.
