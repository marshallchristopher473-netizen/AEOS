# P0 Stage A — security-only release candidate

**Status: candidate for independent review. This is not P0 approval.** P0 stays
OPEN until a separate verifier reproduces this candidate from its exact pushed
SHA (`.github/agents/aeos-p0-independent-verifier.agent.md`). Live Supabase RLS
and hosted-login evidence are **not** part of this candidate and remain
BLOCKED (see "Remaining blockers").

Exact SHAs, test totals and the mutation matrix for this candidate are recorded
in its pull request and in the CI artifacts keyed to the head SHA. They are kept
out of this file on purpose: a total written into the tree describes only the
tree it was measured on.

## Source coordinates

Refreshed from the remote before any edit:

| Ref | SHA |
| --- | --- |
| `origin/main` (base) | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` |
| PR #20 head | `0aefabcd752797e341577f2c027e54df4f005e9b` |
| PR #22 head | `e7de87d7d5d0c2656d20d46fc2b09834fec0042e` |
| PR #23 head | `3fb76752642d8d6f9e3e99a8a1b79784d9d4b4f2` |
| PR #24 head (on #23) | `f211c9691b0d6eca5884461dd519e751c2e4fc9d` |
| PR #25 head (on #24) | `6453ae17bce3cd01aa9263b30ef56ee8e6210969` |

`AEOS_P0_V04_Independent_Check_2026-10-07.md` was not found in any git ref,
pull-request or issue comment, or the connected Drive. This candidate was built
from the audit's summary of it. A verifier holding that file should check each
V04 finding against the control manifest below.

## Source-to-control manifest

| Control | Source | Files | Killing tests (examples) | Mutations |
| --- | --- | --- | --- | --- |
| Client roles hold no TRUNCATE/TRIGGER/REFERENCES on existing tables | #20 `a33155b` | `005_revoke_rls_blind_table_privileges.sql` | `TestPrivilegesRlsDoesNotGovern::*`, `TestTruncateCascadeAndFutureTables::test_truncate_cascade_*` | M19a, M19d |
| …nor on tables created later, for every creator, global and per-schema defaults | #20 `a33155b`; scope tests added here | `005_…sql`, `test_rls_enforcement.py` | `test_tables_created_later_*`, `test_tables_created_by_every_authorized_creator_*`, `test_no_default_privilege_entry_*` | M19b, M19c |
| Test DB privileges come from default privileges, not a blanket re-grant | #20 `a33155b` | `tests/sql/supabase_shim.sql`, `test_rls_enforcement.py` fixture | `test_authenticated_keeps_every_dml_grant_rls_governs` (positive control) | — |
| WHERE-less UPDATE/DELETE cannot reach another tenant on any table | #20 `2eb0507` | `test_rls_enforcement.py` | `TestWherelessWritesAcrossEveryTable::*` | M20 |
| Any JOSE error fails closed as 401 (SEC-G1-06) | #20 `2eb0507` + #22 `e7de87d` | `app/core/auth.py` | `test_published_key_python_jose_cannot_load_is_401_not_a_server_error` | M18g, M18h |
| Published key pins one algorithm: RSA→RS256, EC P-256→ES256; `oct`, OKP, P-384 refused | #22 `a87e511`, `e7de87d` | `app/core/auth.py` (`signing_algorithm`, `construct_jwk`) | `test_symmetric_key_in_the_jwks_is_never_accepted`, `test_algorithm_the_published_key_does_not_allow_is_401[*]`, `test_published_key_this_backend_must_not_use_*[*]` | M18i, M18j, M18k |
| JWKS URL defaults to Supabase's documented discovery endpoint | #22 `9a3ccd4` | `app/core/config.py`, `.env.example` | `test_config.py::test_default_jwks_url_*` | — |
| Tokens without `exp` are rejected | **new here** | `app/core/auth.py` | `test_token_with_no_expiry_claim_is_401` | M18l |
| Cached key set expires; revoked keys stop verifying; failed refresh fails closed | **new here** | `app/core/auth.py` | `test_revoked_signing_key_is_refused_once_the_cached_key_set_expires`, `test_expired_key_set_is_not_used_when_its_refresh_fails`, `test_cached_key_set_is_reused_within_its_max_age` | M18m |
| Complete `tests/` runs against PostgreSQL 16 with zero skips | **new here** | `.github/workflows/p0-backend-tests.yml` | CI step "Require zero failed, errored or skipped tests" | — |
| Frontend dependencies audit clean at `low`, full and production, no exceptions | #23 `9545537`, #24 `f211c96`, #25 `6453ae1`; refreshed here | `frontend/package.json`, `package-lock.json`, workflow | CI audit steps | — |
| Lint-plugin glob override stays safe | #24 `f211c96` | `frontend/tests/lint-glob-override.test.mjs`, workflow | 3 guards: resolution/API, `rootDir` unset, rule still fires | — |

Every control from main (M01–M18g) is retained unchanged.

### Deliberately not imported

| Delta | Source | Reason |
| --- | --- | --- |
| `frontend/audit-exceptions.json`, `.github/scripts/check-npm-audit.mjs`, split dated-exception audit | #20 `0aefabc` | An audit exclusion. This candidate keeps the full `--audit-level=low` gate with no exceptions file. |
| #20's frontend lockfile | #20 `0aefabc` | Superseded: the #25 lockfile, refreshed below, clears the same and later advisories without exceptions. |
| `docs/P0_G1_EVIDENCE_PACKET.md`, `docs/evidence/g1/*` | #20 | Evidence frozen for a different SHA (`54a0477`). Its totals do not describe this tree. |
| Teacher review UI, API/schema changes, `review_fixture_server.py`, `browser_review.py`, `assessment-api.test.mjs`, `next.config.mjs` rewrites, `frontend/.env.example`, README/replit edits | #23 | Stage B product work, not security. |
| `docs/DEPENDENCY_SECURITY_REVIEW.md` | #23–#25 | Mixed with #23's review-flow context; its dependency findings are carried into the inventory below. |

## Composition decisions

1. **`auth.py` conflicts (2).** Import block: `construct_jwk` (#22) kept beside
   `JOSEError` (both). Exception comment: #20's text said the failing key "is
   not an RSA key", which is no longer true once #22 accepts EC P-256; #22's
   wording kept, with #20's `SEC-G1-06` tag.
2. **M18h killer reassigned, not lost.** Under #22's key policy, #20's
   `test_unusable_published_key_is_401_not_a_server_error[*]` no longer reaches
   `JWKError`: EC P-256 is now a supported type and `oct` is refused before
   python-jose. That test still passes (both cases are 401), but applying M18h to
   the composed tree shows it is killed only by #22's
   `test_published_key_python_jose_cannot_load_is_401_not_a_server_error`. The
   test's id and docstring and the contract table were updated to say so.
3. **Shared mutation anchors.** M18g's anchor changed identically in #20 and
   #22 and merged cleanly. Every mutation anchor is asserted by the harness to
   match exactly one site; none is stale.
4. **Expiry check placement.** Inserting into the `options={...}` dict would
   have broken the M02 and M18c anchors, and python-jose's `require_exp`
   forces `verify_exp` on, making M18a undetectable. The check is therefore an
   explicit post-decode test, outside every existing anchor.

## Item 4 — expiry and key-trust reproduction

Reproduced on **unmodified main** with synthetic RSA keys and an in-process
JWKS transport:

| Case | main `b9c68aa` | this candidate |
| --- | --- | --- |
| Validly signed token with no `exp` | **ACCEPTED** | 401 |
| Token with `exp` in the past | 401 | 401 |
| Key published, token valid (positive control) | accepted | accepted |
| New key after rotation (positive control) | accepted | accepted |
| Key removed from the JWKS, process up 24 h with no unknown-`kid` traffic | **ACCEPTED** | 401 |

Both violate the existing contract ("JWT verification enforces … expiration …
and unknown-key rejection"). Fixes: an explicit `exp`-presence check, and a
600 s maximum age for the cached key set. HS256 was not enabled.

The refresh-on-unknown-`kid` path is unchanged: each request with an unknown
`kid` still triggers one JWKS fetch. That can be used to generate outbound
JWKS traffic; it does not grant access. Rate-limiting it is left as follow-up
because it would delay acceptance of a newly rotated key.

## Asymmetric-key deployment prerequisites

These are requirements of the code in this candidate. None has been exercised
against a hosted Supabase project.

1. The Supabase project must sign sessions with an **asymmetric** key: ECC
   P-256 (ES256) or RSA (RS256). A project still on the legacy HS256 shared
   secret publishes no usable key, so every token is refused with 401. That is
   intended; do not enable HS256 to work around it.
2. `SUPABASE_URL` must be set (or `SUPABASE_JWKS_URL` and `SUPABASE_JWT_ISSUER`
   explicitly). Defaults: JWKS `<SUPABASE_URL>/auth/v1/.well-known/jwks.json`,
   issuer `<SUPABASE_URL>/auth/v1`, audience `authenticated`.
3. The backend needs outbound HTTPS to the JWKS URL. If a due refresh fails,
   requests fail with 503 until it succeeds.
4. Tokens must carry `kid`, `exp`, `aud`, `iss` and a non-empty `sub`. Each
   published key may declare only the `alg` its type maps to.
5. Rotation: publish the new key before switching signing to it. After a key is
   revoked, this backend refuses its tokens within at most
   `JWKS_MAX_AGE_SECONDS` (600 s) of its own cache, plus whatever caching sits
   in front of the JWKS endpoint (not measured).
6. No clock-skew leeway is configured; host clocks must be synchronised.

## Item 5 — TRUNCATE CASCADE and future tables

- Every client role (`anon`, and `authenticated` as organization B's teacher)
  issues the exact `TRUNCATE public.<table> CASCADE` against each of the 11
  public tables. Each must be refused with `InsufficientPrivilege`, and every
  row of every table must survive. All 11 tables carry rows during the attempt,
  and counting happens in the same rolled-back transaction, so a breach would
  be visible rather than merely "no exception".
- Negative control: with TRUNCATE granted back inside the transaction, the
  same `TRUNCATE organizations CASCADE` empties all 11 tables for both roles.
- Future tables: for **every** role able to create in `public` (superuser or
  `CREATE` on the schema), a probe table is created as that role and the client
  roles must hold no TRUNCATE/TRIGGER/REFERENCES on it. Separately, every
  `pg_default_acl` entry for tables, for any role, **global or for `public`**,
  must withhold those privileges from the client roles. A global entry matters
  on its own because a per-schema REVOKE cannot remove what it grants.
- In the PostgreSQL 16 model the only creator is `postgres` and the only
  default-ACL entry is its `public` entry, which 005 narrows; no violation was
  found, so no migration was added.

**Deployment check (read-only)**, to run on the target Supabase project before
any pilot. Any returned row means a role's future tables would hand a client
role a privilege RLS does not govern, and 005 alone does not cover it:

```sql
SELECT d.defaclrole::regrole AS creator,
       COALESCE(d.defaclnamespace::regnamespace::text, '<global>') AS scope,
       grantee.rolname AS grantee,
       acl.privilege_type
FROM pg_default_acl d
CROSS JOIN LATERAL aclexplode(d.defaclacl) acl
JOIN pg_roles grantee ON grantee.oid = acl.grantee
WHERE d.defaclobjtype = 'r'
  AND (d.defaclnamespace = 0 OR d.defaclnamespace = 'public'::regnamespace)
  AND grantee.rolname IN ('anon', 'authenticated')
  AND acl.privilege_type IN ('TRUNCATE', 'TRIGGER', 'REFERENCES');
```

Hosted Supabase may have creators beyond `postgres` (for example
`supabase_admin`) whose defaults the migrating role cannot alter. That has not
been observed here and cannot be fixed from a migration run as `postgres`.

## Dependency inventory and dispositions

### Frontend (`npm audit`, Node 22.22.0, npm 10.9.4)

| Package | Advisory | Path | Disposition |
| --- | --- | --- | --- |
| `next` 16.3.6 (from #25) | GHSA-3w37-wq28-93x7, GHSA-4jqv-mc3x-m676, GHSA-39w2-rjm5-chcv, GHSA-f87g-xv8r-7p7x, GHSA-mcj8-r9mp-w47p, GHSA-cjq9-62q9-8jv4 (range 16.0.0–16.3.7) | direct, production | **Fixed**: lock `16.3.8`; manifest floor raised to `^16.3.8`. Not `16.4.0`, which `^16.3.8` alone resolved to. |
| `sharp` 0.35.4 | GHSA-wq5f-xc86-pv6w (`<0.35.5`) | `next` optional dependency, production | **Fixed**: `0.35.5`, inside `next`'s `^0.35.4`, via `npm audit fix --package-lock-only` (no `--force`). |
| `braces` chain | GHSA-vfj7-8cjw-p6xm | dev, lint plugin | **Removed** by #24's scoped `fast-glob → tinyglobby@0.2.17` override, retained. |
| `source-map-js` | GHSA-68fv-2mgg-jv7q | `next → postcss` | **Fixed** by #25 (`1.2.2`), retained. |

After the change both `npm audit --audit-level=low` and
`npm audit --omit=dev --audit-level=low` report 0 vulnerabilities. Lockfile
changes relative to #25 are confined to `next`, its `@next/env` and
`@next/swc-*` binaries, and `sharp` with its `@img/*` binaries.

### Backend (`pip-audit -r requirements.txt`; `requirements-dev.txt` adds no findings)

| Package | Advisory | Reachability here | Disposition |
| --- | --- | --- | --- |
| `python-jose` 3.3.0 | CVE-2024-33663 (HMAC/ECDSA key confusion), CVE-2024-33664 (JWE decompression DoS) | Not reachable: algorithm pinned per key, keys built from JWK dicts, HS256 never allowed, JWE not used | **Upgraded** to 3.5.0 (compatible with installed `pyasn1` 0.6.4; 3.4.0 would have forced `pyasn1<0.5`). |
| `python-jose` 3.5.0 | GHSA-3qf3-8w2g-rqmx / CVE-2026-85394 (DER public key accepted as HMAC secret "when algorithms are not explicitly restricted"); no fixed release | Not reachable for the same reasons; pinned by the new `hs256-keyed-with-the-rsa-public-key-der` case | **Open, no fix**. Revisit on a python-jose release, or by moving to a maintained JOSE library. |
| `python-jose` 3.3.0 | CVE-2024-29370 (`jwe.decrypt`) | JWE not used | No longer reported after the upgrade to 3.5.0. |
| `python-dotenv` 1.0.1 | CVE-2026-28684 (`set_key`/`unset_key` follow symlinks) | Not reachable: only `load_dotenv` is called | **Upgraded** to 1.2.2 (drop-in). |
| `starlette` 0.38.6 (via `fastapi` 0.115.0) | CVE-2024-47874, CVE-2025-54121, CVE-2026-54283 (multipart forms) | Not reachable: `python-multipart` is not installed and no route parses forms | **Open.** Fix needs a `fastapi` release that permits `starlette` ≥ 1.3.1 (the latest, 0.143.0, also requires `pydantic` ≥ 2.9; the minimum such release was not established) — a framework upgrade, kept out of this security-only candidate. |
| `starlette` 0.38.6 | CVE-2026-48710 (Host header), CVE-2026-54282 (path) — `request.url` can diverge from the routed path | No application code reads `request.url`; auth uses the `Authorization` header and routing uses the raw path | **Open**, same upgrade. Needed before the API is exposed behind any proxy that does not normalise `Host`. |
| `starlette` 0.38.6 | CVE-2026-48817 (`HTTPEndpoint`), CVE-2026-48818 (`StaticFiles`, Windows) | Neither is used | **Open**, same upgrade. |
| `ecdsa` 0.19.2 | CVE-2024-23342 (Minerva timing on signing) | Not reachable: the backend only verifies; verification is unaffected, and python-jose uses the `cryptography` backend | **Open, no fix** (upstream will not fix). |

## Independent check of #24's glob divergence

The plugin's only `fast-glob` use is `globSync(..., { onlyDirectories: true })`
in `dist/utils/get-root-dirs.js`, reached only when `settings.next.rootDir` is a
string or array; otherwise `rootDirs = [context.cwd]`. Compared directly
(`fast-glob@3.3.1` vs `tinyglobby@0.2.17`, synthetic tree):

| Pattern | fast-glob | tinyglobby |
| --- | --- | --- |
| `apps/*`, `apps/*/`, `packages/*/lib` | same | same |
| `src/` | `src/` | `src` + every subdirectory |
| `src` (no slash), `.` | the directory itself | the directory + every subdirectory |
| `apps/**` | subdirectories | subdirectories + `apps` |

#24 documents the `src/` and `**` cases. The plain-directory case (`src`,
`.`), the most common `rootDir` form, also diverges. The conclusion holds:
the guard that `settings.next.rootDir` stays unset keeps the override
behaviour-neutral. Anyone setting `rootDir` must remove the override first.

## Validation commands

```bash
# backend (Python 3.11, fresh venv, disposable PostgreSQL 16)
pip install -r backend/requirements-dev.txt
python -m compileall -q backend/app backend/tests
(cd backend && python -c "from app.main import app; print('backend OK')")
(cd backend && AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres \
   AEOS_REQUIRE_RLS_TESTS=1 python -m pytest tests/ -v -rs)
(cd backend && AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres \
   python -m tests.security_mutations --json mutation-matrix.json)

# frontend (Node 22)
cd frontend && npm ci && npm audit --audit-level=low && npm audit --omit=dev --audit-level=low \
  && npm ls --all && node tests/lint-glob-override.test.mjs && CI=1 npm run lint \
  && npx tsc --noEmit && npm run build
```

## Remaining blockers

| Gate | State | Needed |
| --- | --- | --- |
| Independent verification of this SHA | NOT STARTED | Verifier per `aeos-p0-independent-verifier.agent.md` |
| Live Supabase RLS / cross-tenant attacks | BLOCKED | An isolated non-production Supabase project with synthetic tenants |
| Hosted asymmetric-key login | BLOCKED | Same project, signing with ES256 or RS256 |
| Default-privilege check on the hosted project | BLOCKED | Run the query above on that project |
| starlette advisories | OPEN | Separate, bounded `fastapi`/`pydantic` upgrade candidate |
| Vercel preview status | Pre-existing, not this candidate | Project setting (Root Directory = `frontend`), owner's call |

## Rollback

This candidate is unmerged. If it is merged and must be reverted:

- **Application and tests:** `git revert` the merge commit. Nothing outside
  `backend/`, `frontend/`, `docs/` and the workflow changes.
- **Migration 005** is privilege-only and forward-only. If it has been applied
  and must be undone, use a new forward migration that re-grants exactly what
  005 revoked (`GRANT TRUNCATE, TRIGGER, REFERENCES ON ALL TABLES IN SCHEMA
  public TO anon, authenticated;` plus the matching `ALTER DEFAULT PRIVILEGES`).
  Doing so re-opens the cross-tenant TRUNCATE wipe; do not do it on a database
  holding real data.
- **Frontend dependencies:** restore the previous `package.json` and
  `package-lock.json` and run `npm ci`. That re-introduces the advisories above.
