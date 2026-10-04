# Teacher assessment review

## Scope and behavior

The bounded workflow is `/assessments` → open or create an assessment → read
saved reviews → enter a summary and optional score → save a draft or complete
review → reload the page and read it again. Discard clears an unsaved form.
Every save creates a new assessment-result row. It does not edit an older review,
change the assessment's status, or create an intervention plan.

The UI shows loading, empty, failed-read, failed-save, and confirmed-save states.
It keeps form contents after a failed save and disables the form during a write.
A score of zero is displayed as zero. The UI does not generate findings or AI
recommendations; every new summary is teacher-entered.

## Services and boundaries

- All three assessment pages use `src/lib/api.ts` through `src/lib/assessments.ts`.
  The client reads the existing `aeos_access_token` session convention.
- Next.js proxies same-origin `/api` requests to `AEOS_API_URL`. Bearer headers
  reach the unchanged backend authentication dependencies.
- `AssessmentService` and `AssessmentResultService` reuse `tenant_scope.py`.
  The shared insert helper generates UUIDs because the migrations do not supply
  ID defaults. No schema migration is required for this change.
- The filtered result collection checks that the assessment belongs to the
  server-derived organization before returning only that assessment's results.
  The underlying tenant collection remains unpaginated, as in the existing slice.
- Teacher/admin write authorization and server-derived organization, author,
  and student identity remain in force. Support users receive the existing 403
  on writes. The form does not supply those authority fields.
- Scores are optional, finite, and bounded by the existing `NUMERIC(6,2)` storage.
  A supplied maximum is at least 0.01; score cannot exceed it. The browser accepts
  hundredths. The API accepts the existing assessment status vocabulary.

## Development prerequisites

Use the startup commands in the root README. For a real database run, configure
the existing backend environment and an isolated database with migrations
001–004 applied. This guide does not establish hosted Supabase readiness.

The current main authentication code accepts RS256 sessions and derives the
AEOS user from the verified subject. Its default JWKS path and ES256 support
are the subject of the still-separate draft PR #22. Check the configured
`SUPABASE_JWKS_URL`, issuer, audience, active organization, and active teacher
membership before using a real session. Do not treat that unmerged PR as part
of this workflow candidate.

The frontend currently expects a valid session access token under the browser
local-storage key `aeos_access_token`; it has no sign-in UI. A development user
must obtain that session from their configured authentication provider. Never
use a service-role key as a browser session token.

Open `/assessments`, select **Review**, enter findings, select **Draft** or
**Complete**, and choose **Save review**. Confirm the saved review appears,
then reload and confirm it remains. Choosing **Complete** completes the new
review only; assessment intake and review status are separate records.

## Reproduction commands

```bash
cd backend
python -m pytest tests/test_assessment_results.py tests/test_assessments.py tests/test_authorization.py tests/test_route_authentication.py -q
python -m pytest tests/ -q -rs
```

```bash
cd frontend
node --experimental-vm-modules tests/assessment-api.test.mjs
npm ci
npm run lint
npx tsc --noEmit
npm run build
```

The six request-contract checks use Node's built-in test tools (Node 22.13+),
with the actual TypeScript request modules and synthetic fetch responses.
They can run before `npm ci`; they do not render React. CI now uses Node 22
to meet the pinned frontend packages' engine requirement and runs these checks.

CI also builds the actual Next.js frontend, starts the loopback-only
`backend/tests/review_fixture_server.py` with `AEOS_SYNTHETIC_REVIEW=1`, and runs
`frontend/tests/browser_review.py` against Chrome. The fixture uses production
HTTP routes, actor resolution, services, and schemas with synthetic sessions
and storage. The browser check covers intake, empty reviews, saving/reloading
both states, zero/optional scores, validation, discard, failed-save retention,
role and cross-tenant denial, and missing-session feedback. It uses the
existing backend dependencies and the runner's Chrome; no lockfile is changed.
It does not establish JWT verification or real PostgREST persistence.

