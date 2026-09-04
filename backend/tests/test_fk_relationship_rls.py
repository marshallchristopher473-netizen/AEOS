import re
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
FK_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "003_fk_relationship_hardening.sql"
BASE_RLS_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "002_tenant_rls.sql"

# Column names that exist on more than one table participating in these
# policies' correlated subqueries. Derived by inspecting
# 001_initial_schema.sql and the assessment_results table added by this
# migration:
#   organization_id -> organizations(as "id"), schools, users, students,
#                       assessments, ai_recommendations, intervention_plans,
#                       progress_events, audit_logs, assessment_results
#   student_id       -> assessments, intervention_plans, assessment_results
#   assessment_id    -> ai_recommendations, intervention_plans,
#                       assessment_results
#   created_by       -> students, assessments, ai_recommendations,
#                       intervention_plans, assessment_results
# Revisit this list whenever a new tenant-owned table or column is added.
RISKY_COLUMNS = (
    "organization_id",
    "student_id",
    "assessment_id",
    "created_by",
)


def policy_sql(sql: str, policy_name: str) -> str:
    marker = f"CREATE POLICY {policy_name}\n"
    assert marker in sql
    return sql.split(marker, 1)[1].split(";", 1)[0]


def bare_references(text: str, column: str) -> list:
    """Unqualified occurrences of `column` in `text` — not immediately
    preceded by a `.` (i.e. not written as `alias.column`).

    Inside a correlated EXISTS/JOIN subquery, an unqualified column name
    resolves to the *innermost* table that has a column of that name, not
    necessarily the outer policy row. A bare reference to a column that
    also exists on the inner (related) table therefore silently binds to
    the inner table, which can collapse an intended cross-tenant comparison
    into a self-referential tautology. This is exactly the bug this
    migration's policies must never reintroduce.
    """
    pattern = re.compile(rf"(?<!\.)\b{re.escape(column)}\b")
    return pattern.findall(text)


def test_bare_reference_detector_flags_the_original_bug_pattern():
    # Guard the guard: prove the detector actually catches the exact
    # shadowing pattern the original (pre-fix) students_insert policy
    # contained, and does not false-positive on the corrected form.
    buggy_fragment = (
        "SELECT 1 FROM public.schools AS related_school "
        "WHERE related_school.id = school_id "
        "AND related_school.organization_id = organization_id"
    )
    assert bare_references(buggy_fragment, "organization_id")

    fixed_fragment = (
        "SELECT 1 FROM public.schools AS related_school "
        "WHERE related_school.id = students.school_id "
        "AND related_school.organization_id = students.organization_id"
    )
    assert not bare_references(fixed_fragment, "organization_id")


def test_fk_migration_is_forward_only():
    # This migration must not edit either prior migration file.
    assert "DROP TABLE" not in FK_MIGRATION.read_text()
    original_002 = BASE_RLS_MIGRATION.read_text()
    assert "ai_recommendations_insert" in original_002  # sanity: unedited file
    assert "related_student.organization_id = organization_id" in original_002
    # ^ 002's own assessments_insert/update carry the same unqualified-
    # reference bug this migration exists to close for every other table;
    # 002 is intentionally left as-is (forward-only) and superseded by this
    # migration's DROP POLICY + CREATE POLICY for assessments_insert/update.


def test_no_bare_risky_column_references_in_any_policy_body():
    sql = FK_MIGRATION.read_text()
    policy_names = re.findall(r"CREATE POLICY (\w+)", sql)
    assert len(policy_names) == 15  # sanity: every expected policy is present

    for policy_name in policy_names:
        policy = policy_sql(sql, policy_name)
        for column in RISKY_COLUMNS:
            bare = bare_references(policy, column)
            assert not bare, (
                f"policy {policy_name} references unqualified '{column}' — "
                "in a correlated subquery this can bind to the wrong table "
                "and silently collapse a cross-tenant check into a tautology"
            )


def assert_actor_is_bound_to_row_organization(policy: str, table: str):
    assert "public.aeos_is_current_actor_for_org(" in policy
    assert f"{table}.created_by" in policy
    assert f"{table}.organization_id" in policy


def test_actor_helper_binds_subject_user_and_row_organization():
    sql = FK_MIGRATION.read_text()

    assert "CREATE OR REPLACE FUNCTION public.aeos_is_current_actor_for_org(" in sql
    helper = sql.split(
        "CREATE OR REPLACE FUNCTION public.aeos_is_current_actor_for_org(", 1
    )[1].split("$$;", 1)[0]
    for relationship in (
        "membership.id = target_user_id",
        "membership.organization_id = target_organization_id",
        "membership.auth_user_id = auth.uid()::text",
        "membership.status = 'active'",
    ):
        assert relationship in helper


def test_identity_trigger_prevents_tenant_and_creator_reassignment():
    sql = FK_MIGRATION.read_text()

    assert "NEW.organization_id IS DISTINCT FROM OLD.organization_id" in sql
    assert "NEW.created_by IS DISTINCT FROM OLD.created_by" in sql
    for table in (
        "students",
        "assessments",
        "ai_recommendations",
        "intervention_plans",
        "assessment_results",
    ):
        assert f"CREATE TRIGGER {table}_preserve_row_identity" in sql
        assert f"BEFORE UPDATE ON public.{table}" in sql


