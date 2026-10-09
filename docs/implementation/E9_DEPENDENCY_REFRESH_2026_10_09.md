# E9 dependency refresh — 9 October 2026

Requirements: NFR-MNT-001 and the security/release dependency-audit gate.
Status: local checks pass; hosted application/container regression pending.

Today's JavaScript audit failed on three high-severity advisories introduced into the registry since
prior acceptance. Update the runtime Next.js pin from 16.3.6 to 16.3.8; resolve affected Sharp
versions to 0.35.5 and source-map-js versions to 1.2.2 through bounded pnpm overrides. Regenerate
and commit the frozen lockfile using `make deps-lock`. Do not suppress audit findings.

Verified advisory sources:

- [Next.js image optimization SSRF](https://github.com/advisories/GHSA-cjq9-62q9-8jv4), fixed in 16.3.8.
- [Sharp librsvg dependency](https://github.com/advisories/GHSA-wq5f-xc86-pv6w), fixed in 0.35.5.
- [source-map-js indexed offsets](https://github.com/advisories/GHSA-68fv-2mgg-jv7q), fixed in 1.2.2.

The existing ADR-031 lint-only plugin/patch remains pinned and unchanged. Its five integration
checks still verify actual root discovery, safe glob behavior and lint rules. No framework, runtime,
provider or accepted architecture is replaced. Browser/container behavior still needs hosted checks.

`make deps-lock setup` passed with the existing environment preserved. After installation,
`make format lint openapi-check test-unit build security` passed: 427 Python unit/contract and five
tooling tests, Python/TypeScript checks, production Next.js 16.3.8 build, Bandit, secret boundary
and both dependency audits (no known vulnerabilities reported). An overlapping lint attempt during
installation temporarily could not resolve Next's parser; the full post-install run passed.

Native Docker service availability remains a separate issue; successful dependency setup is not
successful database/browser acceptance. The complete hosted pipeline and scanner results remain
required before promotion. No external model, messaging, email or cloud runtime call was made.
