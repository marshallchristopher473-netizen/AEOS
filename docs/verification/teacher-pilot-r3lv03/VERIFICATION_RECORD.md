# AEOS teacher-pilot release candidate: independent verification

Date: 2026-10-17. Verifier: a separate Claude Code session (did not build the candidate).
Method: read the code, ran every check from clean detached worktrees with fresh
virtual environments, and wrote independent hostile probes. Builder summaries,
PR bodies and committed evidence were used only as a checklist.

**This record does not approve or publish a launch.**

## 1. Verdicts

| Verdict | Result | Why, in one line |
| --- | --- | --- |
| **P0 VERIFIED** | **NOT ISSUED. P0 REJECTED on the current candidate head** | The strict production `npm audit` required by the candidate's own P0 workflow fails (2 high). The hosted-Supabase gate and CI on the exact head are also BLOCKED. |
| **TECHNICAL PILOT READY** | **NOT ISSUED (FAIL)** | No sign-in, student pages fail in a real browser, no API deployment, no rollback/recovery procedure, and the teacher workflow definition is unresolved (owner decision D1). |
| Teacher value | **NOT TESTED** | No teacher has used the workflow. |
| Paid demand | **NOT TESTED** | No buyer conversation or transaction exists. |
| Launch approval sheet | **NOT PRODUCED** | Required evidence is absent (§7 lists what it needs). |

## 2. What was verified: identity and reconciliation

No repository record names a "selected" teacher-pilot candidate. I chose the
candidate with this rule and state it as an assumption:

> The newest open head that contains the full teacher workflow in scope (AI
> labeling, teacher approval, evaluator output, no gradebook publication).

| Item | Value | Status |
| --- | --- | --- |
| Candidate | PR #35, `claude/pr32-pter-reconcile-hcm5cf` | Draft, open, base = PR #32 branch (not `main`) |
| Candidate full SHA | `7a727920c6bf831a7dbc7951a5694bad2d77c23d` (tree `3dbf9525415a9d364b23bf53c7467dcae587d911`) | Rechecked on the remote at the end: unchanged |
| Lineage | `main` ⊂ #28 (RC) ⊂ #32 (AI feedback) ⊂ #35 | `git merge-base --is-ancestor` |
| Merged baseline | `main` = `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` | The only merged, publishable code |
| Parallel, not selected | PR #31 `37cd637ac1fce26f3d82f76ecb8ae2e08cffad58` (and #26) | A separate RC lineage. Not an ancestor of #35. **Needs an owner decision: one RC lineage, the other closed.** |
| Migration/schema version | Candidate: 001–006 (006 = `ai_feedback_drafts`). `main`: 001–004 | Applied cleanly to local PostgreSQL 16.15 |
| Supabase project | `AEOS-MVP` `hbcgsukmbgiytcznmmec` (named in `.replit` and the "Supabase Preview" check) is **INACTIVE (paused)**. `aeos-v05-verify-disposable` is active but refused migration listing (auth failure). | **BLOCKED.** The hosted schema version cannot be read. |
| API deployment | **None identified.** No Dockerfile, Procfile or host config for FastAPI in either SHA. | FAIL |
| Frontend build | Local only: `next build` exit 0 for both SHAs | Local evidence, not a published build |
| Served URL | Vercel project `aeos` (`prj_YN58grCsUbX3NNvC0ySXlBAfpNqR`) exists. Listing deployments returned **403**. | **BLOCKED.** The served SHA is unknown. |
| CI on the exact head | **None.** #35 targets a stacked branch, so `p0-backend-tests.yml` never ran. The only checks are a Vercel comment bot (success) and a Supabase preview (skipped). | BLOCKED |

**Reconciliation statement:** the repository head, my test runs and any
deployment cannot yet be tied together. Every PASS below is **local evidence
on the exact SHA**, not a published-build result.

## 3. Executed checks (this session)

Environment: Python 3.13.16 (CI pins 3.11), Node 22.22.0 / npm 10.9.4,
PostgreSQL 16.15 (disposable local cluster), Chromium 1194 through Playwright.

