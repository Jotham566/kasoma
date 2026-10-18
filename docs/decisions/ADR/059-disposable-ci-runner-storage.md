# ADR-059: Disposable CI runner storage preflight

Date: 19 October 2026
Status: Accepted for disposable hosted CI profile only; no developer/application cleanup
Requirements: NFR-MNT-001; supports existing security/release verification

## Observed failure and decision

Hold-clock run 39167600610 at 978ab30 passes 918 unit/contract, 373 integration and
five 15-case browser batches, then terminates with the runner's `No space left on
device` diagnostic. That is a failed pipeline, not application acceptance. The job
has no disk snapshots sufficient to attribute consumption to a particular component.
Do not assume an application bug or hide this by relaxing tests/retrying indefinitely.

Before dependencies/builds on the existing disposable Ubuntu 24.04 X64 GitHub-hosted
job, reclaim only its preinstalled .NET and Android SDK directories. Kasoma uses
neither SDK; host Python/Node, Docker/Go image builds, browsers, checkout, caches,
application databases/volumes and runner internals must remain untouched. No local
cleanup, Docker prune, volume reset, user-supplied path or self-hosted execution.

The helper defaults to read-only JSON disk reporting. An explicit prepare mode requires
Linux/Ubuntu 24.04, CI/GitHub markers, the runner.environment context github-hosted,
X64, root, and canonical checkout/temp locations under /home/runner/work. Reject
unsafe/symlink/non-directory SDK targets before any removal. Only fixed SDK roots are
eligible; no environment-derived removal path. Preserve a minimum 24 GiB of free root
space after preparation, otherwise fail early with a closed reason. This is an initial
engineering capacity budget, not a production SLO or guaranteed peak-use estimate.

Report bounded total/used/free bytes before/after preparation and at later stages.
A separate read-only check requires 8 GiB before the browser and image-build phases,
so low capacity fails while diagnostic space remains; default reporting has no gate.
Split browser, security/image build and final smoke steps so failed phases are visible;
keep every existing check. Add always-run read-only root/Docker usage diagnostics.
No sensitive environment dump, credential, source payload or personal identifier.
No provider, database schema, product retention or learner behavior changes.

## Safety and acceptance

Test refusal on developer/self-hosted/wrong-platform/non-root/invalid-workspace profiles,
unsafe targets without partial deletion, exact allowlist removal in a synthetic temporary
filesystem, insufficient capacity and default read-only behavior. Never execute real SDK
cleanup locally. Strict lint/types/unit/source checks and complete hosted acceptance are
required; failed/cancelled historical runs remain failed/cancelled evidence. Local Docker
services stay running. Rollback removes this CI-only preparation and retains diagnostics;
if capacity is insufficient, fix the profile without reducing application acceptance.

## Sources and approval boundary

The failed run identifies image ubuntu24/20261012.334. Its official
[manifest](https://github.com/actions/runner-images/blob/ubuntu24/20261012.334/images/ubuntu/Ubuntu2404-Readme.md)
locates the Android SDK at /usr/local/lib/android/sdk; the official
[.NET installer](https://github.com/actions/runner-images/blob/ubuntu24/20261012.334/images/ubuntu/scripts/build/install-dotnetcore-sdk.sh)
uses /usr/share/dotnet. The
[runner context](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#runner-context)
distinguishes hosted/self-hosted execution. These are verified fixed locations, not
permission to remove similarly named paths elsewhere. No new cloud application service,
production approval or authority over developer data is introduced.

## Complete hosted acceptance

Integrated source `5d95f9d7cc2fe37a9a2f8624ea6b6960f8e5f497` passes complete
[39171302022](https://github.com/Jotham566/kasoma/actions/runs/39171302022): 940 unit/contract, 378 integration,
35 tooling, 105 ordinary browser executions, three UI harness cases and three native
WebKit transport-control cases, migrations/restore/restricted login, source/dependency/
image security and container smoke. It is promoted to main with a documentation-only
closeout; merged branches are removed. The older standalone clock disk failure remains
failed evidence. No real-data, academic, provider or production approval is inferred.
