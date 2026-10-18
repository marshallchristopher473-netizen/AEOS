'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import { ApiError, getAccessToken } from '@/lib/api';
import {
  DecisionInput,
  FeedbackDraft,
  listFeedbackDrafts,
  newIdempotencyKey,
  recordFeedbackDecision,
  requestFeedbackDraft,
} from '@/lib/aiFeedback';

const MAX_RESPONSE = 4000;
const MAX_SOURCE = 6000;

const FLAG_LABELS: Record<string, string> = {
  possible_embedded_instructions: 'The response contains text that looks like instructions to the AI. It was treated as student writing only.',
  off_topic: 'The AI marked the response as possibly off topic.',
  very_short_response: 'The response is very short.',
  needs_teacher_judgment: 'The AI asked for teacher judgment.',
  unverified_evidence_removed: 'Feedback that cited text not found in the response was removed.',
  partial_abstention: 'The AI did not draft feedback for every criterion.',
};

const ABSTENTION_LABELS: Record<string, string> = {
  insufficient_response: 'Not enough writing to give feedback on this criterion.',
  off_task: 'The response appears off task.',
  not_assessable_from_response: 'This criterion cannot be judged from the response.',
  evidence_not_verified: 'Removed: the AI cited text that is not in the response.',
};

const STATUS_LABELS: Record<FeedbackDraft['status'], string> = {
  ready: 'Draft ready for review',
  abstained: 'AI abstained',
  rejected_output: 'AI output discarded by safety validation',
  provider_error: 'AI provider error',
  provider_refused: 'AI provider declined',
};

