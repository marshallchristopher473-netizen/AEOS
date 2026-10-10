# AEOS bounded release candidate handoff — 2026-10-10

**P0 NOT READY.** Builder integration only. Independent verification belongs to a separate fresh session. No merge or deployment is authorized by this handoff.

## Provenance

Repository: `marshallchristopher473-netizen/AEOS`.
Baseline refreshed through GitHub on 2026-10-10: `b9c68aa3e6fe35f676da04c10683bfdda12a9eed`.
Dedicated branch: `p0/security-release-candidate-20261010`.
Isolated worktree: `/workspace/aeos-rc`; source checkout: `/workspace/aeos-source`.
The exact published head, its tree, draft PR URL and actual CI checkout identity are recorded in the draft PR description and final external handoff, after this document is committed.

The environment initially contained no repository. Shell cloning failed (unreachable proxy, then no DNS); CLI authentication was invalid. The working GitHub connector refreshed main and PRs #20–25. It retrieved the exact source blobs and Git metadata. All 137 unique blobs, seven complete source trees, and 17 commits between the heads and baseline were reconstructed locally and SHA-1 checked before writing Git objects. The local repository is shallow at the baseline; earlier history is not available locally. No original remote history or PR was altered. No pre-existing user files were changed.

| Source | Refreshed head | Included |
|---|---|---|
| #20 | `0aefabcd752797e341577f2c027e54df4f005e9b` | Security repairs and expanded regression coverage; exception policy superseded |
| #21 | `3da5601c5a0a16da4481e554f700f849013e22d0` | Historical baseline evidence, not evidence for this head |
| #22 | `e7de87d7d5d0c2656d20d46fc2b09834fec0042e` | Authentication repair and M18i–M18k |
| #23 | `3fb76752642d8d6f9e3e99a8a1b79784d9d4b4f2` | Teacher workflow, request/browser tests |
| #24 | `f211c9691b0d6eca5884461dd519e751c2e4fc9d` | Scoped tooling override and guards |
| #25 | `6453ae17bce3cd01aa9263b30ef56ee8e6210969` | Production source-map-js patch |

Ancestry was inspected before merging: #24's only parent is #23; #25's only parent is #24. Local `git merge-base --is-ancestor` confirms both. #25 contains all six commits in the #23–25 stack. It was integrated once, then #20, #22 and #21. The published integration uses main as its first parent and the source heads as additional parents, retaining source ancestry without rewriting historical PRs.

## Conflict and evidence decisions

- Workflow: retain Node 22, full-tree `npm audit --audit-level=low`, strict production `npm audit --omit=dev --audit-level=low`, all request/browser tests and the scoped lint guards. No suppression, exception script, lower threshold, or `continue-on-error`. Both audit JSON files publish even on failure; Bash pipefail preserves audit exits.
- #20's dated braces exception and checker are excluded from the candidate. The original PR and historical evidence packet remain intact; their audit/count claims apply only to their stated historical trees.
- Lockfile: retain #25's reviewed package.json and lockfile byte-for-byte, including #23's brace-expansion fixes, #24's alias and #25's source-map-js 1.2.2. #20's separate Next/tooling 16.3.8 lock refresh is not replayed over this reviewed stack. Current lockfile SHA-256: `cfd4b5042f2e6c4a52bfc563295097786e6f79ba4a36afd2aed5cf7f62373f4e`.
- Auth imports/comment: retain `JOSEError`, `jwt`, and `construct_jwk`; retain #22's RSA/EC wording. All #20 and #22 auth tests remain; update only the obsolete #20 test docstring. M18h now reaches the unloadable EC-key test rather than the RSA-versus-EC case.
- Migration 005 is included exactly once in the RLS fixture and SQL mutant prechecks. M19a/M19b and M20 remain. M02/M18g/M18j anchors follow key construction. Migrations 001–004 are unchanged. The fixture never re-grants the revoked privileges.
- tinyglobby is **not** a general fast-glob replacement. Keep the override scoped to the Next lint plugin. Guards retain member resolution and the raw-link lint probe; rootDir must be unset for every linted source file (expanded from one example file). Configured rootDir globbing requires removal or a separately reviewed compatible solution.
- Mutation evidence repair: record subset and complete-suite exits/errors; setup/collection failures cannot count as kills even alongside assertions; an assertion must also be observed in the full suite; configured database subprocesses run with required RLS. Invalid mutants retain durations. Five stdlib regression tests cover these reporting failures. All source mutations remain in the denominator contract.
- CI: the branch matches the existing `p0/security-*` push trigger; the draft targets main. Pin Node 22.22.2/npm 10.9.7 and Python 3.11.15. PostgreSQL service is version 16. Run complete backend with required RLS, focused RLS and the entire mutation contract. Each job records reviewed head, event SHA, actual `HEAD`, tree and lockfile digest; command artifacts record exits and durations and backend JUnit artifacts record actual cases/skips.

## Local execution evidence

Local environment: Python 3.12.14, Node 24.19.0/npm 11.9.0. Node 22 and PostgreSQL tooling/service are unavailable. Pinned backend installation in a new virtual environment failed (no package source available); npm registry access fails with `EPERM` at the proxy. No live Supabase project or credentials were used.

The following are actual exits and elapsed seconds. Failed dependency/infrastructure attempts are **BLOCKED**, not product acceptance failures or successful audit reports. Full backend and RLS cannot collect tests because pytest is absent; pass/fail/skip case counts are unavailable, not inferred from historical PRs. Browser verification is BLOCKED because the built frontend/backend dependencies are unavailable; it was not executed.