def test_policies_do_not_self_query_their_protected_table_to_preserve_identity():
    sql = FK_MIGRATION.read_text()

    for table in (
        "students",
        "assessments",
        "ai_recommendations",
        "intervention_plans",
        "assessment_results",
    ):
        update_policy = policy_sql(sql, f"{table}_update")
        assert f"FROM public.{table} AS original" not in update_policy


def test_student_school_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS students_insert ON public.students;" in sql
    assert "DROP POLICY IF EXISTS students_update ON public.students;" in sql
    for policy_name in ("students_insert", "students_update"):
        policy = policy_sql(sql, policy_name)
        assert "related_school.id = students.school_id" in policy
        assert "related_school.organization_id = students.organization_id" in policy
    for policy_name in ("students_insert", "students_update"):
        assert_actor_is_bound_to_row_organization(policy_sql(sql, policy_name), "students")


def test_assessment_student_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS assessments_insert ON public.assessments;" in sql
    assert "DROP POLICY IF EXISTS assessments_update ON public.assessments;" in sql
    for policy_name in ("assessments_insert", "assessments_update"):
        policy = policy_sql(sql, policy_name)
        assert "related_student.id = assessments.student_id" in policy
        assert "related_student.organization_id = assessments.organization_id" in policy
    for policy_name in ("assessments_insert", "assessments_update"):
        assert_actor_is_bound_to_row_organization(policy_sql(sql, policy_name), "assessments")


def test_recommendation_assessment_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS ai_recommendations_insert ON public.ai_recommendations;" in sql
    assert "DROP POLICY IF EXISTS ai_recommendations_update ON public.ai_recommendations;" in sql
    for policy_name in ("ai_recommendations_insert", "ai_recommendations_update"):
        policy = policy_sql(sql, policy_name)
        assert "related_student.id = related_assessment.student_id" in policy
        assert "related_assessment.id = ai_recommendations.assessment_id" in policy
        assert (
            "related_assessment.organization_id = ai_recommendations.organization_id"
            in policy
        )
        assert "related_student.organization_id = ai_recommendations.organization_id" in policy
    for policy_name in ("ai_recommendations_insert", "ai_recommendations_update"):
        assert_actor_is_bound_to_row_organization(
            policy_sql(sql, policy_name), "ai_recommendations"
        )


def test_intervention_plan_student_and_assessment_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS intervention_plans_insert ON public.intervention_plans;" in sql
    assert "DROP POLICY IF EXISTS intervention_plans_update ON public.intervention_plans;" in sql
    for policy_name in ("intervention_plans_insert", "intervention_plans_update"):
        policy = policy_sql(sql, policy_name)
        assert "related_student.id = intervention_plans.student_id" in policy
        assert "related_student.organization_id = intervention_plans.organization_id" in policy
        assert "related_assessment.id = intervention_plans.assessment_id" in policy
        assert "related_assessment.organization_id = intervention_plans.organization_id" in policy
        assert "related_assessment.student_id = intervention_plans.student_id" in policy
    for policy_name in ("intervention_plans_insert", "intervention_plans_update"):
        assert_actor_is_bound_to_row_organization(
            policy_sql(sql, policy_name), "intervention_plans"
        )


def test_intervention_action_plan_and_assignee_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS intervention_actions_insert ON public.intervention_actions;" in sql
    assert "DROP POLICY IF EXISTS intervention_actions_update ON public.intervention_actions;" in sql
    for policy_name in ("intervention_actions_insert", "intervention_actions_update"):
        policy = policy_sql(sql, policy_name)
        assert "parent_plan.id = intervention_actions.intervention_plan_id" in policy
        assert "assignee.id = intervention_actions.assigned_to" in policy
        assert "assignee.organization_id = parent_plan.organization_id" in policy


def test_progress_event_student_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS progress_events_insert ON public.progress_events;" in sql
    policy = policy_sql(sql, "progress_events_insert")
    assert "related_student.id = progress_events.student_id" in policy
    assert "related_student.organization_id = progress_events.organization_id" in policy
    assert "public.aeos_is_current_actor_for_org(" in policy
    assert "progress_events.actor_id" in policy
    # Append-only log: no update policy is defined for this table.
    assert "CREATE POLICY progress_events_update" not in sql


def test_assessment_results_table_and_rls_are_present():
    sql = FK_MIGRATION.read_text()

    assert "CREATE TABLE public.assessment_results (" in sql
    assert "ALTER TABLE public.assessment_results ENABLE ROW LEVEL SECURITY;" in sql
    assert "ALTER TABLE public.assessment_results FORCE ROW LEVEL SECURITY;" in sql
    for policy in (
        "assessment_results_select",
        "assessment_results_insert",
        "assessment_results_update",
        "assessment_results_delete",
    ):
        assert f"CREATE POLICY {policy}" in sql
    for policy_name in ("assessment_results_insert", "assessment_results_update"):
        policy = policy_sql(sql, policy_name)
        assert "related_assessment.id = assessment_results.assessment_id" in policy
        assert "related_assessment.organization_id = assessment_results.organization_id" in policy
        assert "related_assessment.student_id = assessment_results.student_id" in policy
        assert "related_student.id = assessment_results.student_id" in policy
        assert "related_student.organization_id = assessment_results.organization_id" in policy
    for policy_name in ("assessment_results_insert", "assessment_results_update"):
        assert_actor_is_bound_to_row_organization(
            policy_sql(sql, policy_name), "assessment_results"
        )