| # | Check | `main` b9c68aa | PR #35 7a72792 |
| --- | --- | --- | --- |
| C1 | `compileall` backend | exit 0 | exit 0 |
| C2 | `import app.main` | OK | OK |
| C3 | Full backend suite, `AEOS_REQUIRE_RLS_TESTS=1` | **170 passed, 0 skipped** | **538 passed, 0 skipped** |
| C4 | Mutation contract `python -m tests.security_mutations` | **30/30 killed**, 0 invalid | **37/37 killed**, 0 survived, 0 invalid, 0 not executed |
| C5 | Mutation anchor check | n/a | 37 anchors, exit 0 |
| C6 | `npm ci` | exit 0 | exit 0 |
| C7 | `npm audit --audit-level=low` (full tree) | **exit 1**: 1 critical (`next`), 8 high | **exit 1**: 2 high |
| C8 | `npm audit --omit=dev --audit-level=low` | not in workflow | **exit 1**: `next@16.3.6` high (Draft Mode leak via `use cache`), `sharp` high (librsvg) |
| C9 | lint / `tsc --noEmit` / `next build` | pass / pass / pass | pass / pass / pass |
| C10 | Frontend node tests (3 files) | n/a | all exit 0 |
| C11 | `git diff --check` b9c68aa..7a72792 | n/a | clean |
| C12 | PR #32 head `2674540` clean import | n/a | **fails**: `ModuleNotFoundError: app.models.ai_feedback` (confirms the #35 claim) |

### Independent hostile probes (my code, in `evidence/`)

**Direct database, migration 006, two synthetic tenants** (`hostile_probe.sql` → `hostile_probe_result.txt`):

| Probe | Actor | Expected | Observed |
| --- | --- | --- | --- |
| P1 | trigger | audit row per draft and decision, actor-correlated, no student text | 1 + 1 rows, `performed_by` = decider, 0 leaks |
| P2 | Org B teacher | sees none of A's requests, drafts, decisions or audit rows; none by id | 0 / 0 / 0 / 0 / 0 |
| P3 | Org B teacher | cannot write a decision on A's draft | rejected by integrity trigger |
| P4 | Org B teacher | cannot call the budget reservation RPC | permission denied |
| P5 | Org A teacher (positive control) | sees own decision | 1 |
| P6/P7 | Org A teacher | cannot UPDATE (no `WHERE`) or DELETE their own decision | `UPDATE 0`, `DELETE 0` |
| P8 | Org A teacher | cannot insert a decision directly (bypassing the API) | RLS violation |
| P9 | Org A teacher | cannot delete audit rows | `DELETE 0` |
| P10 | after attacks | stored decision text and counts unchanged | unchanged |
| P11 | disabled member | revoked: sees nothing | 0 |
| P12 | suspended org | revoked: sees nothing | 0 |
| P13 | anon | sees nothing | 0 |

**Malformed evaluator output against the production validator** (`malformed_output_result.txt`):
10 of 11 hostile outputs were rejected with a coded reason (prose, `null`,
array, unknown criterion, injected `score`/`grade`, 20,000-item array, `NaN`,
trailing garbage, BOM). **One defect:** 20,000-deep nested JSON raises an
unhandled `RecursionError`. See finding F3.

**Built frontend in Chromium against the candidate's loopback fixture API**
(`browser_probe.py` → `browser_probe_result.json`; the fixture API is in-memory with a deterministic provider):

| Check | Result |
| --- | --- |
| AI label visible ("does not score, diagnose, or decide anything"; nothing final until a decision) | PASS |
| Keyboard only (Tab plus Space/Enter): request a draft, edit, save a revision | PASS |
| Forced network failure on save: error shown, teacher text kept | PASS |
| Retry after failure reuses the same `Idempotency-Key` (2 sends, 1 key) | PASS |
| After hard reload / in a fresh browser context, the decision is still current | PASS (in-memory fixture, **not** durable storage) |
| Other-tenant session opening A's assessment URL | PASS ("Assessment not found") |
| No provider key or service-role string in the page | PASS |
| 375 px, assessment detail page (AI panel) | PASS (screenshot in `evidence/`) |
| 375 px, `/assessments` list | **FAIL**: scrollWidth 572 > 375 (table not wrapped) |
| `/students`, `/students/new`, `/students/[id]` in a real browser | **FAIL**: "Failed to fetch". The pages call `http://127.0.0.1:8000` cross-origin and the API has no CORS (preflight 405). |
| Console | Only a favicon 404 plus the forced abort |

## 4. Findings, most severe first

