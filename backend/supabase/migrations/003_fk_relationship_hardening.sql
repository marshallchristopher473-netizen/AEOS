-- P0 follow-up: constrain every tenant-owned foreign-key relationship to the
-- acting organization, and add the assessment_results resource.
--
-- Forward-only: this migration does not edit 001_initial_schema.sql or
-- 002_tenant_rls.sql. It redefines a subset of 002's policies (via
-- DROP POLICY + CREATE POLICY) to add the missing relationship checks below,
-- and adds one new table with its own RLS from scratch.
--
-- Gaps closed here (each policy previously verified only that a row belonged
-- to the acting organization, not that a referenced row on the same row
-- belonged to that same organization):
--   * students.school_id            -> schools.organization_id
--   * ai_recommendations.assessment_id -> assessments.organization_id
--   * intervention_plans.assessment_id (optional) -> assessments.organization_id
--     and assessments.student_id must match intervention_plans.student_id
--   * intervention_actions.assigned_to -> users.organization_id (of the parent plan)
--   * progress_events.student_id    -> students.organization_id
--   * new: assessment_results.assessment_id / .student_id -> assessments row
--     that itself belongs to the org and to that student

-- ---------------------------------------------------------------------------
-- Student -> School
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS students_insert ON public.students;
CREATE POLICY students_insert
ON public.students FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND (
        school_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.schools AS related_school
            WHERE related_school.id = students.school_id
              AND related_school.organization_id = students.organization_id
        )
    )
);

DROP POLICY IF EXISTS students_update ON public.students;
CREATE POLICY students_update
ON public.students FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND (
        school_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.schools AS related_school
            WHERE related_school.id = students.school_id
              AND related_school.organization_id = students.organization_id
        )
    )
);

-- ---------------------------------------------------------------------------
-- Recommendation (ai_recommendations) -> Assessment
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS ai_recommendations_insert ON public.ai_recommendations;
CREATE POLICY ai_recommendations_insert
ON public.ai_recommendations FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.assessments AS related_assessment
        JOIN public.students AS related_student
          ON related_student.id = related_assessment.student_id
        WHERE related_assessment.id = ai_recommendations.assessment_id
          AND related_assessment.organization_id = ai_recommendations.organization_id
          AND related_student.organization_id = ai_recommendations.organization_id
    )
);

DROP POLICY IF EXISTS ai_recommendations_update ON public.ai_recommendations;
CREATE POLICY ai_recommendations_update
ON public.ai_recommendations FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.assessments AS related_assessment
        JOIN public.students AS related_student
          ON related_student.id = related_assessment.student_id
        WHERE related_assessment.id = ai_recommendations.assessment_id
          AND related_assessment.organization_id = ai_recommendations.organization_id
          AND related_student.organization_id = ai_recommendations.organization_id
    )
);

-- ---------------------------------------------------------------------------
-- Intervention Plan -> Student and optional Assessment
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS intervention_plans_insert ON public.intervention_plans;
CREATE POLICY intervention_plans_insert
ON public.intervention_plans FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = intervention_plans.student_id
          AND related_student.organization_id = intervention_plans.organization_id
    )
    AND (
        assessment_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.assessments AS related_assessment
            WHERE related_assessment.id = intervention_plans.assessment_id
              AND related_assessment.organization_id = intervention_plans.organization_id
              AND related_assessment.student_id = intervention_plans.student_id
        )
    )
);

DROP POLICY IF EXISTS intervention_plans_update ON public.intervention_plans;
CREATE POLICY intervention_plans_update
ON public.intervention_plans FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = intervention_plans.student_id
          AND related_student.organization_id = intervention_plans.organization_id
    )
    AND (
        assessment_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.assessments AS related_assessment
            WHERE related_assessment.id = intervention_plans.assessment_id
              AND related_assessment.organization_id = intervention_plans.organization_id
              AND related_assessment.student_id = intervention_plans.student_id
        )
    )
);

-- ---------------------------------------------------------------------------
-- Intervention Action -> Plan and Assigned User
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS intervention_actions_insert ON public.intervention_actions;
CREATE POLICY intervention_actions_insert
ON public.intervention_actions FOR INSERT TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_actions.intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
          AND (
              intervention_actions.assigned_to IS NULL
              OR EXISTS (
                  SELECT 1 FROM public.users AS assignee
                  WHERE assignee.id = intervention_actions.assigned_to
                    AND assignee.organization_id = parent_plan.organization_id
              )
          )
    )
);

DROP POLICY IF EXISTS intervention_actions_update ON public.intervention_actions;
CREATE POLICY intervention_actions_update
ON public.intervention_actions FOR UPDATE TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_actions.intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.intervention_plans AS parent_plan
        WHERE parent_plan.id = intervention_actions.intervention_plan_id
          AND public.aeos_can_write_org(parent_plan.organization_id)
          AND (
              intervention_actions.assigned_to IS NULL
              OR EXISTS (
                  SELECT 1 FROM public.users AS assignee
                  WHERE assignee.id = intervention_actions.assigned_to
                    AND assignee.organization_id = parent_plan.organization_id
              )
          )
    )
);

-- ---------------------------------------------------------------------------
-- Progress Event -> Student
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS progress_events_insert ON public.progress_events;
CREATE POLICY progress_events_insert
ON public.progress_events FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND actor_id = ANY(public.aeos_current_user_ids())
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = progress_events.student_id
          AND related_student.organization_id = progress_events.organization_id
    )
);

-- ---------------------------------------------------------------------------
-- New resource: assessment_results, scoped to Assessment and Student jointly
-- ---------------------------------------------------------------------------
CREATE TABLE public.assessment_results (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES public.assessments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    score NUMERIC(6,2),
    max_score NUMERIC(6,2),
    summary TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER assessment_results_set_updated_at
BEFORE UPDATE ON public.assessment_results
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.assessment_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessment_results FORCE ROW LEVEL SECURITY;

CREATE POLICY assessment_results_select
ON public.assessment_results FOR SELECT TO authenticated
USING (public.aeos_has_org_access(organization_id));

CREATE POLICY assessment_results_insert
ON public.assessment_results FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
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

CREATE POLICY assessment_results_update
ON public.assessment_results FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(organization_id))
WITH CHECK (
    public.aeos_can_write_org(organization_id)
    AND created_by = ANY(public.aeos_current_user_ids())
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

CREATE POLICY assessment_results_delete
ON public.assessment_results FOR DELETE TO authenticated
USING (public.aeos_can_write_org(organization_id));
