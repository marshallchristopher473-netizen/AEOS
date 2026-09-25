"""Executed proof that the AEOS RLS migrations enforce tenant isolation.

WHAT THIS FILE IS FOR
---------------------
Every other RLS test in this suite asserts against the *text* of the migration
files (`test_security_artifacts.py` string-matches, `test_fk_relationship_rls.py`
regex-parses). Those cannot detect a policy that fails to parse, fails to apply,
or fails to deny. This module closes that gap: it runs 001 -> 002 -> 003 against a
real PostgreSQL server, seeds two synthetic organizations, and attempts real
cross-tenant SELECT / INSERT / UPDATE / DELETE as an authenticated member of
organization A against organization B's rows.

NO REAL DATA. Every row is synthetic and generated in this file.

NEGATIVE CONTROL
----------------
`TestNegativeControl` disables the specific RLS protection under test and proves
the same attack then succeeds. Without it, a green suite would be indistinguishable
from a suite that silently tests nothing. If those tests ever stop observing a
breach with RLS off, this module has itself become vacuous.

SCOPE (deliberately bounded)
----------------------------
This measures the direct-database / PostgREST boundary, which is what RLS governs.
It does NOT measure the FastAPI request path: the backend connects with the
service-role client, which carries BYPASSRLS, so RLS never constrains application
traffic today. That is documented in the header of 002_tenant_rls.sql and is a
separate question from the one this file answers.

RUNNING LOCALLY
---------------
    export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
    python -m pytest tests/test_rls_enforcement.py -v

Without AEOS_TEST_DATABASE_URL these tests SKIP, so the existing suite is
unaffected on machines with no database.
"""

import os
import uuid
from pathlib import Path

import pytest

REQUIRED = os.environ.get("AEOS_REQUIRE_RLS_TESTS") == "1"
DATABASE_URL = os.environ.get("AEOS_TEST_DATABASE_URL")

# A security test that silently skips is worse than no test: CI stays green while
# proving nothing. In the dedicated CI job AEOS_REQUIRE_RLS_TESTS=1 turns a
# missing/unreachable database into a hard collection error instead of a skip.
#
# ORDERING IS PART OF THE CONTRACT. This guard MUST run before any module-level
# skip. `pytest.importorskip("psycopg")` previously sat above it, so with
# psycopg absent the whole module skipped at exit code 0 even under
# AEOS_REQUIRE_RLS_TESTS=1 — required mode reported success having executed
# nothing. Both required-mode failure causes are therefore checked here first,
# and only then is the import allowed to skip.
if REQUIRED and not DATABASE_URL:
    raise RuntimeError(
        "AEOS_REQUIRE_RLS_TESTS=1 but AEOS_TEST_DATABASE_URL is unset. "
        "The RLS enforcement tests would have skipped silently."
    )

if REQUIRED:
    # Hard import: in required mode a missing driver is a failure, never a skip.
    import psycopg
else:
    # Outside required mode a machine without the driver may still skip.
    psycopg = pytest.importorskip(
        "psycopg", reason="psycopg is required for RLS enforcement tests"
    )

from psycopg.conninfo import conninfo_to_dict, make_conninfo  # noqa: E402


BACKEND_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = BACKEND_DIR / "supabase" / "migrations"
SHIM_SQL = Path(__file__).resolve().parent / "sql" / "supabase_shim.sql"

MIGRATIONS = (
    "001_initial_schema.sql",
    "002_tenant_rls.sql",
    "003_fk_relationship_hardening.sql",
    "004_org_lifecycle_and_write_authority.sql",
)

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="AEOS_TEST_DATABASE_URL is not set; RLS enforcement tests require PostgreSQL",
)


# Synthetic tenants, in a UUID namespace deliberately disjoint from the demo
# rows that 001_initial_schema.sql seeds (organization 11111111-...). Those
# seeded rows are left in place and act as a third tenant that must remain
# invisible to both synthetic organizations.
ORG_A = "0aaa0000-0000-4000-8000-000000000001"
ORG_B = "0bbb0000-0000-4000-8000-000000000002"
SCHOOL_A = "0aaa0000-0000-4000-8000-000000000003"
SCHOOL_B = "0bbb0000-0000-4000-8000-000000000004"
USER_A = "0aaa0000-0000-4000-8000-000000000005"
USER_B = "0bbb0000-0000-4000-8000-000000000006"
# auth.uid() returns UUID, so the authenticated subject must be UUID-shaped.
AUTH_A = "0aaa0000-0000-4000-8000-000000000007"
AUTH_B = "0bbb0000-0000-4000-8000-000000000008"
# Second teacher and an admin, both in organization A, for the peer-access and
# delete-authority cases (M2).
PEER_A = "0aaa0000-0000-4000-8000-000000000010"
AUTH_PEER_A = "0aaa0000-0000-4000-8000-000000000011"
ADMIN_A = "0aaa0000-0000-4000-8000-000000000012"
AUTH_ADMIN_A = "0aaa0000-0000-4000-8000-000000000013"
SUPPORT_A = "0aaa0000-0000-4000-8000-000000000014"
AUTH_SUPPORT_A = "0aaa0000-0000-4000-8000-000000000015"
# A student created by the peer teacher, not by USER_A.
STUDENT_PEER = "0aaa0000-0000-4000-8000-000000000016"
# A student in organization A with NO school. `students_update`'s WITH CHECK is
# `aeos_can_write_org(...) AND (school_id IS NULL OR <school belongs to org>)`,
# so a NULL school_id satisfies the second conjunct vacuously and leaves
# `aeos_can_write_org` as the only control on that write path. That is exactly
# the condition M09 removes, so this row is what makes the mutation observable.
STUDENT_A_NO_SCHOOL = "0aaa0000-0000-4000-8000-000000000019"
STUDENT_A = "0aaa0000-0000-4000-8000-000000000009"
STUDENT_B = "0bbb0000-0000-4000-8000-00000000000a"
ASSESSMENT_A = "0aaa0000-0000-4000-8000-00000000000b"
ASSESSMENT_B = "0bbb0000-0000-4000-8000-00000000000c"
PLAN_A = "0aaa0000-0000-4000-8000-00000000000d"
PLAN_B = "0bbb0000-0000-4000-8000-00000000000e"
RESULT_A = "0aaa0000-0000-4000-8000-000000000017"
RESULT_B = "0bbb0000-0000-4000-8000-000000000018"
# Seeded by 001_initial_schema.sql.
ORG_DEMO = "11111111-1111-4111-8111-111111111111"


