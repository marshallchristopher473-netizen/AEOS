import { getDb } from '@db/client';
import { handle } from '@/lib/http';
import { currentReviewer } from '@/lib/reviewer';
import {
  listResponses,
  latestScoringRun,
  listDecisionsForResponse,
  defaultRubric,
} from '@/lib/repo';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/responses
 * Worklist for the reviewer: every response with its scoring state and how far
 * the current reviewer has got. Response text is included — this is synthetic
 * pilot data by design (see brief, golden rule 4).
 */
export async function GET() {
  return handle(() => {
    const db = getDb();
    const reviewer = currentReviewer();
    const { rubric } = defaultRubric(db);

    const items = listResponses(db).map((r) => {
      const run = latestScoringRun(db, r.id);
      const decisions = reviewer ? listDecisionsForResponse(db, r.id, reviewer) : [];
      return {
        id: r.id,
        pseudonym: r.pseudonym,
        subgroup: r.subgroup,
        prompt: r.prompt,
        text: r.text,
        createdAt: r.created_at,
        scoringRun: run
          ? {
              id: run.id,
              modelVersion: run.model_version,
              promptVersion: run.prompt_version,
              createdAt: run.created_at,
            }
          : null,
        decidedCriteria: decisions.length,
        totalCriteria: rubric.criteria.length,
        complete: decisions.length === rubric.criteria.length,
      };
    });

    return { reviewer, rubricId: rubric.id, responses: items };
  });
}
