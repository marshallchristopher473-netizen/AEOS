import { apiFetch } from './api';

// The browser talks only to the AEOS backend. The provider, model, key and
// system instructions live on the server; nothing here can choose them.

export type EvidenceSpan = { start: number; end: number; quote: string };

export type CriterionFeedback = {
  criterion_id: string;
  criterion_name: string;
  outcome: 'feedback' | 'abstain';
  strength: string | null;
  next_step: string | null;
  evidence: EvidenceSpan[];
  abstention_reason: string | null;
};

export type FeedbackDecision = {
  id: string;
  draft_id: string;
  decided_by: string;
  decision: 'accepted' | 'revised' | 'rejected';
  approved_text: string | null;
  review_flags_acknowledged: boolean;
  created_at: string | null;
};

export type FeedbackDraft = {
  id: string;
  assessment_id: string;
  status: 'ready' | 'abstained' | 'rejected_output' | 'provider_error' | 'provider_refused';
  feedback: { overall_abstention: string | null; criteria: CriterionFeedback[] } | null;
  draft_text: string | null;
  review_flags: string[];
  error_code: string | null;
  response_text: string;
  model_id: string;
  prompt_version: string;
  rubric_id: string;
  rubric_version: string;
  data_classification: string;
  decisions: FeedbackDecision[];
  current_decision: FeedbackDecision | null;
  created_at: string | null;
};

export type DraftInput = {
  assessment_id: string;
  response_text: string;
  source_text: string | null;
};

export type DecisionInput = {
  decision: FeedbackDecision['decision'];
  approved_text: string | null;
  review_flags_acknowledged: boolean;
};

// The only rubric approved for this synthetic phase (approval is enforced
// server-side by content hash).
export const SYNTHETIC_RUBRIC = { id: 'RUB-CER3', version: '0.1' };

export function newIdempotencyKey(): string {
  return crypto.randomUUID();
}

export function listFeedbackDrafts(assessmentId: string, signal?: AbortSignal) {
  return apiFetch<FeedbackDraft[]>(`/ai-feedback/drafts?assessment_id=${encodeURIComponent(assessmentId)}`, { signal });
}

export function requestFeedbackDraft(input: DraftInput, idempotencyKey: string, signal?: AbortSignal) {
  return apiFetch<FeedbackDraft>('/ai-feedback/drafts', {
    method: 'POST',
    headers: { 'Idempotency-Key': idempotencyKey },
    body: JSON.stringify({
      assessment_id: input.assessment_id,
      rubric_id: SYNTHETIC_RUBRIC.id,
      rubric_version: SYNTHETIC_RUBRIC.version,
      response_text: input.response_text,
      ...(input.source_text ? { source_text: input.source_text } : {}),
      data_classification: 'synthetic',
    }),
    signal,
  });
}

// Called only from an explicit teacher button press.
export function recordFeedbackDecision(draftId: string, input: DecisionInput, idempotencyKey: string, signal?: AbortSignal) {
  return apiFetch<FeedbackDraft>(`/ai-feedback/drafts/${encodeURIComponent(draftId)}/decisions`, {
    method: 'POST',
    headers: { 'Idempotency-Key': idempotencyKey },
    body: JSON.stringify({
      decision: input.decision,
      ...(input.decision === 'rejected' ? {} : { approved_text: input.approved_text }),
      review_flags_acknowledged: input.review_flags_acknowledged,
      teacher_confirmed: true,
    }),
    signal,
  });
}
