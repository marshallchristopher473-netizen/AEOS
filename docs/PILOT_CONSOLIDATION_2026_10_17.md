# Teacher pilot working consolidation — not launch approval

## Identity and scope

Working branch: `p0/security-pilot-20261017`.

Parent: PR #35 `7a727920c6bf831a7dbc7951a5694bad2d77c23d`.
Lineage: `main` → PR #28 → PR #32 → PR #35 → this bounded repair.
This selects a working integration for review; it does not approve or close
any historical PR, select a production release, or issue independent verification.

The only executable changes relative to that parent are:

1. `frontend/package.json` and `frontend/package-lock.json`, copied exactly
   from the focused repair `930d2c7` / PR #34 `976a1ad`.
2. The every-linted-file rootDir guard from PR #34 `976a1ad`.

The inherited CI already pins Node 22.22.2 / npm 10.9.7, runs full and
production strict audits, and executes this guard. Its existing `p0/security-*`
push trigger matches this branch, so publication can test the exact head even
though PR #35's stacked target did not trigger CI. No workflow threshold or
backend code is changed here. The feature flag remains off, approval pins
remain empty, and the candidate rubric remains unapproved.

## Fresh local evidence

Environment: Node 22.22.2, npm 10.9.7, Python 3.12.14. No live model calls.

| Check | Result |
| --- | --- |
| Clean `npm ci` | PASS |
| Full and production `npm audit --audit-level=low` | Both 0 vulnerabilities |
| `npm ls --all` | PASS |
| Assessment request contracts | 6 passed, 0 failed, 0 skipped |
| AI feedback request contracts | 6 passed, 0 failed, 0 skipped |
| Lint override guard | 3 passed, 0 failed, 0 skipped |
| Lint, TypeScript, production build | PASS |
| Backend suite, no database | 288 passed, 250 skipped |
| Mutation anchor integrity | 37 unique anchors, Python targets parse |
| `git diff --check` | PASS |

The first backend attempt had 287 passes and one environment failure: the
installed HTTP client required `socksio` to support this environment's proxy.
Installing that environment-only dependency resolved it; the repeated full
suite returned the result above. No application test or requirement was edited.

The 250 database skips do not establish RLS or tenant isolation. Local PostgreSQL
could not be installed in this execution environment. No fresh mutation-kill,
browser, hosted-login or durable-storage result is asserted. Prior PR results
remain scoped to their original SHA.

## Current blockers and next bounded actions

| Gate | Status | Fresh evidence / next action |
| --- | --- | --- |
| Local dependency repair | PASS | Full and production audits both report 0 |
| Publication and exact-head CI | BLOCKED | Automatic approval review rejected the push as unapproved repository-content disclosure to the destination. Owner approval of the exact payload and destination is required before publication. Then publish this branch and inspect every CI job and artifact. |
| Hosted SQL connection | BLOCKED | Read-only `select current_database(), current_user, version()` against `aeos-v05-verify-disposable` (`doblbkfogcykpfwkfycs`) returned `28P01` for `postgres`. Restore working database access through the project's supported controls; do not paste credentials into chat. |
| Hosted RLS and two-tenant attacks | NOT TESTED | Depends on working isolated-project access and an exact tested candidate. Review the current schema before any migration or destructive probe. |
| Vercel served SHA / backend mapping | BLOCKED | Project `prj_YN58grCsUbX3NNvC0ySXlBAfpNqR` under team `team_3l5DZy3Rr91pttvZdWfgQ9KJ`: project inspection returns 404, deployment listing returns 403. No accessible CLI authentication is available here. |
| Real teacher sign-in / session | FAIL (inherited) | There is no sign-in page. Bind the pilot identity project and public configuration, implement the shared session flow, then test successful, invalid, expired and revoked sessions. |
| Student pages' API transport | FAIL (inherited, code read confirmed) | Three pages still call `http://127.0.0.1:8000` directly. Move them to the existing shared same-origin API client and test against the actual backend. |
| Malformed deeply nested model JSON | FAIL (inherited report) | PR #38 records an uncaught RecursionError and orphaned reservation. Reproduce and repair in a separate bounded commit. |
| Reconstructed models review | BLOCKED | `backend/app/models/ai_feedback.py` is unchanged. Passing tests and this consolidation are not the required human review. |
| D1–D5 / rubric approval | BLOCKED | No product or scoring decision is inferred from this repair. Reconcile the authoritative protocol and obtain the recorded human approvals. |
| API deployment / rollback / recovery | NOT TESTED | No deploy or hosted write was attempted. Requires security verification, a concrete isolated target and an exercised recovery plan. |
| Teacher value / paid demand | NOT TESTED | Depends on technical readiness and the approved adult-teacher synthetic feasibility protocol. |

P0 VERIFIED and TECHNICAL PILOT READY are **not issued**. No launch approval
sheet is produced. The full-story check stops at the unresolved real sign-in
and hosted-data boundaries. No deployed configuration, credentials, hosted
records, approval pins, visibility settings, or historical PRs were changed.
