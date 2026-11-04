import { z } from 'zod';
import { getDb } from '@db/client';
import { handle, readJson, notFound, badRequest, conflict } from '@/lib/http';
import { requireReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { newId, nowIso } from '@/lib/ids';
import { getResponse, defaultRubric } from '@/lib/repo';
import { calibrationScale } from '@/lib/calibration';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const bodySchema = z.object({
  responseId: z.string().min(1),
  manualScore: z.number().int(),
});

/**
 * POST /api/calibration  { responseId, manualScore }
 *
 * Blind holistic score: the reviewer records their own judgement BEFORE seeing
 * the AI draft. `ai_score` and `revealed_at` stay null until /reveal, so the
 * row itself is evidence that the manual score was made blind.
 */
export async function POST(req: Request) {
  return handle(async () => {
    const reviewer = requireReviewer();
    const { responseId, manualScore } = bodySchema.parse(await readJson(req));

    const db = getDb();
    const response = getResponse(db, responseId);
    if (!response) throw notFound(`response ${responseId} not found`);

    const { rubric } = defaultRubric(db);
    const scale = calibrationScale(rubric);
    if (manualScore < scale.min || manualScore > scale.max) {
      throw badRequest(`manualScore must be between ${scale.min} and ${scale.max}`);
    }

    const existing = db
      .prepare('SELECT id FROM calibration_sessions WHERE reviewer = ? AND response_id = ?')
      .get(reviewer, responseId) as { id: string } | undefined;
    if (existing) {
      throw conflict(`${reviewer} has already calibrated on this anchor`);
    }

    const id = newId('cal');
    const createdAt = nowIso();

    const write = db.transaction(() => {
      db.prepare(
        `INSERT INTO calibration_sessions
           (id, reviewer, response_id, manual_score, ai_score, revealed_at, created_at)
         VALUES (?,?,?,?,NULL,NULL,?)`,
      ).run(id, reviewer, responseId, manualScore, createdAt);

      appendAudit(db, reviewer, 'calibration_scored', {
        calibrationId: id,
        responseId,
        manualScore,
      });
    });
    write();

    return { calibrationId: id, responseId, manualScore, createdAt };
  });
}
