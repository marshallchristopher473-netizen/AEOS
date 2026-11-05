import type Database from 'better-sqlite3';
import { quadraticWeightedKappa } from './qwk';
import { verifyQuote } from './evidence';
import { evaluateKill, DEFAULT_KILL, type KillCriteria, type KillStatus } from './killswitch';
import {
  listDecisions,
  listResponses,
  listAuditByAction,
  getScoringRun,
  parseDrafts,
  findDraft,
  defaultRubric,
  type DecisionRow,
} from './repo';

/**
 * Pilot metrics.
 *
 * Every number here is a validation claim, so each one states its own
 * definition and its own denominator. A rate whose denominator is 0 is `null`,
 * never 0 — "no accepted decisions yet" and "nothing went wrong" must not look
 * the same on the dashboard.
 */

export type Metrics = {
  counts: {
    responses: number;
    decisions: number;
    accepted: number;
    scoredResponses: number;
  };
  /**
   * AI draft vs. teacher final, pooled over all decisions.
   * Null before any decision, and null when the sample has no rating variance
   * (kappa undefined — see `quadraticWeightedKappa`).
   */
  qwk: number | null;
  /** Decisions behind `qwk`. Needed to tell "too early" from "flat sample". */
  qwkN: number;
  /**
   * A view of the null, not a parallel source of truth: true when QWK is
   * undefined despite having decisions, i.e. every AI score and every final
   * score were the same value. Kept because it is cheaper to read on the
   * dashboard than re-deriving the condition.
   */
  qwkDegenerate: boolean;
  /** Same statistic computed within each criterion. */
  qwkByCriterion: Record<string, number | null>;
  acceptanceRate: number | null;
  reviseRate: number | null;
  rejectRate: number | null;
  flagRate: number | null;
  /** Median seconds from `started_at` to `decided_at`, per criterion. */
  medianReviewSeconds: Record<string, number | null>;
  medianReviewSecondsOverall: number | null;
  /**
   * Share of accepted decisions for which an `evidence_viewed` audit event on
   * the same response was recorded strictly BEFORE the decision timestamp.
   * Measures whether the teacher actually looked before accepting.
   */
  evidenceVerificationRate: number | null;
  /**
   * Share of accepted decisions whose AI draft quote could not be located in
   * the student response at all (`verifyQuote` status `not_found`).
   * This feeds a kill criterion.
   */
  unverifiedAcceptRate: number;
  /**
   * Accepted decisions whose quote matched only when case was ignored.
   * Reported separately so it is visible rather than folded into the
   * kill-criterion numerator.
   */
  caseInsensitiveAcceptRate: number | null;
  /** Decisions whose scoring run carries both a model and a prompt version. */
  auditCompleteness: number | null;
  kill: KillStatus;
  killCriteria: KillCriteria;
};

/**
 * Cumulative QWK after each decision, in decision order.
 *
 * This is the dashboard's "QWK trend": it answers "is agreement improving or
 * degrading as the pilot runs?", which a single pooled number cannot.
 */
export function qwkTrend(
  db: Database.Database,
): Array<{ n: number; qwk: number | null; at: string }> {
  const decisions = listDecisions(db);
  if (decisions.length === 0) return [];

  let scaleMin = 0;
  let scaleMax = 1;
  try {
    const { rubric } = defaultRubric(db);
    scaleMin = Math.min(...rubric.criteria.map((c) => c.scale.min));
    scaleMax = Math.max(...rubric.criteria.map((c) => c.scale.max));
  } catch {
    return [];
  }
  if (scaleMax <= scaleMin) return [];

  const ai: number[] = [];
  const final: number[] = [];
  return decisions.map((d, i) => {
    ai.push(d.ai_score);
    final.push(d.final_score);
    return {
      n: i + 1,
      qwk: quadraticWeightedKappa(ai, final, scaleMin, scaleMax),
      at: d.decided_at,
    };
  });
}

function rate(numerator: number, denominator: number): number | null {
  if (denominator === 0) return null;
  return numerator / denominator;
}

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((x, y) => x - y);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[mid] as number;
  return (((sorted[mid - 1] as number) + (sorted[mid] as number)) / 2);
}

/** Evidence status of the AI draft behind a decision, as the reviewer saw it. */
export function draftEvidenceStatus(
  db: Database.Database,
  decision: DecisionRow,
  responseTextById: Map<string, string>,
): 'verified' | 'case-insensitive' | 'not_found' | 'missing_draft' {
  const run = getScoringRun(db, decision.scoring_run_id);
  if (!run) return 'missing_draft';
  const draft = findDraft(parseDrafts(run), decision.criterion_id);
  if (!draft) return 'missing_draft';
  const text = responseTextById.get(decision.response_id);
  if (text === undefined) return 'missing_draft';
  return verifyQuote(text, draft.evidence).status;
}

