# AEOS release candidate 1: integration handoff

Status: **builder handoff, not verified.** This branch integrates five reviewed
draft PRs once, for a separate independent verification session. It does not
claim `P0 VERIFIED`. Nothing here is merged or deployed.

## Provenance

| Item | SHA |
| --- | --- |
| Baseline `origin/main` | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` |
| #20 security repair (SEC-G1-10/-06/-04, migration 005) | `0aefabcd752797e341577f2c027e54df4f005e9b` |
| #22 authentication repair (ES256, JWKS endpoint) | `e7de87d7d5d0c2656d20d46fc2b09834fec0042e` |
| #23 teacher assessment review | `3fb76752642d8d6f9e3e99a8a1b79784d9d4b4f2` |
| #24 tinyglobby override (stacked on #23) | `f211c9691b0d6eca5884461dd519e751c2e4fc9d` |
| #25 source-map-js (stacked on #24) | `6453ae17bce3cd01aa9263b30ef56ee8e6210969` |

All six were fetched and matched the audit anchors exactly. Ancestry:
#23 ⊂ #24 ⊂ #25, each based on `b9c68aa`; #20 and #22 are independent siblings
of the same base. #21 (docs-only verification record) is not integrated.
All source PRs are left open and unchanged.

Every source head is an ancestor of this branch (merge commits, no rebase), so
`git merge-base --is-ancestor <sha> HEAD` holds for each.

The reviewed head SHA, its tree, the CI run and the merge commit CI checked out
are recorded in the pull request description, because a commit cannot contain
its own SHA or the CI run it triggers.

## Integration order and conflict decisions

1. `merge #25` (brings #23, #24, #25): clean.
2. `merge #22`: clean; no file overlap with the stack.
3. `merge #20`: three conflicts.

| Path | Decision |
| --- | --- |
| `backend/app/core/auth.py` | Keep #22's `construct_jwk` import and #22's comment on the `JOSEError` handler. #20's wording ("not an RSA key") is false once EC keys are supported. #20's `SEC-G1-06` tag is kept. This is the resolution #22's description prescribes. |
| `.github/workflows/p0-backend-tests.yml` | Keep #23's full-tree audit (`npm audit --audit-level=low`, pipefail, JSON artifact). Add #20's production audit (`npm audit --omit=dev --audit-level=low`) as its own step that runs even when the full audit fails. Drop #20's dated-exception step. Node 22 (from #23) is kept. |
| `frontend/package-lock.json` | Take #25's lockfile. Re-apply #20's Next.js 16.3.8 remedy with npm instead of merging lockfile JSON by hand. |

Auto-merged files, checked by hand:

- `backend/tests/security_mutations.py`: all 37 mutation anchors (contract IDs
  M01–M20, 31 IDs) match exactly one site in the integrated tree. None is
  marked equivalent.
- Migration 005 is the only new migration on any integrated line. Nothing is
  renumbered and no historical migration is edited.

## Explicit decision: #20's dated braces exception vs. #23/#24's strict audit

**Decision: strict audit, no suppression.** `frontend/audit-exceptions.json`
and `.github/scripts/check-npm-audit.mjs` are removed in their own commit.
CI runs both `npm audit --audit-level=low` (full tree) and
`npm audit --omit=dev --audit-level=low` (production), each without exceptions.

Why this is safe: the exception covered only GHSA-vfj7-8cjw-p6xm (braces).
#24's scoped override (`@next/eslint-plugin-next` → `fast-glob` →
`npm:tinyglobby@0.2.17`) removes every braces, micromatch and fast-glob copy, so
the exception had nothing left to cover. Strict audit passes (below).

## Commits added on top of the merges