SEED_SQL = f"""
INSERT INTO public.organizations (id, name, type, status) VALUES
    ('{ORG_A}', 'Synthetic Org A', 'district', 'active'),
    ('{ORG_B}', 'Synthetic Org B', 'district', 'active');

INSERT INTO public.schools (id, organization_id, name, status) VALUES
    ('{SCHOOL_A}', '{ORG_A}', 'Synthetic School A', 'active'),
    ('{SCHOOL_B}', '{ORG_B}', 'Synthetic School B', 'active');

INSERT INTO public.users
    (id, organization_id, auth_user_id, email, full_name, role, status) VALUES
    ('{USER_A}', '{ORG_A}', '{AUTH_A}', 'teacher-a@synthetic.test', 'Teacher A', 'teacher', 'active'),
    ('{PEER_A}', '{ORG_A}', '{AUTH_PEER_A}', 'peer-a@synthetic.test', 'Peer A', 'teacher', 'active'),
    ('{ADMIN_A}', '{ORG_A}', '{AUTH_ADMIN_A}', 'admin-a@synthetic.test', 'Admin A', 'admin', 'active'),
    ('{SUPPORT_A}', '{ORG_A}', '{AUTH_SUPPORT_A}', 'support-a@synthetic.test', 'Support A', 'support', 'active'),
    ('{USER_B}', '{ORG_B}', '{AUTH_B}', 'teacher-b@synthetic.test', 'Teacher B', 'teacher', 'active');

INSERT INTO public.students
    (id, organization_id, school_id, first_name, last_name, grade_level, status, created_by) VALUES
    ('{STUDENT_A}', '{ORG_A}', '{SCHOOL_A}', 'Ada', 'Synthetic', '6', 'active', '{USER_A}'),
    ('{STUDENT_PEER}', '{ORG_A}', '{SCHOOL_A}', 'Grace', 'Synthetic', '6', 'active', '{PEER_A}'),
    ('{STUDENT_A_NO_SCHOOL}', '{ORG_A}', NULL, 'Noether', 'Synthetic', '6', 'active', '{USER_A}'),
    ('{STUDENT_B}', '{ORG_B}', '{SCHOOL_B}', 'Blaise', 'Synthetic', '7', 'active', '{USER_B}');

INSERT INTO public.assessments
    (id, organization_id, student_id, created_by, title, assessment_type, status) VALUES
    ('{ASSESSMENT_A}', '{ORG_A}', '{STUDENT_A}', '{USER_A}', 'Org A Assessment', 'ela', 'draft'),
    ('{ASSESSMENT_B}', '{ORG_B}', '{STUDENT_B}', '{USER_B}', 'Org B Assessment', 'ela', 'draft');

INSERT INTO public.intervention_plans
    (id, organization_id, student_id, assessment_id, created_by, title, status) VALUES
    ('{PLAN_A}', '{ORG_A}', '{STUDENT_A}', '{ASSESSMENT_A}', '{USER_A}', 'Org A Plan', 'draft'),
    ('{PLAN_B}', '{ORG_B}', '{STUDENT_B}', '{ASSESSMENT_B}', '{USER_B}', 'Org B Plan', 'draft');

INSERT INTO public.assessment_results
    (id, organization_id, assessment_id, student_id, created_by, summary, status) VALUES
    ('{RESULT_A}', '{ORG_A}', '{ASSESSMENT_A}', '{STUDENT_A}', '{USER_A}', 'Org A Result', 'draft'),
    ('{RESULT_B}', '{ORG_B}', '{ASSESSMENT_B}', '{STUDENT_B}', '{USER_B}', 'Org B Result', 'draft');
"""


@pytest.fixture(scope="session")
def migrated_database():
    """Apply shim + 001 -> 002 -> 003 to a scratch database, then seed two tenants.

    Migration failure surfaces here as a hard error, which is itself the first
    thing this module is meant to detect.
    """
    admin_url = DATABASE_URL
    db_name = f"aeos_rls_{uuid.uuid4().hex[:12]}"

    with psycopg.connect(admin_url, autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{db_name}"')

    target_url = _swap_database(admin_url, db_name)

    try:
        with psycopg.connect(target_url, autocommit=True) as conn:
            conn.execute(SHIM_SQL.read_text())

            for migration in MIGRATIONS:
                path = MIGRATIONS_DIR / migration
                assert path.exists(), f"missing migration: {path}"
                conn.execute(path.read_text())

            # Mirror Supabase's standing grants for tables created by the
            # migrations. Without this, cross-tenant access would fail as a
            # GRANT error rather than an RLS denial and the tests below would
            # pass for the wrong reason.
            conn.execute(
                "GRANT ALL ON ALL TABLES IN SCHEMA public "
                "TO anon, authenticated, service_role"
            )
            conn.execute(
                "GRANT ALL ON ALL SEQUENCES IN SCHEMA public "
                "TO anon, authenticated, service_role"
            )

            conn.execute(SEED_SQL)

        yield target_url
    finally:
        with psycopg.connect(admin_url, autocommit=True) as conn:
            conn.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (db_name,),
            )
            conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')