export function computeMetrics(
  db: Database.Database,
  criteria: KillCriteria = DEFAULT_KILL,
): Metrics {
  const responses = listResponses(db);
  const decisions = listDecisions(db);
  const responseTextById = new Map(responses.map((r) => [r.id, r.text]));

  const scoredResponses = (
    db.prepare('SELECT COUNT(DISTINCT response_id) AS n FROM scoring_runs').get() as { n: number }
  ).n;

  // ---- Scale bounds come from the rubric, not from observed scores, so a
  // ---- narrow set of early decisions cannot silently redefine the metric.
  let scaleMin = 0;
  let scaleMax = 1;
  let criterionScales = new Map<string, { min: number; max: number }>();
  try {
    const { rubric } = defaultRubric(db);
    scaleMin = Math.min(...rubric.criteria.map((c) => c.scale.min));
    scaleMax = Math.max(...rubric.criteria.map((c) => c.scale.max));
    criterionScales = new Map(rubric.criteria.map((c) => [c.id, c.scale]));
  } catch {
    // No rubric seeded yet: every rate below still resolves to null/0.
  }

  // ---- Agreement -----------------------------------------------------------
  const qwk =
    decisions.length > 0 && scaleMax > scaleMin
      ? quadraticWeightedKappa(
          decisions.map((d) => d.ai_score),
          decisions.map((d) => d.final_score),
          scaleMin,
          scaleMax,
        )
      : null;

  const qwkN = decisions.length;
  // Undefined kappa despite having decisions => the sample is flat.
  const qwkDegenerate = qwk === null && qwkN > 0;

  const qwkByCriterion: Record<string, number | null> = {};
  const byCriterion = new Map<string, DecisionRow[]>();
  for (const d of decisions) {
    const bucket = byCriterion.get(d.criterion_id) ?? [];
    bucket.push(d);
    byCriterion.set(d.criterion_id, bucket);
  }
  for (const [criterionId, rows] of byCriterion) {
    const scale = criterionScales.get(criterionId) ?? { min: scaleMin, max: scaleMax };
    qwkByCriterion[criterionId] =
      scale.max > scale.min
        ? quadraticWeightedKappa(
            rows.map((d) => d.ai_score),
            rows.map((d) => d.final_score),
            scale.min,
            scale.max,
          )
        : null;
  }

  // ---- Action mix ----------------------------------------------------------
  const total = decisions.length;
  const accepted = decisions.filter((d) => d.action === 'accept');
  const acceptanceRate = rate(accepted.length, total);
  const reviseRate = rate(decisions.filter((d) => d.action === 'revise').length, total);
  const rejectRate = rate(decisions.filter((d) => d.action === 'reject').length, total);
  const flagRate = rate(decisions.filter((d) => d.action === 'flag').length, total);

  // ---- Time on task --------------------------------------------------------
  const medianReviewSeconds: Record<string, number | null> = {};
  const allSeconds: number[] = [];
  for (const [criterionId, rows] of byCriterion) {
    const seconds = rows
      .map((d) => (Date.parse(d.decided_at) - Date.parse(d.started_at)) / 1000)
      .filter((s) => Number.isFinite(s) && s >= 0);
    allSeconds.push(...seconds);
    medianReviewSeconds[criterionId] = median(seconds);
  }
  const medianReviewSecondsOverall = median(allSeconds);

  // ---- Evidence discipline -------------------------------------------------
  // `evidence_viewed` events, bucketed by response, as epoch millis.
  const viewedByResponse = new Map<string, number[]>();
  for (const row of listAuditByAction(db, 'evidence_viewed')) {
    let responseId: string | undefined;
    try {
      const payload = JSON.parse(row.payload) as { responseId?: unknown };
      if (typeof payload.responseId === 'string') responseId = payload.responseId;
    } catch {
      // A malformed payload cannot credit a response with a view.
    }
    if (!responseId) continue;
    const bucket = viewedByResponse.get(responseId) ?? [];
    bucket.push(Date.parse(row.ts));
    viewedByResponse.set(responseId, bucket);
  }

  let viewedBeforeAccept = 0;
  let notFoundAccepts = 0;
  let caseInsensitiveAccepts = 0;
  for (const d of accepted) {
    const decidedAt = Date.parse(d.decided_at);
    const views = viewedByResponse.get(d.response_id) ?? [];
    if (views.some((ts) => ts < decidedAt)) viewedBeforeAccept++;

    const status = draftEvidenceStatus(db, d, responseTextById);
    // A decision whose draft cannot be reconstructed is counted as unverified:
    // the safety metric must fail closed.
    if (status === 'not_found' || status === 'missing_draft') notFoundAccepts++;
    if (status === 'case-insensitive') caseInsensitiveAccepts++;
  }

  const evidenceVerificationRate = rate(viewedBeforeAccept, accepted.length);
  // Kill criteria compare against a number, so an empty denominator is 0 here
  // (no accepted decisions means nothing has been accepted unverified yet).
  const unverifiedAcceptRate = accepted.length === 0 ? 0 : notFoundAccepts / accepted.length;
  const caseInsensitiveAcceptRate = rate(caseInsensitiveAccepts, accepted.length);

  // ---- Auditability --------------------------------------------------------
  const complete = decisions.filter((d) => {
    const run = getScoringRun(db, d.scoring_run_id);
    return Boolean(run && run.model_version && run.prompt_version);
  }).length;
  const auditCompleteness = rate(complete, total);

  const kill = evaluateKill({ qwk, qwkN, unverifiedAcceptRate }, criteria);

  return {
    counts: {
      responses: responses.length,
      decisions: total,
      accepted: accepted.length,
      scoredResponses,
    },
    qwk,
    qwkN,
    qwkDegenerate,
    qwkByCriterion,
    acceptanceRate,
    reviseRate,
    rejectRate,
    flagRate,
    medianReviewSeconds,
    medianReviewSecondsOverall,
    evidenceVerificationRate,
    unverifiedAcceptRate,
    caseInsensitiveAcceptRate,
    auditCompleteness,
    kill,
    killCriteria: criteria,
  };
}
