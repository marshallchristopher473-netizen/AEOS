# AEOS Repository Truth Report

Generated: 2026-08-17 (UTC)

## branch
- [VERIFIED] Current branch: `copilot/establish-repository-state`

## HEAD SHA
- [VERIFIED] `001bf12123cce0a61a2d63a316d3be44572292ae`
- [VERIFIED] Repository is shallow: `git rev-parse --is-shallow-repository` => `true`

## Git state
- [VERIFIED] Git status is clean (`git status --short --branch`)
- [VERIFIED] Local branches: `copilot/establish-repository-state`
- [VERIFIED] Remote-tracking branches fetched locally: `origin/copilot/establish-repository-state`
- [VERIFIED] Remote heads discovered via `git ls-remote --heads origin`:
  - `copilot/establish-repository-state` -> `001bf12123cce0a61a2d63a316d3be44572292ae`
  - `docs/aeos-grading-mvp-blueprint` -> `6466021227c4e708f1234d96e0c3c2efe2bff5e7`
  - `feat/org-data-access-layer` -> `6466021227c4e708f1234d96e0c3c2efe2bff5e7`
  - `fix/p0-0-stabilization-reconstruction` -> `4c503a78a4075c4f5fd8740db0eba8da745f7c12`
  - `fix/p0-stabilization` -> `616dbe7274133acb223a5757f7ea4e28afda81ce`
  - `main` -> `001bf12123cce0a61a2d63a316d3be44572292ae`
- [PARTIAL] Recent commit history available locally is limited by shallow clone (2 commits visible):
  - `001bf12` fix(P0.0): Restore backend module structure and test dependencies
  - `6466021` feat: assessment intake with auth and frontend UI

## architecture map
- [VERIFIED] `backend/` FastAPI service
  - `app/main.py` wires routers: health, assessments, students, intervention-plans
  - Supabase access in `app/services/supabase_service.py`
  - JWT verification helper in `app/core/auth.py`
- [VERIFIED] `frontend/` Next.js app-router UI
  - Student pages: list/new/detail
  - Assessment pages: list/new/detail
  - API helper in `src/lib/api.ts`
- [VERIFIED] `backend/supabase/migrations/001_initial_schema.sql` contains initial schema + seed rows
- [VERIFIED] Root SQL file `AEOS_Supabase_Setup.sql` defines a second schema variant
- [VERIFIED] CI workflow exists: `.github/workflows/p0-backend-tests.yml`
- [PARTIAL] Deployment config is script-driven (`AEOS_Vercel_Deploy.sh`, `.replit`) with no complete production IaC manifests (no Render/Railway/Fly config found)

## implemented functionality
- [VERIFIED] Backend health endpoint: `GET /health`
- [VERIFIED] Backend create/get by id:
  - `POST /students`, `GET /students/{id}`
  - `POST /assessments`, `GET /assessments/{id}`
  - `POST /intervention-plans`, `GET /intervention-plans/{id}`
- [VERIFIED] Frontend pages exist for student + assessment create/list/detail flows
- [VERIFIED] Supabase client/service-role client factories exist
- [VERIFIED] JWT verification utility exists (Supabase JWKS)

## partially implemented functionality
- [PARTIAL] Authentication plumbing exists (`get_current_user`, `get_db_user`) but API routes do not enforce auth dependencies
- [PARTIAL] Organization field exists in payloads/tables, but route-level org scoping/authorization checks are absent
- [PARTIAL] Frontend uses token from `localStorage`, but there is no sign-in/logout/profile workflow in repo
- [PARTIAL] Frontend list pages call list endpoints (`GET /students?search=...`, `GET /assessments`) that are not implemented in backend
- [PARTIAL] Schema includes broader entities than API currently exposes

## demo-only functionality
- [PROVISIONAL] `backend/supabase/migrations/001_initial_schema.sql` inserts fixed demo organization/school/user/student seed records
- [PROVISIONAL] Setup shell scripts scaffold starter code and appear bootstrap-oriented rather than production runtime
- [PROVISIONAL] Tests rely on fake Supabase clients (unit-level stubs), not integration with live Supabase

## missing functionality
- [MISSING] No backend endpoints for `assessment_results`
- [MISSING] No backend endpoints for recommendations (`ai_recommendations` / `ai_recommendation_runs` generation/review workflow)
- [MISSING] No backend endpoints for progress tracking (`progress_events`) beyond schema presence
- [MISSING] No explicit grading engine/grade-calculation implementation (only `grade_level` student field)
- [MISSING] No RBAC enforcement by role on API routes
- [MISSING] No complete auth session endpoints (`/auth/login`, `/auth/logout`, `/auth/me`) in backend
- [MISSING] No audit-log write path in API handlers
- [MISSING] No CI workflow for frontend lint/build/tests

## security blockers
- [VERIFIED] Service-role Supabase client is used directly in public route handlers (students/assessments/intervention-plans) without auth dependency; this is high-risk if exposed
- [VERIFIED] API handlers do not check caller organization against requested `organization_id`; cross-tenant access risk
- [VERIFIED] `.replit` contains a real Supabase project URL in committed config
- [VERIFIED] Tracked `__pycache__/*.pyc` artifacts exist in git history (`git ls-files`), indicating build artifacts committed to source control
- [PARTIAL] Frontend currently stores bearer token in `localStorage` (XSS-sensitive pattern); no compensating controls are visible in repo