def _swap_database(url, db_name):
    """Re-point a connection string at a different database.

    Uses psycopg's own conninfo parser rather than string surgery so that URLs
    carrying query parameters (``?host=/tmp&port=5432``) and keyword-form DSNs
    are both handled correctly.
    """
    params = conninfo_to_dict(url)
    params["dbname"] = db_name
    return make_conninfo(**params)


@pytest.fixture
def admin_conn(migrated_database):
    """Privileged connection (BYPASSRLS), used only for setup and assertions.

    `lock_timeout` matters: the negative control takes an ACCESS EXCLUSIVE lock
    via ALTER TABLE, which blocks behind any open reader transaction. Without a
    timeout that contention hangs the CI job forever instead of failing.
    """
    with psycopg.connect(migrated_database, autocommit=True) as conn:
        conn.execute("SET lock_timeout = '10s'")
        yield conn


@pytest.fixture
def as_org_a(migrated_database):
    """Connection acting as an authenticated member of organization A.

    `SET ROLE authenticated` drops the session's BYPASSRLS, and
    `request.jwt.claims` is the same GUC PostgREST populates from a verified
    JWT, so `auth.uid()` resolves exactly as it does in production.
    """
    with psycopg.connect(migrated_database) as conn:
        _become(conn, AUTH_A)
        yield conn


@pytest.fixture
def as_org_a_peer(migrated_database):
    """A second teacher in organization A who did not create STUDENT_A."""
    with psycopg.connect(migrated_database) as conn:
        _become(conn, AUTH_PEER_A)
        yield conn


@pytest.fixture
def as_org_a_admin(migrated_database):
    """An admin in organization A."""
    with psycopg.connect(migrated_database) as conn:
        _become(conn, AUTH_ADMIN_A)
        yield conn


@pytest.fixture
def as_org_a_support(migrated_database):
    """A support-role member of organization A (read-only by policy)."""
    with psycopg.connect(migrated_database) as conn:
        _become(conn, AUTH_SUPPORT_A)
        yield conn


@pytest.fixture
def suspended_org_a(admin_conn, as_org_a):
    """Suspend organization A for the duration of one test."""
    as_org_a.rollback()
    admin_conn.execute(
        "UPDATE public.organizations SET status = 'suspended' WHERE id = %s", (ORG_A,)
    )
    try:
        yield
    finally:
        as_org_a.rollback()
        admin_conn.execute(
            "UPDATE public.organizations SET status = 'active' WHERE id = %s", (ORG_A,)
        )


def _become(conn, auth_user_id):
    """Assume the `authenticated` role and inject a verified JWT subject.

    Applied in autocommit so both settings are session-level. This matters:
    `SET ROLE` is transactional, so if it were applied inside the test's
    transaction, any later `rollback()` would silently revert the session to
    the superuser that opened the connection — which holds BYPASSRLS. Tests
    would then run as `postgres` and pass regardless of what the policies say.
    """
    previous = conn.autocommit
    conn.autocommit = True
    try:
        conn.execute("SET ROLE authenticated")
        conn.execute(
            "SELECT set_config('request.jwt.claims', %s, false)",
            (f'{{"sub": "{auth_user_id}", "role": "authenticated"}}',),
        )
    finally:
        conn.autocommit = previous


# ---------------------------------------------------------------------------
# Preconditions: prove the environment is the one we think it is.
# ---------------------------------------------------------------------------


