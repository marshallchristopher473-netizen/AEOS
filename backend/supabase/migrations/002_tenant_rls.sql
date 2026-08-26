-- P0 tenant isolation for direct Supabase/PostgREST access.
--
-- The FastAPI application currently uses the server-only service-role client,
-- which deliberately bypasses RLS and therefore applies matching tenant
-- filters in app/services/tenant_scope.py. Authenticated browser/database
-- clients are constrained here. This migration is forward-only; it does not
-- modify 001_initial_schema.sql.

CREATE OR REPLACE FUNCTION public.aeos_has_org_access(target_organization_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, auth, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.users AS membership
        WHERE membership.auth_user_id = auth.uid()::text
          AND membership.organization_id = target_organization_id
          AND membership.status = 'active'
    );
$$;

CREATE OR REPLACE FUNCTION public.aeos_can_write_org(target_organization_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, auth, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.users AS membership
        WHERE membership.auth_user_id = auth.uid()::text
          AND membership.organization_id = target_organization_id
          AND membership.status = 'active'
          AND membership.role IN ('teacher', 'admin')
    );
$$;

CREATE OR REPLACE FUNCTION public.aeos_is_org_admin(target_organization_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, auth, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.users AS membership
        WHERE membership.auth_user_id = auth.uid()::text
          AND membership.organization_id = target_organization_id
          AND membership.status = 'active'
          AND membership.role = 'admin'
    );
$$;

CREATE OR REPLACE FUNCTION public.aeos_current_user_ids()
RETURNS UUID[]
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, auth, pg_temp
AS $$
    SELECT COALESCE(array_agg(membership.id), ARRAY[]::UUID[])
    FROM public.users AS membership
    WHERE membership.auth_user_id = auth.uid()::text
      AND membership.status = 'active';
$$;

REVOKE ALL ON FUNCTION public.aeos_has_org_access(UUID) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_can_write_org(UUID) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_is_org_admin(UUID) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_current_user_ids() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.aeos_has_org_access(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.aeos_can_write_org(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.aeos_is_org_admin(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.aeos_current_user_ids() TO authenticated;

ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schools ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intervention_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intervention_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.progress_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.organizations FORCE ROW LEVEL SECURITY;
ALTER TABLE public.schools FORCE ROW LEVEL SECURITY;
ALTER TABLE public.users FORCE ROW LEVEL SECURITY;
ALTER TABLE public.students FORCE ROW LEVEL SECURITY;
ALTER TABLE public.assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE public.ai_recommendations FORCE ROW LEVEL SECURITY;
ALTER TABLE public.intervention_plans FORCE ROW LEVEL SECURITY;
ALTER TABLE public.intervention_actions FORCE ROW LEVEL SECURITY;
ALTER TABLE public.progress_events FORCE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs FORCE ROW LEVEL SECURITY;

CREATE POLICY organizations_select
ON public.organizations FOR SELECT TO authenticated
USING (public.aeos_has_org_access(id));

CREATE POLICY schools_select
ON public.schools FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY schools_insert
ON public.schools FOR INSERT TO authenticated
WITH CHECK (public.aeos_is_org_admin(organization_id));

CREATE POLICY schools_update
ON public.schools FOR UPDATE TO authenticated
USING (public.aeos_is_org_admin(organization_id))
WITH CHECK (public.aeos_is_org_admin(organization_id));

CREATE POLICY schools_delete
ON public.schools FOR DELETE TO authenticated
USING (public.aeos_is_org_admin(organization_id));

CREATE POLICY users_select
ON public.users FOR SELECT TO authenticated
USING (
    auth_user_id = auth.uid()::text
    OR public.aeos_is_org_admin(organization_id)
);

CREATE POLICY students_select
ON public.students FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY students_insert
ON public.students FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
);

CREATE POLICY students_update
ON public.students FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
);

CREATE POLICY students_delete
ON public.students FOR DELETE TO authenticated
USING (public.aeos_can_write_org(organization_id));

CREATE POLICY assessments_select
ON public.assessments FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY assessments_insert
ON public.assessments FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = student_id
          AND related_student.organization_id = organization_id
    )
);

CREATE POLICY assessments_update
ON public.assessments FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = student_id
          AND related_student.organization_id = organization_id
    )
);

CREATE POLICY assessments_delete
ON public.assessments FOR DELETE TO authenticated
USING (public.aeos_can_write_org(organization_id));

CREATE POLICY ai_recommendations_select
ON public.ai_recommendations FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY ai_recommendations_insert
ON public.ai_recommendations FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
);

CREATE POLICY ai_recommendations_update
ON public.ai_recommendations FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (public.aeos_can_write_org(organization_id));

CREATE POLICY ai_recommendations_delete
ON public.ai_recommendations FOR DELETE TO authenticated
USING (public.aeos_can_write_org(organization_id));

CREATE POLICY intervention_plans_select
ON public.intervention_plans FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY intervention_plans_insert
ON public.intervention_plans FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = student_id
          AND related_student.organization_id = organization_id
    )
);

CREATE POLICY intervention_plans_update
ON public.intervention_plans FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
);

CREATE POLICY intervention_plans_delete
ON public.intervention_plans FOR DELETE TO authenticated
USING (public.aeos_can_write_org(organization_id));

CREATE POLICY intervention_actions_select
ON public.intervention_actions FOR SELECT TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_plan_id
          AND public.aeos_has_org_access(parent_plan.organization_id)
    )
);

CREATE POLICY intervention_actions_insert
ON public.intervention_actions FOR INSERT TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
    )
);

CREATE POLICY intervention_actions_update
ON public.intervention_actions FOR UPDATE TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
    )
);

CREATE POLICY intervention_actions_delete
ON public.intervention_actions FOR DELETE TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
    )
);

CREATE POLICY progress_events_select
ON public.progress_events FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY progress_events_insert
ON public.progress_events FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND actor_id = ANY(public.aeos_current_user_ids())
);

CREATE POLICY audit_logs_select
ON public.audit_logs FOR SELECT TO authenticated
USING (public.aeos_is_org_admin(organization_id));

COMMENT ON FUNCTION public.aeos_has_org_access(UUID)
IS 'True only for an active AEOS membership derived from auth.uid().';
COMMENT ON FUNCTION public.aeos_can_write_org(UUID)
IS 'True only for an active teacher/admin membership derived from auth.uid().';
