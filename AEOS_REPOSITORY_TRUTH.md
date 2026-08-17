# AEOS Repository Truth — B01

**Audit date:** 2026-08-17  
**Audit scope:** canonical remote repository state for `marshallchristopher473-netizen/AEOS`  
**Source branch:** `main`  
**Source SHA:** `4fc0533c40c0290f84df3b4641c5a2bb1066ce46`  
**Audit branch:** `audit/b01-repository-truth`  
**Product changes made:** none

## B01 status

**PARTIAL — remote repository audit complete; fresh-Codespaces shell verification remains NOT TESTED.**

This document records only evidence available from the canonical GitHub repository. The GitHub connector cannot execute shell commands inside a fresh Codespace, so the requested `git status`, local branch view, filesystem `find`, and fresh-runtime test/build commands are not claimed as executed.

No feature, schema, security, dependency, deployment, or application behavior was changed during B01.

## Requested B01 shell commands

The following commands remain to be run in a fresh Codespace created from current `main` before B01 is promoted from PARTIAL to COMPLETE:

```bash
git status --short --branch
git rev-parse HEAD
git branch -a
git log --oneline --decorate -15
find . -maxdepth 3 -type f | sort | sed -n '1,240p'
```

### Remote-equivalent GitHub evidence already collected

- Default branch: `main`.
- Current `main` SHA: `4fc0533c40c0290f84df3b4641c5a2bb1066ce46`.
- `main` is currently **not protected**.
- Remote branches were enumerated through the GitHub API.
- The recent commit history was enumerated through the GitHub API.
- The repository tree and launch-critical files were inspected through the GitHub API.
- Open pull requests and current execution issues were inspected.

## Remote branches observed

- `main` — `4fc0533c40c0290f84df3b4641c5a2bb1066ce46`
- `fix/p0-0-stabilization-reconstruction` — `4c503a78a4075c4f5fd8740db0eba8da745f7c12`
- `fix/p0-stabilization` — `616dbe7274133acb223a5757f7ea4e28afda81ce`
- `feat/org-data-access-layer` — `6466021227c4e708f1234d96e0c3c2efe2bff5e7`
- `docs/aeos-grading-mvp-blueprint` — `6466021227c4e708f1234d96e0c3c2efe2bff5e7`
- `copilot/establish-repository-state` — `dfcacc5863065a3e1d89b38f3c3c7ec70dca4a2c`
- `copilot/fix-failing-copilot-job` — `cf7079f418397c0944f30fde8f718c484749ca5c`
- `copilot/install-claude-cli-tool` — `d7cc027b19f78e72f507c94a3bd5b1fde8e2b34a`
- `copilot/research-current-repo-state` — `001bf12123cce0a61a2d63a316d3be44572292ae`
- `copilot/task-288473297-1302291425-a8c60967-721b-41aa-aeb2-4df2aeaaaddd` — `001bf12123cce0a61a2d63a316d3be44572292ae`

These branches are not all active architecture. Several are historical Copilot/reconstruction branches and must not be treated as canonical merely because they exist remotely.

## Open pull requests observed

### PR #2 — `fix(P0.0): stabilize backend imports and test dependencies`

- Draft.
- Head: `fix/p0-stabilization`.
- The branch has diverged from current `main`.
- Historical PR evidence reports backend tests, frontend lint, and frontend build passing on that older branch.
- Those results are **not** accepted as fresh verification of current `main`.

### PR #5 — `Document safe optional Claude Code CLI setup for AEOS contributors`

- Draft.
- Documentation/tooling only.
- Not required for B01/B02.
- Must not distract from the P0 launch path.

## Architecture map

### Root

The repository contains platform documentation/setup artifacts, including:

- `README.md`
- `AEOS_Project_Structure.md`
- `AEOS_MVP_Roadmap.md`
- `AEOS_Backend_FastAPI_Setup.sh`
- `AEOS_Vercel_Deploy.sh`
- `AEOS_Supabase_Setup.sql`
- `AGENTS.md`

`AEOS_Supabase_Setup.sql` exists at the root in addition to the canonical migration path. Under the current P0 operating rule, `backend/supabase/migrations/` should be treated as the future migration source; the root SQL file is therefore **PROVISIONAL/HISTORICAL**, not automatically authoritative.

### Backend

Framework: FastAPI.

Canonical app structure exists under `backend/app/`:

- `main.py`
- `api/`
- `core/`
- `models/`
- `services/`

Registered API routers on `main`:

- health
- students
- assessments
- intervention plans

Backend tests present:

- `test_auth.py`
- `test_students.py`
- `test_assessments.py`
- `test_intervention_plans.py`

Development dependencies are declared in `backend/requirements-dev.txt`.

### Frontend

Framework: Next.js 14 / React 18 / TypeScript.

