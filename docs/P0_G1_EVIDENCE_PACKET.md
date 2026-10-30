# P0 G1 evidence packet — exact-SHA verification of PR #17

This packet records the independent reproduction of the AEOS P0 security
candidate for pilot gate **G1 (P0 security)**. It is an evidence record, not a
certification. It contains facts observed on the exact artifact, then findings,
then one recommendation. Nothing in the candidate was modified to produce it.

## G1 recommendation

**G1 for `54a0477`: REVISE.**

> **Correction, 2026-09-28.** This packet was first issued on 2026-09-26 as
> *BLOCKED on one evidence item only*, stating that no control had been shown
> to fail. That was wrong. A follow-up check found a tenant-boundary control
> gap the first issue missed: **SEC-G1-10**. Client roles hold `TRUNCATE`,
> which row-level security does not govern, and a teacher in organization B
> emptied organization A's students with it. The evidence from the first issue
> below is unchanged and still accurate for what it measured. Section 11
> records the finding, why it was missed, and the proposed fix.

Two things stand between this candidate and PASS:

1. **SEC-G1-10 must be fixed and independently re-verified.** A fix (migration
   005) is proposed alongside this packet. It was written by the same session
   that found the defect, so under the repository's verifier contract a
   separate fresh session must reproduce it at the fix's exact SHA.
2. **SEC-G1-01 stays BLOCKED** until the founder authorizes an isolated,
   non-production Supabase project. The live run should use the fixed SHA, so
   it only has to run once.

| G1 evidence item | Result |
| --- | --- |
| Provenance: candidate pinned, reachable, same tree as `main` | PASS |
| CI on the exact candidate SHA | PASS |
| Frontend verification at the exact SHA (the item the gate board listed as remaining) | PASS |
| Frontend static security review | PASS, with 5 non-critical findings |
| Backend suite against real PostgreSQL 16, required mode | PASS — 170 passed, 0 skipped |
| M01–M18 mutation contract | PASS — 30 killed / 30, 0 survived |
| WHERE-less UPDATE/DELETE sweep across all 11 RLS tables (new) | PASS — 102 probes, 0 breaches |
| **Table privileges RLS does not govern (TRUNCATE)** | **FAIL — SEC-G1-10, cross-tenant wipe reproduced** |
| Live RLS against an isolated hosted Supabase project | **BLOCKED — not run, needs founder authorization** |

**What this stops:** G4 staging on hosted Supabase, and any exposure beyond
synthetic data. **What it does not stop:** the G2, G3, G5 and G6 preparation
the operating model already allows to run in parallel.

**Smallest unblocking actions:** (a) a fresh session independently verifies the
SEC-G1-10 fix; (b) the founder authorizes one isolated, non-production Supabase
project (or a Supabase branch) that holds synthetic data only. The verifier
then applies migrations 001–005 there and runs the same cross-tenant attack
set, TRUNCATE included, through PostgREST with real Supabase-issued tokens.

## Artifact identity

