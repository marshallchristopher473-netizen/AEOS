import { apiFetch } from './api';

export type Assessment = {
  id: string;
  organization_id: string;
  student_id: string;
  created_by: string;
  title: string;
  assessment_type: string;
  status: string;
  notes?: string | null;
};

export type AssessmentResult = {
  id: string;
  assessment_id: string;
  student_id: string;
  created_by: string;
  score: number | null;
  max_score: number | null;
  summary: string | null;
  status: string;
  created_at: string | null;
};

export type ReviewDraft = {
  score: number | null;
  max_score: number | null;
  summary: string;
  status: 'draft' | 'complete';
};

export function createAssessment(payload: Pick<Assessment, 'student_id' | 'title' | 'assessment_type' | 'status' | 'notes'>) {
  return apiFetch<Assessment>('/assessments', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAssessments(signal?: AbortSignal) {
  return apiFetch<Assessment[]>('/assessments', { signal });
}

export function getAssessment(id: string, signal?: AbortSignal) {
  return apiFetch<Assessment>(`/assessments/${encodeURIComponent(id)}`, { signal });
}

export function listAssessmentResults(id: string, signal?: AbortSignal) {
  return apiFetch<AssessmentResult[]>(`/assessment-results?assessment_id=${encodeURIComponent(id)}`, { signal });
}

export function saveAssessmentReview(id: string, draft: ReviewDraft, signal?: AbortSignal) {
  return apiFetch<AssessmentResult>('/assessment-results', {
    method: 'POST',
    body: JSON.stringify({ assessment_id: id, ...draft }),
    signal,
  });
}
