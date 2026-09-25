-- P0 follow-up: constrain every tenant-owned foreign-key relationship to the
-- acting organization, and add the assessment_results resource.
--
-- Forward-only: this migration does not edit 001_initial_schema.sql or
-- 002_tenant_rls.sql. It redefines a subset of 002's policies (via
-- DROP POLICY + CREATE POLICY) to add the missing relationship checks below,
-- and adds one new table with its own RLS from scratch.
--
-- Every column reference in every policy body below is explicitly qualified
-- with its owning table (or alias), including references to the policy's
-- own target table, even where no ambiguity exists today. This is not
-- cosmetic: in a correlated EXISTS/JOIN subquery, an unqualified column name
-- resolves to the *innermost* table that has a column of that name — and
-- several related tables here (schools, assessments, students, users) also
-- have an `organization_id` column. An unqualified `organization_id` inside
-- such a subquery therefore does not mean "the outer row's organization_id";
-- it silently binds to the inner table's own `organization_id`, collapsing
-- an intended cross-tenant comparison into a self-referential tautology
-- (e.g. `related_school.organization_id = organization_id` really means
-- `related_school.organization_id = related_school.organization_id`, which
-- is always true). Qualifying every reference, including ones outside a
-- subquery today, means a future edit that adds another correlated table
-- cannot silently reintroduce this bug class.
--
-- Relationship gaps closed here (each policy previously verified only that
-- a row belonged to the acting organization, not that a *referenced* row on
-- that same row belonged to that same organization, and in some cases the
-- relationship check was altogether absent):
--   * students.school_id               -> schools.organization_id
--   * assessments.student_id           -> students.organization_id
--     (redefines 002's assessments_insert/update, which had this exact
--     unqualified-reference bug from the start)
--   * ai_recommendations.assessment_id -> assessments.organization_id,
--     and assessments.student_id's own organization must match too
--   * intervention_plans.assessment_id (optional) -> assessments row that
--     also belongs to the same organization and the same student
--   * intervention_actions.assigned_to -> users.organization_id (of the
--     parent plan)
--   * progress_events.student_id       -> students.organization_id
--   * new: assessment_results.assessment_id / .student_id -> an assessments
--     row that itself belongs to the org and to that student
--
-- Actor-identity hardening: every actor foreign key is bound to both the
-- authenticated subject and the row's organization. A trigger makes
-- organization_id and created_by immutable without recursively querying a
-- protected table from inside its own RLS policy.

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
        WHERE membership.id = target_user_id
          AND membership.organization_id = target_organization_id
          AND membership.auth_user_id = auth.uid()::text
          AND membership.status = 'active'
    );
$$;

REVOKE ALL ON FUNCTION public.aeos_is_current_actor_for_org(UUID, UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.aeos_is_current_actor_for_org(UUID, UUID) TO authenticated;

CREATE OR REPLACE FUNCTION public.aeos_preserve_row_identity()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
    IF NEW.organization_id IS DISTINCT FROM OLD.organization_id
       OR NEW.created_by IS DISTINCT FROM OLD.created_by THEN
        RAISE EXCEPTION 'organization_id and created_by are immutable'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER students_preserve_row_identity
BEFORE UPDATE ON public.students
FOR EACH ROW EXECUTE FUNCTION public.aeos_preserve_row_identity();

CREATE TRIGGER assessments_preserve_row_identity
BEFORE UPDATE ON public.assessments
FOR EACH ROW EXECUTE FUNCTION public.aeos_preserve_row_identity();

CREATE TRIGGER ai_recommendations_preserve_row_identity
BEFORE UPDATE ON public.ai_recommendations
FOR EACH ROW EXECUTE FUNCTION public.aeos_preserve_row_identity();

CREATE TRIGGER intervention_plans_preserve_row_identity
BEFORE UPDATE ON public.intervention_plans
FOR EACH ROW EXECUTE FUNCTION public.aeos_preserve_row_identity();

-- ---------------------------------------------------------------------------
-- Student -> School
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS students_insert ON public.students;
CREATE POLICY students_insert
ON public.students FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(students.organization_id)
    AND public.aeos_is_current_actor_for_org(
        students.created_by,
        students.organization_id
    )
    AND (
        students.school_id IS NULL
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
USING (public.aeos_can_write_org(students.organization_id))
WITH CHECK (
    public.aeos_can_write_org(students.organization_id)
    AND public.aeos_is_current_actor_for_org(
        students.created_by,
        students.organization_id
    )
    AND (
        students.school_id IS NULL
        OR EXISTS (
            SELECT 1 FROM public.schools AS related_school
            WHERE related_school.id = students.school_id
              AND related_school.organization_id = students.organization_id
        )
    )
);

-- ---------------------------------------------------------------------------
-- Assessment -> Student
-- (redefines 002's assessments_insert/update: the original policy compared
-- `related_student.organization_id = organization_id` inside a correlated
-- subquery against the `students` table, which itself has an
-- `organization_id` column — the unqualified reference bound to the inner
-- table, not the outer `assessments` row, making the check a tautology.)
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS assessments_insert ON public.assessments;
CREATE POLICY assessments_insert
ON public.assessments FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(assessments.organization_id)
    AND public.aeos_is_current_actor_for_org(
        assessments.created_by,
        assessments.organization_id
    )
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = assessments.student_id
          AND related_student.organization_id = assessments.organization_id
    )
);

