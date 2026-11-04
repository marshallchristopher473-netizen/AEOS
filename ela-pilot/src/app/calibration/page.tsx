import Link from 'next/link';
import { getDb } from '@db/client';
import { currentReviewer } from '@/lib/reviewer';
import { listResponses, latestScoringRun, defaultRubric, type CalibrationRow } from '@/lib/repo';
import { calibrationScale } from '@/lib/calibration';
import { CalibrationClient, type AnchorView } from './CalibrationClient';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/** The pilot calibrates on the first three responses as anchor papers. */
const ANCHOR_COUNT = 3;

export default function CalibrationPage() {
  const db = getDb();
  const reviewer = currentReviewer();

  let rubricName = '';
  let scale = { min: 1, max: 4 };
  try {
    const { rubric } = defaultRubric(db);
    rubricName = rubric.name;
    scale = calibrationScale(rubric);
  } catch {
    return (
      <div className="card">
        <h1 className="text-lg font-semibold">No rubric found</h1>
        <p className="mt-2 text-sm text-slate-600">
          Run <code className="rounded bg-slate-100 px-1">npm run seed</code> first.
        </p>
      </div>
    );
  }

  if (!reviewer) {
    return (
      <div className="card">
        <h1 className="text-lg font-semibold">Select a reviewer first</h1>
        <p className="mt-2 text-sm text-slate-600">
          Calibration scores are recorded per reviewer so blind scores can be compared with peers.
        </p>
        <Link href="/" className="btn btn-neutral mt-4 inline-block">
          Go to dashboard
        </Link>
      </div>
    );
  }

  const anchors: AnchorView[] = listResponses(db)
    .slice(0, ANCHOR_COUNT)
    .map((r) => {
      const mine = db
        .prepare('SELECT * FROM calibration_sessions WHERE reviewer = ? AND response_id = ?')
        .get(reviewer, r.id) as CalibrationRow | undefined;
      const run = latestScoringRun(db, r.id);
      return {
        responseId: r.id,
        pseudonym: r.pseudonym,
        subgroup: r.subgroup,
        prompt: r.prompt,
        text: r.text,
        hasRun: Boolean(run),
        myScore: mine?.manual_score ?? null,
        // Only surface the AI score once the reviewer has revealed it, so the
        // page itself cannot leak the anchor before a blind score is recorded.
        revealed: mine?.revealed_at
          ? {
              aiScore: mine.ai_score,
              revealedAt: mine.revealed_at,
              peers: (
                db
                  .prepare(
                    'SELECT reviewer, manual_score FROM calibration_sessions WHERE response_id = ? AND reviewer != ? ORDER BY created_at ASC',
                  )
                  .all(r.id, reviewer) as Array<{ reviewer: string; manual_score: number }>
              ).map((p) => ({ reviewer: p.reviewer, manualScore: p.manual_score })),
            }
          : null,
      };
    });

  return (
    <CalibrationClient
      reviewer={reviewer}
      rubricName={rubricName}
      scaleMin={scale.min}
      scaleMax={scale.max}
      anchors={anchors}
    />
  );
}
