'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

/** Creates a scoring run for a response that has none yet. */
export function ScoreResponseButton({ responseId }: { responseId: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function score() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responseId }),
      });
      const body = (await res.json()) as { error?: string };
      if (!res.ok) throw new Error(body.error ?? `HTTP ${res.status}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'failed to score');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <button className="btn btn-neutral" onClick={score} disabled={busy}>
        {busy ? 'Scoring…' : 'Generate AI draft scores'}
      </button>
      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
    </div>
  );
}