DROP POLICY IF EXISTS assessments_update ON public.assessments;
CREATE POLICY assessments_update
ON public.assessments FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(assessments.organization_id))
WITH CHECK (
    public.aeos_can_write_org(assessments.organization_id)
    AND public.aeos_is_current_actor_for_org(
        assessments.created_by,
        assessments.organization_id
    )
    AND EXISTS (
        SELECT 1 FROM public.students AS related_student
        WHERE related_student.id = assessments.student_id
          AND related_student.organization_id = assessments.organization_id
    )
);

-- ---------------------------------------------------------------------------
-- Recommendation (ai_recommendations) -> Assessment (and its Student)
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS ai_recommendations_insert ON public.ai_recommendations;
CREATE POLICY ai_recommendations_insert
ON public.ai_recommendations FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(ai_recommendations.organization_id)
    AND public.aeos_is_current_actor_for_org(
        ai_recommendations.created_by,
        ai_recommendations.organization_id
    )
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
USING (public.aeos_can_write_org(ai_recommendations.organization_id))
WITH CHECK (
    public.aeos_can_write_org(ai_recommendations.organization_id)
    AND public.aeos_is_current_actor_for_org(
        ai_recommendations.created_by,
        ai_recommendations.organization_id
    )
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
    public.aeos_can_write_org(intervention_plans.organization_id)
    AND public.aeos_is_current_actor_for_org(
        intervention_plans.created_by,
        intervention_plans.organization_id
    )
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

DROP POLICY IF EXISTS intervention_plans_update ON public.intervention_plans;
CREATE POLICY intervention_plans_update
ON public.intervention_plans FOR UPDATE TO authenticated
USING (public.aeos_can_write_org(intervention_plans.organization_id))
WITH CHECK (
    public.aeos_can_write_org(intervention_plans.organization_id)
    AND public.aeos_is_current_actor_for_org(
        intervention_plans.created_by,
        intervention_plans.organization_id
    )
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
-- (append-only: no UPDATE policy exists on this table, matching its
-- event-log semantics — nothing to preserve on update.)
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS progress_events_insert ON public.progress_events;
CREATE POLICY progress_events_insert
ON public.progress_events FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(progress_events.organization_id)
    AND public.aeos_is_current_actor_for_org(
        progress_events.actor_id,
        progress_events.organization_id
    )
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

CREATE TRIGGER assessment_results_preserve_row_identity
BEFORE UPDATE ON public.assessment_results
FOR EACH ROW EXECUTE FUNCTION public.aeos_preserve_row_identity();

ALTER TABLE public.assessment_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessment_results FORCE ROW LEVEL SECURITY;

CREATE POLICY assessment_results_select
ON public.assessment_results FOR SELECT TO authenticated
USING (public.aeos_has_org_access(assessment_results.organization_id));

CREATE POLICY assessment_results_insert
ON public.assessment_results FOR INSERT TO authenticated
WITH CHECK (
    public.aeos_can_write_org(assessment_results.organization_id)
    AND public.aeos_is_current_actor_for_org(
        assessment_results.created_by,
        assessment_results.organization_id
    )
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
USING (public.aeos_can_write_org(assessment_results.organization_id))
WITH CHECK (
    public.aeos_can_write_org(assessment_results.organization_id)
    AND public.aeos_is_current_actor_for_org(
        assessment_results.created_by,
        assessment_results.organization_id
    )
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
USING (public.aeos_can_write_org(assessment_results.organization_id));
