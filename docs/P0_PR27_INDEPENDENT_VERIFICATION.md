# P0 Stage A — Independent Verification of PR #27

**Verifier session:** separate from the builder session (`session_01J58GVwxqzenqXBnLbt5phL`).
**Date:** 2026-10-10
**Scope:** Gate 1 only (independent local reproduction plus adversarial review). The
candidate was **not modified**. Nothing was written to any hosted Supabase project.

## Decision (updated 2026-10-11, run 2)

| Gate | Decision | Basis |
| --- | --- | --- |
| 1. Independent local reproduction of `bcf58e1` | **VERIFIED** (twice) | Every builder claim reproduced exactly in two separate clean checkouts (section 3 and section 6) |
| 2a. Hosted target confirmed | **CONFIRMED** | Section 6.2 |
| 2b. Hosted privilege inventory | **MEASURED: 1 pass, 3 gaps** | Section 6.3. New findings F3 and F4 |
| 2c. Hosted two-tenant attack, TRUNCATE … CASCADE denial, row survival | **BLOCKED** | First attempt timed out with no residue. The retry now needs per-call approval in the session (section 6.4) |
| 2d. Asymmetric JWT against real Supabase Auth | **BLOCKED** | The container's network policy denies `*.supabase.co` (section 6.1) |
| **P0 overall** | **BLOCKED** | 2c and 2d have not run. F4 is a hosted-only gap in the class migration 005 exists to close. Do not merge, deploy or use real student data |

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

## 6. Run 2: clean re-checkout, local reproduction, hosted-native checks (2026-10-11)

### 6.1 Network and retries (reported separately from results)

| Path | Outcome |
| --- | --- |
| `git fetch` of the PR head, `main` and `refs/pull/27/merge` | Succeeded on the first attempt. No retry needed |
| PyPI and npm registry (dependency install) | Succeeded |
| Supabase management API (through the Supabase MCP connector) | **502 Bad Gateway twice**, then recovered after backoff. One later call timed out at 60 s (section 6.4). The connector also disconnected and reconnected several times during the run |
| Direct HTTPS from the container to `*.supabase.co` (Auth sign-in, JWKS, PostgREST) | **Denied with 403 by the environment's network policy.** This is a configuration block, not a transient error, so it was not retried |

Local test infrastructure stayed local. `AEOS_TEST_DATABASE_URL` pointed only at a throwaway PostgreSQL 16.15 cluster on `localhost:55433`, which the verifier created and later stopped. The test suite's create/drop-database behavior never touched the hosted project.

### 6.2 Hosted target confirmation (read-only)

| Check | Result |
| --- | --- |
| Project | `doblbkfogcykpfwkfycs` "aeos-v05-verify-disposable", org `yhvgioxlphpruwcalklk`, us-west-1, PostgreSQL 17.6, ACTIVE_HEALTHY |
| Not the integration-linked project | GitHub and Vercel previews point at `hbcgsukmbgiytcznmmec` (AEOS-MVP), which was not touched |
| Data (exact `count(*)`, not planner estimates) | `auth.users` 0, `auth.identities` 0, `storage.objects` 0. Public tables hold 4 orgs, 9 users and 7 students. Every row is either the fictional seed in `001_initial_schema.sql` ("Demo District", "Northview Academy", "Ava Johnson", "Maya Patel") or earlier verifier fixtures ("Synthetic District A/B/S", `*@synthetic.invalid`, `SYN-*`). **Synthetic only** |
| Schema equals the candidate | Applied 005 is byte-identical to `bcf58e1` (md5 `74584b3a…`). Applied 001–004 differ in bytes only because comments were stripped. A behavioral fingerprint of every policy (33), function body (7), constraint (41), column (107), trigger (14), enum (11) and RLS flag (11) gave **identical digests** on hosted and on a local database built from `bcf58e1`, so no migration or reset was needed |
| Scope used | Read-only catalog queries, plus one attack transaction designed to roll back. No DDL was applied and nothing was committed. A post-timeout check found no verifier rows and unchanged counts |

### 6.3 Hosted privilege inventory (read-only, `has_*_privilege` and `pg_default_acl`)

| Check | Result |
| --- | --- |
| TRUNCATE, TRIGGER and REFERENCES on the 11 existing tables for `anon` and `authenticated` | **0 of 11 each: PASS** (005 is effective on hosted) |
| Future tables created by `postgres` | `anon=arwdm`, `authenticated=arwdm`: no `D`, `x` or `t`. **PASS** |
| **F3: future tables created by `supabase_admin`** | `anon=arwdDxtm`, `authenticated=arwdDxtm`. **GAP.** A table that `supabase_admin` creates in `public` would grant TRUNCATE, TRIGGER and REFERENCES to client roles. 005's `ALTER DEFAULT PRIVILEGES` covers only the role that runs it, and `postgres` cannot alter `supabase_admin`'s defaults |
| **F4: MAINTAIN (PostgreSQL 17)** | `anon` and `authenticated` hold **MAINTAIN on 11 of 11 tables**, and the `postgres` default ACL also grants it (`m`). **GAP.** MAINTAIN is not governed by RLS. It permits `LOCK TABLE` in any mode, `VACUUM`, `ANALYZE`, `CLUSTER`, `REINDEX` and `REFRESH MATERIALIZED VIEW` on every tenant's table. The local suite runs PostgreSQL 16, which has no MAINTAIN, so neither the tests nor the mutation harness can see this |
| F1: `anon` EXECUTE on the 5 SECURITY DEFINER helpers | **Confirmed on hosted** (`anon=true` for all 5) |

