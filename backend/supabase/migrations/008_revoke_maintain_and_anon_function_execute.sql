-- P0 follow-up to 005: two privileges hosted Supabase hands the client roles
-- that no row-level security policy governs.
--
-- Forward-only: this migration edits none of 001-005 and changes no policy,
-- table or function body. It only narrows what `anon` and `authenticated`
-- may do.
--
-- Numbered 008, not 006: 006 and 007 are already used by the AI-feedback
-- migrations on the integration branch (006_ai_feedback_drafts.sql,
-- 007_ai_feedback_draft_ownership.sql). Nothing here depends on running
-- before or after them. The REVOKE ... ON ALL statements cover whatever
-- tables and functions exist when this runs, and the default-privilege
-- changes cover whatever the migrating role creates afterwards.
--
-- ---------------------------------------------------------------------------
-- F4 — MAINTAIN on PostgreSQL 17.
-- ---------------------------------------------------------------------------
-- PostgreSQL 17 added the MAINTAIN table privilege, and the `ALL` in
-- Supabase's standing `GRANT ALL ON TABLES TO anon, authenticated` includes
-- it. Hosted Supabase runs 17, and the hosted inventory recorded in
-- docs/P0_PR27_INDEPENDENT_VERIFICATION.md (section 6.3) found both client
-- roles holding it on every table, plus the `postgres` default ACL granting
-- it to tables created later. 005 predates 17 support in the test suite and
-- does not name it.
--
-- RLS does not govern MAINTAIN. It permits VACUUM, ANALYZE, CLUSTER, REINDEX,
-- REFRESH MATERIALIZED VIEW and LOCK TABLE on the whole table, every
-- tenant's rows included. Reproduced on PostgreSQL 17.6 against 001-005 with
-- synthetic tenants: a teacher in organization B could REINDEX, and CLUSTER
-- (rewrite under an ACCESS EXCLUSIVE lock), the shared `students` table.
-- That is a cross-tenant availability hole of the same class as the TRUNCATE
-- grant 005 closed.
--
-- PostgreSQL 16 has no MAINTAIN privilege and rejects the word, so the revoke
-- runs only on 17 and later. On 16 the privilege cannot be held.
--
-- Not closed here, by design: LOCK TABLE is also permitted by UPDATE or
-- DELETE, which the policies need granted, on 16 and 17 alike. Only a direct
-- database session as a client role can issue it; PostgREST exposes no LOCK.
--
-- ---------------------------------------------------------------------------
-- F1 — `anon` can execute the SECURITY DEFINER helpers.
-- ---------------------------------------------------------------------------
-- 002-004 run `REVOKE ALL ON FUNCTION ... FROM PUBLIC` and then grant EXECUTE
-- to `authenticated`. Hosted Supabase also has
-- `ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon,
-- authenticated, service_role`, which is a DIRECT grant to `anon` that a
-- revoke from PUBLIC does not remove. The hosted inventory confirmed `anon`
-- holds EXECUTE on all five `aeos_*` helpers, which PostgREST serves at
-- /rest/v1/rpc/<name> to anyone holding the anon key. They returned nothing
-- for `anon`, so no tenant data was shown to leak, but they read membership
-- with RLS bypassed and no policy is written for `anon`, so nothing
-- legitimate needs the grant.
--
-- Revoking from `anon` alone leaves `authenticated` able to execute every
-- helper, which every policy requires. Trigger functions are unaffected:
-- PostgreSQL checks EXECUTE on a trigger function when the trigger is
-- created, not when it fires.

DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 170000 THEN
        EXECUTE 'REVOKE MAINTAIN ON ALL TABLES IN SCHEMA public FROM anon, authenticated';
        EXECUTE 'ALTER DEFAULT PRIVILEGES IN SCHEMA public '
                'REVOKE MAINTAIN ON TABLES FROM anon, authenticated';
    END IF;
END
$$;

REVOKE EXECUTE
    ON ALL FUNCTIONS IN SCHEMA public
    FROM anon;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE EXECUTE ON FUNCTIONS
    FROM anon;
