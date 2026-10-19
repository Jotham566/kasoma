# Week 8 provider recovery decision evidence

Reviewed:19 October2026. Requirements: NFR-REL-001/002, NFR-SEC-001/002,
NFR-PERF-001/002, NFR-MNT-001; production-pilot specification section8 and local
portability specification section7. Status: public-documentation research only.
No provider, region, budget, processor or production configuration is approved here.
No authenticated cloud-management/application API, resource provisioning, model,
messaging or email operation is performed.

## Binding requirement and present evidence

The approved [production decisions](../specifications/16_Production_Pilot_Decisions.md)
require35-day PostgreSQL PITR, an encrypted approved secondary-region recovery copy,
RPO≤24 hours/RTO≤8 hours and a pre-beta restore rehearsal. Web/API, PostgreSQL, Redis
and object storage should share the approved primary region. Data transfers and
processor/notice review remain explicit release gates. [Portability policy](../specifications/17_Local_Development_and_Provider_Portability.md)
keeps ordinary local/automated execution on fakes/local services until that decision.

ADR-042/065 supply logical/private-object synthetic preparation. They do not prove a
managed PITR window, regional copy, escrow, deletion/expiry after restore or production
recovery. A documented vendor capability or SLA does not prove Kasoma's recovery time.
The [release register](RELEASE_GATES.md) remains open; research is not an exception.

## Candidate recovery options and material constraints

| Candidate for evaluation, not selection | Verified documentation | Consequence for Kasoma's future configuration |
| --- | --- | --- |
| AWS RDS for PostgreSQL; Cape Town primary candidate | DB-instance retention permits0–35 days; API/CLI creation defaults to1 day, console7. Cross-region automated replication supports Multi-AZ DB instances, not Multi-AZ DB clusters; Cape Town's listed destinations are Frankfurt, Ireland and London. | Set35 explicitly; select the exact HA deployment type and an approved recovery country. Do not assume an African primary keeps its recovery copy in Africa. |
| Azure Database for PostgreSQL; South Africa North candidate | Retention defaults to7 and supports35 days. Geo-redundant backup is a creation-time choice. The service table lists South Africa North with zone HA/geo-backup; its paired South Africa West region has restricted access. | Include the geo-backup choice before creation, verify subscription access/capacity and price the matching HA tier. A regional pairing is not evidence of granted access or application recovery. |
| Google Cloud SQL for PostgreSQL Enterprise Plus; Johannesburg candidate | Enterprise Plus supports up to35-day PITR logs; Enterprise supports up to7. The region matrix lists Enterprise Plus in africa-south1. Backup-location and transaction-log retention are separate settings. | Enterprise's7-day log ceiling does not meet the unchanged35-day requirement. Evaluate Plus and the chosen recovery location/policy; retaining35 snapshots is not proof of35-day PITR. |

Primary sources, opened/checked on the review date:

- AWS [retention settings/defaults](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html)
  and [cross-region replication modes/destination matrix](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReplicateBackups.html).
- Azure [backup retention/creation-time geo-backup](https://learn.microsoft.com/en-us/azure/postgresql/backup-restore/concepts-backup-restore),
  [service/region table](https://learn.microsoft.com/en-us/azure/postgresql/overview),
  [HA tier requirements](https://learn.microsoft.com/en-us/azure/reliability/reliability-postgresql-flexible-server)
  and [paired/restricted regions](https://learn.microsoft.com/en-us/azure/reliability/regions-paired).
- Google [edition comparison](https://docs.cloud.google.com/sql/docs/postgres/editions-intro),
  [region/machine-series table](https://docs.cloud.google.com/sql/docs/postgres/region-availability-overview),
  [backup-location/log-retention options](https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/backup-options)
  and [PITR restore overview](https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/restore).

The table's final column is an engineering inference from vendor capabilities and the
binding Kasoma requirements, not a vendor recommendation or legal determination.
Recheck exact service/version/region/capacity at the actual decision; research cannot
reserve capacity. Azure HA requires General Purpose or Memory Optimized, so a cheap
Burstable quotation cannot be treated as the same HA configuration. Google documents
daily log purging and backup-count interactions that can shorten the effective window;
the chosen policy must demonstrate the complete window while honoring approved expiry.
Do not silently extend retention or reduce35 days to make a cheaper plan pass.

## Inputs still missing before a comparable quote or decision

| Required input/evidence | Current state / why it matters |
| --- | --- |
| Accountable technical/product/privacy owners and decision date | Not recorded; do not infer sign-off or the current sprint week from a repository date. |
| Monthly pilot cap, currency, tax/support assumptions and contingency | Not supplied; no numerical total, cheapest-provider claim, paid account or resource allocation is invented. |
| Approved primary and recovery countries, contractual safeguards and notices | Not supplied; region names alone are not transfer approval. |
| Exact PostgreSQL16/pgvector version, privileges, extensions and connection behavior | Region-specific managed compatibility has not been executed; do not silently downgrade the pinned local stack. |
| HA SKU/capacity, compute, Redis queue behavior and private networking | Unverified for a selected full stack; a database region is not proof that every component is available there. |
| Private object storage, recovery copies, lifecycle expiry and key custody | Must restore the encrypted export with the correct database/search-path namespace and original required keys, without public URLs. |
| Worker/API/web capacity and actual Uganda latency | Native finite synthetic load is not a cloud SKU sizing result or a monthly availability measurement. |
| Model, SMS/email/WhatsApp adapters, regions, limits and vendor terms | Unselected; include failure handling, minimum commitments and approved pseudonymous alternate-region model paths. Academic calibration remains separate. |
| Production restore and delete/expiry reconciliation | Must verify restricted logins, immutable guards, retention/holds and erasure-related obligations after restore. ADR-061 remains unapproved; no erasure execution is granted by a backup plan. |

Compare like-for-like compute/HA, database storage/IO,35-day backup/WAL and secondary
copy, Redis, object storage/requests/egress, networking, key/secret services, monitoring,
provider usage and support. Do not extrapolate a monthly bill from a125-second local
fixture, assume500 daily active means500 daily OTPs, or substitute free-tier quotas for
an approved spend cap. Exact quotes need the missing workload/owner inputs above.

## Reviewable next decision and acceptance sequence

The decision record must name one approved provider, primary/recovery regions, precise
service/HA/backup configuration, version compatibility, owners, costed workload/cap and
processor/transfer review references. It must explain remaining unsupported capabilities
and cannot waive an existing security/recovery gate. No winner is established by this
research. An architectural change belongs in its own approved ADR before implementation.

After authorization, implement the selected production profile/adapters with typed
server-only secrets and fake automated provider tests. Then execute explicitly bounded
pre-production checks: query the actual approved extension/version/ACL configuration;
restore to a fresh isolated target with source unavailable; recover matching encrypted
objects and required keys without changing storage scope; verify original restricted
logins/holds/expiry/disabled features; measure the agreed RPO/RTO and Uganda latency;
record actual spend, alarms, restore/rollback and owner sign-offs. No commands or cloud
calls from that future sequence are executed by this document.

## Verification boundary

This is documentation-only: verify local links and whitespace. The public primary
sources above were inspected; no vendor page is an approval instruction. No application,
API/generated contract, schema, dependency, cloud SDK, secret or production flag changes.
No application/production acceptance is claimed from these documentation checks.
