'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import type { VerificationResult } from '@/lib/evidence';
import { EvidenceBadge, ConfidenceBadge, ActionBadge } from '@/components/Badges';

export type CriterionView = {
  id: string;
  label: string;
  description: string;
  weight: number;
  scale: { min: number; max: number };
  draft: {
    score: number;
    rationale: string;
    evidence: string;
    confidence: 'low' | 'medium' | 'high';
  } | null;
  verification: VerificationResult;
  decision: {
    action: string;
    finalScore: number;
    note: string | null;
    decidedAt: string;
  } | null;
};

type Props = {
  responseId: string;
  pseudonym: string;
  subgroup: string | null;
  prompt: string;
  text: string;
  modelVersion: string;
  promptVersion: string;
  scoringRunId: string;
  rubricName: string;
  criteria: CriterionView[];
  killPaused: boolean;
  killViolations: string[];
  acceptAllowed: boolean;
};

type Action = 'accept' | 'revise' | 'reject' | 'flag';

export function ReviewClient(props: Props) {
  const router = useRouter();
  const [highlight, setHighlight] = useState<{ start: number; end: number } | null>(null);
  const [scores, setScores] = useState<Record<string, number>>(() =>
    Object.fromEntries(
      props.criteria.map((c) => [c.id, c.decision?.finalScore ?? c.draft?.score ?? c.scale.min]),
    ),
  );
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [viewed, setViewed] = useState<Record<string, boolean>>({});

  // Time on task is recorded server-side; this is the visible clock only.
  const [elapsed, setElapsed] = useState(0);
  const mountedAt = useRef(Date.now());
  useEffect(() => {
    const t = setInterval(() => setElapsed(Math.floor((Date.now() - mountedAt.current) / 1000)), 1000);
    return () => clearInterval(t);
  }, []);

  const verifyEvidence = useCallback(
    async (c: CriterionView) => {
      if (c.verification.status !== 'not_found') {
        setHighlight({ start: c.verification.start, end: c.verification.end });
      } else {
        setHighlight(null);
      }
      setViewed((v) => ({ ...v, [c.id]: true }));
      try {
        await fetch('/api/audit/evidence-viewed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ responseId: props.responseId, criterionId: c.id }),
        });
      } catch {
        // The audit write is best-effort from the UI; the server-side record is
        // what counts and a failure here must not block the reviewer.
      }
    },
    [props.responseId],
  );

  async function decide(c: CriterionView, action: Action) {
    if (!c.draft) return;
    setBusy(`${c.id}:${action}`);
    setErrors((e) => ({ ...e, [c.id]: '' }));
    try {
      const res = await fetch('/api/decisions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          responseId: props.responseId,
          criterionId: c.id,
          aiScore: c.draft.score,
          finalScore: action === 'accept' ? c.draft.score : scores[c.id],
          action,
          note: notes[c.id]?.trim() ? notes[c.id] : undefined,
          scoringRunId: props.scoringRunId,
        }),
      });
      const body = (await res.json()) as { error?: string; details?: unknown };
      if (!res.ok) throw new Error(body.error ?? `HTTP ${res.status}`);
      router.refresh();
    } catch (err) {
      setErrors((e) => ({ ...e, [c.id]: err instanceof Error ? err.message : 'failed' }));
    } finally {
      setBusy(null);
    }
  }

  const decidedCount = props.criteria.filter((c) => c.decision).length;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <h1 className="text-xl font-semibold">Review — {props.pseudonym}</h1>
        {props.subgroup ? (
          <span className="badge bg-slate-200 text-slate-700" title="De-identified cohort label">
            {props.subgroup}
          </span>
        ) : null}
        <span className="text-sm text-slate-500">
          {decidedCount}/{props.criteria.length} criteria decided
        </span>
        <span className="text-sm tabular-nums text-slate-500">on screen {elapsed}s</span>
        <Link href="/" className="ml-auto text-sm text-slate-600 hover:text-slate-900">
          ← Back to dashboard
        </Link>
      </div>

      {props.killPaused ? (
        <div
          className="mb-4 rounded-md border-2 border-red-700 bg-red-50 p-4"
          role="alert"
          data-testid="kill-banner"
        >
          <p className="font-semibold text-red-900">
            Kill criteria tripped — Accept is {props.acceptAllowed ? 'enabled by acknowledgement' : 'disabled'}
          </p>
          <ul className="mt-1 list-inside list-disc text-sm text-red-900">
            {props.killViolations.map((v) => (
              <li key={v}>{v}</li>
            ))}
          </ul>
          {!props.acceptAllowed ? (
            <p className="mt-2 text-sm text-red-900">
              Acknowledge on the{' '}
              <Link href="/" className="underline">
                dashboard
              </Link>{' '}
              to continue accepting, or keep reviewing with Revise / Reject / Flag.
            </p>
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
        {/* Left: the student response, with evidence highlighting. */}
        <section className="card lg:sticky lg:top-4 lg:self-start">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Student response
          </h2>
          <p className="mt-1 text-sm italic text-slate-600">{props.prompt}</p>
          <p className="mt-3 whitespace-pre-wrap leading-relaxed">
            <HighlightedText text={props.text} highlight={highlight} />
          </p>
          <p className="mt-4 text-xs text-slate-500">
            Rubric: {props.rubricName} · model <code>{props.modelVersion}</code> · prompt{' '}
            <code>{props.promptVersion}</code>
          </p>
        </section>

        {/* Right: one card per criterion. */}
        <section className="space-y-4">
          {props.criteria.map((c) => (
            <CriterionCard
              key={c.id}
              criterion={c}
              score={scores[c.id] ?? c.scale.min}
              note={notes[c.id] ?? ''}
              busy={busy}
              error={errors[c.id] ?? ''}
              viewed={Boolean(viewed[c.id])}
              acceptAllowed={props.acceptAllowed}
              onScore={(v) => setScores((s) => ({ ...s, [c.id]: v }))}
              onNote={(v) => setNotes((n) => ({ ...n, [c.id]: v }))}
              onVerify={() => verifyEvidence(c)}
              onDecide={(a) => decide(c, a)}
            />
          ))}
        </section>
      </div>
    </div>
  );
}

function HighlightedText({
  text,
  highlight,
}: {
  text: string;
  highlight: { start: number; end: number } | null;
}) {
  if (!highlight) return <>{text}</>;
  const { start, end } = highlight;
  if (start < 0 || end > text.length || start >= end) return <>{text}</>;
  return (
    <>
      {text.slice(0, start)}
      <mark className="evidence-hit">{text.slice(start, end)}</mark>
      {text.slice(end)}
    </>
  );
}

function CriterionCard({
  criterion: c,
  score,
  note,
  busy,
  error,
  viewed,
  acceptAllowed,
  onScore,
  onNote,
  onVerify,
  onDecide,
}: {
  criterion: CriterionView;
  score: number;
  note: string;
  busy: string | null;
  error: string;
  viewed: boolean;
  acceptAllowed: boolean;
  onScore: (v: number) => void;
  onNote: (v: string) => void;
  onVerify: () => void;
  onDecide: (a: Action) => void;
}) {
  const scaleValues = useMemo(() => {
    const out: number[] = [];
    for (let v = c.scale.min; v <= c.scale.max; v++) out.push(v);
    return out;
  }, [c.scale.min, c.scale.max]);

  if (!c.draft) {
    return (
      <article className="card">
        <h3 className="font-semibold">{c.label}</h3>
        <p className="mt-2 text-sm text-red-700">
          No AI draft for this criterion in the current scoring run.
        </p>
      </article>
    );
  }

  const decided = c.decision !== null;
  const isBusy = busy?.startsWith(`${c.id}:`) ?? false;
  const unchanged = score === c.draft.score;

  return (
    <article className={`card ${decided ? 'opacity-90' : ''}`} data-criterion={c.id}>
      <header className="flex flex-wrap items-center gap-2">
        <h3 className="font-semibold">{c.label}</h3>
        <span className="text-xs text-slate-500">weight {c.weight}</span>
        <span className="ml-auto flex items-center gap-2">
          <ConfidenceBadge level={c.draft.confidence} />
          <EvidenceBadge status={c.verification.status} />
        </span>
      </header>

      <p className="mt-1 text-xs text-slate-500">{c.description}</p>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-sm text-slate-600">AI draft score</span>
        <span className="text-2xl font-semibold tabular-nums">{c.draft.score}</span>
        <span className="text-sm text-slate-500">
          / {c.scale.min}–{c.scale.max}
        </span>
      </div>

      <p className="mt-2 text-sm text-slate-700">{c.draft.rationale}</p>

      <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-3">
        <div className="flex items-start justify-between gap-3">
          <p className="text-sm">
            <span className="text-xs uppercase tracking-wide text-slate-500">Claimed evidence</span>
            <br />
            <q className="italic">{c.draft.evidence}</q>
          </p>
          <button className="btn btn-neutral shrink-0" onClick={onVerify} type="button">
            {viewed ? 'Re-check' : 'Verify'}
          </button>
        </div>
        {c.verification.status === 'not_found' ? (
          <p className="mt-2 text-sm font-medium text-red-800">
            This quote does not appear in the student response. Do not accept this score on the
            strength of it.
          </p>
        ) : null}
        {c.verification.status === 'case-insensitive' ? (
          <p className="mt-2 text-sm text-amber-800">
            Matched only when letter case is ignored.
          </p>
        ) : null}
      </div>

      {decided ? (
        <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-3">
          <ActionBadge action={c.decision?.action ?? ''} />
          <span className="text-sm text-slate-600">
            final score <strong className="tabular-nums">{c.decision?.finalScore}</strong>
          </span>
          {c.decision?.note ? (
            <span className="text-sm text-slate-500">· {c.decision.note}</span>
          ) : null}
          <span className="ml-auto text-xs text-slate-400">decided — one decision per criterion</span>
        </div>
      ) : (
        <div className="mt-3 border-t border-slate-200 pt-3">
          <div className="flex flex-wrap items-center gap-3">
            <label className="text-sm text-slate-600">
              Your score{' '}
              <select
                className="ml-1 rounded border border-slate-300 px-2 py-1"
                value={score}
                onChange={(e) => onScore(Number(e.target.value))}
              >
                {scaleValues.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </label>
            <input
              className="min-w-0 flex-1 rounded border border-slate-300 px-2 py-1 text-sm"
              placeholder="Note (optional)"
              value={note}
              onChange={(e) => onNote(e.target.value)}
            />
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <button
              className="btn btn-accept"
              type="button"
              disabled={isBusy || !acceptAllowed || !unchanged}
              title={
                !acceptAllowed
                  ? 'Accept is disabled while a kill criterion is unacknowledged'
                  : !unchanged
                    ? 'Your score differs from the AI draft — use Revise'
                    : 'Accept the AI draft score'
              }
              onClick={() => onDecide('accept')}
            >
              Accept
            </button>
            <button
              className="btn btn-revise"
              type="button"
              disabled={isBusy || unchanged}
              title={unchanged ? 'Change your score first, then Revise' : 'Replace with your score'}
              onClick={() => onDecide('revise')}
            >
              Revise
            </button>
            <button
              className="btn btn-reject"
              type="button"
              disabled={isBusy}
              onClick={() => onDecide('reject')}
            >
              Reject
            </button>
            <button
              className="btn btn-flag"
              type="button"
              disabled={isBusy}
              onClick={() => onDecide('flag')}
            >
              Flag
            </button>
          </div>

          {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
        </div>
      )}
    </article>
  );
}
