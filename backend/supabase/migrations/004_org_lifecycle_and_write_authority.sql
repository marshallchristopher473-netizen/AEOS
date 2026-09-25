-- P0 follow-up: make organization lifecycle a real containment control, and
-- make write authority internally consistent.
--
-- Forward-only: this migration edits none of 001, 002 or 003. It redefines a
-- subset of their functions and policies via CREATE OR REPLACE / DROP POLICY +
-- CREATE POLICY. Every column reference remains explicitly table-qualified for
-- the reason recorded at the top of 003.
--
-- ---------------------------------------------------------------------------
-- M1 — organization suspension provided no containment.
-- ---------------------------------------------------------------------------
-- 001 models `organizations.status` as ENUM ('active','suspended'), but no
-- policy and no application code ever consulted it. A suspended district's
-- members retained full read and write access, so suspension was inert for
-- offboarding, non-payment and breach containment alike.
--
-- Every `aeos_*` helper below now additionally requires the membership's
-- organization to be active. Because all tenant policies are expressed through
-- these helpers, adding the condition here closes the gap for every table at
-- once rather than repeating it across ~30 policies.
--
-- ---------------------------------------------------------------------------
-- M2 — the destructive operation was the less restricted one.
-- ---------------------------------------------------------------------------
-- 003 bound UPDATE to the row's creator (`aeos_is_current_actor_for_org(
-- <table>.created_by, ...)` in WITH CHECK) while DELETE required only
-- `aeos_can_write_org(...)`. A teacher therefore could not correct a
-- colleague's student record but could delete it outright. That is both
-- unsafe and backwards, and it is reachable by any authenticated Supabase
-- client directly, independently of which routes FastAPI exposes.
--
-- Resolved in two directions:
--
--   * UPDATE is opened to any active teacher/admin in the owning organization.
--     This does NOT weaken ownership: `organization_id` and `created_by`
--     remain immutable via the `aeos_preserve_row_identity` trigger installed
--     by 003, and every foreign-key relationship check is retained verbatim.
--     Dropping the creator binding from WITH CHECK is therefore safe — the
--     trigger already makes those columns unwritable on UPDATE.
--
--   * DELETE is narrowed to organization admins for the MVP. Destruction is
--     the least reversible operation and warrants the highest bar; teachers
--     retain full create and update authority within their tenant.
--
-- `schools_delete` already required admin in 002 and is left unchanged.
-- `intervention_actions` carries no `created_by` column, so only its DELETE
-- authority changes. `progress_events` is append-only and has no UPDATE or
-- DELETE policy; nothing to change.

-- ---------------------------------------------------------------------------
-- Helpers: require an ACTIVE organization, not merely an active membership.
-- ---------------------------------------------------------------------------

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
        JOIN public.organizations AS tenant
          ON tenant.id = membership.organization_id
        WHERE membership.auth_user_id = auth.uid()::text
          AND membership.organization_id = target_organization_id
          AND membership.status = 'active'
          AND tenant.status = 'active'
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
        JOIN public.organizations AS tenant
          ON tenant.id = membership.organization_id
        WHERE membership.auth_user_id = auth.uid()::text
          AND membership.organization_id = target_organization_id
          AND membership.status = 'active'
          AND tenant.status = 'active'
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
        JOIN public.organizations AS tenant
          ON tenant.id = membership.organization_id
        WHERE membership.auth_user_id = auth.uid()::text
          AND membership.organization_id = target_organization_id
          AND membership.status = 'active'
          AND tenant.status = 'active'
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
    JOIN public.organizations AS tenant
      ON tenant.id = membership.organization_id
    WHERE membership.auth_user_id = auth.uid()::text
      AND membership.status = 'active'
      AND tenant.status = 'active';
$$;

CREATE OR REPLACE FUNCTION public.aeos_is_current_actor_for_org(
    target_user_id UUID,
    target_organization_id UUID
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, auth, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.users AS membership
        JOIN public.organizations AS tenant
          ON tenant.id = membership.organization_id
        WHERE membership.id = target_user_id
          AND membership.organization_id = target_organization_id
          AND membership.auth_user_id = auth.uid()::text
          AND membership.status = 'active'
          AND tenant.status = 'active'
    );
$$;

-- ---------------------------------------------------------------------------
-- UPDATE: same-tenant teacher/admin. Ownership columns stay immutable via the
-- aeos_preserve_row_identity trigger (003); relationship checks are retained.
-- ---------------------------------------------------------------------------

DROP POLICY IF EXISTS students_update ON public.students;
CREATE POLICY students_update
ON public.students FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(students.organization_id))
WITH CHECK (
    public.aeos_can_write_org(students.organization_id)
    AND (
        students.school_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.schools AS related_school
            WHERE related_school.id = students.school_id
              AND related_school.organization_id = students.organization_id
        )
    )
);

DROP POLICY IF EXISTS assessments_update ON public.assessments;
CREATE POLICY assessments_update
ON public.assessments FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(assessments.organization_id))
WITH CHECK (
    public.aeos_can_write_org(assessments.organization_id)
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = assessments.student_id
          AND related_student.organization_id = assessments.organization_id
    )
);

DROP POLICY IF EXISTS ai_recommendations_update ON public.ai_recommendations;
CREATE POLICY ai_recommendations_update
ON public.ai_recommendations FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(ai_recommendations.organization_id))
WITH CHECK (
    public.aeos_can_write_org(ai_recommendations.organization_id)
    AND EXISTS (
        SELECT 1 FROM public.assessments AS related_assessment
        JOIN public.students AS related_student
          ON related_student.id = related_assessment.student_id
        WHERE related_assessment.id = ai_recommendations.assessment_id
          AND related_assessment.organization_id = ai_recommendations.organization_id
          AND related_student.organization_id = ai_recommendations.organization_id
    )
);

DROP POLICY IF EXISTS intervention_plans_update ON public.intervention_plans;
CREATE POLICY intervention_plans_update
ON public.intervention_plans FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(intervention_plans.organization_id))
WITH CHECK (
    public.aeos_can_write_org(intervention_plans.organization_id)
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = intervention_plans.student_id
          AND related_student.organization_id = intervention_plans.organization_id
    )
    AND (
        intervention_plans.assessment_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.assessments AS related_assessment
            WHERE related_assessment.id = intervention_plans.assessment_id
              AND related_assessment.organization_id = intervention_plans.organization_id
              AND related_assessment.student_id = intervention_plans.student_id
        )
    )
);

DROP POLICY IF EXISTS assessment_results_update ON public.assessment_results;
CREATE POLICY assessment_results_update
ON public.assessment_results FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(assessment_results.organization_id))
WITH CHECK (
    public.aeos_can_write_org(assessment_results.organization_id)
    AND EXISTS (
        SELECT 1 FROM public.assessments AS related_assessment
        WHERE related_assessment.id = assessment_results.assessment_id
          AND related_assessment.organization_id = assessment_results.organization_id
          AND related_assessment.student_id = assessment_results.student_id
    )
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = assessment_results.student_id
          AND related_student.organization_id = assessment_results.organization_id
    )
);

-- ---------------------------------------------------------------------------
-- DELETE: organization admins only, for the MVP.
-- ---------------------------------------------------------------------------

DROP POLICY IF EXISTS students_delete ON public.students;
CREATE POLICY students_delete
ON public.students FOR DELETE TO authenticated
USING (public.aeos_is_org_admin(students.organization_id));

DROP POLICY IF EXISTS assessments_delete ON public.assessments;
CREATE POLICY assessments_delete
ON public.assessments FOR DELETE TO authenticated
USING (public.aeos_is_org_admin(assessments.organization_id));

DROP POLICY IF EXISTS ai_recommendations_delete ON public.ai_recommendations;
CREATE POLICY ai_recommendations_delete
ON public.ai_recommendations FOR DELETE TO authenticated
USING (public.aeos_is_org_admin(ai_recommendations.organization_id));

DROP POLICY IF EXISTS intervention_plans_delete ON public.intervention_plans;
CREATE POLICY intervention_plans_delete
ON public.intervention_plans FOR DELETE TO authenticated
USING (public.aeos_is_org_admin(intervention_plans.organization_id));

DROP POLICY IF EXISTS assessment_results_delete ON public.assessment_results;
CREATE POLICY assessment_results_delete
ON public.assessment_results FOR DELETE TO authenticated
USING (public.aeos_is_org_admin(assessment_results.organization_id));

DROP POLICY IF EXISTS intervention_actions_delete ON public.intervention_actions;
CREATE POLICY intervention_actions_delete
ON public.intervention_actions FOR DELETE TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_actions.intervention_plan_id
          AND public.aeos_is_org_admin(parent_plan.organization_id)
    )
);

COMMENT ON FUNCTION public.aeos_has_org_access(UUID)
IS 'True only for an active membership in an ACTIVE organization, derived from auth.uid().';
COMMENT ON FUNCTION public.aeos_can_write_org(UUID)
IS 'True only for an active teacher/admin membership in an ACTIVE organization.';
COMMENT ON FUNCTION public.aeos_is_org_admin(UUID)
IS 'True only for an active admin membership in an ACTIVE organization. Gates DELETE.';