class TestEnvironmentPreconditions:
    def test_migrations_apply_cleanly_and_create_expected_tables(self, admin_conn):
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            names = {row[0] for row in cur.fetchall()}

        for expected in (
            "organizations",
            "schools",
            "users",
            "students",
            "assessments",
            "intervention_plans",
            "assessment_results",
        ):
            assert expected in names, f"{expected} was not created by the migrations"

    def test_rls_is_enabled_and_forced_on_tenant_tables(self, admin_conn):
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT relname, relrowsecurity, relforcerowsecurity "
                "FROM pg_class WHERE relnamespace = 'public'::regnamespace "
                "AND relname = ANY(%s)",
                (["students", "assessments", "intervention_plans", "assessment_results"],),
            )
            rows = cur.fetchall()

        assert rows, "expected tenant tables to exist"
        for relname, enabled, forced in rows:
            assert enabled, f"RLS not ENABLED on {relname}"
            assert forced, f"RLS not FORCED on {relname}"

    def test_policies_were_actually_created(self, admin_conn):
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM pg_policies WHERE schemaname = 'public'"
            )
            (count,) = cur.fetchone()
        assert count > 0, "no RLS policies exist despite migrations having run"

    def test_helper_owner_bypasses_rls_as_supabase_postgres_does(self, admin_conn):
        """The aeos_* helpers are SECURITY DEFINER and read public.users, which
        has FORCE RLS. They can only return rows because their owner bypasses
        RLS. Assert that precondition rather than relying on it silently."""
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT r.rolbypassrls, p.prosecdef "
                "FROM pg_proc p JOIN pg_roles r ON r.oid = p.proowner "
                "WHERE p.proname = 'aeos_has_org_access'"
            )
            row = cur.fetchone()
        assert row is not None, "aeos_has_org_access was not created"
        bypassrls, security_definer = row
        assert security_definer, "aeos_has_org_access must be SECURITY DEFINER"
        assert bypassrls, "helper owner must hold BYPASSRLS (matches Supabase `postgres`)"

    def test_authenticated_role_holds_table_grants(self, admin_conn):
        """If `authenticated` lacked GRANTs, every cross-tenant test below would
        pass with a permission error instead of an RLS denial."""
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT has_table_privilege('authenticated', 'public.students', %s)",
                ("SELECT",),
            )
            (can_select,) = cur.fetchone()
            cur.execute(
                "SELECT has_table_privilege('authenticated', 'public.students', %s)",
                ("DELETE",),
            )
            (can_delete,) = cur.fetchone()

        assert can_select, "authenticated must hold SELECT for RLS to be the control under test"
        assert can_delete, "authenticated must hold DELETE for RLS to be the control under test"

    def test_authenticated_session_does_not_bypass_rls(self, as_org_a):
        with as_org_a.cursor() as cur:
            cur.execute("SELECT current_user")
            (who,) = cur.fetchone()
            cur.execute("SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user")
            (bypass,) = cur.fetchone()
        assert who == "authenticated"
        assert not bypass, "authenticated must not hold BYPASSRLS"

    def test_identity_survives_rollback(self, as_org_a):
        """Guard the guard: `SET ROLE` is transactional, so an identity applied
        inside a transaction would silently revert to the superuser on rollback
        and every later assertion would run with BYPASSRLS."""
        as_org_a.rollback()
        with as_org_a.cursor() as cur:
            cur.execute("SELECT current_user, auth.uid()::text")
            who, subject = cur.fetchone()
        assert who == "authenticated", f"identity lost after rollback: {who}"
        assert subject == AUTH_A, "JWT subject lost after rollback"

    def test_auth_uid_resolves_the_injected_subject(self, as_org_a):
        with as_org_a.cursor() as cur:
            cur.execute("SELECT auth.uid()::text")
            (subject,) = cur.fetchone()
        assert subject == AUTH_A


# ---------------------------------------------------------------------------
# Cross-tenant denial, executed through the database.
# ---------------------------------------------------------------------------


class TestCrossTenantSelectDenial:
    @pytest.mark.parametrize(
        "table,foreign_id",
        [
            ("students", STUDENT_B),
            ("assessments", ASSESSMENT_B),
            ("intervention_plans", PLAN_B),
            ("assessment_results", RESULT_B),
        ],
    )
    def test_foreign_tenant_row_is_invisible(self, as_org_a, table, foreign_id):
        with as_org_a.cursor() as cur:
            cur.execute(f"SELECT id FROM public.{table} WHERE id = %s", (foreign_id,))
            assert cur.fetchall() == [], f"org A could read org B row in {table}"

    @pytest.mark.parametrize(
        "table,own_id",
        [
            ("students", STUDENT_A),
            ("assessments", ASSESSMENT_A),
            ("intervention_plans", PLAN_A),
        ],
    )
    def test_own_tenant_row_remains_visible(self, as_org_a, table, own_id):
        """Guards against a policy that denies everything, which would make the
        denial tests above pass while breaking the product."""
        with as_org_a.cursor() as cur:
            cur.execute(f"SELECT id FROM public.{table} WHERE id = %s", (own_id,))
            assert len(cur.fetchall()) == 1, f"org A cannot read its own {table} row"

    @pytest.mark.parametrize(
        "table",
        ["students", "assessments", "intervention_plans", "assessment_results"],
    )
    def test_unfiltered_scan_returns_only_own_tenant(self, as_org_a, table):
        """An unscoped `SELECT *` is the realistic exfiltration attempt."""
        with as_org_a.cursor() as cur:
            cur.execute(f"SELECT organization_id::text FROM public.{table}")
            orgs = {row[0] for row in cur.fetchall()}
        assert orgs == {ORG_A}, f"unfiltered scan of {table} leaked: {orgs}"


class TestCrossTenantInsertDenial:
    def test_insert_into_foreign_tenant_is_rejected(self, as_org_a):
        new_id = str(uuid.uuid4())
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with as_org_a.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.students "
                    "(id, organization_id, school_id, first_name, last_name, "
                    " grade_level, status, created_by) "
                    "VALUES (%s, %s, %s, 'Mallory', 'Injected', '8', 'active', %s)",
                    (new_id, ORG_B, SCHOOL_B, USER_B),
                )
        as_org_a.rollback()

    def test_insert_claiming_foreign_creator_is_rejected(self, as_org_a):
        """Tenant correct, actor spoofed: `created_by` must belong to the caller."""
        new_id = str(uuid.uuid4())
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with as_org_a.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.students "
                    "(id, organization_id, school_id, first_name, last_name, "
                    " grade_level, status, created_by) "
                    "VALUES (%s, %s, %s, 'Mallory', 'Spoofed', '8', 'active', %s)",
                    (new_id, ORG_A, SCHOOL_A, USER_B),
                )
        as_org_a.rollback()

    def test_assessment_cannot_reference_foreign_tenant_student(self, as_org_a):
        """FK smuggling: own org on the row, foreign org's student underneath.
        This is the bypass class 003_fk_relationship_hardening.sql exists to close."""
        new_id = str(uuid.uuid4())
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with as_org_a.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.assessments "
                    "(id, organization_id, student_id, created_by, title, "
                    " assessment_type, status) "
                    "VALUES (%s, %s, %s, %s, 'Smuggled', 'ela', 'draft')",
                    (new_id, ORG_A, STUDENT_B, USER_A),
                )
        as_org_a.rollback()

    def test_legitimate_insert_still_succeeds(self, as_org_a):
        """Proves the INSERT policies are not simply denying everything."""
        new_id = str(uuid.uuid4())
        with as_org_a.cursor() as cur:
            cur.execute(
                "INSERT INTO public.students "
                "(id, organization_id, school_id, first_name, last_name, "
                " grade_level, status, created_by) "
                "VALUES (%s, %s, %s, 'Grace', 'Legitimate', '6', 'active', %s)",
                (new_id, ORG_A, SCHOOL_A, USER_A),
            )
        as_org_a.rollback()