| Commit | Change |
| --- | --- |
| `ci: drop the dated npm audit exception mechanism from #20` | Removes the two files above. |
| `fix(frontend): clear current production advisories in next and sharp` | The strict audit on the merged tree failed with two high **production** findings: `next` 16.0.0–16.3.7 (six advisories; #20's 16.3.8 remedy) and `sharp` < 0.35.5 (GHSA-wq5f-xc86-pv6w, newer than every source PR). Applied with `npm install next@16.3.8` and `npm update sharp`. Only `next`/`@next/*` (16.3.6 → 16.3.8) and `sharp`/`@img/*` (0.35.4 → 0.35.5, libvips 1.3.3 → 1.3.4) change. `npm audit fix` was rejected because it proposed `next` 16.4.0. No `--force`, no new override. |
| `test(frontend): check rootDir on every linted file, not one sample` | Hardens #24's guard; see below. |
| `test(auth): correct the SEC-G1-06 test docstring after the ES256 repair` | Docstring only. |
| `docs: …` | This file, the dependency review follow-up, and the M18h row of the mutation doc. |

## tinyglobby compatibility review

tinyglobby is not a general drop-in for fast-glob: it expands directory patterns
and includes the base of `**`. The override is safe here only because the
plugin never globs. Checked against the installed plugin source:
`getRootDirs` (`@next/eslint-plugin-next/dist/utils/get-root-dirs.js`) calls
`globSync` only when `settings.next.rootDir` is a string or array; otherwise it
returns `[context.cwd]`. Its only caller is `no-html-link-for-pages`.

#24's three guards, reviewed:

1. Plugin's `fast-glob` resolves to tinyglobby and every member it uses
   (`globSync`) is a function there; fails with "remove the override" if the
   plugin drops fast-glob. **Adequate.**
2. `settings.next.rootDir` is unset. **Gap found and fixed.** It read the
   effective config of one file. Flat config can scope `settings` to a `files`
   glob, so `{ files: ['src/lib/**'], settings: { next: { rootDir: 'src' } } }`
   re-enables the divergent glob while all three original guards pass
   (reproduced). The guard now checks every file ESLint's own enumeration
   (`lintFiles('.')`) returns. Verified: passes on the real config; fails for
   `rootDir` scoped to `src/lib/**`, `src/app/assessments/**`, `**/*.mjs` and
   the original sample file, each with the `rootDir` assertion (not a discovery
   error).
3. `no-html-link-for-pages` still flags a raw `<a href="/students">`. **Adequate.**

Remove the override when the plugin stops depending on fast-glob, or braces
ships a release outside the advisory range.

## Local evidence (measured)

One clean run in a fresh detached worktree at code commit
`0574dcf07bae2d80e316807eab0c276432858b8e` (tree
`c6dd0411d1b78accf37d06b006d7310f5ed693a3`), 2026-10-09 23:33–23:43 UTC: fresh
`npm ci`, freshly created database, every step logged. The only later commit
adds documentation (`*.md`), so it cannot change these results; the PR
description records a repeat run at the final head.

Environment: Node 22.22.0, npm 10.9.4, Python 3.11.17, PostgreSQL 16.15
(local, disposable database, synthetic data only). Lockfile SHA-256
`59fa036f303e300763340d10dbc39068f72e71dd3b69d89585281bd3971673a0`.

| Step (CI order) | Command | Exit | Seconds | Result |
| --- | --- | --- | --- | --- |
| Install | `npm ci` | 0 | 11.8 | 357 packages |
| Full audit | `npm audit --audit-level=low` | 0 | 0.5 | 0 vulnerabilities |
| Production audit | `npm audit --omit=dev --audit-level=low` | 0 | 0.5 | 0 vulnerabilities |
| Tree | `npm ls --all` | 0 | 0.5 | valid |
| API contracts | `node --experimental-vm-modules tests/assessment-api.test.mjs` | 0 | 0.3 | 6 pass, 0 fail, 0 skip |
| Glob guards | `node tests/lint-glob-override.test.mjs` | 0 | 3.0 | 3 pass, 0 fail, 0 skip |
| Lint | `CI=1 npm run lint` | 0 | 3.3 | clean |
| Types | `npx tsc --noEmit` | 0 | 2.3 | clean |
| Build | `npm run build` | 0 | 10.2 | Next.js 16.3.8 |
| Compile | `python -m compileall -q backend/app backend/tests` | 0 | 0.1 | |
| Imports | app / schemas / dependencies | 0, 0, 0 | 0.8, 0.2, 0.7 | |
| Backend, no DB (CI `backend-tests` path) | `pytest tests/ -v -rs` | 0 | 4.6 | 143 passed, 187 skipped, 0 failed |
| Assessments | `pytest tests/test_assessments.py -v` | 0 | 1.2 | 7 passed |
| **Backend, PostgreSQL required** | `AEOS_REQUIRE_RLS_TESTS=1 pytest tests/ -v -rs` | 0 | 8.7 | **330 passed, 0 skipped, 0 failed** |
| RLS module, required (CI step) | `AEOS_REQUIRE_RLS_TESTS=1 pytest tests/test_rls_enforcement.py -v -rs` | 0 | 5.1 | 187 passed, 0 skipped |
| **Mutation contract** | `python -m tests.security_mutations --json …` | 0 | 521.3 | **37 killed / 37; 0 survived, 0 invalid, 0 equivalent, 0 not executed** |
| Chrome teacher review | `python frontend/tests/browser_review.py` | 0 | 2.6 | 6 of 6 scenario groups PASS |

Notes:

- The 187 skips in the no-DB run all have one reason ("AEOS_TEST_DATABASE_URL
  is not set"). They are exactly the 187 RLS tests that pass in required mode.
- Test-ID union check: every test ID collected at `origin/main` (170), #20
  (297), #22 (188) and #25 (185) is collected here (330 = 170 + 127 + 18 + 15).
  This includes all TRUNCATE (12), WHERE-less sweep (108) and `test_auth.py`
  (32) test IDs.
- Mutation kills by the new controls: M18h by
  `test_published_key_python_jose_cannot_load_is_401_not_a_server_error`;
  M18i–M18k by #22's auth tests; M19a by 13 `TestPrivilegesRlsDoesNotGovern`
  cases; M19b by `test_tables_created_later_do_not_inherit_rls_blind_privileges`;
  M20 by 4 `TestWherelessWritesAcrossEveryTable` cases. Each mutant was
  pre-checked (compiles and imports, or migrations 001–005 apply) before scoring.
- Chrome used Playwright's bundled Chromium in place of `google-chrome`, with
  the synthetic fixture (in-memory fakes, synthetic sessions). It does not show
  hosted Supabase persistence or live JWT interoperability.
- The worktree was clean afterwards except the known untracked
  `frontend/tsconfig.tsbuildinfo` (SEC-G1-09).

### How to reproduce

```bash
# disposable PostgreSQL 16; never a production database
export AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/<disposable_db>
(cd frontend && npm ci && npm audit --audit-level=low && npm audit --omit=dev --audit-level=low \
  && npm ls --all && node --experimental-vm-modules tests/assessment-api.test.mjs \
  && node tests/lint-glob-override.test.mjs && CI=1 npm run lint && npx tsc --noEmit && npm run build)
pip install -r backend/requirements-dev.txt
python -m compileall -q backend/app backend/tests
(cd backend && env -u AEOS_TEST_DATABASE_URL python -m pytest tests/ -v -rs)
(cd backend && AEOS_REQUIRE_RLS_TESTS=1 python -m pytest tests/ -v -rs)
(cd backend && python -m tests.security_mutations --json mutation-matrix.json)
```

## Outstanding gates (not addressed here)

| Gate | State | Evidence in this tree |
| --- | --- | --- |
| Live hosted-Supabase RLS (SEC-G1-01) | **BLOCKED** | Needs founder authorization of an isolated, non-production Supabase project with synthetic data. PostgreSQL 16 RLS tests are not a substitute. |
| Live JWT interoperability | **BLOCKED** | The project's signing key must be ES256 or RS256 (legacy HS256 projects cannot sign in, by design, per #22). Not observable from this environment. |
| Sign-in flow (SEC-G1-03) | **OPEN** | No sign-in UI. Pages read `localStorage['aeos_access_token']`; nothing in `frontend/src` writes it. Browser checks use synthetic sessions. |
| Student pages API base (SEC-G1-02) | **OPEN, partial** | Assessment pages use the shared client (#23). `src/app/students/page.tsx`, `students/new/page.tsx` and `students/[id]/page.tsx` still call `http://127.0.0.1:8000` directly. |
| AI features | **NOT BUILT** | No model-provider call exists in `backend/app` or `frontend/src`. #23 removed unsupported AI, outcome and readiness claims. Any AI module needs its own evaluation gate before claims. |
| Hosted deployment (Vercel/Supabase) | **NOT DONE** | No deployment was attempted or authorized. #20 notes a red Vercel status caused by the Root Directory project setting. |
| Independent P0 verification | **REQUIRED** | A separate session must reproduce this evidence from the exact head SHA under `.github/agents/aeos-p0-independent-verifier.agent.md`. |
| Remaining G1 ledger items | unchanged | SEC-G1-08 (mutation artifact named with the merge-ref SHA), SEC-G1-09 (`tsconfig.tsbuildinfo` not ignored) and #22's follow-ups (JWKS cache TTL, `exp` not required, python-jose CVEs, supabase-py new key format). |