| Field | Value |
| --- | --- |
| Repository | `marshallchristopher473-netizen/AEOS` |
| Pull request | #17, merged into `main` 2026-09-25 by the repository owner |
| Baseline (`main` before PR #17) | `679d0707dbf94a1b9cbadb292a24457093a234ae` |
| **Candidate (exact tested SHA)** | **`54a04773fd8aa73547f49d125bf3b6b0ec08caf2`** |
| Merge commit on `main` | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` |
| Candidate tree | `df6e6d6047f725035af6c7aadd1c4852aeb5f326` |
| Merge commit tree | `df6e6d6047f725035af6c7aadd1c4852aeb5f326` — identical |
| Verification date | 2026-09-26 |
| Verifier | A separate Claude Code session, not the builder session |

Because the merge commit's tree matches the candidate's byte for byte, this
evidence applies to the code on `main` today.

**Independence limit:** the reproduction used a clean detached worktree, a
fresh Python virtual environment and a fresh `npm ci`. It reused no builder
state. It was still run by an AI from the same vendor as the builder, so it is
an independent reproduction, not a review by a separate organization or a
human.

## 1. Provenance

| Check | Command | Result |
| --- | --- | --- |
| Candidate object exists | `git cat-file -e 54a0477…^{commit}` | exists |
| Baseline object exists | `git cat-file -e 679d070…^{commit}` | exists |
| Candidate is the pushed PR head | `git ls-remote origin` | `refs/heads/claude/aeos-p0-security-repair-hjs067` → `54a0477…` |
| Baseline is an ancestor | `git merge-base --is-ancestor` | yes; 14 commits, 40 files |
| Whitespace/conflict markers | `git diff --check 679d070 54a0477` | exit 0 |
| Merge changed content | tree comparison above | no |
| Committed secrets | `backend/.env.example` inspected | placeholders only (`your-project`, `your-anon-key`, `your-service-role-key`) |

Changed paths from baseline to candidate: `backend/app` (12),
`backend/tests` (15), `backend/supabase` (3), `frontend` (6),
`.github/workflows` (1), `backend/requirements-dev.txt`,
`backend/.env.example`, `docs/P0_MUTATION_VERIFICATION.md`. No product-module
features were added.

## 2. CI reconciliation

| Run | Event | `head_sha` | Jobs | Conclusion |
| --- | --- | --- | --- | --- |
| [35188123888](https://github.com/marshallchristopher473-netizen/AEOS/actions/runs/35188123888) | push | `54a04773…` (exact) | backend-tests, rls-enforcement, frontend-validation | success |
| [35188172259](https://github.com/marshallchristopher473-netizen/AEOS/actions/runs/35188172259) | pull_request | merge ref | same three | success |

The push run is the one pinned to the exact candidate SHA. The local results
below match CI and the builder's report on every count.

The Vercel deployment on this head reported an error. The builder attributes
this to the Vercel project's Root Directory setting, since the Next.js app
lives in `frontend/`. This session did not verify that cause and has no
access to the Vercel project. It does not bear on tenant isolation.

## 3. Frontend verification at the exact SHA

Environment: clean detached worktree at `54a0477…`, Node `v20.20.2`, npm
`10.8.2` (Node 20 matches CI).

| Step (same as CI `frontend-validation`) | Exit | Result |
| --- | --- | --- |
| `npm ci` | 0 | 372 packages; engine warnings, see SEC-G1-05 |
| `npm audit --audit-level=low` | 0 | found 0 vulnerabilities |
| `npm ls --all` | 0 | tree valid |
| `CI=1 npm run lint` | 0 | no findings |
| `npx tsc --noEmit` | 0 | no errors |
| `npm run build` | 0 | Next.js build compiled; 7 routes |

### Frontend static security review

| Control | Evidence | Result |
| --- | --- | --- |
| No service-role or other secret in client code | no `SERVICE_ROLE`, `SUPABASE_*` key or secret reference under `frontend/src`; the only env read is `NEXT_PUBLIC_API_URL` | PASS |
| Forms cannot assert tenant, actor or role | `students/new` sends only `first_name, last_name, student_number, grade_level, iep_status, birth_date`; `assessments/new` sends only `student_id, title, assessment_type, status, notes` | PASS |
| Server rejects smuggled authority fields | `StudentCreateRequest`, `InterventionPlanCreateRequest`, `AssessmentCreateRequest`, `AssessmentResultCreateRequest` all set `extra="forbid"` | PASS |
| No raw HTML injection sinks | no `dangerouslySetInnerHTML`, `innerHTML` or `eval` | PASS |
| Guard against service-role exposure is live | mutation M16 killed (section 5) | PASS |

Frontend findings SEC-G1-02, 03, 05, 06 and 07 are in the ledger. None of them
is a tenant-boundary defect. Two of them block G4 staging usability.

## 4. Backend reproduction at the exact SHA

Environment: fresh venv, Python `3.11.15`, python-jose `3.3.0`, fastapi
`0.115.0`, psycopg `3.3.6`, disposable local PostgreSQL `16.13`. Synthetic
fixtures only.

| Command | Exit | Result |
| --- | --- | --- |
| `python -m compileall -q app tests` | 0 | clean |
| `python -c "from app.main import app"` | 0 | 17 routes |
| `pytest tests/` (no DB, the CI backend-tests path) | 0 | 108 passed, 62 skipped |
| `AEOS_REQUIRE_RLS_TESTS=1 pytest tests/` with PostgreSQL | 0 | **170 passed, 0 failed, 0 skipped** |
| `AEOS_REQUIRE_RLS_TESTS=1 pytest tests/test_rls_enforcement.py` | 0 | 62 passed |
| `pytest tests/test_security_artifacts.py` | 0 | 5 passed |
| required mode **without** a DB | 2 | fails hard, as designed (no silent skip) |
| mutation suite **without** a DB | 1 | fails hard, as designed |

## 5. M01–M18 mutation contract

`python -m tests.security_mutations --json mutation-matrix.json` → exit 0 in
234 s.

**30 killed · 0 survived · 0 equivalent · 0 invalid · 0 not executed —
30/30 = 100%.** Nothing is excluded from the denominator. All four M09
suspension mutants, including `aeos_can_write_org`, were killed. The full
matrix is in [`evidence/g1/mutation-matrix.json`](evidence/g1/mutation-matrix.json)
(the local path has been removed from it).

## 6. WHERE-less UPDATE/DELETE sweep (new evidence)

The PR #17 builder closed the WHERE-less blind spot for `students` only and
flagged the other tables as not swept (known item 3). This sweep closes that
uncertainty for the current migrations.

Method ([`evidence/g1/whereless_probe.py`](evidence/g1/whereless_probe.py)):
build a template database from the candidate's shim and migrations 001–004,
seed the candidate's own synthetic tenants plus one row per unseeded table,
then for each probe clone a fresh database, become the `authenticated` role
with a JWT subject exactly as the test suite does, issue
`UPDATE <table> SET <col> = '<marker>'` or `DELETE FROM <table>` with no
`WHERE` and no `RETURNING`, **commit**, and inspect organization A's rows over
a privileged connection.

| Scenario | Actor | Tables × ops | Org A rows changed or deleted |
| --- | --- | --- | --- |
| Org A suspended | org A admin | 11 × 2 | 0 |
| Org A suspended | org A teacher | 11 × 2 | 0 |
| Admin account disabled | org A admin | 11 × 2 | 0 |
| Cross-tenant | active org B teacher | 11 × 2 | 0 (org B's own rows updated where allowed) |
| **Positive control** | active org A admin | 7 writable tables × 2 | writes observed on all 14 — the probe can see a breach |

**102 probes, 0 breaches, 0 control failures.** Full results are in
[`evidence/g1/whereless-probe.json`](evidence/g1/whereless-probe.json).

Static confirmation: every `FOR UPDATE` and `FOR DELETE` policy's `USING`
clause calls `aeos_can_write_org` or `aeos_is_org_admin`, directly or through
the parent plan. Both functions require an active organization and an active
membership. `organizations`, `users`, `audit_logs` and `progress_events` have
no UPDATE or DELETE policy and deny by default under forced RLS.

**Limit:** the sweep is not in the committed test suite. A future per-table
policy regression would not be caught by CI (SEC-G1-04).

**Limit found later:** the sweep covered UPDATE and DELETE only. TRUNCATE is a
separate statement that RLS does not govern at all, and it was not probed.
See SEC-G1-10 and section 11.

## 7. Decision ledger entries

| ID | Objective | Module | Severity | Evidence | Confidence | Consequence | Bounded correction | Approval | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-G1-10 | Validation | Shared data layer | **High, gate item** | `anon` and `authenticated` hold TRUNCATE (plus TRIGGER and REFERENCES) on all 11 public tables through the standing `GRANT ALL`. RLS does not apply to TRUNCATE. Reproduced: an org B teacher ran `TRUNCATE public.students CASCADE` and org A's students went from 3 to 0 (rolled back, synthetic data) | High | Any direct database session as a client role, or any future function running dynamic SQL with the caller's rights, can wipe every tenant at once. PostgREST exposes no TRUNCATE, so no HTTP route is known to reach it today | Migration 005 revokes TRUNCATE, TRIGGER and REFERENCES from both client roles, for existing tables and via default privileges; tests and mutants M19a/M19b pin it | None to write; founder merges | Fix proposed (section 11); awaiting independent verification |
| SEC-G1-01 | Validation | Shared data layer | **Gate item** | No isolated hosted Supabase project was available or authorized | High | Supabase-specific behaviour (PostgREST role switching, real `auth.uid()`, issued-token claims) is unverified; the local shim emulates it | Authorize one isolated non-production Supabase project with synthetic data; apply 001–004; rerun the cross-tenant attack set with real tokens | Founder | Proposed |
| SEC-G1-02 | Completion | Frontend | Medium, blocks G4 | 6 pages call `http://127.0.0.1:8000` directly; `lib/api.ts` `apiFetch` (which honours `NEXT_PUBLIC_API_URL`) is unused | High | A deployed staging frontend cannot reach the backend | Route all six pages through `apiFetch` | None | Proposed |
| SEC-G1-03 | Completion | Frontend / auth | Medium, blocks G4 | No sign-in flow exists; pages read `localStorage['aeos_access_token']`, which nothing in the app writes | High | Pilot users cannot sign in without manual token injection; a token in localStorage can be read by any XSS | Pick the session approach (e.g. cookie-based `@supabase/ssr`, already a dependency) before staging | Founder (auth design) | Proposed |
| SEC-G1-04 | Validation | Security suite | Medium (raised from Low, section 12) | WHERE-less probes committed for `students` only; sweep in section 6 is out of suite. Demonstrated: the committed suite still passes with `ai_recommendations_delete` widened to `USING (true)` | High | A per-table regression that lets any tenant delete another's rows passes CI | Add a parametrized WHERE-less UPDATE/DELETE test over all RLS tables | None | Fix proposed (section 12); awaiting independent verification |
| SEC-G1-05 | Completion | Frontend / CI | Low | `npm ci` on Node 20: `@supabase/{supabase,auth,functions,postgrest,realtime,storage}-js@2.111.0` require Node ≥ 22; none is imported by `frontend/src` | High | Unsupported runtime for declared dependencies | Move CI and hosting to Node 22, or drop the unused packages | None | Proposed |
| SEC-G1-06 | Validation | Backend auth | Low (fails closed) | Reproduced: an RS256 token whose `kid` matches a non-RSA JWKS key raises `jose.exceptions.JWKError`, which `except (JWTError, ValueError, TypeError)` does not catch, so the response is HTTP 500 instead of 401. The backend accepts only `RS256` | High | No access granted. Wrong status code, and if the Supabase project signs with a non-RS256 key every login fails | Catch `JOSEError`; confirm the Supabase project's signing algorithm before staging | None | Fix proposed (section 12); awaiting independent verification. Signing-algorithm check still open for staging |
| SEC-G1-07 | Validation | Frontend | Low | `assessments/[id]` renders raw `organization_id` and `created_by` UUIDs | High | Unnecessary exposure of internal identifiers (data minimization) | Remove or replace with display names | None | Proposed |
| SEC-G1-08 | Validation | CI | Low | Mutation artifact is named with `github.sha`, which is the merge ref on `pull_request` events | High | Evidence artifact is not keyed to the reviewed head | `${{ github.event.pull_request.head.sha \|\| github.sha }}` | None | Proposed (carried from PR #17 item 1) |
| SEC-G1-09 | Completion | Repo hygiene | Info | `tsc --noEmit` leaves an untracked `frontend/tsconfig.tsbuildinfo`; not in `.gitignore` | High | Noise in working trees | Add `*.tsbuildinfo` to `.gitignore` | None | Proposed |

Owner for every entry: Chief Technology Platform and Security AI. Human
approver: Christopher Marshall.

## 8. Builder claims compared with reproduced evidence

| Builder claim (PR #17) | Reproduced | Match |
| --- | --- | --- |
| 170 passed / 0 failed / 0 skipped with DB | 170 / 0 / 0 | yes |
| 108 passed / 62 skipped without DB | 108 / 62 | yes |
| 62 RLS tests, 5 artifact tests | 62, 5 | yes |
| Mutation 30/30, exit 0 | 30/30, exit 0 | yes |
| Missing DB fails hard | exit 2 and exit 1 | yes |
| 17 routes | 17 | yes |
| "frontend files changed: 0" | 0 relative to `06fecbd`; **6** relative to baseline `679d070` (the Next.js 16 upgrade commits carried in the branch) | wording only; CI covered the 6 files and they pass here |

## 9. Data safety

- Synthetic data only. Every row is generated by the candidate's test module or the probe script.
- Disposable local PostgreSQL only. No production database, Supabase project, Base44 app or payment system was contacted.
- No JWTs, keys or credentials were printed or committed.
- Nothing was merged or deployed.

## 10. Reproducing this packet

```bash
git worktree add --detach /tmp/g1 54a04773fd8aa73547f49d125bf3b6b0ec08caf2
cd /tmp/g1

# Frontend, Node 20 to match CI
(cd frontend && npm ci && npm audit --audit-level=low && npm ls --all \
  && CI=1 npm run lint && npx tsc --noEmit && npm run build)

# Backend, disposable PostgreSQL 16 only
export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
(cd backend && pip install -r requirements-dev.txt \
  && AEOS_REQUIRE_RLS_TESTS=1 python -m pytest tests/ -q \
  && python -m tests.security_mutations --json mutation-matrix.json)

# WHERE-less sweep; the script lives on the branch that added this packet
python <path-to>/docs/evidence/g1/whereless_probe.py backend whereless-probe.json
```

## 11. Correction: SEC-G1-10 (2026-09-28)

### How it was found

While preparing the next security-lane fixes, a privilege inventory of the
migrated database (`information_schema.role_table_grants`) showed `anon` and
`authenticated` holding every table privilege, TRUNCATE included, on all 11
public tables. PostgreSQL applies row-level security to SELECT, INSERT, UPDATE
and DELETE only, so TRUNCATE is checked against the table privilege alone.

### Reproduction at `54a0477` (synthetic data, rolled back)

Migrations 001–004 on PostgreSQL 16.13, standing Supabase grants as the shim
models them. The session became `authenticated` with organization B's teacher
as the JWT subject, exactly as the RLS suite does:

| Step | Observed |
| --- | --- |
| `has_table_privilege('authenticated', 'public.students', 'TRUNCATE')` | `true` |
| `TRUNCATE public.students CASCADE` as org B's teacher | succeeded |
| Org A students afterwards, inside the same transaction | 3 → **0** |

The transaction was rolled back.

### Why the first issue missed it

- The WHERE-less sweep enumerated the DML verbs RLS governs. It did not
  inventory the privileges RLS does not govern.
- The RLS suite's fixture ran a blanket `GRANT ALL ON ALL TABLES` after every
  migration, and no test inspected table privileges beyond SELECT and DELETE
  on `students`. Nothing in the suite could observe this.

### Proposed fix (builder change, in this PR)

| File | Change |
| --- | --- |
| `backend/supabase/migrations/005_revoke_rls_blind_table_privileges.sql` | New forward-only migration. Revokes TRUNCATE, TRIGGER and REFERENCES from `anon` and `authenticated` on all public tables, and from the default privileges for tables created later. DML grants are untouched |
| `backend/tests/test_rls_enforcement.py` | Applies 005. Drops the post-migration blanket re-grant, which would have silently undone 005; grants now come only from the shim's default privileges at table creation, as in Supabase. Adds `TestPrivilegesRlsDoesNotGovern` (17 tests) and a TRUNCATE negative control |
| `backend/tests/security_mutations.py` | Applies 005 in the precheck. Adds M19a (existing tables keep TRUNCATE) and M19b (default privileges keep TRUNCATE) |
| `backend/tests/sql/supabase_shim.sql`, `docs/P0_MUTATION_VERIFICATION.md`, workflow comment | Comments and contract table brought up to date |

The fix's own evidence, on PostgreSQL 16.13 with synthetic data:

| Check | Result |
| --- | --- |
| New tests before the fix | 14 failed, 65 passed. Exactly the new checks fail; every original test and the new negative control pass |
| Full suite after the fix, required mode | **187 passed, 0 skipped** |
| Full suite without a database | 108 passed, 79 skipped |
| Mutation contract M01–M19 | **32 killed / 32**, 0 survived, 0 invalid |
| M19a killed by | both static privilege checks and all 11 cross-tenant TRUNCATE checks |
| M19b killed by | `test_tables_created_later_do_not_inherit_rls_blind_privileges` |

**Independence:** the session that found the defect also wrote the fix. The
repository's verifier contract does not let a builder verify their own change,
so a separate fresh session must reproduce this at the fix's exact SHA before
SEC-G1-10 can be closed.

**Hosted Supabase:** whether a hosted project's standing grant includes
TRUNCATE for client roles is to be confirmed in the SEC-G1-01 live run. The fix
is correct either way: revoking a privilege that is not held is a no-op.

## 12. Further security-lane fixes (2026-09-28)

Two ledger items that needed no founder decision were fixed before the
independent verification and the live Supabase run, so that both can run once,
on the final code. Both are builder changes and need the same independent
verification as SEC-G1-10.

### SEC-G1-06 — unusable published keys now fail closed as 401

| | |
| --- | --- |
| Change | `backend/app/core/auth.py` catches `JOSEError`, python-jose's base class, instead of `JWTError`. `JWKError` is a `JOSEError` but not a `JWTError` |
| Test | `test_auth.py::test_unusable_published_key_is_401_not_a_server_error`, with an EC key and a symmetric key published under the token's `kid`. Both cases failed with an escaped `JWKError` before the fix |
| Mutant | M18h re-raises `JWKError` past the handler, reproducing the old behaviour exactly. M18g's anchor moved with the changed line |
| Still open | This does not add ES256 support. If the Supabase project signs with a non-RS256 key, logins are refused with 401. Confirm the signing algorithm before staging |

### SEC-G1-04 — the WHERE-less sweep is now part of the suite

| | |
| --- | --- |
| Change | `TestWherelessWritesAcrossEveryTable` in `test_rls_enforcement.py`: WHERE-less UPDATE and DELETE on all 11 tables × 4 attackers (suspended organization's admin, suspended organization's teacher, disabled admin account, another organization's teacher) = 88 probes |
| Isolation | Each probe runs in one privileged transaction that is always rolled back, so a wrongful write never reaches the shared seed data |
| Negative controls | With RLS off for the table, the same writes reach organization A: UPDATE on all 11 tables, DELETE on 9 (`organizations` and `users` are excluded because RESTRICT foreign keys fail first) |
| Mutant | M20 widens `ai_recommendations_delete` to `USING (true)`. The suite without the sweep passes under it (189 passed, 0 failed); the sweep fails in all four attacker scenarios |

## Next action

1. **Independent verification of the SEC-G1-10, SEC-G1-06 and SEC-G1-04
   fixes** in a fresh session, at the branch's final exact SHA.
2. **Founder decision:** authorize, or decline, one isolated non-production
   Supabase project holding synthetic data only, so that SEC-G1-01 can be run
   on the fixed SHA.

Once both pass, G1 can be re-issued as PASS.
