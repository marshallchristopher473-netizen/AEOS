"""Executed proof that ONE documented equivalent mutant is genuinely equivalent.

The mutation suite (`tests/security_mutations.py`) records exactly one mutation
as EQUIVALENT: removing `AND tenant.status = 'active'` from
`public.aeos_can_write_org`. A mutation marked equivalent is excluded from the
mutation score, so the claim must be *proved*, not asserted — otherwise
"equivalent" becomes a way to launder a surviving mutant.

WHAT THIS PROVES
----------------
Against a database carrying ONLY that mutation, with organization A suspended
and acting as an authenticated teacher of organization A:

  1. the mutation is LIVE   — `aeos_can_write_org(ORG_A)` returns TRUE, while
     the unmutated helpers `aeos_has_org_access`, `aeos_is_org_admin` and
     `aeos_is_current_actor_for_org` all return FALSE; and
  2. the mutation is INERT  — every reachable write against organization A is
     still refused, so no observable security behaviour changes.

Both halves are required. (1) alone would not show the control is redundant;
(2) alone could be satisfied by a mutation that never applied.

WHY IT IS INERT (the structural reason the run below confirms)
--------------------------------------------------------------
Every write path carries the suspended-organization condition independently of
`aeos_can_write_org`:

  * INSERT  — every INSERT policy that calls `aeos_can_write_org` also calls
              `aeos_is_current_actor_for_org(created_by/actor_id, ...)`, which
              is unmutated and still requires `tenant.status = 'active'`.
  * UPDATE  — PostgreSQL applies the SELECT policy when locating the target
              row, and SELECT is governed by the unmutated
              `aeos_has_org_access`, so no row is ever found to update.
  * DELETE  — governed by the unmutated `aeos_is_org_admin`.

If any *_insert policy drops its actor binding, or any write path stops
reading an existing row, this proof must be re-run and the EQUIVALENT flag
re-checked.

RUNNING
-------
    export AEOS_TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres
    python -m tests.equivalence_proof_can_write_org

Exit code 0 means the equivalence claim holds.
"""

import os
import sys
import uuid
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

BACKEND = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = BACKEND / "supabase" / "migrations"
SHIM_SQL = Path(__file__).resolve().parent / "sql" / "supabase_shim.sql"

MIGRATIONS = (
    "001_initial_schema.sql",
    "002_tenant_rls.sql",
    "003_fk_relationship_hardening.sql",
    "004_org_lifecycle_and_write_authority.sql",
)

# The mutation under proof, character-identical to the entry in
# tests/security_mutations.py.
MUTATION_TARGET = "004_org_lifecycle_and_write_authority.sql"
MUTATION_OLD = (
    "          AND membership.status = 'active'\n"
    "          AND tenant.status = 'active'\n"
    "          AND membership.role IN ('teacher', 'admin')"
)
MUTATION_NEW = (
    "          AND membership.status = 'active'\n"
    "          AND membership.role IN ('teacher', 'admin')"
)

ORG_A = "0aaa0000-0000-4000-8000-000000000001"
SCHOOL_A = "0aaa0000-0000-4000-8000-000000000003"
USER_A = "0aaa0000-0000-4000-8000-000000000005"
AUTH_A = "0aaa0000-0000-4000-8000-000000000007"
STUDENT_A = "0aaa0000-0000-4000-8000-000000000009"
ASSESSMENT_A = "0aaa0000-0000-4000-8000-00000000000b"
PLAN_A = "0aaa0000-0000-4000-8000-00000000000d"
RESULT_A = "0aaa0000-0000-4000-8000-000000000017"
ACTION_A = "0aaa0000-0000-4000-8000-000000000019"

SEED_SQL = f"""
INSERT INTO public.organizations (id, name, type, status) VALUES
    ('{ORG_A}', 'Synthetic Org A', 'district', 'active');
INSERT INTO public.schools (id, organization_id, name, status) VALUES
    ('{SCHOOL_A}', '{ORG_A}', 'Synthetic School A', 'active');
INSERT INTO public.users
    (id, organization_id, auth_user_id, email, full_name, role, status) VALUES
    ('{USER_A}', '{ORG_A}', '{AUTH_A}', 'teacher-a@synthetic.test',
     'Teacher A', 'teacher', 'active');
INSERT INTO public.students
    (id, organization_id, school_id, first_name, last_name, grade_level, status, created_by)
VALUES
    ('{STUDENT_A}', '{ORG_A}', '{SCHOOL_A}', 'Ada', 'Synthetic', '6', 'active', '{USER_A}');
INSERT INTO public.assessments
    (id, organization_id, student_id, created_by, title, assessment_type, status) VALUES
    ('{ASSESSMENT_A}', '{ORG_A}', '{STUDENT_A}', '{USER_A}', 'Org A Assessment', 'ela', 'draft');
INSERT INTO public.intervention_plans
    (id, organization_id, student_id, assessment_id, created_by, title, status) VALUES
    ('{PLAN_A}', '{ORG_A}', '{STUDENT_A}', '{ASSESSMENT_A}', '{USER_A}', 'Org A Plan', 'draft');
INSERT INTO public.assessment_results
    (id, organization_id, assessment_id, student_id, created_by, summary, status) VALUES
    ('{RESULT_A}', '{ORG_A}', '{ASSESSMENT_A}', '{STUDENT_A}', '{USER_A}', 'Org A Result', 'draft');
INSERT INTO public.intervention_actions
    (id, intervention_plan_id, action_type, description, status) VALUES
    ('{ACTION_A}', '{PLAN_A}', 'small_group', 'Org A Action', 'pending');
"""

