# ADR-038: Bound local WhatsApp practice conversations

Date: 4 October 2026
Status: Accepted within delegated MVP implementation discretion; implementation in progress
Requirements: FR-WA-002/003/004/005/006, FR-ID-003/006, FR-CNT-004, NFR-PERF-002

## Decision

Enable only local fake transport and independently reviewed synthetic objective content. START
presents enrolled subject/topic choices when no active channel session exists; a numbered reply
explicitly selects a topic. With an active pointer, START resumes rather than replacing assignments. CONTINUE
resumes the channel's five-item revision pointer and serves the current unanswered assignment.
After an answer, send concise shared-grade feedback with the authenticated web link; CONTINUE
serves the next question. PROGRESS returns a protected web progress link until a shared concise
progress projection is verified. HELP lists the commands. No free-form tutoring is enabled.

Migration 0020 also extends the channel insert guard to honor WEB suitability on shared sessions,
closing the WA-only continuation edge without rewriting any existing evidence.

Store one expiring conversation per link, bound to its current revision, with either a finite
menu of topic UUIDs or an owned session pointer. Keep the exact outgoing menu/question UUID and
assignment reference. Menu choices and answers require provider reply context matching that
successfully sent outbound message, actor, recipient and current link revision. Bare, stale,
foreign or duplicate answers cannot select or grade another question. A repeated CONTINUE may
send the current question again; only its latest bound outgoing message can accept an answer.

Retain at most 96 characters of encrypted structured reply text while queued, and scrub on
terminal processing or 24-hour expiry. Do not retain unsolicited free-form text. Store outgoing
question/grade/menu references rather than raw assessment or answer bodies. Reconstruct text
under current account, consent, enrollment, content approval, link and STOP checks immediately
before fake delivery. Cancel stale/unauthorized/retired dynamic replies; only transient provider
failures use transport retries. Bound every rendered message, including links, to 500 characters.

Commit conversation changes, inbound status, assessment receipt, immutable attempt/grade/mastery
and outgoing reference in the same transaction using ADR-035/037 shared operations. Permanent
validation failures create a safe generic clarification; unexpected failures roll back the
savepoint and use existing bounded retries. Transport replay remains keyed by provider message ID.

STOP keeps the immediate intake barrier, cancels queued messages and removes the channel pointer.
It stops channel participation without deleting answers or abandoning a shared web session.
Unlink/relink invalidates conversation and outgoing state by link revision. A new link and explicit
START/CONTINUE are required after STOP. Conversation pointers expire after 24 hours of inactivity;
shared learning evidence retains its existing lifetime. Extend owned exports and deletion inventory
with these transient pointers; do not imply full channel legal-hold or erasure coverage.

## Delivery and acceptance gates

Durable acknowledgement precedes asynchronous processing. Add a bounded best-effort local Redis
wake-up after commit, with the existing periodic queue drain as recovery. Redis failure must never
lose an accepted message or cause a duplicate grade. Do not claim the deterministic feedback latency
SLO from functional tests; measure it separately with the normal worker and document degraded mode.

Exercise complete five-question flows, web/channel score and evidence parity, exact reply binding,
concurrent/duplicate/out-of-order events, malformed responses, current approval/consent withdrawal,
STOP before delivery, unlink/relink, expiry, rollback, rate limits and owned projections. Use only
fake providers and synthetic fixtures. Migration, browser, security and container gates remain
mandatory before promotion. Production provider/academic/privacy/pilot approval remains outstanding.
