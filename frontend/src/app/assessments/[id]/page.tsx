'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { FormEvent, useEffect, useRef, useState } from 'react';
import { getAccessToken } from '@/lib/api';
import {
  Assessment,
  AssessmentResult,
  getAssessment,
  listAssessmentResults,
  ReviewDraft,
  saveAssessmentReview,
} from '@/lib/assessments';

function ReviewForm({ assessmentId, onSave }: {
  assessmentId: string;
  onSave: (result: AssessmentResult) => void;
}) {
  const [score, setScore] = useState('');
  const [maxScore, setMaxScore] = useState('');
  const [summary, setSummary] = useState('');
  const [status, setStatus] = useState<ReviewDraft['status']>('draft');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const request = useRef<AbortController | null>(null);

  useEffect(() => () => request.current?.abort(), []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (request.current) return;
    setError('');
    setMessage('');

    const enteredScore = score.trim() === '' ? null : Number(score);
    const enteredMax = maxScore.trim() === '' ? null : Number(maxScore);
    if (!summary.trim()) {
      setError('Add a review summary before saving.');
      return;
    }
    if ((enteredScore !== null && (!Number.isFinite(enteredScore) || enteredScore < 0 || enteredScore > 9999.99)) ||
        (enteredMax !== null && (!Number.isFinite(enteredMax) || enteredMax < 0.01 || enteredMax > 9999.99)) ||
        (enteredScore !== null && enteredMax !== null && enteredScore > enteredMax)) {
      setError('Use scores from 0 to 9999.99 and a maximum of at least 0.01. The score cannot exceed the maximum.');
      return;
    }
    if (!getAccessToken()) {
      setError('Please sign in before saving a review.');
      return;
    }

    const controller = new AbortController();
    request.current = controller;
    setSaving(true);
    try {
      const result = await saveAssessmentReview(assessmentId, {
        score: enteredScore,
        max_score: enteredMax,
        summary: summary.trim(),
        status,
      }, controller.signal);
      if (controller.signal.aborted) return;
      onSave(result);
      setMessage(result.status === 'complete' ? 'Completed review saved.' : 'Draft review saved.');
      setScore('');
      setMaxScore('');
      setSummary('');
      setStatus('draft');
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err instanceof Error ? err.message : 'Unable to save review.');
      }
    } finally {
      if (!controller.signal.aborted) {
        request.current = null;
        setSaving(false);
      }
    }
  }

  return (
    <section className="card review-section" aria-labelledby="review-heading">
      <h2 id="review-heading">Add a teacher review</h2>
      <p>Record your assessment findings. Each save adds a new review; the assessment status stays unchanged.</p>
      {error ? <div role="alert" className="error">{error}</div> : null}
      {message ? <p role="status">{message}</p> : null}
      <form onSubmit={handleSubmit}>
        <fieldset disabled={saving} className="review-fields">
          <div className="form-grid">
            <div className="field">
              <label htmlFor="review-score">Score (optional)</label>
              <input id="review-score" type="number" min="0" max="9999.99" step="0.01" value={score} onChange={(event) => setScore(event.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="review-max-score">Maximum score (optional)</label>
              <input id="review-max-score" type="number" min="0.01" max="9999.99" step="0.01" value={maxScore} onChange={(event) => setMaxScore(event.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="review-status">Review status</label>
              <select id="review-status" value={status} onChange={(event) => setStatus(event.target.value as ReviewDraft['status'])}>
                <option value="draft">Draft</option>
                <option value="complete">Complete</option>
              </select>
            </div>
            <div className="field review-summary-field">
              <label htmlFor="review-summary">Review summary</label>
              <textarea id="review-summary" rows={5} required value={summary} onChange={(event) => setSummary(event.target.value)} />
            </div>
          </div>
          <div className="button-row review-actions">
            <button type="submit" className="primary-btn">{saving ? 'Saving…' : 'Save review'}</button>
            <button type="button" className="ghost-btn" onClick={() => {
              setScore(''); setMaxScore(''); setSummary(''); setStatus('draft'); setError(''); setMessage('');
            }}>Discard unsaved review</button>
          </div>
        </fieldset>
      </form>
    </section>
  );
}

export default function AssessmentDetailPage() {
  const params = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [results, setResults] = useState<AssessmentResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function loadReview() {
      setLoading(true);
      setError('');
      setAssessment(null);
      setResults([]);
      try {
        if (!getAccessToken()) throw new Error('Please sign in to review this assessment.');
        const [record, reviews] = await Promise.all([
          getAssessment(params.id, controller.signal),
          listAssessmentResults(params.id, controller.signal),
        ]);
        if (!controller.signal.aborted) {
          setAssessment(record);
          setResults(reviews);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : 'Unable to load assessment review.');
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    loadReview();
    return () => controller.abort();
  }, [params.id, attempt]);

  if (loading) return <main className="page-shell"><p role="status">Loading assessment review…</p></main>;

  if (error || !assessment) {
    return (
      <main className="page-shell">
        <div role="alert" className="error">{error || 'Assessment not found.'}</div>
        <div className="button-row">
          <button className="primary-btn" onClick={() => setAttempt((value) => value + 1)}>Try again</button>
          <Link href="/assessments" className="secondary-btn">Back to assessments</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>{assessment.title}</h1>
        <div className="button-row">
          <Link href="/assessments" className="secondary-btn">Back to assessments</Link>
        </div>
      </div>
      <section className="card" aria-label="Assessment details">
        <div className="detail-grid">
          <div className="meta-box"><strong>Type</strong><br />{assessment.assessment_type}</div>
          <div className="meta-box"><strong>Assessment status</strong><br />{assessment.status}</div>
          <div className="meta-box"><strong>Student ID</strong><br />{assessment.student_id}</div>
          <div className="meta-box"><strong>Notes</strong><p className="review-text">{assessment.notes || 'No notes recorded.'}</p></div>
        </div>
      </section>
      <section className="card review-section" aria-labelledby="saved-reviews-heading">
        <h2 id="saved-reviews-heading">Saved reviews</h2>
        {results.length === 0 ? <p className="empty-state">No reviews recorded for this assessment.</p> : (
          <ul className="review-list">
            {results.map((result) => (
              <li key={result.id} className="meta-box">
                <p><strong>Review status:</strong> {result.status}</p>
                <p><strong>Score:</strong> {result.score ?? 'Not recorded'}{result.max_score !== null ? ` / ${result.max_score}` : ''}</p>
                <p className="review-text">{result.summary || 'No summary recorded.'}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
      <ReviewForm key={assessment.id} assessmentId={assessment.id} onSave={(result) => setResults((previous) => [result, ...previous])} />
    </main>
  );
}