| ID | Severity | Finding | Evidence |
| --- | --- | --- | --- |
| F1 | Blocker | Strict production audit fails: `next@16.3.6` (high) and `sharp` (high). Under the candidate's no-exception policy, P0 CI would be red. The #35 PR body reports frontend checks as passing and does not mention the audit. | C7, C8 |
| F2 | Blocker | No sign-in path. Every page reads `localStorage['aeos_access_token']`, and nothing in the app writes it. A teacher cannot authenticate through the product. | `frontend/src/lib/api.ts:20`, student pages |
| F3 | Medium | A deeply nested evaluator response raises `RecursionError`. `create_draft` catches only `OutputRejected` (`service.py`, validation block), so the error escapes after the budget reservation and before any draft row: HTTP 500, then `request_in_progress` 409 on every replay of that key. It fails closed (no unsafe text is shown). Constrained decoding makes this unlikely live. Fix cost: one `except` clause. | `malformed_output_result.txt` |
| F4 | High | Student pages hardcode `http://127.0.0.1:8000`, and the API has no CORS. Broken in any browser and any deployment. Assessment pages use the same-origin `/api` rewrite and work. | browser probe, CORS preflight 405 |
| F5 | High | No API deployment target, no rollback procedure, no pilot recovery runbook. | §2, repo search |
| F6 | High | Teacher workflow definition unresolved. #35 records owner decision D1: PR #30's assisted condition shows AI rubric values, and PR #32 forbids them. The rubric RUB-CER3 is unapproved (pins empty). | PR #35 body, `docs/pilots/p-ter-01/` |
| F7 | High | `backend/app/models/ai_feedback.py` in #35 is a **reconstruction**. The original was never committed (`.gitignore` `models/`). Tests pass against it, but the file needs human review. | PR #35 commit `ed10dc9` |
| F8 | Medium | `/assessments` overflows at 375 px. | browser probe |
| F9 | Medium | Audit coverage applies only to AI-feedback tables (DB triggers in 006). Students, assessments, results and plans writes are not audited. | `grep audit_logs`, migration 006 |
| F10 | Low | Backend transitive dependencies are not locked (`requirements*.txt` pins only top level; dev uses `>=`). The frontend is lockfile-reproducible. | requirements files |
| F11 | Low | Two RC lineages (#31 vs #28→#35) both claim to integrate the same security PRs. | §2 |

**Verified as working (code read plus execution):** JWT verification
(signature, exp, iss, aud required, kid required, unknown kid refused);
tenant and role derived server-side from the DB row; suspension and disable
checks in both the app and RLS; service-role queries tenant-filtered;
immutable AI drafts and append-only decisions (DB trigger); idempotency with
payload hashing; org allowlist; feature flag **off by default**; rubric pin
required; secrets never in browser bundles, logs or settings `repr`. **No
student-facing or gradebook publication path exists**: the only outputs are
`ai_feedback_*` rows and audit rows, there is no export or notify route, and
the UI states nothing is shared.

## 5. Gate table

Status vocabulary: PASS / FAIL / BLOCKED / NOT TESTED. P0 IDs are the existing
`P0-C01…C10` from `.github/agents/aeos-p0-independent-verifier.agent.md`.
`TP-*` IDs are **proposed** (none existed). Env "local-PG16" = disposable local
PostgreSQL on the exact SHA. Owner "Builder" = the implementation agent
session, "Founder" = the repository owner.

| ID | Gate | Status | Owner | Dependency | SHA / version / env | Executed check | Evidence | Next bounded action | Compute |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0-C01 | Business routes require verified auth | PASS | Builder | — | 7a72792 / local | C3 (`test_route_authentication`), M01 killed | mutation-matrix-pr35 | none | — |
| P0-C02 | JWT alg/sig/exp/iss/aud/kid | PASS | Builder | — | 7a72792 / local | C3, M02/M18a–k killed | mutation-matrix-pr35 | none | — |
| P0-C03 | Actor from verified `sub` | PASS | Builder | — | 7a72792 / local | M03 killed | mutation-matrix-pr35 | none | — |
| P0-C04 | Tenant/role server-derived | PASS | Builder | — | 7a72792 / local | M04 killed, P2 | matrix, hostile_probe_result | none | — |
| P0-C05 | Collection/object reads scoped | PASS (local) | Builder | P0-C08 hosted | 7a72792 / local-PG16 | M05–M08, M15, P2 | same | hosted re-run | low |
| P0-C06 | Schemas can't supply tenant/user/role | PASS | Builder | — | 7a72792 | code read (`extra="forbid"`), tests | `app/models/*` | none | — |
| P0-C07 | Service role server-only | PASS | Builder | — | 7a72792 | M16 killed, bundle scan | browser probe | none | — |
| P0-C08 | RLS enforced, all operations | PASS local / **BLOCKED hosted** | Founder | Active isolated Supabase project | local-PG16; hosted unknown | C3, C4, P1–P13 | hostile_probe_result | Unpause or create an isolated project and run migrations 001–006 plus P1–P13 there | low, one session |
| P0-C09 | Two-tenant hostile tests | PASS local / **BLOCKED hosted** | Founder | P0-C08 | local-PG16 | P2–P4, browser other-tenant | evidence/ | same as P0-C08 | low |
| P0-C10 | Test coverage of attack classes | PASS | Builder | — | 7a72792 | 538 tests, 37/37 mutants | matrix | none | — |
| TP-01 | Strict dependency audit | **FAIL** | Builder | — | 7a72792 lockfile | C8 | §3 | Bump `next` and `sharp` to patched compatible versions, re-run audit, lint, build | low |
| TP-02 | CI on the exact head | **BLOCKED** | Builder | TP-01 | 7a72792 | none ran | PR #35 checks | Retarget the final RC PR to `main` (or push to a `p0/security-*` branch) so the workflow runs | low |
| TP-03 | One selected RC lineage | **BLOCKED** | Founder | — | #31 vs #35 | ancestry check | §2 | Choose one; close the other | none |
| TP-04 | Sign-in / session | **FAIL** | Builder | TP-03 | 7a72792 | code read, browser | F2 | Add a Supabase email sign-in page that stores the session; test valid, invalid and expired sessions | medium, one session |
| TP-05 | Invalid credentials refused | PASS (API) / NOT TESTED (UI) | Builder | TP-04 | 7a72792 | C3 auth tests | test_auth | UI test after TP-04 | low |
| TP-06 | Revoked access (disabled, suspended) | PASS local | Builder | P0-C08 | local-PG16 | P11, P12, M09/M10 | hostile_probe_result | hosted re-run | low |
| TP-07 | Student pages reach the API | **FAIL** | Builder | — | 7a72792 | browser | F4 | Point student pages at the `/api` rewrite (as assessment pages already do) | low |
| TP-08 | AI output labeled, teacher approval required | PASS | Builder | — | 7a72792 | code read, browser | browser probe | none | — |
| TP-09 | Teacher workflow definition (D1–D5) | **BLOCKED** | Founder | — | docs/pilots/p-ter-01 | doc read | F6 | Decide D1 (AI values shown or not) and D2–D5 in writing | none |
| TP-10 | Rubric approved and pinned | **BLOCKED** | Founder + qualified Grade 6–8 ELA reviewer | TP-09 | RUB-CER3 v0.1 | pins empty | manifest.json | Complete worksheet Part F, then pin the hash | none |
| TP-11 | Durable versions/records (immutable, append-only) | PASS local | Builder | P0-C08 | local-PG16 | P6–P10 | hostile_probe_result | hosted re-run | low |
| TP-12 | Persistence after hard reload / fresh session | PASS (fixture) / NOT TESTED (durable) | Builder | TP-04, hosted DB | fixture | browser | browser probe | Repeat against a hosted DB | low |
| TP-13 | Save-failure retention | PASS | Builder | — | built frontend | browser forced abort | browser probe | none | — |
| TP-14 | Idempotency / concurrency | PASS | Builder | — | 7a72792 / local-PG16 | C3 (`concurrent_reservations`, duplicate tests), browser key reuse | browser probe | none | — |
| TP-15 | Audit correlation | PASS for AI tables / **FAIL** for other writes | Builder | — | local-PG16 | P1, grep | F9 | Decide whether pilot scope needs student/assessment write audit; if yes, add triggers | low–medium |
| TP-16 | Malformed evaluator output | PASS 10/11, **FAIL** 1 (F3) | Builder | — | 7a72792 | malformed probe | malformed_output_result | Catch `RecursionError`/`ValueError` as `OutputRejected` and add a test | low |
| TP-17 | Live AI provider | NOT TESTED | Founder | TP-09, TP-10, API key | flag off | none | — | Provider smoke test on synthetic data after rubric approval | low |
| TP-18 | Keyboard completion | PASS | Builder | — | built frontend | browser | browser probe | none | — |
| TP-19 | Mobile overflow at 375 px | **FAIL** (`/assessments`) | Builder | — | built frontend | browser | browser probe | Wrap the table in a horizontal scroll container | low |
| TP-20 | Secrets/log exposure | PASS | Builder | — | 7a72792 | bundle scan, logger read, history scan | §4 | none | — |
| TP-21 | No student/gradebook publication | PASS | Builder | — | 7a72792 | route inventory, code read | §4 | none | — |
| TP-22 | API deployment | **FAIL** | Founder + Builder | TP-03 | none | repo search | F5 | Choose a host for FastAPI; add its config; record the URL and SHA | medium |
| TP-23 | Served build identified | **BLOCKED** | Founder | Vercel access, TP-22 | Vercel 403 | list_deployments | §2 | Grant read access or paste the production deployment SHA | none |
| TP-24 | Reproducible build | PASS frontend / **FAIL** backend lock | Builder | — | both SHAs | `npm ci` in clean worktrees; requirements read | F10 | Generate a hashed lock (`pip-compile --generate-hashes`) | low |
| TP-25 | Rollback procedure | **FAIL** | Builder | TP-22 | none | repo search | F5 | Write and rehearse: redeploy previous SHA plus the forward-only DB plan | low |
| TP-26 | Pilot recovery procedure (synthetic) | **FAIL** | Builder | TP-22, P0-C08 | none | repo search | F5 | Runbook: restore a synthetic tenant, verify P1–P13; rehearse once | low |
| TP-27 | Reconstructed models module reviewed | **BLOCKED** | Founder (human review) | — | 7a72792 `ed10dc9` | tests pass | F7 | Human line-by-line review of `app/models/ai_feedback.py` | none |
| TP-28 | Base44 boundary | **NOT TESTED / excluded** | Founder | — | both SHAs | repo search | §6 | Confirm in writing that no Base44 app holds Supabase keys for the pilot project | none |
| TP-29 | Teacher value | NOT TESTED | Founder | all TP | — | — | — | Pilot measurement plan | — |
| TP-30 | Paid demand | NOT TESTED | Founder | TP-29 | — | — | — | Paid-pilot offer | — |

## 6. Base44

Treated as **excluded**. Boundary evidence:

- No Base44 code, config, SDK or reference exists at either SHA (`git grep -i base44`: 0 hits).
- The API accepts only asymmetric Supabase JWTs verified against the configured JWKS, and then requires an active DB user row in an active organization (`app/core/auth.py`, `app/core/dependencies.py`). A token from any other issuer is refused (M02/M18 killed).
- The service-role key is server-only (M16 killed; bundle scan clean).

**Not provable from here:** whether a Base44 app outside this repository holds
a Supabase key for the pilot project. That key-holder inventory needs the
Supabase dashboard. Optional Base44 access stays **NOT TESTED/excluded**. If
Base44 is ever included, identity, authorization, persistence and
published-build tests become required.

## 7. Launch approval sheet

**Not produced.** It requires, at minimum: TP-01, TP-02, TP-03, TP-04,
TP-07, TP-09, TP-10, TP-22, TP-23, TP-25 and TP-26 to PASS; P0-C08/C09 to
PASS on the hosted project; and TP-27 human review signed.

## 8. Prior evidence (preserved, not re-used)

| Source | Claim | My reproduction |
| --- | --- | --- |
| PR #35 body | 538 passed, 37/37 killed | **Matches** (538 passed; 37/37) |
| PR #35 body | Frontend checks pass | lint/tsc/build match; **audit fails** (not mentioned) |
| PR #35 body | #32 head does not import | **Matches** |
| `docs/evidence/rc-20261010/*` (builder) | 0 killed, 37 invalid (no DB) | Superseded for this SHA by my 37/37 run; the file is left unchanged |
| PR #21 / PR #29 | historical P0 records | Not used as evidence for this head |

## 9. Unrelated backlog (kept separate, not gated here)

- PRs #18 (presentation agents) and #19 (lead qualification) are outside the pilot.
- `backend/app/**/__pycache__/*.pyc` is committed on `main` (9 files).
- Legacy `AEOS_Vercel_Deploy.sh` would scaffold Next 14.2.15.
- `/health` is public and returns setup hints; `/docs` and `/openapi.json` are public.
- `teacher_confirmed` is always set to `true` server-side, so the column carries no signal.