class TestCrossTenantUpdateDenial:
    @pytest.mark.parametrize(
        "table,foreign_id,column",
        [
            ("students", STUDENT_B, "last_name"),
            ("assessments", ASSESSMENT_B, "title"),
            ("intervention_plans", PLAN_B, "title"),
            ("assessment_results", RESULT_B, "summary"),
        ],
    )
    def test_update_of_foreign_row_affects_nothing(
        self, as_org_a, admin_conn, table, foreign_id, column
    ):
        with as_org_a.cursor() as cur:
            cur.execute(
                f"UPDATE public.{table} SET {column} = 'TAMPERED' WHERE id = %s",
                (foreign_id,),
            )
            assert cur.rowcount == 0, f"org A updated org B row in {table}"
        as_org_a.commit()

        with admin_conn.cursor() as cur:
            cur.execute(f"SELECT {column} FROM public.{table} WHERE id = %s", (foreign_id,))
            (value,) = cur.fetchone()
        assert value != "TAMPERED", f"org B row in {table} was modified"

    def test_update_cannot_move_own_row_into_foreign_tenant(self, as_org_a):
        """Tenant reassignment: taking a row you own and pushing it to org B."""
        with as_org_a.cursor() as cur:
            with pytest.raises(
                (psycopg.errors.InsufficientPrivilege, psycopg.errors.RaiseException)
            ):
                cur.execute(
                    "UPDATE public.students SET organization_id = %s WHERE id = %s",
                    (ORG_B, STUDENT_A),
                )
        as_org_a.rollback()


class TestCrossTenantDeleteDenial:
    @pytest.mark.parametrize(
        "table,foreign_id",
        [
            ("intervention_plans", PLAN_B),
            ("assessments", ASSESSMENT_B),
            ("students", STUDENT_B),
        ],
    )
    def test_delete_of_foreign_row_affects_nothing(
        self, as_org_a, admin_conn, table, foreign_id
    ):
        with as_org_a.cursor() as cur:
            cur.execute(f"DELETE FROM public.{table} WHERE id = %s", (foreign_id,))
            assert cur.rowcount == 0, f"org A deleted org B row in {table}"
        as_org_a.commit()

        with admin_conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM public.{table} WHERE id = %s", (foreign_id,))
            (count,) = cur.fetchone()
        assert count == 1, f"org B row in {table} no longer exists"


# ---------------------------------------------------------------------------
# Scope of the authorization contract: ORGANIZATION-level, not school-level.
# ---------------------------------------------------------------------------


class TestAuthorizationContractScope:
    """Pin the tenancy boundary so a future narrowing or widening is visible.

    `AuthenticatedActor` carries no school, no route filters by school, and
    `schools_select` is scoped by `aeos_has_org_access(organization_id)`.
    `school_id` participates in policies only as an FK integrity constraint
    *within* the tenant (`related_school.organization_id =
    students.organization_id`), never as an isolation boundary.

    These tests assert that contract rather than a stronger one the system
    does not implement. If per-school scoping is ever required, that is a
    product decision and these tests should change with it.
    """

    def test_school_is_not_an_isolation_boundary_within_a_tenant(
        self, as_org_a, admin_conn
    ):
        """A second school in the same organization stays visible: the boundary
        is the organization, not the school."""
        other_school = str(uuid.uuid4())
        admin_conn.execute(
            "INSERT INTO public.schools (id, organization_id, name, status) "
            "VALUES (%s, %s, 'Second School A', 'active')",
            (other_school, ORG_A),
        )
        try:
            with as_org_a.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.schools")
                (visible,) = cur.fetchone()
            assert visible == 2, (
                "expected both organization-A schools to be visible; the contract "
                "is organization-level, not school-level"
            )
        finally:
            as_org_a.rollback()
            admin_conn.execute(
                "DELETE FROM public.schools WHERE id = %s", (other_school,)
            )

    def test_foreign_tenant_school_is_invisible(self, as_org_a):
        """School isolation that IS in the contract: across organizations."""
        with as_org_a.cursor() as cur:
            cur.execute("SELECT id FROM public.schools WHERE id = %s", (SCHOOL_B,))
            assert cur.fetchall() == [], "organization A could read organization B's school"

    def test_student_cannot_be_attached_to_foreign_tenant_school(self, as_org_a):
        """school_id is constrained to the acting tenant on write."""
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with as_org_a.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.students "
                    "(id, organization_id, school_id, first_name, last_name, "
                    " grade_level, status, created_by) "
                    "VALUES (%s, %s, %s, 'Cross', 'School', '8', 'active', %s)",
                    (str(uuid.uuid4()), ORG_A, SCHOOL_B, USER_A),
                )
        as_org_a.rollback()


# ---------------------------------------------------------------------------
# M1 — organization lifecycle. Suspension must contain, immediately.
# ---------------------------------------------------------------------------


