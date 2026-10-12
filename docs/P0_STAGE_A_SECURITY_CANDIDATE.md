# P0 Stage A — Security-Only Release Candidate

**Status:** candidate for independent review. This is **not** P0 approval.
P0 stays OPEN until a separate verifier reproduces this candidate from its exact
pushed SHA and the hosted gates in section 8 have run.

The exact candidate SHA and tree are recorded in the pull request, not here: a
commit cannot contain its own hash.

## 1. Source coordinates (fetched 2026-10-11, all re-verified with `git fetch`)

| Source | Commit | Used for |
| --- | --- | --- |
| `main` (base) | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` | branch base |
| PR #20 security repair | `0aefabcd752797e341577f2c027e54df4f005e9b` | migration 005, RLS-blind and WHERE-less coverage, `JOSEError` handling |
| PR #22 signing-key repair | `e7de87d7d5d0c2656d20d46fc2b09834fec0042e` | key-bound RS256/ES256 verification, JWKS default URL, mutation tests |
| PR #23 teacher review | `3fb76752642d8d6f9e3e99a8a1b79784d9d4b4f2` | **nothing taken** (review UI and its CI steps excluded) |
| PR #24 tooling repair | `f211c9691b0d6eca5884461dd519e751c2e4fc9d` | lint-plugin glob override and its guard test |
| PR #25 dependency repair | `6453ae17bce3cd01aa9263b30ef56ee8e6210969` | `package.json` and lockfile, then refreshed (section 4) |

`AEOS_P0_V04_Independent_Check_2026-10-07.md` was not found on `main`, on any PR
head fetched above, or in issue #1, so it could not be read. The V04 FAIL and
V05 NOT REACHED status is taken from the task brief.

## 2. Source-to-control manifest

| Control | Source | Files | Proof |
| --- | --- | --- | --- |
| C1 TRUNCATE, TRIGGER, REFERENCES revoked from `anon` and `authenticated`, now and by default (forward-only) | #20 | `migrations/005_revoke_rls_blind_table_privileges.sql`, `tests/sql/supabase_shim.sql` | `TestPrivilegesRlsDoesNotGovern`, `TestTruncateCascadeAndFutureTables`; M19a–M19d |
| C2 WHERE-less UPDATE/DELETE cannot reach another tenant on any table | #20 | `tests/test_rls_enforcement.py` | `TestWherelessWritesAcrossEveryTable`; M20 |
| C3 Every JOSE error on the verification path fails closed with 401 | #20 + #22 (overlapping) | `app/core/auth.py` | `test_published_key_python_jose_cannot_load_is_401_not_a_server_error`; M18g, M18h |
| C4 Algorithm pinned by the published key (RSA→RS256, EC P-256→ES256); symmetric and other keys refused; key built with `construct_jwk` | #22 | `app/core/auth.py` | M18i–M18k and the ES256 tests |
| C5 JWKS default is Supabase's documented `/.well-known/jwks.json` | #22 | `app/core/config.py`, `.env.example` | `tests/test_config.py` |
| C6 `exp` claim required | **new (this candidate)** | `app/core/auth.py` | `test_token_with_no_expiry_claim_is_401`; M18l |
| C7 Key set refetched once 600 s old; a failed due refresh fails closed (503) | **new (this candidate)** | `app/core/auth.py` | 3 freshness tests; M18m, M18n |
| C8 Patched python-jose / python-dotenv | **new (this candidate)** | `requirements.txt` | section 5 |
| C9 Frontend: zero advisories, full and production; glob override guarded | #24, #25, then refreshed | `frontend/package.json`, `package-lock.json`, `tests/lint-glob-override.test.mjs` | section 4 |
| C10 CI runs the complete unmodified `tests/` against PostgreSQL 16 with a zero-skip gate, plus full and production audits | **new (this candidate)** + #24/#25 audit steps | `.github/workflows/p0-backend-tests.yml` | CI on the PR |

### Composition notes

- **Auth conflicts.** A three-way merge of `auth.py` (base `main`, sides #20 and
  #22) produced exactly the two reported conflicts. (1) Imports: `construct_jwk`
  is kept, because #22's verifier uses it. (2) The comment on the `except`
  clause: #22's wording is kept with #20's `SEC-G1-06` reference, because #20's
  "not an RSA key" no longer describes the code. Both sides catch
  `(JOSEError, ValueError, TypeError)`. `security_mutations.py`, `test_auth.py`
  and `P0_MUTATION_VERIFICATION.md` merged without conflicts.
- **No suite was replaced.** The composed test IDs are a strict superset of
  #20's (297) and #22's (188): 315 tests after composition, with none of either
  side's tests missing. All 37 composed mutations (30 from main, 4 from #20,
  3 from #22) were killed before any new work.
- **Stale descriptions updated.** Per-key pinning means
  `test_unusable_published_key_is_401_not_a_server_error` (#20) no longer reaches
  `JWKError`: the EC key now pins ES256, and the symmetric key is refused before
  python-jose sees it. Its docstring and parameter id were corrected, and the
  M18h row now names the test that actually kills it
  (`test_published_key_python_jose_cannot_load_is_401_not_a_server_error`, from
  #22), as the mutation matrix confirms.
- **Excluded from #20:** `.github/scripts/check-npm-audit.mjs` and
  `frontend/audit-exceptions.json`. That mechanism is a dated audit exclusion.
  #24 removed the advisory it excepted, and this candidate keeps the full audit
  threshold with no exceptions file. Also excluded: the G1 evidence packet and
  its JSON, because they describe a different tree.
- **Excluded from #23–#25:** the review UI, `next.config.mjs` rewrites,
  `frontend/.env.example`, the schema and service changes, the assessment-API
  test, the browser fixture and its CI steps, and the README/doc rewrites.

## 3. Expiry and key-trust reproduction (before → after)

Probe: the real `get_current_user` and `get_jwks`, with only the HTTP transport
replaced.

| Case | Composed #20 + #22 | This candidate |
| --- | --- | --- |
| Valid RS256 token | accepted | accepted |
| Validly signed token with **no `exp`** | **accepted** | 401 `JWT is missing the expiry claim` |
| Key removed from the JWKS, cache under 600 s old | accepted | accepted (the designed bounded window) |
| Same key, cache over 600 s old | **accepted indefinitely** | 401 `JWT signing key is unknown` |
| Due refresh fails | n/a | 503, with no fallback to the expired set |
| 50 requests with random `kid`s | 51 JWKS fetches, all 401 | 51 JWKS fetches, all 401 (**F2 open**, section 7) |

## 4. Frontend dependency inventory

The lockfile from #25 was **stale on 2026-10-11**: `npm audit` reported 2 high
advisories (next 16.0.0–16.3.7: GHSA-3w37-wq28-93x7, -4jqv-mc3x-m676,
-39w2-rjm5-chcv, -f87g-xv8r-7p7x, -mcj8-r9mp-w47p, -cjq9-62q9-8jv4; sharp
<0.35.5: GHSA-wq5f-xc86-pv6w). The fix used no `--force` and no exclusion:
`next` was bumped to `^16.3.8` (the smallest patched release), and a plain
`npm audit fix` moved `sharp` to 0.35.5 within next's declared `^0.35.4` range.
Only `next`, `@next/*`, `sharp` and `@img/*` versions changed in the lockfile,
and no package was added.

The #24 lint-plugin override (`fast-glob` → `tinyglobby@0.2.17`) was inspected
independently. The plugin calls `globSync` only in
`dist/utils/get-root-dirs.js`, and only when `settings.next.rootDir` is set. A
side-by-side probe confirms that the documented divergence is real. tinyglobby
appends `/` to directory results, expands `.` to every subdirectory, and
includes the parent directory for `dir/**`. The substitution is therefore
equivalent only while `rootDir` is unset, which is exactly what
`lint-glob-override.test.mjs` pins, together with the plugin's API surface and a
live `no-html-link-for-pages` report.

## 5. Backend dependency inventory (pip-audit over a fresh `pip install -r requirements-dev.txt`)

| Package | Before → after | Advisories | Disposition |
| --- | --- | --- | --- |
| python-jose | 3.3.0 → **3.5.0** | CVE-2024-33663 (algorithm confusion), CVE-2024-33664 (JWE bomb) | **Fixed** by the upgrade |
| python-jose | 3.5.0 | CVE-2026-85394 / GHSA-3qf3-8w2g-rqmx (HS256 forged with a DER public key "when algorithms are not explicitly restricted"), no fix released | **Not exploitable here:** `algorithms=[pinned]` is never HS256, and the key is built for the pinned algorithm. Pinned by `test_algorithm_the_published_key_does_not_allow_is_401[hs256-keyed-with-the-rsa-public-key]` and M18i/M18j |
| python-jose | 3.3.0 | PYSEC-2025-185 (`jwe.decrypt` DoS), no fix | JWE is never used. No longer reported on 3.5.0 |
| python-dotenv | 1.0.1 → **1.2.2** | CVE-2026-28684 (`set_key` symlink) | **Fixed.** Only `load_dotenv` is used |
| ecdsa | 0.19.2 | CVE-2024-23342 (Minerva timing, signing only), no fix planned | **Not applicable:** the backend only verifies, and the advisory states verification is unaffected |
| starlette | 0.38.6 (pinned by fastapi 0.115.0) | CVE-2024-47874, CVE-2025-54121, CVE-2026-48710, -48817, -48818, -54282, -54283 | **Deferred, not reachable today:** no route parses forms (python-multipart is not installed), nothing reads `request.url` or its hostname, and nothing uses `HTTPEndpoint` or `StaticFiles`. The fix needs starlette ≥1.3.1, and with it a FastAPI framework upgrade. A trial on fastapi 0.135.1 + starlette 1.7.0 resolved cleanly and passed **319/319** tests (pre-TRUNCATE-coverage tree). Recommended as its own PR **before any pilot**, not inside this security RC |

## 6. Validation commands

Environment: Python 3.11.17 fresh venv, Node 22.22.0, npm 10.9.4, throwaway
PostgreSQL 16.15 cluster on `localhost:55432`. Synthetic data only.

| Command | Exit | Result |
| --- | --- | --- |
| `pip install -r backend/requirements-dev.txt` (fresh venv) + `pip check` | 0 | no broken requirements |
| `python -m compileall -q backend/app backend/tests` | 0 | |
| `from app.main import app` / schemas / dependencies imports | 0 | |
| `AEOS_REQUIRE_RLS_TESTS=1 pytest tests/` (PG 16.15) | 0 | **350 passed, 0 failed, 0 errors, 0 skipped** (JUnit) |
| `python -m tests.security_mutations --json …` | 0 | **42/42 killed**: 0 survived, 0 invalid, 0 equivalent, 0 not executed |
| `npm ci` | 0 | |
| `npm audit --audit-level=low` / `--omit=dev` | 0 / 0 | 0 vulnerabilities / 0 vulnerabilities |
| `npm ls --all` | 0 | |
| `node tests/lint-glob-override.test.mjs` | 0 | 3 pass, 0 fail |
| `CI=1 npm run lint` / `npx tsc --noEmit` / `npm run build` | 0 / 0 / 0 | |

Counts describe this tree only. They are not additive with the totals of #20,
#22, #27 or any other tree.

### Mutation manifest (42 scored mutants)

| Group | IDs | Count |
| --- | --- | --- |
| Inherited from `main` | M01–M17 (M09 ×4, M10 ×2, M15 ×2, M17 ×2), M18a–M18g | 30 |
| From #20 | M18h, M19a, M19b, M20 | 4 |
| From #22 | M18i, M18j, M18k | 3 |
| New: expiry and key-set freshness | M18l, M18m, M18n | 3 |
| New: `anon` RLS-blind privileges | M19c, M19d (M19d is killed **only** by the new anon future-table tests) | 2 |
| **Total** | 36 contract IDs | **42** |

The authoritative per-mutant list, with killing tests, is the
`mutation-matrix-<sha>` CI artifact for the candidate SHA.

### New tests (31 in `test_rls_enforcement.py`, 4 in `test_auth.py`)

- `TestTruncateCascadeAndFutureTables` checks that every table holds rows (a
  precondition, which caught 4 empty tables before they were seeded). It also
  covers:
  - exact `TRUNCATE public.<t> CASCADE` as **anon** and **authenticated** for
    all 11 tables, with row counts of **every** table unchanged (22 cases);
  - one `TRUNCATE <all 11> RESTART IDENTITY CASCADE` per role (2);
  - a negative control showing that the wipe is observable once the privilege
    is restored;
  - client roles lack `CREATE` on `public` (2);
  - no `pg_default_acl` table entry, global or `public`-scoped, for **any**
    creator grants D/x/t to a client role;
  - a behavioural check that every role able to create in `public` makes a
    table, and that each client role holds no RLS-blind privilege on it while
    keeping DML (2).
- `test_auth.py` adds the missing-`exp` test and three key-set freshness tests,
  one of which is a positive control.

## 7. Remaining blockers and risks

| ID | Item | Severity | Status |
| --- | --- | --- | --- |
| G2c | Hosted two-tenant attack, TRUNCATE … CASCADE denial and row survival against an isolated Supabase project | — | **BLOCKED**: needs an approved isolated project. This session's network policy denies `*.supabase.co` |
| G2d | Asymmetric (ES256) JWT accepted or rejected by real Supabase Auth | — | **BLOCKED**: same network restriction |
| F4 | PostgreSQL 17 `MAINTAIN` held by `anon`/`authenticated` on hosted (PR #29 §6.3). It is RLS-blind (LOCK/VACUUM/REINDEX) | Blocking for P0 VERIFIED | **OPEN.** Not reproducible on PG16, where the privilege does not exist. Needs a forward-only, version-guarded migration 006 plus a PostgreSQL 17 CI service. Out of the requested PG16 scope; owner decision |
| F3 | `supabase_admin`'s default ACL on hosted grants D/x/t to client roles (PR #29 §6.3) | Owner decision | **OPEN.** Migrations run as `postgres` cannot change it. The new default-ACL test would flag it on any database where that entry exists. Run the hosted query below |
| F1 | `anon` holds EXECUTE on the SECURITY DEFINER helpers on hosted (PR #29 §4) | Low | OPEN. No data exposure measured |
| F2 | An unknown `kid` forces an unthrottled JWKS refetch | Medium (availability) | OPEN. Fix before any public pilot (cooldown on forced refresh) |
| D1 | starlette advisories (section 5) | Not reachable today | Deferred to a FastAPI upgrade PR before pilot |
| R1 | FastAPI data routes use the service-role client, which bypasses RLS. API-path isolation rests on `tenant_scope` and is tested against a fake DB | Pre-existing | Gate 2 must attack both PostgREST and the API |

Hosted read-only inventory for the verifier:

```sql
SELECT pg_get_userbyid(defaclrole), defaclnamespace::regnamespace, defaclobjtype, defaclacl
FROM pg_default_acl;                                            -- F3
SELECT has_schema_privilege(r, 'public', 'CREATE') FROM unnest(ARRAY['anon','authenticated']) r;
SELECT c.relname, has_table_privilege('authenticated', c.oid, 'MAINTAIN')
FROM pg_class c WHERE c.relnamespace = 'public'::regnamespace AND c.relkind = 'r';  -- F4 (PG17)
```

## 8. Asymmetric-key deployment prerequisites (HS256 is never enabled)

1. The Supabase project must have **asymmetric JWT signing keys** enabled
   (Dashboard → Project Settings → JWT Keys), with the current key ECC P-256
   (ES256, recommended) or RSA (RS256). A project that still signs with the
   legacy HS256 shared secret publishes no usable key, so every token is
   refused as signed by an unknown key. This is intended. Do not add HS256 or
   the JWT secret to the backend.
2. Backend environment: `SUPABASE_URL` (the JWKS URL and issuer derive from it),
   or explicit `SUPABASE_JWKS_URL=<project>/auth/v1/.well-known/jwks.json` and
   `SUPABASE_JWT_ISSUER=<project>/auth/v1`, plus `SUPABASE_JWT_AUDIENCE=authenticated`.
3. The backend host must reach `<project>.supabase.co` over HTTPS. If it cannot,
   every authenticated request fails closed with 503.
4. Key rotation: publish the new key (stand-by) before rotating. A revoked key
   keeps verifying for at most `JWKS_MAX_AGE_SECONDS` (600 s) after revocation.
5. Migrations 001–005 applied in order, as `postgres`.

## 9. Rollback plan

Nothing is merged or deployed. Rollback before merge means closing the draft
PR. If the candidate were later merged:

- **Code and dependencies:** revert the merge commit. No data migration is
  involved.
- **Migration 005:** do **not** delete it from history. It only revokes
  privileges, so it never needs reversing for correctness. If it must be undone
  on a disposable project, use a new forward migration:
  `GRANT TRUNCATE, TRIGGER, REFERENCES ON ALL TABLES IN SCHEMA public TO anon, authenticated;`
  plus the matching `ALTER DEFAULT PRIVILEGES … GRANT`. This reopens SEC-G1-10,
  so it is for disposable projects only.
- **Auth:** reverting C6/C7 restores accepting tokens without `exp` and
  indefinite trust of revoked keys. Revert only together with the whole
  candidate.
