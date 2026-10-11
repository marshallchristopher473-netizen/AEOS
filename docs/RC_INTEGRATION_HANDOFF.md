# AEOS release-candidate integration handoff (#20, #22, #23–#25)

Builder record for one bounded integration. It is **not** an independent
verification and makes no `P0 VERIFIED` claim. Independent verification is a
separate session under `.github/agents/aeos-p0-independent-verifier.agent.md`.

| | |
| --- | --- |
| Repository | `marshallchristopher473-netizen/AEOS` |
| Branch | `claude/aeos-rc-integration-m8bgcw` |
| Draft PR | [#31](https://github.com/marshallchristopher473-netizen/AEOS/pull/31) (draft; no merge, no deployment) |
| Baseline `origin/main` | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` (rechecked unchanged before integration) |
| Reviewed code head | `f9bbbfa2283c6ca74b271808234bf1b3a75cf350`, tree `0552d0ac3ec16dd6ece4eebb56cafdaa3e1e5fde` |
| Commits after the reviewed head | this handoff document only (docs; no code, test, workflow or lockfile change) |
| Date | 2026-10-11 |

## 1. Decisions

- **Integration:** complete. All three source lines are merged once, every
  conflict is resolved explicitly (section 4), and the full CI contract passes
  locally on PostgreSQL 16 and in GitHub Actions on the reviewed head.
- **Builder P0 decision: `P0 NOT READY`.** Nothing in this candidate has been
  shown to fail, but one known open finding applies to it unchanged: F4
  (hosted Supabase PostgreSQL 17 grants `MAINTAIN` to client roles; migration
  005 does not revoke it), reported by the independent verification of #27 in
  #29 and judged blocking for `P0 VERIFIED` there. Hosted sign-in and the hosted
  two-tenant attack have also not run. See section 8.

## 2. Source identity and ancestry

All anchors resolved locally and matched the live PR heads at integration time.

| PR | Head SHA | Base | Ahead of `b9c68aa` | Content |
| --- | --- | --- | --- | --- |
| #20 | `0aefabcd752797e341577f2c027e54df4f005e9b` | `main` | 6 | SEC-G1-10 TRUNCATE revoke (migration 005), SEC-G1-06 JOSEError, SEC-G1-04 WHERE-less sweep, mutants M18h/M19a/M19b/M20, dated audit exceptions |
| #22 | `e7de87d7d5d0c2656d20d46fc2b09834fec0042e` | `main` | 3 | Supabase ES256 keys pinned per published key, documented JWKS endpoint, mutants M18i/M18j/M18k |
| #23 | `3fb76752642d8d6f9e3e99a8a1b79784d9d4b4f2` | `main` | 4 | Teacher assessment review slice, request/browser tests, Node 22, strict audit |
| #24 | `f211c9691b0d6eca5884461dd519e751c2e4fc9d` | #23 | 5 | Scoped `fast-glob` → `tinyglobby@0.2.17` override, lint-glob guard |
| #25 | `6453ae17bce3cd01aa9263b30ef56ee8e6210969` | #24 | 6 | `source-map-js` 1.2.2 |

Ancestry checked with `git merge-base --is-ancestor`: #23 ⊂ #24 ⊂ #25, so #25's
head integrates the stack once. #20 and #22 are independent of each other and of
the stack (merge base `b9c68aa` for each).

Historical PRs are untouched: #20–#25 and the earlier integration attempts #26
(`70a02f8`), #27 (`bcf58e1`), #28 (`3816773`), verification record #29 and pilot
harness #30 stay open as they were. #26 and #28 were used only as a
cross-check after this integration was built. #26 independently reached the
identical `package.json` and `package-lock.json`. #28's mutation-harness
hardening is not part of #20–#25 and was not ported (section 6).

## 3. Integration commits (on top of `b9c68aa`)

| Commit | Purpose |
| --- | --- |
| `abea7d6` | merge #20 @ `0aefabc` (no conflicts) |
| `cd24031` | merge #22 @ `e7de87d` (conflict in `auth.py`) |
| `9ae98ae` | merge #23 > #24 > #25 @ `6453ae1` (conflicts in workflow and lockfile) |
| `db5197e` | fix(frontend): next 16.3.8 and sharp 0.35.5 patch advisories |
| `5eaf5e0` | test(frontend): rootDir checked on every linted file; every fast-glob import |
| `7adc53a` | ci: drop #20's dated npm audit exception mechanism |
| `c82a225` | test(auth): correct the SEC-G1-06 test docstring after the ES256 repair |
| `68ab159` | ci: run on `claude/aeos-rc-**` and record the checked-out tree |
| `f9bbbfa` | docs: audit decision, tinyglobby review, M18h killing test |

## 4. Conflict and reconciliation decisions

| Area | Sources | Decision |
| --- | --- | --- |
| `backend/app/core/auth.py` | #20, #22 | Both made the same `JWTError` → `JOSEError` change. #22's version taken (it needs `construct_jwk`), keeping #20's SEC-G1-06 reference in the comment. No code difference from either side. |
| Auth imports | #22 vs #23 code | The only auth import outside auth tests is `get_current_user` (`dependencies.py`, `conftest.py`, `review_fixture_server.py`), whose signature is unchanged. No `JWTError`/`RS256` use remains outside `auth.py`/tests. |
| Mutation anchors | #20, #22 | Both re-anchored M18g identically. #20's M18h/M19a/M19b/M20 and #22's M18i/M18j/M18k are disjoint; all 37 retained and all apply (0 INVALID). |
| SEC-G1-06 tests | #20, #22 | Both kept. #20's test no longer reaches `JWKError` after #22 (EC P-256 is now a supported key and fails on the pinned algorithm; `oct` is refused by `signing_algorithm` first; traced with a probe). Assertions unchanged, docstring corrected. The mutation run records #22's `test_published_key_python_jose_cannot_load_is_401_not_a_server_error` as M18h's only killer; `P0_MUTATION_VERIFICATION.md` corrected to match. |
| Migration 005 | #20 only | Applied unchanged. #23 adds no table or column; `assessment_results` (003) is covered by 005's `ON ALL TABLES` revoke; the review service writes only existing columns, supplies the `id` the table has no default for, and the request schema forbids `id`/`organization_id`. |
| npm audit policy | #20 vs #23/#24 | **Strict, no exceptions.** Kept `npm audit --omit=dev --audit-level=low` (from #20) and the full-tree `npm audit --audit-level=low --json` with pipefail and artifact (from #23). Removed #20's dated braces exception (`check-npm-audit.mjs`, `audit-exceptions.json`, expiry 2026-12-31). The full-tree audit runs even if the production audit fails. |
| `frontend/package-lock.json` | #20 (next 16.3.8, no manifest change) vs #25 (next 16.3.6, override, manifest) | Took #25's lockfile verbatim, since it matches the merged manifest. No hand merge. Then re-resolved with npm (next row). |
| New advisories | registry, 2026-10-11 | Both strict audits failed on the integrated tree: `next` 16.0.0–16.3.7 (6 advisories, high) and `sharp` <0.35.5 (high). Compatible patches: next `16.3.8` (manifest floor `^16.3.8`; npm first resolved 16.4.0, which was rejected as more than the minimal patch) and sharp `0.35.5` (lockfile only, in next's `^0.35.4`). No force upgrade or new override. |
| tinyglobby | #24 | Kept, with its limits recorded. It is not a general fast-glob replacement. It is safe here only because the plugin's single call, `globSync(rootDir, {onlyDirectories:true})` in `dist/utils/get-root-dirs.js`, runs only when `settings.next.rootDir` is set, which AEOS never does. The guard was strengthened: `rootDir` is now checked on every linted file (the old guard passed 3/3 with `rootDir` set for `src/lib/**`), and any unrecognised `require("fast-glob")` form fails the guard. Every guard was shown to fail under a deliberate break. |
| Workflow | #20, #23 | Node 22 setup, request-contract tests, lint-glob guard and the Chrome check come from #23/#24. #20's M01–M20 comment is kept. Added a `claude/aeos-rc-**` push trigger and a per-job "Record checkout identity" step. |

## 5. Changed paths (41 vs baseline)

Union of #20 (15), #22 (7) and #25 (27) minus 6 overlaps = 43, minus the 2
removed exception files. Every file touched by a single source is
byte-identical to that source, except these deliberate changes:
`frontend/package.json`, `frontend/package-lock.json`,
`frontend/tests/lint-glob-override.test.mjs`, `docs/DEPENDENCY_SECURITY_REVIEW.md`.
No test function from any source (or the baseline) is missing:
`test_auth.py`, `test_rls_enforcement.py` (56 tests including
`TestPrivilegesRlsDoesNotGovern` and `TestWherelessWritesAcrossEveryTable`),
`test_config.py` and `test_assessment_results.py` were checked by name.
`git diff --check b9c68aa f9bbbfa` is clean, and no generated files, caches,
`.env` files or secrets were added.

## 6. Local evidence (fresh detached worktree at `f9bbbfa`)

Environment: Python 3.11.17 venv with `pip install -r backend/requirements-dev.txt`,
Node v22.22.0 / npm 10.9.4, `npm ci` with `node_modules` removed first,
PostgreSQL 16.15 at `localhost:5432` (synthetic data only), Playwright Chromium
1194 in place of `google-chrome`. Worktree identity: HEAD `f9bbbfa…`, tree
`0552d0ac…`, clean before the run.

| Step (CI equivalent) | Exit | Duration | Result |
| --- | --- | --- | --- |
| `python -m compileall -q backend/app backend/tests` | 0 | 0.1 s | |
| import `app.main` / schemas / dependencies | 0 / 0 / 0 | 1.0 / 0.2 / 0.8 s | |
| `pytest tests/ -v` (no DB, as in `backend-tests`) | 0 | 5.3 s | 143 passed, **187 skipped** (all `test_rls_enforcement.py`: no `AEOS_TEST_DATABASE_URL`, by design in this job) |
| `pytest tests/test_assessments.py -v` | 0 | 1.5 s | 7 passed |
| `pytest tests/test_rls_enforcement.py -v -rs` with `AEOS_REQUIRE_RLS_TESTS=1` | 0 | 7.5 s | 187 passed, 0 skipped |
| `pytest tests/ -v -rs` with PostgreSQL 16 **required** | 0 | 10.7 s | **330 passed, 0 skipped, 0 failed** |
| `python -m tests.security_mutations --json …` | 0 | 655.6 s | **37 killed, 0 survived, 0 equivalent, 0 invalid, 0 not executed (37/37)**. No killed record had errors, no mutant run reported skips, every mutant also failed the complete suite |
| `npm ci` | 0 | 14.0 s | |
| `npm audit --omit=dev --audit-level=low` | 0 | 0.6 s | 0 vulnerabilities |
| `npm audit --audit-level=low --json` | 0 | 0.6 s | 0 vulnerabilities, 409 packages |
| `npm ls --all` | 0 | 0.6 s | |
| `node --experimental-vm-modules tests/assessment-api.test.mjs` | 0 | 0.3 s | 6 pass, 0 fail, 0 skipped |
| `node tests/lint-glob-override.test.mjs` | 0 | 3.5 s | 3 pass, 0 fail, 0 skipped |
| `CI=1 npm run lint` | 0 | 4.0 s | |
| `npx tsc --noEmit` | 0 | 2.8 s | |
| `npm run build` | 0 | 12.2 s | Next.js 16.3.8 |
| Chrome teacher review vs synthetic backend | 0 | 2.8 s | 6/6 PASS (save/reload, draft, invalid score, forbidden save, cross-tenant, missing session) |

The two pytest warnings are a third-party `DeprecationWarning` from
`starlette/testclient.py`. An earlier run on `68ab159` plus the two then-uncommitted
doc edits gave the same counts and 37/37. Its browser step first reported exit 1
because of a bug in the local runner's cleanup trap (fixed). The test itself had
exited 0 with 6/6.

The mutation harness was used as merged from #20/#22. #28's hardening (forcing
`AEOS_REQUIRE_RLS_TESTS=1` inside mutant runs, and classifying runs with errors
as INVALID) is outside #20–#25 and was not ported. Instead, the recorded matrix
was checked for exactly those cases: none occurred.

## 7. CI evidence (workflow "P0 Security Candidate")

| Run | Event | Checked-out commit | Checked-out tree | Conclusion |
| --- | --- | --- | --- | --- |
| [38168850435](https://github.com/marshallchristopher473-netizen/AEOS/actions/runs/38168850435) (#48) | push | `f9bbbfa…` (the head) | `0552d0ac…` | success |
| [38168872957](https://github.com/marshallchristopher473-netizen/AEOS/actions/runs/38168872957) (#49) | pull_request | `75fd5dae3d72bd663dcc2ff76ab592530869546a` (GitHub merge, parents `b9c68aa` + `f9bbbfa`) | `0552d0ac…` | success |

The merge tree is byte-identical to the reviewed head's tree, so both runs tested
the same files. In both runs all three jobs (`backend-tests`, `rls-enforcement`,
`frontend-validation`) succeeded. Read from the job logs: backend 143 passed /
187 skipped and 7 passed; both audits "found 0 vulnerabilities" (409 packages);
contracts 6/6; glob guard 3/3; Chrome 6/6 PASS; Next.js 16.3.8.

**Not read from CI in this environment:** the RLS pytest totals and the
per-mutant matrix. The log API returns only the last 5,000 lines, which are
PostgreSQL container shutdown output, and the artifact host is blocked by this
environment's network policy. The mutation step's success implies 0 survived,
0 invalid and 0 not executed, because the harness exits 1 on any of them and no
mutant is declared equivalent. This is an inference from the exit code, not a
read of the matrix. Artifacts for the verifier: `mutation-matrix-f9bbbfa…`
(ID 11713785425, sha256 `95180afb…6f4d`) and `mutation-matrix-75fd5da…`
(ID 11714090245, sha256 `457009ee…3a49`).

## 8. Outstanding gates

| Gate | Status | What it needs |
| --- | --- | --- |
| Independent P0 verification of this exact head | **NOT TESTED** | A separate verifier session from the exact final PR head SHA |
| F4: `MAINTAIN` held by `anon`/`authenticated` on hosted PostgreSQL 17 (from #29) | **OPEN, applies unchanged** (005 identical) | A forward-only migration 006 revoking `MAINTAIN` (plus default privileges) and a PostgreSQL 17 CI service to pin it, or an explicit owner risk acceptance. The PG16 suite cannot see this privilege |
| F3: tables created by `supabase_admin` regain client privileges (from #29) | **OWNER DECISION** | Accept and document, or add a check rejecting `public` tables not owned by `postgres` |
| F1: `anon` EXECUTE on SECURITY DEFINER helpers (low) / F2: unthrottled JWKS refresh on unknown `kid` (medium, availability) (from #29) | **OPEN, non-blocking per #29** | Owner triage |
| Hosted two-tenant attack, TRUNCATE CASCADE denial, row survival | **BLOCKED** | Approved rolled-back transaction on the isolated hosted test project |
| Sign-in: real Supabase Auth ES256 session against the hosted JWKS | **NOT TESTED** | Network access to the isolated project and a synthetic test user. JWT verification here is unit-tested with locally generated keys only |
| Browser sessions and persistence | Synthetic only | The Chrome check uses `review_fixture_server` (loopback, synthetic subjects, in-memory store) and proves no hosted readiness |
| AI | **Not implemented, NOT TESTED** | No AI code path exists. `ai_recommendations` is only an RLS-protected table. No AI quality, safety or outcome claim is supported |
| Real student data, pilot, deployment | **Not authorized** | Every gate above. No merge or deployment was performed |

## 9. Next action

Run the independent verifier on PR #31's exact head. Separately, the owner
decides F4: accept it as a documented risk, or authorise a bounded follow-up
candidate (migration 006 plus PostgreSQL 17 in CI) before hosted Gate 2 is run.
