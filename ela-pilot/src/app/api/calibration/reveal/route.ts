import { z } from 'zod';
import { getDb } from '@db/client';
import { handle, readJson, notFound, badRequest } from '@/lib/http';
import { requireReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { nowIso } from '@/lib/ids';
import { latestScoringRun, parseDrafts, defaultRubric, type CalibrationRow } from '@/lib/repo';
import { holisticAiScore } from '@/lib/calibration';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const bodySchema = z.object({
  responseId: z.string().min(1),
});

/**
 * POST /api/calibration/reveal  { responseId }
 *
 * Reveals the AI's holistic score and peers' blind scores for an anchor the
 * reviewer has already scored. The AI score is written onto the reviewer's own
 * calibration row at reveal time, so the record shows what they were shown.
 */
export async function POST(req: Request) {
  return handle(async () => {
    const reviewer = requireReviewer();
    const { responseId } = bodySchema.parse(await readJson(req));

    const db = getDb();
    const row = db
      .prepare('SELECT * FROM calibration_sessions WHERE reviewer = ? AND response_id = ?')
      .get(reviewer, responseId) as CalibrationRow | undefined;
    if (!row) throw badRequest('score this anchor blind before revealing');

    const run = latestScoringRun(db, responseId);
    if (!run) throw notFound(`response ${responseId} has no scoring run`);

    const { rubric } = defaultRubric(db);
    const aiScore = holisticAiScore(rubric, parseDrafts(run));
    const revealedAt = row.revealed_at ?? nowIso();

    if (row.revealed_at === null) {
      const write = db.transaction(() => {
        db.prepare(
          'UPDATE calibration_sessions SET ai_score = ?, revealed_at = ? WHERE id = ?',
        ).run(aiScore, revealedAt, row.id);

        appendAudit(db, reviewer, 'calibration_revealed', {
          calibrationId: row.id,
          responseId,
          manualScore: row.manual_score,
          aiScore,
          scoringRunId: run.id,
          modelVersion: run.model_version,
          promptVersion: run.prompt_version,
        });
      });
      write();
    }

    // Peers: other reviewers' blind scores on the same anchor.
    const peers = db
      .prepare(
        'SELECT reviewer, manual_score FROM calibration_sessions WHERE response_id = ? AND reviewer != ? ORDER BY created_at ASC',
      )
      .all(responseId, reviewer) as Array<{ reviewer: string; manual_score: number }>;

    return {
      responseId,
      manualScore: row.manual_score,
      aiScore,
      revealedAt,
      peers: peers.map((p) => ({ reviewer: p.reviewer, manualScore: p.manual_score })),
    };
  });
}
