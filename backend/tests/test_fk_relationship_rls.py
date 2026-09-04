from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
FK_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "003_fk_relationship_hardening.sql"
BASE_RLS_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "002_tenant_rls.sql"


def policy_sql(sql: str, policy_name: str) -> str:
    marker = f"CREATE POLICY {policy_name}\n"
    assert marker in sql
    return sql.split(marker, 1)[1].split(";", 1)[0]


def test_fk_migration_is_forward_only():
    # This migration must not edit either prior migration file.
    assert "DROP TABLE" not in FK_MIGRATION.read_text()
    original_002 = BASE_RLS_MIGRATION.read_text()
    assert "ai_recommendations_insert" in original_002  # sanity: unedited file


def test_student_school_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS students_insert ON public.students;" in sql
    assert "DROP POLICY IF EXISTS students_update ON public.students;" in sql
    for policy_name in ("students_insert", "students_update"):
        policy = policy_sql(sql, policy_name)
        assert "related_school.id = students.school_id" in policy
        assert "related_school.organization_id = students.organization_id" in policy


def test_recommendation_assessment_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS ai_recommendations_insert ON public.ai_recommendations;" in sql
    assert "DROP POLICY IF EXISTS ai_recommendations_update ON public.ai_recommendations;" in sql
    for policy_name in ("ai_recommendations_insert", "ai_recommendations_update"):
        policy = policy_sql(sql, policy_name)
        assert "created_by = ANY(public.aeos_current_user_ids())" in policy
        assert "related_student.id = related_assessment.student_id" in policy
        assert "related_assessment.id = ai_recommendations.assessment_id" in policy
        assert (
            "related_assessment.organization_id = ai_recommendations.organization_id"
            in policy
        )
        assert "related_student.organization_id = ai_recommendations.organization_id" in policy


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
        assert "created_by = ANY(public.aeos_current_user_ids())" in policy
        assert "related_assessment.id = assessment_results.assessment_id" in policy
        assert "related_assessment.organization_id = assessment_results.organization_id" in policy
        assert "related_assessment.student_id = assessment_results.student_id" in policy
        assert "related_student.id = assessment_results.student_id" in policy
        assert "related_student.organization_id = assessment_results.organization_id" in policy


def test_relationship_policies_never_use_shadowable_outer_column_references():
    sql = FK_MIGRATION.read_text()

    # In a correlated subquery, these unqualified names can bind to the inner
    # table and reduce an intended cross-tenant comparison to a tautology.
    forbidden_fragments = (
        "related_school.id = school_id",
        "related_school.organization_id = organization_id",
        "related_assessment.id = assessment_id",
        "related_assessment.organization_id = organization_id",
        "related_assessment.student_id = student_id",
        "related_student.id = student_id",
        "related_student.organization_id = organization_id",
        "parent_plan.id = intervention_plan_id",
        "assignee.id = assigned_to",
    )
    for fragment in forbidden_fragments:
        assert fragment not in sql
