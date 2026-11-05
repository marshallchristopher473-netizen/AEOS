'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export type AnchorView = {
  responseId: string;
  pseudonym: string;
  subgroup: string | null;
  prompt: string;
  text: string;
  hasRun: boolean;
  myScore: number | null;
  revealed: {
    aiScore: number | null;
    revealedAt: string;
    peers: Array<{ reviewer: string; manualScore: number }>;
  } | null;
};

export function CalibrationClient({
  reviewer,
  rubricName,
  scaleMin,
  scaleMax,
  anchors,
}: {
  reviewer: string;
  rubricName: string;
  scaleMin: number;
  scaleMax: number;
  anchors: AnchorView[];
}) {
  const router = useRouter();
  const [busy, setBusy] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [drafts, setDrafts] = useState<Record<string, number>>({});

  const scaleValues: number[] = [];
  for (let v = scaleMin; v <= scaleMax; v++) scaleValues.push(v);

  async function post(url: string, body: unknown, key: string) {
    setBusy(key);
    setErrors((e) => ({ ...e, [key]: '' }));
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const json = (await res.json()) as { error?: string };
      if (!res.ok) throw new Error(json.error ?? `HTTP ${res.status}`);
      router.refresh();
    } catch (err) {
      setErrors((e) => ({ ...e, [key]: err instanceof Error ? err.message : 'failed' }));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-semibold">Calibration</h1>
        <p className="mt-1 text-sm text-slate-600">
          Score each anchor paper holistically on the {scaleMin}–{scaleMax} scale{' '}
          <strong>before</strong> revealing the AI score and your peers&apos;. Scoring blind is what
          makes the comparison meaningful — the reveal is one-way and recorded in the audit log.
        </p>
        <p className="mt-1 text-xs text-slate-500">
          Rubric: {rubricName} · reviewer: {reviewer}
        </p>
      </header>

      {anchors.map((a) => {
        const scoreKey = `score:${a.responseId}`;
        const revealKey = `reveal:${a.responseId}`;
        const selected = drafts[a.responseId] ?? scaleMin;

        return (
          <article key={a.responseId} className="card">
            <header className="flex flex-wrap items-center gap-2">
              <h2 className="font-semibold">{a.pseudonym}</h2>
              {a.subgroup ? (
                <span className="badge bg-slate-200 text-slate-700">{a.subgroup}</span>
              ) : null}
              {a.myScore !== null ? (
                <span className="badge bg-sky-100 text-sky-900">your blind score: {a.myScore}</span>
              ) : (
                <span className="badge bg-slate-100 text-slate-600">not yet scored</span>
              )}
            </header>

            <p className="mt-1 text-sm italic text-slate-600">{a.prompt}</p>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{a.text}</p>

            {a.myScore === null ? (
              <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-3">
                <label className="text-sm text-slate-600">
                  Your holistic score{' '}
                  <select
                    className="ml-1 rounded border border-slate-300 px-2 py-1"
                    value={selected}
                    onChange={(e) =>
                      setDrafts((d) => ({ ...d, [a.responseId]: Number(e.target.value) }))
                    }
                  >
                    {scaleValues.map((v) => (
                      <option key={v} value={v}>
                        {v}
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  className="btn btn-neutral"
                  type="button"
                  disabled={busy === scoreKey}
                  onClick={() =>
                    post(
                      '/api/calibration',
                      { responseId: a.responseId, manualScore: selected },
                      scoreKey,
                    )
                  }
                >
                  {busy === scoreKey ? 'Saving…' : 'Submit blind score'}
                </button>
                {errors[scoreKey] ? (
                  <span className="text-sm text-red-700">{errors[scoreKey]}</span>
                ) : null}
              </div>
            ) : a.revealed === null ? (
              <div className="mt-3 border-t border-slate-200 pt-3">
                <button
                  className="btn btn-neutral"
                  type="button"
                  disabled={busy === revealKey || !a.hasRun}
                  title={a.hasRun ? undefined : 'This anchor has no scoring run yet'}
                  onClick={() => post('/api/calibration/reveal', { responseId: a.responseId }, revealKey)}
                >
                  {busy === revealKey ? 'Revealing…' : 'Reveal AI score + peers'}
                </button>
                {errors[revealKey] ? (
                  <span className="ml-2 text-sm text-red-700">{errors[revealKey]}</span>
                ) : null}
              </div>
            ) : (
              <div className="mt-3 border-t border-slate-200 pt-3 text-sm">
                <div className="flex flex-wrap items-center gap-4">
                  <span>
                    You: <strong className="tabular-nums">{a.myScore}</strong>
                  </span>
                  <span>
                    AI:{' '}
                    <strong className="tabular-nums">
                      {a.revealed.aiScore ?? 'n/a'}
                    </strong>
                  </span>
                  {a.revealed.aiScore !== null ? (
                    <span
                      className={
                        a.revealed.aiScore === a.myScore
                          ? 'badge bg-green-100 text-green-900'
                          : Math.abs(a.revealed.aiScore - a.myScore) === 1
                            ? 'badge bg-amber-100 text-amber-900'
                            : 'badge bg-red-100 text-red-900'
                      }
                    >
                      gap {Math.abs(a.revealed.aiScore - a.myScore)}
                    </span>
                  ) : null}
                </div>
                <div className="mt-2 text-slate-600">
                  Peers:{' '}
                  {a.revealed.peers.length === 0
                    ? 'no other reviewers have calibrated on this anchor yet'
                    : a.revealed.peers
                        .map((p) => `${p.reviewer}: ${p.manualScore}`)
                        .join(' · ')}
                </div>
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
}