NEW = str(uuid.uuid4())

# (label, SQL). Every one of these must be refused while ORG_A is suspended.
WRITES = [
    ("students INSERT", f"""
        INSERT INTO public.students
            (organization_id, school_id, first_name, last_name, grade_level, status, created_by)
        VALUES ('{ORG_A}', '{SCHOOL_A}', 'Mallory', 'Synthetic', '6', 'active', '{USER_A}')
     """),
    ("students UPDATE", f"""
        UPDATE public.students SET first_name = 'Mutated' WHERE id = '{STUDENT_A}'
     """),
    ("students DELETE", f"""
        DELETE FROM public.students WHERE id = '{STUDENT_A}'
     """),
    ("assessments INSERT", f"""
        INSERT INTO public.assessments
            (organization_id, student_id, created_by, title, assessment_type, status)
        VALUES ('{ORG_A}', '{STUDENT_A}', '{USER_A}', 'Mutated', 'ela', 'draft')
     """),
    ("assessments UPDATE", f"""
        UPDATE public.assessments SET title = 'Mutated' WHERE id = '{ASSESSMENT_A}'
     """),
    ("assessments DELETE", f"""
        DELETE FROM public.assessments WHERE id = '{ASSESSMENT_A}'
     """),
    ("intervention_plans INSERT", f"""
        INSERT INTO public.intervention_plans
            (organization_id, student_id, assessment_id, created_by, title, status)
        VALUES ('{ORG_A}', '{STUDENT_A}', '{ASSESSMENT_A}', '{USER_A}', 'Mutated', 'draft')
     """),
    ("intervention_plans UPDATE", f"""
        UPDATE public.intervention_plans SET title = 'Mutated' WHERE id = '{PLAN_A}'
     """),
    ("intervention_plans DELETE", f"""
        DELETE FROM public.intervention_plans WHERE id = '{PLAN_A}'
     """),
    ("assessment_results INSERT", f"""
        INSERT INTO public.assessment_results
            (organization_id, assessment_id, student_id, created_by, summary, status)
        VALUES ('{ORG_A}', '{ASSESSMENT_A}', '{STUDENT_A}', '{USER_A}', 'Mutated', 'draft')
     """),
    ("assessment_results UPDATE", f"""
        UPDATE public.assessment_results SET summary = 'Mutated' WHERE id = '{RESULT_A}'
     """),
    ("assessment_results DELETE", f"""
        DELETE FROM public.assessment_results WHERE id = '{RESULT_A}'
     """),
    ("intervention_actions INSERT", f"""
        INSERT INTO public.intervention_actions
            (intervention_plan_id, action_type, description, status)
        VALUES ('{PLAN_A}', 'small_group', 'Mutated', 'pending')
     """),
    ("intervention_actions UPDATE", f"""
        UPDATE public.intervention_actions SET description = 'Mutated' WHERE id = '{ACTION_A}'
     """),
    ("intervention_actions DELETE", f"""
        DELETE FROM public.intervention_actions WHERE id = '{ACTION_A}'
     """),
    ("progress_events INSERT", f"""
        INSERT INTO public.progress_events
            (organization_id, student_id, actor_id, event_type, event_message)
        VALUES ('{ORG_A}', '{STUDENT_A}', '{USER_A}', 'progress_logged', 'Mutated')
     """),
    ("ai_recommendations INSERT", f"""
        INSERT INTO public.ai_recommendations
            (organization_id, assessment_id, created_by, model_name,
             recommendation_text, status)
        VALUES ('{ORG_A}', '{ASSESSMENT_A}', '{USER_A}', 'test-model',
                'Mutated', 'generated')
     """),
    ("schools INSERT", f"""
        INSERT INTO public.schools (organization_id, name, status)
        VALUES ('{ORG_A}', 'Mutated School', 'active')
     """),
    ("schools UPDATE", f"""
        UPDATE public.schools SET name = 'Mutated' WHERE id = '{SCHOOL_A}'
     """),
    ("schools DELETE", f"""
        DELETE FROM public.schools WHERE id = '{SCHOOL_A}'
     """),
]


