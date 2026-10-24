# Frontend dependency gate repair

This is a focused repair on `main` at `b9c68aa3e6fe35f676da04c10683bfdda12a9eed`.
It does not approve P0, the pilot, a merge, or a deployment.

## Provenance and scope

The package manifest and lockfile are copied byte-for-byte from PR #34,
`976a1ade79ee760f87e7365c46adfb303a462608` (which retains PR #27's dependency
repair). The lockfile's Git blob is `2331c17d65003fa69b11c39d9d64388d50c635a7`.
The every-linted-file guard is also copied from that head.

- Next.js resolves to 16.3.8, sharp to 0.35.5, source-map-js to 1.2.2.
- The `fast-glob` replacement remains scoped to `@next/eslint-plugin-next`.
  Its guard checks required members, every linted file's `settings.next.rootDir`,
  and the raw-link rule. This is not a general fast-glob compatibility claim.
- CI uses Node 22.22.2 / npm 10.9.7, matching Supabase's Node >=22 requirement.
- Full-tree and production audits both fail on findings at severity low or above.
  There is no exception, suppression, force upgrade, or threshold change.
- CI now executes the lint replacement guard before normal frontend validation.

## Executed locally

Node 22.22.2 / npm 10.9.7, clean `npm ci`:

| Check | Result |
| --- | --- |
| Full audit, `npm audit --audit-level=low --json` | 0 vulnerabilities |
| Production audit, `npm audit --omit=dev --audit-level=low --json` | 0 vulnerabilities |
| `npm ls --all` | PASS |
| `node tests/lint-glob-override.test.mjs` | 3 passed, 0 failed, 0 skipped |
| `CI=1 npm run lint` | PASS |
| `npx --no-install tsc --noEmit` | PASS |
| `npm run build` | PASS |
| Backend without database, Python 3.12.14 | 108 passed, 62 skipped |
| `git diff --check` | PASS |

The 62 local skips are database tests, not tenant-isolation evidence. CI must run
the unchanged backend/RLS/mutation jobs against its disposable PostgreSQL service.
Historical green checks are not substituted for this repair's CI results.

## Remaining gates

Apply this repair to one documented teacher-pilot candidate and validate that
exact head separately. Hosted SQL on `aeos-v05-verify-disposable` returned
`28P01` (database password authentication failure) on the read-only connection
probe. No hosted credentials, schema, records, deployments, feature flags or
approval pins were changed. Hosted login, isolation, pilot quality and paid
demand remain unverified.
