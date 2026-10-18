# Legacy hold DELETE clock readiness

19 October 2026. FR-ID-006, BR-010, NFR-SEC-002, NFR-MNT-001.

Read ADR-030/043/045/055, the security retention schedule, data model/API constraints,
current hold migrations and the existing hold/publication/restricted-login tests. Four
legacy wrappers use transaction-start time; terminal channel guards already use wall
clock. See [ADR-056](../decisions/ADR/056-wall-clock-hold-delete-guards.md).

The smallest complete slice is a forward replacement of four trigger function bodies,
changing only the DELETE evaluation clock. Preserve the explicit historical predicate,
all source append-only guards, ownership/recent-ADMIN checks and disabled erasure.
No API/client, enum, data column, user-visible policy or source-row transform is needed.

First reproduce with actual valid owned holds and temporary probe rows under two real
transactions, covering all four ID shapes. Then verify clean/0035 upgrade, original
hold replay, original evidence guards, restricted logins, populated restore and final
security/container gates. No original row is deleted to demonstrate this boundary.
This is engineering readiness, not application acceptance or full preservation clearance.