function DraftReview({ draft, onDecided }: { draft: FeedbackDraft; onDecided: (draft: FeedbackDraft) => void }) {
  const [text, setText] = useState(draft.current_decision?.approved_text ?? draft.draft_text ?? '');
  const [acknowledged, setAcknowledged] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const pendingKey = useRef<{ fingerprint: string; key: string } | null>(null);
  const reviewable = draft.status === 'ready' || draft.status === 'abstained';
  const unchanged = draft.draft_text !== null && text === draft.draft_text;
  const flagged = draft.review_flags.length > 0;

  async function decide(input: DecisionInput) {
    if (saving) return;
    setError('');
    setMessage('');
    if (input.decision !== 'rejected' && flagged && !acknowledged) {
      setError('Confirm that you reviewed the flags before saving feedback.');
      return;
    }
    // Reuse the key only when retrying the identical decision after a
    // network failure, so a retry cannot save twice.
    const fingerprint = JSON.stringify(input);
    if (pendingKey.current?.fingerprint !== fingerprint) {
      pendingKey.current = { fingerprint, key: newIdempotencyKey() };
    }
    setSaving(true);
    try {
      const updated = await recordFeedbackDecision(draft.id, input, pendingKey.current.key);
      pendingKey.current = null;
      onDecided(updated);
      setMessage(input.decision === 'rejected' ? 'Draft rejected.' : 'Teacher-approved feedback saved.');
    } catch (err) {
      if (err instanceof ApiError) pendingKey.current = null;
      setError(err instanceof Error ? err.message : 'Unable to save the decision.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <li className="meta-box ai-draft">
      <p><strong>{STATUS_LABELS[draft.status]}</strong></p>
      <p className="ai-meta">Rubric {draft.rubric_id} v{draft.rubric_version} · prompt {draft.prompt_version} · model {draft.model_id}</p>
      <details>
        <summary>Synthetic response used</summary>
        <p className="review-text">{draft.response_text}</p>
      </details>
      {draft.review_flags.length > 0 ? (
        <ul className="ai-flags" aria-label="Review flags">
          {draft.review_flags.map((flag) => <li key={flag}>{FLAG_LABELS[flag] ?? flag}</li>)}
        </ul>
      ) : null}
      {draft.feedback ? (
        <ul className="ai-criteria">
          {draft.feedback.criteria.map((item) => (
            <li key={item.criterion_id}>
              <strong>{item.criterion_name}</strong>
              {item.outcome === 'abstain' ? (
                <p className="empty-state">{ABSTENTION_LABELS[item.abstention_reason ?? ''] ?? 'No feedback drafted.'}</p>
              ) : (
                <>
                  {item.strength ? <p>Strength: {item.strength}</p> : null}
                  {item.next_step ? <p>Next step: {item.next_step}</p> : null}
                  <p className="ai-evidence">Evidence from the response: {item.evidence.map((span) => `“${span.quote}”`).join(' · ')}</p>
                </>
              )}
            </li>
          ))}
        </ul>
      ) : null}
      {draft.current_decision ? (
        <p role="status"><strong>Current teacher decision:</strong> {draft.current_decision.decision}</p>
      ) : reviewable ? <p className="empty-state">No teacher decision yet. Nothing is final until you choose below.</p> : null}
      {reviewable ? (
        <fieldset disabled={saving} className="review-fields">
          {error ? <div role="alert" className="error">{error}</div> : null}
          {message ? <p role="status">{message}</p> : null}
          <div className="field">
            <label htmlFor={`approved-${draft.id}`}>Feedback text (edit to revise)</label>
            <textarea id={`approved-${draft.id}`} rows={6} maxLength={6000} value={text} onChange={(event) => setText(event.target.value)} />
          </div>
          {flagged ? (
            <label className="ai-ack">
              <input type="checkbox" checked={acknowledged} onChange={(event) => setAcknowledged(event.target.checked)} />
              {' '}I reviewed the flags above.
            </label>
          ) : null}
          <div className="button-row">
            <button type="button" className="primary-btn" disabled={draft.status !== 'ready' || !unchanged}
              onClick={() => decide({ decision: 'accepted', approved_text: text, review_flags_acknowledged: acknowledged })}>
              Accept draft as written
            </button>
            <button type="button" className="secondary-btn" disabled={unchanged || !text.trim()}
              onClick={() => decide({ decision: 'revised', approved_text: text, review_flags_acknowledged: acknowledged })}>
              Save my revision
            </button>
            <button type="button" className="ghost-btn"
              onClick={() => decide({ decision: 'rejected', approved_text: null, review_flags_acknowledged: acknowledged })}>
              Reject draft
            </button>
          </div>
        </fieldset>
      ) : null}
    </li>
  );
}

export default function AiFeedbackPanel({ assessmentId }: { assessmentId: string }) {
  const [drafts, setDrafts] = useState<FeedbackDraft[]>([]);
  const [unavailable, setUnavailable] = useState('');
  const [loading, setLoading] = useState(true);
  const [responseText, setResponseText] = useState('');
  const [sourceText, setSourceText] = useState('');
  const [synthetic, setSynthetic] = useState(false);
  const [requesting, setRequesting] = useState(false);
  const [error, setError] = useState('');
  const pendingKey = useRef<{ fingerprint: string; key: string } | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    listFeedbackDrafts(assessmentId, controller.signal)
      .then((items) => {
        if (!controller.signal.aborted) {
          setDrafts([...items].sort((a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? '')));
        }
      })
      .catch((err) => {
        if (controller.signal.aborted) return;
        setUnavailable(err instanceof Error ? err.message : 'AI feedback drafting is not available.');
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [assessmentId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (requesting) return;
    setError('');
    if (!synthetic) {
      setError('Confirm that this is a synthetic response. Real student work is not allowed in this phase.');
      return;
    }
    if (!responseText.trim()) {
      setError('Paste a synthetic response first.');
      return;
    }
    if (!getAccessToken()) {
      setError('Please sign in before requesting a draft.');
      return;
    }
    const input = {
      assessment_id: assessmentId,
      response_text: responseText,
      source_text: sourceText.trim() ? sourceText : null,
    };
    const fingerprint = JSON.stringify(input);
    if (pendingKey.current?.fingerprint !== fingerprint) {
      pendingKey.current = { fingerprint, key: newIdempotencyKey() };
    }
    setRequesting(true);
    try {
      const draft = await requestFeedbackDraft(input, pendingKey.current.key);
      pendingKey.current = null;
      setDrafts((previous) => [draft, ...previous.filter((item) => item.id !== draft.id)]);
    } catch (err) {
      // An HTTP answer is final for this key; a network failure keeps the key
      // so a retry of the same text is deduplicated by the server.
      if (err instanceof ApiError) pendingKey.current = null;
      setError(err instanceof Error ? err.message : 'Unable to request a draft.');
    } finally {
      setRequesting(false);
    }
  }

  if (loading) return <section className="card review-section"><p role="status">Loading AI feedback drafts…</p></section>;
  if (unavailable) {
    return (
      <section className="card review-section" aria-labelledby="ai-feedback-heading">
        <h2 id="ai-feedback-heading">AI feedback draft</h2>
        <p className="empty-state">{unavailable}</p>
      </section>
    );
  }

  return (
    <section className="card review-section" aria-labelledby="ai-feedback-heading">
      <h2 id="ai-feedback-heading">AI feedback draft (synthetic responses only)</h2>
      <p>
        The AI drafts criterion-linked feedback for you to review. It does not score, diagnose, or decide anything.
        Nothing is final, shared, or written to a gradebook until you accept, revise, or reject it.
      </p>
      <form onSubmit={handleSubmit}>
        <fieldset disabled={requesting} className="review-fields">
          {error ? <div role="alert" className="error">{error}</div> : null}
          <div className="field">
            <label htmlFor="ai-response">Synthetic short response ({responseText.length}/{MAX_RESPONSE})</label>
            <textarea id="ai-response" rows={5} maxLength={MAX_RESPONSE} value={responseText} onChange={(event) => setResponseText(event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="ai-source">Source passage, optional ({sourceText.length}/{MAX_SOURCE})</label>
            <textarea id="ai-source" rows={4} maxLength={MAX_SOURCE} value={sourceText} onChange={(event) => setSourceText(event.target.value)} />
          </div>
          <label className="ai-ack">
            <input type="checkbox" checked={synthetic} onChange={(event) => setSynthetic(event.target.checked)} />
            {' '}This is a synthetic response, not real student work.
          </label>
          <div className="button-row">
            <button type="submit" className="primary-btn">{requesting ? 'Drafting…' : 'Draft feedback'}</button>
          </div>
        </fieldset>
      </form>
      {drafts.length === 0 ? <p className="empty-state">No AI drafts for this assessment yet.</p> : (
        <ul className="review-list">
          {drafts.map((draft) => (
            <DraftReview key={draft.id} draft={draft}
              onDecided={(updated) => setDrafts((previous) => previous.map((item) => item.id === updated.id ? updated : item))} />
          ))}
        </ul>
      )}
    </section>
  );
}
