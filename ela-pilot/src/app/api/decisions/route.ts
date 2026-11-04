import { z } from 'zod';
import type Database from 'better-sqlite3';
import { getDb } from '@db/client';
import { handle, readJson, notFound, badRequest, conflict, ApiError } from '@/lib/http';
import { requireReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { verifyQuote } from '@/lib/evidence';
import { findCriterion, isScoreInScale } from '@/lib/rubric';
import { computeMetrics } from '@/lib/metrics';
import { newId, nowIso } from '@/lib/ids';
import {
  getResponse,
  getScoringRun,
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
  aiScore: z.number().int(),
  finalScore: z.number().int(),
  action: z.enum(['accept', 'revise', 'reject', 'flag']),
  note: z.string().max(2000).optional(),
  /** Optional: pin the decision to a specific run. Defaults to the latest. */
  scoringRunId: z.string().min(1).optional(),
});

/**
 * When this criterion's review began, derived server-side.
 *
 * Time-on-task is evidence, so it is never taken from the client. The clock for
 * a criterion starts at whichever came last: the reviewer opening this response
 * (`review_started`), or the reviewer's previous decision on it.
 */
function deriveStartedAt(
  db: Database.Database,
  responseId: string,
  reviewer: string,
): string | null {
  const started = db
    .prepare(
      `SELECT ts FROM audit_log
        WHERE action = 'review_started' AND actor = ?
          AND json_extract(payload, '$.responseId') = ?
        ORDER BY id DESC LIMIT 1`,
    )
    .get(reviewer, responseId) as { ts: string } | undefined;

  const lastDecision = db
    .prepare(
      `SELECT decided_at AS ts FROM decisions
        WHERE response_id = ? AND reviewer = ?
        ORDER BY decided_at DESC LIMIT 1`,
    )
    .get(responseId, reviewer) as { ts: string } | undefined;

  const candidates = [started?.ts, lastDecision?.ts].filter(
    (t): t is string => typeof t === 'string',
  );
  if (candidates.length === 0) return null;
  return candidates.reduce((a, b) => (Date.parse(a) >= Date.parse(b) ? a : b));
}

/**
 * POST /api/decisions
 * { responseId, criterionId, aiScore, finalScore, action, note?, scoringRunId? }
 *
 * One row per criterion per review (brief, golden rule 5). Blocked while a kill
 * criterion is tripped unless the reviewer has acknowledged it.
 */
export async function POST(req: Request) {
  return handle(async () => {
    const reviewer = requireReviewer();
    const body = bodySchema.parse(await readJson(req));

    const db = getDb();
    const response = getResponse(db, body.responseId);
    if (!response) throw notFound(`response ${body.responseId} not found`);

    const { rubric } = defaultRubric(db);
    const criterion = findCriterion(rubric, body.criterionId);
    if (!criterion) throw notFound(`criterion ${body.criterionId} is not in rubric ${rubric.id}`);

    const run = body.scoringRunId
      ? getScoringRun(db, body.scoringRunId)
      : latestScoringRun(db, body.responseId);
    if (!run) throw badRequest('response has no scoring run — score it first');
    if (run.response_id !== body.responseId) {
      throw badRequest('scoringRunId does not belong to this response');
    }

    // Scores must sit inside the rubric scale: an out-of-range final score
    // would corrupt QWK, the pilot's headline validation metric.
    if (!isScoreInScale(criterion, body.finalScore)) {
      throw badRequest(
        `finalScore ${body.finalScore} outside scale ${criterion.scale.min}-${criterion.scale.max}`,
      );
    }
    if (!isScoreInScale(criterion, body.aiScore)) {
      throw badRequest(
        `aiScore ${body.aiScore} outside scale ${criterion.scale.min}-${criterion.scale.max}`,
      );
    }

    // The client reports the AI score it displayed; it must match the stored
    // draft, otherwise the agreement metric is comparing against a fiction.
    const draft = findDraft(parseDrafts(run), body.criterionId);
    if (!draft) throw badRequest(`scoring run ${run.id} has no draft for ${body.criterionId}`);
    if (draft.score !== body.aiScore) {
      throw conflict(
        `aiScore ${body.aiScore} does not match stored draft score ${draft.score} for ${body.criterionId}`,
      );
    }

    // `accept` means "the AI score stands": enforce it rather than trusting the
    // client to keep action and score consistent.
    if (body.action === 'accept' && body.finalScore !== body.aiScore) {
      throw badRequest('accept requires finalScore to equal aiScore — use revise instead');
    }
    if (body.action === 'revise' && body.finalScore === body.aiScore) {
      throw badRequest('revise requires a finalScore different from aiScore — use accept instead');
    }

    // Kill criteria gate acceptance (brief, golden rule 6).
    const before = computeMetrics(db);
    if (before.kill.paused && body.action === 'accept') {
      throw new ApiError(
        423,
        'accept is disabled: a kill criterion is tripped and has not been acknowledged',
        before.kill.violations,
      );
    }

    const decidedAt = nowIso();
    const startedAt = deriveStartedAt(db, body.responseId, reviewer) ?? decidedAt;
    const evidenceStatus = verifyQuote(response.text, draft.evidence).status;
    const decisionId = newId('dec');

    const write = db.transaction(() => {
      try {
        db.prepare(
          `INSERT INTO decisions
             (id, response_id, scoring_run_id, criterion_id, ai_score, final_score,
              action, reviewer, started_at, decided_at, note)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)`,
        ).run(
          decisionId,
          body.responseId,
          run.id,
          body.criterionId,
          body.aiScore,
          body.finalScore,
          body.action,
          reviewer,
          startedAt,
          decidedAt,
          body.note ?? null,
        );
      } catch (err) {
        if (err instanceof Error && /UNIQUE constraint failed/.test(err.message)) {
          throw conflict(
            `${reviewer} has already decided ${body.criterionId} for this response`,
          );
        }
        throw err;
      }

      appendAudit(db, reviewer, 'decision', {
        decisionId,
        responseId: body.responseId,
        scoringRunId: run.id,
        criterionId: body.criterionId,
        aiScore: body.aiScore,
        finalScore: body.finalScore,
        action: body.action,
        evidenceVerification: evidenceStatus,
        modelVersion: run.model_version,
        promptVersion: run.prompt_version,
        startedAt,
        decidedAt,
        reviewSeconds: (Date.parse(decidedAt) - Date.parse(startedAt)) / 1000,
        hasNote: Boolean(body.note),
      });
    });
    write();

    return {
      decisionId,
      startedAt,
      decidedAt,
      reviewSeconds: (Date.parse(decidedAt) - Date.parse(startedAt)) / 1000,
      evidenceVerification: evidenceStatus,
      metrics: computeMetrics(db),
    };
  });
}
