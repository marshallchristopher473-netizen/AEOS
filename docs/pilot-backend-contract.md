# AEOS Pilot Backend Contract (P01 inventory)

Status: **OBSERVED — read-only inventory.** This file describes what the code
on the inspected SHA actually does. It is not a design proposal and makes no
verification claim.

| Field | Value |
|---|---|
| Inspected SHA | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` (`origin/main`, merge of PR #17, 2026-09-25) |
| Inspected on | 2026-10-24 |
| Source documents | `AEOS_Pilot_Launch_Prompts_2026-10-13.md` and `AEOS_Research_to_Pilot_Decision_Packet_v0.1.md` were **not found** in the repo, the session filesystem, or Google Drive. The P01 prompt text was therefore not available verbatim; this inventory follows the task description's stated P01 objective. |

---

## 1. Architecture as built

```
Browser (Next.js 16, frontend/)
   │  Authorization: Bearer <token from localStorage 'aeos_access_token'>
   ▼
FastAPI (backend/app, Python)  ── verifies JWT, resolves actor from DB
   │  service-role Supabase client (bypasses RLS)
   │  + explicit organization_id filter on every query (tenant_scope.py)
   ▼
Supabase Postgres  ── RLS policies (migrations 002–004) defend DIRECT
                      PostgREST/client access, not the FastAPI path
