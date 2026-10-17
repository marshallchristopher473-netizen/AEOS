-- Supabase-equivalent bootstrap for RLS enforcement testing on stock PostgreSQL.
--
-- WHY THIS EXISTS
-- ---------------
-- The AEOS migrations (002, 003) depend on two things stock PostgreSQL does not
-- provide: the `auth.uid()` function and Supabase's role set. To execute those
-- migrations and observe whether their policies actually deny cross-tenant
-- access, the test database must reproduce that environment faithfully.
--
-- This file reproduces ONLY what the migrations touch. It is deliberately
-- minimal and auditable.
--
-- FIDELITY: WHAT IS MODELLED AND WHY IT MATTERS
-- ---------------------------------------------
-- 1. `auth.uid()` uses Supabase's own definition: it reads the `request.jwt.claims`
--    GUC and returns the `sub` claim as UUID. Setting that GUC is exactly how
--    PostgREST conveys a verified JWT subject to the database, so `SET LOCAL
--    request.jwt.claims = ...` in a test is the same input path production uses.
--
-- 2. Table privileges are GRANTed to `authenticated`, matching Supabase's default
--    `GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role`.
--    This is CRITICAL for test validity: without these grants, a cross-tenant query
--    would fail with "permission denied for table" — a GRANT error, not an RLS
--    denial — and the test would pass for the wrong reason. With the grants in
--    place, RLS is the only control standing between the attacker and the data.
--
-- 3. `postgres` owns the tables and the SECURITY DEFINER helper functions, and
--    holds BYPASSRLS, matching Supabase's `postgres` role. This matters because
--    002 applies FORCE ROW LEVEL SECURITY to `public.users`, which subjects even
--    the table owner to RLS. The `aeos_*` helpers are SECURITY DEFINER and read
--    `public.users`; they only return rows because their owner bypasses RLS.
--    `test_helper_owner_bypasses_rls_as_supabase_postgres_does` asserts this
--    precondition explicitly so the assumption is visible rather than silent.
--
-- 4. `service_role` is created with BYPASSRLS, matching Supabase. The FastAPI
--    backend uses this role today (see the header of 002_tenant_rls.sql), so
--    RLS does not constrain application traffic. These tests therefore measure
--    the DIRECT-database/PostgREST boundary that RLS is actually responsible for.

-- Supabase role set. NOLOGIN except `authenticator`, which is the role PostgREST
-- authenticates as before assuming `anon`/`authenticated` via SET ROLE.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon NOLOGIN NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated NOLOGIN NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
        CREATE ROLE service_role NOLOGIN NOINHERIT BYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticator') THEN
        CREATE ROLE authenticator LOGIN NOINHERIT;
    END IF;
END
$$;

GRANT anon, authenticated, service_role TO authenticator;

-- Supabase's `postgres` role carries BYPASSRLS. The test cluster's bootstrap
-- superuser already bypasses RLS; this makes the dependency explicit and keeps
-- the shim correct when applied by a non-superuser owner.
ALTER ROLE postgres BYPASSRLS;

CREATE SCHEMA IF NOT EXISTS auth;
GRANT USAGE ON SCHEMA auth TO anon, authenticated, service_role;

-- Supabase's own definition of auth.uid().
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS UUID
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(
        NULLIF(current_setting('request.jwt.claim.sub', true), ''),
        (NULLIF(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
    )::uuid
$$;

CREATE OR REPLACE FUNCTION auth.role()
RETURNS TEXT
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(
        NULLIF(current_setting('request.jwt.claim.role', true), ''),
        (NULLIF(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
    )::text
$$;

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

-- Covers every table the AEOS migrations create, at creation time, as
-- Supabase's standing grant does. Migration 005 later narrows it.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO anon, authenticated, service_role;