class TestOrganizationLifecycle:
    def test_suspended_organization_cannot_read(self, as_org_a, suspended_org_a):
        with as_org_a.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.students")
            (visible,) = cur.fetchone()
        assert visible == 0, "suspended organization could still read its students"

    def test_suspended_organization_cannot_write(self, as_org_a, suspended_org_a):
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with as_org_a.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.students "
                    "(id, organization_id, school_id, first_name, last_name, "
                    " grade_level, status, created_by) "
                    "VALUES (%s, %s, %s, 'Sus', 'Pended', '8', 'active', %s)",
                    (str(uuid.uuid4()), ORG_A, SCHOOL_A, USER_A),
                )
        as_org_a.rollback()

    def test_suspended_organization_cannot_update(self, as_org_a, suspended_org_a):
        """Distinct from the INSERT case above, and not implied by it.

        `students_insert` is protected by BOTH `aeos_can_write_org` and
        `aeos_is_current_actor_for_org`, so the INSERT test still passes if only
        one of them loses its organization-active condition. Every `*_update`
        policy (004) relies on `aeos_can_write_org` alone, so UPDATE is the
        operation that actually pins that helper. The mutation suite found this
        gap: `aeos_can_write_org stops requiring an ACTIVE organization` was
        undetected until this test existed.
        """
        with as_org_a.cursor() as cur:
            cur.execute(
                "UPDATE public.students SET last_name = 'Suspended' WHERE id = %s",
                (STUDENT_A,),
            )
            assert cur.rowcount == 0, "suspended organization could still update"
        as_org_a.rollback()

    def test_suspended_organization_cannot_update_without_a_where_clause(
        self, as_org_a, admin_conn, suspended_org_a
    ):
        """M09 kill: the WHERE-less UPDATE shape, which no other test covers.

        Every other UPDATE probe in this file carries a `WHERE` clause. That
        matters more than it looks: PostgreSQL applies a table's SELECT policy
        to an UPDATE only when the statement has to locate rows — i.e. when it
        carries `WHERE` or `RETURNING`. A bare `UPDATE students SET ...` never
        consults the SELECT policy, so `aeos_has_org_access` (which is NOT
        mutated by M09) never gets a chance to deny it, and `students_update`'s
        `USING` clause stands alone:

            USING (public.aeos_can_write_org(students.organization_id))

        With `aeos_can_write_org` no longer requiring an ACTIVE organization,
        and with `WITH CHECK`'s school conjunct satisfied vacuously by
        STUDENT_A_NO_SCHOOL, nothing on that path carries the suspension
        condition. The mutant then writes to a suspended tenant's row.

        This is the test that makes M09 non-equivalent. It was the gap that let
        `aeos_can_write_org stops requiring an ACTIVE organization` be
        classified EQUIVALENT: the equivalence proof's 20 probes all used
        `WHERE`, so all 20 were masked by the SELECT policy.

        Asserted behaviourally, in two independent ways:
          * the statement must affect zero rows, and
          * the value in the database must be unchanged afterwards, read back
            on the privileged connection because the suspended actor cannot
            see its own rows.
        """
        before = admin_conn.execute(
            "SELECT first_name FROM public.students WHERE id = %s",
            (STUDENT_A_NO_SCHOOL,),
        ).fetchone()[0]
        assert before == "Noether", "fixture drifted; the probe would prove nothing"

        with as_org_a.cursor() as cur:
            # Deliberately no WHERE and no RETURNING.
            cur.execute("UPDATE public.students SET first_name = 'PWNED'")
            affected = cur.rowcount
        as_org_a.commit()

        after = admin_conn.execute(
            "SELECT first_name FROM public.students WHERE id = %s",
            (STUDENT_A_NO_SCHOOL,),
        ).fetchone()[0]

        assert affected == 0, (
            "a WHERE-less UPDATE by a member of a SUSPENDED organization "
            f"affected {affected} row(s)"
        )
        assert after == "Noether", (
            "a WHERE-less UPDATE persisted an unauthorized change against a "
            f"suspended organization: first_name is now {after!r}"
        )

    def test_suspended_organization_cannot_delete_without_a_where_clause(
        self, as_org_a_admin, admin_conn
    ):
        """Companion shape for DELETE, which is gated by `aeos_is_org_admin`.

        Run as an admin so DELETE authority actually exists; suspension is the
        only thing that should stop it. Pins `aeos_is_org_admin`'s
        organization-active condition against the same WHERE-less blind spot.
        """
        as_org_a_admin.rollback()
        admin_conn.execute(
            "UPDATE public.organizations SET status = 'suspended' WHERE id = %s",
            (ORG_A,),
        )
        try:
            with as_org_a_admin.cursor() as cur:
                cur.execute("DELETE FROM public.students")
                affected = cur.rowcount
            as_org_a_admin.commit()

            (remaining,) = admin_conn.execute(
                "SELECT count(*) FROM public.students WHERE organization_id = %s",
                (ORG_A,),
            ).fetchone()
            assert affected == 0, (
                f"a WHERE-less DELETE by a suspended organization's admin "
                f"removed {affected} row(s)"
            )
            assert remaining == 3, (
                f"suspended organization's rows were deleted: {remaining} left"
            )
        finally:
            as_org_a_admin.rollback()
            admin_conn.execute(
                "UPDATE public.organizations SET status = 'active' WHERE id = %s",
                (ORG_A,),
            )

    def test_suspended_organization_admin_cannot_delete(
        self, as_org_a_admin, admin_conn
    ):
        """Suspension must also contain admins, who hold DELETE authority.
        Pins the organization-active condition in `aeos_is_org_admin`."""
        as_org_a_admin.rollback()
        admin_conn.execute(
            "UPDATE public.organizations SET status = 'suspended' WHERE id = %s",
            (ORG_A,),
        )
        try:
            with as_org_a_admin.cursor() as cur:
                cur.execute("DELETE FROM public.students WHERE id = %s", (STUDENT_A,))
                assert cur.rowcount == 0, "suspended organization's admin could delete"
        finally:
            as_org_a_admin.rollback()
            admin_conn.execute(
                "UPDATE public.organizations SET status = 'active' WHERE id = %s",
                (ORG_A,),
            )

    def test_suspended_organization_cannot_insert_intervention_action(
        self, as_org_a, suspended_org_a
    ):
        """`intervention_actions_insert` is gated SOLELY by `aeos_can_write_org`
        (003), with no actor binding and no row to read. It is therefore the
        only operation that isolates that helper's organization-active
        condition: on UPDATE/DELETE the SELECT policy finds the row first and
        `aeos_has_org_access` masks the result. The table has no API route but
        is reachable directly through PostgREST.
        """
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with as_org_a.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.intervention_actions "
                    "(id, intervention_plan_id, action_type, description, status) "
                    "VALUES (%s, %s, 'check_in', 'Suspended-org write', 'pending')",
                    (str(uuid.uuid4()), PLAN_A),
                )
        as_org_a.rollback()

    def test_suspended_organization_admin_cannot_insert_school(
        self, as_org_a_admin, admin_conn
    ):
        """`schools_insert` is gated SOLELY by `aeos_is_org_admin`, isolating
        that helper's organization-active condition for the same reason."""
        as_org_a_admin.rollback()
        admin_conn.execute(
            "UPDATE public.organizations SET status = 'suspended' WHERE id = %s",
            (ORG_A,),
        )
        try:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with as_org_a_admin.cursor() as cur:
                    cur.execute(
                        "INSERT INTO public.schools "
                        "(id, organization_id, name, status) "
                        "VALUES (%s, %s, 'Suspended-org School', 'active')",
                        (str(uuid.uuid4()), ORG_A),
                    )
        finally:
            as_org_a_admin.rollback()
            admin_conn.execute(
                "UPDATE public.organizations SET status = 'active' WHERE id = %s",
                (ORG_A,),
            )

    def test_active_organization_admin_may_insert_school(self, as_org_a_admin):
        """Positive control for the pair above: an active tenant still works."""
        with as_org_a_admin.cursor() as cur:
            cur.execute(
                "INSERT INTO public.schools (id, organization_id, name, status) "
                "VALUES (%s, %s, 'Active School', 'active')",
                (str(uuid.uuid4()), ORG_A),
            )
            assert cur.rowcount == 1, "active organization's admin could not add a school"
        as_org_a_admin.rollback()

    def test_active_organization_still_works(self, as_org_a):
        """Positive control: suspension enforcement must not deny healthy tenants."""
        with as_org_a.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.students")
            (visible,) = cur.fetchone()
        # STUDENT_A, STUDENT_PEER and STUDENT_A_NO_SCHOOL.
        assert visible == 3, "active organization lost access to its own students"

    def test_disabled_member_cannot_read(self, as_org_a, admin_conn):
        as_org_a.rollback()
        admin_conn.execute(
            "UPDATE public.users SET status = 'disabled' WHERE id = %s", (USER_A,)
        )
        try:
            with as_org_a.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.students")
                (visible,) = cur.fetchone()
            assert visible == 0, "disabled member could still read"
        finally:
            as_org_a.rollback()
            admin_conn.execute(
                "UPDATE public.users SET status = 'active' WHERE id = %s", (USER_A,)
            )

    @pytest.mark.parametrize(
        "table", ["organizations", "users", "students", "assessments"]
    )
    def test_anonymous_role_sees_nothing(self, migrated_database, table):
        with psycopg.connect(migrated_database) as conn:
            conn.execute("SET ROLE anon")
            with conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM public.{table}")
                (visible,) = cur.fetchone()
            conn.rollback()
        assert visible == 0, f"anon could read public.{table}"