```

- **Backend:** FastAPI is the only API layer. There are **no Next.js API
  routes** (`frontend/src/app/api/` does not exist) and no `middleware.ts`.
- **Frontend:** `frontend/src/app/{students,assessments}` pages call FastAPI
  directly. `NEXT_PUBLIC_API_URL` is the only env var read. `@supabase/ssr` and
  `@supabase/supabase-js` are installed but **unused**. There is no login flow;
  the token is expected to already be in `localStorage`.
- **Paths:** the frontend lives at `frontend/src/...`, not `src/...`.

## 2. Authentication and authorization chain

All in `backend/app/core/`. Every business route depends on it.

| Step | Code | Behavior |
|---|---|---|
| 1. Bearer token | `auth.py:get_current_user` | Missing or non-Bearer → 401 |
| 2. Signature | same | RS256 only, key chosen by `kid` from JWKS (`SUPABASE_JWKS_URL`); unknown `kid` → one forced JWKS refresh, then 401 |
| 3. Claims | same | `exp`, `iss` (`SUPABASE_JWT_ISSUER`), `aud` (`SUPABASE_JWT_AUDIENCE`, default `authenticated`) verified; **missing `aud` explicitly rejected**; non-empty `sub` required |
| 4. Actor | `dependencies.py:get_db_user` | `users` row where `auth_user_id = sub` AND `status = 'active'`; 0 rows → 403, >1 → 403 |
| 5. Tenant lifecycle | same | `organizations.status = 'active'` required, else 403 |
| 6. Actor object | `get_current_actor` | `AuthenticatedActor{user_id, organization_id, role, auth_user_id}` built **only from the DB row** |
| 7. Role gate | `require_privileged_write` | Writes require role `teacher` or `admin`; `support` is read-only |

Identity is never taken from `user_metadata`, a request `organization_id`,
editable profile fields, or email. Request models use `extra="forbid"`, and
`insert_tenant_scoped_row` raises if a payload carries `organization_id`.

**The existing "auth middleware" is this FastAPI dependency chain.** Any new
pilot endpoint must use `get_current_actor` / `require_role(...)`.

## 3. API surface

| Method | Path | Auth | Tenant control |
|---|---|---|---|
| GET | `/health` | none | anon client; reports DB status only |
| POST/GET | `/students`, `/students/{id}` | actor; POST = teacher/admin | org filter; `school_id` checked in-tenant |
| POST/GET | `/assessments`, `/assessments/{id}` | same | `student_id` checked in-tenant |
| POST/GET | `/assessment-results`, `/assessment-results/{id}` | same | assessment checked in-tenant |
| POST/GET | `/intervention-plans`, `/intervention-plans/{id}` | same | student + assessment checked, assessment must belong to student |

No UPDATE or DELETE routes exist. No route writes `audit_logs`,
`progress_events`, or `ai_recommendations`.

## 4. Data model (repo migrations 001–004)

Tables: `organizations`, `schools`, `users`, `students`, `assessments`,
`assessment_results` (added in 003), `ai_recommendations`,
`intervention_plans`, `intervention_actions`, `progress_events`, `audit_logs`.

Enums that matter for the pilot:

| Enum | Values |
|---|---|
| `user_role` | `teacher`, `admin`, `support` |
| `organization_status` | `active`, `suspended` |
| `recommendation_status` | `generated`, `reviewed`, `accepted`, `rejected` |
| `assessment_status` | `draft`, `submitted`, `in_review`, `complete` |

RLS: every table has RLS enabled and forced. Access is expressed through
`SECURITY DEFINER` helpers `aeos_has_org_access`, `aeos_can_write_org`,
`aeos_is_org_admin`, `aeos_current_user_ids`, `aeos_is_current_actor_for_org`,
all of which require an active membership in an active organization (004).
`aeos_preserve_row_identity` makes `organization_id` / `created_by` immutable
on UPDATE. DELETE is admin-only (004). `audit_logs` is SELECT-only for org
admins; it has no INSERT policy.

## 5. Reconciliation notes for the pilot scaffold (P02 input)

These are observations, not changes. The scaffold files referenced by the
master task (`contract.ts`, `auth.ts`, `audit.ts`, `evaluator.ts`, the two
route handlers, the migration) were **not provided**, so names could not be
compared line by line.

| Scaffold concept (from task text) | Existing equivalent | Observation |
|---|---|---|
| "decisions" (teacher accept/revise/reject) | `ai_recommendations` + `recommendation_status` | Already models AI suggestion → teacher review → accepted/rejected. Has no `revised` state, no reviewer column, no version, no evidence link. Extend this rather than add a parallel table. |
| "drafts" | `status = 'draft'` on `assessments`, `assessment_results`, `intervention_plans` | No standalone drafts table. |
| audit events | `audit_logs` (`entity_type`, `entity_id`, `action`, `performed_by`, `metadata`) | Exists; never written by the app; no correlation/request ID column; no insert policy. |
| idempotency key | none | Not present anywhere. |
| optimistic concurrency / stale version | none | No `version` column on any table. |
| evidence linkage | `intervention_plans.evidence_summary JSONB` (placeholder) | No evidence table or FK. |
| `src/lib/pilot/auth.ts` (TypeScript auth) | `backend/app/core/auth.py` + `dependencies.py` | **Conflict.** A TS auth module plus Next.js route handlers would be a second JWT-verification and actor-resolution path beside FastAPI. See §6. |

## 6. Open architecture conflict (escalated, not resolved)

The master task places pilot endpoints at `src/app/api/pilot/*/route.ts`
(Next.js route handlers) and wires them "to the existing auth middleware."
The existing middleware is Python. That leaves two options, and choosing
between them is a human decision:

| Option | What it means | Risk |
|---|---|---|
| A. Pilot endpoints in FastAPI (`backend/app/api/pilot_*.py`) | Reuses the verified auth chain and the 30-mutant security suite. Scaffold `.ts` files become thin frontend clients only. | Scaffold must be translated to Python. |
| B. Next.js route handlers as specified | Needs JWT verification and actor resolution reimplemented in TypeScript, and a service-role key in the Next.js server runtime. | Second auth system, not covered by the existing mutation suite. Conflicts with the "no new auth system" rule. |

## 7. Gaps the P02 security tests must cover (found in this inventory)

| Gap | Evidence | Status |
|---|---|---|
| `anon` and `authenticated` hold `TRUNCATE` on every public table | Reproduced on local PG16 with repo migrations + Supabase default grants: `SET ROLE anon; TRUNCATE public.audit_logs;` **succeeded**. RLS does not apply to TRUNCATE. Migrations contain no `REVOKE`. Live `AEOS-MVP` grants the same privilege (see environment map). | FAIL (privilege present). No PostgREST verb issues TRUNCATE; a reachable path would need an RPC or a login role. **Not exploited, not tested end-to-end.** |
| No test asserts TRUNCATE is denied | `grep -i truncate backend/tests` returns nothing | NOT TESTED |
| Self-role-change | `users` has no UPDATE policy, so direct updates are denied by RLS; no API route updates users | Not explicitly tested |

## 8. Baseline test evidence on `b9c68aa`

Run 2026-10-24 in this session, against a throwaway local PostgreSQL 16.15 with
`AEOS_REQUIRE_RLS_TESTS=1`.

| Check | Result |
|---|---|
| `pytest tests/` (170 tests, 62 against real Postgres) | PASS, 3 consecutive runs. The first run reported one teardown ERROR on `test_student_create_rejects_cross_tenant_school_id`; it did not reproduce in 3 later runs or in isolation. Recorded, not explained. |
| `python -m tests.security_mutations` (M01–M18) | PASS: 30 killed, 0 survived, 0 invalid, 0 not executed |

This is the repo's own P0 evidence reproduced locally. It is **not** a P0
VERIFIED verdict; only P05 can issue that.
