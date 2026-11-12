# End-to-end tenant-isolation harness

Drives the real request path with synthetic data only:

```
HTTP client -> AEOS FastAPI (uvicorn) -> supabase-py -> PostgREST 12.2.3 -> PostgreSQL 16
                                                         (shim + every committed migration)
```

It also calls PostgREST directly as an authenticated tenant member, which is the
path the RLS policies govern.

## Why it exists

The unit suite uses an in-memory fake, and `test_rls_enforcement.py` exercises
PostgreSQL directly. Neither runs the API against a real database. That gap hid
a defect for the whole of P0: no table had an `id` default, so every create
endpoint returned 500 against PostgreSQL (fixed by migration 005, found by
P0-01). This harness is the only check that covers the assembled stack.

## What it checks (89 checks; all must pass)

| ID | Boundary |
| --- | --- |
| U1–U3 | Unauthenticated, forged, expired, wrong-audience/issuer, unknown-subject tokens rejected; anonymous PostgREST sees no rows |
| X1–X2 | Lists return only the caller's tenant; another tenant's record by id is 404 |
| X3 | Creating a record that references another tenant's school/student/assessment is 404 |
| X4 | `organization_id` / `created_by` in a request body is 422; tenant claims in the token are ignored |
| X5 | No update/delete routes exist (405) |
| R1–R6 | Direct PostgREST as tenant A cannot read, update, delete, insert into, or move rows into tenant B |
| X6 | Tenant B's rows are byte-identical after every attack |
| A1–A2 | Authorized creates succeed (201) and are invisible to the other tenant |
| P1–P2 | Created and seeded records survive a full app + PostgREST restart |

`run_e2e.py` fails if the number of checks that ran is not exactly 89, so a
check that silently stops running cannot produce a green result.

## Running locally

```bash
# Disposable PostgreSQL 16 only. `init` drops and recreates $AEOS_E2E_DB.
export AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
cd backend/tests/e2e
./stack.sh fetch     # PostgREST binary, SHA-256 verified
./stack.sh init      # local-only keys + fresh database
./stack.sh up
python3 run_e2e.py   # exit 0 only when 89/89 pass
./stack.sh down
```

Uses ports 8000 (API), 3001 (PostgREST) and 54321 (gateway). Keys, logs, the
PostgREST binary and `e2e-results.json` go to `backend/tests/e2e/.work/`
(git-ignored), or `$AEOS_E2E_WORKDIR`.

## Fidelity and limits

- **Tokens** are RS256, signed by a key generated per run and served as JWKS by
  `gateway.py`. The app verifies them through its real `get_current_user`.
  Supabase Auth (GoTrue) itself is not run: login, refresh and sign-up are out
  of scope.
- **`gateway.py`** only maps Supabase's URL layout (`/auth/v1/jwks`,
  `/rest/v1/*`). It makes no access decisions: PostgREST and PostgreSQL do.
- **Roles and `auth.uid()`** come from `tests/sql/supabase_shim.sql`, not a real
  Supabase instance.
- A pass here is **local evidence only**. It does not establish isolation on a
  deployed Supabase project.
