from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
FK_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "003_fk_relationship_hardening.sql"
BASE_RLS_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "002_tenant_rls.sql"


def test_fk_migration_is_forward_only():
    # This migration must not edit either prior migration file.
    assert "DROP TABLE" not in FK_MIGRATION.read_text()
    original_002 = BASE_RLS_MIGRATION.read_text()
    assert "ai_recommendations_insert" in original_002  # sanity: unedited file


def test_student_school_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS students_insert ON public.students;" in sql
    assert "DROP POLICY IF EXISTS students_update ON public.students;" in sql
    assert (
        "SELECT 1 FROM public.schools AS related_school\n"
        "            WHERE related_school.id = school_id\n"
        "              AND related_school.organization_id = organization_id"
        in sql
    )


def test_recommendation_assessment_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS ai_recommendations_insert ON public.ai_recommendations;" in sql
    assert (
        "SELECT 1 FROM public.assessments AS related_assessment\n"
        "        WHERE related_assessment.id = assessment_id\n"
        "          AND related_assessment.organization_id = organization_id\n"
        "    )\n"
        ");"
        in sql
    )


def test_intervention_plan_student_and_assessment_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS intervention_plans_insert ON public.intervention_plans;" in sql
    assert "related_assessment.student_id = student_id" in sql


def test_intervention_action_plan_and_assignee_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS intervention_actions_insert ON public.intervention_actions;" in sql
    assert (
        "SELECT 1 FROM public.users AS assignee\n"
        "                  WHERE assignee.id = assigned_to\n"
        "                    AND assignee.organization_id = parent_plan.organization_id"
        in sql
    )


def test_progress_event_student_relationship_is_enforced():
    sql = FK_MIGRATION.read_text()

    assert "DROP POLICY IF EXISTS progress_events_insert ON public.progress_events;" in sql
    assert (
        "SELECT 1 FROM public.students AS related_student\n"
        "        WHERE related_student.id = student_id\n"
        "          AND related_student.organization_id = organization_id\n"
        "    )\n"
        ");"
        in sql
    )


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
    assert "related_assessment.student_id = student_id" in sql
