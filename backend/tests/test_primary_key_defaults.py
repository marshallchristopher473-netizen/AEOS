"""Executed proof that the application's own insert path can create a row.

WHAT THIS FILE IS FOR
---------------------
Every create endpoint in this backend reaches the database through exactly one
function, `app.services.tenant_scope.insert_tenant_scoped_row`. It builds
`{**payload, "organization_id": <server-derived>}` and never supplies `id`.

Nothing in the suite had ever run that payload shape against real PostgreSQL:

  * `tests/fakes.py` auto-assigns an id (`row.setdefault("id", ...)`), so the
    FastAPI tests exercised an insert the database never sees.
  * `tests/test_rls_enforcement.py` seeds every synthetic row with an explicit
    literal id, because its subject is tenant isolation, not row creation.

The gap that hid in between was that 001_initial_schema.sql declares every
primary key as `id UUID PRIMARY KEY` with no DEFAULT, so each of
POST /students, /assessments, /assessment-results and /intervention-plans
failed against the real schema with:

    null value in column "id" of relation "students"
    violates not-null constraint

005_primary_key_defaults.sql attaches `gen_random_uuid()` to each primary key.
This module runs the real `insert_tenant_scoped_row` against a database built
from shim + migrations 001-005 and asserts a row is created and given an id.

NO REAL DATA. Every row is synthetic and generated in this file.

RUNNING LOCALLY
---------------
    export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
    python -m pytest tests/test_primary_key_defaults.py -v

Without AEOS_TEST_DATABASE_URL these tests SKIP, matching
tests/test_rls_enforcement.py. AEOS_REQUIRE_RLS_TESTS=1 turns a missing
database into a hard failure rather than a silent skip.
"""

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List

import pytest

from app.services.tenant_scope import insert_tenant_scoped_row

REQUIRED = os.environ.get("AEOS_REQUIRE_RLS_TESTS") == "1"
DATABASE_URL = os.environ.get("AEOS_TEST_DATABASE_URL")

# Same ordering contract as tests/test_rls_enforcement.py: the required-mode
# guard runs before any import that could skip the module, so required mode can
# never report success having executed nothing.
if REQUIRED and not DATABASE_URL:
    raise RuntimeError(
        "AEOS_REQUIRE_RLS_TESTS=1 but AEOS_TEST_DATABASE_URL is unset. "
        "The primary-key default tests would have skipped silently."
    )

if REQUIRED:
    import psycopg
else:
    psycopg = pytest.importorskip(
        "psycopg", reason="psycopg is required for primary-key default tests"
    )

from psycopg.conninfo import conninfo_to_dict, make_conninfo  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = BACKEND_DIR / "supabase" / "migrations"
SHIM_SQL = Path(__file__).resolve().parent / "sql" / "supabase_shim.sql"

# Migration order must match tests/test_rls_enforcement.py.
MIGRATIONS = (
    "001_initial_schema.sql",
    "002_tenant_rls.sql",
    "003_fk_relationship_hardening.sql",
    "004_org_lifecycle_and_write_authority.sql",
    "005_primary_key_defaults.sql",
)

# Tables the application inserts into, plus the rest of the tenant model. A
# primary key with no default is unwritable by any client that does not invent
# its own id, so the whole set is asserted rather than only today's endpoints.
TABLES_REQUIRING_A_PRIMARY_KEY_DEFAULT = (
    "organizations",
    "schools",
    "users",
    "students",
    "assessments",
    "assessment_results",
    "ai_recommendations",
    "intervention_plans",
    "intervention_actions",
    "progress_events",
    "audit_logs",
)

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="AEOS_TEST_DATABASE_URL is not set; primary-key default tests require PostgreSQL",
)

ORG = "0ccc0000-0000-4000-8000-000000000001"
SCHOOL = "0ccc0000-0000-4000-8000-000000000002"
USER = "0ccc0000-0000-4000-8000-000000000003"
AUTH_USER = "0ccc0000-0000-4000-8000-000000000004"
STUDENT = "0ccc0000-0000-4000-8000-000000000005"
ASSESSMENT = "0ccc0000-0000-4000-8000-000000000006"

SEED_SQL = f"""
INSERT INTO public.organizations (id, name, type, status) VALUES
    ('{ORG}', 'Synthetic Org C', 'district', 'active');

INSERT INTO public.schools (id, organization_id, name, status) VALUES
    ('{SCHOOL}', '{ORG}', 'Synthetic School C', 'active');

INSERT INTO public.users
    (id, organization_id, auth_user_id, email, full_name, role, status) VALUES
    ('{USER}', '{ORG}', '{AUTH_USER}', 'teacher-c@synthetic.test', 'Teacher C', 'teacher', 'active');

INSERT INTO public.students
    (id, organization_id, school_id, first_name, last_name, grade_level, status, created_by) VALUES
    ('{STUDENT}', '{ORG}', '{SCHOOL}', 'Cleo', 'Synthetic', '6', 'active', '{USER}');

INSERT INTO public.assessments
    (id, organization_id, student_id, created_by, title, assessment_type, status) VALUES
    ('{ASSESSMENT}', '{ORG}', '{STUDENT}', '{USER}', 'Org C Assessment', 'ela', 'draft');
"""