| Command label (exact argv in JSON) | Exit | Seconds |
|---|---|---|
| `npm-ci` | 1 | 1.427 |
| `npm-tree` | 1 | 0.295 |
| `audit-full` | 1 | 0.394 |
| `audit-production` | 1 | 0.349 |
| `lint` | 127 | 0.126 |
| `typecheck` | 1 | 0.270 |
| `build` | 127 | 0.117 |
| `backend-required` | 1 | 0.016 |
| `rls-required` | 1 | 0.016 |
| `compile` | 0 | 0.266 |
| `request-contract` | 0 | 0.490 |
| `harness-unit` | 0 | 0.185 |
| `mutation-anchors` | 0 | 0.069 |
| `mutation-contract` | 1 | 11.295 |
| `lint-glob-guards` | 1 | 0.106 |
| `backend-import` | 1 | 0.924 |
| `backend-install` | 1 | 0.339 |

Supplementary local passes: request contracts **6 passed / 0 failed / 0 skipped** on Node 24; harness evidence tests **5 passed / 0 failed / 0 skipped**; compilation, YAML parsing and `git diff --check` pass. Static anchor check finds **37** unique substitutions and parsable Python targets; that count is an inventory, not an expected kill count.

The diagnostic full mutation attempt: **0 killed, 0 survived, 0 equivalent, 37 invalid, 0 not executed**, exit **1**. No security mutation result is accepted. Python targets fail imports without the pinned SDK; SQL targets lack psycopg/PostgreSQL; the frontend source mutant cannot execute pytest. An earlier diagnostic exposed a harness reporting error (missing pytest treated as survived); it is covered by the new regression test and corrected above. No old PR result is substituted for this candidate's evidence.

Raw local command evidence: `docs/evidence/rc-20261010/local-commands.json`.
Raw infrastructure-only mutation matrix: `docs/evidence/rc-20261010/local-mutation-diagnostic.json`.
CI must supply fresh actual backend/RLS/mutation counts, skips, invalids, command exits/durations and checkout identities. A generated merge commit is not assumed tree-identical: compare actual tree hashes.

## Reproduction commands

Run from a clean checkout of the exact published SHA, using Node 22.22.2/npm 10.9.7, Python 3.11.15, fresh backend dependencies, and disposable PostgreSQL 16 with synthetic data:

```bash
python -m compileall -q backend/app backend/tests
python .github/scripts/check-mutation-anchors.py
(cd frontend && npm ci)
(cd frontend && npm ls --all)
(cd frontend && npm audit --audit-level=low)
(cd frontend && npm audit --omit=dev --audit-level=low)
(cd frontend && node --experimental-vm-modules tests/assessment-api.test.mjs)
(cd frontend && node tests/lint-glob-override.test.mjs)
(cd frontend && CI=1 npm run lint)
(cd frontend && npx --no-install tsc --noEmit)
(cd frontend && npm run build)
python -m pip install -r backend/requirements-dev.txt
(cd backend && python -c 'from app.main import app; print("backend OK")')
export AEOS_REQUIRE_RLS_TESTS=1
export AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
(cd backend && python -m pytest tests/ -v -rs)
(cd backend && python -m pytest tests/test_rls_enforcement.py -v -rs)
(cd backend && python -m tests.security_mutations --json ../mutation-matrix.json)
```

The exact synthetic Chrome launch/server/trap commands are retained in `.github/workflows/p0-backend-tests.yml`; they execute `frontend/tests/browser_review.py`. Browser test results cover synthetic sessions/storage only.

## Outstanding gates and supported alternatives

- **Strict dependency audit: BLOCKED locally.** No usable current registry audit was returned; do not infer zero vulnerabilities from #24/#25's dated reports. If current CI reports an advisory, retain draft and report the exact package/path/advisory. Supported bounded remedies are compatible patched versions or upstream removal of the vulnerable lint chain. The reviewed scoped alias is conditional on its guards. A separately reviewed tooling migration is an alternative if those assumptions fail. No force upgrade, Next 14 downgrade, general alias or dev-only exception is accepted here.
- **Backend/RLS/full mutation/Node 22/browser: BLOCKED locally**, awaiting actual CI execution and reconciliation. If CI runners, packages or PostgreSQL are unavailable, keep BLOCKED.
- **Sign-in:** live session acquisition/UI provisioning and Supabase RS256/ES256 JWT/JWKS interoperability remain untested. Confirm a supported asymmetric signing key and documented JWKS endpoint; legacy HS256 is intentionally rejected. Legacy Python API-key compatibility and cache lifetime are carried follow-ups, not silently repaired in this release candidate.
- **Hosted tenant boundary:** safe isolated hosted Supabase migration/RLS tests and two-tenant attacks remain BLOCKED. Local PostgreSQL CI cannot substitute for the hosted gate. No production credentials/data or hosted writes were used.
- **AI:** no AI output quality, outcomes, readiness or pilot gate is asserted. Teacher-entered reviews remain the bounded supported workflow.
- **Independent verification:** a fresh session must verify the exact pushed candidate under `.github/agents/aeos-p0-independent-verifier.agent.md`. This builder session cannot issue P0 VERIFIED.

Changed paths are in the draft PR and `git diff --name-only b9c68aa3e6fe35f676da04c10683bfdda12a9eed HEAD`. Source records under `docs/evidence/g1` and `docs/P0_VERIFICATION_RECORD.md` remain historical, not candidate evidence.
