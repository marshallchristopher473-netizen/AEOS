-- P0 follow-up: revoke the table privileges that row-level security does not
-- govern from the client roles.
--
-- Forward-only: this migration edits none of 001-004 and changes no policy,
-- function or table. It only narrows what `anon` and `authenticated` may do.
--
-- ---------------------------------------------------------------------------
-- SEC-G1-10 — TRUNCATE bypasses every tenant policy.
-- ---------------------------------------------------------------------------
-- Supabase's standing grant for the public schema is
-- `GRANT ALL ON TABLES TO anon, authenticated, service_role`, and ALL includes
-- TRUNCATE. PostgreSQL applies row-level security to SELECT, INSERT, UPDATE and
-- DELETE only; TRUNCATE is checked against the table privilege alone. While
-- that grant stands, an authenticated teacher in any organization can run
-- `TRUNCATE public.students CASCADE` and empty every organization's students,
-- plus every row that cascades from them. The policies in 002-004 never get a
-- say. Reproduced against migrations 001-004 on PostgreSQL 16 with synthetic
-- tenants: a teacher in organization B took organization A's students from 3
-- rows to 0.
--
-- PostgREST exposes no TRUNCATE operation, so no HTTP route is known to reach
-- this today. It is still revoked here because any direct database session as
-- a client role, or any future function that runs dynamic SQL with the
-- caller's rights, would turn the grant into a wipe of every tenant.
--
-- TRIGGER and REFERENCES are revoked with it on least-privilege grounds. RLS
-- does not govern creating a trigger on, or a constraint over, another tenant's
-- table, and neither the application nor PostgREST needs either privilege:
-- triggers fire and foreign keys are checked with the table owner's rights.
--
-- SELECT, INSERT, UPDATE and DELETE are deliberately left granted. Those are
-- the verbs RLS does govern, and removing them would make the policies
-- untestable, because a denial would then come from a permission error rather
-- than from a policy.
--
-- Two statements, because each covers a different set of tables:
--   1. the REVOKE covers every table that exists now;
--   2. the default-privilege change covers tables created later by the role
--      that runs migrations, which would otherwise regain TRUNCATE from the
--      standing grant the moment a future migration creates them.

REVOKE TRUNCATE, TRIGGER, REFERENCES
    ON ALL TABLES IN SCHEMA public
    FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE TRUNCATE, TRIGGER, REFERENCES ON TABLES
    FROM anon, authenticated;