For the limited offline business-logic check from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python docs/evidence/teacher-review-offline-check.py
```

That harness imports the production request schemas, endpoint functions, shared
services, and membership/role dependencies. It calls those functions directly
against the existing synthetic fake, using import-only placeholders for the
unavailable JWT and Supabase SDK modules. It does not exercise HTTP dispatch,
JWT verification, the Supabase SDK, or a real database.

The API workflow regression uses the repository's synthetic database fake and
checks explicit server-generated IDs, both review states, zero-score retention,
reload, assessment isolation, cross-tenant denial, and invalid input rejection.
It does not exercise PostgREST persistence or certify live RLS. The full backend
suite's database tests require an isolated PostgreSQL service and
`AEOS_TEST_DATABASE_URL`; use `AEOS_REQUIRE_RLS_TESTS=1` to fail on missing RLS
infrastructure instead of silently skipping it.

## Repository provenance and verification record

Recovered source: `marshallchristopher473-netizen/AEOS`, main commit
`b9c68aa3e6fe35f676da04c10683bfdda12a9eed`, tree
`df6e6d6047f725035af6c7aadd1c4852aeb5f326`.
The workspace initially had no checkout. The GitHub connector supplied all 85
tracked blobs; their hashes, file modes, reconstructed tree, and signed shallow
commit matched the remote evidence before edits. No open feature/security branch
was merged into this slice.

Local checks recorded on 2026-10-04:

| Check | Result | Scope |
| --- | --- | --- |
| Source recovery | Exact commit/tree and all 85 tracked blobs matched | Repository provenance only |
| Offline business-logic harness | 8 passed, exit 0 | Synthetic create/save/reload, both states, zero score, UUID generation, tenant/role/lifecycle checks, invalid/spoofed fields |
| Frontend request contracts | 6 passed, exit 0 | Real API modules, synthetic fetch/storage; same-origin/configured base, payload, bearer header, errors and cancellation |
| TSX syntax | All 3 assessment pages parsed | Installed Playwright Babel parser; not type checking or rendering |
| Python compilation and `git diff --check` | Exit 0 | Syntax/patch checks |
| Pinned dependency installation | Blocked locally | npm network denied; pip dependencies unavailable; network-access requests were canceled |
| Full pinned pytest, lint, type check, build, browser run, live database | Not established locally | Do not infer these from the limited checks above |

Offline Python runtime: Python 3.12.14, FastAPI 0.141.1, Pydantic 2.13.4;
these differ from the repository pins. Frontend request checks used Node
24.19.0. The installed unpinned HTTP runtime also timed out on a minimal
synchronous FastAPI endpoint, so the HTTP harness was stopped and replaced
by the explicitly limited direct-function check above. This is not a failure
attributed to the pinned candidate.

The draft workflow PR is the place to reconcile the existing GitHub Actions
jobs against its exact pushed head. Historical PR test counts are not evidence
that this modified candidate passed. Hosted Supabase, browser verification,
and independent P0 certification require separate evidence.

The initial PR #23 candidate `823dcdf` passed the backend and RLS CI jobs but
failed the frontend audit on the unchanged lockfile: 7 reported vulnerabilities
(6 high, 1 critical), including the Next.js ImageResponse advisory
`GHSA-vcvr-r3jv-pc5j`. That run skipped subsequent frontend steps. CI now runs
the functional checks after a successful install even when audit fails;
the audit remains a failing gate. Dependencies and the lockfile are preserved,
and this workflow is not cleared for merge or deployment by that evidence.

## Claims this workflow supports

This is a teacher-entered assessment review prototype. A synthetic-data check
can establish the specific behavior it exercises. It cannot establish AI
accuracy, reduced workload, improved student outcomes, complete audit coverage,
completed sign-in, independent P0 verification, deployment success, or pilot
readiness. Those claims have been removed from the root README and the Replit
overview; the MVP criteria remain explicitly marked as targets.
