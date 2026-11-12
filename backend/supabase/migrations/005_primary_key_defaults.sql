-- Pilot blocker: no AEOS table could accept a row created by the application.
--
-- 001_initial_schema.sql declares every primary key as `id UUID PRIMARY KEY`
-- with no DEFAULT. The application's only insert path,
-- `app/services/tenant_scope.insert_tenant_scoped_row`, builds
-- `{**payload, "organization_id": <server-derived>}` and never supplies `id`.
-- Against the real schema every create endpoint therefore failed with:
--
--     null value in column "id" of relation "students"
--     violates not-null constraint
--
-- That is POST /students, /assessments, /assessment-results and
-- /intervention-plans — the entire write half of the teacher workflow.
--
-- WHY THE SUITE DID NOT CATCH IT
-- ------------------------------
-- The two test paths each supply an `id` the application does not:
--   * `tests/fakes.py` auto-assigns one (`row.setdefault("id", ...)`), so the
--     FastAPI tests exercised an insert shape the database never sees.
--   * `tests/test_rls_enforcement.py` seeds every synthetic row with an
--     explicit literal `id`, because its subject is tenant isolation.
-- Neither ever performed an application-shaped insert against real PostgreSQL.
-- `tests/test_primary_key_defaults.py` now does exactly that.
--
-- THE FIX
-- -------
-- Forward-only, consistent with 002-004: this migration edits no earlier file.
-- It attaches `gen_random_uuid()` as the default for each primary key, so the
-- database supplies the identifier for every writer — the FastAPI service-role
-- path, PostgREST, and direct SQL alike. `gen_random_uuid()` is built into
-- PostgreSQL 13+ (and present in Supabase), so no extension is required.
--
-- `ALTER COLUMN ... SET DEFAULT` is idempotent and does not rewrite the table:
-- it changes the catalog entry only. Existing rows are untouched, and any
-- writer that already supplies its own `id` keeps overriding the default.

ALTER TABLE public.organizations       ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.schools             ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.users               ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.students            ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.assessments         ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.assessment_results  ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.ai_recommendations  ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.intervention_plans  ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.intervention_actions ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.progress_events     ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE public.audit_logs          ALTER COLUMN id SET DEFAULT gen_random_uuid();
