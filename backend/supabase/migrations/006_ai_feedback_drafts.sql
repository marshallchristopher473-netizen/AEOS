-- AI feedback drafting: request ledger, immutable AI drafts, and append-only
-- teacher decisions.
--
-- Forward-only: this migration edits none of 001-005 and changes no existing
-- table, policy or function.
--
-- ---------------------------------------------------------------------------
-- Why the existing ai_recommendations table is not reused
-- ---------------------------------------------------------------------------
-- 001 created `ai_recommendations` (one free-text column, a `confidence_score`
-- and a generated/reviewed/accepted/rejected status). No service or route
-- writes it. Reusing it would require:
--
--   * recording the teacher's decision by UPDATE-ing the AI row's status, which
--     its 003/004 policies allow any teacher to do. The AI draft and the
--     teacher decision would then share one mutable row, so the AI's original
--     text could be overwritten by, and become indistinguishable from, teacher-
--     approved text. The teacher review slice (assessment_results) is the
--     opposite: every save is a new row and nothing is edited in place.
--   * columns it lacks: criterion-linked structured output, verified evidence
--     spans, review flags, prompt/rubric versions, an idempotency key and token
--     usage. Its `confidence_score` invites accuracy claims nobody has
--     validated.
--
-- The narrow change is therefore three new tables that follow the existing
-- append-only review semantics, with the separation enforced in the database:
--
--   ai_feedback_requests   one row per generation attempt, written BEFORE the
--                          provider is called. It is the idempotency, rate-limit
--                          and budget ledger, and holds the synthetic input.
--   ai_feedback_drafts     the AI outcome for one request (at most one). Never
--                          updated. Failed attempts are recorded here too, so
--                          every provider call is accountable.
--   ai_feedback_decisions  explicit teacher decisions on a draft: accepted,
--                          revised (with the teacher's own text) or rejected.
--                          Append-only; the latest row is the current decision,
--                          exactly as the latest assessment_results row is the
--                          current review.
--
-- Nothing here writes to assessment_results, intervention_plans or any other
-- record. There is no automatic gradebook write.
--
-- ---------------------------------------------------------------------------
-- Write path and RLS
-- ---------------------------------------------------------------------------
-- Only the FastAPI backend writes these tables, through the server-only
-- service-role client. RLS is enabled and forced; authenticated members of the
-- owning organization may SELECT. There is deliberately no INSERT, UPDATE or
-- DELETE policy, so a direct client write is refused by RLS. Table DML grants
-- are left as Supabase grants them so that the refusal comes from RLS (the
-- control under test), consistent with 005 and tests/test_rls_enforcement.py.
--
-- UPDATE is refused for every role, including the service role, by trigger.
-- DELETE is left to the service role for organization offboarding (the
-- ON DELETE CASCADE from organizations) and retention; no client can delete.
--
-- Audit rows are written by AFTER INSERT triggers in the same transaction as
-- the draft or decision. If the audit row cannot be written, the save fails.

CREATE TYPE ai_feedback_draft_status AS ENUM (
    'ready',
    'abstained',
    'rejected_output',
    'provider_error',
    'provider_refused'
);

CREATE TYPE ai_feedback_decision AS ENUM ('accepted', 'revised', 'rejected');

CREATE TABLE public.ai_feedback_requests (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES public.assessments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    request_key UUID NOT NULL,
    input_sha256 TEXT NOT NULL CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
    -- This phase accepts synthetic data only. Real student data needs consent,
    -- a data agreement and the hosted tenant-isolation gate first.
    data_classification TEXT NOT NULL CHECK (data_classification = 'synthetic'),
    response_text TEXT NOT NULL
        CHECK (char_length(response_text) BETWEEN 1 AND 4000),
    source_text TEXT
        CHECK (source_text IS NULL OR char_length(source_text) BETWEEN 1 AND 6000),
    rubric_id TEXT NOT NULL CHECK (char_length(rubric_id) BETWEEN 1 AND 64),
    rubric_version TEXT NOT NULL CHECK (char_length(rubric_version) BETWEEN 1 AND 32),
    rubric_sha256 TEXT NOT NULL CHECK (rubric_sha256 ~ '^[0-9a-f]{64}$'),
    prompt_version TEXT NOT NULL CHECK (char_length(prompt_version) BETWEEN 1 AND 64),
    provider TEXT NOT NULL CHECK (char_length(provider) BETWEEN 1 AND 32),
    model_id TEXT NOT NULL CHECK (char_length(model_id) BETWEEN 1 AND 128),
    reserved_cost_microusd BIGINT NOT NULL CHECK (reserved_cost_microusd > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_feedback_requests_key_unique
        UNIQUE (organization_id, created_by, request_key),
    CONSTRAINT ai_feedback_requests_id_org_unique UNIQUE (id, organization_id)
);

CREATE INDEX ai_feedback_requests_budget_idx
    ON public.ai_feedback_requests (organization_id, created_at);

CREATE TABLE public.ai_feedback_drafts (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    request_id UUID NOT NULL UNIQUE,
    status ai_feedback_draft_status NOT NULL,
    -- Server-validated structured output: criterion-linked feedback whose
    -- evidence spans were located verbatim in the response, or abstentions.
    output JSONB,
    draft_text TEXT CHECK (draft_text IS NULL OR char_length(draft_text) <= 6000),
    review_flags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    error_code TEXT CHECK (error_code IS NULL OR char_length(error_code) <= 64),
    response_model_id TEXT CHECK (response_model_id IS NULL OR char_length(response_model_id) <= 128),
    input_tokens INTEGER CHECK (input_tokens IS NULL OR input_tokens >= 0),
    output_tokens INTEGER CHECK (output_tokens IS NULL OR output_tokens >= 0),
    actual_cost_microusd BIGINT NOT NULL DEFAULT 0 CHECK (actual_cost_microusd >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_feedback_drafts_request_fk
        FOREIGN KEY (request_id, organization_id)
        REFERENCES public.ai_feedback_requests (id, organization_id)
        ON DELETE CASCADE,
    CONSTRAINT ai_feedback_drafts_id_org_unique UNIQUE (id, organization_id),
    CONSTRAINT ai_feedback_drafts_outcome_shape CHECK (
        (status IN ('ready', 'abstained')
            AND output IS NOT NULL AND error_code IS NULL)
        OR
        (status NOT IN ('ready', 'abstained')
            AND output IS NULL AND draft_text IS NULL AND error_code IS NOT NULL)
    )
);

CREATE TABLE public.ai_feedback_decisions (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    draft_id UUID NOT NULL,
    decided_by UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    decision ai_feedback_decision NOT NULL,
    approved_text TEXT,
    review_flags_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    -- Every decision is an explicit teacher action; a row cannot exist without it.
    teacher_confirmed BOOLEAN NOT NULL CHECK (teacher_confirmed),
    decision_key UUID NOT NULL,
    payload_sha256 TEXT NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_feedback_decisions_draft_fk
        FOREIGN KEY (draft_id, organization_id)
        REFERENCES public.ai_feedback_drafts (id, organization_id)
        ON DELETE CASCADE,
    CONSTRAINT ai_feedback_decisions_key_unique
        UNIQUE (organization_id, decided_by, decision_key),
    CONSTRAINT ai_feedback_decisions_text_shape CHECK (
        (decision = 'rejected' AND approved_text IS NULL)
        OR
        (decision <> 'rejected'
            AND approved_text IS NOT NULL
            AND char_length(approved_text) BETWEEN 1 AND 6000)
    )
);

CREATE INDEX ai_feedback_decisions_draft_idx
    ON public.ai_feedback_decisions (draft_id, created_at);

-- ---------------------------------------------------------------------------
-- Integrity: related rows must belong to the same organization, and only an
-- active teacher/admin of that organization may request or decide. The backend
-- checks the same conditions first; these triggers hold even if it does not.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.aeos_ai_feedback_request_integrity()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM public.assessments AS related_assessment
        WHERE related_assessment.id = NEW.assessment_id
          AND related_assessment.organization_id = NEW.organization_id
          AND related_assessment.student_id = NEW.student_id
    ) THEN
        RAISE EXCEPTION 'ai_feedback_requests: assessment does not belong to the organization and student'
            USING ERRCODE = '23514';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM public.users AS requester
        JOIN public.organizations AS tenant ON tenant.id = requester.organization_id
        WHERE requester.id = NEW.created_by
          AND requester.organization_id = NEW.organization_id
          AND requester.status = 'active'
          AND requester.role IN ('teacher', 'admin')
          AND tenant.status = 'active'
    ) THEN
        RAISE EXCEPTION 'ai_feedback_requests: requester is not an active teacher or admin of the organization'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER ai_feedback_requests_integrity
BEFORE INSERT ON public.ai_feedback_requests
FOR EACH ROW
EXECUTE FUNCTION public.aeos_ai_feedback_request_integrity();

CREATE OR REPLACE FUNCTION public.aeos_ai_feedback_decision_integrity()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    draft_status ai_feedback_draft_status;
BEGIN
    SELECT draft.status INTO draft_status
    FROM public.ai_feedback_drafts AS draft
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

    RETURN NEW;
END;
$$;

CREATE TRIGGER ai_feedback_decisions_integrity
BEFORE INSERT ON public.ai_feedback_decisions
FOR EACH ROW
EXECUTE FUNCTION public.aeos_ai_feedback_decision_integrity();

-- ---------------------------------------------------------------------------
-- Append-only: no role may UPDATE these rows.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.aeos_reject_ai_feedback_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
    RAISE EXCEPTION '% is append-only; record a new row instead', TG_TABLE_NAME
        USING ERRCODE = '0A000';
END;
$$;

CREATE TRIGGER ai_feedback_requests_append_only
BEFORE UPDATE ON public.ai_feedback_requests
FOR EACH ROW
EXECUTE FUNCTION public.aeos_reject_ai_feedback_update();

CREATE TRIGGER ai_feedback_drafts_append_only
BEFORE UPDATE ON public.ai_feedback_drafts
FOR EACH ROW
EXECUTE FUNCTION public.aeos_reject_ai_feedback_update();

CREATE TRIGGER ai_feedback_decisions_append_only
BEFORE UPDATE ON public.ai_feedback_decisions
FOR EACH ROW
EXECUTE FUNCTION public.aeos_reject_ai_feedback_update();

-- ---------------------------------------------------------------------------
-- Audit: written in the same transaction as the save. No student text is
-- copied into audit metadata.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.aeos_audit_ai_feedback_draft()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    source_request public.ai_feedback_requests;
BEGIN
    SELECT * INTO source_request
    FROM public.ai_feedback_requests AS request
    WHERE request.id = NEW.request_id
      AND request.organization_id = NEW.organization_id;

    INSERT INTO public.audit_logs
        (id, organization_id, entity_type, entity_id, action, performed_by, metadata)
    VALUES (
        gen_random_uuid(),
        NEW.organization_id,
        'ai_feedback_draft',
        NEW.id,
        'ai_feedback.draft.' || NEW.status::text,
        source_request.created_by,
        jsonb_build_object(
            'request_id', NEW.request_id,
            'assessment_id', source_request.assessment_id,
            'status', NEW.status,
            'error_code', NEW.error_code,
            'provider', source_request.provider,
            'model_id', source_request.model_id,
            'prompt_version', source_request.prompt_version,
            'rubric_id', source_request.rubric_id,
            'rubric_version', source_request.rubric_version,
            'review_flag_count', cardinality(NEW.review_flags),
            'actual_cost_microusd', NEW.actual_cost_microusd
        )
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER ai_feedback_drafts_audit
AFTER INSERT ON public.ai_feedback_drafts
FOR EACH ROW
EXECUTE FUNCTION public.aeos_audit_ai_feedback_draft();

CREATE OR REPLACE FUNCTION public.aeos_audit_ai_feedback_decision()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    INSERT INTO public.audit_logs
        (id, organization_id, entity_type, entity_id, action, performed_by, metadata)
    VALUES (
        gen_random_uuid(),
        NEW.organization_id,
        'ai_feedback_decision',
        NEW.id,
        'ai_feedback.decision.' || NEW.decision::text,
        NEW.decided_by,
        jsonb_build_object(
            'draft_id', NEW.draft_id,
            'decision', NEW.decision,
            'review_flags_acknowledged', NEW.review_flags_acknowledged,
            'payload_sha256', NEW.payload_sha256
        )
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER ai_feedback_decisions_audit
AFTER INSERT ON public.ai_feedback_decisions
FOR EACH ROW
EXECUTE FUNCTION public.aeos_audit_ai_feedback_decision();

-- ---------------------------------------------------------------------------
-- Atomic reservation: idempotency, per-user and per-organization rate limits
-- and cost budgets are checked and the request row is inserted under one
-- per-organization advisory lock, so concurrent requests cannot jointly
-- overspend. A request without a draft (in flight, or abandoned by a crash)
-- counts at its worst-case reservation; a completed request counts at its
-- recorded actual cost.
--
-- SECURITY INVOKER: callable only by the service role (granted below), which
-- already holds the table privileges it needs.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.aeos_reserve_ai_feedback_request(
    p_request JSONB,
    p_limits JSONB
)
RETURNS JSONB
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
DECLARE
    new_request public.ai_feedback_requests;
    existing_id UUID;
    user_hourly_limit INTEGER := (p_limits ->> 'user_hourly_requests')::INTEGER;
    org_daily_limit INTEGER := (p_limits ->> 'org_daily_requests')::INTEGER;
    user_daily_cap BIGINT := (p_limits ->> 'user_daily_cost_microusd')::BIGINT;
    org_daily_cap BIGINT := (p_limits ->> 'org_daily_cost_microusd')::BIGINT;
    used INTEGER;
    spent BIGINT;
BEGIN
    IF user_hourly_limit IS NULL OR user_hourly_limit < 1
        OR org_daily_limit IS NULL OR org_daily_limit < 1
        OR user_daily_cap IS NULL OR user_daily_cap < 1
        OR org_daily_cap IS NULL OR org_daily_cap < 1 THEN
        RAISE EXCEPTION 'aeos_reserve_ai_feedback_request: every limit must be a positive number'
            USING ERRCODE = '22023';
    END IF;

    new_request := jsonb_populate_record(NULL::public.ai_feedback_requests, p_request);
    new_request.created_at := NOW();

    IF new_request.id IS NULL OR new_request.organization_id IS NULL
        OR new_request.created_by IS NULL OR new_request.request_key IS NULL THEN
        RAISE EXCEPTION 'aeos_reserve_ai_feedback_request: request identity is incomplete'
            USING ERRCODE = '22023';
    END IF;

    PERFORM pg_advisory_xact_lock(
        hashtextextended('aeos_ai_feedback:' || new_request.organization_id::text, 0)
    );

    SELECT request.id INTO existing_id
    FROM public.ai_feedback_requests AS request
    WHERE request.organization_id = new_request.organization_id
      AND request.created_by = new_request.created_by
      AND request.request_key = new_request.request_key;

    IF existing_id IS NOT NULL THEN
        RETURN jsonb_build_object('outcome', 'duplicate', 'request_id', existing_id);
    END IF;

    SELECT count(*) INTO used
    FROM public.ai_feedback_requests AS request
    WHERE request.organization_id = new_request.organization_id
      AND request.created_by = new_request.created_by
      AND request.created_at > NOW() - INTERVAL '1 hour';
    IF used >= user_hourly_limit THEN
        RETURN jsonb_build_object('outcome', 'user_rate_limited');
    END IF;

    SELECT count(*) INTO used
    FROM public.ai_feedback_requests AS request
    WHERE request.organization_id = new_request.organization_id
      AND request.created_at > NOW() - INTERVAL '24 hours';
    IF used >= org_daily_limit THEN
        RETURN jsonb_build_object('outcome', 'org_rate_limited');
    END IF;

    SELECT COALESCE(sum(COALESCE(draft.actual_cost_microusd, request.reserved_cost_microusd)), 0)
    INTO spent
    FROM public.ai_feedback_requests AS request
    LEFT JOIN public.ai_feedback_drafts AS draft ON draft.request_id = request.id
    WHERE request.organization_id = new_request.organization_id
      AND request.created_by = new_request.created_by
      AND request.created_at > NOW() - INTERVAL '24 hours';
    IF spent + new_request.reserved_cost_microusd > user_daily_cap THEN
        RETURN jsonb_build_object('outcome', 'user_budget_exceeded');
    END IF;

    SELECT COALESCE(sum(COALESCE(draft.actual_cost_microusd, request.reserved_cost_microusd)), 0)
    INTO spent
    FROM public.ai_feedback_requests AS request
    LEFT JOIN public.ai_feedback_drafts AS draft ON draft.request_id = request.id
    WHERE request.organization_id = new_request.organization_id
      AND request.created_at > NOW() - INTERVAL '24 hours';
    IF spent + new_request.reserved_cost_microusd > org_daily_cap THEN
        RETURN jsonb_build_object('outcome', 'org_budget_exceeded');
    END IF;

    INSERT INTO public.ai_feedback_requests VALUES (new_request.*);

    RETURN jsonb_build_object('outcome', 'reserved', 'request_id', new_request.id);
END;
$$;

REVOKE ALL ON FUNCTION public.aeos_reserve_ai_feedback_request(JSONB, JSONB) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_reserve_ai_feedback_request(JSONB, JSONB) FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.aeos_reserve_ai_feedback_request(JSONB, JSONB) TO service_role;

REVOKE ALL ON FUNCTION public.aeos_ai_feedback_request_integrity() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_ai_feedback_decision_integrity() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_audit_ai_feedback_draft() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_audit_ai_feedback_decision() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.aeos_reject_ai_feedback_update() FROM PUBLIC;

-- ---------------------------------------------------------------------------
-- RLS: members of the owning organization may read. No client write policy.
-- ---------------------------------------------------------------------------

ALTER TABLE public.ai_feedback_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_feedback_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_feedback_decisions ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.ai_feedback_requests FORCE ROW LEVEL SECURITY;
ALTER TABLE public.ai_feedback_drafts FORCE ROW LEVEL SECURITY;
ALTER TABLE public.ai_feedback_decisions FORCE ROW LEVEL SECURITY;

CREATE POLICY ai_feedback_requests_select
ON public.ai_feedback_requests FOR SELECT TO authenticated
USING (public.aeos_has_org_access(ai_feedback_requests.organization_id));

CREATE POLICY ai_feedback_drafts_select
ON public.ai_feedback_drafts FOR SELECT TO authenticated
USING (public.aeos_has_org_access(ai_feedback_drafts.organization_id));

CREATE POLICY ai_feedback_decisions_select
ON public.ai_feedback_decisions FOR SELECT TO authenticated
USING (public.aeos_has_org_access(ai_feedback_decisions.organization_id));
