import { z } from 'zod';
import { getDb } from '@db/client';
import { handle, readJson, notFound } from '@/lib/http';
import { requireReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { verifyQuote } from '@/lib/evidence';
import { findCriterion } from '@/lib/rubric-schema';
import {
  getResponse,
  latestScoringRun,
  parseDrafts,
  findDraft,
  defaultRubric,
} from '@/lib/repo';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const bodySchema = z.object({
  responseId: z.string().min(1),
  criterionId: z.string().min(1),
});

/**
 * POST /api/audit/evidence-viewed  { responseId, criterionId }
 *
 * Records that the reviewer actually opened the evidence for a criterion.
 * `evidenceVerificationRate` counts accepted decisions preceded by one of these
 * events, so this is the sole source of that evidence — it is written from the
 * server with a server-side timestamp and cannot be back-dated by the client.
 */
export async function POST(req: Request) {
  return handle(async () => {
    const reviewer = requireReviewer();
    const { responseId, criterionId } = bodySchema.parse(await readJson(req));

    const db = getDb();
    const response = getResponse(db, responseId);
    if (!response) throw notFound(`response ${responseId} not found`);

    const { rubric } = defaultRubric(db);
    if (!findCriterion(rubric, criterionId)) {
      throw notFound(`criterion ${criterionId} is not in rubric ${rubric.id}`);
    }

    // Record the verification status the reviewer was shown, so the audit entry
    // is meaningful on its own months later.
    const run = latestScoringRun(db, responseId);
    const draft = run ? findDraft(parseDrafts(run), criterionId) : undefined;
    const status = draft ? verifyQuote(response.text, draft.evidence).status : 'not_found';

    const { ts, hash } = appendAudit(db, reviewer, 'evidence_viewed', {
      responseId,
      criterionId,
      scoringRunId: run?.id ?? null,
      verification: status,
    });

    return { ok: true, ts, hash, verification: status };
  });
}