class _PostgresQuery:
    """The slice of the Supabase query builder `tenant_scope` actually uses.

    Deliberately NOT the FakeClient: the whole point of this module is to run
    the real `insert_tenant_scoped_row` against real PostgreSQL, so this
    adapter must never invent a value the application does not send. It
    translates the insert verbatim and lets the database answer.
    """

    def __init__(self, connection, table: str):
        self._connection = connection
        self._table = table
        self._payload: Dict[str, Any] = {}

    def insert(self, payload: Dict[str, Any]) -> "_PostgresQuery":
        self._payload = dict(payload)
        return self

    def execute(self) -> "_PostgresResponse":
        columns = ", ".join(self._payload)
        placeholders = ", ".join(["%s"] * len(self._payload))
        sql = (
            f"INSERT INTO public.{self._table} ({columns}) "
            f"VALUES ({placeholders}) RETURNING *"
        )
        cursor = self._connection.execute(sql, tuple(self._payload.values()))
        names = [description.name for description in cursor.description]
        rows = [dict(zip(names, record)) for record in cursor.fetchall()]
        return _PostgresResponse(rows)


class _PostgresResponse:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data


class _PostgresClient:
    def __init__(self, connection):
        self._connection = connection

    def table(self, name: str) -> _PostgresQuery:
        return _PostgresQuery(self._connection, name)


@pytest.fixture(scope="module")
def migrated_database():
    """A scratch database built from shim + migrations, dropped afterwards."""
    scratch = f"aeos_pk_defaults_{uuid.uuid4().hex[:12]}"
    params = conninfo_to_dict(DATABASE_URL)
    params["dbname"] = scratch
    scratch_url = make_conninfo(**params)

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{scratch}"')

    try:
        with psycopg.connect(scratch_url, autocommit=True) as conn:
            conn.execute(SHIM_SQL.read_text())
            for migration in MIGRATIONS:
                conn.execute((MIGRATIONS_DIR / migration).read_text())
            conn.execute(SEED_SQL)
        yield scratch_url
    finally:
        with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
            conn.execute(f'DROP DATABASE IF EXISTS "{scratch}" WITH (FORCE)')


@pytest.fixture
def service_role_client(migrated_database):
    """Connects as the service role, matching the FastAPI runtime path."""
    with psycopg.connect(migrated_database, autocommit=True) as conn:
        conn.execute("SET ROLE service_role")
        yield _PostgresClient(conn)


@pytest.mark.parametrize("table", TABLES_REQUIRING_A_PRIMARY_KEY_DEFAULT)
def test_every_tenant_table_can_generate_its_own_primary_key(migrated_database, table):
    """Without a default, no writer that omits `id` can create a row at all."""
    with psycopg.connect(migrated_database) as conn:
        default = conn.execute(
            "SELECT column_default FROM information_schema.columns"
            " WHERE table_schema = 'public' AND table_name = %s AND column_name = 'id'",
            (table,),
        ).fetchone()

    assert default is not None, f"public.{table} has no id column"
    assert default[0] == "gen_random_uuid()", (
        f"public.{table}.id has default {default[0]!r}; a writer that omits `id` "
        "— which is every AEOS create endpoint — cannot insert into this table."
    )


def test_student_create_path_inserts_without_supplying_an_id(service_role_client):
    """The exact payload POST /students builds, against the real schema."""
    row = insert_tenant_scoped_row(
        service_role_client,
        "students",
        {
            "first_name": "Cara",
            "last_name": "Gamma",
            "student_number": "C-003",
            "iep_status": False,
            "created_by": USER,
        },
        ORG,
    )

    assert uuid.UUID(str(row["id"]))
    assert str(row["organization_id"]) == ORG
    assert str(row["created_by"]) == USER


def test_assessment_create_path_inserts_without_supplying_an_id(service_role_client):
    row = insert_tenant_scoped_row(
        service_role_client,
        "assessments",
        {
            "student_id": STUDENT,
            "created_by": USER,
            "title": "Synthetic Reading Screen",
            "assessment_type": "ela",
        },
        ORG,
    )

    assert uuid.UUID(str(row["id"]))
    assert str(row["organization_id"]) == ORG


def test_assessment_result_create_path_inserts_without_supplying_an_id(service_role_client):
    row = insert_tenant_scoped_row(
        service_role_client,
        "assessment_results",
        {
            "assessment_id": ASSESSMENT,
            "student_id": STUDENT,
            "created_by": USER,
            "summary": "Synthetic result",
        },
        ORG,
    )

    assert uuid.UUID(str(row["id"]))
    assert str(row["organization_id"]) == ORG


def test_intervention_plan_create_path_inserts_without_supplying_an_id(service_role_client):
    row = insert_tenant_scoped_row(
        service_role_client,
        "intervention_plans",
        {
            "student_id": STUDENT,
            "assessment_id": ASSESSMENT,
            "created_by": USER,
            "title": "Synthetic Reading Plan",
        },
        ORG,
    )

    assert uuid.UUID(str(row["id"]))
    assert str(row["organization_id"]) == ORG


def test_generated_identifiers_are_distinct(service_role_client):
    """A constant default would satisfy every assertion above exactly once."""
    ids = {
        str(
            insert_tenant_scoped_row(
                service_role_client,
                "students",
                {
                    "first_name": "Repeat",
                    "last_name": f"Synthetic{index}",
                    "created_by": USER,
                },
                ORG,
            )["id"]
        )
        for index in range(3)
    }

    assert len(ids) == 3, f"primary keys were not distinct: {ids}"