`frontend/package-lock.json` is committed.

Current app routes visibly include:

- student list
- student detail
- new student
- assessment list
- assessment detail
- new assessment

`frontend/src/lib/api.ts` defines a shared API helper that reads `aeos_access_token` from `localStorage` and sends a bearer token.

However, some pages bypass the helper and call `http://127.0.0.1:8000` directly.

`frontend/package.json` currently provides:

- `dev`
- `build`
- `start`
- `lint`

It does **not** provide a frontend `test` script or explicit `typecheck` script.

### Database / Supabase

Canonical migration directory exists:

`backend/supabase/migrations/`

Current migration inventory:

- `001_initial_schema.sql`

The migration defines:

- organizations
- schools
- users
- students
- assessments
- AI recommendations
- intervention plans
- intervention actions
- progress events
- audit logs

It also contains demo/synthetic seed rows directly in the migration.

No `assessment_results` table is present in the inspected canonical migration.

No Row Level Security enablement or policies are present in the inspected canonical migration.

### CI

Current workflow:

`.github/workflows/p0-backend-tests.yml`

It performs:

- Python 3.11 setup
- backend dependency install
- compile check
- backend import checks
- backend pytest suite
- assessment test rerun

Current limitations:

- backend only
- no frontend build/lint/typecheck gate
- no direct RLS test gate
- no cross-tenant attack gate
- push trigger targets the old reconstruction branch, not `main`
- `main` currently has no branch protection

## Launch-critical subsystem status

| Subsystem | Status | Evidence / reason |
|---|---|---|
| Canonical repository identity | **VERIFIED** | `main` and SHA resolved through GitHub |
| Backend module structure | **VERIFIED** | FastAPI app, routes, core, models, services present |
| Frontend module structure | **VERIFIED** | Next.js app, lockfile, routes and API helper present |
| Canonical migration directory | **VERIFIED** | `backend/supabase/migrations/001_initial_schema.sql` present |
| Fresh Codespaces working tree | **NOT TESTED** | GitHub connector cannot run `git status` inside Codespaces |
| Fresh `main` backend runtime | **NOT TESTED** | must run in B02 Codespace |
| Fresh `main` frontend build | **NOT TESTED** | must run in B04 Codespace |
| JWT signature verification code | **PARTIAL** | JWKS + RS256 path exists |
| JWT audience verification | **BLOCKED** | current code explicitly uses `verify_aud: False` |
| JWT issuer verification | **MISSING** | no expected issuer validation observed |
| JWKS rotation/refresh behavior | **PARTIAL** | global cache exists; no verified refresh-on-missing-key behavior |
| Authenticated DB-user helper | **PARTIAL** | helper exists but maps by email and uses admin client |
| Auth enforcement on Student routes | **BLOCKED** | routes do not depend on authenticated user |
| Auth enforcement on Assessment routes | **BLOCKED** | routes do not depend on authenticated user |
| Auth enforcement on Intervention routes | **BLOCKED** | routes do not depend on authenticated user |
| Server-derived organization identity | **BLOCKED** | client-supplied organization ownership remains in API models |
| Server-derived actor identity | **BLOCKED** | client-supplied `created_by` remains in assessment/intervention flows |
| Tenant-scoped Student reads/writes | **BLOCKED** | admin client queries raw IDs without organization filter |
| Tenant-scoped Assessment reads/writes | **BLOCKED** | admin client queries raw IDs without organization filter |
| Tenant-scoped Intervention reads/writes | **BLOCKED** | admin client queries raw IDs without organization filter |
| RLS | **MISSING** | no RLS enablement/policies in canonical migration |
| Cross-tenant attack tests | **MISSING** | current test inventory does not prove tenant isolation |
| Student workflow integration | **BLOCKED** | frontend omits required backend `organization_id`; DB also requires `created_by` |
| Assessment workflow integration | **BLOCKED** | UI asks user to type `organization_id` and `created_by`; unsafe ownership contract |
| Intervention workflow | **PARTIAL/BLOCKED** | API exists but ownership/auth boundary is unsafe |
| AssessmentResult | **MISSING** | no inspected route/table in canonical `main` path |
| Recommendation API | **MISSING** | table exists, no registered router observed |
| Progress/evidence API | **MISSING** | table exists, no registered router observed |
| Grade 6–8 ELA evaluation harness | **MISSING** | remains blocked behind P0 Security |
| Backend CI | **PARTIAL** | backend workflow exists but is not a full launch gate |
| Frontend CI | **MISSING** | no frontend workflow gate observed |
| Branch protection | **MISSING** | `main` reports protection disabled |
| Deployment verification | **NOT TESTED** | no B01 runtime/deployment claim made |

## P0 Security findings

### P0-1 — Business routes do not enforce authentication