def _become(conn, auth_user_id):
    conn.execute("SELECT set_config('role', 'authenticated', false)")
    conn.execute(
        "SELECT set_config('request.jwt.claims', %s, false)",
        ('{"sub": "%s", "role": "authenticated"}' % auth_user_id,),
    )
    conn.execute("SET ROLE authenticated")


def main():
    database_url = os.environ.get("AEOS_TEST_DATABASE_URL")
    if not database_url:
        print("AEOS_TEST_DATABASE_URL is unset; this proof requires PostgreSQL.")
        return 1

    db_name = f"aeos_equiv_{uuid.uuid4().hex[:12]}"
    params = conninfo_to_dict(database_url)
    params["dbname"] = db_name
    target_url = make_conninfo(**params)

    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{db_name}"')

    failures = []
    try:
        with psycopg.connect(target_url, autocommit=True) as conn:
            conn.execute(SHIM_SQL.read_text())
            for migration in MIGRATIONS:
                sql = (MIGRATIONS_DIR / migration).read_text()
                if migration == MUTATION_TARGET:
                    if MUTATION_OLD not in sql:
                        print("FATAL: mutation anchor not found; this proof is stale.")
                        return 1
                    sql = sql.replace(MUTATION_OLD, MUTATION_NEW, 1)
                    print(f"applied mutation to {migration}")
                conn.execute(sql)

            conn.execute(
                "GRANT ALL ON ALL TABLES IN SCHEMA public "
                "TO anon, authenticated, service_role"
            )
            conn.execute(
                "GRANT ALL ON ALL SEQUENCES IN SCHEMA public "
                "TO anon, authenticated, service_role"
            )
            conn.execute(SEED_SQL)
            # Suspend the tenant. This is the condition the mutation removed.
            conn.execute(
                "UPDATE public.organizations SET status = 'suspended' WHERE id = %s",
                (ORG_A,),
            )

        print()
        print("STEP 1 — the mutation is LIVE (helper states with ORG_A suspended)")
        with psycopg.connect(target_url) as conn:
            _become(conn, AUTH_A)
            helpers = {
                "aeos_can_write_org (MUTATED)":
                    f"SELECT public.aeos_can_write_org('{ORG_A}')",
                "aeos_has_org_access (unmutated)":
                    f"SELECT public.aeos_has_org_access('{ORG_A}')",
                "aeos_is_org_admin (unmutated)":
                    f"SELECT public.aeos_is_org_admin('{ORG_A}')",
                "aeos_is_current_actor_for_org (unmutated)":
                    f"SELECT public.aeos_is_current_actor_for_org('{USER_A}', '{ORG_A}')",
            }
            states = {}
            for label, sql in helpers.items():
                states[label] = conn.execute(sql).fetchone()[0]
                print(f"  {label:<45} -> {states[label]}")

            if states["aeos_can_write_org (MUTATED)"] is not True:
                failures.append(
                    "mutation is NOT live: aeos_can_write_org did not return TRUE "
                    "for a suspended organization, so this proof shows nothing"
                )
            for label in list(helpers)[1:]:
                if states[label] is not False:
                    failures.append(f"unmutated helper {label} unexpectedly returned {states[label]}")

        print()
        print("STEP 2 — the mutation is INERT (every reachable write still refused)")
        allowed = []
        for label, sql in WRITES:
            with psycopg.connect(target_url) as conn:
                _become(conn, AUTH_A)
                try:
                    cursor = conn.execute(sql)
                    affected = cursor.rowcount
                    conn.commit()
                    if affected and affected > 0:
                        allowed.append(f"{label} (rows affected: {affected})")
                        print(f"  {label:<32} -> ALLOWED ({affected} rows)  <-- BREACH")
                    else:
                        print(f"  {label:<32} -> refused (0 rows)")
                except psycopg.Error as exc:
                    conn.rollback()
                    reason = type(exc).__name__
                    print(f"  {label:<32} -> refused ({reason})")

        if allowed:
            failures.append(
                "the mutation changed observable behaviour; these writes "
                "succeeded against a suspended organization: " + "; ".join(allowed)
            )
    finally:
        with psycopg.connect(database_url, autocommit=True) as conn:
            conn.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (db_name,),
            )
            conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')

    print()
    if failures:
        print("EQUIVALENCE CLAIM REJECTED:")
        for failure in failures:
            print(f"  - {failure}")
        print("\nThis mutant must be reclassified (SURVIVED or KILLED), not "
              "excluded from the mutation score.")
        return 1

    print("EQUIVALENCE CLAIM UPHELD.")
    print(f"  aeos_can_write_org was live and permissive for a suspended tenant,")
    print(f"  yet all {len(WRITES)} reachable writes were still refused.")
    print("  Removing `tenant.status = 'active'` from aeos_can_write_org alone "
          "cannot change observable security behaviour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
