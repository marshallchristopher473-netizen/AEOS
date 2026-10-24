# AI feedback pilot consolidation — not launch approval

## Identity and scope

The owner selected **teacher-reviewed AI feedback drafting on synthetic ELA
responses** as the pilot workflow. This record covers folding the P0 Stage A
security candidate into that workflow's lineage. It adds no feature code.

| | SHA |
| --- | --- |
| `main` | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` |
| AI feedback lineage tip (PR #47) | `92ed3984c90ac3314a22f18a77482d6b76974966` |
| Security-only lineage tip (PR #49) | `38877cffcf1f47108135bb46d49bf52674b01082` |
| **Tested commit** | **`4347113b0e2fed5b330bf32a737876834aeb34c5`** |
| Tested tree | `6589ebfbd69a47a7a9e03ee8ae2a607f0ad23c6a` |

Lineages: `main` → #28 → #32 → #35 → #42 → #46 → #47, and `main` → #27 → #34 → #49.
Pull request: #50 (draft).

## Blockers closed on the pilot lineage

Each control below was absent at `92ed398` and is present at `4347113`.

| Blocker | From | Mutants |
| --- | --- | --- |
| A token without `exp` was accepted | #27 | M18l |
| The JWKS cache never expired, so a revoked key kept verifying; a failed refresh must fail closed | #27 | M18m, M18n |
| F2: every unknown `kid` caused an outbound JWKS fetch | #49 | M18o |
| F1: `anon` held EXECUTE on SECURITY DEFINER functions | #49 (migration 008) | M22a, M22b |
| F4: client roles held MAINTAIN on PostgreSQL 17 | #49 (migration 008) | M19e, M19f |
| `next` ≤ 16.4.0 (critical/high) and `zod` < 4.6.6 (high) | #49 | — (strict audits) |
| CI exercised PostgreSQL 16 only | #49 | — (16 + 17 matrix) |

Migration 008 revokes `anon` EXECUTE from all ten SECURITY DEFINER functions
on this tree, including the five added by migrations 006 and 007.

## Evidence on the tested commit

Local environment: Python 3.11.17 venv from `requirements-dev.txt`;
PostgreSQL 16.15 (Ubuntu cluster); PostgreSQL 17.6 from
`@embedded-postgres/linux-x64@17.6.0-beta.15`, because postgresql.org is
blocked in this environment; Node 22.22.0 and npm 10.9.4. CI pins Node
22.22.2 and npm 10.9.7. Synthetic data only. No hosted system was contacted.

| Check | Environment | Result |
| --- | --- | --- |
| Full backend suite, `AEOS_REQUIRE_RLS_TESTS=1` | local PG 16.15 | 637 passed, 0 failed, 0 errors, 0 skipped |
| Full backend suite, `AEOS_REQUIRE_RLS_TESTS=1` | local PG 17.6 | 637 passed, 0 failed, 0 errors, 0 skipped |
| Backend suite without a database | local | 312 passed, 325 skipped (database modules) |
| Mutation contract | local PG 16.15 | **52/52 killed**; 0 survived, equivalent, invalid or not executed; M19e/M19f NOT APPLICABLE (no MAINTAIN on 16) |
| Mutation contract | local PG 17.6 | **54/54 killed**; 0 survived, equivalent, invalid, not executed or not applicable |
| Mutation anchors | local | 54 unique anchors substitute |
| `npm ci`; `npm audit --audit-level=low`, full and `--omit=dev`; `npm ls --all` | local | exit 0; 0 vulnerabilities |
| Request-contract tests, lint-glob guard, lint, `tsc --noEmit`, build | local | exit 0 |
| `rls-enforcement (16)`, `rls-enforcement (17)`, `backend-tests`, `frontend-validation` | GitHub Actions on `4347113` | success |

Matrices: [`evidence/pilot-consolidation-4347113/`](evidence/pilot-consolidation-4347113/)

| File | SHA-256 |
| --- | --- |
| `mutation-matrix-pg16.json` | `b6036a26600180b1e26c7c228d63c407945ba513af403ec1880b0be0d6207485` |
| `mutation-matrix-pg17.json` | `52d900efe6e9fdb4f24ae841da1ca5dbbfd1119e3cd6ff0e1c7eb5c58ad3945e` |

## NOT RUN

| Check | Why |
| --- | --- |
| Hosted Supabase two-tenant attacks, real ES256 JWT, migrations 001–008 on a disposable project | No disposable-project credentials; `*.supabase.co` not allowed from the build session |
| Genuine provider smoke check and teacher-free quality check | No server-side provider key, model ID or prices configured; the build session's own credentials were deliberately not used |
| Browser walk-through, run locally | Not run locally; CI `frontend-validation` runs it |
| Independent verification | A builder session cannot verify its own head |

## Still blocked

| Gate | Owner |
| --- | --- |
| Teacher sign-in: the frontend reads a bearer token from `localStorage`, and no sign-in screen exists on this lineage. PR #48 adds one but conflicts in 10 files. | Engineering: a separate PR stacked on #50 |
| Teacher approval of rubric RUB-CER3 v0.1; until its hash is pinned the server refuses every request | Teacher / owner |
| Real student data: consent, data-processing agreement, retention policy | Owner |

P0 VERIFIED and TECHNICAL PILOT READY are not claimed.
