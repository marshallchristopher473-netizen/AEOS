# AEOS Pilot Environment Map (P01 inventory)

Status: **OBSERVED — read-only inventory, 2026-10-24.** Every row says how it
was observed. Blank or BLOCKED means it could not be established without
guessing. No secret values appear in this file. Project refs and URLs are
identifiers, not credentials.

## 1. Gate summary for P02

| Required artifact | Status | Why |
|---|---|---|
| Candidate branch / SHA | Observed | `main` = `b9c68aa3e6fe35f676da04c10683bfdda12a9eed`. Working branch `ccr-f3f20edd-1srqpx` started at the same SHA. A human must still confirm this is the pilot candidate. |
| Local/test Supabase project for P02 migrations | **BLOCKED** | No project is both reachable and designated as test. See §3. |
| Backend deployment | **BLOCKED** | No FastAPI deployment is observable. See §4. |
| Launch pack + decision packet | **BLOCKED** | Not found in repo, filesystem, or Google Drive. |
| Scaffold files (migration + 6 TS files + 2 tests) | **BLOCKED** | Referenced as "provided below" in the master task; not included. |

## 2. Source control

| Item | Value | How observed |
|---|---|---|
| Repo | `marshallchristopher473-netizen/AEOS` | git remote |
| Default branch | `main` | git |
| HEAD of `main` | `b9c68aa` (merge of PR #17, P0 security repair) | `git rev-parse origin/main` |
| CI | `.github/workflows/p0-backend-tests.yml`: RLS-against-Postgres job, mutation suite, backend pytest, frontend lint/typecheck/build/`npm audit` | file read |

## 3. Supabase

Observed through the Supabase connector with read-only calls
(`list_projects`, `list_migrations`, `list_branches`, `list_tables`, one
privilege-metadata `SELECT`). No data rows were read. Nothing was written.

| Project | Ref | Status | Observation |
|---|---|---|---|
| AEOS-MVP | `hbcgsukmbgiytcznmmec` | ACTIVE_HEALTHY | Referenced by `.replit` (`SUPABASE_URL`). See detail below. |
| aeos-v05-verify-disposable | `doblbkfogcykpfwkfycs` | ACTIVE_HEALTHY | `list_migrations` failed: password authentication failed for user `postgres`. Not usable from this session. |
| GradeFreed-AI | `drcetslvctzkgaxvzerq` | INACTIVE | Out of scope (no standalone GradeFreed). |

**AEOS-MVP detail:**

| Check | Result |
|---|---|
| Tracked migrations (`supabase_migrations`) | **none** (empty list) |
| Supabase branch `main` | status `MIGRATIONS_FAILED` (created 2026-08-31) |
| Tables in `public` | 13: the repo-migration set **plus** `notes` and `ai_recommendation_runs` from the root `AEOS_Supabase_Setup.sql`. Hybrid of two schema sources. |
| Row counts | 0 in every table (connector summary) |
| RLS enabled | yes on all 13; **forced on none** |
| RLS policies | **0 on every table** |
| Repo helper functions (`aeos_has_org_access`, …) | **absent** |
| `anon` / `authenticated` hold TRUNCATE | **yes, on all 13 tables** |
| `anon` holds SELECT grant | yes (RLS with zero policies currently denies rows to PostgREST) |

**What this means:**

1. The P0-hardened RLS in migrations 002–004 is **not deployed** to AEOS-MVP.
   The live schema did not come from the repo's migration chain.
2. With zero policies, PostgREST access is deny-all today. That is safe by
   accident, not by design. The FastAPI service-role path is unaffected.
3. Applying the pilot migration on top of this would apply to a schema whose
   provenance is unknown. It is not a reviewable base.
4. Whether AEOS-MVP is "production" is not recorded anywhere. Because it is
   the only healthy, reachable AEOS project and the one `.replit` points to,
   treating it as a disposable test target would be a guess. **No migration
   was applied to it.**

## 4. Deployments

| Surface | Observation | Status |
|---|---|---|
| Frontend on Vercel | A project named `aeos` (`prj_YN58grCsUbX3NNvC0ySXlBAfpNqR`, team `team_3l5DZy3Rr91pttvZdWfgQ9KJ`) appears in `list_projects`. `get_project` returned 404 and `list_deployments` returned 403. Git link, framework, root directory, env var names and deployed SHA are **not observable**. | BLOCKED |
| FastAPI backend | `.replit` runs `uvicorn app.main:app` on port 8000 (Replit workflow). No deployment URL, SHA, or health response was observable from this session. No other backend host is configured in the repo. | BLOCKED |
| `NEXT_PUBLIC_API_URL` in any deployed frontend | not observable | |

## 5. Configuration variable names (no values)

| Runtime | Variable | Source |
|---|---|---|
| Backend | `APP_ENV`, `DEBUG`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISSUER`, `SUPABASE_JWT_AUDIENCE`, `AI_PROVIDER` | `backend/app/core/config.py`, `.env.example` |
| Frontend | `NEXT_PUBLIC_API_URL` | `frontend/src/lib/api.ts` |
| Tests | `AEOS_TEST_DATABASE_URL`, `AEOS_REQUIRE_RLS_TESTS` | CI workflow, `tests/` |

`SUPABASE_SERVICE_ROLE_KEY` is read only by the backend
(`supabase_service.py`). No frontend code references it.

## 6. Local/test environment actually used in this session

| Item | Value |
|---|---|
| Database | Throwaway PostgreSQL 16.15, `127.0.0.1:55432`, trust auth, destroyed with the container |
| Supabase emulation | `backend/tests/sql/supabase_shim.sql` (roles, `auth.uid()`, default grants) |
| Supabase Auth / JWKS / PostgREST | **not available**; the Supabase CLI is not installed. End-to-end JWT tests against a real issuer cannot run here. |
| Results | See `docs/pilot-backend-contract.md` §8 |

This environment is enough for RLS and API-unit tests. It is **not** a
Supabase project, so it cannot satisfy "apply the migration to the local/test
Supabase project and record the version" on its own.

## 7. Decisions needed from a human before P02

1. **Test target:** designate one project for P02 migrations. Options:
   (a) restore DB access to `aeos-v05-verify-disposable` and confirm it is
   disposable; (b) run the Supabase CLI locally (Docker); (c) explicitly
   designate AEOS-MVP as non-production and accept rebuilding its schema
   from migrations 001–004 first.
2. **Architecture:** pilot endpoints in FastAPI (reuses the verified auth
   chain) or Next.js route handlers (a second auth path). See the contract,
   §6.
3. **Inputs:** supply the launch pack, the decision packet, and the scaffold
   files.
4. **Live schema drift:** decide whether AEOS-MVP should be brought onto the
   repo's migration chain. Separate from the pilot, its RLS is not the
   verified RLS.
