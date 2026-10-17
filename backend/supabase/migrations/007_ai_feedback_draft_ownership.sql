-- AI feedback drafting: a draft belongs to the teacher who requested it.
--
-- Forward-only: this migration edits none of 001-006. It replaces the three
-- SELECT policies 006 created and the body of one 006 trigger function.
--
-- ---------------------------------------------------------------------------
-- Why
-- ---------------------------------------------------------------------------
-- 006 let every active member of the organization read every request, draft
-- and decision, and let any active teacher or admin record the decision on
-- any draft. A request row holds a student's response, and the decision is
-- the requesting teacher's professional judgement. Inside one organization:
--
--   * Teacher B could read Teacher A's student responses and drafts, directly
--     through the Supabase data API with an ordinary session token.
--   * Teacher B, or an admin, could accept, revise or reject Teacher A's
--     draft, and that decision became the current one.
--
-- The rule from 007 on:
--
--   read    the requesting teacher, or an admin of the organization
--   decide  the requesting teacher only
--
-- Admins keep read access for oversight. They do not decide on a teacher's
-- behalf. Support staff and peer teachers see nothing they did not request.
-- The FastAPI service applies the same rule first (app/services/ai_feedback/
-- service.py); these controls hold even if it does not.
--
-- Unchanged: no client INSERT, UPDATE or DELETE policy; append-only triggers;
-- audit triggers; the reservation function.

-- ---------------------------------------------------------------------------
-- Read helper. SECURITY DEFINER so the drafts and decisions policies can check
-- the parent request without depending on the requests policy, matching how
-- 002-004 bind actors through the aeos_* helpers.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.aeos_can_read_ai_feedback_request(
    target_request_id UUID,
    target_organization_id UUID
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, auth, pg_temp
AS $$
    SELECT public.aeos_is_org_admin(target_organization_id)
        OR EXISTS (
            SELECT 1
            FROM public.ai_feedback_requests AS request
            WHERE request.id = target_request_id
              AND request.organization_id = target_organization_id
              AND public.aeos_is_current_actor_for_org(request.created_by, request.organization_id)
        );
$$;

REVOKE ALL ON FUNCTION public.aeos_can_read_ai_feedback_request(UUID, UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.aeos_can_read_ai_feedback_request(UUID, UUID) TO authenticated;

-- ---------------------------------------------------------------------------
-- RLS: the requester and org admins may read.
-- ---------------------------------------------------------------------------

DROP POLICY IF EXISTS ai_feedback_requests_select ON public.ai_feedback_requests;
CREATE POLICY ai_feedback_requests_select
ON public.ai_feedback_requests FOR SELECT TO authenticated
USING (public.aeos_can_read_ai_feedback_request(ai_feedback_requests.id, ai_feedback_requests.organization_id));

DROP POLICY IF EXISTS ai_feedback_drafts_select ON public.ai_feedback_drafts;
CREATE POLICY ai_feedback_drafts_select
ON public.ai_feedback_drafts FOR SELECT TO authenticated
USING (public.aeos_can_read_ai_feedback_request(ai_feedback_drafts.request_id, ai_feedback_drafts.organization_id));

DROP POLICY IF EXISTS ai_feedback_decisions_select ON public.ai_feedback_decisions;
CREATE POLICY ai_feedback_decisions_select
ON public.ai_feedback_decisions FOR SELECT TO authenticated
USING (
    EXISTS (
        SELECT 1
        FROM public.ai_feedback_drafts AS draft
        WHERE draft.id = ai_feedback_decisions.draft_id
          AND draft.organization_id = ai_feedback_decisions.organization_id
          AND public.aeos_can_read_ai_feedback_request(draft.request_id, draft.organization_id)
    )
);

-- ---------------------------------------------------------------------------
-- Integrity: only the requesting teacher may decide. Same checks as 006, plus
-- decided_by = the request's created_by. The service role writes these rows,
-- so this trigger, not RLS, is the database control for decisions.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.aeos_ai_feedback_decision_integrity()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    draft_status ai_feedback_draft_status;
    requester_id UUID;
BEGIN
    SELECT draft.status, request.created_by INTO draft_status, requester_id
    FROM public.ai_feedback_drafts AS draft
    JOIN public.ai_feedback_requests AS request
      ON request.id = draft.request_id
     AND request.organization_id = draft.organization_id
    WHERE draft.id = NEW.draft_id
      AND draft.organization_id = NEW.organization_id;

    IF draft_status IS NULL OR draft_status NOT IN ('ready', 'abstained') THEN
        RAISE EXCEPTION 'ai_feedback_decisions: draft has no reviewable output'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.decision = 'accepted' AND draft_status <> 'ready' THEN
        RAISE EXCEPTION 'ai_feedback_decisions: an abstained draft cannot be accepted'
            USING ERRCODE = '23514';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM public.users AS reviewer
        JOIN public.organizations AS tenant ON tenant.id = reviewer.organization_id
        WHERE reviewer.id = NEW.decided_by
          AND reviewer.organization_id = NEW.organization_id
          AND reviewer.status = 'active'
          AND reviewer.role IN ('teacher', 'admin')
          AND tenant.status = 'active'
    ) THEN
        RAISE EXCEPTION 'ai_feedback_decisions: reviewer is not an active teacher or admin of the organization'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.decided_by IS DISTINCT FROM requester_id THEN
        RAISE EXCEPTION 'ai_feedback_decisions: only the teacher who requested the draft may decide it'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.aeos_ai_feedback_decision_integrity() FROM PUBLIC;
