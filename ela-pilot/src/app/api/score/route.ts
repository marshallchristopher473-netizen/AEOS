import { z } from 'zod';
import { getDb } from '@db/client';
import { handle, readJson, notFound } from '@/lib/http';
import { requireReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { runScoring } from '@/lib/scoring';
import { getResponse, defaultRubric } from '@/lib/repo';
import { nowIso } from '@/lib/ids';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const bodySchema = z.object({
  responseId: z.string().min(1),
});

/**
 * POST /api/score  { responseId }
 *
 * Creates a new scoring run and records it in the audit chain. The model and
 * prompt versions are captured on the row at insert time and are never updated
 * afterwards (brief, golden rule 3) — re-scoring creates a new run instead.
 */
export async function POST(req: Request) {
  return handle(async () => {
    const reviewer = requireReviewer();
    const { responseId } = bodySchema.parse(await readJson(req));

    const db = getDb();
    const response = getResponse(db, responseId);
    if (!response) throw notFound(`response ${responseId} not found`);

    const { row: rubricRow, rubric } = defaultRubric(db);
    const run = await runScoring(response.text, rubric);
    const createdAt = nowIso();

    const insert = db.transaction(() => {
      db.prepare(
        `INSERT INTO scoring_runs
           (id, response_id, rubric_id, model_version, prompt_version, output_json, created_at)
         VALUES (?,?,?,?,?,?,?)`,
      ).run(
        run.id,
        response.id,
        rubricRow.id,
        run.modelVersion,
        run.promptVersion,
        JSON.stringify(run.drafts),
        createdAt,
      );

      appendAudit(db, reviewer, 'scoring_run', {
        scoringRunId: run.id,
        responseId: response.id,
        rubricId: rubricRow.id,
        modelVersion: run.modelVersion,
        promptVersion: run.promptVersion,
        criterionIds: run.drafts.map((d) => d.criterionId),
      });
    });
    insert();

    return {
      scoringRunId: run.id,
      responseId: response.id,
      modelVersion: run.modelVersion,
      promptVersion: run.promptVersion,
      createdAt,
      drafts: run.drafts,
    };
  });
}
