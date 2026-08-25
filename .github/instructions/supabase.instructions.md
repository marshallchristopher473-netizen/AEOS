---
applyTo: "backend/supabase/**"
---

# Supabase / migration instructions

## Current, verified state

- `backend/supabase/migrations/001_initial_schema.sql` is the only versioned migration. It defines 10 tables (`organizations`, `schools`, `users`, `students`, `assessments`, `ai_recommendations`, `intervention_plans`, `intervention_actions`, `progress_events`, `audit_logs`) with foreign keys, but contains **no `ENABLE ROW LEVEL SECURITY` and no `CREATE POLICY` statements**.
- The live Supabase project backing this app (see `backend/.env.example` / Codespaces secrets for `SUPABASE_URL`) has **drifted from this file**: as last checked, the live database had RLS *enabled* on every table (via an out-of-band change, not present in this migration) but **zero policies** — which is functionally equivalent to no access via the `anon`/`authenticated` roles, and irrelevant to the app's actual behavior since the app uses the service-role key everywhere. The live database also contained tables (`assessment_results`, `notes`, `ai_recommendation_runs`) not present in this migration at all.
- Re-verify both sides (versioned migration + live project) before making a claim about RLS state. Don't trust either one alone.

## Rules

1. **Never edit `001_initial_schema.sql` in place once it has been applied anywhere.** Add a new, sequentially-numbered migration file for any schema change, including enabling RLS.
2. **Any table holding tenant-owned data must have RLS enabled AND explicit policies** for `SELECT`/`INSERT`/`UPDATE`/`DELETE`, scoped to the requesting user's `organization_id`. "RLS enabled, zero policies" is not a completed control — with zero policies, `authenticated`/`anon` roles are blocked from everything (fail-closed) but the service-role key still bypasses it entirely, so RLS alone provides no defense-in-depth as long as application code uses the service-role client.
3. **If you change anything in the live Supabase project directly** (dashboard, SQL editor, MCP `execute_sql`/`apply_migration`), immediately also commit the equivalent as a versioned migration in this directory. An unversioned live-only change is exactly the kind of drift that makes this repository's schema state unreliable to reason about.
4. **Before writing a new migration, reconcile against the live project** (`list_tables`, `get_advisors`, or direct SQL against `pg_policies`/`pg_class.relrowsecurity`) rather than assuming this directory is a complete description of what's deployed.
5. **No real student, IEP, or 504 data — ever**, in migrations, seed data, or as fixtures. The existing seed rows in `001_initial_schema.sql` are synthetic demo data; keep any future seed data the same way.
