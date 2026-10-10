# P0 Stage A — Independent Verification of PR #27

**Verifier session:** separate from the builder session (`session_01J58GVwxqzenqXBnLbt5phL`).
**Date:** 2026-10-10
**Scope:** Gate 1 only (independent local reproduction plus adversarial review). The
candidate was **not modified**. Nothing was written to any hosted Supabase project.

## Decision

| Gate | Decision | Basis |
| --- | --- | --- |
| 1. Independent local reproduction of `bcf58e1` | **VERIFIED** | Every builder claim reproduced exactly (table below) |
| 2. Isolated non-production Supabase verification | **BLOCKED** | Not run. Needs explicit approval to write to a hosted project |
| 3. Remaining findings → final P0 decision | **BLOCKED** on Gate 2 | Two new non-blocking findings (F1, F2) recorded below |
| **P0 overall** | **BLOCKED** | Gate 2 is unresolved. Do not merge, deploy or use real student data |

## 1. Candidate identity

| Item | Builder claim | Independently observed |
| --- | --- | --- |
| Head SHA | `bcf58e1660a47738450d9795a327a75f7e573c90` | same |
| Head parent | `b9c68aa` (main) | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` |
| Head tree | `3f296e04488010ea45d7a1dfbd8a5477ea1ff843` | same |
| `refs/pull/27/merge` | `522eaac…`, same tree | `522eaac6abadfe173922aff75e5fff4a4ea185d0`, tree `3f296e04…` (identical) |
| Changed files | 16, +2104 / −447 | same |

Because the merge-ref tree equals the head tree byte for byte, the CI artifacts keyed to
`522eaac…` describe exactly the code at `bcf58e1`.

## 2. Environment

A clean, detached `git worktree` at `bcf58e1`, a fresh Python 3.11.17 venv
(`pip install -r backend/requirements-dev.txt`), a fresh `npm ci` (Node 22.22.0, npm 10.9.4),
and a throwaway PostgreSQL 16.15 cluster created for this run. Resolved security-relevant
versions: `python-jose 3.5.0`, `python-dotenv 1.2.2`, `fastapi 0.115.0`, `starlette 0.38.6`,
`cryptography 50.0.2`, `next 16.3.8`, `sharp 0.35.5`.

## 3. Reproduction results (every CI step, same commands)

| Command | Exit | Result |
| --- | --- | --- |
| `python -m compileall -q backend/app backend/tests` | 0 | |
| `from app.main import app` / schemas / dependencies imports | 0 / 0 / 0 | |
| `pytest tests/test_rls_enforcement.py` (`AEOS_REQUIRE_RLS_TESTS=1`) | 0 | **214 passed** |
| `pytest tests/` (`AEOS_REQUIRE_RLS_TESTS=1`, PG 16.15) | 0 | **347 passed, 0 failed, 0 skipped** |
| JUnit zero-skip gate | 0 | `{'tests': 347, 'failures': 0, 'errors': 0, 'skipped': 0}` |
| `python -m tests.security_mutations --json` | 0 | **41/41 killed; 0 survived, 0 invalid, 0 equivalent, 0 not executed** |
| `pytest tests/` with no database (the `backend-tests` job) | 0 | 133 passed, 214 skipped (expected; the RLS job enforces zero skips) |
| `npm ci` | 0 | |
| `npm audit --audit-level=low` / `--omit=dev` | 0 / 0 | 0 vulnerabilities / 0 vulnerabilities |
| `npm ls --all` | 0 | |
| `node tests/lint-glob-override.test.mjs` | 0 | 0 failures |
| `CI=1 npm run lint` / `npx tsc --noEmit` / `npm run build` | 0 / 0 / 0 | |

After all runs, `git status` in the worktree showed only `frontend/tsconfig.tsbuildinfo`,
which is a build byproduct. No tracked file changed.

## 4. Adversarial review (beyond the builder's suite)

The JWT verification path (`backend/app/core/auth.py`) and migration 005 were read line by
line. Neither has a confidentiality or integrity defect. The algorithm is pinned by the
selected key and never taken from the token. Symmetric keys are refused. `exp`, `aud`, `iss`
and `sub` are required. JOSE errors map to 401. A failed key refresh fails closed with 503.
Two new findings came out of probes the existing suite does not model.

### F1 — `anon` keeps EXECUTE on SECURITY DEFINER helpers on hosted Supabase (Low, hardening)

- **What:** Migrations 002/003 run `REVOKE ALL ON FUNCTION … FROM PUBLIC` and then grant
  EXECUTE to `authenticated`. Hosted Supabase also has
  `ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon, authenticated, service_role`.
  That is a *direct* grant to `anon`, which a revoke from `PUBLIC` does not remove. The test
  shim (`tests/sql/supabase_shim.sql`) models Supabase's table defaults but not its function
  or sequence defaults, so the suite cannot see this.
- **Reproduced:** A probe database used the shim plus Supabase's function and sequence default
  privileges, then applied migrations 001–005. `has_function_privilege('anon', …, 'EXECUTE')`
  was **true** for `aeos_has_org_access`, `aeos_can_write_org`, `aeos_is_org_admin`,
  `aeos_current_user_ids` and `aeos_is_current_actor_for_org`. Through PostgREST these are
  callable as `/rest/v1/rpc/<name>` with only the anon key.
- **Impact measured:** As `anon`, each helper returned `false` or an empty array. No row data
  leaked, and `anon` still saw 0 organizations. This is a least-privilege gap and a mismatch
  between the test model and the hosted environment, not a demonstrated tenant breach.
- **Disposition:** Non-blocking for P0. Confirm on the hosted project in Gate 2 (query below).
  Fix in a follow-up candidate with a forward-only migration that runs
  `REVOKE EXECUTE ON FUNCTION … FROM anon` for each helper, and extend the shim with
  Supabase's function and sequence defaults so a test can pin it.

### F2 — Unknown `kid` forces an unthrottled JWKS refresh (Medium, availability)

- **What:** In `get_current_user`, a token whose `kid` is not cached triggers
  `get_jwks(force_refresh=True)` on every request, with no cooldown. The token needs no valid
  signature to reach that point.
- **Reproduced:** 50 unauthenticated requests with random `kid`s caused **51 outbound JWKS
  fetches**, and all 50 were correctly rejected with 401 (probe: patched `httpx.AsyncClient`
  counting `get` calls).
- **Impact:** No authentication bypass, because the check fails closed. An anonymous caller can,
  however, drive unbounded traffic to the Supabase key endpoint. If that endpoint rate-limits
  the backend, the next scheduled 600 s refresh fails and **legitimate users get 503** until it
  recovers.
- **Disposition:** Non-blocking for the P0 confidentiality gate. **Fix before any pilot that
  exposes the API publicly.** Smallest fix: allow at most one forced refresh per short window
  (for example 30–60 s), and add a test that N random-`kid` requests cause at most one fetch.

### Observation (pre-existing, not introduced by #27)

Every FastAPI data route uses `get_supabase_admin_client()` (the service role, which
**bypasses RLS**). For the API path, tenant isolation therefore rests on the app layer:
`get_db_user` takes the organization from the server-side user record, and the
`tenant_scope` helpers filter every query by it. Those checks are tested against a fake DB.
The database RLS policies protect direct PostgREST access only. Gate 2 should therefore
attack **both** paths: direct PostgREST with a user JWT, and the FastAPI routes.

## 5. Gate 2 plan (not yet executed — requires approval)

Run this against an isolated, non-production project with synthetic data only. Candidate
seen in the account: `aeos-v05-verify-disposable` (`doblbkfogcykpfwkfycs`, PG 17). Do not use
`AEOS-MVP` (`hbcgsukmbgiytcznmmec`).

1. Confirm the project is disposable and holds no real data. Apply migrations 001–005 from `bcf58e1`.
2. Create two synthetic orgs (A, B) with one teacher each, signed in through Supabase Auth
   using the project's asymmetric (ES256) signing key.
3. Cross-tenant attacks as teacher B against org A, over PostgREST and the FastAPI routes:
   SELECT, INSERT, UPDATE and DELETE all denied, and A's row counts unchanged.
4. `TRUNCATE … CASCADE` as `anon` and `authenticated` is denied on all 11 tables.
5. Hosted privilege inventory:
   - `has_table_privilege` for TRUNCATE, TRIGGER and REFERENCES is false for `anon` and `authenticated`.
   - `pg_default_acl` shows no TRUNCATE for those roles **for every creator role** (`postgres`,
     `supabase_admin`), not only the role that ran migrations.
   - F1: `has_function_privilege('anon', …)` for the five helpers.
6. Real JWT checks: a valid ES256 token is accepted. Tokens that are expired, have no `exp`,
   have the wrong `aud` or `iss`, are HS256-signed, or carry an unknown `kid` are all rejected
   with 401.
7. Tear down, or reset the project afterwards.

**Definition of done for P0:** Gate 2 steps 1–6 all pass and are recorded with outputs, F1 is
confirmed or refuted on hosted, and a final `VERIFIED` / `REJECTED` decision is written here.