**F4 assessment.** PostgREST exposes no `LOCK`, `VACUUM`, `CLUSTER` or `REINDEX` operation, so no known HTTP route reaches it today. That is the same reachability argument migration 005 already rejected for TRUNCATE ("any direct database session as a client role, or any future function that runs dynamic SQL… would turn the grant into a wipe"). MAINTAIN is the availability version of that hole: an `ACCESS EXCLUSIVE` lock on `students` blocks every tenant. Disposition: **blocking for P0 VERIFIED.** It should be fixed in a forward-only migration 006, for example `REVOKE MAINTAIN ON ALL TABLES IN SCHEMA public FROM anon, authenticated` plus the matching `ALTER DEFAULT PRIVILEGES … REVOKE MAINTAIN`, with a PostgreSQL 17 CI service so a test can pin it. The behavioral `LOCK TABLE` probe was part of the transaction that has not yet completed (section 6.4).

**F3 assessment.** This is reachable only if `supabase_admin` creates a table in `public`. AEOS migrations run as `postgres`, so it is not triggered by the current workflow. Disposition: an **owner decision** (accept and document, or add an event-trigger or CI check that rejects `public` tables not owned by `postgres`).

### 6.4 Hosted attack transaction: not yet completed

A single `DO` block was prepared. It inserts two verifier-only synthetic tenants (`e7000000-…`), then acts as teacher B with PostgREST-equivalent claims (`SET LOCAL ROLE authenticated` plus `request.jwt.claims`) and asserts the following:

- B cannot read A's org, schools, users, students or assessments, while B can read its own rows (positive control).
- B's UPDATE and DELETE of A's rows affect 0 rows.
- B's INSERT into A, and B moving its own row into A, are denied.
- `TRUNCATE … CASCADE` is denied with 42501 for `anon` and `authenticated` on all 11 tables (22 attempts).
- Row counts on all 11 tables are unchanged.
- Negative control: an owner truncate shows that the measurement can see a wipe.
- F4 behavioral probe: `LOCK TABLE … ACCESS EXCLUSIVE` as `authenticated`.

The block ends with `RAISE EXCEPTION` so the whole transaction rolls back by construction.

- **Attempt 1** timed out at 60 s in the connector. The most likely cause is an `ACCESS EXCLUSIVE` step waiting on a lock. The follow-up showed no active sessions, no verifier rows and unchanged counts.
- **Attempt 2** split the run, kept only the steps that need no `ACCESS EXCLUSIVE` lock, and added `lock_timeout` and `statement_timeout`. The connector stopped it with "MCP tool call requires approval". It did not run, and it was not retried around the approval.

**These hosted results are therefore NOT established.** Restoring or confirming the project does not count as a passing gate.

### 6.5 Local reproduction, run 2 (fresh worktree at `bcf58e1`, fresh Python 3.11.17 venv, fresh `npm ci`, PostgreSQL 16.15)

| Command | Exit | Result |
| --- | --- | --- |
| `compileall` and the 3 import checks | 0 | |
| `pytest tests/test_rls_enforcement.py` (`AEOS_REQUIRE_RLS_TESTS=1`) | 0 | 214 passed |
| `pytest tests/` (`AEOS_REQUIRE_RLS_TESTS=1`) | 0 | **347 passed, 0 failed, 0 skipped** |
| JUnit zero-skip gate | 0 | `{'tests': 347, 'failures': 0, 'errors': 0, 'skipped': 0}` |
| `python -m tests.security_mutations --json` | 0 | **41/41 killed**: 0 survived, 0 invalid, 0 equivalent, 0 not executed |
| `pytest tests/` with no database | 0 | 133 passed, 214 skipped (expected) |
| `npm audit --audit-level=low` (full and `--omit=dev`) | 0 / 0 | 0 vulnerabilities each |
| `npm ls --all`, glob guards (3 pass, 0 fail), lint, `tsc`, build | all 0 | |
| Worktree after all runs | | No tracked file changed |

### 6.6 Unchanged-head recheck

After all checks: head `bcf58e1660a47738450d9795a327a75f7e573c90`, tree `3f296e04488010ea45d7a1dfbd8a5477ea1ff843`, `main` `b9c68aa`. **Unchanged.**

### 6.7 Verdict: **P0 BLOCKED**

- **Blocked gates:**
  - 2c (hosted two-tenant attack, TRUNCATE CASCADE denial, row survival) needs approval for one rolled-back transaction.
  - 2d (asymmetric JWT) needs `*.supabase.co` allowed in the environment's network settings, or the JWT checks run from a machine that can reach the project.
- **Expected outcome once unblocked:** `bcf58e1` cannot be VERIFIED as is, because F4 (MAINTAIN) is open on the hosted engine. Unless the owner explicitly accepts F4 as a documented risk, the path is a small follow-up candidate (migration 006 plus PostgreSQL 17 in CI), then rerun 2c and 2d against it.