Student, Assessment, and Intervention routes invoke the Supabase admin client directly and do not require `get_current_user` or `get_db_user`.

**Impact:** a bearer token supplied by the frontend is not sufficient protection if the backend route never validates it.

### P0-2 — JWT verification is incomplete

The current verifier checks RS256 signature material and expiration but explicitly disables audience verification. Expected issuer validation was not observed.

### P0-3 — Client controls tenant/actor identifiers

Current request contracts permit client-controlled `organization_id`; assessment and intervention flows also permit client-controlled `created_by`.

**Impact:** tenant and actor identity are not derived from authenticated server context.

### P0-4 — Admin client is used as routine application data access

Student, Assessment, and Intervention routes/services use `get_supabase_admin_client()` for ordinary request handling.

**Impact:** database RLS cannot serve as meaningful defense-in-depth when routine application requests bypass it with service-role access.

### P0-5 — RLS is absent from the canonical migration

The inspected `001_initial_schema.sql` creates tenant-owned tables but does not enable RLS or define tenant policies.

### P0-6 — Cross-tenant regression evidence is absent

Current tests cover basic auth and resource behavior but do not establish direct organization isolation for Student, Assessment, AssessmentResult, or Intervention resources.

### P0-7 — Student contracts are structurally inconsistent

- Backend `StudentCreateRequest` requires `organization_id`.
- Current Student frontend creation payload omits `organization_id`.
- Canonical database schema requires `created_by` for Student rows.
- Current Student creation API model does not supply `created_by`.

The current end-to-end Student create path is therefore **BLOCKED** pending runtime confirmation and contract correction.

### P0-8 — Assessment intake exposes ownership controls to the browser

The current Assessment UI presents editable `organization_id` and `created_by` inputs. This conflicts with the P0 rule that organization and actor identity must be derived server-side.

### P0-9 — `main` is unprotected

Required security/test checks are not enforced by branch protection at the repository level.

## Test/build evidence available before B02

### Repository-visible evidence

- Backend test files are present.
- A backend GitHub Actions workflow is present.
- The corrected Copilot-agent guidance PR previously received a successful backend workflow run on its PR head before merge.
- Older draft PR #2 reports `9 passed`, frontend lint success, and frontend build success on its older branch.

### What is **not** claimed

Those historical/PR results are **not** a substitute for a fresh deterministic run on current `main` SHA `4fc0533c40c0290f84df3b4641c5a2bb1066ce46`.

Current `main` backend tests: **NOT TESTED in fresh Codespaces during B01**.  
Current `main` frontend lint/build: **NOT TESTED in fresh Codespaces during B01**.

## Demo / provisional / contradictory paths

- Root `AEOS_Supabase_Setup.sql`: **PROVISIONAL/HISTORICAL** relative to canonical migration directory.
- Multiple stale Copilot/reconstruction branches: **PROVISIONAL/HISTORICAL**, not canonical architecture.
- PR #2: useful historical verification evidence but branch has diverged from current `main`.
- Direct hard-coded frontend calls to localhost coexist with `frontend/src/lib/api.ts`: **PARTIAL/CONTRADICTORY API client path**.
- Compiled Python `__pycache__` artifacts are committed under backend paths: repository-hygiene issue, not a B01 fix.

## B01 conclusion

The repository has a real FastAPI + Next.js + Supabase MVP skeleton and basic Student/Assessment/Intervention implementations. It is **not yet safe to proceed to grading or other feature expansion**.

The central launch blocker is not missing UI. It is the absence of a verified server-side tenant boundary and RLS defense-in-depth on canonical `main`.

**B01 release decision: NOT READY FOR FEATURE WORK.**

## Immediate B02 action — deterministic backend environment verification

First, in a fresh Codespace from current `main`, run the five pending B01 shell commands and confirm:

1. branch is `main`;
2. HEAD is `4fc0533c40c0290f84df3b4641c5a2bb1066ce46` unless `main` has intentionally advanced;
3. working tree is clean.

Then begin B02 without changing product code:

```bash
python --version
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m compileall -q app tests
python -c "from app.main import app; print('backend OK')"
python -c "from app.models.schemas import AssessmentCreateRequest, AssessmentResponse; print('schemas OK')"
python -c "from app.core.dependencies import get_db_user; print('dependencies OK')"
python -m pytest tests/ -v
```

Record:

- Python version
- dependency-install result
- import results
- complete pytest totals
- warnings
- failures/blockers

Do **not** fix security or feature code during B02. If the deterministic backend environment does not reproduce, stop and classify the failure before proceeding to P0 Security implementation.

## Definition of B01 completion

B01 becomes **COMPLETE** only when the fresh Codespaces shell output is captured and reconciled with this remote audit. Until then, remote architecture/security truth is established, but local-runtime truth remains explicitly **NOT TESTED**.
