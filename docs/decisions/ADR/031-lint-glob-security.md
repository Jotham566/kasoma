# ADR-031: Remove vulnerable lint-only glob dependency

Date: 3 October 2026
Status: Accepted within delegated dependency-maintenance discretion
Requirements: NFR-MNT-001, NFR-SEC-001; security release gate

## Decision

The 3 October dependency audit reports GHSA-vfj7-8cjw-p6xm in braces <=3.0.3,
through @next/eslint-plugin-next 16.3.6 -> fast-glob -> micromatch. The
[advisory](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) lists no patched version.
Registry checks confirm braces 3.0.3 and micromatch 4.0.8 remain latest, and Next's
16.3.8 lint plugin still depends on fast-glob.

Use an exact, parent-scoped pnpm override for @next/eslint-plugin-next@16.3.6's
fast-glob dependency to npm:tinyglobby@0.2.17. tinyglobby is already locked in this
repository. Inspection of the pinned Next plugin shows its only fast-glob usage is
getRootDirs: globSync(pattern, {onlyDirectories: true}). The replacement supports
that operation. A pinned helper patch disables automatic directory expansion and
preserves absolute-pattern output. Trailing separators are normalized by the consumer's
path joins; regression tests compare resolved locations and exercise its actual link rule.
This is not a general drop-in alias for arbitrary fast-glob users.

No Next lint rules are disabled, audit finding ignored or severity threshold reduced.
Application runtime, APIs and data are unchanged. Tests exercise the actual resolved
plugin helper, root defaults, directory-only matching, multiple roots, glob alternatives
and deep patterns. A lint-rule regression proves Next checks still reject invalid links.
Review this override on the next plugin upgrade; its exact parent selector deliberately
does not assume future versions have the same usage. Audit runs still catch regressions.

## Alternatives and rollback

Waiting for an upstream patch leaves the security gate failing. Ignoring the advisory
or excluding developer dependencies weakens the gate. Vendoring braces adds a security
maintenance burden while the registry advisory still applies. Those options are rejected.
If matching or lint compatibility fails, revert the override and keep publication blocked;
do not ignore the advisory. Use make setup to verify the frozen lock installation.

References: [tinyglobby](https://github.com/SuperchupuDev/tinyglobby),
[pnpm overrides](https://pnpm.io/settings#overrides).