# ---------------------------------------------------------------------------
# M2 — peer access semantics within one tenant.
# UPDATE was creator-gated while DELETE was not; the destructive operation was
# the less restricted one. Updates are now open to same-tenant teachers/admins
# (ownership columns remain immutable) and DELETE is admin-only.
# ---------------------------------------------------------------------------


class TestPeerAccessSemantics:
    def test_teacher_may_update_peers_student(self, as_org_a):
        """A co-teacher must be able to edit a colleague's student record."""
        with as_org_a.cursor() as cur:
            cur.execute(
                "UPDATE public.students SET last_name = 'Edited' WHERE id = %s",
                (STUDENT_PEER,),
            )
            assert cur.rowcount == 1, "teacher could not update a peer's student"
        as_org_a.rollback()

    def test_teacher_may_not_delete_peers_student(self, as_org_a, admin_conn):
        with as_org_a.cursor() as cur:
            cur.execute("DELETE FROM public.students WHERE id = %s", (STUDENT_PEER,))
            assert cur.rowcount == 0, "teacher deleted a peer's student"
        as_org_a.commit()

        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM public.students WHERE id = %s", (STUDENT_PEER,)
            )
            (surviving,) = cur.fetchone()
        assert surviving == 1, "peer's student no longer exists"

    def test_teacher_may_not_delete_own_student(self, as_org_a):
        """DELETE is admin-only for the MVP, including the creator's own rows."""
        with as_org_a.cursor() as cur:
            cur.execute("DELETE FROM public.students WHERE id = %s", (STUDENT_A,))
            assert cur.rowcount == 0, "teacher deleted a student"
        as_org_a.rollback()

    def test_admin_may_delete_same_tenant_student(self, as_org_a_admin):
        with as_org_a_admin.cursor() as cur:
            cur.execute("DELETE FROM public.students WHERE id = %s", (STUDENT_PEER,))
            assert cur.rowcount == 1, "admin could not delete a same-tenant student"
        as_org_a_admin.rollback()

    def test_admin_may_not_delete_foreign_tenant_student(self, as_org_a_admin):
        with as_org_a_admin.cursor() as cur:
            cur.execute("DELETE FROM public.students WHERE id = %s", (STUDENT_B,))
            assert cur.rowcount == 0, "admin deleted another tenant's student"
        as_org_a_admin.rollback()

    def test_support_may_not_update(self, as_org_a_support):
        with as_org_a_support.cursor() as cur:
            cur.execute(
                "UPDATE public.students SET last_name = 'Edited' WHERE id = %s",
                (STUDENT_A,),
            )
            assert cur.rowcount == 0, "support role updated a student"
        as_org_a_support.rollback()

    def test_ownership_columns_remain_immutable_on_peer_update(self, as_org_a):
        """Opening UPDATE to peers must not open tenant or creator reassignment."""
        with as_org_a.cursor() as cur:
            with pytest.raises(
                (psycopg.errors.InsufficientPrivilege, psycopg.errors.RaiseException)
            ):
                cur.execute(
                    "UPDATE public.students SET created_by = %s WHERE id = %s",
                    (USER_A, STUDENT_PEER),
                )
        as_org_a.rollback()


