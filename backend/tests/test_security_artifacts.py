from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_DIR.parent
RLS_MIGRATION = BACKEND_DIR / "supabase" / "migrations" / "002_tenant_rls.sql"


TENANT_TABLES = (
    "organizations",
    "schools",
    "users",
    "students",
    "assessments",
    "ai_recommendations",
    "intervention_plans",
    "intervention_actions",
    "progress_events",
    "audit_logs",
)


def test_forward_only_rls_migration_enables_and_forces_rls():
    sql = RLS_MIGRATION.read_text()

    for table in TENANT_TABLES:
        assert f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;" in sql
        assert f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY;" in sql


def test_rls_context_is_derived_from_authenticated_subject():
    sql = RLS_MIGRATION.read_text()

    assert "membership.auth_user_id = auth.uid()::text" in sql
    assert "membership.status = 'active'" in sql
    assert "aeos_has_org_access" in sql
    assert "aeos_can_write_org" in sql
    assert "TO authenticated" in sql


def test_rls_policies_cover_active_tenant_entities_and_operations():
    sql = RLS_MIGRATION.read_text()

    required_policies = (
        "students_select",
        "students_insert",
        "students_update",
        "students_delete",
        "assessments_select",
        "assessments_insert",
        "assessments_update",
        "assessments_delete",
        "intervention_plans_select",
        "intervention_plans_insert",
        "intervention_plans_update",
        "intervention_plans_delete",
    )
    for policy in required_policies:
        assert f"CREATE POLICY {policy}" in sql


def test_frontend_assessment_form_does_not_submit_authority_fields():
    form = (
        REPOSITORY_ROOT / "frontend" / "src" / "app" / "assessments" / "new" / "page.tsx"
    ).read_text()

    assert "organization_id" not in form
    assert "created_by" not in form


def test_service_role_key_is_not_referenced_by_frontend_source():
    frontend_source = REPOSITORY_ROOT / "frontend" / "src"

    for path in frontend_source.rglob("*"):
        if path.is_file():
            assert "SUPABASE_SERVICE_ROLE_KEY" not in path.read_text()