## existing Student / Assessment / AssessmentResult / Intervention / Recommendation / Progress coverage
- [VERIFIED] Student: create + get-by-id backend; frontend create/list/detail pages
- [VERIFIED] Assessment: create + get-by-id backend; frontend create/list/detail pages
- [MISSING] AssessmentResult: schema-level presence only (in `AEOS_Supabase_Setup.sql`), no backend/frontend handling
- [PARTIAL] Intervention: intervention plan create + get-by-id backend; no update/list lifecycle or intervention actions endpoints
- [MISSING] Recommendation: no implemented generation/review endpoints or UI workflow
- [MISSING] Progress: no implemented progress event APIs/UI

## existing grading functionality
- [MISSING] No grading subsystem found (no rubric/grading computation/services/endpoints)
- [PARTIAL] `grade_level` exists as student metadata only

## tests
- [VERIFIED] Backend test suite exists: auth, students, assessments, intervention plans
- [VERIFIED] `python -m pytest tests/ -v` => **9 passed**
- [VERIFIED] `python -m pytest tests/test_assessments.py -v` => **3 passed**
- [VERIFIED] Tests are mostly route/service unit tests with fake clients
- [MISSING] No frontend tests found
- [MISSING] No integration/e2e tests against real Supabase found

## build results
- [VERIFIED] Backend static compile check succeeded: `python -m compileall -q backend/app backend/tests`
- [VERIFIED] Backend import checks succeeded (`app.main`, schemas, dependencies)
- [BLOCKED] `npm run lint` is not currently non-interactive; Next.js prompts for ESLint setup because no ESLint config file is committed
- [VERIFIED] `CI=1 npm run build` succeeded in frontend

## CI/CD configuration
- [VERIFIED] One workflow: `.github/workflows/p0-backend-tests.yml`
- [PARTIAL] Workflow trigger includes a branch (`fix/p0-0-stabilization-reconstruction`) that is not the current working branch
- [PARTIAL] CI validates backend only; no frontend CI job

## deployment state
- [PARTIAL] Local dev run path exists via `.replit` workflow for backend uvicorn on port 8000
- [PROVISIONAL] `AEOS_Vercel_Deploy.sh` scaffolds a minimal frontend but is not a full deployment pipeline
- [MISSING] No verified staging/production deployment manifests or environment promotion flow found

## environment-variable requirements
- [VERIFIED] Backend requires (from `backend/.env.example` and config):
  - `APP_ENV`
  - `DEBUG`
  - `DATABASE_URL`
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `AI_PROVIDER`
- [PARTIAL] Frontend supports `NEXT_PUBLIC_API_URL` in `src/lib/api.ts` but pages mostly hardcode `http://127.0.0.1:8000`

## provisional/demo/mock adapters
- [VERIFIED] Test suite fake adapters: `FakeClient` / `FakeTable` in backend tests
- [VERIFIED] Demo seed records in migration SQL
- [PROVISIONAL] Bootstrap shell scripts create starter scaffolding

## code capable of contacting a live backend
- [VERIFIED] Frontend pages directly call backend HTTP endpoints on `http://127.0.0.1:8000`
- [VERIFIED] `frontend/src/lib/api.ts` can call configurable `NEXT_PUBLIC_API_URL`
- [VERIFIED] Backend can call live Supabase (`create_client`) and Supabase JWKS endpoint for JWT key fetch

## security-sensitive Supabase service-role usage
- [VERIFIED] Service-role key is loaded in `backend/app/core/config.py`
- [VERIFIED] `get_supabase_admin_client()` uses service-role key in `backend/app/services/supabase_service.py`
- [VERIFIED] Service-role client is used in student/assessment/intervention plan create and read handlers without attached authz checks

## existing documentation and completion reports
- [VERIFIED] Present docs/artifacts:
  - `README.md`
  - `backend/README.md`
  - `AEOS_Project_Structure.md`
  - `AEOS_MVP_Roadmap.md`
  - `docs/MVP_ACCEPTANCE_CRITERIA.md`
  - `replit.md`
- [PARTIAL] Documentation contains contradictions with current codebase state (see below)
- [MISSING] No formal completion report file found beyond planning/roadmap docs

## dead, duplicated, provisional, or contradictory implementations
- [VERIFIED] Contradictory schema definitions exist:
  - `AEOS_Supabase_Setup.sql` and `backend/supabase/migrations/001_initial_schema.sql` differ materially (types/tables/columns)
- [VERIFIED] `backend/README.md` references `POST /assessments/analyze`, but route does not exist
- [VERIFIED] `replit.md` says frontend not built/empty, but frontend pages are implemented
- [VERIFIED] Tracked `.pyc` and `__pycache__` files duplicate generated artifacts in repository history
- [PROVISIONAL] Setup scripts represent bootstrap state and may not match current maintained runtime paths

## P0 / P1 / P2 issue list

### P0
- [VERIFIED] API routes use Supabase service-role client without enforced authentication/authorization
- [VERIFIED] No organization-scoped authorization checks on tenant data mutations/reads
- [VERIFIED] Frontend expects list APIs that backend does not implement, causing core UI flows to fail

### P1
- [VERIFIED] Dual, contradictory SQL schema sources create migration/deployment ambiguity
- [VERIFIED] Missing recommendation/progress/assessment-result APIs despite MVP docs claiming broader scope
- [VERIFIED] No frontend CI coverage (lint/build/test) in GitHub Actions
- [VERIFIED] Committed `.pyc/__pycache__` artifacts pollute source state

### P2
- [VERIFIED] Documentation drift (`backend/README.md`, `replit.md`) vs actual implementation
- [PARTIAL] Frontend env abstraction exists but is bypassed by hardcoded backend URLs in page components
- [PROVISIONAL] Legacy scaffold scripts may confuse future onboarding unless clearly marked archival

