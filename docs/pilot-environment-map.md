# Pilot Environment Map — Teacher ELA Short-Response Pilot

| Field | Value |
| --- | --- |
| Inventory date | 2026-10-17 |
| Method | Read-only. Git, GitHub, the Vercel API and the Supabase management API. No code, schema, configuration or deployment was changed. No secret values were read or printed. |
| Verdict | **BLOCKED.** A Vercel project `aeos` (root `frontend/`) exists, but its production build and environment variables are not readable with the available credentials. No deployed backend could be found. The only hosted database that names AEOS is paused, so it could not be inspected. |
| Companion | [`pilot-backend-contract.md`](pilot-backend-contract.md) |

A blank cell means the value could not be verified. Nothing has been filled in by inference.

---

## 1. Repository candidate

| Item | Value | Evidence |
| --- | --- | --- |
| Repository | `marshallchristopher473-netizen/AEOS` | git remote |
| Default branch `main` | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` | `git rev-parse origin/main`. Merge of PR #17. |
| Does `main` contain any ELA short-response pilot operation? | **No** | The routers on `main` (`backend/app/main.py`) are `/health`, `/assessments`, `/assessment-results`, `/students` and `/intervention-plans`. |
| Pilot candidate branch | `claude/pr32-pter-reconcile-hcm5cf` (PR #35, open, not merged) | GitHub PR list, `git log origin/main..` |
| Pilot candidate full SHA | `7a727920c6bf831a7dbc7951a5694bad2d77c23d` | `git rev-parse` |
| Stack below the candidate | PR #35 → PR #32 (`ccr-e346b2cd-z98173` @ `26745404d799511717f9053171ad857529704540`) → PR #28 (`p0/security-release-candidate-20261010` @ `38167733b6b1639d480ba0e1a4b5bf7cf331620c`) → `main` | `git log` on each branch |
| Why #35 and not #32 | PR #32's head does not import from a clean checkout: `backend/app/models/ai_feedback.py` was never committed because `.gitignore` rule `models/` ignored it. PR #35 commit `ed10dc9` **reconstructs** the module and fixes `.gitignore`. | `docs/pilots/p-ter-01/README.md` @ 7a72792 |
| Candidate status as its own docs record it | Feature flag `AEOS_AI_FEEDBACK_ENABLED=false`. Rubric approval pins empty. Synthetic data only. P-TER-01 v0.3 protocol `SOURCE_NOT_LOCATED`. Reconstructed module still needs human review. | `docs/pilots/p-ter-01/README.md`, `docs/pilots/p-ter-01/manifest.json` @ 7a72792 |
| CI on the exact candidate SHA | *(unverified)* | Not inspected in this task |

**Selection rule.** PR #35 is the only ref that carries the pilot's AI feedback workflow and imports from a clean checkout. It is recorded as the candidate because of that evidence. No owner has designated it in a repository artifact. If the owner intends a different ref, that ref must be named. No other branch was substituted.

## 2. Environment mapping

| Environment | Frontend build | API / backend deployment | Supabase project (ref) | DB engine (reported) | Evidence |
| --- | --- | --- | --- | --- | --- |
| Local development | `frontend/` (Next.js `^16.3.6` at candidate), `next dev` | `uvicorn app.main:app` on port 8000 | Whatever `backend/.env` names. *(not in repo)* | n/a | `backend/.env.example`, `frontend/.env.example` |
| Replit workspace | none configured | `.replit` runs `uvicorn app.main:app --port 8000` and maps it to port 80 | `hbcgsukmbgiytcznmmec` (AEOS-MVP). Only `SUPABASE_URL` is set in `.replit`. | `17.6.1.155` | `.replit` `[userenv.shared]` |
| Replit published deployment | | | | | Not observed. No deployment artifact or URL found. |
| Vercel production | Project `aeos` (`prj_YN58grCsUbX3NNvC0ySXlBAfpNqR`, team `team_3l5DZy3Rr91pttvZdWfgQ9KJ`), root directory `frontend`, Git-linked to this repository. Production deployment ID, SHA and URL: | Value of `AEOS_API_URL`: | Not configured in the frontend. Value: | The project's existence, root directory and Git link come from the `vercel[bot]` comment on PR #37 (2026-10-17). The Vercel connector returned `404` for `get_project` and `403` for `list_deployments` on this project, and `list_projects` did not return it. Production build and environment variables are therefore **unverified**. |
| Vercel preview (this PR) | `aeos-git-claude-aeos-ela-924c3b-christopher-marshall-s-projects.vercel.app`, built from `claude/aeos-ela-pilot-verify-e4ittf` (docs-only). Status `Ready`. | | | | `vercel[bot]` comment on PR #37. The frontend code in this preview is `main`'s, not the candidate's. |
| Vercel, other project | `neurolearning-os` (`prj_BHeDWrfnpdHanriHF7BzicI2AOpz`). Latest production deployment `ERROR`, `live: false`. | n/a | | | Vercel API. No git link to this repository was returned. **Not** mapped to AEOS. |
| GitHub Actions CI | `npm` build and tests | pytest | Ephemeral `postgres:16` service container (not Supabase) | PG 16 | `.github/workflows/p0-backend-tests.yml` |
| Disposable verification DB | n/a | n/a | `doblbkfogcykpfwkfycs` (`aeos-v05-verify-disposable`, ACTIVE_HEALTHY) | `17.6.1.166` | Supabase API. Read access failed with `28P01` password authentication. No repository config points at it. |
| Other Supabase project | n/a | n/a | `drcetslvctzkgaxvzerq` (`GradeFreed-AI`, INACTIVE) | `17.6.1.147` | Supabase API. No repository config points at it. |
| Base44 checkpoint | Base44-hosted UI | `AEOS_API` integration **disabled** (reported) | Base44's own data store (reported) | | Reported by the owner as synthetic-demo evidence. Not inspected here. |

Project names alone were not treated as a mapping. AEOS-MVP is linked to this repository in two observable places:

1. `.replit` (`SUPABASE_URL`).
2. The Supabase GitHub integration. Its `Supabase Preview` check on PR #37 points at `supabase.com/dashboard/project/hbcgsukmbgiytcznmmec/branches` (conclusion `skipped`, 2026-10-17).

Neither link shows that a deployed backend uses this project. No repository file references `doblbkfogcykpfwkfycs` or `drcetslvctzkgaxvzerq`.

## 3. Database reconciliation: AEOS-MVP (`hbcgsukmbgiytcznmmec`)

| Question | Repository (`main` @ b9c68aa) | Candidate (@ 7a72792) | Hosted AEOS-MVP |
| --- | --- | --- | --- |
| Versioned migrations | `001`–`004` | `001`–`006` | **0 recorded** (reported). Could not re-check: project `INACTIVE`, connection timed out. |
| Public tables | 11: organizations, schools, users, students, assessments, ai_recommendations, intervention_plans, intervention_actions, progress_events, audit_logs (001); assessment_results (003) | 14: the 11 above plus `ai_feedback_requests`, `ai_feedback_drafts`, `ai_feedback_decisions` (006) | **13** (reported). Not re-checked. |
| RLS | Enabled **and** forced, with tenant policies (002–004) | Same, plus SELECT-only policies on the 3 feedback tables (006). TRUNCATE/TRIGGER/REFERENCES revoked from client roles (005). | RLS enabled, **no policies** (reported) |
| Legacy setup script | `AEOS_Supabase_Setup.sql` creates 11 tables (including `notes` and `ai_recommendation_runs`) and enables **no** RLS | unchanged | |
| Security advisors | | | `get_advisors(security)` returned an empty list on 2026-10-17. A paused project may not be evaluated, so this is **not** evidence of a clean state. |

**Reconciliation finding.** The hosted state matches neither `main` nor the candidate.

- No recorded migrations means the policies and functions in 002–006 are not applied the way the repository defines them.
- 13 tables is neither 11 nor 14.
- A union of the legacy setup script (11 tables) and 001's `ai_recommendations` and `progress_events` would give 13. That is a **hypothesis only** and could not be checked.
- The three `ai_feedback_*` tables that the pilot routes need cannot be present in a 13-table schema that also holds the 11 core tables. So the candidate backend cannot run its pilot routes against AEOS-MVP as reported.
- RLS with no policies denies `anon` and `authenticated` by default. That fails closed for client roles. It does nothing for the backend, which uses the service role and bypasses RLS (see the contract §4).

Historical PR checks ran against PostgreSQL 16 containers in CI, not against this project. They are **not** evidence about the hosted state.

## 4. Identity systems (kept separate)

| Identity system | Where it's used | Token issuer | Trusted by the AEOS backend? |
| --- | --- | --- | --- |
| Supabase Auth for the project named by `SUPABASE_URL` | AEOS backend (`get_current_user`) | `SUPABASE_JWT_ISSUER`, default `${SUPABASE_URL}/auth/v1` | **Yes.** Only this issuer, and only signatures from that project's JWKS. |
| Supabase Auth on other projects (GradeFreed-AI, disposable) | none in repo | their own issuers | No. The issuer must match exactly. |
| Base44 user identity | Base44 checkpoint | Base44 | **No.** No code accepts Base44 tokens. No email matching exists. `users.auth_user_id` is matched to the JWT `sub` only. |

Bridging Base44 users to AEOS users would need an explicit, designed identity link. None exists, and none should be assumed.

## 5. Platform changes relevant to this inventory

| Item | Applies to | Status | Action taken |
| --- | --- | --- | --- |
| Postgres security upgrade advisory (reported by owner) | AEOS-MVP `17.6.1.155`; GradeFreed-AI `17.6.1.147`; disposable `17.6.1.166` | The advisory text, its affected range and its fixed version were **not** observed through the API (advisor list empty, project paused). The fixed version and whether `17.6.1.155` is affected are left blank. | **None.** No upgrade was started. |
| Supabase asymmetric JWT signing keys (ES256/RS256) and the JWKS path `/auth/v1/.well-known/jwks.json` | Backend auth | Candidate accepts ES256 or RS256 and uses the documented path. `main` accepts RS256 only, at `/auth/v1/jwks`. Which signing key the hosted project actually uses is unverified. | None |
| Paused (INACTIVE) projects | AEOS-MVP, GradeFreed-AI | Paused. A restore changes compute state and is out of scope here. | None |
| Next.js 16 upgrade | Frontend | Merged on `main` (`ffc4d8b`) | None |

## 6. Blocking gaps (environment)

| # | Gap | Missing artifact |
| --- | --- | --- |
| E1 | Vercel project `aeos` exists, but its production deployment and its `AEOS_API_URL` are unverified | Production deployment ID and SHA, plus whether `AEOS_API_URL` is set (name only, no value). Needs Vercel access that can read `prj_YN58grCsUbX3NNvC0ySXlBAfpNqR`. |
| E2 | No deployed AEOS backend | A deployment record (URL, platform, deployed SHA) for `backend/` |
| E3 | Pilot database state is unknown and diverges from the repo | AEOS-MVP restored for read-only inspection, or a decision to use a fresh project built only from migrations 001–006 |
| E4 | Candidate is unmerged and contains a reconstructed module | Human review of `backend/app/models/ai_feedback.py` @ 7a72792, then a merge decision |
| E5 | Postgres advisory not tied to a version | Advisory ID or text with its fixed version |
| E6 | CI not confirmed on the exact candidate SHA | A green CI run on `7a72792` |
| E7 | `frontend-validation` fails on `main`'s lockfile. `npm audit` reports `next` 16.0.0–16.3.7 (critical, GHSA-vcvr-r3jv-pc5j and others), plus `sharp` and `source-map-js` (high). Seen on PR #37, which touches no frontend files. On the same head, `backend-tests` and `rls-enforcement` passed. | A bounded dependency PR that moves `next` past 16.3.7 |

## 7. Source references

- `.replit`; `replit.md`; `AEOS_Vercel_Deploy.sh`; `AEOS_Supabase_Setup.sql`
- `backend/app/core/config.py`, `backend/.env.example` (main and @ 7a72792)
- `frontend/next.config.mjs`, `frontend/.env.example`, `frontend/src/lib/api.ts` @ 7a72792
- `backend/supabase/migrations/001`–`006` @ 7a72792
- `docs/pilots/p-ter-01/README.md` @ 7a72792
- Supabase management API: `list_projects`, `get_project`, `get_advisors` (2026-10-17). Failed calls: `list_tables` and `list_migrations` on AEOS-MVP (timeout), and on the disposable project (`28P01`).
- Vercel API: `list_teams`, `list_projects`, `get_project` (2026-10-17). `get_project` → `404` and `list_deployments` → `403` for `prj_YN58grCsUbX3NNvC0ySXlBAfpNqR`.
- `vercel[bot]` comment on PR #37 (2026-10-17), which identifies project `aeos`, root `frontend` and the preview URL
