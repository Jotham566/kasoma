# ADR-046: Shared locks for immutable assessment content

Date: 9 October 2026
Status: Accepted within delegated MVP engineering discretion; runtime verification pending
Requirements: NFR-PERF-001/002, FR-REV-002/003, FR-CNT-004, FR-WA-003

## Evidence and decision

The first isolated 50-concurrent objective HTTP profile completed 500 sessions and 2,500 grades
without errors, but session creation p95 was 652.530 ms. Its mixed API p95 of 30.115 ms masked that
slow operation. Gate each measured non-AI operation against the unchanged 500 ms target, not only
the mixed aggregate. This preliminary result is not performance acceptance.

Assessment currently takes exclusive row locks while reading immutable approved versions. This
serializes independent learners selecting the same questions. Use PostgreSQL FOR SHARE when
refreshing content for assessment and locked candidate selection. Concurrent assessment readers
can coexist; approval/retirement/other content writes must still wait for those transactions.
Do not use FOR KEY SHARE: retirement changes a non-key status and must conflict with the read.
Continue refreshing and checking approval after lock acquisition, retain existing author/reviewer
separation and immutable version guards, and leave administrative writes exclusive.

Manual topic practice also enumerates all subject topics before discarding unrelated candidates.
Allow the existing candidate service to restrict its topic query and eligible candidate count to
the manual request. Preserve
the same eligibility, ordering, exclusions, repetition/channel rules and final content recheck.
Revalidate and lock the selected revision plan in one bounded query (at most 15 distinct version
IDs), locking only item_versions with FOR SHARE and returning the original selector order. Missing,
foreign, retired, non-synthetic or short-text versions fail the whole plan. Populate current ORM
state rather than trusting a previously cached candidate. Both manual and recommended starts use
this content-owned boundary; individual serving/submission rechecks remain unchanged.
Diagnostics/recommendations retain their existing full-subject selection. No grading, mastery,
authentication, transaction ownership, version provenance or learner contract changes.

## Verification and rollback

Test two independent readers sharing a version, a writer blocked while readers are active, and
an assessment reader rejecting retirement committed between eligibility read and locked refresh. Exercise the
candidate topic filter against the unchanged full-subject result and verify existing selection,
diagnostic/channel parity, repeat protection and rollback suites. Re-run the objective profile
and full repository checks. No pool/statement/client application limit is increased.

This changes lock policy under the shared transaction boundary in ADR-035; it introduces no schema,
provider, production entitlement or academic enablement. Rollback can restore exclusive reads at
the cost of concurrency; immutable records and existing API behavior remain compatible.