# ---------------------------------------------------------------------------
# Negative control.
# ---------------------------------------------------------------------------


class TestNegativeControl:
    """Prove the tests above can fail.

    Each test disables one specific RLS protection, re-runs the exact attack the
    corresponding denial test performs, and asserts the breach becomes
    observable. If any of these stop detecting a breach, the denial tests above
    are no longer evidence of anything.
    """

    @pytest.fixture
    def students_rls_disabled(self, admin_conn, as_org_a):
        """Disable RLS on public.students for the duration of one test.

        ALTER TABLE needs ACCESS EXCLUSIVE, so the authenticated connection's
        transaction is released first on both entry and exit. Without the exit
        rollback, teardown deadlocks against the very transaction the test used.
        """
        as_org_a.rollback()
        admin_conn.execute("ALTER TABLE public.students DISABLE ROW LEVEL SECURITY")
        try:
            yield
        finally:
            as_org_a.rollback()
            admin_conn.execute("ALTER TABLE public.students ENABLE ROW LEVEL SECURITY")

    def test_select_breach_is_observable_without_rls(self, as_org_a, students_rls_disabled):
        with as_org_a.cursor() as cur:
            cur.execute("SELECT id FROM public.students WHERE id = %s", (STUDENT_B,))
            rows = cur.fetchall()
        assert len(rows) == 1, (
            "negative control failed: org B row still invisible with RLS disabled, "
            "so the SELECT denial test proves nothing"
        )

    def test_unfiltered_scan_breach_is_observable_without_rls(
        self, as_org_a, students_rls_disabled
    ):
        with as_org_a.cursor() as cur:
            cur.execute("SELECT organization_id::text FROM public.students")
            orgs = {row[0] for row in cur.fetchall()}
        assert ORG_B in orgs, (
            "negative control failed: unfiltered scan did not leak with RLS disabled"
        )

    def test_update_breach_is_observable_without_rls(
        self, as_org_a, admin_conn, students_rls_disabled
    ):
        with as_org_a.cursor() as cur:
            cur.execute(
                "UPDATE public.students SET last_name = 'TAMPERED' WHERE id = %s",
                (STUDENT_B,),
            )
            affected = cur.rowcount
        as_org_a.rollback()
        assert affected == 1, (
            "negative control failed: UPDATE still affected 0 rows with RLS disabled"
        )

    def test_delete_breach_is_observable_without_rls(
        self, as_org_a, students_rls_disabled
    ):
        with as_org_a.cursor() as cur:
            cur.execute("DELETE FROM public.students WHERE id = %s", (STUDENT_B,))
            affected = cur.rowcount
        as_org_a.rollback()
        assert affected == 1, (
            "negative control failed: DELETE still affected 0 rows with RLS disabled"
        )

    def test_suspension_denial_is_caused_by_rls_not_the_fixture(
        self, as_org_a, suspended_org_a, students_rls_disabled
    ):
        """Negative control for M1: with RLS off, a suspended organization's
        member can read again — proving the suspension denial above is enforced
        by policy, not by the fixture merely breaking the session."""
        with as_org_a.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.students")
            (visible,) = cur.fetchone()
        assert visible > 0, (
            "negative control failed: suspended-org reads stayed blocked with RLS "
            "disabled, so the suspension test proves nothing"
        )

    def test_insert_breach_is_observable_without_rls(
        self, as_org_a, students_rls_disabled
    ):
        new_id = str(uuid.uuid4())
        with as_org_a.cursor() as cur:
            cur.execute(
                "INSERT INTO public.students "
                "(id, organization_id, school_id, first_name, last_name, "
                " grade_level, status, created_by) "
                "VALUES (%s, %s, %s, 'Mallory', 'Injected', '8', 'active', %s)",
                (new_id, ORG_B, SCHOOL_B, USER_B),
            )
            affected = cur.rowcount
        as_org_a.rollback()
        assert affected == 1, (
            "negative control failed: INSERT into org B was still blocked with RLS disabled"
        )
